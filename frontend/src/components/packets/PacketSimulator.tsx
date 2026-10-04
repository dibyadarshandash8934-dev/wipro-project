/** Packet simulator component with animation. */

import { useState, FormEvent } from 'react';
import { simulatePacket } from '../../services/api';
import { Button, Input, Select } from '../common';
import { ErrorMessage } from '../common';
import { PacketDetails } from './PacketDetails';
import { TransformationSteps } from './TransformationSteps';
import PacketAnimation from './PacketAnimation';
import TransformationPanel from './TransformationPanel';
import { usePacketAnimation } from '../../hooks/usePacketAnimation';
import type { PacketSimulationResponse, Protocol, PacketDirection } from '../../types';

export default function PacketSimulator({
  network,
  devices,
}: { 
  network: { public_ip: string; gateway_ip: string } | null; 
  devices: { id: string; ip: string; name: string }[] 
}) {
  const [direction, setDirection] = useState<PacketDirection>('LAN_TO_INTERNET');
  const [protocol, setProtocol] = useState<Protocol>('TCP');
  const [sourceIp, setSourceIp] = useState('');
  const [sourcePort, setSourcePort] = useState('');
  const [destinationIp, setDestinationIp] = useState('');
  const [destinationPort, setDestinationPort] = useState('');
  const [result, setResult] = useState<PacketSimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAnimation, setShowAnimation] = useState(false);

  const { 
    packetState, 
    isPlaying, 
    isPaused, 
    play, 
    pause, 
    resume, 
    replay, 
    skip, 
    reset 
  } = usePacketAnimation({
    simulationResult: result,
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setShowAnimation(false);
    try {
      const data = await simulatePacket({
        direction,
        protocol,
        source_ip: sourceIp,
        source_port: parseInt(sourcePort, 10),
        destination_ip: destinationIp,
        destination_port: parseInt(destinationPort, 10),
      });
      setResult(data);
      if (data.success) {
        setShowAnimation(true);
        // Small delay to allow UI to update
        setTimeout(() => play(), 100);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const getDefaultSourcePort = () => {
    return Math.floor(Math.random() * 10000) + 50000;
  };

  const handleReplay = () => {
    setShowAnimation(true);
    replay();
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Packet Simulator</h2>
        {result && result.success && (
          <div className="flex items-center gap-2">
            <Button 
              variant={isPlaying ? 'secondary' : 'primary'} 
              size="sm"
              onClick={isPlaying ? pause : (isPaused ? resume : play)}
              disabled={loading || !result.success}
            >
              {isPlaying ? 'Pause' : isPaused ? 'Resume' : 'Play Animation'}
            </Button>
            <Button variant="secondary" size="sm" onClick={handleReplay} disabled={loading || !result.success}>
              Replay
            </Button>
            <Button variant="ghost" size="sm" onClick={skip} disabled={loading || !result.success || isPlaying}>
              Skip
            </Button>
            <Button variant="ghost" size="sm" onClick={reset} disabled={loading}>
              Reset
            </Button>
          </div>
        )}
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Select
            label="Direction"
            value={direction}
            onChange={(e) => setDirection(e.target.value as PacketDirection)}
            options={[
              { value: 'LAN_TO_INTERNET', label: 'LAN → Internet (SNAT)' },
              { value: 'INTERNET_TO_LAN', label: 'Internet → LAN (DNAT/Reverse)' },
            ]}
            disabled={loading}
          />
          <Select
            label="Protocol"
            value={protocol}
            onChange={(e) => setProtocol(e.target.value as Protocol)}
            options={[
              { value: 'TCP', label: 'TCP' },
              { value: 'UDP', label: 'UDP' },
            ]}
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Source IP"
            value={sourceIp}
            onChange={(e) => setSourceIp(e.target.value)}
            placeholder={direction === 'LAN_TO_INTERNET' ? '192.168.1.10' : '198.51.100.20'}
            disabled={loading}
          />
          <Input
            label="Source Port"
            type="number"
            value={sourcePort}
            onChange={(e) => setSourcePort(e.target.value)}
            placeholder={String(getDefaultSourcePort())}
            min={1}
            max={65535}
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Destination IP"
            value={destinationIp}
            onChange={(e) => setDestinationIp(e.target.value)}
            placeholder={direction === 'LAN_TO_INTERNET' ? '8.8.8.8' : network?.public_ip || ''}
            disabled={loading}
          />
          <Input
            label="Destination Port"
            type="number"
            value={destinationPort}
            onChange={(e) => setDestinationPort(e.target.value)}
            placeholder={direction === 'LAN_TO_INTERNET' ? '443' : '8080'}
            min={1}
            max={65535}
            disabled={loading}
          />
        </div>

        <div className="pt-4">
          <Button type="submit" loading={loading} className="w-full sm:w-auto">
            Simulate Packet
          </Button>
        </div>
      </form>

      {/* Animation Area */}
      {showAnimation && result && (
        <div className="relative mt-6">
          <PacketAnimation
            packetState={packetState}
            simulationResult={{ direction, translated_packet: result.translated_packet }}
            devices={devices}
            network={network ? { gateway_ip: network.gateway_ip, public_ip: network.public_ip } : null}
          />
          <TransformationPanel
            packetState={packetState}
            simulationResult={result}
            direction={direction}
          />
        </div>
      )}

      {/* Results */}
      {result && !showAnimation && (
        <div className="mt-6 animate-fade-in">
          <PacketDetails result={result} />
          <TransformationSteps transformations={result.transformations} />
        </div>
      )}
    </div>
  );
}