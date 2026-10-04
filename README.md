# Virtual NAT Gateway & Port-Forwarding Simulator

## Overview

The **Virtual NAT Gateway & Port-Forwarding Simulator** is an educational web application that demonstrates Network Address Translation (NAT) concepts through interactive visualization. It simulates SNAT (Source NAT), DNAT (Destination NAT/Port Forwarding), and reverse NAT for response packets - all without requiring real network infrastructure.

## Problem Statement

NAT is a fundamental networking concept that allows multiple devices on a private network to share a single public IP address. Understanding how NAT works - including SNAT for outbound connections, DNAT for port forwarding, and stateful connection tracking - is essential for network engineers and students. However, experimenting with real NAT configurations requires physical/virtual networking equipment, Linux network namespaces, or cloud infrastructure.

This simulator provides a safe, instant, and visual way to learn NAT concepts without any real network configuration.

## Objectives

- **NAT Simulation**: Core NAT engine with IPv4 validation using Python's `ipaddress` module
- **SNAT (Source NAT)**: Outbound packet translation with stateful connection tracking
- **DNAT (Destination NAT)**: Port forwarding for inbound connections
- **Stateful NAT**: Connection tracking with automatic mapping reuse
- **Port Forwarding**: Configurable port forwarding rules with validation
- **Packet Visualization**: Animated packet flow through the NAT gateway
- **Transformation History**: Step-by-step packet transformation display
- **Statistics Dashboard**: Real-time metrics and performance monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Network    │  │  Packet     │  │  NAT        │            │
│  │  Config     │  │  Simulator  │  │  Table      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Device     │  │  Port       │  │  Topology   │            │
│  │  Manager    │  │  Forwarding │  │  (React     │            │
│  └─────────────┘  └─────────────┘  │  Flow)      │            │
│                                     └─────────────┘            │
└─────────────────────────────┬──────────────────────────────────┘
                              │ REST API (JSON)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              NAT Simulation Engine                        │   │
│  │  • IPv4 validation (ipaddress module)                     │   │
│  │  • SNAT / DNAT / Reverse NAT                              │   │
│  │  • Stateful connection tracking                           │   │
│  │  • Public port allocation (40000-50000)                   │   │
│  │  • Port forwarding validation                             │   │
│  │  • Metrics collection (perf_counter)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Network    │  │  Device     │  │  NAT        │            │
│  │  Service    │  │  Service    │  │  Service    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IN-MEMORY STATE                              │
│  • Virtual Network (CIDR, Gateway, Public IP)                   │
│  • Virtual Devices (ID, Name, IP, Type)                         │
│  • NAT Translation Table (SNAT mappings)                        │
│  • Port Forward Rules (DNAT mappings)                           │
│  • Metrics (packet counts, processing times)                    │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Flow** for network topology visualization
- **Vitest** + React Testing Library for testing

### Backend
- **Python 3.11+** with FastAPI
- **Pydantic v2** for validation
- **ipaddress** module for IPv4 handling
- **Pytest** + httpx for testing
- **Uvicorn** ASGI server

### Testing
- **Pytest** (backend): 89 tests
- **Vitest** (frontend): 3 tests

## Features

### NAT Simulation
- **Virtual Network**: Configurable CIDR, gateway IP, public IP
- **Virtual Devices**: Add/remove devices with IP validation
- **IPv4 Validation**: Uses Python's `ipaddress` module (no string manipulation)
- **Subnet Enforcement**: Devices must be within the configured CIDR

### SNAT (Source NAT)
- **Stateful Translation**: Outbound packets get public IP + allocated port
- **Mapping Reuse**: Same flow (protocol, src IP/port, dst IP/port) reuses mapping
- **Port Allocation**: Deterministic allocation from 40000-50000 range
- **TCP/UDP Independence**: Separate mappings for TCP and UDP

