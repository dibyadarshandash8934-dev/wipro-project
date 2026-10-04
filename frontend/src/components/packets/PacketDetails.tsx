/** Packet details display component. */

import { StatusBadge } from '../common';
import type { PacketSimulationResponse } from '../../types';

interface PacketDetailsProps {
  result: PacketSimulationResponse;
}

const actionColors: Record<string, 'default' | 'success' | 'error' | 'warning' | 'info'> = {
  SNAT: 'success',
  DNAT: 'info',
  REVERSE_SNAT: 'warning',
  ERROR: 'error',
};

const actionDescriptions: Record<string, string> = {
  SNAT: 'Source NAT - Translated private source to public',
  DNAT: 'Destination NAT - Forwarded to internal device',
  REVERSE_SNAT: 'Reverse SNAT - Response packet translated back',
  ERROR: 'Packet dropped - No matching rule or mapping',
};

export function PacketDetails({ result }: PacketDetailsProps) {
  const actionType = result.action ?? 'ERROR';
  const isSuccess = result.success;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Simulation Result</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {actionDescriptions[actionType] || 'Unknown action'}
          </p>
        </div>
        <StatusBadge status={actionType} variant={actionColors[actionType] ?? 'default'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Original Packet */}
        <div className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800/50">
          <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3">Original Packet</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500 dark:text-slate-400">Protocol</span>
              <span className="font-mono text-sm text-slate-900 dark:text-white">{result.original_packet.protocol}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500 dark:text-slate-400">Source</span>
              <span className="font-mono text-sm text-slate-900 dark:text-white">
                {result.original_packet.source_ip}:{result.original_packet.source_port}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-500 dark:text-slate-400">Destination</span>
              <span className="font-mono text-sm text-slate-900 dark:text-white">
                {result.original_packet.destination_ip}:{result.original_packet.destination_port}
              </span>
            </div>
          </div>
        </div>

        {/* Translated Packet */}
        <div className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800/50">
          <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3">
            {isSuccess ? 'Translated Packet' : 'Packet Dropped'}
          </h4>
          {isSuccess && result.translated_packet ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500 dark:text-slate-400">Protocol</span>
                <span className="font-mono text-sm text-slate-900 dark:text-white">{result.translated_packet.protocol}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500 dark:text-slate-400">Source</span>
                <span className="font-mono text-sm text-blue-600 dark:text-blue-400">
                  {result.translated_packet.source_ip}:{result.translated_packet.source_port}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500 dark:text-slate-400">Destination</span>
                <span className="font-mono text-sm text-slate-900 dark:text-white">
                  {result.translated_packet.destination_ip}:{result.translated_packet.destination_port}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-red-600 dark:text-red-400">
              {result.error || 'Packet was dropped'}
            </p>
          )}
        </div>
      </div>

      {/* NAT Entry Reference */}
      {result.nat_entry && isSuccess && (
        <div className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50 dark:bg-slate-800/50">
          <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3">NAT Table Entry</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div>
              <span className="text-slate-400 dark:text-slate-500">Protocol</span>
              <div className="font-mono text-slate-900 dark:text-white">{result.nat_entry.protocol}</div>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Private</span>
              <div className="font-mono text-slate-900 dark:text-white">{result.nat_entry.private_ip}:{result.nat_entry.private_port}</div>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Public</span>
              <div className="font-mono text-blue-600 dark:text-blue-400">{result.nat_entry.public_ip}:{result.nat_entry.public_port}</div>
            </div>
            <div>
              <span className="text-slate-400 dark:text-slate-500">Destination</span>
              <div className="font-mono text-slate-900 dark:text-white">{result.nat_entry.destination_ip}:{result.nat_entry.destination_port}</div>
            </div>
            <div className="md:col-span-4">
              <span className="text-slate-400 dark:text-slate-500">State</span>
              <div className="font-mono text-slate-900 dark:text-white">{result.nat_entry.state}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}