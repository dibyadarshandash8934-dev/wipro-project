# Demo Guide: Virtual NAT Gateway & Port-Forwarding Simulator

## 5-Minute Demonstration Script

### Pre-Demo Setup (30 seconds before)
- Start backend: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- Start frontend: `cd frontend && npm run dev`
- Open browser to `http://localhost:5173`
- Verify backend status shows "● Connected" in header

---

## Demo Sequence (5 minutes)

### 0:00 – 0:30 | Introduction (30 sec)

**Say:**
> "This is the Virtual NAT Gateway & Port-Forwarding Simulator - an educational tool that demonstrates how Network Address Translation works without any real network infrastructure. It simulates SNAT for outbound connections, DNAT for port forwarding, and reverse NAT for response packets - all with animated packet visualization."

**Show:** Dashboard with "Backend: Connected" status

---

### 0:30 – 1:00 | Create Private LAN (30 sec)

**Actions:**
1. Fill Network Configuration:
   - CIDR: `192.168.1.0/24`
   - Gateway IP: `192.168.1.1`
   - Public IP: `203.0.113.5`
2. Click "Create Network"

**Say:**
> "First, I'll create a private LAN with CIDR 192.168.1.0/24. The gateway is 192.168.1.1, and the NAT gateway's public IP is 203.0.113.5 - a reserved documentation address."

**Show:** Network configuration appears in header and topology

---

### 1:00 – 1:30 | Add Virtual Device (30 sec)

**Actions:**
1. In Device Manager, add:
   - Name: `PC-01`
   - IP: `192.168.1.10`
   - Type: `PC`
2. Click "Add Device"

**Say:**
> "Now I'll add a virtual PC to our LAN. The IP 192.168.1.10 is validated to be within our 192.168.1.0/24 subnet. The simulator rejects IPs outside the subnet, network/broadcast addresses, and duplicates."

**Show:** Device appears in device list and topology

---

### 1:30 – 2:00 | Explain NAT Gateway (30 sec)

**Say:**
> "Here's our NAT Gateway card showing the LAN gateway (192.168.1.1), public IP (203.0.113.5), and real-time counters. The topology shows our PC on the left, NAT Gateway in the middle, and Internet on the right. The animated edges show the SNAT path."

**Point to:** Header stats, NAT Gateway card, Network Topology

---

### 2:00 – 2:30 | Send Outbound Packet (SNAT) (30 sec)

**Actions:**
1. In Packet Simulator:
   - Direction: `LAN → Internet (SNAT)`
   - Protocol: `TCP`
   - Source IP: `192.168.1.10`
   - Source Port: `50000`
   - Destination IP: `8.8.8.8`
   - Destination Port: `443`
2. Click "Simulate Packet"
3. Click "Play Animation"

**Say:**
> "Now I'll simulate an outbound HTTPS request from our PC to Google DNS. Watch the packet travel from the PC to the NAT Gateway, get translated, then continue to the Internet."

**Watch:** Packet animation, then Transformation Panel appears

**Point out:** "Notice the Transformation Panel shows SNAT: private 192.168.1.10:50000 becomes public 203.0.113.5:40000. The destination stays unchanged."

---

### 2:30 – 3:00 | Show NAT Translation Table (30 sec)

**Actions:**
1. Look at NAT Translation Table panel

**Say:**
> "The NAT Translation Table now shows our active mapping. The private 192.168.1.10:50000 is mapped to public 203.0.113.5:40000 for destination 8.8.8.8:443. If the same flow is simulated again, the same public port is reused - no new allocation."

**Point out:** NAT table entry, "Active NAT Mappings: 1" counter

---

### 3:00 – 3:30 | Add Port Forward Rule (30 sec)

**Actions:**
1. In Port Forwarding panel:
   - Protocol: `TCP`
   - Public Port: `8080`
   - Private IP: `192.168.1.20`
   - Private Port: `80`
2. Click "Add Rule"

