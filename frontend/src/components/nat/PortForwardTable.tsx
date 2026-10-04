/** Port Forwarding table component. */

import { useState, FormEvent } from 'react';
import { createPortForwardRule, deletePortForwardRule, getPortForwardRules } from '../../services/api';
import { Button, Input, Select } from '../common';
import { LoadingState, EmptyState, ErrorMessage } from '../common';
import type { PortForwardRule, Protocol } from '../../types';

export default function PortForwardTable({
  onRulesChanged,
  networkPublicIp,
}: { onRulesChanged: () => void; networkPublicIp: string | null }) {
  const [rules, setRules] = useState<PortForwardRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [protocol, setProtocol] = useState<Protocol>('TCP');
  const [publicPort, setPublicPort] = useState('');
  const [privateIp, setPrivateIp] = useState('');
  const [privatePort, setPrivatePort] = useState('');

  const fetchRules = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPortForwardRules();
      setRules(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load port forward rules');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!publicPort || !privateIp || !privatePort) return;
    setAdding(true);
    setError(null);
    try {
      await createPortForwardRule({
        protocol,
        public_ip: networkPublicIp!,
        public_port: parseInt(publicPort, 10),
        private_ip: privateIp,
        private_port: parseInt(privatePort, 10),
      });
      setPublicPort('');
      setPrivateIp('');
      setPrivatePort('');
      onRulesChanged();
      await fetchRules();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add port forward rule');
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this port forward rule?')) return;
    setDeleting(ruleId);
    try {
      await deletePortForwardRule(ruleId);
      onRulesChanged();
      await fetchRules();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete port forward rule');
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Port Forwarding</h2>
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Add Rule Form */}
      <form onSubmit={handleSubmit} className="mb-6 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg space-y-4">
        <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">Add Port Forward Rule</h3>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <Select
            label="Protocol"
            value={protocol}
            onChange={(e) => setProtocol(e.target.value as Protocol)}
            options={[
              { value: 'TCP', label: 'TCP' },
              { value: 'UDP', label: 'UDP' },
            ]}
            disabled={adding}
          />
          <Input
            label="Public Port"
            type="number"
            value={publicPort}
            onChange={(e) => setPublicPort(e.target.value)}
            placeholder="8080"
            min={1}
            max={65535}
            disabled={adding || !networkPublicIp}
          />
          <Input
            label="Private IP"
            value={privateIp}
            onChange={(e) => setPrivateIp(e.target.value)}
            placeholder="192.168.1.10"
            disabled={adding}
          />
          <Input
            label="Private Port"
            type="number"
            value={privatePort}
            onChange={(e) => setPrivatePort(e.target.value)}
            placeholder="80"
            min={1}
            max={65535}
            disabled={adding}
          />
        </div>
        <div className="flex items-center gap-2">
          <Button type="submit" loading={adding} disabled={adding || !networkPublicIp || !publicPort || !privateIp || !privatePort}>
            Add Rule
          </Button>
          {!networkPublicIp && (
            <span className="text-sm text-amber-600 dark:text-amber-400">Create network first</span>
          )}
        </div>
      </form>

      {/* Rules Table */}
      <div className="overflow-x-auto">
        {loading ? (
          <LoadingState message="Loading port forward rules..." />
        ) : rules.length === 0 ? (
          <EmptyState
            title="No port forward rules"
            description="Add rules to forward incoming Internet traffic to internal devices"
            icon={
              <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            }
          />
        ) : (
          <table className="w-full" role="grid">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Protocol</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Public</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Private</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {rules.map((rule) => (
                <tr key={rule.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      rule.protocol === 'TCP'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                        : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    }`}>
                      {rule.protocol}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-sm font-mono text-slate-900 dark:text-white">
                      {rule.public_ip}:{rule.public_port}
                    </code>
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-sm font-mono text-green-600 dark:text-green-400">
                      {rule.private_ip}:{rule.private_port}
                    </code>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(rule.id)}
                      disabled={deleting === rule.id}
                      className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium disabled:opacity-50"
                    >
                      {deleting === rule.id ? 'Deleting...' : 'Delete'}
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