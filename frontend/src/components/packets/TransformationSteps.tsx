/** Transformation steps display component. */

import type { PacketTransformation } from '../../types';

interface TransformationStepsProps {
  transformations: PacketTransformation[];
}

const stageColors: Record<string, string> = {
  LAN: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800',
  NAT_GATEWAY: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200 dark:border-purple-800',
  INTERNET: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800',
};

const actionIcons: Record<string, React.ReactNode> = {
  ORIGINAL: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  SNAT: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4M8 7l4 4m-4-4v12" />
    </svg>
  ),
  DNAT: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7h-12m0 0l4 4m-4-4l4-4m12 0h-12m0 0l-4 4m4-4l-4-4M4 7v12" />
    </svg>
  ),
  FORWARD: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>
  ),
};

const actionLabels: Record<string, string> = {
  ORIGINAL: 'Original Packet',
  SNAT: 'SNAT Applied',
  DNAT: 'DNAT Applied',
  FORWARD: 'Forwarded',
};

export function TransformationSteps({ transformations }: TransformationStepsProps) {
  if (!transformations.length) return null;

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Transformation Steps</h3>
      <div className="space-y-3">
        {transformations.map((step, index) => (
          <div key={`${step.stage}-${step.action}-${index}`} className="relative">
            <div className="flex items-start gap-4">
              {/* Step number and connector */}
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white ${stageColors[step.stage] || 'bg-gray-200 text-gray-800'}`}>
                  {index + 1}
                </div>
                {index < transformations.length - 1 && (
                  <div className="w-0.5 h-8 bg-slate-200 dark:bg-slate-700 mt-1" />
                )}
              </div>

              {/* Step content */}
              <div className={`flex-1 p-4 rounded-lg border ${stageColors[step.stage] || 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'}`}>
                <div className="flex items-center gap-3 mb-2">
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${stageColors[step.stage] || 'bg-gray-100 text-gray-800'}`}>
                    {step.stage}
                  </span>
                  <span className="flex items-center gap-1 text-sm font-medium text-slate-700 dark:text-slate-300">
                    {actionIcons[step.action]}
                    {actionLabels[step.action] || step.action}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-slate-400 dark:text-slate-500">Source</span>
                    <div className="font-mono text-slate-900 dark:text-white">{step.source_ip}:{step.source_port}</div>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-slate-500">Destination</span>
                    <div className="font-mono text-slate-900 dark:text-white">{step.destination_ip}:{step.destination_port}</div>
                  </div>
                </div>

                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{step.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}