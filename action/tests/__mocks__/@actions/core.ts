/**
 * Mock @actions/core for Vitest testing.
 *
 * SECURITY: P1-SEC-003 - Tests for token masking
 */

import { vi } from 'vitest';

// Input storage
let mockInputs: Record<string, string> = {};

// Output storage
let mockOutputs: Record<string, string> = {};

// Secret storage
let mockSecrets: string[] = [];

// Log storage
let mockInfoMessages: string[] = [];
let mockWarningMessages: string[] = [];
let mockErrorMessages: string[] = [];
let mockFailedMessages: string[] = [];

/**
 * Set mock inputs for testing.
 */
export function setMockInputs(inputs: Record<string, string>): void {
  mockInputs = { ...inputs };
}

/**
 * Get recorded outputs.
 */
export function getMockOutputs(): Record<string, string> {
  return { ...mockOutputs };
}

/**
 * Get recorded secrets (for P1-SEC-003 testing).
 */
export function getMockSecrets(): string[] {
  return [...mockSecrets];
}

/**
 * Get recorded info messages.
 */
export function getInfoMessages(): string[] {
  return [...mockInfoMessages];
}

/**
 * Get recorded warning messages.
 */
export function getWarningMessages(): string[] {
  return [...mockWarningMessages];
}

/**
 * Get recorded error messages.
 */
export function getErrorMessages(): string[] {
  return [...mockErrorMessages];
}

/**
 * Get recorded setFailed messages.
 */
export function getFailedMessages(): string[] {
  return [...mockFailedMessages];
}

/**
 * Clear all mock state.
 */
export function clearMockState(): void {
  mockInputs = {};
  mockOutputs = {};
  mockSecrets = [];
  mockInfoMessages = [];
  mockWarningMessages = [];
  mockErrorMessages = [];
  mockFailedMessages = [];
}

// Mock implementations
export const getInput = vi.fn((name: string): string => {
  return mockInputs[name] || '';
});

export const setOutput = vi.fn((name: string, value: string): void => {
  mockOutputs[name] = value;
});

export const setSecret = vi.fn((secret: string): void => {
  mockSecrets.push(secret);
});

export const info = vi.fn((message: string): void => {
  mockInfoMessages.push(message);
});

export const warning = vi.fn((message: string | Error): void => {
  const msg = message instanceof Error ? message.message : message;
  mockWarningMessages.push(msg);
});

export const error = vi.fn((message: string | Error): void => {
  const msg = message instanceof Error ? message.message : message;
  mockErrorMessages.push(msg);
});

export const setFailed = vi.fn((message: string | Error): void => {
  const msg = message instanceof Error ? message.message : message;
  mockFailedMessages.push(msg);
});

export const startGroup = vi.fn((_name: string): void => {});

export const endGroup = vi.fn((): void => {});

export const debug = vi.fn((_message: string): void => {});

export default {
  getInput,
  setOutput,
  setSecret,
  info,
  warning,
  error,
  setFailed,
  startGroup,
  endGroup,
  debug,
};
