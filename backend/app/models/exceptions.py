"""Network-related exceptions."""

class NetworkError(Exception):
    """Base network error."""
    pass


class InvalidNetwork(NetworkError):
    """Invalid network configuration."""
    pass


class InvalidIPAddress(NetworkError):
    """Invalid IP address."""
    pass


class IPOutsideNetwork(NetworkError):
    """IP address outside the configured network."""
    pass


class DeviceNotFound(NetworkError):
    """Device not found in network."""
    pass


class DuplicateIPAddress(NetworkError):
    """Duplicate IP address assigned to devices."""
    pass


class InvalidPort(NetworkError):
    """Invalid port number."""
    pass


class UnsupportedProtocol(NetworkError):
    """Unsupported protocol."""
    pass


class PortForwardConflict(NetworkError):
    """Port forwarding rule conflict."""
    pass


class NATPortExhausted(NetworkError):
    """No available public ports for NAT."""
    pass


class NATMappingNotFound(NetworkError):
    """NAT mapping not found for packet."""
    pass