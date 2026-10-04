/** Packet animation component - visualizes packet movement on network topology. */

import { useEffect, useRef, useMemo } from 'react';
import type { PacketVisualState } from '../../constants/animation';

interface PacketAnimationProps {
  packetState: PacketVisualState;
  simulationResult: {
    direction: 'LAN_TO_INTERNET' | 'INTERNET_TO_LAN';
    translated_packet: {
      source_ip: string;
      source_port: number;
      destination_ip: string;
      destination_port: number;
    } | null;
  } | null;
  devices: { id: string; name: string; ip: string }[];
  network: { gateway_ip: string; public_ip: string } | null;
}

export default function PacketAnimation({
  packetState,
  simulationResult,
  devices,
  network,
}: PacketAnimationProps) {
  // Calculate fixed positions for topology nodes
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number }> = {};
    
    // Devices on the left
    devices.forEach((device, index) => {
      positions[device.id] = { 
        x: 80, 
        y: 120 + index * 140 
      };
    });
    
    // NAT Gateway in the middle
    if (network) {
      positions['nat-gateway'] = { x: 400, y: 300 };
    }
    
    // Internet on the right
    positions['internet'] = { x: 720, y: 300 };
    
    return positions;
  }, [devices, network]);

  // Get the path for the packet based on direction and current step
  const getPacketPosition = (): { x: number; y: number } | null => {
    if (!simulationResult || packetState.status === 'IDLE' || !network) return null;

    const direction = simulationResult.direction;
    
    // Find source device (the one matching the source IP)
    const sourceDevice = devices.find(d => d.ip === packetState.sourceIp);
    const sourceDeviceId = sourceDevice?.id || (direction === 'LAN_TO_INTERNET' ? devices[0]?.id : 'internet');
    
    const gatewayPos = nodePositions['nat-gateway'];
    const internetPos = nodePositions['internet'];
    const sourcePos = nodePositions[sourceDeviceId] || (direction === 'INTERNET_TO_LAN' ? internetPos : null);
    
    if (!gatewayPos) return null;
    
    // For LAN_TO_INTERNET: source -> gateway -> internet
    // For INTERNET_TO_LAN: internet -> gateway -> source device
    const targetDeviceId = direction === 'LAN_TO_INTERNET' ? 'internet' : (sourceDevice?.id || devices[0]?.id);
    const targetPos = nodePositions[targetDeviceId] || internetPos;

    if (!sourcePos || !targetPos) return null;

    const progress = packetState.progress;

    if (packetState.status === 'TRAVELLING_TO_GATEWAY') {
      // Moving from source to gateway
      return {
        x: sourcePos.x + (gatewayPos.x - sourcePos.x) * progress,
        y: sourcePos.y + (gatewayPos.y - sourcePos.y) * progress,
      };
    } else if (packetState.status === 'AT_GATEWAY' || packetState.status === 'TRANSLATING') {
      // At gateway
      return gatewayPos;
    } else if (packetState.status === 'TRAVELLING_TO_DESTINATION') {
      // Moving from gateway to target
      return {
        x: gatewayPos.x + (targetPos.x - gatewayPos.x) * progress,
        y: gatewayPos.y + (targetPos.y - gatewayPos.y) * progress,
      };
    } else if (packetState.status === 'COMPLETED') {
      // At final destination
      return targetPos;
    }

    return sourcePos;
  };

  const position = getPacketPosition();

  // Animate packet position smoothly
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (!position) return;

    const animate = () => {
      // Trigger re-render for smooth animation
    };

    animationFrameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameRef.current!);
  }, [position]);

  if (!position || packetState.status === 'IDLE' || packetState.status === 'ERROR') {
    return null;
  }

  // Determine packet color based on protocol and status
  const getPacketColor = () => {
    if (packetState.status === 'COMPLETED') return '#22c55e'; // green
    if (packetState.status === 'ERROR') return '#ef4444'; // red
    if (packetState.status === 'AT_GATEWAY' || packetState.status === 'TRANSLATING') return '#f59e0b'; // amber
    return packetState.protocol === 'TCP' ? '#3b82f6' : '#22c55e'; // blue for TCP, green for UDP
  };

  const color = getPacketColor();
  const isCompleted = packetState.status === 'COMPLETED';

  return (
    <>
      {/* Packet trail */}
      {(packetState.status === 'TRAVELLING_TO_GATEWAY' || packetState.status === 'TRAVELLING_TO_DESTINATION') && (
        <PacketTrail
          startPos={nodePositions[simulationResult?.direction === 'LAN_TO_INTERNET' 
            ? (devices.find(d => d.ip === packetState.sourceIp)?.id || devices[0]?.id || '')
            : 'internet']}
          endPos={nodePositions['nat-gateway']}
          progress={packetState.progress}
          color={color}
        />
      )}

      {/* Animated packet */}
      <div
        style={{
          position: 'absolute',
          left: position.x - 12,
          top: position.y - 12,
          zIndex: 1000,
          pointerEvents: 'none',
          transition: 'transform 0.1s ease-out',
        }}
        className="animate-fade-in"
      >
        <div
          className="relative"
          style={{
            width: 24,
            height: 24,
            borderRadius: '50%',
            backgroundColor: color,
            boxShadow: `0 0 8px ${color}, 0 0 16px ${color}80`,
            border: isCompleted ? '2px solid #22c55e' : '2px solid rgba(255,255,255,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {packetState.protocol === 'TCP' ? (
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
              <path d="M8 7h12m0 0l-4-4m4 4l-4 4M8 7l4 4m-4-4v12" />
            </svg>
          ) : (
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
              <path d="M12 2v20M17 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2z" />
              <path d="M12 9v12M15 9l-3-3M9 9l3-3" />
            </svg>
          )}
        </div>
        
        {/* Packet info tooltip */}
        <div
          style={{
            position: 'absolute',
            bottom: -40,
            left: '50%',
            transform: 'translateX(-50%)',
            whiteSpace: 'nowrap',
            fontSize: '10px',
            padding: '2px 6px',
            background: 'rgba(15, 23, 42, 0.95)',
            color: 'white',
            borderRadius: '4px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            border: `1px solid ${color}40`,
          }}
        >
          {packetState.status === 'COMPLETED' 
            ? `${packetState.translatedPacket?.sourceIp || packetState.sourceIp}:${packetState.translatedPacket?.sourcePort || packetState.sourcePort} → ${packetState.translatedPacket?.destinationIp || packetState.destinationIp}:${packetState.translatedPacket?.destinationPort || packetState.destinationPort}`
            : `${packetState.sourceIp}:${packetState.sourcePort} → ${packetState.destinationIp}:${packetState.destinationPort}`}
        </div>
      </div>
    </>
  );
}

