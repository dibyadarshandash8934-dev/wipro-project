"""Packet models for NAT simulation."""

from enum import Enum
from pydantic import BaseModel, field_validator

from app.models.exceptions import InvalidIPAddress, InvalidPort, UnsupportedProtocol


class Protocol(str, Enum):
    """Supported transport protocols."""
    TCP = "TCP"
    UDP = "UDP"

    @classmethod
    def normalize(cls, v: str) -> "Protocol":
        """Normalize protocol string to enum."""
        upper = v.upper()
        if upper in ("TCP", "UDP"):
            return Protocol(upper)
        raise UnsupportedProtocol(f"Unsupported protocol: {v}. Supported: TCP, UDP")


class Packet(BaseModel):
    """Network packet representation."""

    protocol: Protocol
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int

    @field_validator("protocol", mode="before")
    @classmethod
    def validate_protocol(cls, v: str | Protocol) -> Protocol:
        if isinstance(v, str):
            return Protocol.normalize(v)
        return v

    @field_validator("source_ip", "destination_ip")
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

    @field_validator("source_port", "destination_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not isinstance(v, int) or v < 1 or v > 65535:
            raise InvalidPort(f"Port must be between 1 and 65535, got: {v}")
        return v

    def flow_key(self) -> tuple:
        """Generate a flow key for NAT mapping lookup."""
        return (self.protocol.value, self.source_ip, self.source_port, self.destination_ip, self.destination_port)

    def reverse_flow_key(self) -> tuple:
        """Generate reverse flow key for incoming response lookup."""
        return (self.protocol.value, self.destination_ip, self.destination_port, self.source_ip, self.source_port)

    def copy_with(self, **changes) -> "Packet":
        """Create a copy with modified fields."""
        data = self.model_dump()
        data.update(changes)
        return Packet(**data)

    def __str__(self) -> str:
        return f"{self.protocol.value} {self.source_ip}:{self.source_port} -> {self.destination_ip}:{self.destination_port}"