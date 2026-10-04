"""Simulation state manager - holds the current simulation state."""

from app.models import Network
from app.models.exceptions import NetworkError
from app.services.nat_engine import NATEngine


class SimulationState:
    """Manages the current simulation state."""

    def __init__(self):
        self._network: Network | None = None
        self._engine: NATEngine | None = None

    @property
    def network(self) -> Network | None:
        return self._network

    @property
    def engine(self) -> NATEngine | None:
        return self._engine

    @property
    def is_configured(self) -> bool:
        return self._network is not None and self._engine is not None

    def create_network(self, network: Network) -> NATEngine:
        """Create a new network and engine, replacing any existing state."""
        self._network = network
        self._engine = NATEngine(network)
        return self._engine

    def get_engine(self) -> NATEngine:
        """Get the current engine, raising an error if not configured."""
        if not self.is_configured:
            raise NetworkError("Network not configured. Create a network first.")
        return self._engine

    def reset(self) -> None:
        """Reset the simulation state."""
        self._network = None
        self._engine = None


# Global simulation state instance
simulation_state = SimulationState()