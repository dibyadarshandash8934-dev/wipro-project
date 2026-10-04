/** Main Dashboard page component. */

import { useState, useEffect, useCallback } from 'react';
import { DashboardLayout } from '../components/layout';
import { NetworkConfiguration } from '../components/network';
import { DeviceList } from '../components/network';
import { NetworkTopology } from '../components/network';
import { NatGatewayCard } from '../components/nat';
import { TranslationTable } from '../components/nat';
import { PortForwardTable } from '../components/nat';
import { PacketSimulator } from '../components/packets';
import { ErrorMessage, LoadingState } from '../components/common';
import { checkHealth, getSimulationState, resetSimulation, getSimulationStats } from '../services/api';
import type { SimulationState, SimulationStats } from '../types';

export default function Dashboard() {
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [simulationState, setSimulationState] = useState<SimulationState | null>(null);
  const [simulationStats, setSimulationStats] = useState<SimulationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resetting, setResetting] = useState(false);

  const fetchHealth = useCallback(async () => {
    try {
      await checkHealth();
      setConnectionStatus('connected');
    } catch {
      setConnectionStatus('disconnected');
    }
  }, []);

  const fetchSimulationState = useCallback(async () => {
    try {
      setError(null);
      const data = await getSimulationState();
      setSimulationState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load simulation state');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSimulationStats = useCallback(async () => {
    try {
      const data = await getSimulationStats();
      setSimulationStats(data);
    } catch {
      // Silently ignore stats errors
    }
  }, []);

  const handleReset = useCallback(async () => {
    if (!confirm('Are you sure you want to reset the simulation? This will remove all network configuration, devices, NAT mappings, and port forward rules.')) {
      return;
    }
    setResetting(true);
    setError(null);
    try {
      await resetSimulation();
      setSimulationState({ network: null, devices: [], nat_entries: [], port_forward_rules: [] });
      setSimulationStats(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset simulation');
    } finally {
      setResetting(false);
    }
  }, []);

  const handleNetworkChange = useCallback(async () => {
    await fetchSimulationState();
    await fetchSimulationStats();
  }, [fetchSimulationState, fetchSimulationStats]);

  const handleDevicesChange = useCallback(async () => {
    await fetchSimulationState();
    await fetchSimulationStats();
  }, [fetchSimulationState, fetchSimulationStats]);

  const handleTableChange = useCallback(async () => {
    await fetchSimulationState();
    await fetchSimulationStats();
  }, [fetchSimulationState, fetchSimulationStats]);

  const handleRulesChange = useCallback(async () => {
    await fetchSimulationState();
    await fetchSimulationStats();
  }, [fetchSimulationState, fetchSimulationStats]);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  useEffect(() => {
    fetchSimulationState();
  }, [fetchSimulationState]);

  useEffect(() => {
    fetchSimulationStats();
  }, [fetchSimulationStats]);

  const stats = simulationState
    ? {
        devices: simulationState.devices.length,
        natMappings: simulationState.nat_entries.length,
        portForwardRules: simulationState.port_forward_rules.length,
      }
    : null;

  const statsData = simulationStats
    ? {
        totalPackets: simulationStats.total_packets,
        successfulPackets: simulationStats.successful_packets,
        failedPackets: simulationStats.failed_packets,
        snatPackets: simulationStats.snat_packets,
        dnatPackets: simulationStats.dnat_packets,
        reverseNatPackets: simulationStats.reverse_nat_packets,
        activeNatMappings: simulationStats.active_nat_mappings,
        activePortForwardRules: simulationStats.active_port_forward_rules,
        averageProcessingTimeMs: simulationStats.average_processing_time_ms,
      }
    : null;

  if (loading) {
    return (
      <DashboardLayout connectionStatus={connectionStatus} simulationState={stats} statsData={statsData}>
        <LoadingState message="Loading simulation..." size="lg" />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout connectionStatus={connectionStatus} simulationState={stats} statsData={statsData}>
      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Top Row - Network Config, NAT Gateway, Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-1">
          <NetworkConfiguration
            onNetworkCreated={handleNetworkChange}
            existingNetwork={simulationState?.network ?? null}
          />
        </div>
        <div className="lg:col-span-1">
          <NatGatewayCard
            network={simulationState?.network ?? null}
            natMappingsCount={simulationState?.nat_entries.length ?? 0}
            portForwardRulesCount={simulationState?.port_forward_rules.length ?? 0}
          />
        </div>
        <div className="lg:col-span-1">
          <DeviceList
            onDevicesChanged={handleDevicesChange}
            network={simulationState?.network ? { gateway_ip: simulationState.network.gateway_ip, cidr: simulationState.network.cidr } : null}
          />
        </div>
      </div>

      {/* Middle Row - Network Topology */}
      <div className="mb-6">
        <NetworkTopology
          network={simulationState?.network ?? null}
          devices={simulationState?.devices ?? []}
        />
      </div>

      {/* Bottom Row - Packet Simulator, Port Forwarding, NAT Table */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-1">
          <PacketSimulator
            network={simulationState?.network ? { public_ip: simulationState.network.public_ip, gateway_ip: simulationState.network.gateway_ip } : null}
            devices={simulationState?.devices.map(d => ({ id: d.id, ip: d.ip, name: d.name })) ?? []}
          />
        </div>
        <div className="xl:col-span-1">
          <PortForwardTable
            onRulesChanged={handleRulesChange}
            networkPublicIp={simulationState?.network?.public_ip ?? null}
          />
        </div>
        <div className="xl:col-span-1">
          <TranslationTable onTableChanged={handleTableChange} />
        </div>
      </div>

      {/* Reset Button */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={handleReset}
          disabled={resetting}
          className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg transition-colors disabled:opacity-50"
        >
          {resetting ? 'Resetting...' : 'Reset Simulation'}
        </button>
      </div>
    </DashboardLayout>
  );
}