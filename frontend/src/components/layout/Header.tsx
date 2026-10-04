/** Header component. */

import { StatusBadge } from '../common';

interface HeaderProps {
  connectionStatus: 'connected' | 'disconnected' | 'checking';
  simulationState: {
    devices: number;
    natMappings: number;
    portForwardRules: number;
  } | null;
  statsData: {
    totalPackets: number;
    successfulPackets: number;
    failedPackets: number;
    snatPackets: number;
    dnatPackets: number;
    reverseNatPackets: number;
    activeNatMappings: number;
    activePortForwardRules: number;
    averageProcessingTimeMs: number;
  } | null;
}

export default function Header({
  connectionStatus,
  simulationState,
  statsData,
}: HeaderProps) {
  return (
    <header className="bg-slate-900 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Virtual NAT Gateway</h1>
                <p className="text-xs text-slate-400">Network Simulation & Packet Analysis</p>
              </div>
            </div>
            {simulationState && (
              <div className="hidden md:flex items-center gap-6 text-sm">
                <div className="flex items-center gap-1 text-slate-300">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  <span>{simulationState.devices} Devices</span>
                </div>
                <div className="flex items-center gap-1 text-slate-300">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  <span>{simulationState.natMappings} NAT Mappings</span>
                </div>
                <div className="flex items-center gap-1 text-slate-300">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <span>{simulationState.portForwardRules} Port Rules</span>
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            {statsData && (
              <div className="hidden lg:flex items-center gap-4 text-sm text-slate-300">
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="font-mono text-blue-400">{statsData.totalPackets}</span>
                  <span className="text-slate-500">packets</span>
                </div>
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="font-mono text-green-400">{statsData.successfulPackets}</span>
                  <span className="text-slate-500">ok</span>
                </div>
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4M8 7l4 4m-4-4v12" />
                  </svg>
                  <span className="font-mono text-blue-400">{statsData.snatPackets}</span>
                  <span className="text-slate-500">SNAT</span>
                </div>
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7h-12m0 0l4 4m-4-4l4-4m12 0h-12m0 0l-4 4m4-4l-4-4M4 7v12" />
                  </svg>
                  <span className="font-mono text-purple-400">{statsData.dnatPackets}</span>
                  <span className="text-slate-500">DNAT</span>
                </div>
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v12m12-12v12M16 7h-12m0 0l4 4m-4-4l4-4m12 0h-12m0 0l-4 4m4-4l-4-4" />
                  </svg>
                  <span className="font-mono text-amber-400">{statsData.reverseNatPackets}</span>
                  <span className="text-slate-500">Rev</span>
                </div>
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span className="font-mono text-cyan-400">{statsData.averageProcessingTimeMs.toFixed(2)}</span>
                  <span className="text-slate-500">ms avg</span>
                </div>
              </div>
            )}
            <StatusBadge status={connectionStatus.toUpperCase()} />
          </div>
        </div>
      </div>
    </header>
  );
}