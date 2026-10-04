import '@testing-library/jest-dom';
import { vi } from 'vitest';

Object.defineProperty(window, 'fetch', {
  value: vi.fn(),
  writable: true,
});