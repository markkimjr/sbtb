import { vi } from "vitest";

export function mockRouter() {
  return {
    push: vi.fn(),
    replace: vi.fn(),
    refresh: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    prefetch: vi.fn(),
  };
}

export function mockSearchParams(entries: Record<string, string> = {}) {
  return new URLSearchParams(entries);
}
