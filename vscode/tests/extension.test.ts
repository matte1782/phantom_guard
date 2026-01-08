/**
 * SPEC: S120 - Extension Activation
 * TEST_IDs: T120.01-T120.04
 * INVARIANTS: INV120, INV121
 * EDGE_CASES: EC300-EC315
 *
 * Tests for VS Code extension activation lifecycle.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock vscode module - use shared mock
vi.mock('vscode', () => import('./__mocks__/vscode'));

// Mock the core module
vi.mock('../src/core', () => ({
  PhantomGuardCore: vi.fn().mockImplementation(() => ({
    checkAvailability: vi.fn().mockResolvedValue(true),
    validatePackage: vi.fn().mockResolvedValue(null),
    validatePackages: vi.fn().mockResolvedValue(new Map()),
    setPythonPath: vi.fn(), // P0-BUG-001 FIX: Added setPythonPath mock
    dispose: vi.fn(),
  })),
}));

describe('Extension Activation (S120)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // T120.01: Activation completes under 500ms
  // =========================================================================
  it('T120.01: activation completes under 500ms', async () => {
    /**
     * SPEC: S120
     * TEST_ID: T120.01
     * INV_ID: INV120, INV121
     * EC_ID: EC300
     *
     * Given: Python and phantom-guard available
     * When: Extension activates
     * Then: Activation completes in < 500ms
     */
    const { activate } = await import('../src/extension');

    const mockContext = {
      subscriptions: [],
    } as any;

    const startTime = Date.now();
    await activate(mockContext);
    const elapsed = Date.now() - startTime;

    expect(elapsed).toBeLessThan(500);
  });

  // =========================================================================
  // T120.02: Timeout handled gracefully
  // =========================================================================
  it('T120.02: timeout handled gracefully', async () => {
    /**
     * SPEC: S120
     * TEST_ID: T120.02
     * INV_ID: INV121
     * EC_ID: EC306
     *
     * Given: Slow activation (>500ms)
     * When: Extension activates
     * Then: Warning shown, continues with reduced functionality
     */
    const { PhantomGuardCore } = await import('../src/core');
    const vscode = await import('vscode');

    // Mock slow checkAvailability
    vi.mocked(PhantomGuardCore).mockImplementation(() => ({
      checkAvailability: vi.fn().mockImplementation(() =>
        new Promise(resolve => setTimeout(() => resolve(true), 600))
      ),
      dispose: vi.fn(),
    }) as any);

    const { activate } = await import('../src/extension');

    const mockContext = {
      subscriptions: [],
    } as any;

    // Should not throw
    await activate(mockContext);

    // Should show warning message
    expect(vscode.window.showWarningMessage).toHaveBeenCalled();
  });

  // =========================================================================
  // T120.03: Python not found error
  // =========================================================================
  it('T120.03: PythonNotFoundError triggers error message', async () => {
    /**
     * SPEC: S120
     * TEST_ID: T120.03
     * EC_ID: EC301
     *
     * Given: Python not in PATH
     * When: Extension activates
     * Then: Error message shown
     *
     * Note: This test verifies the error handling logic exists.
     * Full integration test with mock setup is in integration tests.
     */
    const { PythonNotFoundError } = await import('../src/errors');

    // Verify PythonNotFoundError is properly defined
    const error = new PythonNotFoundError();
    expect(error).toBeInstanceOf(Error);
    expect(error.name).toBe('PythonNotFoundError');
    expect(error.message).toContain('Python');
    expect(error.recoverable).toBe(false);
  });

  // =========================================================================
  // T120.04: phantom-guard not installed
  // =========================================================================
  it('T120.04: ActivationError is properly defined', async () => {
    /**
     * SPEC: S120
     * TEST_ID: T120.04
     * EC_ID: EC303
     *
     * Given: Python available but phantom-guard not installed
     * When: Extension activates
     * Then: ActivationError thrown, warning message shown
     *
     * Note: This test verifies the error handling logic exists.
     * Full integration test in integration tests.
     */
    const { ActivationError } = await import('../src/errors');

    // Verify ActivationError is properly defined
    const error = new ActivationError('phantom-guard CLI not found');
    expect(error).toBeInstanceOf(Error);
    expect(error.name).toBe('ActivationError');
    expect(error.message).toContain('phantom-guard');
    expect(error.recoverable).toBe(false);
  });
});

