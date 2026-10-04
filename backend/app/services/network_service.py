"""Network service for managing virtual network and devices."""

from app.models import (
    Network,
    VirtualDevice,
    DeviceType,
    InvalidIPAddress,
    IPOutsideNetwork,
    DuplicateIPAddress,
    DeviceNotFound,
)
from app.models.exceptions import NetworkError


class NetworkService:
    """Manages virtual network and devices."""

    def __init__(self, network: Network):
        self._network = network
        self._devices: dict[str, VirtualDevice] = {}  # id -> device
        self._ip_to_device_id: dict[str, str] = {}  # ip -> device id

    @property
    def network(self) -> Network:
        return self._network

    @property
    def devices(self) -> list[VirtualDevice]:
        return list(self._devices.values())

    def add_device(self, device: VirtualDevice) -> VirtualDevice:
        """Add a device to the network."""
        # Validate IP format
        try:
            self._network.get_network()
        except Exception as e:
            raise NetworkError(f"Invalid network: {e}")

        # Check if IP is valid for host assignment
        if not self._network.is_valid_host_ip(device.ip):
            raise IPOutsideNetwork(f"IP {device.ip} is not a valid host IP in network {self._network.cidr}")

        # Check for duplicate IP
        if device.ip in self._ip_to_device_id:
            existing_id = self._ip_to_device_id[device.ip]
            existing_device = self._devices[existing_id]
            raise DuplicateIPAddress(
                f"IP {device.ip} already assigned to device {existing_device.name} ({existing_id})"
            )

        # Check for duplicate ID
        if device.id in self._devices:
            raise DuplicateIPAddress(f"Device with ID {device.id} already exists")

        self._devices[device.id] = device
        self._ip_to_device_id[device.ip] = device.id
        return device

    def remove_device(self, device_id: str) -> VirtualDevice:
        """Remove a device from the network."""
        if device_id not in self._devices:
            raise DeviceNotFound(f"Device {device_id} not found")
        device = self._devices.pop(device_id)
        self._ip_to_device_id.pop(device.ip, None)
        return device

    def get_device(self, device_id: str) -> VirtualDevice:
        """Get a device by ID."""
        if device_id not in self._devices:
            raise DeviceNotFound(f"Device {device_id} not found")
        return self._devices[device_id]

    def get_device_by_ip(self, ip: str) -> VirtualDevice | None:
        """Get a device by IP address."""
        device_id = self._ip_to_device_id.get(ip)
        if device_id:
            return self._devices[device_id]
        return None

    def find_device(self, name: str) -> VirtualDevice | None:
        """Find a device by name."""
        for device in self._devices.values():
            if device.name == name:
                return device
        return None

    def validate_device_ip(self, ip: str) -> bool:
        """Validate if an IP can be assigned to a device."""
        return self._network.is_valid_host_ip(ip) and ip not in self._ip_to_device_id

    def clear_devices(self) -> None:
        """Remove all devices."""
        self._devices.clear()
        self._ip_to_device_id.clear()