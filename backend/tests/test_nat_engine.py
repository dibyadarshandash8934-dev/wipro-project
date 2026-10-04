"""Comprehensive tests for NAT simulation engine."""

import pytest

from app.models import (
    Network,
    VirtualDevice,
    DeviceType,
    Packet,
    Protocol,
    PortForwardRule,
    Stage,
    Action,
)
from app.services.nat_engine import NATEngine
from app.models.exceptions import (
    InvalidNetwork,
    InvalidIPAddress,
    IPOutsideNetwork,
    DuplicateIPAddress,
    DeviceNotFound,
    InvalidPort,
    UnsupportedProtocol,
    PortForwardConflict,
    NATPortExhausted,
    NATMappingNotFound,
)


# Fixtures

@pytest.fixture
def network() -> Network:
    """Create a test network."""
    return Network(
        cidr="192.168.1.0/24",
        gateway_ip="192.168.1.1",
        public_ip="203.0.113.5",
    )


@pytest.fixture
def engine(network: Network) -> NATEngine:
    """Create a NAT engine with test network."""
    return NATEngine(network)


@pytest.fixture
def device_pc(network: Network) -> VirtualDevice:
    """Create a test PC device."""
    return VirtualDevice(
        id="pc-01",
        name="PC-01",
        ip="192.168.1.10",
        type=DeviceType.PC,
    )


@pytest.fixture
def device_server(network: Network) -> VirtualDevice:
    """Create a test server device."""
    return VirtualDevice(
        id="server-01",
        name="WEB-01",
        ip="192.168.1.20",
        type=DeviceType.SERVER,
    )


# Network Tests

def test_create_network(network: Network):
    """Test network creation."""
    assert network.cidr == "192.168.1.0/24"
    assert network.gateway_ip == "192.168.1.1"
    assert network.public_ip == "203.0.113.5"
    assert network.get_network().prefixlen == 24


def test_invalid_cidr():
    """Test invalid CIDR rejection."""
    with pytest.raises(InvalidNetwork):
        Network(cidr="invalid", gateway_ip="192.168.1.1", public_ip="203.0.113.5")


def test_invalid_gateway_ip():
    """Test invalid gateway IP rejection."""
    with pytest.raises(InvalidIPAddress):
        Network(cidr="192.168.1.0/24", gateway_ip="invalid", public_ip="203.0.113.5")


def test_gateway_outside_network():
    """Test gateway outside network rejection."""
    with pytest.raises(IPOutsideNetwork):
        Network(cidr="192.168.1.0/24", gateway_ip="192.168.2.1", public_ip="203.0.113.5")


# Device Tests

def test_add_valid_device(engine: NATEngine, device_pc: VirtualDevice):
    """Test adding a valid device."""
    added = engine.add_device(device_pc)
    assert added.id == "pc-01"
    assert added.ip == "192.168.1.10"
    assert len(engine.devices) == 1


def test_reject_invalid_ip():
    """Test rejecting device with invalid IP."""
    network = Network(cidr="192.168.1.0/24", gateway_ip="192.168.1.1", public_ip="203.0.113.5")
    engine = NATEngine(network)
    with pytest.raises(InvalidIPAddress):
        VirtualDevice(id="pc-01", name="PC-01", ip="invalid", type=DeviceType.PC)


def test_reject_device_outside_subnet(engine: NATEngine):
    """Test rejecting device outside subnet."""
    device = VirtualDevice(id="pc-01", name="PC-01", ip="192.168.2.10", type=DeviceType.PC)
    with pytest.raises(IPOutsideNetwork):
        engine.add_device(device)


def test_reject_duplicate_device_ip(engine: NATEngine, device_pc: VirtualDevice):
    """Test rejecting duplicate device IP."""
    engine.add_device(device_pc)
    device2 = VirtualDevice(id="pc-02", name="PC-02", ip="192.168.1.10", type=DeviceType.PC)
    with pytest.raises(DuplicateIPAddress):
        engine.add_device(device2)


