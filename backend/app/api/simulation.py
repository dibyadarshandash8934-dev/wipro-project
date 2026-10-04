"""Simulation state API routes."""

from fastapi import APIRouter, status
from app.api.schemas.simulation import SimulationStateResponse, ResetResponse, SimulationStatsResponse
from app.api.schemas.error import ErrorResponse
from app.api.schemas.network import NetworkResponse
from app.api.schemas.device import DeviceResponse
from app.api.schemas.nat import NATEntryResponse, PortForwardResponse
from app.services import simulation_state
from app.models.exceptions import NetworkError

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.get(
    "/state",
    response_model=SimulationStateResponse,
    summary="Get complete simulation state",
    description="Return a complete snapshot of the current simulation state including network, devices, NAT entries, and port forward rules.",
    responses={
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def get_simulation_state() -> SimulationStateResponse:
    """Get the complete simulation state."""
    if not simulation_state.is_configured:
        return SimulationStateResponse(
            network=None,
            devices=[],
            nat_entries=[],
            port_forward_rules=[],
        )

    engine = simulation_state.engine
    network = simulation_state.network

    # Convert network
    network_resp = None
    if network:
        network_resp = NetworkResponse(
            cidr=network.cidr,
            gateway_ip=network.gateway_ip,
            public_ip=network.public_ip,
        )

    # Convert devices
    devices = [
        DeviceResponse(
            id=d.id,
            name=d.name,
            ip=d.ip,
            type=d.type,
        )
        for d in engine.devices
    ]

    # Convert NAT entries
    nat_entries = [
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
        for e in engine.get_nat_entries()
    ]

    # Convert port forward rules
    port_forward_rules = [
        PortForwardResponse(
            id=r.id,
            protocol=r.protocol,
            public_ip=r.public_ip,
            public_port=r.public_port,
            private_ip=r.private_ip,
            private_port=r.private_port,
        )
        for r in engine.get_port_forward_rules()
    ]

    return SimulationStateResponse(
        network=network_resp,
        devices=devices,
        nat_entries=nat_entries,
        port_forward_rules=port_forward_rules,
    )


@router.get(
    "/stats",
    response_model=SimulationStatsResponse,
    summary="Get simulation statistics",
    description="Return current simulation statistics including packet counts and processing times.",
    responses={
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def get_simulation_stats() -> SimulationStatsResponse:
    """Get the simulation statistics."""
    if not simulation_state.is_configured:
        return SimulationStatsResponse(
            total_packets=0,
            successful_packets=0,
            failed_packets=0,
            snat_packets=0,
            dnat_packets=0,
            reverse_nat_packets=0,
            active_nat_mappings=0,
            active_port_forward_rules=0,
            average_processing_time_ms=0.0,
        )

    engine = simulation_state.engine
    metrics = engine.metrics

    return SimulationStatsResponse(
        total_packets=metrics.total_packets,
        successful_packets=metrics.successful_packets,
        failed_packets=metrics.failed_packets,
        snat_packets=metrics.snat_packets,
        dnat_packets=metrics.dnat_packets,
        reverse_nat_packets=metrics.reverse_nat_packets,
        active_nat_mappings=len(engine.get_nat_entries()),
        active_port_forward_rules=len(engine.get_port_forward_rules()),
        average_processing_time_ms=metrics.average_processing_time_ms,
    )


@router.post(
    "/reset",
    response_model=ResetResponse,
    summary="Reset simulation",
    description="Reset the simulation to an empty state. Removes network, devices, NAT mappings, port forward rules, and allocated ports.",
)
async def reset_simulation() -> ResetResponse:
    """Reset the simulation."""
    # Always clear engine state if engine exists, regardless of is_configured
    if simulation_state.engine is not None:
        simulation_state.engine.clear_all_state()
    simulation_state.reset()
    return ResetResponse()