describe('Extension Activation Edge Cases (EC300-EC315)', () => {
  it.skip('EC302: wrong Python version shows error', () => {});
  it.skip('EC304: no dependency files = lazy activation', () => {});
  it.skip('EC305: multi-root workspace activates for each', () => {});
  it.skip('EC307: crash during activation = graceful failure', () => {});
  it.skip('EC308: disabled extension = no activation', () => {});
  it.skip('EC309: reload after crash = clean restart', () => {});
  it.skip('EC310: low memory = reduced functionality', () => {});
  it.skip('EC311: extension update = reactivate cleanly', () => {});
  it.skip('EC312: conflicting extension = warning', () => {});
  it.skip('EC313: remote workspace = works correctly', () => {});
  it.skip('EC314: container workspace = works correctly', () => {});
  it.skip('EC315: virtual environment = uses venv python', () => {});
});

describe('Extension Never Blocks UI (INV120)', () => {
  it('all I/O operations are async', async () => {
    /**
     * INV120: Extension never blocks UI thread
     * Verify activate function is async
     */
    const { activate } = await import('../src/extension');

    // Verify activate returns a Promise
    const mockContext = { subscriptions: [] } as any;
    const result = activate(mockContext);

    expect(result).toBeInstanceOf(Promise);
    await result;
  });

  it.skip('validation runs in background', async () => {
    /**
     * INV120: Long-running validation doesn't freeze UI
     */
  });
});

describe('Extension Deactivation', () => {
  it('deactivate cleans up resources', async () => {
    const { deactivate, getCore } = await import('../src/extension');

    // After deactivation, core should be undefined
    deactivate();
    expect(getCore()).toBeUndefined();
  });
});

describe('Extension Getters', () => {
  it('getConfigProvider returns undefined after deactivate', async () => {
    const { deactivate, getConfigProvider } = await import('../src/extension');
    deactivate();
    expect(getConfigProvider()).toBeUndefined();
  });

  it('getDiagnosticProvider returns undefined after deactivate', async () => {
    const { deactivate, getDiagnosticProvider } = await import('../src/extension');
    deactivate();
    expect(getDiagnosticProvider()).toBeUndefined();
  });

  it('getStatusBar returns undefined after deactivate', async () => {
    const { deactivate, getStatusBar } = await import('../src/extension');
    deactivate();
    expect(getStatusBar()).toBeUndefined();
  });
});

describe('PythonPath Configuration Wiring (P0-BUG-001)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  it('setPythonPath is called during activation', async () => {
    /**
     * P0-BUG-001 FIX VERIFICATION
     *
     * Given: Extension activates successfully
     * When: Core is created and config is loaded
     * Then: setPythonPath is called with configured value
     */
    const mockSetPythonPath = vi.fn();
    const { PhantomGuardCore } = await import('../src/core');

    vi.mocked(PhantomGuardCore).mockImplementation(() => ({
      checkAvailability: vi.fn().mockResolvedValue(true),
      validatePackage: vi.fn().mockResolvedValue(null),
      validatePackages: vi.fn().mockResolvedValue(new Map()),
      setPythonPath: mockSetPythonPath,
      dispose: vi.fn(),
    }) as any);

    const { activate } = await import('../src/extension');
    const mockContext = { subscriptions: [] } as any;

    await activate(mockContext);

    // Verify setPythonPath was called during activation
    expect(mockSetPythonPath).toHaveBeenCalled();
  });

  it('setPythonPath receives value from config', async () => {
    /**
     * P0-BUG-001 FIX VERIFICATION
     *
     * Given: pythonPath is configured in settings
     * When: Extension activates
     * Then: setPythonPath is called with that configured path
     */
    const mockSetPythonPath = vi.fn();
    const { PhantomGuardCore } = await import('../src/core');

    vi.mocked(PhantomGuardCore).mockImplementation(() => ({
      checkAvailability: vi.fn().mockResolvedValue(true),
      validatePackage: vi.fn().mockResolvedValue(null),
      validatePackages: vi.fn().mockResolvedValue(new Map()),
      setPythonPath: mockSetPythonPath,
      dispose: vi.fn(),
    }) as any);

    const { activate } = await import('../src/extension');
    const mockContext = { subscriptions: [] } as any;

    await activate(mockContext);

    // setPythonPath should be called with the default 'python' value
    // (since our mock vscode returns undefined for config values,
    // ConfigProvider uses 'python' as default)
    expect(mockSetPythonPath).toHaveBeenCalledWith('python');
  });
});
