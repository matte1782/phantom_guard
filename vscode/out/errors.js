"use strict";
/**
 * IMPLEMENTS: S120, S126
 * Error types for VS Code Extension
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.PythonNotFoundError = exports.CoreParseError = exports.CoreTimeoutError = exports.CoreSpawnError = exports.ActivationError = exports.ExtensionError = void 0;
class ExtensionError extends Error {
    recoverable;
    constructor(message, recoverable = true) {
        super(message);
        this.recoverable = recoverable;
        this.name = 'ExtensionError';
    }
}
exports.ExtensionError = ExtensionError;
class ActivationError extends ExtensionError {
    constructor(reason) {
        super(`Extension activation failed: ${reason}`, false);
        this.name = 'ActivationError';
    }
}
exports.ActivationError = ActivationError;
class CoreSpawnError extends ExtensionError {
    constructor(reason) {
        super(`Failed to spawn phantom-guard process: ${reason}`, true);
        this.name = 'CoreSpawnError';
    }
}
exports.CoreSpawnError = CoreSpawnError;
class CoreTimeoutError extends ExtensionError {
    constructor(timeoutMs) {
        super(`Core process timed out after ${timeoutMs}ms`, true);
        this.name = 'CoreTimeoutError';
    }
}
exports.CoreTimeoutError = CoreTimeoutError;
class CoreParseError extends ExtensionError {
    constructor(output) {
        const safeOutput = output ? String(output).slice(0, 100) : '(empty)';
        super(`Failed to parse core output: ${safeOutput}...`, true);
        this.name = 'CoreParseError';
    }
}
exports.CoreParseError = CoreParseError;
class PythonNotFoundError extends ExtensionError {
    constructor() {
        super('Python 3.11+ not found. Please install Python or configure path.', false);
        this.name = 'PythonNotFoundError';
    }
}
exports.PythonNotFoundError = PythonNotFoundError;
//# sourceMappingURL=errors.js.map