def test_reject_network_address_as_device(engine: NATEngine):
    """Test rejecting network address as device IP."""
    device = VirtualDevice(id="pc-01", name="PC-01", ip="192.168.1.0", type=DeviceType.PC)
    with pytest.raises(IPOutsideNetwork):
        engine.add_device(device)


def test_reject_broadcast_address_as_device(engine: NATEngine):
    """Test rejecting broadcast address as device IP."""
    device = VirtualDevice(id="pc-01", name="PC-01", ip="192.168.1.255", type=DeviceType.PC)
    with pytest.raises(IPOutsideNetwork):
        engine.add_device(device)


def test_remove_device(engine: NATEngine, device_pc: VirtualDevice):
    """Test removing a device."""
    engine.add_device(device_pc)
    removed = engine.remove_device("pc-01")
    assert removed.id == "pc-01"
    assert len(engine.devices) == 0


def test_get_device_not_found(engine: NATEngine):
    """Test getting non-existent device."""
    with pytest.raises(DeviceNotFound):
        engine.get_device("non-existent")


# SNAT Tests

def test_tcp_snat(engine: NATEngine, device_pc: VirtualDevice):
    """Test TCP SNAT (Scenario 1)."""
    engine.add_device(device_pc)

    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )

    result = engine.process_outgoing_packet(packet)

    assert result.success
    assert result.translated_packet is not None
    assert result.translated_packet.source_ip == "203.0.113.5"
    assert result.translated_packet.source_port == 40000
    assert result.translated_packet.destination_ip == "8.8.8.8"
    assert result.translated_packet.destination_port == 443
    assert len(result.transformations) == 3


def test_udp_snat(engine: NATEngine, device_pc: VirtualDevice):
    """Test UDP SNAT."""
    engine.add_device(device_pc)

    packet = Packet(
        protocol=Protocol.UDP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=53,
    )

    result = engine.process_outgoing_packet(packet)

    assert result.success
    assert result.translated_packet.source_ip == "203.0.113.5"
    assert result.translated_packet.source_port == 40000
    assert result.translated_packet.protocol == Protocol.UDP


def test_existing_mapping_reuse(engine: NATEngine, device_pc: VirtualDevice):
    """Test existing mapping reuse (Scenario 2)."""
    engine.add_device(device_pc)

    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )

    result1 = engine.process_outgoing_packet(packet)
    result2 = engine.process_outgoing_packet(packet)

    assert result1.success
    assert result2.success
    assert result1.translated_packet.source_port == result2.translated_packet.source_port == 40000
    # Should have same NAT entry
    assert len(engine.nat_entries) == 1


def test_different_tcp_flows_different_ports(engine: NATEngine, device_pc: VirtualDevice):
    """Test different TCP flows get different public ports (Scenario 3)."""
    engine.add_device(device_pc)

    packet1 = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )
    packet2 = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50001,
        destination_ip="8.8.8.8",
        destination_port=443,
    )

    result1 = engine.process_outgoing_packet(packet1)
    result2 = engine.process_outgoing_packet(packet2)

    assert result1.success
    assert result2.success
    assert result1.translated_packet.source_port == 40000
    assert result2.translated_packet.source_port == 40001
    assert len(engine.nat_entries) == 2


def test_tcp_udp_same_private_port(engine: NATEngine, device_pc: VirtualDevice):
    """Test TCP and UDP can use same private port."""
    engine.add_device(device_pc)

    tcp_packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )
    udp_packet = Packet(
        protocol=Protocol.UDP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=53,
    )

    tcp_result = engine.process_outgoing_packet(tcp_packet)
    udp_result = engine.process_outgoing_packet(udp_packet)

    assert tcp_result.success
    assert udp_result.success
    assert tcp_result.translated_packet.source_port == 40000
    assert udp_result.translated_packet.source_port == 40001  # Different protocol gets different port
    assert len(engine.nat_entries) == 2


