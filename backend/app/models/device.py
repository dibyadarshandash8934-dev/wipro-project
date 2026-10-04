"""Virtual device model."""

from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Literal

from app.models.exceptions import InvalidIPAddress


class DeviceType(str, Enum):
    """Types of virtual devices."""
    PC = "pc"
    SERVER = "server"
    LAPTOP = "laptop"
    PHONE = "phone"
    IOT = "iot"


class VirtualDevice(BaseModel):
    """Virtual device in the network."""

    id: str
    name: str
    ip: str
    type: DeviceType = DeviceType.PC

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Basic IP format validation."""
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

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: str | DeviceType) -> DeviceType:
        if isinstance(v, str):
            try:
                return DeviceType(v.lower())
            except ValueError:
                raise ValueError(f"Invalid device type: {v}. Must be one of: {[t.value for t in DeviceType]}")
        return v