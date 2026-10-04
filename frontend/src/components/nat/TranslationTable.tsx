/** NAT Translation Table component. */

import { useState } from 'react';
import { getNatTable, clearNatTable } from '../../services/api';
import { Button, LoadingState, EmptyState, ErrorMessage } from '../common';
import type { NATEntry } from '../../types';

export default function TranslationTable({ onTableChanged }: { onTableChanged: () => void }) {
  const [entries, setEntries] = useState<NATEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTable = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getNatTable();
      setEntries(data.entries);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load NAT table');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!confirm('Are you sure you want to clear all NAT mappings?')) return;
    setClearing(true);
    setError(null);
    try {
      await clearNatTable();
      onTableChanged();
      await fetchTable();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear NAT table');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">NAT Translation Table</h2>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={fetchTable} disabled={loading}>
            Refresh
          </Button>
          <Button variant="danger" size="sm" onClick={handleClear} loading={clearing} disabled={loading || entries.length === 0}>
            Clear Table
          </Button>
        </div>
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {loading ? (
        <LoadingState message="Loading NAT table..." />
      ) : entries.length === 0 ? (
        <EmptyState
          title="No active NAT mappings"
          description="NAT mappings will appear here when devices communicate with the Internet"
          icon={
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          }
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full" role="grid">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Protocol</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Private Address</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Public Address</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Destination</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {entries.map((entry, index) => (
                <tr key={`${entry.protocol}-${entry.private_ip}-${entry.private_port}-${index}`} className="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      entry.protocol === 'TCP'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                        : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    }`}>
                      {entry.protocol}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-sm font-mono text-slate-900 dark:text-white">
                      {entry.private_ip}:{entry.private_port}
                    </code>
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-sm font-mono text-blue-600 dark:text-blue-400">
                      {entry.public_ip}:{entry.public_port}
                    </code>
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-sm font-mono text-slate-600 dark:text-slate-400">
                      {entry.destination_ip}:{entry.destination_port}
                    </code>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      entry.state === 'ACTIVE'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                        : 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
                    }`}>
                      {entry.state}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}