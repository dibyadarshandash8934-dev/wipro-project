/** Animation timing constants. */

export const ANIMATION_TIMING = {
  /** Duration for packet to travel between nodes (ms) */
  PACKET_TRAVEL_DURATION: 1000,
  /** Pause duration at NAT gateway for transformation (ms) */
  GATEWAY_PAUSE_DURATION: 1200,
  /** Duration for transformation display (ms) */
  TRANSFORMATION_DURATION: 1000,
  /** Duration for final state display (ms) */
  FINAL_DISPLAY_DURATION: 800,
} as const;

/** Animation status states. */
export type AnimationStatus =
  | 'IDLE'
  | 'TRAVELLING_TO_GATEWAY'
  | 'AT_GATEWAY'
  | 'TRANSLATING'
  | 'TRAVELLING_TO_DESTINATION'
  | 'COMPLETED'
  | 'ERROR';

/** Animation step corresponding to transformation stages. */
export type AnimationStep = {
  index: number;
  status: AnimationStatus;
  stage: 'LAN' | 'NAT_GATEWAY' | 'INTERNET';
  action: 'ORIGINAL' | 'SNAT' | 'DNAT' | 'FORWARD' | 'REVERSE_SNAT';
};

/** Packet visual state for rendering. */
export interface PacketVisualState {
  id: string;
  protocol: 'TCP' | 'UDP';
  sourceIp: string;
  sourcePort: number;
  destinationIp: string;
  destinationPort: number;
  status: AnimationStatus;
  position: { x: number; y: number } | null;
  progress: number; // 0-1
  currentStepIndex: number;
  action: 'ORIGINAL' | 'SNAT' | 'DNAT' | 'FORWARD' | 'REVERSE_SNAT' | null;
  translatedPacket: {
    sourceIp: string;
    sourcePort: number;
    destinationIp: string;
    destinationPort: number;
  } | null;
}

/** Default initial packet state. */
export const createInitialPacketState = (): PacketVisualState => ({
  id: 'animated-packet',
  protocol: 'TCP',
  sourceIp: '',
  sourcePort: 0,
  destinationIp: '',
  destinationPort: 0,
  status: 'IDLE',
  position: null,
  progress: 0,
  currentStepIndex: -1,
  action: null,
  translatedPacket: null,
});

/** Action labels for display. */
export const ActionLabels: Record<string, string> = {
  ORIGINAL: 'Original Packet',
  SNAT: 'SNAT Applied',
  DNAT: 'DNAT Applied',
  FORWARD: 'Forwarded',
  REVERSE_SNAT: 'Reverse SNAT',
};

/** Reduced motion check. */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/** Get animation duration based on reduced motion preference. */
export function getAnimationDuration(baseDuration: number): number {
  return prefersReducedMotion() ? 0 : baseDuration;
}