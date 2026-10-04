"""NAT simulation engine - core packet processing logic."""

import time
from dataclasses import dataclass, field
from app.models import (
    Network,
    VirtualDevice,
    Packet,
    Protocol,
    NATEntry,
    NATState,
    PortForwardRule,
    PacketTransformation,
    Stage,
    Action,
    SimulationResult,
    InvalidIPAddress,
    IPOutsideNetwork,
    DeviceNotFound,
    DuplicateIPAddress,
    InvalidPort,
    UnsupportedProtocol,
    PortForwardConflict,
    NATPortExhausted,
    NATMappingNotFound,
    NetworkError,
)
from app.services.network_service import NetworkService


@dataclass
class SimulationMetrics:
    """Simulation performance metrics."""

    total_packets: int = 0
    successful_packets: int = 0
    failed_packets: int = 0
    snat_packets: int = 0
    dnat_packets: int = 0
    reverse_nat_packets: int = 0
    total_processing_time_ms: float = 0.0

    @property
    def average_processing_time_ms(self) -> float:
        if self.total_packets == 0:
            return 0.0
        return self.total_processing_time_ms / self.total_packets

    def reset(self) -> None:
        """Reset all metrics."""
        self.total_packets = 0
        self.successful_packets = 0
        self.failed_packets = 0
        self.snat_packets = 0
        self.dnat_packets = 0
        self.reverse_nat_packets = 0
        self.total_processing_time_ms = 0.0