def test_snat_unknown_device(engine: NATEngine):
    """Test SNAT with unknown source device."""
    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.99",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )

    result = engine.process_outgoing_packet(packet)

    assert not result.success
    assert "not found" in result.error.lower()


# Reverse SNAT Tests

def test_reverse_nat_lookup(engine: NATEngine, device_pc: VirtualDevice):
    """Test reverse NAT lookup for response packets."""
    engine.add_device(device_pc)

    # First create outbound mapping
    outbound = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )
    engine.process_outgoing_packet(outbound)

    # Now process incoming response
    response = Packet(
        protocol=Protocol.TCP,
        source_ip="8.8.8.8",
        source_port=443,
        destination_ip="203.0.113.5",
        destination_port=40000,
    )

    result = engine.process_incoming_response(response)

    assert result.success
    assert result.translated_packet is not None
    assert result.translated_packet.destination_ip == "192.168.1.10"
    assert result.translated_packet.destination_port == 50000
    assert result.translated_packet.source_ip == "8.8.8.8"
    assert result.translated_packet.source_port == 443


def test_unknown_reverse_mapping(engine: NATEngine):
    """Test unknown reverse NAT mapping returns error."""
    response = Packet(
        protocol=Protocol.TCP,
        source_ip="8.8.8.8",
        source_port=443,
        destination_ip="203.0.113.5",
        destination_port=40000,
    )

    result = engine.process_incoming_response(response)

    assert not result.success
    assert "no active nat mapping" in result.error.lower()


# Port Forwarding / DNAT Tests

def test_add_port_forward_rule(engine: NATEngine, device_server: VirtualDevice):
    """Test adding port forwarding rule."""
    engine.add_device(device_server)

    rule = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )

    added = engine.add_port_forward(rule)
    assert added.id == "pf-01"
    assert len(engine.port_forward_rules) == 1


def test_dnat(engine: NATEngine, device_server: VirtualDevice):
    """Test DNAT (Scenario 4)."""
    engine.add_device(device_server)

    rule = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )
    engine.add_port_forward(rule)

    incoming = Packet(
        protocol=Protocol.TCP,
        source_ip="198.51.100.20",
        source_port=45000,
        destination_ip="203.0.113.5",
        destination_port=8080,
    )

    result = engine.process_incoming_packet(incoming)

    assert result.success
    assert result.translated_packet is not None
    assert result.translated_packet.destination_ip == "192.168.1.20"
    assert result.translated_packet.destination_port == 80
    assert result.translated_packet.source_ip == "198.51.100.20"
    assert result.translated_packet.source_port == 45000


def test_dnat_preserves_source(engine: NATEngine, device_server: VirtualDevice):
    """Test DNAT preserves source IP and port."""
    engine.add_device(device_server)

    rule = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )
    engine.add_port_forward(rule)

    incoming = Packet(
        protocol=Protocol.TCP,
        source_ip="198.51.100.20",
        source_port=45000,
        destination_ip="203.0.113.5",
        destination_port=8080,
    )

    result = engine.process_incoming_packet(incoming)

    assert result.success
    assert result.translated_packet.source_ip == "198.51.100.20"
    assert result.translated_packet.source_port == 45000


def test_duplicate_port_forward_rule(engine: NATEngine, device_server: VirtualDevice):
    """Test duplicate port forward rule rejection."""
    engine.add_device(device_server)

    rule1 = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )
    rule2 = PortForwardRule(
        id="pf-02",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=8080,
    )

    engine.add_port_forward(rule1)
    with pytest.raises(PortForwardConflict):
        engine.add_port_forward(rule2)


def test_tcp_udp_port_forward_independence(engine: NATEngine, device_server: VirtualDevice):
    """Test TCP and UDP can use same public port for port forwarding."""
    engine.add_device(device_server)

    tcp_rule = PortForwardRule(
        id="pf-tcp",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )
    udp_rule = PortForwardRule(
        id="pf-udp",
        protocol=Protocol.UDP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=53,
    )

    engine.add_port_forward(tcp_rule)
    engine.add_port_forward(udp_rule)

    assert len(engine.port_forward_rules) == 2