**Say:**
> "Now I'll configure port forwarding. External traffic to port 8080 on our public IP will be forwarded to our web server at 192.168.1.20 on port 80. The simulator validates that the private IP exists in our LAN and that the rule doesn't conflict with existing rules."

**Show:** Rule appears in table, Port Forward counter increments

---

### 4:00 – 4:30 | Simulate Inbound Packet (DNAT) (30 sec)

**Actions:**
1. In Packet Simulator:
   - Direction: `Internet → LAN (DNAT/Reverse)`
   - Protocol: `TCP`
   - Source IP: `198.51.100.20`
   - Source Port: `45000`
   - Destination IP: `203.0.113.5`
   - Destination Port: `8080`
2. Click "Simulate Packet"
3. Click "Play Animation"

**Say:**
> "Now I'll simulate an inbound HTTP request from the Internet to our public IP on port 8080. This should trigger DNAT - the destination gets translated to our internal web server."

**Watch:** Animation from Internet → NAT Gateway → Web Server

**Point out:** "Transformation Panel shows DNAT: public destination 203.0.113.5:8080 becomes private 192.168.1.20:80. Source IP/port stays unchanged."

---

### 4:30 – 5:00 | Show Metrics & Architecture (30 sec)

**Actions:**
1. Look at header metrics bar
2. Check Simulation Stats panel (if visible)
3. Click "Reset Simulation" to clean up

**Say:**
> "The header shows real-time metrics: 4 total packets, 3 successful, 1 failed, broken down by SNAT, DNAT, and Reverse NAT. Average processing time is sub-millisecond because it's a pure Python simulation. The stats API at /api/simulation/stats provides this data programmatically."

**Click Reset:** "The reset button clears all state - network, devices, NAT mappings, port forwards, and metrics - returning to a clean slate."

---

## Key Talking Points During Demo

| Moment | Emphasize |
|--------|-----------|
| Network creation | IPv4 validation via `ipaddress` module, not string parsing |
| Device addition | Subnet validation, no duplicates, no network/broadcast |
| SNAT animation | Source IP/port changes, destination unchanged |
| NAT table | Mapping reuse for same flow |
| DNAT animation | Destination IP/port changes, source unchanged |
| Port forwarding | Validation: public IP matches gateway, private IP exists |
| Reverse NAT | Response packet translated back automatically |
| Metrics | Sub-millisecond processing, per-action breakdown |
| Reset | Complete state cleanup |

---

## Common Questions & Answers

**Q: "Does this use real network packets?"**
> No, it's a pure software simulation. The backend NAT engine is pure Python with no socket operations, no Linux namespaces, no packet capture.

**Q: "Can this handle real traffic?"**
> No, this is an educational simulator. The NAT engine is pure Python and could theoretically be adapted, but it lacks kernel integration, performance optimization, and production hardening.

**Q: "How does the animation work?"**
> The backend returns structured transformation steps (stage, action, before/after IPs). The frontend animates a packet along React Flow edges using those steps. The packet movement is purely visual - the actual NAT logic runs in Python.

**Q: "Why Python for the NAT engine?"**
> Python's `ipaddress` module provides robust IPv4 validation. FastAPI + Pydantic gives type-safe APIs. The engine is framework-agnostic - pure Python with zero FastAPI dependencies.

**Q: "What about scaling?"**
> The NAT engine is completely decoupled from FastAPI. For production: externalize state to Redis, add horizontal scaling, Prometheus metrics, authentication.

---

## Troubleshooting During Demo

| Issue | Fix |
|-------|-----|
| Backend shows "Disconnected" | Check backend running on port 8000, CORS allows localhost:5173 |
| Animation doesn't play | Click "Play Animation" button after simulation |
| "Network not configured" | Create network first |
| Port forward fails | Verify device exists in LAN with matching IP |
| Stats show 0 | Run simulations first, then refresh stats |

---

## Post-Demo Cleanup

1. Click "Reset Simulation" button
2. Verify all panels clear
3. Stop servers: `Ctrl+C` in both terminals

---

*Demo guide for Wipro Capstone Project*