### DNAT / Port Forwarding
- **Rule Management**: Add/remove port forwarding rules
- **Validation**: Public IP must match NAT gateway, private IP must exist in LAN
- **Protocol Independence**: TCP and UDP can share same public port
- **Conflict Prevention**: Duplicate rules rejected

### Reverse NAT
- **Response Handling**: Inbound responses automatically translated back
- **Mapping Lookup**: Uses reverse NAT table for O(1) lookup
- **Error Handling**: Clear errors for unmatched responses

### Visualization
- **Packet Animation**: Animated packet flow along React Flow edges
- **Transformation Panel**: Modal showing before/after at NAT gateway
- **Transformation Timeline**: Step-by-step history with stage/action
- **Network Topology**: React Flow diagram with devices, gateway, internet

### Metrics & Monitoring
- **Real-time Stats**: Total/successful/failed packets
- **Breakdown**: SNAT, DNAT, Reverse NAT counts
- **Performance**: Average processing time (perf_counter)
- **Active Counts**: NAT mappings, port forward rules

## NAT Concepts

### What is NAT?
Network Address Translation (NAT) modifies IP address information in packet headers while in transit across a traffic routing device.

### Why is NAT Needed?
- **IPv4 Exhaustion**: Not enough public IPv4 addresses for all devices
- **Security**: Hides internal network structure
- **Flexibility**: Internal addressing can change without affecting external connectivity

### SNAT vs DNAT

| Aspect | SNAT (Source NAT) | DNAT (Destination NAT) |
|--------|-------------------|------------------------|
| **Direction** | Outbound (LAN → Internet) | Inbound (Internet → LAN) |
| **What Changes** | Source IP + Port | Destination IP + Port |
| **Use Case** | Internet access for LAN devices | Port forwarding to internal servers |
| **Stateful** | Yes, tracks connections | Yes, for port forwards |

### Port Forwarding
Maps external (public IP:port) to internal (private IP:port). Allows external access to services on private network.

### Stateful NAT
Maintains connection state so return traffic is automatically translated back. Essential for TCP and UDP flows.

### Why Ports Are Required
- **Multiplexing**: Multiple connections share single public IP
- **Identification**: 5-tuple (protocol, src IP, src port, dst IP, dst port) uniquely identifies flows
- **Return Path**: Reverse lookup uses destination port to find original connection

## Packet Flow

### LAN → Internet (SNAT)
```
1. LAN Device sends:     192.168.1.10:50000 → 8.8.8.8:443 (TCP)
2. NAT Gateway (SNAT):   192.168.1.10:50000 → 203.0.113.5:40000
3. Internet receives:    203.0.113.5:40000 → 8.8.8.8:443 (TCP)
```

### Internet → LAN (DNAT / Port Forward)
```
1. Internet sends:       198.51.100.20:45000 → 203.0.113.5:8080 (TCP)
2. NAT Gateway (DNAT):   198.51.100.20:45000 → 192.168.1.20:80
3. LAN Device receives:  198.51.100.20:45000 → 192.168.1.20:80 (TCP)
```

### Reverse NAT (Response)
```
1. Internet responds:    8.8.8.8:443 → 203.0.113.5:40000 (TCP)
2. NAT Gateway (Rev):    8.8.8.8:443 → 192.168.1.10:50000
3. LAN Device receives:  8.8.8.8:443 → 192.168.1.10:50000 (TCP)
```

## Project Structure

