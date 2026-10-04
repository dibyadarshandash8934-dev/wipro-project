"""Packet simulation API schemas."""

from pydantic import BaseModel, field_validator
from typing import Literal

from app.models.packet import Protocol
from app.models.nat import Stage, Action


class Direction(str):
    """Packet direction enum."""
    LAN_TO_INTERNET = "LAN_TO_INTERNET"
    INTERNET_TO_LAN = "INTERNET_TO_LAN"


class PacketSimulationRequest(BaseModel):
    """Request schema for packet simulation."""

    direction: Literal["LAN_TO_INTERNET", "INTERNET_TO_LAN"]
    protocol: Protocol
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int

    @field_validator("source_ip", "destination_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 4:
            raise ValueError(f"Invalid IP format: {v}")
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError(f"Invalid IP octet: {part}")
            except ValueError:
                raise ValueError(f"Invalid IP octet: {part}")
        return v

    @field_validator("source_port", "destination_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not isinstance(v, int) or v < 1 or v > 65535:
            raise ValueError(f"Port must be between 1 and 65535, got: {v}")
        return v


class PacketResponse(BaseModel):
    """Response schema for packet."""

    protocol: Protocol
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int


class TransformationResponse(BaseModel):
    """Response schema for packet transformation."""

    stage: Stage
    action: Action
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int
    description: str


class NATEntryRef(BaseModel):
    """Reference to a NAT entry in simulation response."""

    protocol: Protocol
    private_ip: str
    private_port: int
    public_ip: str
    public_port: int
    destination_ip: str
    destination_port: int
    state: str


class PacketSimulationResponse(BaseModel):
    """Response schema for packet simulation."""

    success: bool
    action: str | None = None
    original_packet: PacketResponse
    translated_packet: PacketResponse | None = None
    transformations: list[TransformationResponse] = []
    nat_entry: NATEntryRef | None = None
    error: str | None = None