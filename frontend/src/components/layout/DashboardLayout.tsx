/** Dashboard layout component. */

import { ReactNode } from 'react';
import Header from './Header';

interface DashboardLayoutProps {
  children: ReactNode;
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

export default function DashboardLayout({
  children,
  connectionStatus,
  simulationState,
  statsData,
}: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Header connectionStatus={connectionStatus} simulationState={simulationState} statsData={statsData} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}