/**
 * IMPLEMENTS: S120, S126
 * Error types for VS Code Extension
 */

export class ExtensionError extends Error {
  constructor(message: string, public readonly recoverable: boolean = true) {
    super(message);
    this.name = 'ExtensionError';
  }
}

export class ActivationError extends ExtensionError {
  constructor(reason: string) {
    super(`Extension activation failed: ${reason}`, false);
    this.name = 'ActivationError';
  }
}

export class CoreSpawnError extends ExtensionError {
  constructor(reason: string) {
    super(`Failed to spawn phantom-guard process: ${reason}`, true);
    this.name = 'CoreSpawnError';
  }
}

export class CoreTimeoutError extends ExtensionError {
  constructor(timeoutMs: number) {
    super(`Core process timed out after ${timeoutMs}ms`, true);
    this.name = 'CoreTimeoutError';
  }
}

export class CoreParseError extends ExtensionError {
  constructor(output: string | undefined | null) {
    const safeOutput = output ? String(output).slice(0, 100) : '(empty)';
    super(`Failed to parse core output: ${safeOutput}...`, true);
    this.name = 'CoreParseError';
  }
}

export class PythonNotFoundError extends ExtensionError {
  constructor() {
    super('Python 3.11+ not found. Please install Python or configure path.', false);
    this.name = 'PythonNotFoundError';
  }
}
