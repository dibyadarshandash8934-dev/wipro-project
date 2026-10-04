"""Packet simulation API routes."""

from fastapi import APIRouter, status
from app.api.schemas.packet import (
    PacketSimulationRequest,
    PacketSimulationResponse,
    PacketResponse,
    TransformationResponse,
    NATEntryRef,
)
from app.api.schemas.error import ErrorResponse
from app.models import Packet, Protocol
from app.services import simulation_state
from app.models.exceptions import NetworkError

router = APIRouter(prefix="/packets", tags=["Packets"])


def _get_engine():
    """Get the current engine or raise an error."""
    if not simulation_state.is_configured:
        raise NetworkError("Network not configured. Create a network first.")
    return simulation_state.engine


@router.post(
    "/simulate",
    response_model=PacketSimulationResponse,
    summary="Simulate packet processing",
    description="Simulate a packet going through the NAT gateway. Supports LAN_TO_INTERNET (SNAT) and INTERNET_TO_LAN (DNAT/Reverse SNAT).",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid packet or no matching rule"},
        503: {"model": ErrorResponse, "description": "Network not configured"},
    },
)
async def simulate_packet(request: PacketSimulationRequest) -> PacketSimulationResponse:
    """Simulate packet processing through NAT."""
    engine = _get_engine()

    packet = Packet(
        protocol=request.protocol,
        source_ip=request.source_ip,
        source_port=request.source_port,
        destination_ip=request.destination_ip,
        destination_port=request.destination_port,
    )

    if request.direction == "LAN_TO_INTERNET":
        result = engine.process_outgoing_packet(packet)
        action = "SNAT" if result.success else "ERROR"
    elif request.direction == "INTERNET_TO_LAN":
        # Try DNAT first (port forwarding)
        dnat_result = engine.process_incoming_packet(packet)
        if dnat_result.success:
            result = dnat_result
            action = "DNAT"
        else:
            # Try reverse SNAT (response to existing mapping)
            snat_result = engine.process_incoming_response(packet)
            result = snat_result
            action = "REVERSE_SNAT" if snat_result.success else "ERROR"
    else:
        from app.models.exceptions import UnsupportedProtocol
        raise UnsupportedProtocol(f"Invalid direction: {request.direction}")

    # Build response
    original_packet = PacketResponse(
        protocol=result.original_packet.protocol,
        source_ip=result.original_packet.source_ip,
        source_port=result.original_packet.source_port,
        destination_ip=result.original_packet.destination_ip,
        destination_port=result.original_packet.destination_port,
    )

    translated_packet = None
    if result.translated_packet:
        translated_packet = PacketResponse(
            protocol=result.translated_packet.protocol,
            source_ip=result.translated_packet.source_ip,
            source_port=result.translated_packet.source_port,
            destination_ip=result.translated_packet.destination_ip,
            destination_port=result.translated_packet.destination_port,
        )

    transformations = [
        TransformationResponse(
            stage=t.stage,
            action=t.action,
            source_ip=t.source_ip,
            source_port=t.source_port,
            destination_ip=t.destination_ip,
            destination_port=t.destination_port,
            description=t.description,
        )
        for t in result.transformations
    ]

    nat_entry = None
    if result.success and result.translated_packet:
        # Find the relevant NAT entry
        if request.direction == "LAN_TO_INTERNET":
            flow_key = packet.flow_key()
            entry = engine.find_nat_entry(flow_key)
        elif request.direction == "INTERNET_TO_LAN" and action == "DNAT":
            match_key = (packet.protocol.value, packet.destination_ip, packet.destination_port)
            rule = engine.get_port_forward_rules()
            # We need to find the rule - but we can just return a reference
            entry = None
        elif request.direction == "INTERNET_TO_LAN" and action == "REVERSE_SNAT":
            reverse_key = packet.reverse_flow_key()
            entry = engine._reverse_nat_table.get(reverse_key)

        if entry:
            nat_entry = NATEntryRef(
                protocol=entry.protocol,
                private_ip=entry.private_ip,
                private_port=entry.private_port,
                public_ip=entry.public_ip,
                public_port=entry.public_port,
                destination_ip=entry.destination_ip,
                destination_port=entry.destination_port,
                state=entry.state.value,
            )

    return PacketSimulationResponse(
        success=result.success,
        action=action if result.success else None,
        original_packet=original_packet,
        translated_packet=translated_packet,
        transformations=transformations,
        nat_entry=nat_entry,
        error=result.error,
    )