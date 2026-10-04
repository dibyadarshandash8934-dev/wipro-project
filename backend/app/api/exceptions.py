"""Exception handlers for converting domain exceptions to HTTP responses."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

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


async def network_error_handler(request: Request, exc: NetworkError) -> JSONResponse:
    """Handle network-related errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "error": str(exc)},
    )


async def invalid_network_handler(request: Request, exc: InvalidNetwork) -> JSONResponse:
    """Handle invalid network errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "error": str(exc)},
    )


async def invalid_ip_address_handler(request: Request, exc: InvalidIPAddress) -> JSONResponse:
    """Handle invalid IP address errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "error": str(exc)},
    )


async def ip_outside_network_handler(request: Request, exc: IPOutsideNetwork) -> JSONResponse:
    """Handle IP outside network errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "error": str(exc)},
    )


async def device_not_found_handler(request: Request, exc: DeviceNotFound) -> JSONResponse:
    """Handle device not found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"success": False, "error": str(exc)},
    )


async def duplicate_ip_address_handler(request: Request, exc: DuplicateIPAddress) -> JSONResponse:
    """Handle duplicate IP address errors."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"success": False, "error": str(exc)},
    )


async def invalid_port_handler(request: Request, exc: InvalidPort) -> JSONResponse:
    """Handle invalid port errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "error": str(exc)},
    )


async def unsupported_protocol_handler(request: Request, exc: UnsupportedProtocol) -> JSONResponse:
    """Handle unsupported protocol errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "error": str(exc)},
    )


async def port_forward_conflict_handler(request: Request, exc: PortForwardConflict) -> JSONResponse:
    """Handle port forward conflict errors."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"success": False, "error": str(exc)},
    )


async def nat_port_exhausted_handler(request: Request, exc: NATPortExhausted) -> JSONResponse:
    """Handle NAT port exhausted errors."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"success": False, "error": str(exc)},
    )


async def nat_mapping_not_found_handler(request: Request, exc: NATMappingNotFound) -> JSONResponse:
    """Handle NAT mapping not found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"success": False, "error": str(exc)},
    )


def register_exception_handlers(app) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(NetworkError, network_error_handler)
    app.add_exception_handler(InvalidNetwork, invalid_network_handler)
    app.add_exception_handler(InvalidIPAddress, invalid_ip_address_handler)
    app.add_exception_handler(IPOutsideNetwork, ip_outside_network_handler)
    app.add_exception_handler(DeviceNotFound, device_not_found_handler)
    app.add_exception_handler(DuplicateIPAddress, duplicate_ip_address_handler)
    app.add_exception_handler(InvalidPort, invalid_port_handler)
    app.add_exception_handler(UnsupportedProtocol, unsupported_protocol_handler)
    app.add_exception_handler(PortForwardConflict, port_forward_conflict_handler)
    app.add_exception_handler(NATPortExhausted, nat_port_exhausted_handler)
    app.add_exception_handler(NATMappingNotFound, nat_mapping_not_found_handler)