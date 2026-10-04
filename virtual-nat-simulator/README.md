# Virtual NAT Gateway & Port-Forwarding Simulator

## Purpose

An educational web application that visually demonstrates how NAT (Network
Address Translation), SNAT, DNAT, stateful NAT, and port forwarding work.

> **This is a software simulator.** It does not perform real NAT operations,
> transmit real network packets, or modify any actual network configuration.

Built as a **Wipro Capstone Project**.

---

## Technology Stack

| Layer         | Technology                                                  |
| ------------- | ----------------------------------------------------------- |
| Frontend      | React, TypeScript, Vite, Tailwind CSS, React Flow           |
| Backend       | Python, FastAPI, Pydantic                                   |
| Simulation    | Pure Python, in-memory state                                |
| Testing       | Pytest (backend), Vitest + React Testing Library (frontend) |
| Communication | REST API (JSON)                                             |

---

## Architecture

```
React Frontend
      ↓
  REST API (JSON)
      ↓
  FastAPI Backend
      ↓
  Simulation Services
      ↓
  NAT Simulation Engine
      ↓
  In-Memory Simulation State
```

The NAT simulation engine is independent from FastAPI and can be unit tested
without running the web server.

---

## Current Development Phase

**Phase 0 — Foundation**

- [x] Project structure
- [x] FastAPI backend with health endpoint
- [x] React frontend with dashboard
- [x] Backend ↔ Frontend connectivity
- [x] Testing infrastructure
- [ ] NAT simulation engine (Phase 1)
- [ ] Network & device management (Phase 1)

---

## How to Run

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. API docs at
`http://localhost:8000/api/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

### Running Tests

**Backend:**

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

**Frontend:**

```bash
cd frontend
npx vitest run
```

---

## Planned Features

1. Network management (create/configure virtual networks)
2. Virtual device management (hosts, routers, gateways)
3. NAT Gateway simulation (SNAT, DNAT, stateful NAT)
4. Port forwarding rules
5. NAT translation table visualization
6. Packet simulation with step-by-step transformation
7. React Flow network topology visualization
8. Packet transformation animation
9. Simulation statistics and logging
