"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, network, devices, nat, packets, simulation
from app.api.exceptions import register_exception_handlers
from app.core.security_headers import SecurityHeadersMiddleware

app = FastAPI(
    title="Virtual NAT Gateway & Port-Forwarding Simulator",
    description="Educational simulator for NAT, SNAT, DNAT, and port forwarding",
    version="0.2.0",
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(network.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(nat.router, prefix="/api")
app.include_router(packets.router, prefix="/api")
app.include_router(simulation.router, prefix="/api")