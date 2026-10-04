"""NAT API schemas."""

from pydantic import BaseModel, field_validator
from typing import Literal

from app.models.nat import NATState
from app.models.packet import Protocol


class PortForwardBase(BaseModel):
    """Base port forward schema."""

    protocol: Protocol
    public_ip: str
    public_port: int
    private_ip: str
    private_port: int

    @field_validator("public_ip", "private_ip")
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

    @field_validator("public_port", "private_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not isinstance(v, int) or v < 1 or v > 65535:
            raise ValueError(f"Port must be between 1 and 65535, got: {v}")
        return v


class PortForwardCreate(PortForwardBase):
    """Request schema for creating a port forward rule."""

    pass


class PortForwardResponse(PortForwardBase):
    """Response schema for port forward rule."""

    id: str


class NATEntryResponse(BaseModel):
    """Response schema for NAT entry."""

    protocol: Protocol
    private_ip: str
    private_port: int
    public_ip: str
    public_port: int
    destination_ip: str
    destination_port: int
    state: NATState


class NATTableResponse(BaseModel):
    """Response schema for NAT table."""

    entries: list[NATEntryResponse]


class NATTableClearResponse(BaseModel):
    """Response schema for clearing NAT table."""

    success: bool = True
    message: str = "NAT table cleared successfully"