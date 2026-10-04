/** Network configuration form component. */

import { useState, FormEvent } from 'react';
import { createNetwork, deleteNetwork } from '../../services/api';
import { Button, Input } from '../common';
import { ErrorMessage } from '../common';
import type { Network } from '../../types';

interface NetworkConfigurationProps {
  onNetworkCreated: () => void;
  existingNetwork: Network | null;
}

export default function NetworkConfiguration({ onNetworkCreated, existingNetwork }: NetworkConfigurationProps) {
  const [cidr, setCidr] = useState('192.168.1.0/24');
  const [gatewayIp, setGatewayIp] = useState('192.168.1.1');
  const [publicIp, setPublicIp] = useState('203.0.113.5');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(!existingNetwork);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createNetwork({ cidr, gateway_ip: gatewayIp, public_ip: publicIp });
      setShowForm(false);
      onNetworkCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create network');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete the network configuration? This will also reset all devices and NAT mappings.')) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await deleteNetwork();
      setShowForm(true);
      onNetworkCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete network');
    } finally {
      setLoading(false);
    }
  };

  if (existingNetwork && !showForm) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Network Configuration</h2>
          <Button variant="danger" size="sm" onClick={() => setShowForm(true)}>
            Reconfigure
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">CIDR</label>
            <p className="text-sm font-mono text-slate-900 dark:text-white mt-1">{existingNetwork.cidr}</p>
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Gateway IP</label>
            <p className="text-sm font-mono text-slate-900 dark:text-white mt-1">{existingNetwork.gateway_ip}</p>
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Public IP</label>
            <p className="text-sm font-mono text-slate-900 dark:text-white mt-1">{existingNetwork.public_ip}</p>
          </div>
        </div>
        <Button variant="danger" size="sm" onClick={handleDelete}>
          Delete Network
        </Button>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Create Network</h2>
      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="CIDR"
            value={cidr}
            onChange={(e) => setCidr(e.target.value)}
            placeholder="192.168.1.0/24"
            helperText="Network CIDR (e.g., 192.168.1.0/24)"
            disabled={loading}
          />
          <Input
            label="Gateway IP"
            value={gatewayIp}
            onChange={(e) => setGatewayIp(e.target.value)}
            placeholder="192.168.1.1"
            helperText="LAN gateway IP"
            disabled={loading}
          />
          <Input
            label="Public IP"
            value={publicIp}
            onChange={(e) => setPublicIp(e.target.value)}
            placeholder="203.0.113.5"
            helperText="NAT gateway public IP"
            disabled={loading}
          />
        </div>
        <div className="pt-4">
          <Button type="submit" loading={loading} className="w-full md:w-auto">
            {existingNetwork ? 'Update Network' : 'Create Network'}
          </Button>
        </div>
      </form>
    </div>
  );
}