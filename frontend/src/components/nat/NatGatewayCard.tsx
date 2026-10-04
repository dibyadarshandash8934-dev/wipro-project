/** NAT Gateway card component. */

import { StatusBadge } from '../common';
import type { Network } from '../../types';

interface NatGatewayCardProps {
  network: Network | null;
  natMappingsCount: number;
  portForwardRulesCount: number;
}

export default function NatGatewayCard({
  network,
  natMappingsCount,
  portForwardRulesCount,
}: NatGatewayCardProps) {
  if (!network) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <div className="text-center py-8">
          <svg className="w-16 h-16 mx-auto mb-4 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">NAT Gateway</h3>
          <p className="text-slate-500 dark:text-slate-400">Create a network to configure the NAT gateway</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">NAT Gateway</h2>
        <StatusBadge status="ACTIVE" variant="success" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">LAN Gateway</label>
          <p className="text-sm font-mono text-slate-900 dark:text-white mt-1">{network.gateway_ip}</p>
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Public IP</label>
          <p className="text-sm font-mono text-slate-900 dark:text-white mt-1">{network.public_ip}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
          <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{natMappingsCount}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">Active NAT Mappings</div>
        </div>
        <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
          <div className="text-3xl font-bold text-green-600 dark:text-green-400">{portForwardRulesCount}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">Port Forward Rules</div>
        </div>
      </div>
    </div>
  );
}