def test_invalid_port_forward_public_ip(engine: NATEngine, device_server: VirtualDevice):
    """Test port forward with wrong public IP."""
    engine.add_device(device_server)

    rule = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.99",  # Wrong public IP
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )

    with pytest.raises(PortForwardConflict):
        engine.add_port_forward(rule)


def test_invalid_port_forward_private_ip(engine: NATEngine):
    """Test port forward to non-existent private IP."""
    rule = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.99",  # No device at this IP
        private_port=80,
    )

    with pytest.raises(DeviceNotFound):
        engine.add_port_forward(rule)


def test_invalid_port(engine: NATEngine):
    """Test invalid port rejection."""
    with pytest.raises(InvalidPort):
        Packet(protocol=Protocol.TCP, source_ip="192.168.1.10", source_port=0, destination_ip="8.8.8.8", destination_port=443)

    with pytest.raises(InvalidPort):
        Packet(protocol=Protocol.TCP, source_ip="192.168.1.10", source_port=70000, destination_ip="8.8.8.8", destination_port=443)


def test_invalid_protocol():
    """Test invalid protocol rejection."""
    with pytest.raises(UnsupportedProtocol):
        Packet(protocol="ICMP", source_ip="192.168.1.10", source_port=50000, destination_ip="8.8.8.8", destination_port=443)


# NAT Table Tests

def test_get_nat_entries(engine: NATEngine, device_pc: VirtualDevice):
    """Test getting NAT entries."""
    engine.add_device(device_pc)

    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )
    engine.process_outgoing_packet(packet)

    entries = engine.get_nat_entries()
    assert len(entries) == 1
    assert entries[0].private_ip == "192.168.1.10"
    assert entries[0].public_ip == "203.0.113.5"


def test_remove_nat_entry(engine: NATEngine, device_pc: VirtualDevice):
    """Test removing NAT entry."""
    engine.add_device(device_pc)

    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )
    engine.process_outgoing_packet(packet)

    flow_key = packet.flow_key()
    removed = engine.remove_nat_entry(flow_key)

    assert removed is not None
    assert len(engine.get_nat_entries()) == 0


def test_clear_nat_table(engine: NATEngine, device_pc: VirtualDevice):
    """Test clearing NAT table."""
    engine.add_device(device_pc)

    for port in range(50000, 50003):
        packet = Packet(
            protocol=Protocol.TCP,
            source_ip="192.168.1.10",
            source_port=port,
            destination_ip="8.8.8.8",
            destination_port=443,
        )
        engine.process_outgoing_packet(packet)

    assert len(engine.get_nat_entries()) == 3

    engine.clear_nat_table()

    assert len(engine.get_nat_entries()) == 0
    assert engine._next_port == engine._port_range_start


def test_remove_port_forward_rule(engine: NATEngine, device_server: VirtualDevice):
    """Test removing port forward rule."""
    engine.add_device(device_server)

    rule = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )
    engine.add_port_forward(rule)

    removed = engine.remove_port_forward("pf-01")

    assert removed.id == "pf-01"
    assert len(engine.port_forward_rules) == 0


# NAT Port Exhaustion Test

def test_nat_port_exhaustion(engine: NATEngine, device_pc: VirtualDevice):
    """Test NAT port exhaustion."""
    engine.add_device(device_pc)

    # Fill up all ports - create unique flows to consume all public ports
    port_count = engine._port_range_end - engine._port_range_start + 1
    for i in range(port_count):
        packet = Packet(
            protocol=Protocol.TCP,
            source_ip="192.168.1.10",
            source_port=50000 + i,
            destination_ip="8.8.8.8",
            destination_port=443,
        )
        result = engine.process_outgoing_packet(packet)
        if not result.success:
            break

    # Next one should fail - use a source port not used above
    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=61000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )
    result = engine.process_outgoing_packet(packet)

    assert not result.success
    assert "no available ports" in result.error.lower()


