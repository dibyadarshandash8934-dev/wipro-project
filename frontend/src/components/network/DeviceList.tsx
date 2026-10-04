/** Device list component. */

import { useState, FormEvent } from 'react';
import { createDevice, deleteDevice, getDevices } from '../../services/api';
import { Button, Input, Select } from '../common';
import { LoadingState, ErrorMessage, EmptyState } from '../common';
import type { VirtualDevice, DeviceType } from '../../types';

interface DeviceListProps {
  onDevicesChanged: () => void;
  network: { gateway_ip: string; cidr: string } | null;
}

const deviceTypeOptions = [
  { value: 'pc', label: 'PC' },
  { value: 'server', label: 'Server' },
  { value: 'laptop', label: 'Laptop' },
  { value: 'phone', label: 'Phone' },
  { value: 'iot', label: 'IoT' },
] as const satisfies { value: DeviceType; label: string }[];

export default function DeviceList({ onDevicesChanged, network }: DeviceListProps) {
  const [devices, setDevices] = useState<VirtualDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [ip, setIp] = useState('');
  const [type, setType] = useState<DeviceType>('pc');

  const fetchDevices = async () => {
    try {
      setLoading(true);
      const data = await getDevices();
      setDevices(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load devices');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !ip.trim()) return;
    setAdding(true);
    setError(null);
    try {
      await createDevice({ name: name.trim(), ip: ip.trim(), type });
      setName('');
      setIp('');
      setType('pc');
      onDevicesChanged();
      await fetchDevices();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add device');
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (deviceId: string) => {
    if (!confirm('Are you sure you want to remove this device?')) return;
    try {
      await deleteDevice(deviceId);
      onDevicesChanged();
      await fetchDevices();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete device');
    }
  };

  const getSuggestedIp = () => {
    if (!network) return '';
    const base = network.gateway_ip.split('.').slice(0, 3).join('.');
    const used = new Set(devices.map(d => d.ip.split('.')[3]));
    for (let i = 2; i <= 254; i++) {
      if (!used.has(String(i))) {
        return `${base}.${i}`;
      }
    }
    return '';
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Virtual Devices</h2>
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Add Device Form */}
      <form onSubmit={handleSubmit} className="mb-6 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg space-y-4">
        <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">Add Device</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Input
            label="Device Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="PC-01"
            disabled={adding}
          />
          <Input
            label="IP Address"
            value={ip}
            onChange={(e) => setIp(e.target.value)}
            placeholder={getSuggestedIp() || '192.168.1.10'}
            helperText={network ? `Must be in ${network.cidr}` : 'Create network first'}
            disabled={adding || !network}
          />
          <Select
            label="Type"
            value={type}
            onChange={(e) => setType(e.target.value as DeviceType)}
            options={deviceTypeOptions}
            disabled={adding}
          />
        </div>
        <Button type="submit" loading={adding} disabled={!network || !name.trim() || !ip.trim()}>
          Add Device
        </Button>
      </form>

      {/* Device List */}
      <div className="overflow-x-auto">
        {loading ? (
          <LoadingState message="Loading devices..." />
        ) : devices.length === 0 ? (
          <EmptyState
            title="No devices configured"
            description="Add virtual devices to your network to begin simulation"
            icon={
              <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
          />
        ) : (
          <table className="w-full" role="grid">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Name</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Type</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">IP Address</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {devices.map((device) => (
                <tr key={device.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                        <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          {device.type === 'server' && (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                          )}
                          {device.type === 'laptop' && (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h-2l-1.5-4.5A2 2 0 0010.5 11H8.5a2 2 0 00-1.983 1.5L6 17H4a2 2 0 00-2 2v1h20v-1a2 2 0 00-2-2zM11 9v6m3-6v6m-9-2V7a2 2 0 012-2h2a2 2 0 012 2v2m-6 0h.01M13 14h.01M9 14h.01" />
                          )}
                          {device.type === 'phone' && (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          )}
                          {device.type === 'iot' && (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                          )}
                          {device.type === 'pc' && (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                          )}
                        </svg>
                      </div>
                      <span className="font-medium text-slate-900 dark:text-white">{device.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-slate-600 dark:text-slate-400 capitalize">{device.type}</span>
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-sm font-mono text-slate-900 dark:text-white">{device.ip}</code>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(device.id)}
                      className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}