/** Custom hook for managing simulation state. */

import { useState, useEffect, useCallback } from 'react';
import { getSimulationState, resetSimulation as apiResetSimulation } from '../services/api';
import type { SimulationState } from '../types';

interface UseSimulationStateReturn {
  state: SimulationState | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  resetSimulation: () => Promise<void>;
}

export function useSimulationState(): UseSimulationStateReturn {
  const [state, setState] = useState<SimulationState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSimulationState();
      setState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load simulation state');
    } finally {
      setLoading(false);
    }
  }, []);

  const resetSimulation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await apiResetSimulation();
      setState({ network: null, devices: [], nat_entries: [], port_forward_rules: [] });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset simulation');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { state, loading, error, refresh, resetSimulation };
}