# Transformation History Tests

def test_snat_transformation_history(engine: NATEngine, device_pc: VirtualDevice):
    """Test SNAT transformation history structure."""
    engine.add_device(device_pc)

    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )

    result = engine.process_outgoing_packet(packet)

    assert result.success
    assert len(result.transformations) == 3
    assert result.transformations[0].stage == Stage.LAN
    assert result.transformations[0].action == Action.ORIGINAL
    assert result.transformations[1].stage == Stage.NAT_GATEWAY
    assert result.transformations[1].action == Action.SNAT
    assert result.transformations[2].stage == Stage.INTERNET
    assert result.transformations[2].action == Action.FORWARD


def test_dnat_transformation_history(engine: NATEngine, device_server: VirtualDevice):
    """Test DNAT transformation history structure."""
    engine.add_device(device_server)

    rule = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )
    engine.add_port_forward(rule)

    incoming = Packet(
        protocol=Protocol.TCP,
        source_ip="198.51.100.20",
        source_port=45000,
        destination_ip="203.0.113.5",
        destination_port=8080,
    )

    result = engine.process_incoming_packet(incoming)

    assert result.success
    assert len(result.transformations) == 3
    assert result.transformations[0].stage == Stage.INTERNET
    assert result.transformations[0].action == Action.ORIGINAL
    assert result.transformations[1].stage == Stage.NAT_GATEWAY
    assert result.transformations[1].action == Action.DNAT
    assert result.transformations[2].stage == Stage.LAN
    assert result.transformations[2].action == Action.FORWARD


# Scenario Tests

def test_scenario_1_tcp_snat(engine: NATEngine, device_pc: VirtualDevice):
    """Test Scenario 1: Basic TCP SNAT."""
    engine.add_device(device_pc)

    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )

    result = engine.process_outgoing_packet(packet)

    assert result.success
    assert str(result.translated_packet) == "TCP 203.0.113.5:40000 -> 8.8.8.8:443"


def test_scenario_2_same_flow_reuse(engine: NATEngine, device_pc: VirtualDevice):
    """Test Scenario 2: Same flow reuses mapping."""
    engine.add_device(device_pc)

    packet = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )

    result1 = engine.process_outgoing_packet(packet)
    result2 = engine.process_outgoing_packet(packet)

    assert result1.translated_packet.source_port == 40000
    assert result2.translated_packet.source_port == 40000


def test_scenario_3_another_device(engine: NATEngine, device_pc: VirtualDevice, device_server: VirtualDevice):
    """Test Scenario 3: Another device gets different port."""
    engine.add_device(device_pc)
    engine.add_device(device_server)

    packet1 = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.10",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )
    packet2 = Packet(
        protocol=Protocol.TCP,
        source_ip="192.168.1.20",
        source_port=50000,
        destination_ip="8.8.8.8",
        destination_port=443,
    )

    result1 = engine.process_outgoing_packet(packet1)
    result2 = engine.process_outgoing_packet(packet2)

    assert result1.translated_packet.source_port == 40000
    assert result2.translated_packet.source_port == 40001


def test_scenario_4_dnat(engine: NATEngine, device_server: VirtualDevice):
    """Test Scenario 4: DNAT port forwarding."""
    engine.add_device(device_server)

    rule = PortForwardRule(
        id="pf-01",
        protocol=Protocol.TCP,
        public_ip="203.0.113.5",
        public_port=8080,
        private_ip="192.168.1.20",
        private_port=80,
    )
    engine.add_port_forward(rule)

    incoming = Packet(
        protocol=Protocol.TCP,
        source_ip="198.51.100.20",
        source_port=45000,
        destination_ip="203.0.113.5",
        destination_port=8080,
    )

    result = engine.process_incoming_packet(incoming)

    assert result.success
    assert str(result.translated_packet) == "TCP 198.51.100.20:45000 -> 192.168.1.20:80"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])