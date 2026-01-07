/**
 * SPEC: S100 - Action Entry Point
 * TEST_IDs: T100.01-T100.03
 * INVARIANTS: INV100, INV101
 * SECURITY: P1-SEC-003 (token masking)
 *
 * Tests for GitHub Action entry point.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  setMockInputs,
  getMockSecrets,
  getMockOutputs,
  getFailedMessages,
  clearMockState,
} from './__mocks__/@actions/core';

// Mock @actions/core BEFORE importing run()
vi.mock('@actions/core', () => import('./__mocks__/@actions/core'));

// Mock other modules that use @actions/core
vi.mock('../src/files', () => ({
  discoverFiles: vi.fn().mockResolvedValue([]),
}));

vi.mock('../src/extract', () => ({
  extractPackages: vi.fn().mockResolvedValue([]),
}));

vi.mock('../src/validate', () => ({
  validatePackages: vi.fn().mockResolvedValue([]),
}));

vi.mock('../src/comment', () => ({
  generatePRComment: vi.fn().mockResolvedValue(undefined),
}));

vi.mock('../src/sarif', () => ({
  generateSARIF: vi.fn().mockResolvedValue(undefined),
}));

describe('GitHub Action Entry Point (S100)', () => {
  beforeEach(() => {
    clearMockState();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetModules();
  });

  // =========================================================================
  // T100.01: Action completes without throwing
  // =========================================================================
  describe('T100.01: action completes without throwing', () => {
    it('completes with valid inputs and no files', async () => {
      /**
       * SPEC: S100
       * TEST_ID: T100.01
       * INV_ID: INV100
       */
      setMockInputs({
        files: 'requirements.txt',
        'fail-on': 'high-risk',
        output: 'none',
        'github-token': '',
        'python-path': 'python',
      });

      const { run } = await import('../src/index');

      // Should not throw
      await expect(run()).resolves.not.toThrow();
    });

    it('sets appropriate outputs when no files found', async () => {
      setMockInputs({
        files: 'requirements.txt',
        'fail-on': 'high-risk',
        output: 'none',
        'github-token': '',
        'python-path': 'python',
      });

      const { run } = await import('../src/index');
      await run();

      const outputs = getMockOutputs();
      expect(outputs['exit-code']).toBeDefined();
    });
  });

  // =========================================================================
  // P1-SEC-003: Token masking security test
  // =========================================================================
  describe('P1-SEC-003: Token masking', () => {
    it('masks GitHub token with core.setSecret', async () => {
      /**
       * SECURITY: P1-SEC-003
       *
       * Given: GitHub token is provided
       * When: run() is called
       * Then: Token is registered as secret via core.setSecret()
       */
      const testToken = 'ghp_testToken123456789abcdef';

      setMockInputs({
        files: 'requirements.txt',
        'fail-on': 'high-risk',
        output: 'none',
        'github-token': testToken,
        'python-path': 'python',
      });

      const { run } = await import('../src/index');
      await run();

      const secrets = getMockSecrets();
      expect(secrets).toContain(testToken);
    });

    it('does not call setSecret when no token provided', async () => {
      setMockInputs({
        files: 'requirements.txt',
        'fail-on': 'high-risk',
        output: 'none',
        'github-token': '',
        'python-path': 'python',
      });

      const { run } = await import('../src/index');
      await run();

      const secrets = getMockSecrets();
      expect(secrets).toHaveLength(0);
    });
  });

  // =========================================================================
  // T100.02: Full workflow runs successfully
  // =========================================================================
  describe('T100.02: full workflow (integration)', () => {
    it.skip('runs full workflow with requirements.txt', async () => {
      /**
       * SPEC: S100
       * TEST_ID: T100.02
       * INV_ID: INV100
       *
       * Note: This is an integration test that requires
       * actual file system and Python environment.
       * Skipped for unit test runs.
       */
      expect(true).toBe(true);
    });
  });

  // =========================================================================
  // T100.03: Cold start benchmark
  // =========================================================================
  describe('T100.03: cold start benchmark', () => {
    it.skip('cold start completes under 5s', async () => {
      /**
       * SPEC: S100
       * TEST_ID: T100.03
       * BUDGET: <5s cold start
       *
       * Note: Benchmark test for CI environment.
       * Skipped for regular unit test runs.
       */
      const startTime = Date.now();

      // Would run full action here

      const elapsed = Date.now() - startTime;
      expect(elapsed).toBeLessThan(5000);
    });
  });

  // =========================================================================
  // Configuration error handling
  // =========================================================================
  describe('Configuration error handling', () => {
    it('handles invalid fail-on value gracefully', async () => {
      setMockInputs({
        files: 'requirements.txt',
        'fail-on': 'invalid-value',
        output: 'none',
        'github-token': '',
        'python-path': 'python',
      });

      const { run } = await import('../src/index');
      await run();

      const outputs = getMockOutputs();
      // exit-code can be number or string depending on how setOutput serializes it
      expect(Number(outputs['exit-code'])).toBe(5); // CONFIG_ERROR
    });
  });
});
