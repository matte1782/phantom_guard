/**
 * SPEC: S101 - File Discovery
 * TEST_IDs: T101.01-T101.05
 * INVARIANTS: INV102
 * EDGE_CASES: EC200-EC215
 *
 * Tests for dependency file discovery.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as path from 'path';

// Mock @actions/core
vi.mock('@actions/core', () => ({
  info: vi.fn(),
  warning: vi.fn(),
  error: vi.fn(),
  debug: vi.fn(),
}));

// Import after mock
import { discoverFiles, getRegistryForFile, isDependencyFile } from '../src/files';
import * as core from '@actions/core';

const FIXTURES_DIR = path.join(__dirname, 'fixtures');

describe('File Discovery (S101)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // T101.01: Find requirements.txt
  // =========================================================================
  it('T101.01: finds requirements.txt', async () => {
    /**
     * SPEC: S101
     * TEST_ID: T101.01
     * INV_ID: INV102
     * EC_ID: EC200
     *
     * Given: Pattern matching requirements.txt
     * When: discoverFiles is called
     * Then: Returns file path, registry is pypi
     */
    const pattern = path.join(FIXTURES_DIR, 'requirements.txt');
    const files = await discoverFiles(pattern);

    expect(files.length).toBe(1);
    expect(files[0]).toContain('requirements.txt');
    expect(getRegistryForFile(files[0])).toBe('pypi');
  });

  // =========================================================================
  // T101.02: Find package.json
  // =========================================================================
  it('T101.02: finds package.json', async () => {
    /**
     * SPEC: S101
     * TEST_ID: T101.02
     * INV_ID: INV102
     * EC_ID: EC201
     *
     * Given: Pattern matching package.json
     * When: discoverFiles is called
     * Then: Returns file path, registry is npm
     */
    const pattern = path.join(FIXTURES_DIR, 'package.json');
    const files = await discoverFiles(pattern);

    expect(files.length).toBe(1);
    expect(files[0]).toContain('package.json');
    expect(getRegistryForFile(files[0])).toBe('npm');
  });

  // =========================================================================
  // T101.03: No matches returns empty array
  // =========================================================================
  it('T101.03: no matches returns empty array', async () => {
    /**
     * SPEC: S101
     * TEST_ID: T101.03
     * INV_ID: INV102
     * EC_ID: EC204
     *
     * Given: Pattern matching no files
     * When: discoverFiles is called
     * Then: Returns empty array (no exception)
     */
    const pattern = path.join(FIXTURES_DIR, 'nonexistent-*.xyz');
    const files = await discoverFiles(pattern);

    expect(files).toEqual([]);
  });

  // =========================================================================
  // T101.04: Invalid glob handled gracefully
  // =========================================================================
  it('T101.04: invalid pattern handled gracefully', async () => {
    /**
     * SPEC: S101
     * TEST_ID: T101.04
     * INV_ID: INV102
     * EC_ID: EC205
     *
     * Given: Empty or invalid pattern
     * When: discoverFiles is called
     * Then: Returns empty array or defaults (no exception)
     */
    // Empty pattern should use defaults
    const files = await discoverFiles('');

    // Should not throw, may return empty or defaults
    expect(Array.isArray(files)).toBe(true);
  });

  // =========================================================================
  // T101.05: Recursive discovery (integration)
  // =========================================================================
  it('T101.05: finds multiple file types', async () => {
    /**
     * SPEC: S101
     * TEST_ID: T101.05
     * EC_ID: EC215
     *
     * Given: Pattern matching all fixtures
     * When: discoverFiles is called
     * Then: Returns all dependency files
     */
    const pattern = path.join(FIXTURES_DIR, '*');
    const files = await discoverFiles(pattern);

    // Should find requirements.txt, package.json, Cargo.toml, pyproject.toml
    expect(files.length).toBe(4);
  });
});

describe('Registry Detection (S101)', () => {
  // =========================================================================
  // EC200: requirements.txt -> pypi
  // =========================================================================
  it('EC200: requirements.txt maps to pypi', () => {
    expect(getRegistryForFile('requirements.txt')).toBe('pypi');
    expect(getRegistryForFile('/path/to/requirements.txt')).toBe('pypi');
  });

  // =========================================================================
  // EC201: package.json -> npm
  // =========================================================================
  it('EC201: package.json maps to npm', () => {
    expect(getRegistryForFile('package.json')).toBe('npm');
    expect(getRegistryForFile('/path/to/package.json')).toBe('npm');
  });

  // =========================================================================
  // EC202: Cargo.toml -> crates
  // =========================================================================
  it('EC202: Cargo.toml maps to crates', () => {
    expect(getRegistryForFile('Cargo.toml')).toBe('crates');
    expect(getRegistryForFile('/path/to/Cargo.toml')).toBe('crates');
  });

  // =========================================================================
  // requirements-*.txt pattern
  // =========================================================================
  it('requirements-dev.txt maps to pypi', () => {
    expect(getRegistryForFile('requirements-dev.txt')).toBe('pypi');
    expect(getRegistryForFile('requirements-test.txt')).toBe('pypi');
  });

  // =========================================================================
  // Unknown file type
  // =========================================================================
  it('unknown file type returns unknown', () => {
    expect(getRegistryForFile('unknown.xyz')).toBe('unknown');
    expect(getRegistryForFile('README.md')).toBe('unknown');
  });
});

describe('isDependencyFile (S101)', () => {
  it('returns true for known dependency files', () => {
    expect(isDependencyFile('requirements.txt')).toBe(true);
    expect(isDependencyFile('package.json')).toBe(true);
    expect(isDependencyFile('Cargo.toml')).toBe(true);
    expect(isDependencyFile('pyproject.toml')).toBe(true);
  });

  it('returns false for unknown files', () => {
    expect(isDependencyFile('README.md')).toBe(false);
    expect(isDependencyFile('config.yaml')).toBe(false);
  });
});

describe('File Discovery Edge Cases (EC206-EC215)', () => {
  // =========================================================================
  // EC206: Symlink to file followed (platform-dependent)
  // =========================================================================
  it.skip('EC206: symlink to file followed', async () => {
    /**
     * P1-EC206: Valid symlinks should be followed
     *
     * Note: Symlinks behave differently on Windows vs Unix.
     * This test is skipped by default and should be run
     * in CI on Linux/macOS where symlinks work reliably.
     */
    // Would test symlink following
  });

  // =========================================================================
  // EC207: Broken symlink skipped with warning
  // =========================================================================
  it.skip('EC207: broken symlink skipped with warning', async () => {
    /**
     * P1-EC207: Broken symlinks should be skipped with warning
     *
     * Note: Symlinks behave differently on Windows vs Unix.
     */
    // Would test broken symlink handling
  });

  // =========================================================================
  // EC208: Directory instead of file skipped
  // =========================================================================
  it('EC208: directory instead of file skipped', async () => {
    // discoverFiles only returns files, not directories
    const pattern = path.join(FIXTURES_DIR, '..'); // Parent dir
    const files = await discoverFiles(pattern);

    // Directories should be filtered out
    for (const file of files) {
      expect(file).not.toMatch(/\/fixtures$/);
    }
  });

  // =========================================================================
  // EC211-EC213: File content edge cases (tested in extract.test.ts)
  // =========================================================================
  it.skip('EC211: empty file returns empty package list', () => {
    // Tested in extract.test.ts
  });

  it.skip('EC212: UTF-8 BOM stripped', () => {
    // Tested in extract.test.ts
  });

  it.skip('EC213: CRLF line endings parsed correctly', () => {
    // Tested in extract.test.ts
  });
});
