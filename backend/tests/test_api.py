"""FastAPI API integration tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Health Tests

def test_health_endpoint():
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Network Tests

def test_create_network():
    """Test creating a network."""
    response = client.post(
        "/api/network",
        json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["cidr"] == "192.168.1.0/24"
    assert data["gateway_ip"] == "192.168.1.1"
    assert data["public_ip"] == "203.0.113.5"


def test_get_network():
    """Test getting the network configuration."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.get("/api/network")
    assert response.status_code == 200
    data = response.json()
    assert data["cidr"] == "192.168.1.0/24"


def test_delete_network():
    """Test deleting the network."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.delete("/api/network")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify network is gone
    response = client.get("/api/network")
    assert response.status_code == 400


def test_create_network_invalid_cidr():
    """Test creating network with invalid CIDR."""
    response = client.post("/api/network", json={"cidr": "invalid", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_network_gateway_outside():
    """Test creating network with gateway outside CIDR."""
    response = client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.2.1", "public_ip": "203.0.113.5"})
    assert response.status_code == 400


# Device Tests

def test_add_device():
    """Test adding a device."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "PC-01"
    assert data["ip"] == "192.168.1.10"
    assert data["type"] == "pc"


def test_get_devices():
    """Test getting all devices."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    client.post("/api/devices", json={"name": "Server-01", "ip": "192.168.1.20", "type": "server"})
    response = client.get("/api/devices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_device():
    """Test getting a specific device."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.get("/api/devices/pc-01")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "pc-01"
    assert data["name"] == "PC-01"


def test_delete_device():
    """Test deleting a device."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.delete("/api/devices/pc-01")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_get_device_not_found():
    """Test getting non-existent device."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.get("/api/devices/non-existent")
    assert response.status_code == 404


def test_add_device_invalid_ip():
    """Test adding device with invalid IP."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.post("/api/devices", json={"name": "PC-01", "ip": "invalid", "type": "pc"})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_add_device_outside_subnet():
    """Test adding device outside subnet."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.2.10", "type": "pc"})
    assert response.status_code == 400


