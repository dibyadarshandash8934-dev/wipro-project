/** Frontend type definitions matching the FastAPI API. */

export type Protocol = 'TCP' | 'UDP';
export type DeviceType = 'pc' | 'server' | 'laptop' | 'phone' | 'iot';
export type PacketDirection = 'LAN_TO_INTERNET' | 'INTERNET_TO_LAN';
export type NATState = 'ACTIVE' | 'EXPIRED';
export type PacketAction = 'ORIGINAL' | 'SNAT' | 'DNAT' | 'FORWARD' | 'REVERSE_SNAT';
export type PacketStage = 'LAN' | 'NAT_GATEWAY' | 'INTERNET';

export interface Network {
  cidr: string;
  gateway_ip: string;
  public_ip: string;
}

export interface VirtualDevice {
  id: string;
  name: string;
  ip: string;
  type: DeviceType;
}

export interface Packet {
  protocol: Protocol;
  source_ip: string;
  source_port: number;
  destination_ip: string;
  destination_port: number;
}

export interface NATEntry {
  protocol: Protocol;
  private_ip: string;
  private_port: number;
  public_ip: string;
  public_port: number;
  destination_ip: string;
  destination_port: number;
  state: NATState;
}

export interface PortForwardRule {
  id: string;
  protocol: Protocol;
  public_ip: string;
  public_port: number;
  private_ip: string;
  private_port: number;
}

export interface PacketTransformation {
  stage: PacketStage;
  action: PacketAction;
  source_ip: string;
  source_port: number;
  destination_ip: string;
  destination_port: number;
  description: string;
}

export interface NATEntryRef {
  protocol: Protocol;
  private_ip: string;
  private_port: number;
  public_ip: string;
  public_port: number;
  destination_ip: string;
  destination_port: number;
  state: string;
}

export interface PacketSimulationResponse {
  success: boolean;
  action: string | null;
  original_packet: Packet;
  translated_packet: Packet | null;
  transformations: PacketTransformation[];
  nat_entry: NATEntryRef | null;
  error: string | null;
}

export interface SimulationState {
  network: Network | null;
  devices: VirtualDevice[];
  nat_entries: NATEntry[];
  port_forward_rules: PortForwardRule[];
}

export interface SimulationStats {
  total_packets: number;
  successful_packets: number;
  failed_packets: number;
  snat_packets: number;
  dnat_packets: number;
  reverse_nat_packets: number;
  active_nat_mappings: number;
  active_port_forward_rules: number;
  average_processing_time_ms: number;
}

export interface ResetResponse {
  success: boolean;
  message: string;
}

export interface ApiError {
  success: boolean;
  error: string;
  detail?: string;
}