"""Devices API routes."""

from fastapi import APIRouter, status
from app.api.schemas.device import DeviceCreate, DeviceResponse, DeviceDeleteResponse
from app.api.schemas.error import ErrorResponse
from app.models import VirtualDevice, DeviceType
from app.services import simulation_state
from app.models.exceptions import NetworkError, DeviceNotFound

router = APIRouter(prefix="/devices", tags=["Devices"])


def _get_engine():
    """Get the current engine or raise an error."""
    if not simulation_state.is_configured:
        raise NetworkError("Network not configured. Create a network first.")
    return simulation_state.engine


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a virtual device",
    description="Add a new virtual device to the network.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid IP or IP outside network"},
        409: {"model": ErrorResponse, "description": "Duplicate IP address"},
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def create_device(device_data: DeviceCreate) -> DeviceResponse:
    """Add a new device to the network."""
    engine = _get_engine()
    device = VirtualDevice(
        id=device_data.name.lower().replace(" ", "-"),
        name=device_data.name,
        ip=device_data.ip,
        type=device_data.type,
    )
    engine.add_device(device)
    return DeviceResponse(
        id=device.id,
        name=device.name,
        ip=device.ip,
        type=device.type,
    )


@router.get(
    "",
    response_model=list[DeviceResponse],
    summary="Get all virtual devices",
    description="Return all virtual devices in the network.",
    responses={
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def get_devices() -> list[DeviceResponse]:
    """Get all devices in the network."""
    engine = _get_engine()
    devices = engine.devices
    return [
        DeviceResponse(
            id=d.id,
            name=d.name,
            ip=d.ip,
            type=d.type,
        )
        for d in devices
    ]


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Get a virtual device by ID",
    description="Return a specific virtual device by its ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Device not found"},
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def get_device(device_id: str) -> DeviceResponse:
    """Get a device by ID."""
    engine = _get_engine()
    device = engine.get_device(device_id)
    return DeviceResponse(
        id=device.id,
        name=device.name,
        ip=device.ip,
        type=device.type,
    )


@router.delete(
    "/{device_id}",
    response_model=DeviceDeleteResponse,
    summary="Remove a virtual device",
    description="Remove a virtual device from the network by its ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Device not found"},
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def delete_device(device_id: str) -> DeviceDeleteResponse:
    """Remove a device from the network."""
    engine = _get_engine()
    engine.remove_device(device_id)
    return DeviceDeleteResponse()