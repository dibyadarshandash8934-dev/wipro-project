"""Network API schemas."""

from pydantic import BaseModel, field_validator
from ipaddress import IPv4Address, IPv4Network


class NetworkBase(BaseModel):
    """Base network schema."""

    cidr: str
    gateway_ip: str
    public_ip: str

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, v: str) -> str:
        try:
            network = IPv4Network(v, strict=False)
            if network.version != 4:
                raise ValueError("Only IPv4 networks are supported")
            if network.prefixlen < 8 or network.prefixlen > 30:
                raise ValueError("CIDR prefix must be between /8 and /30")
        except ValueError as e:
            raise ValueError(f"Invalid CIDR: {e}")
        return v

    @field_validator("gateway_ip", "public_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        try:
            IPv4Address(v)
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")
        return v


class NetworkCreate(NetworkBase):
    """Request schema for creating a network."""

    pass


class NetworkResponse(NetworkBase):
    """Response schema for network."""

    pass


class NetworkDeleteResponse(BaseModel):
    """Response schema for network deletion."""

    success: bool = True
    message: str = "Network deleted successfully"