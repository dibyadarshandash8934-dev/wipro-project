"""Simulation state API schemas."""

from pydantic import BaseModel
from typing import List

from app.api.schemas.network import NetworkResponse
from app.api.schemas.device import DeviceResponse
from app.api.schemas.nat import NATEntryResponse, PortForwardResponse


class SimulationStateResponse(BaseModel):
    """Response schema for complete simulation state."""

    network: NetworkResponse | None = None
    devices: List[DeviceResponse] = []
    nat_entries: List[NATEntryResponse] = []
    port_forward_rules: List[PortForwardResponse] = []


class SimulationStatsResponse(BaseModel):
    """Response schema for simulation statistics."""

    total_packets: int = 0
    successful_packets: int = 0
    failed_packets: int = 0
    snat_packets: int = 0
    dnat_packets: int = 0
    reverse_nat_packets: int = 0
    active_nat_mappings: int = 0
    active_port_forward_rules: int = 0
    average_processing_time_ms: float = 0.0


class ResetResponse(BaseModel):
    """Response schema for simulation reset."""

    success: bool = True
    message: str = "Simulation reset successfully"