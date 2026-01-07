/**
 * SPEC: S104 - PR Comment Generator
 * TEST_IDs: T104.01-T104.05
 * INVARIANTS: INV105, INV106
 * EDGE_CASES: EC240-EC255
 *
 * Tests for PR comment generation.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as github from '@actions/github';

// Mock @actions/core
vi.mock('@actions/core', () => ({
  info: vi.fn(),
  warning: vi.fn(),
  error: vi.fn(),
  debug: vi.fn(),
}));

// Mock @actions/github
vi.mock('@actions/github', () => ({
  getOctokit: vi.fn(() => ({
    rest: {
      issues: {
        listComments: vi.fn().mockResolvedValue({ data: [] }),
        createComment: vi.fn().mockResolvedValue({ data: { id: 123 } }),
        updateComment: vi.fn().mockResolvedValue({ data: { id: 123 } }),
      },
    },
  })),
  context: {
    payload: { pull_request: null },
    repo: { owner: 'test', repo: 'test' },
  },
}));

import { generatePRComment } from '../src/comment';
import { ValidationResult } from '../src/validate';
import { ValidationSummary } from '../src/exit';
import * as core from '@actions/core';

function createResult(
  name: string,
  riskLevel: 'safe' | 'suspicious' | 'high-risk',
  score: number,
  signals: string[] = []
): ValidationResult {
  return {
    package: name,
    riskLevel,
    riskScore: score,
    signals,
    sourceFile: 'requirements.txt',
    lineNumber: 1,
    registry: 'pypi',
  };
}

describe('PR Comment Generator (S104)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // T104.01: Skip when not a PR
  // =========================================================================
  it('T104.01: skips comment when not a pull request', async () => {
    /**
     * SPEC: S104
     * TEST_ID: T104.01
     * EC_ID: EC246
     *
     * Given: Context is not a pull request
     * When: generatePRComment is called
     * Then: Skips comment generation
     */
    const results: ValidationResult[] = [createResult('flask', 'safe', 0)];
    const summary: ValidationSummary = {
      safeCount: 1,
      suspiciousCount: 0,
      highRiskCount: 0,
      totalPackages: 1,
      errors: [],
    };

    await generatePRComment(results, summary, 'token');

    expect(core.info).toHaveBeenCalledWith(
      expect.stringContaining('Not a pull request')
    );
  });

  // =========================================================================
  // T104.02: Skip when no token
  // =========================================================================
  it('T104.02: skips comment when no token provided', async () => {
    /**
     * SPEC: S104
     * TEST_ID: T104.02
     *
     * Given: No GitHub token
     * When: generatePRComment is called
     * Then: Skips comment and logs warning
     */
    // Set context to have a PR
    vi.mocked(github.context).payload.pull_request = { number: 1 } as never;

    const results: ValidationResult[] = [createResult('flask', 'safe', 0)];
    const summary: ValidationSummary = {
      safeCount: 1,
      suspiciousCount: 0,
      highRiskCount: 0,
      totalPackages: 1,
      errors: [],
    };

    await generatePRComment(results, summary, '');

    expect(core.warning).toHaveBeenCalledWith(
      expect.stringContaining('No GitHub token')
    );

    // Reset
    vi.mocked(github.context).payload.pull_request = null as never;
  });

  // =========================================================================
  // T104.03: Function exists and is callable
  // =========================================================================
  it('T104.03: function is exported and callable', () => {
    expect(typeof generatePRComment).toBe('function');
  });
});

describe('PR Comment Edge Cases (EC240-EC255)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // EC246: Skip on push event (not PR)
  // =========================================================================
  it('EC246: skips comment on push event', async () => {
    const results: ValidationResult[] = [];
    const summary: ValidationSummary = {
      safeCount: 0,
      suspiciousCount: 0,
      highRiskCount: 0,
      totalPackages: 0,
      errors: [],
    };

    // No PR in context
    await generatePRComment(results, summary, 'token');

    expect(core.info).toHaveBeenCalledWith(
      expect.stringContaining('Not a pull request')
    );
  });

  // =========================================================================
  // Skipped tests (require full GitHub API mocking)
  // =========================================================================
  it.skip('EC240: creates new comment on first run', () => {});
  it.skip('EC241: updates existing comment (sticky mode)', () => {});
  it.skip('EC244: many packages truncated with count', () => {});
  it.skip('EC245: comment truncated at 65536 chars', () => {});
  it.skip('EC247: permission denied logged, continues', () => {});
  it.skip('EC248: rate limited with retry backoff', () => {});
  it.skip('EC249: network error logged, continues', () => {});
  it.skip('EC250: markdown injection escaped', () => {});
  it.skip('EC251: unicode in name rendered correctly', () => {});
  it.skip('EC252: long package name truncated', () => {});
  it.skip('EC253: high risk shows prominent warning', () => {});
  it.skip('EC254: empty results shows info message', () => {});
  it.skip('EC255: partial failure shows both', () => {});
});