```
virtual-nat-simulator/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   │   ├── health.py
│   │   │   ├── network.py
│   │   │   ├── devices.py
│   │   │   ├── nat.py
│   │   │   ├── packets.py
│   │   │   └── simulation.py
│   │   ├── core/          # Security headers, exceptions
│   │   ├── models/        # Pydantic models
│   │   │   ├── network.py
│   │   │   ├── device.py
│   │   │   ├── packet.py
│   │   │   ├── nat.py
│   │   │   └── exceptions.py
│   │   ├── services/      # Business logic
│   │   │   ├── network_service.py
│   │   │   ├── nat_engine.py
│   │   │   └── simulation_state.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_nat_engine.py   # 40 unit tests
│   │   ├── test_api.py          # 30 API tests
│   │   └── test_health.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/       # Header, DashboardLayout
│   │   │   ├── network/      # NetworkConfig, DeviceList, Topology
│   │   │   ├── nat/          # NatGatewayCard, TranslationTable, PortForwardTable
│   │   │   ├── packets/      # PacketSimulator, Animation, TransformationPanel
│   │   │   └── common/       # Button, Input, Select, Badge, etc.
│   │   ├── hooks/            # useSimulationState, usePacketAnimation
│   │   ├── services/         # API client
│   │   ├── types/            # TypeScript types
│   │   └── pages/            # Dashboard
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── WIPRO_INTERVIEW.md
│   └── DEMO_GUIDE.md
└── README.md
```

## Installation

### Backend
```bash
cd virtual-nat-simulator/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd virtual-nat-simulator/frontend
npm install
```

## Running

### Start Backend
```bash
cd virtual-nat-simulator/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
API available at: http://localhost:8000
Swagger UI: http://localhost:8000/docs

### Start Frontend
```bash
cd virtual-nat-simulator/frontend
npm run dev
```
Frontend available at: http://localhost:5173

## Testing

### Backend Tests
```bash
cd virtual-nat-simulator/backend
source venv/bin/activate
python -m pytest tests/ -v
```
Expected: 89 tests passing (40 NAT engine + 30 API + 1 health + 18 edge cases)

### Frontend Tests
```bash
cd virtual-nat-simulator/frontend
npm test
```
Expected: 3 tests passing

### Build
```bash
cd virtual-nat-simulator/frontend
npm run build
```

## API Endpoints

### Health
- `GET /api/health` - Health check

### Network
- `POST /api/network` - Create network
- `GET /api/network` - Get network config
- `DELETE /api/network` - Delete network

### Devices
- `POST /api/devices` - Add device
- `GET /api/devices` - List devices
- `GET /api/devices/{id}` - Get device
- `DELETE /api/devices/{id}` - Delete device

### NAT
- `POST /api/nat/port-forward` - Add port forward rule
- `GET /api/nat/port-forward` - List port forward rules
- `DELETE /api/nat/port-forward/{id}` - Delete rule
- `GET /api/nat/table` - Get NAT translation table
- `DELETE /api/nat/table` - Clear NAT table

### Packets
- `POST /api/packets/simulate` - Simulate packet (SNAT/DNAT/Reverse)

### Simulation
- `GET /api/simulation/state` - Complete state snapshot
- `GET /api/simulation/stats` - Statistics/metrics
- `POST /api/simulation/reset` - Reset all state

## Example Scenarios

### SNAT Example
```
Input:  TCP 192.168.1.10:50000 → 8.8.8.8:443
Output: TCP 203.0.113.5:40000 → 8.8.8.8:443
```

### DNAT Example
```
Input:  TCP 198.51.100.20:45000 → 203.0.113.5:8080
Output: TCP 198.51.100.20:45000 → 192.168.1.10:80
```

## Limitations

- **No Real Network Traffic**: Pure software simulation
- **In-Memory State**: Data lost on restart
- **Single Instance**: One simulation per backend
- **IPv4 Only**: No IPv6 support
- **TCP/UDP Only**: No ICMP or other protocols
- **Single NAT Gateway**: No multi-gateway scenarios
- **Educational Focus**: Not for production use

## Future Improvements

- Configuration persistence (file/database)
- IPv6 support
- Multiple NAT gateways
- ACL/Firewall simulation
- Packet loss / latency simulation
- Session timeout / expiry
- Multi-user with authentication
- WebSocket for real-time updates

---

*This project is a software simulation for educational purposes. It does not perform real network packet transmission, real NAT configuration, packet capture, Linux network namespaces, or actual packet transmission.*