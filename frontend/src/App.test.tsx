import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import StatusIndicator from './components/StatusIndicator';

describe('StatusIndicator', () => {
  it('renders connected status', () => {
    render(<StatusIndicator status="connected" />);
    expect(screen.getByText('Backend: Connected')).toBeInTheDocument();
    const indicator = screen.getByTestId('status-indicator');
    expect(indicator).toHaveClass('bg-green-500');
  });

  it('renders disconnected status', () => {
    render(<StatusIndicator status="disconnected" />);
    expect(screen.getByText('Backend: Disconnected')).toBeInTheDocument();
    const indicator = screen.getByTestId('status-indicator');
    expect(indicator).toHaveClass('bg-red-500');
  });

  it('renders checking status', () => {
    render(<StatusIndicator status="checking" />);
    expect(screen.getByText('Backend: Checking...')).toBeInTheDocument();
    const indicator = screen.getByTestId('status-indicator');
    expect(indicator).toHaveClass('bg-yellow-500');
  });
});