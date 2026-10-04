import { useEffect, useState } from 'react';
import { checkHealth } from '../services/api';

type ConnectionStatus = 'checking' | 'connected' | 'disconnected';

export function StatusIndicator() {
  const [status, setStatus] = useState<ConnectionStatus>('checking');

  useEffect(() => {
    let mounted = true;

    async function verify() {
      try {
        const data = await checkHealth();
        if (mounted) {
          setStatus(data.status === 'ok' ? 'connected' : 'disconnected');
        }
      } catch {
        if (mounted) setStatus('disconnected');
      }
    }

    verify();
    return () => {
      mounted = false;
    };
  }, []);

  const colors: Record<ConnectionStatus, string> = {
    checking: 'bg-yellow-400',
    connected: 'bg-green-500',
    disconnected: 'bg-red-500',
  };

  const labels: Record<ConnectionStatus, string> = {
    checking: 'Checking connection...',
    connected: 'Backend connected',
    disconnected: 'Backend unavailable',
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className={`inline-block h-3 w-3 rounded-full ${colors[status]}`} />
      <span className="text-gray-300">{labels[status]}</span>
    </div>
  );
}
