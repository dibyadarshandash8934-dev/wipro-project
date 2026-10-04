"""NAT API routes - port forwarding and NAT table."""

from fastapi import APIRouter, status
from app.api.schemas.nat import (
    PortForwardCreate,
    PortForwardResponse,
    NATEntryResponse,
    NATTableResponse,
    NATTableClearResponse,
)
from app.api.schemas.error import ErrorResponse
from app.models import PortForwardRule, Protocol
from app.services import simulation_state
from app.models.exceptions import NetworkError, DeviceNotFound

router = APIRouter(prefix="/nat", tags=["NAT"])


def _get_engine():
    """Get the current engine or raise an error."""
    if not simulation_state.is_configured:
        raise NetworkError("Network not configured. Create a network first.")
    return simulation_state.engine


@router.post(
    "/port-forward",
    response_model=PortForwardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a port forwarding rule",
    description="Add a new port forwarding (DNAT) rule. The public IP must match the NAT gateway public IP.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid IP or port"},
        404: {"model": ErrorResponse, "description": "No device at private IP"},
        409: {"model": ErrorResponse, "description": "Port forward conflict"},
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def add_port_forward(rule_data: PortForwardCreate) -> PortForwardResponse:
    """Add a port forwarding rule."""
    engine = _get_engine()
    rule = PortForwardRule(
        id=f"pf-{rule_data.protocol.value.lower()}-{rule_data.public_port}",
        protocol=rule_data.protocol,
        public_ip=rule_data.public_ip,
        public_port=rule_data.public_port,
        private_ip=rule_data.private_ip,
        private_port=rule_data.private_port,
    )
    engine.add_port_forward(rule)
    return PortForwardResponse(
        id=rule.id,
        protocol=rule.protocol,
        public_ip=rule.public_ip,
        public_port=rule.public_port,
        private_ip=rule.private_ip,
        private_port=rule.private_port,
    )


@router.get(
    "/port-forward",
    response_model=list[PortForwardResponse],
    summary="Get all port forwarding rules",
    description="Return all active port forwarding rules.",
    responses={
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def get_port_forward_rules() -> list[PortForwardResponse]:
    """Get all port forwarding rules."""
    engine = _get_engine()
    rules = engine.get_port_forward_rules()
    return [
        PortForwardResponse(
            id=r.id,
            protocol=r.protocol,
            public_ip=r.public_ip,
            public_port=r.public_port,
            private_ip=r.private_ip,
            private_port=r.private_port,
        )
        for r in rules
    ]


@router.delete(
    "/port-forward/{rule_id}",
    response_model=dict,
    summary="Remove a port forwarding rule",
    description="Remove a port forwarding rule by its ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Rule not found"},
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def delete_port_forward(rule_id: str) -> dict:
    """Remove a port forwarding rule."""
    engine = _get_engine()
    engine.remove_port_forward(rule_id)
    return {"success": True, "message": f"Port forward rule {rule_id} deleted successfully"}


@router.get(
    "/table",
    response_model=NATTableResponse,
    summary="Get NAT translation table",
    description="Return all active NAT mappings.",
    responses={
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def get_nat_table() -> NATTableResponse:
    """Get the NAT translation table."""
    engine = _get_engine()
    entries = engine.get_nat_entries()
    return NATTableResponse(
        entries=[
            NATEntryResponse(
                protocol=e.protocol,
                private_ip=e.private_ip,
                private_port=e.private_port,
                public_ip=e.public_ip,
                public_port=e.public_port,
                destination_ip=e.destination_ip,
                destination_port=e.destination_port,
                state=e.state,
            )
            for e in entries
        ]
    )


@router.delete(
    "/table",
    response_model=NATTableClearResponse,
    summary="Clear NAT translation table",
    description="Clear all active NAT mappings.",
    responses={
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def clear_nat_table() -> NATTableClearResponse:
    """Clear the NAT translation table."""
    engine = _get_engine()
    engine.clear_nat_table()
    return NATTableClearResponse()