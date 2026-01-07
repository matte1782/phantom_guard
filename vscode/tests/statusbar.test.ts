/**
 * SPEC: S124 - Status Bar
 * TEST_IDs: T124.01-T124.02
 * INVARIANTS: INV125
 *
 * Tests for VS Code status bar integration.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock vscode module
vi.mock('vscode', () => import('./__mocks__/vscode'));

describe('Status Bar (S124)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // T124.01: Status bar updates on validation
  // =========================================================================
  it('T124.01: status bar updates after validation', async () => {
    /**
     * SPEC: S124
     * TEST_ID: T124.01
     * INV_ID: INV125
     *
     * Given: Document validated
     * When: Validation completes
     * Then: Status bar shows result summary
     */
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    // Start validation
    const sequence = statusBar.setValidating();
    expect(statusBar.getState()).toBe('validating');

    // Update with results
    statusBar.update(
      { total: 10, safe: 8, suspicious: 2, highRisk: 0, notFound: 0 },
      sequence
    );

    expect(statusBar.getState()).toBe('warning');
    expect(statusBar.getText()).toContain('2');

    statusBar.dispose();
  });

  // =========================================================================
  // T124.02: Shows error count
  // =========================================================================
  it('T124.02: shows error count in status bar', async () => {
    /**
     * SPEC: S124
     * TEST_ID: T124.02
     * INV_ID: INV125
     *
     * Given: 3 suspicious packages detected
     * When: Validation completes
     * Then: Status bar shows "3 issues"
     */
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    const sequence = statusBar.setValidating();
    statusBar.update(
      { total: 10, safe: 7, suspicious: 3, highRisk: 0, notFound: 0 },
      sequence
    );

    expect(statusBar.getText()).toContain('3');
    expect(statusBar.getText()).toContain('issue');

    statusBar.dispose();
  });
});

describe('Status Bar Reflects Most Recent Result (INV125)', () => {
  it('updates after each validation', async () => {
    /**
     * INV125: Status bar reflects most recent validation result
     */
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    // First validation
    const seq1 = statusBar.setValidating();
    statusBar.update({ total: 5, safe: 5, suspicious: 0, highRisk: 0, notFound: 0 }, seq1);
    expect(statusBar.getState()).toBe('success');

    // Second validation
    const seq2 = statusBar.setValidating();
    statusBar.update({ total: 5, safe: 3, suspicious: 2, highRisk: 0, notFound: 0 }, seq2);
    expect(statusBar.getState()).toBe('warning');

    statusBar.dispose();
  });

  it('ignores outdated validation results', async () => {
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    // Start first validation
    const seq1 = statusBar.setValidating();

    // Start second validation (before first completes)
    const seq2 = statusBar.setValidating();

    // First validation completes (outdated)
    statusBar.update({ total: 5, safe: 0, suspicious: 0, highRisk: 5, notFound: 0 }, seq1);

    // Should still be validating (ignored outdated result)
    expect(statusBar.getState()).toBe('validating');

    // Second validation completes
    statusBar.update({ total: 5, safe: 5, suspicious: 0, highRisk: 0, notFound: 0 }, seq2);
    expect(statusBar.getState()).toBe('success');

    statusBar.dispose();
  });

  it('clears when no document open', async () => {
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    const seq = statusBar.setValidating();
    statusBar.update({ total: 5, safe: 3, suspicious: 2, highRisk: 0, notFound: 0 }, seq);

    statusBar.clear();
    expect(statusBar.getState()).toBe('idle');

    statusBar.dispose();
  });

  it.skip('shows "validating..." during validation', () => {});
  it.skip('ordering is guaranteed (no race conditions)', () => {});
});

describe('Status Bar States', () => {
  it('idle state shows ready message', async () => {
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    expect(statusBar.getState()).toBe('idle');
    expect(statusBar.getText()).toContain('Phantom Guard');

    statusBar.dispose();
  });

  it('validating state shows spinner', async () => {
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    statusBar.setValidating();
    expect(statusBar.getState()).toBe('validating');
    expect(statusBar.getText()).toContain('Validating');

    statusBar.dispose();
  });

  it('success state shows safe count', async () => {
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    const seq = statusBar.setValidating();
    statusBar.update({ total: 5, safe: 5, suspicious: 0, highRisk: 0, notFound: 0 }, seq);

    expect(statusBar.getState()).toBe('success');
    expect(statusBar.getText()).toContain('5 safe');

    statusBar.dispose();
  });

  it('warning state for suspicious packages', async () => {
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    const seq = statusBar.setValidating();
    statusBar.update({ total: 5, safe: 3, suspicious: 2, highRisk: 0, notFound: 0 }, seq);

    expect(statusBar.getState()).toBe('warning');

    statusBar.dispose();
  });

  it('error state for high risk packages', async () => {
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    const seq = statusBar.setValidating();
    statusBar.update({ total: 5, safe: 3, suspicious: 1, highRisk: 1, notFound: 0 }, seq);

    expect(statusBar.getState()).toBe('error');

    statusBar.dispose();
  });

  it.skip('idle state (no validation done)', () => {});
  it.skip('validating state (in progress)', () => {});
  it.skip('success state (all safe)', () => {});
  it.skip('warning state (suspicious found)', () => {});
  it.skip('error state (high risk found)', () => {});
});

describe('Status Bar Click Behavior', () => {
  it.skip('click opens problems panel', () => {});
});

describe('Status Bar Disposal', () => {
  it('dispose cleans up resources', async () => {
    const { PhantomGuardStatusBar } = await import('../src/statusbar');

    const statusBar = new PhantomGuardStatusBar();

    // Should not throw
    statusBar.dispose();
    expect(true).toBe(true);
  });
});