class NATEngine:
    """NAT simulation engine with stateful SNAT and DNAT support."""

    DEFAULT_PORT_RANGE_START = 40000
    DEFAULT_PORT_RANGE_END = 50000

    def __init__(
        self,
        network: Network,
        port_range_start: int = DEFAULT_PORT_RANGE_START,
        port_range_end: int = DEFAULT_PORT_RANGE_END,
    ):
        if port_range_start < 1024 or port_range_end > 65535:
            raise InvalidPort("Port range must be within 1024-65535")
        if port_range_start >= port_range_end:
            raise InvalidPort("Port range start must be less than end")

        self._network_service = NetworkService(network)
        self._nat_table: dict[tuple, NATEntry] = {}  # flow_key -> NATEntry
        self._reverse_nat_table: dict[tuple, NATEntry] = {}  # reverse_flow_key -> NATEntry
        self._port_forward_rules: dict[str, PortForwardRule] = {}  # id -> rule
        self._port_forward_index: dict[tuple, PortForwardRule] = {}  # match_key -> rule
        self._allocated_ports: set[int] = set()
        self._port_range_start = port_range_start
        self._port_range_end = port_range_end
        self._next_port = port_range_start
        self._metrics = SimulationMetrics()

    @property
    def network(self) -> Network:
        return self._network_service.network

    @property
    def devices(self) -> list[VirtualDevice]:
        return self._network_service.devices

    @property
    def nat_entries(self) -> list[NATEntry]:
        return list(self._nat_table.values())

    @property
    def port_forward_rules(self) -> list[PortForwardRule]:
        return list(self._port_forward_rules.values())

    @property
    def metrics(self) -> SimulationMetrics:
        return self._metrics

    def add_device(self, device: VirtualDevice) -> VirtualDevice:
        """Add a device to the virtual network."""
        return self._network_service.add_device(device)

    def remove_device(self, device_id: str) -> VirtualDevice:
        """Remove a device from the virtual network."""
        return self._network_service.remove_device(device_id)

    def get_device(self, device_id: str) -> VirtualDevice:
        """Get a device by ID."""
        return self._network_service.get_device(device_id)

    def get_device_by_ip(self, ip: str) -> VirtualDevice | None:
        """Get a device by IP address."""
        return self._network_service.get_device_by_ip(ip)

    def _allocate_port(self) -> int:
        """Allocate a public port deterministically."""
        for port in range(self._next_port, self._port_range_end + 1):
            if port not in self._allocated_ports:
                self._allocated_ports.add(port)
                self._next_port = port + 1
                return port
        # Wrap around and try from start
        for port in range(self._port_range_start, self._next_port):
            if port not in self._allocated_ports:
                self._allocated_ports.add(port)
                self._next_port = port + 1
                return port
        raise NATPortExhausted(
            f"No available ports in range {self._port_range_start}-{self._port_range_end}"
        )

    def _release_port(self, port: int) -> None:
        """Release a public port."""
        self._allocated_ports.discard(port)
        if port < self._next_port:
            self._next_port = port

    def _record_metrics(self, success: bool, action: str, processing_time_ms: float) -> None:
        """Record simulation metrics."""
        self._metrics.total_packets += 1
        self._metrics.total_processing_time_ms += processing_time_ms
        if success:
            self._metrics.successful_packets += 1
        else:
            self._metrics.failed_packets += 1
        if action == "SNAT":
            self._metrics.snat_packets += 1
        elif action == "DNAT":
            self._metrics.dnat_packets += 1
        elif action == "REVERSE_SNAT":
            self._metrics.reverse_nat_packets += 1

    def process_outgoing_packet(self, packet: Packet) -> SimulationResult:
        """Process an outbound packet (SNAT)."""
        start_time = time.perf_counter()
        transformations: list[PacketTransformation] = []

        # Step 1: Validate packet
        try:
            # Validate source device exists in our network
            source_device = self._network_service.get_device_by_ip(packet.source_ip)
            if not source_device:
                raise DeviceNotFound(f"Source device {packet.source_ip} not found in virtual network")

            # Validate source IP is in LAN
            if not self._network_service.network.contains_ip(packet.source_ip):
                raise IPOutsideNetwork(f"Source IP {packet.source_ip} not in LAN")

        except NetworkError as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            self._record_metrics(False, "SNAT", processing_time)
            return SimulationResult(
                original_packet=packet,
                translated_packet=None,
                transformations=[],
                success=False,
                error=str(e),
            )

        # Record original packet
        transformations.append(
            PacketTransformation(
                stage=Stage.LAN,
                action=Action.ORIGINAL,
                source_ip=packet.source_ip,
                source_port=packet.source_port,
                destination_ip=packet.destination_ip,
                destination_port=packet.destination_port,
                description="Original packet from LAN device",
            )
        )

        # Step 2: Check for existing NAT mapping
        flow_key = packet.flow_key()
        existing_entry = self._nat_table.get(flow_key)

        if existing_entry and existing_entry.state == NATState.ACTIVE:
            # Reuse existing mapping
            translated = packet.copy_with(
                source_ip=existing_entry.public_ip,
                source_port=existing_entry.public_port,
            )
            transformations.append(
                PacketTransformation(
                    stage=Stage.NAT_GATEWAY,
                    action=Action.SNAT,
                    source_ip=packet.source_ip,
                    source_port=packet.source_port,
                    destination_ip=packet.destination_ip,
                    destination_port=packet.destination_port,
                    description=f"Reused existing SNAT mapping: {existing_entry.public_ip}:{existing_entry.public_port}",
                )
            )
            transformations.append(
                PacketTransformation(
                    stage=Stage.INTERNET,
                    action=Action.FORWARD,
                    source_ip=translated.source_ip,
                    source_port=translated.source_port,
                    destination_ip=translated.destination_ip,
                    destination_port=translated.destination_port,
                    description="Packet forwarded to Internet",
                )
            )
            processing_time = (time.perf_counter() - start_time) * 1000
            self._record_metrics(True, "SNAT", processing_time)
            return SimulationResult(
                original_packet=packet,
                translated_packet=translated,
                transformations=transformations,
                success=True,
            )

        # Step 3: Allocate new public port
        try:
            public_port = self._allocate_port()
        except NATPortExhausted as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            self._record_metrics(False, "SNAT", processing_time)
            return SimulationResult(
                original_packet=packet,
                translated_packet=None,
                transformations=transformations,
                success=False,
                error=str(e),
            )

        # Step 4: Create NAT entry
        public_ip = str(self._network_service.network.get_public_ip())
        nat_entry = NATEntry(
            protocol=packet.protocol,
            private_ip=packet.source_ip,
            private_port=packet.source_port,
            public_ip=public_ip,
            public_port=public_port,
            destination_ip=packet.destination_ip,
            destination_port=packet.destination_port,
            state=NATState.ACTIVE,
        )

        self._nat_table[flow_key] = nat_entry
        self._reverse_nat_table[nat_entry.reverse_flow_key()] = nat_entry

        # Step 5: Translate packet
        translated = packet.copy_with(
            source_ip=public_ip,
            source_port=public_port,
        )

        transformations.append(
            PacketTransformation(
                stage=Stage.NAT_GATEWAY,
                action=Action.SNAT,
                source_ip=packet.source_ip,
                source_port=packet.source_port,
                destination_ip=packet.destination_ip,
                destination_port=packet.destination_port,
                description=f"SNAT: {packet.source_ip}:{packet.source_port} -> {public_ip}:{public_port}",
            )
        )
        transformations.append(
            PacketTransformation(
                stage=Stage.INTERNET,
                action=Action.FORWARD,
                source_ip=translated.source_ip,
                source_port=translated.source_port,
                destination_ip=translated.destination_ip,
                destination_port=translated.destination_port,
                description="Packet forwarded to Internet",
            )
        )

        processing_time = (time.perf_counter() - start_time) * 1000
        self._record_metrics(True, "SNAT", processing_time)
        return SimulationResult(
            original_packet=packet,
            translated_packet=translated,
            transformations=transformations,
            success=True,
        )

    def process_incoming_response(self, packet: Packet) -> SimulationResult:
        """Process an incoming response packet (reverse SNAT)."""
        start_time = time.perf_counter()
        transformations: list[PacketTransformation] = []

        # Record original incoming packet
        transformations.append(
            PacketTransformation(
                stage=Stage.INTERNET,
                action=Action.ORIGINAL,
                source_ip=packet.source_ip,
                source_port=packet.source_port,
                destination_ip=packet.destination_ip,
                destination_port=packet.destination_port,
                description="Incoming response from Internet",
            )
        )

        # Look up reverse NAT mapping
        reverse_key = packet.reverse_flow_key()
        nat_entry = self._reverse_nat_table.get(reverse_key)

        if not nat_entry or nat_entry.state != NATState.ACTIVE:
            processing_time = (time.perf_counter() - start_time) * 1000
            self._record_metrics(False, "REVERSE_SNAT", processing_time)
            return SimulationResult(
                original_packet=packet,
                translated_packet=None,
                transformations=transformations,
                success=False,
                error=f"No active NAT mapping for {packet.destination_ip}:{packet.destination_port}",
            )

        # Translate destination back to private
        translated = packet.copy_with(
            destination_ip=nat_entry.private_ip,
            destination_port=nat_entry.private_port,
        )

        transformations.append(
            PacketTransformation(
                stage=Stage.NAT_GATEWAY,
                action=Action.SNAT,
                source_ip=packet.source_ip,
                source_port=packet.source_port,
                destination_ip=packet.destination_ip,
                destination_port=packet.destination_port,
                description=f"Reverse SNAT: {packet.destination_ip}:{packet.destination_port} -> {nat_entry.private_ip}:{nat_entry.private_port}",
            )
        )
        transformations.append(
            PacketTransformation(
                stage=Stage.LAN,
                action=Action.FORWARD,
                source_ip=translated.source_ip,
                source_port=translated.source_port,
                destination_ip=translated.destination_ip,
                destination_port=translated.destination_port,
                description="Packet forwarded to LAN device",
            )
        )

        processing_time = (time.perf_counter() - start_time) * 1000
        self._record_metrics(True, "REVERSE_SNAT", processing_time)
        return SimulationResult(
            original_packet=packet,
            translated_packet=translated,
            transformations=transformations,
            success=True,
        )

    def add_port_forward(self, rule: PortForwardRule) -> PortForwardRule:
        """Add a port forwarding (DNAT) rule."""
        # Validate public IP matches NAT gateway public IP
        nat_public_ip = str(self._network_service.network.get_public_ip())
        if rule.public_ip != nat_public_ip:
            raise PortForwardConflict(
                f"Port forward public IP {rule.public_ip} must match NAT gateway public IP {nat_public_ip}"
            )

        # Validate private IP is in LAN and assigned to a device
        if not self._network_service.network.contains_ip(rule.private_ip):
            raise IPOutsideNetwork(f"Private IP {rule.private_ip} not in LAN")

        private_device = self._network_service.get_device_by_ip(rule.private_ip)
        if not private_device:
            raise DeviceNotFound(f"No device found at private IP {rule.private_ip}")

        # Check for conflicts (same protocol, public IP, public port)
        match_key = rule.match_key()
        if match_key in self._port_forward_index:
            existing = self._port_forward_index[match_key]
            raise PortForwardConflict(
                f"Port forward rule for {existing.protocol.value} {existing.public_ip}:{existing.public_port} already exists"
            )

        self._port_forward_rules[rule.id] = rule
        self._port_forward_index[match_key] = rule
        return rule

    def remove_port_forward(self, rule_id: str) -> PortForwardRule:
        """Remove a port forwarding rule."""
        if rule_id not in self._port_forward_rules:
            raise DeviceNotFound(f"Port forward rule {rule_id} not found")
        rule = self._port_forward_rules.pop(rule_id)
        self._port_forward_index.pop(rule.match_key(), None)
        return rule

    def get_port_forward_rules(self) -> list[PortForwardRule]:
        """Get all port forwarding rules."""
        return list(self._port_forward_rules.values())

    def process_incoming_packet(self, packet: Packet) -> SimulationResult:
        """Process an incoming packet from Internet (DNAT for port forwards)."""
        start_time = time.perf_counter()
        transformations: list[PacketTransformation] = []

        # Record original incoming packet
        transformations.append(
            PacketTransformation(
                stage=Stage.INTERNET,
                action=Action.ORIGINAL,
                source_ip=packet.source_ip,
                source_port=packet.source_port,
                destination_ip=packet.destination_ip,
                destination_port=packet.destination_port,
                description="Incoming packet from Internet",
            )
        )

        # Check port forwarding rules
        match_key = (packet.protocol.value, packet.destination_ip, packet.destination_port)
        rule = self._port_forward_index.get(match_key)

        if not rule:
            processing_time = (time.perf_counter() - start_time) * 1000
            self._record_metrics(False, "DNAT", processing_time)
            return SimulationResult(
                original_packet=packet,
                translated_packet=None,
                transformations=transformations,
                success=False,
                error=f"No port forward rule for {packet.destination_ip}:{packet.destination_port} ({packet.protocol.value})",
            )

        # Apply DNAT
        translated = packet.copy_with(
            destination_ip=rule.private_ip,
            destination_port=rule.private_port,
        )

        transformations.append(
            PacketTransformation(
                stage=Stage.NAT_GATEWAY,
                action=Action.DNAT,
                source_ip=packet.source_ip,
                source_port=packet.source_port,
                destination_ip=packet.destination_ip,
                destination_port=packet.destination_port,
                description=f"DNAT: {packet.destination_ip}:{packet.destination_port} -> {rule.private_ip}:{rule.private_port}",
            )
        )
        transformations.append(
            PacketTransformation(
                stage=Stage.LAN,
                action=Action.FORWARD,
                source_ip=translated.source_ip,
                source_port=translated.source_port,
                destination_ip=translated.destination_ip,
                destination_port=translated.destination_port,
                description="Packet forwarded to LAN device",
            )
        )

        processing_time = (time.perf_counter() - start_time) * 1000
        self._record_metrics(True, "DNAT", processing_time)
        return SimulationResult(
            original_packet=packet,
            translated_packet=translated,
            transformations=transformations,
            success=True,
        )

    def get_nat_entries(self) -> list[NATEntry]:
        """Get all active NAT entries."""
        return [entry for entry in self._nat_table.values() if entry.state == NATState.ACTIVE]

    def find_nat_entry(self, flow_key: tuple) -> NATEntry | None:
        """Find a NAT entry by flow key."""
        return self._nat_table.get(flow_key)

    def remove_nat_entry(self, flow_key: tuple) -> NATEntry | None:
        """Remove a NAT entry by flow key."""
        entry = self._nat_table.pop(flow_key, None)
        if entry:
            self._reverse_nat_table.pop(entry.reverse_flow_key(), None)
            self._release_port(entry.public_port)
        return entry

    def clear_nat_table(self) -> None:
        """Clear all NAT mappings."""
        self._nat_table.clear()
        self._reverse_nat_table.clear()
        self._allocated_ports.clear()
        self._next_port = self._port_range_start

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._metrics.reset()

    def clear_all_state(self) -> None:
        """Clear all simulation state including metrics."""
        self.clear_nat_table()
        self._port_forward_rules.clear()
        self._port_forward_index.clear()
        self._metrics.reset()