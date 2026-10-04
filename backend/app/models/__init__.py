"""Models package exports."""

from app.models.exceptions import (
    NetworkError,
    InvalidNetwork,
    InvalidIPAddress,
    IPOutsideNetwork,
    DeviceNotFound,
    DuplicateIPAddress,
    InvalidPort,
    UnsupportedProtocol,
    PortForwardConflict,
    NATPortExhausted,
    NATMappingNotFound,
)

from app.models.network import Network
from app.models.device import VirtualDevice, DeviceType
from app.models.packet import Packet, Protocol
from app.models.nat import (
    NATEntry,
    NATState,
    PortForwardRule,
    PacketTransformation,
    Stage,
    Action,
    SimulationResult,
)

__all__ = [
    # Exceptions
    "NetworkError",
    "InvalidNetwork",
    "InvalidIPAddress",
    "IPOutsideNetwork",
    "DeviceNotFound",
    "DuplicateIPAddress",
    "InvalidPort",
    "UnsupportedProtocol",
    "PortForwardConflict",
    "NATPortExhausted",
    "NATMappingNotFound",
    # Models
    "Network",
    "VirtualDevice",
    "DeviceType",
    "Packet",
    "Protocol",
    "NATEntry",
    "NATState",
    "PortForwardRule",
    "PacketTransformation",
    "Stage",
    "Action",
    "SimulationResult",
]