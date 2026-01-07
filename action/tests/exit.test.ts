/**
 * SPEC: S106 - Exit Codes
 * TEST_IDs: T106.01-T106.04
 * INVARIANTS: INV108
 *
 * Tests for GitHub Action exit code handling.
 */

import { describe, it, expect } from 'vitest';
import {
  ExitCode,
  determineExitCode,
  getExitCodeDescription,
  isValidFailOnThreshold,
  parseFailOnThreshold,
  type ValidationSummary,
} from '../src/exit';

describe('Exit Codes (S106)', () => {
  // =========================================================================
  // T106.01: Exit 0 for all safe packages
  // =========================================================================
  describe('T106.01: exit 0 for all safe', () => {
    it('returns SAFE when all packages are safe', () => {
      const summary: ValidationSummary = {
        safeCount: 10,
        suspiciousCount: 0,
        highRiskCount: 0,
        totalPackages: 10,
        errors: [],
      };

      const result = determineExitCode(summary, 'high-risk');
      expect(result).toBe(ExitCode.SAFE);
    });

    it('returns SAFE with none threshold even with issues', () => {
      const summary: ValidationSummary = {
        safeCount: 5,
        suspiciousCount: 3,
        highRiskCount: 2,
        totalPackages: 10,
        errors: [],
      };

      const result = determineExitCode(summary, 'none');
      expect(result).toBe(ExitCode.SAFE);
    });
  });

  // =========================================================================
  // T106.02: Exit 1 for suspicious packages
  // =========================================================================
  describe('T106.02: exit 1 for suspicious', () => {
    it('returns SUSPICIOUS when fail-on is suspicious and suspicious packages exist', () => {
      const summary: ValidationSummary = {
        safeCount: 7,
        suspiciousCount: 3,
        highRiskCount: 0,
        totalPackages: 10,
        errors: [],
      };

      const result = determineExitCode(summary, 'suspicious');
      expect(result).toBe(ExitCode.SUSPICIOUS);
    });

    it('returns SAFE with high-risk threshold when only suspicious', () => {
      const summary: ValidationSummary = {
        safeCount: 7,
        suspiciousCount: 3,
        highRiskCount: 0,
        totalPackages: 10,
        errors: [],
      };

      const result = determineExitCode(summary, 'high-risk');
      expect(result).toBe(ExitCode.SAFE);
    });
  });

  // =========================================================================
  // T106.03: Exit 2 for high-risk packages
  // =========================================================================
  describe('T106.03: exit 2 for high-risk', () => {
    it('returns HIGH_RISK when high-risk packages exist', () => {
      const summary: ValidationSummary = {
        safeCount: 5,
        suspiciousCount: 3,
        highRiskCount: 2,
        totalPackages: 10,
        errors: [],
      };

      const result = determineExitCode(summary, 'high-risk');
      expect(result).toBe(ExitCode.HIGH_RISK);
    });

    it('returns HIGH_RISK regardless of threshold', () => {
      const summary: ValidationSummary = {
        safeCount: 5,
        suspiciousCount: 0,
        highRiskCount: 1,
        totalPackages: 6,
        errors: [],
      };

      // Even with suspicious threshold, high-risk should fail
      expect(determineExitCode(summary, 'suspicious')).toBe(ExitCode.HIGH_RISK);
    });
  });

  // =========================================================================
  // T106.04: Exit codes always in range [0, 5]
  // =========================================================================
  describe('T106.04: exit codes in range', () => {
    it('all exit codes are in range [0, 5]', () => {
      const codes = [
        ExitCode.SAFE,
        ExitCode.SUSPICIOUS,
        ExitCode.HIGH_RISK,
        ExitCode.ERROR,
        ExitCode.NO_PACKAGES,
        ExitCode.CONFIG_ERROR,
      ];

      for (const code of codes) {
        expect(code).toBeGreaterThanOrEqual(0);
        expect(code).toBeLessThanOrEqual(5);
      }
    });

    it('returns ERROR when errors exist', () => {
      const summary: ValidationSummary = {
        safeCount: 10,
        suspiciousCount: 0,
        highRiskCount: 0,
        totalPackages: 10,
        errors: ['Something went wrong'],
      };

      const result = determineExitCode(summary, 'high-risk');
      expect(result).toBe(ExitCode.ERROR);
    });

    it('returns NO_PACKAGES when total is 0', () => {
      const summary: ValidationSummary = {
        safeCount: 0,
        suspiciousCount: 0,
        highRiskCount: 0,
        totalPackages: 0,
        errors: [],
      };

      const result = determineExitCode(summary, 'high-risk');
      expect(result).toBe(ExitCode.NO_PACKAGES);
    });
  });

  // =========================================================================
  // Additional tests
  // =========================================================================
  describe('getExitCodeDescription', () => {
    it('returns correct description for each code', () => {
      expect(getExitCodeDescription(ExitCode.SAFE)).toContain('safe');
      expect(getExitCodeDescription(ExitCode.SUSPICIOUS)).toContain('Suspicious');
      expect(getExitCodeDescription(ExitCode.HIGH_RISK)).toContain('High-risk');
      expect(getExitCodeDescription(ExitCode.ERROR)).toContain('error');
      expect(getExitCodeDescription(ExitCode.NO_PACKAGES)).toContain('No packages');
      expect(getExitCodeDescription(ExitCode.CONFIG_ERROR)).toContain('Configuration');
    });
  });

  describe('isValidFailOnThreshold', () => {
    it('validates correct thresholds', () => {
      expect(isValidFailOnThreshold('none')).toBe(true);
      expect(isValidFailOnThreshold('suspicious')).toBe(true);
      expect(isValidFailOnThreshold('high-risk')).toBe(true);
    });

    it('rejects invalid thresholds', () => {
      expect(isValidFailOnThreshold('invalid')).toBe(false);
      expect(isValidFailOnThreshold('')).toBe(false);
      expect(isValidFailOnThreshold('HIGH-RISK')).toBe(false);
    });
  });

  describe('parseFailOnThreshold', () => {
    it('parses valid thresholds', () => {
      expect(parseFailOnThreshold('high-risk')).toBe('high-risk');
      expect(parseFailOnThreshold('  suspicious  ')).toBe('suspicious');
      expect(parseFailOnThreshold('NONE')).toBe('none');
    });

    it('throws on invalid thresholds', () => {
      expect(() => parseFailOnThreshold('invalid')).toThrow();
      expect(() => parseFailOnThreshold('')).toThrow();
    });
  });
});
