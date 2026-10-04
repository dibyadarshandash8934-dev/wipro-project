interface StatusIndicatorProps {
  status: 'connected' | 'disconnected' | 'checking';
}

export default function StatusIndicator({ status }: StatusIndicatorProps) {
  const styles = {
    connected: 'bg-green-500',
    disconnected: 'bg-red-500',
    checking: 'bg-yellow-500 animate-pulse',
  };

  const labels = {
    connected: 'Backend: Connected',
    disconnected: 'Backend: Disconnected',
    checking: 'Backend: Checking...',
  };

  return (
    <div className="flex items-center gap-2">
      <span
        data-testid="status-indicator"
        className={`w-3 h-3 rounded-full ${styles[status]}`}
        aria-hidden="true"
      />
      <span className="text-sm font-medium text-gray-700">
        {labels[status]}
      </span>
    </div>
  );
}