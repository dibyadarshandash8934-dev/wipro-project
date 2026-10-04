"""Device API schemas."""

from pydantic import BaseModel, field_validator
from typing import Literal

from app.models.device import DeviceType


class DeviceCreate(BaseModel):
    """Request schema for creating a device."""

    name: str
    ip: str
    type: DeviceType = DeviceType.PC

    @field_validator("ip")
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


class DeviceResponse(BaseModel):
    """Response schema for device."""

    id: str
    name: str
    ip: str
    type: DeviceType


class DeviceDeleteResponse(BaseModel):
    """Response schema for device deletion."""

    success: bool = True
    message: str = "Device deleted successfully"