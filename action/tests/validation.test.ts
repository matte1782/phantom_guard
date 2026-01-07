/**
 * SPEC: S102 - Package Extraction
 * TEST_IDs: T102.SEC
 * INVARIANTS: INV103
 * SECURITY: P1-SEC-002
 *
 * Tests for package name validation and sanitization.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock @actions/core
vi.mock('@actions/core', () => ({
  info: vi.fn(),
  warning: vi.fn(),
  error: vi.fn(),
  debug: vi.fn(),
}));

import {
  isValidPackageName,
  sanitizePackageName,
  stripBOM,
  normalizeLineEndings,
  preprocessContent,
} from '../src/validation';
import * as core from '@actions/core';

describe('Package Name Validation (P1-SEC-002)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // T102.SEC: Shell metacharacters rejected
  // =========================================================================
  describe('T102.SEC: Shell metacharacter rejection', () => {
    it('rejects semicolon (command injection)', () => {
      expect(isValidPackageName('pkg;rm -rf')).toBe(false);
    });

    it('rejects pipe (command chaining)', () => {
      expect(isValidPackageName('pkg|cat /etc/passwd')).toBe(false);
    });

    it('rejects ampersand (background execution)', () => {
      expect(isValidPackageName('pkg&malicious')).toBe(false);
    });

    it('rejects dollar sign (variable expansion)', () => {
      expect(isValidPackageName('$HOME')).toBe(false);
      expect(isValidPackageName('pkg$(whoami)')).toBe(false);
    });

    it('rejects backticks (command substitution)', () => {
      expect(isValidPackageName('pkg`whoami`')).toBe(false);
    });

    it('rejects quotes (string manipulation)', () => {
      expect(isValidPackageName('pkg"name')).toBe(false);
      expect(isValidPackageName("pkg'name")).toBe(false);
    });

    it('rejects redirection operators', () => {
      expect(isValidPackageName('pkg>output')).toBe(false);
      expect(isValidPackageName('pkg<input')).toBe(false);
    });

    it('rejects parentheses and braces', () => {
      expect(isValidPackageName('pkg()')).toBe(false);
      expect(isValidPackageName('pkg{}')).toBe(false);
      expect(isValidPackageName('pkg[]')).toBe(false);
    });

    it('rejects special characters', () => {
      expect(isValidPackageName('pkg!')).toBe(false);
      expect(isValidPackageName('pkg*')).toBe(false);
      expect(isValidPackageName('pkg?')).toBe(false);
      expect(isValidPackageName('pkg~')).toBe(false);
    });

    it('rejects newlines and tabs', () => {
      expect(isValidPackageName('pkg\nmalicious')).toBe(false);
      expect(isValidPackageName('pkg\rmalicious')).toBe(false);
      expect(isValidPackageName('pkg\tmalicious')).toBe(false);
    });
  });

  // =========================================================================
  // Valid package names
  // =========================================================================
  describe('Valid package names', () => {
    it('accepts simple lowercase names', () => {
      expect(isValidPackageName('flask')).toBe(true);
      expect(isValidPackageName('requests')).toBe(true);
      expect(isValidPackageName('numpy')).toBe(true);
    });

    it('accepts names with hyphens', () => {
      expect(isValidPackageName('my-package')).toBe(true);
      expect(isValidPackageName('scikit-learn')).toBe(true);
    });

    it('accepts names with underscores', () => {
      expect(isValidPackageName('my_package')).toBe(true);
      expect(isValidPackageName('typing_extensions')).toBe(true);
    });

    it('accepts names with dots', () => {
      expect(isValidPackageName('zope.interface')).toBe(true);
    });

    it('accepts names with numbers', () => {
      expect(isValidPackageName('package123')).toBe(true);
      expect(isValidPackageName('py2neo')).toBe(true);
    });

    it('accepts npm scoped packages', () => {
      expect(isValidPackageName('@types/node')).toBe(true);
      expect(isValidPackageName('@angular/core')).toBe(true);
      expect(isValidPackageName('@babel/core')).toBe(true);
    });

    it('accepts mixed case (will be normalized)', () => {
      expect(isValidPackageName('Flask')).toBe(true);
      expect(isValidPackageName('NumPy')).toBe(true);
    });
  });

  // =========================================================================
  // Invalid package names (non-security)
  // =========================================================================
  describe('Invalid package names (format)', () => {
    it('rejects empty strings', () => {
      expect(isValidPackageName('')).toBe(false);
      expect(isValidPackageName('   ')).toBe(false);
    });

    it('rejects null and undefined', () => {
      expect(isValidPackageName(null as unknown as string)).toBe(false);
      expect(isValidPackageName(undefined as unknown as string)).toBe(false);
    });

    it('rejects names exceeding 214 characters', () => {
      const longName = 'a'.repeat(215);
      expect(isValidPackageName(longName)).toBe(false);
    });

    it('rejects names starting with special characters', () => {
      expect(isValidPackageName('-package')).toBe(false);
      expect(isValidPackageName('.package')).toBe(false);
      expect(isValidPackageName('_package')).toBe(false);
    });

    it('rejects malformed scoped packages', () => {
      expect(isValidPackageName('@/package')).toBe(false);
      expect(isValidPackageName('@scope/')).toBe(false);
      expect(isValidPackageName('@scope')).toBe(false);
    });
  });
});

describe('sanitizePackageName', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns lowercase name for valid input', () => {
    expect(sanitizePackageName('Flask', 'test.txt', 1)).toBe('flask');
    expect(sanitizePackageName('NumPy', 'test.txt', 1)).toBe('numpy');
  });

  it('returns null for invalid input', () => {
    expect(sanitizePackageName('pkg;rm', 'test.txt', 1)).toBe(null);
    expect(sanitizePackageName('', 'test.txt', 1)).toBe(null);
  });

  it('logs warning for invalid package names', () => {
    sanitizePackageName('pkg;rm', 'test.txt', 5);
    expect(core.warning).toHaveBeenCalledWith(
      expect.stringContaining('Invalid package name at test.txt:5')
    );
  });

  it('truncates long names in warning message', () => {
    // Create an invalid name that's longer than 50 chars (contains semicolon = invalid)
    const longInvalidName = 'a'.repeat(60) + ';rm';
    sanitizePackageName(longInvalidName, 'test.txt', 1);
    expect(core.warning).toHaveBeenCalledWith(
      expect.stringContaining('...')
    );
  });
});

describe('Content preprocessing', () => {
  // =========================================================================
  // EC212: UTF-8 BOM stripped
  // =========================================================================
  describe('EC212: UTF-8 BOM handling', () => {
    it('strips UTF-8 BOM from start of content', () => {
      const withBOM = '\uFEFFflask==1.0.0';
      expect(stripBOM(withBOM)).toBe('flask==1.0.0');
    });

    it('leaves content without BOM unchanged', () => {
      const noBOM = 'flask==1.0.0';
      expect(stripBOM(noBOM)).toBe('flask==1.0.0');
    });
  });

  // =========================================================================
  // EC213: CRLF line endings parsed correctly
  // =========================================================================
  describe('EC213: Line ending normalization', () => {
    it('converts CRLF to LF', () => {
      const crlf = 'line1\r\nline2\r\nline3';
      expect(normalizeLineEndings(crlf)).toBe('line1\nline2\nline3');
    });

    it('converts standalone CR to LF', () => {
      const cr = 'line1\rline2\rline3';
      expect(normalizeLineEndings(cr)).toBe('line1\nline2\nline3');
    });

    it('leaves LF unchanged', () => {
      const lf = 'line1\nline2\nline3';
      expect(normalizeLineEndings(lf)).toBe('line1\nline2\nline3');
    });
  });

  describe('preprocessContent', () => {
    it('handles both BOM and CRLF', () => {
      const content = '\uFEFFline1\r\nline2\r\nline3';
      expect(preprocessContent(content)).toBe('line1\nline2\nline3');
    });
  });
});
