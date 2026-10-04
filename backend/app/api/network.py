"""Network API routes."""

from fastapi import APIRouter, status
from app.api.schemas.network import NetworkCreate, NetworkResponse, NetworkDeleteResponse
from app.api.schemas.simulation import ResetResponse
from app.models import Network
from app.services import simulation_state

router = APIRouter(prefix="/network", tags=["Network"])


@router.post(
    "",
    response_model=NetworkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create/configure the virtual network",
    description="Create a new virtual network with NAT gateway configuration. Replaces any existing network.",
)
async def create_network(network_data: NetworkCreate) -> NetworkResponse:
    """Create a new network configuration."""
    network = Network(
        cidr=network_data.cidr,
        gateway_ip=network_data.gateway_ip,
        public_ip=network_data.public_ip,
    )
    simulation_state.create_network(network)
    return NetworkResponse(
        cidr=network.cidr,
        gateway_ip=network.gateway_ip,
        public_ip=network.public_ip,
    )


@router.get(
    "",
    response_model=NetworkResponse,
    summary="Get current network configuration",
    description="Return the current network configuration if one exists.",
)
async def get_network() -> NetworkResponse:
    """Get the current network configuration."""
    if not simulation_state.is_configured:
        from app.models.exceptions import NetworkError
        raise NetworkError("Network not configured")
    network = simulation_state.network
    return NetworkResponse(
        cidr=network.cidr,
        gateway_ip=network.gateway_ip,
        public_ip=network.public_ip,
    )


@router.delete(
    "",
    response_model=NetworkDeleteResponse,
    summary="Delete network configuration",
    description="Delete the current network configuration and reset simulation state.",
)
async def delete_network() -> NetworkDeleteResponse:
    """Delete the network and reset simulation."""
    simulation_state.reset()
    return NetworkDeleteResponse()