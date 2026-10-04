"""Network model with IPv4 validation."""

from ipaddress import IPv4Address, IPv4Network
from pydantic import BaseModel, field_validator, model_validator
from typing import Self

from app.models.exceptions import InvalidNetwork, InvalidIPAddress, IPOutsideNetwork


class Network(BaseModel):
    """Virtual network configuration."""

    cidr: str
    gateway_ip: str
    public_ip: str

    _cidr_network: IPv4Network | None = None
    _gateway_addr: IPv4Address | None = None
    _public_addr: IPv4Address | None = None

    @field_validator("cidr")
    @classmethod
    def validate_cidr(cls, v: str) -> str:
        try:
            network = IPv4Network(v, strict=False)
            if network.version != 4:
                raise InvalidNetwork("Only IPv4 networks are supported")
            if network.prefixlen < 8 or network.prefixlen > 30:
                raise InvalidNetwork("CIDR prefix must be between /8 and /30")
        except ValueError as e:
            raise InvalidNetwork(f"Invalid CIDR: {e}")
        return v

    @field_validator("gateway_ip")
    @classmethod
    def validate_gateway_ip(cls, v: str) -> str:
        try:
            IPv4Address(v)
        except ValueError:
            raise InvalidIPAddress(f"Invalid gateway IP: {v}")
        return v

    @field_validator("public_ip")
    @classmethod
    def validate_public_ip(cls, v: str) -> str:
        try:
            IPv4Address(v)
        except ValueError:
            raise InvalidIPAddress(f"Invalid public IP: {v}")
        return v

    @model_validator(mode="after")
    def validate_gateway_in_network(self) -> Self:
        network = IPv4Network(self.cidr, strict=False)
        gateway = IPv4Address(self.gateway_ip)
        if gateway not in network:
            raise IPOutsideNetwork(f"Gateway IP {self.gateway_ip} not in network {self.cidr}")
        if gateway == network.network_address or gateway == network.broadcast_address:
            raise InvalidIPAddress("Gateway IP cannot be network or broadcast address")
        return self

    def get_network(self) -> IPv4Network:
        """Get parsed network object."""
        if self._cidr_network is None:
            self._cidr_network = IPv4Network(self.cidr, strict=False)
        return self._cidr_network

    def get_gateway(self) -> IPv4Address:
        """Get parsed gateway address."""
        if self._gateway_addr is None:
            self._gateway_addr = IPv4Address(self.gateway_ip)
        return self._gateway_addr

    def get_public_ip(self) -> IPv4Address:
        """Get parsed public IP address."""
        if self._public_addr is None:
            self._public_addr = IPv4Address(self.public_ip)
        return self._public_addr

    def contains_ip(self, ip: str) -> bool:
        """Check if IP is within the network."""
        try:
            addr = IPv4Address(ip)
            return addr in self.get_network()
        except ValueError:
            return False

    def is_valid_host_ip(self, ip: str) -> bool:
        """Check if IP is a valid host IP (not network/broadcast)."""
        try:
            addr = IPv4Address(ip)
            network = self.get_network()
            return addr in network and addr != network.network_address and addr != network.broadcast_address
        except ValueError:
            return False

    def get_available_host_ips(self) -> list[str]:
        """Get list of available host IPs in the network."""
        network = self.get_network()
        return [str(ip) for ip in network.hosts()]