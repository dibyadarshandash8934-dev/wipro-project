/** API service for backend communication. */

import type {
  Network,
  VirtualDevice,
  NATEntry,
  PortForwardRule,
  PacketSimulationResponse,
  SimulationState,
  ResetResponse,
  SimulationStats,
  PacketDirection,
  Protocol,
  DeviceType,
} from '../types';

const API_BASE = '/api';

interface HealthResponse {
  status: string;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse(response);
}

// Network API
export async function createNetwork(data: { cidr: string; gateway_ip: string; public_ip: string }): Promise<Network> {
  const response = await fetch(`${API_BASE}/network`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

export async function getNetwork(): Promise<Network> {
  const response = await fetch(`${API_BASE}/network`);
  return handleResponse(response);
}

export async function deleteNetwork(): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE}/network`, { method: 'DELETE' });
  return handleResponse(response);
}

// Device API
export interface DeviceCreateRequest {
  name: string;
  ip: string;
  type: DeviceType;
}

export async function createDevice(data: DeviceCreateRequest): Promise<VirtualDevice> {
  const response = await fetch(`${API_BASE}/devices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

export async function getDevices(): Promise<VirtualDevice[]> {
  const response = await fetch(`${API_BASE}/devices`);
  return handleResponse(response);
}

export async function getDevice(deviceId: string): Promise<VirtualDevice> {
  const response = await fetch(`${API_BASE}/devices/${deviceId}`);
  return handleResponse(response);
}

export async function deleteDevice(deviceId: string): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE}/devices/${deviceId}`, { method: 'DELETE' });
  return handleResponse(response);
}

// NAT API - Port Forwarding
export interface PortForwardCreateRequest {
  protocol: Protocol;
  public_ip: string;
  public_port: number;
  private_ip: string;
  private_port: number;
}

export async function createPortForwardRule(data: PortForwardCreateRequest): Promise<PortForwardRule> {
  const response = await fetch(`${API_BASE}/nat/port-forward`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

export async function getPortForwardRules(): Promise<PortForwardRule[]> {
  const response = await fetch(`${API_BASE}/nat/port-forward`);
  return handleResponse(response);
}

export async function deletePortForwardRule(ruleId: string): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE}/nat/port-forward/${ruleId}`, { method: 'DELETE' });
  return handleResponse(response);
}

// NAT API - Translation Table
export async function getNatTable(): Promise<{ entries: NATEntry[] }> {
  const response = await fetch(`${API_BASE}/nat/table`);
  return handleResponse(response);
}

export async function clearNatTable(): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE}/nat/table`, { method: 'DELETE' });
  return handleResponse(response);
}

// Packet Simulation API
export interface PacketSimulationRequest {
  direction: PacketDirection;
  protocol: Protocol;
  source_ip: string;
  source_port: number;
  destination_ip: string;
  destination_port: number;
}

export async function simulatePacket(data: PacketSimulationRequest): Promise<PacketSimulationResponse> {
  const response = await fetch(`${API_BASE}/packets/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

// Simulation State API
export async function getSimulationState(): Promise<SimulationState> {
  const response = await fetch(`${API_BASE}/simulation/state`);
  return handleResponse(response);
}

export async function resetSimulation(): Promise<ResetResponse> {
  const response = await fetch(`${API_BASE}/simulation/reset`, { method: 'POST' });
  return handleResponse(response);
}

export async function getSimulationStats(): Promise<SimulationStats> {
  const response = await fetch(`${API_BASE}/simulation/stats`);
  return handleResponse(response);
}