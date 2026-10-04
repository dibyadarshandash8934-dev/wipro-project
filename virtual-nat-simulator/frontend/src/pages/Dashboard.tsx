import { StatusIndicator } from '../components/StatusIndicator';

export function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-700 px-6 py-4">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <h1 className="text-xl font-semibold tracking-tight">
            Virtual NAT Gateway & Port-Forwarding Simulator
          </h1>
          <StatusIndicator />
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-12">
        <div className="rounded-lg border border-gray-700 bg-gray-800 p-8 text-center">
          <h2 className="mb-2 text-2xl font-bold">
            Virtual NAT Gateway & Port-Forwarding Simulator
          </h2>
          <p className="text-gray-400">Educational network simulation — Phase 0: Foundation</p>
        </div>
      </main>
    </div>
  );
}
