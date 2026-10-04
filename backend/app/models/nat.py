"""NAT models for translation entries and rules."""

from enum import Enum
from pydantic import BaseModel, field_validator

from app.models.exceptions import InvalidIPAddress, InvalidPort, UnsupportedProtocol
from app.models.packet import Packet, Protocol


class NATState(str, Enum):
    """State of NAT mapping."""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


class NATEntry(BaseModel):
    """NAT translation table entry."""

    protocol: Protocol
    private_ip: str
    private_port: int
    public_ip: str
    public_port: int
    destination_ip: str
    destination_port: int
    state: NATState = NATState.ACTIVE

    @field_validator("protocol", mode="before")
    @classmethod
    def validate_protocol(cls, v: str | Protocol) -> Protocol:
        if isinstance(v, str):
            return Protocol.normalize(v)
        return v

    @field_validator("private_ip", "public_ip", "destination_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 4:
            raise InvalidIPAddress(f"Invalid IP format: {v}")
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    raise InvalidIPAddress(f"Invalid IP octet: {part}")
            except ValueError:
                raise InvalidIPAddress(f"Invalid IP octet: {part}")
        return v

    @field_validator("private_port", "public_port", "destination_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not isinstance(v, int) or v < 1 or v > 65535:
            raise InvalidPort(f"Port must be between 1 and 65535, got: {v}")
        return v

    def flow_key(self) -> tuple:
        """Key for outbound flow lookup."""
        return (self.protocol.value, self.private_ip, self.private_port, self.destination_ip, self.destination_port)

    def reverse_flow_key(self) -> tuple:
        """Key for inbound response lookup."""
        return (self.protocol.value, self.public_ip, self.public_port, self.destination_ip, self.destination_port)

    def __str__(self) -> str:
        return f"{self.protocol.value} {self.private_ip}:{self.private_port} -> {self.public_ip}:{self.public_port} (dest: {self.destination_ip}:{self.destination_port})"


class PortForwardRule(BaseModel):
    """Port forwarding (DNAT) rule."""

    id: str
    protocol: Protocol
    public_ip: str
    public_port: int
    private_ip: str
    private_port: int

    @field_validator("protocol", mode="before")
    @classmethod
    def validate_protocol(cls, v: str | Protocol) -> Protocol:
        if isinstance(v, str):
            return Protocol.normalize(v)
        return v

    @field_validator("public_ip", "private_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 4:
            raise InvalidIPAddress(f"Invalid IP format: {v}")
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    raise InvalidIPAddress(f"Invalid IP octet: {part}")
            except ValueError:
                raise InvalidIPAddress(f"Invalid IP octet: {part}")
        return v

    @field_validator("public_port", "private_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not isinstance(v, int) or v < 1 or v > 65535:
            raise InvalidPort(f"Port must be between 1 and 65535, got: {v}")
        return v

    def match_key(self) -> tuple:
        """Key for matching incoming packets."""
        return (self.protocol.value, self.public_ip, self.public_port)

    def __str__(self) -> str:
        return f"{self.protocol.value} {self.public_ip}:{self.public_port} -> {self.private_ip}:{self.private_port}"


class Stage(str, Enum):
    """Packet processing stage."""
    LAN = "LAN"
    NAT_GATEWAY = "NAT_GATEWAY"
    INTERNET = "INTERNET"


class Action(str, Enum):
    """Transformation action."""
    ORIGINAL = "ORIGINAL"
    SNAT = "SNAT"
    DNAT = "DNAT"
    FORWARD = "FORWARD"


class PacketTransformation(BaseModel):
    """Single transformation step in packet processing."""

    stage: Stage
    action: Action
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int
    description: str

    def __str__(self) -> str:
        return f"[{self.stage}] {self.action}: {self.source_ip}:{self.source_port} -> {self.destination_ip}:{self.destination_port} ({self.description})"


class SimulationResult(BaseModel):
    """Result of a packet simulation."""

    original_packet: Packet
    translated_packet: Packet | None
    transformations: list[PacketTransformation]
    success: bool
    error: str | None = None

    def __str__(self) -> str:
        if not self.success:
            return f"FAILED: {self.error}"
        result = f"SUCCESS: {self.original_packet} -> {self.translated_packet}"
        for t in self.transformations:
            result += f"\n  {t}"
        return result