/** Transformation panel - shows SNAT/DNAT/REVERSE_SNAT details at the gateway. */

import type { PacketSimulationResponse } from '../../types';
import { ActionLabels } from '../../constants/animation';

interface TransformationPanelProps {
  packetState: {
    status: string;
    action: string | null;
    sourceIp: string;
    sourcePort: number;
    destinationIp: string;
    destinationPort: number;
    translatedPacket: {
      sourceIp: string;
      sourcePort: number;
      destinationIp: string;
      destinationPort: number;
    } | null;
  } | null;
  simulationResult: PacketSimulationResponse | null;
  direction: 'LAN_TO_INTERNET' | 'INTERNET_TO_LAN' | null;
}

const actionColors: Record<string, { bg: string; text: string; border: string }> = {
  SNAT: { bg: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-800 dark:text-blue-400', border: 'border-blue-200 dark:border-blue-800' },
  DNAT: { bg: 'bg-purple-50 dark:bg-purple-900/20', text: 'text-purple-800 dark:text-purple-400', border: 'border-purple-200 dark:border-purple-800' },
  REVERSE_SNAT: { bg: 'bg-amber-50 dark:bg-amber-900/20', text: 'text-amber-800 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800' },
  ORIGINAL: { bg: 'bg-slate-50 dark:bg-slate-800/50', text: 'text-slate-800 dark:text-slate-300', border: 'border-slate-200 dark:border-slate-700' },
};

const actionIcons: Record<string, React.ReactNode> = {
  SNAT: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4M8 7l4 4m-4-4v12" />
    </svg>
  ),
  DNAT: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7h-12m0 0l4 4m-4-4l4-4m12 0h-12m0 0l-4 4m4-4l-4-4M4 7v12" />
    </svg>
  ),
  REVERSE_SNAT: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v12m12-12v12M16 7h-12m0 0l4 4m-4-4l4-4m12 0h-12m0 0l-4 4m4-4l-4-4" />
    </svg>
  ),
  ORIGINAL: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

export default function TransformationPanel({
  packetState,
  simulationResult,
  direction,
}: TransformationPanelProps) {
  if (!packetState || !simulationResult) return null;
  if (packetState.status !== 'AT_GATEWAY' && packetState.status !== 'TRANSLATING') return null;
  if (!packetState.action || packetState.action === 'FORWARD' || packetState.action === 'ORIGINAL') return null;

  const action = packetState.action;
  const colors = actionColors[action] || actionColors.ORIGINAL;
  const Icon = actionIcons[action] || actionIcons.ORIGINAL;
  const label = ActionLabels[action] || action;

  // Determine before/after based on action type
  let beforeIp = '', beforePort = 0, afterIp = '', afterPort = 0;
  let beforeLabel = '', afterLabel = '';

  if (action === 'SNAT' || action === 'REVERSE_SNAT') {
    // Source IP/port changes
    beforeIp = packetState.sourceIp;
    beforePort = packetState.sourcePort;
    afterIp = packetState.translatedPacket?.sourceIp || packetState.sourceIp;
    afterPort = packetState.translatedPacket?.sourcePort || packetState.sourcePort;
    beforeLabel = 'Private';
    afterLabel = 'Public';
  } else if (action === 'DNAT') {
    // Destination IP/port changes
    beforeIp = packetState.destinationIp;
    beforePort = packetState.destinationPort;
    afterIp = packetState.translatedPacket?.destinationIp || packetState.destinationIp;
    afterPort = packetState.translatedPacket?.destinationPort || packetState.destinationPort;
    beforeLabel = 'Public';
    afterLabel = 'Private';
  }

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 animate-fade-in ${colors.bg}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="transformation-title"
    >
      <div
        className={`w-full max-w-md rounded-xl border p-6 shadow-2xl animate-slide-up ${colors.border} ${colors.bg.replace('bg-', 'bg-').replace('dark:', 'dark:')}`}
      >
        <div className="flex items-center gap-3 mb-4">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${colors.bg} ${colors.border} ${colors.text}`}>
            {Icon}
          </div>
          <div>
            <h2 id="transformation-title" className="text-xl font-bold text-slate-900 dark:text-white">
              {label}
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {direction === 'INTERNET_TO_LAN' ? 'Incoming packet transformed at NAT Gateway' : 'Outbound packet translated at NAT Gateway'}
            </p>
          </div>
        </div>

        {/* Before/After comparison */}
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">BEFORE ({beforeLabel})</span>
              </div>
              <div className="font-mono text-lg text-slate-900 dark:text-white font-bold">
                {beforeIp}:{beforePort}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col items-center justify-center text-slate-400">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <span className="text-xs text-slate-400">TRANSLATES TO</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-xs font-medium text-green-700 dark:text-green-400 uppercase tracking-wider">AFTER ({afterLabel})</span>
                </div>
                <div className="font-mono text-lg text-green-800 dark:text-green-300 font-bold">
                  {afterIp}:{afterPort}
                </div>
              </div>
            </div>
          </div>

          {/* Protocol and ports unchanged notice */}
          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Protocol unchanged: <code className="font-mono text-slate-900 dark:text-white px-1 py-0.5 rounded bg-slate-200 dark:bg-slate-700">{simulationResult.original_packet.protocol}</code></span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 mt-1 ml-6">
              <span>Destination port unchanged: <code className="font-mono text-slate-900 dark:text-white px-1 py-0.5 rounded bg-slate-200 dark:bg-slate-700">{packetState.destinationPort}</code></span>
            </div>
          </div>
        </div>

        {/* Auto-dismiss notice */}
        <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-400 dark:text-slate-500 text-center">
            Transformation completes automatically in ~{Math.round(1200 / 1000)}s...
          </p>
        </div>
      </div>
    </div>
  );
}