/** Trail behind moving packet */
interface PacketTrailProps {
  startPos: { x: number; y: number } | undefined;
  endPos: { x: number; y: number } | undefined;
  progress: number;
  color: string;
}

function PacketTrail({ startPos, endPos, progress, color }: PacketTrailProps) {
  if (!startPos || !endPos || progress <= 0) return null;

  const startX = startPos.x;
  const startY = startPos.y;
  const endX = endPos.x;
  const endY = endPos.y;

  // Draw trail as a series of fading dots
  const trailPoints = 8;
  const trailElements = [];

  for (let i = 0; i < trailPoints; i++) {
    const trailProgress = progress - (i * 0.08);
    if (trailProgress <= 0) continue;

    const opacity = Math.max(0.1, 0.6 - i * 0.07);
    const size = Math.max(4, 8 - i * 0.5);
    const tx = startX + (endX - startX) * trailProgress;
    const ty = startY + (endY - startY) * trailProgress;

    trailElements.push(
      <div
        key={i}
        style={{
          position: 'absolute',
          left: tx - size / 2,
          top: ty - size / 2,
          width: size,
          height: size,
          borderRadius: '50%',
          backgroundColor: color,
          opacity,
          pointerEvents: 'none',
          zIndex: 999,
        }}
      />
    );
  }

  return <>{trailElements}</>;
}