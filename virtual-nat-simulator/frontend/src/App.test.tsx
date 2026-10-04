import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from './App';

// Mock the api module to avoid real fetch calls during tests
vi.mock('./services/api', () => ({
  checkHealth: vi.fn().mockResolvedValue({ status: 'ok' }),
}));

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the dashboard heading', () => {
    render(<App />);
    const headings = screen.getAllByText(/Virtual NAT Gateway & Port-Forwarding Simulator/i);
    expect(headings.length).toBeGreaterThanOrEqual(1);
  });
});