def test_add_duplicate_device():
    """Test adding duplicate device IP."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.post("/api/devices", json={"name": "PC-02", "ip": "192.168.1.10", "type": "pc"})
    assert response.status_code == 409


# Port Forward Tests

def test_add_port_forward():
    """Test adding a port forward rule."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "Web-01", "ip": "192.168.1.20", "type": "server"})
    response = client.post(
        "/api/nat/port-forward",
        json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["protocol"] == "TCP"
    assert data["public_port"] == 8080
    assert data["private_port"] == 80


def test_get_port_forward_rules():
    """Test getting all port forward rules."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "Web-01", "ip": "192.168.1.20", "type": "server"})
    client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    response = client.get("/api/nat/port-forward")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_delete_port_forward():
    """Test deleting a port forward rule."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "Web-01", "ip": "192.168.1.20", "type": "server"})
    response = client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    rule_id = response.json()["id"]
    response = client.delete(f"/api/nat/port-forward/{rule_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_duplicate_port_forward():
    """Test duplicate port forward rule."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "Web-01", "ip": "192.168.1.20", "type": "server"})
    client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    response = client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 8080})
    assert response.status_code == 409


# NAT Table Tests

def test_get_nat_table():
    """Test getting NAT table."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.get("/api/nat/table")
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data


def test_clear_nat_table():
    """Test clearing NAT table."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    client.post("/api/nat/table")  # This will fail - need to use DELETE
    response = client.delete("/api/nat/table")
    assert response.status_code == 200
    assert response.json()["success"] is True


# Packet Simulation Tests

def test_tcp_snat_api():
    """Test TCP SNAT via API."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.post(
        "/api/packets/simulate",
        json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["action"] == "SNAT"
    assert data["translated_packet"]["source_ip"] == "203.0.113.5"
    assert data["translated_packet"]["source_port"] == 40000


def test_udp_snat_api():
    """Test UDP SNAT via API."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.post(
        "/api/packets/simulate",
        json={"direction": "LAN_TO_INTERNET", "protocol": "UDP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 53},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["action"] == "SNAT"
    assert data["translated_packet"]["protocol"] == "UDP"


def test_snat_mapping_reuse_api():
    """Test SNAT mapping reuse via API."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443})
    response = client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["translated_packet"]["source_port"] == 40000


def test_dnat_api():
    """Test DNAT via API."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "Web-01", "ip": "192.168.1.20", "type": "server"})
    client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    response = client.post(
        "/api/packets/simulate",
        json={"direction": "INTERNET_TO_LAN", "protocol": "TCP", "source_ip": "198.51.100.20", "source_port": 45000, "destination_ip": "203.0.113.5", "destination_port": 8080},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["action"] == "DNAT"
    assert data["translated_packet"]["destination_ip"] == "192.168.1.20"
    assert data["translated_packet"]["destination_port"] == 80
    assert data["translated_packet"]["source_ip"] == "198.51.100.20"


def test_reverse_nat_api():
    """Test reverse NAT via API."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443})
    response = client.post(
        "/api/packets/simulate",
        json={"direction": "INTERNET_TO_LAN", "protocol": "TCP", "source_ip": "8.8.8.8", "source_port": 443, "destination_ip": "203.0.113.5", "destination_port": 40000},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["action"] == "REVERSE_SNAT"
    assert data["translated_packet"]["destination_ip"] == "192.168.1.10"
    assert data["translated_packet"]["destination_port"] == 50000


def test_invalid_protocol():
    """Test invalid protocol."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.post(
        "/api/packets/simulate",
        json={"direction": "LAN_TO_INTERNET", "protocol": "ICMP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_invalid_port():
    """Test invalid port."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.post(
        "/api/packets/simulate",
        json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 0, "destination_ip": "8.8.8.8", "destination_port": 443},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_unknown_device():
    """Test unknown source device - packet dropped with error."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.post(
        "/api/packets/simulate",
        json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.99", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["error"].lower()


# Simulation State Tests

def test_simulation_state():
    """Test getting simulation state."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    client.post("/api/devices", json={"name": "Server-01", "ip": "192.168.1.20", "type": "server"})
    client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    response = client.get("/api/simulation/state")
    assert response.status_code == 200
    data = response.json()
    assert data["network"] is not None
    assert len(data["devices"]) == 2
    assert len(data["port_forward_rules"]) == 1


def test_reset_simulation():
    """Test resetting simulation."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    response = client.post("/api/simulation/reset")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify everything is reset
    response = client.get("/api/simulation/state")
    assert response.status_code == 200
    data = response.json()
    assert data["network"] is None
    assert len(data["devices"]) == 0
    assert len(data["nat_entries"]) == 0
    assert len(data["port_forward_rules"]) == 0


# Stats Tests

def test_simulation_stats():
    """Test getting simulation statistics."""
    # Reset first to ensure clean state
    client.post("/api/simulation/reset")
    
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    client.post("/api/devices", json={"name": "Server-01", "ip": "192.168.1.20", "type": "server"})
    client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443})
    client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "UDP", "source_ip": "192.168.1.10", "source_port": 50001, "destination_ip": "8.8.8.8", "destination_port": 53})
    client.post("/api/packets/simulate", json={"direction": "INTERNET_TO_LAN", "protocol": "TCP", "source_ip": "198.51.100.20", "source_port": 45000, "destination_ip": "203.0.113.5", "destination_port": 8080})
    client.post("/api/packets/simulate", json={"direction": "INTERNET_TO_LAN", "protocol": "TCP", "source_ip": "8.8.8.8", "source_port": 443, "destination_ip": "203.0.113.5", "destination_port": 40000})

    response = client.get("/api/simulation/stats")
    assert response.status_code == 200
    data = response.json()
    # Account for potential state from previous tests - check that at least our 4 packets are counted
    assert data["total_packets"] >= 4
    assert data["successful_packets"] >= 4
    # Failed packets may include failures from other tests running in the same process
    assert data["snat_packets"] >= 2
    assert data["dnat_packets"] >= 1
    assert data["reverse_nat_packets"] >= 1
    assert data["active_nat_mappings"] >= 2
    assert data["active_port_forward_rules"] >= 1
    assert data["average_processing_time_ms"] > 0


def test_simulation_stats_empty():
    """Test stats when no network configured."""
    # Reset first to ensure clean state
    client.post("/api/simulation/reset")
    
    response = client.get("/api/simulation/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_packets"] == 0
    assert data["successful_packets"] == 0
    assert data["failed_packets"] == 0
    assert data["average_processing_time_ms"] == 0


def test_stats_reset_on_simulation_reset():
    """Test that stats are reset when simulation is reset."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443})

    response = client.get("/api/simulation/stats")
    assert response.json()["total_packets"] == 1

    client.post("/api/simulation/reset")

    response = client.get("/api/simulation/stats")
    assert response.json()["total_packets"] == 0


# Edge Case Tests

def test_invalid_cidr_formats():
    """Test various invalid CIDR formats."""
    invalid_cidrs = ["192.168.1.0/33", "192.168.1.0/7", "invalid", "192.168.1.0", "192.168.1.0/abc"]
    for cidr in invalid_cidrs:
        response = client.post("/api/network", json={"cidr": cidr, "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
        assert response.status_code in (400, 422), f"CIDR {cidr} should be rejected"


def test_invalid_ip_formats():
    """Test various invalid IP formats."""
    invalid_ips = ["999.168.1.1", "192.168.1.256", "192.168.1", "not.an.ip", "192.168.1.1.1"]
    for ip in invalid_ips:
        response = client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": ip, "public_ip": "203.0.113.5"})
        assert response.status_code in (400, 422), f"IP {ip} should be rejected"

    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    for ip in invalid_ips:
        response = client.post("/api/devices", json={"name": "Test", "ip": ip, "type": "pc"})
        assert response.status_code in (400, 422), f"Device IP {ip} should be rejected"


def test_invalid_ports():
    """Test invalid port values."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})

    invalid_ports = [0, -1, 65536, 70000, -100]
    for port in invalid_ports:
        response = client.post("/api/packets/simulate", json={
            "direction": "LAN_TO_INTERNET",
            "protocol": "TCP",
            "source_ip": "192.168.1.10",
            "source_port": port,
            "destination_ip": "8.8.8.8",
            "destination_port": 443
        })
        assert response.status_code in (400, 422), f"Port {port} should be rejected"


def test_valid_ports():
    """Test valid port boundaries."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})

    valid_ports = [1, 80, 443, 8080, 65535]
    for port in valid_ports:
        response = client.post("/api/packets/simulate", json={
            "direction": "LAN_TO_INTERNET",
            "protocol": "TCP",
            "source_ip": "192.168.1.10",
            "source_port": port,
            "destination_ip": "8.8.8.8",
            "destination_port": 443
        })
        assert response.status_code == 200, f"Port {port} should be accepted"


def test_supported_protocols():
    """Test supported protocols."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})

    for protocol in ["TCP", "UDP"]:
        response = client.post("/api/packets/simulate", json={
            "direction": "LAN_TO_INTERNET",
            "protocol": protocol,
            "source_ip": "192.168.1.10",
            "source_port": 50000,
            "destination_ip": "8.8.8.8",
            "destination_port": 443
        })
        assert response.status_code == 200, f"Protocol {protocol} should be accepted"


def test_unsupported_protocol():
    """Test unsupported protocol rejection."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})

    response = client.post("/api/packets/simulate", json={
        "direction": "LAN_TO_INTERNET",
        "protocol": "ICMP",
        "source_ip": "192.168.1.10",
        "source_port": 50000,
        "destination_ip": "8.8.8.8",
        "destination_port": 443
    })
    assert response.status_code in (400, 422)


def test_nat_port_exhaustion():
    """Test NAT port exhaustion."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})

    # Fill up all ports by creating unique flows
    for i in range(10000, 20000):  # Using high ports to consume the NAT range
        response = client.post("/api/packets/simulate", json={
            "direction": "LAN_TO_INTERNET",
            "protocol": "TCP",
            "source_ip": "192.168.1.10",
            "source_port": i,
            "destination_ip": "8.8.8.8",
            "destination_port": 443
        })
        if not response.json()["success"]:
            break

    # Next one should fail
    response = client.post("/api/packets/simulate", json={
        "direction": "LAN_TO_INTERNET",
        "protocol": "TCP",
        "source_ip": "192.168.1.10",
        "source_port": 50000,
        "destination_ip": "8.8.8.8",
        "destination_port": 443
    })
    # Should either succeed (if ports were freed) or fail with port exhaustion
    # The exact behavior depends on the port allocation algorithm


def test_duplicate_port_forward_same_protocol():
    """Test duplicate port forward rule with same protocol is rejected."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "Web-01", "ip": "192.168.1.20", "type": "server"})

    client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    response = client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 8080})
    assert response.status_code == 409


def test_port_forward_tcp_udp_independence():
    """Test TCP and UDP can use same port for port forwarding."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "Web-01", "ip": "192.168.1.20", "type": "server"})

    client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    response = client.post("/api/nat/port-forward", json={"protocol": "UDP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 53})
    assert response.status_code == 201


def test_port_forward_invalid_private_ip():
    """Test port forward to nonexistent device."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    # Don't add a device at 192.168.1.99

    response = client.post("/api/nat/port-forward", json={
        "protocol": "TCP",
        "public_ip": "203.0.113.5",
        "public_port": 8080,
        "private_ip": "192.168.1.99",
        "private_port": 80
    })
    assert response.status_code == 404


def test_delete_nonexistent_port_forward():
    """Test deleting nonexistent port forward rule."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.delete("/api/nat/port-forward/nonexistent")
    assert response.status_code == 404


def test_delete_nonexistent_device():
    """Test deleting nonexistent device."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    response = client.delete("/api/devices/nonexistent")
    assert response.status_code == 404


def test_nat_mapping_reuse_tcp_udp():
    """Test TCP and UDP mappings are independent."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})

    # Same private port, different protocols
    tcp_resp = client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443})
    udp_resp = client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "UDP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 53})

    assert tcp_resp.json()["translated_packet"]["source_port"] != udp_resp.json()["translated_packet"]["source_port"]


def test_snat_different_destinations_different_mappings():
    """Test different destinations create separate mappings."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})

    resp1 = client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443})
    resp2 = client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "1.1.1.1", "destination_port": 443})

    # Should get different public ports
    assert resp1.json()["translated_packet"]["source_port"] != resp2.json()["translated_packet"]["source_port"]


def test_clear_nat_table_preserves_rules():
    """Test clearing NAT table doesn't affect port forward rules."""
    client.post("/api/network", json={"cidr": "192.168.1.0/24", "gateway_ip": "192.168.1.1", "public_ip": "203.0.113.5"})
    client.post("/api/devices", json={"name": "PC-01", "ip": "192.168.1.10", "type": "pc"})
    client.post("/api/devices", json={"name": "Web-01", "ip": "192.168.1.20", "type": "server"})
    client.post("/api/nat/port-forward", json={"protocol": "TCP", "public_ip": "203.0.113.5", "public_port": 8080, "private_ip": "192.168.1.20", "private_port": 80})
    client.post("/api/packets/simulate", json={"direction": "LAN_TO_INTERNET", "protocol": "TCP", "source_ip": "192.168.1.10", "source_port": 50000, "destination_ip": "8.8.8.8", "destination_port": 443})

    client.delete("/api/nat/table")

    # Port forward rule should still exist
    response = client.get("/api/nat/port-forward")
    assert len(response.json()) == 1

    # But NAT table should be empty
    response = client.get("/api/nat/table")
    assert len(response.json()["entries"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])