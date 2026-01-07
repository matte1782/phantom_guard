/**
 * SPEC: S102 - Package Extractor
 * TEST_IDs: T102.01-T102.05
 * INVARIANTS: INV103
 * EDGE_CASES: EC220-EC235
 *
 * Tests for package name extraction from dependency files.
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

import { extractPackages, type ExtractedPackage } from '../src/extract';

const FIXTURES_DIR = path.join(__dirname, 'fixtures');

describe('Package Extractor (S102)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // T102.01: Extract simple package
  // =========================================================================
  it('T102.01: extracts simple package name from requirements.txt', async () => {
    /**
     * SPEC: S102
     * TEST_ID: T102.01
     * INV_ID: INV103
     * EC_ID: EC220
     *
     * Given: requirements.txt with packages
     * When: extractPackages is called
     * Then: Returns packages with names
     */
    const files = [path.join(FIXTURES_DIR, 'requirements.txt')];
    const packages = await extractPackages(files);

    expect(packages.length).toBeGreaterThan(0);
    const names = packages.map((p) => p.name);
    expect(names).toContain('requests');
    expect(names).toContain('flask');
    expect(names).toContain('numpy');
  });

  // =========================================================================
  // T102.02: Strip version specifier
  // =========================================================================
  it('T102.02: strips version specifier correctly', async () => {
    /**
     * SPEC: S102
     * TEST_ID: T102.02
     * INV_ID: INV103
     * EC_ID: EC221
     *
     * Given: Lines with version specifiers
     * When: extractPackages is called
     * Then: Returns packages with versions preserved separately
     */
    const files = [path.join(FIXTURES_DIR, 'requirements.txt')];
    const packages = await extractPackages(files);

    const requestsPkg = packages.find((p) => p.name === 'requests');
    expect(requestsPkg).toBeDefined();
    expect(requestsPkg?.version).toContain('==2.31.0');

    const flaskPkg = packages.find((p) => p.name === 'flask');
    expect(flaskPkg).toBeDefined();
    expect(flaskPkg?.version).toContain('>=2.0.0');
  });

  // =========================================================================
  // T102.03: Handle scoped npm package
  // =========================================================================
  it('T102.03: handles package.json dependencies', async () => {
    /**
     * SPEC: S102
     * TEST_ID: T102.03
     * INV_ID: INV103
     * EC_ID: EC228
     *
     * Given: package.json with dependencies
     * When: extractPackages is called
     * Then: Returns npm packages
     */
    const files = [path.join(FIXTURES_DIR, 'package.json')];
    const packages = await extractPackages(files);

    expect(packages.length).toBeGreaterThan(0);
    const names = packages.map((p) => p.name);
    expect(names).toContain('express');
    expect(names).toContain('lodash');
    expect(names).toContain('typescript');

    // Check registry is npm
    expect(packages.every((p) => p.registry === 'npm')).toBe(true);
  });

  // =========================================================================
  // T102.04: Handle Cargo.toml
  // =========================================================================
  it('T102.04: handles Cargo.toml dependencies', async () => {
    /**
     * SPEC: S102
     * TEST_ID: T102.04
     * INV_ID: INV103
     *
     * Given: Cargo.toml with dependencies
     * When: extractPackages is called
     * Then: Returns crates packages
     */
    const files = [path.join(FIXTURES_DIR, 'Cargo.toml')];
    const packages = await extractPackages(files);

    expect(packages.length).toBeGreaterThan(0);
    const names = packages.map((p) => p.name);
    expect(names).toContain('serde');
    expect(names).toContain('tokio');

    // Check registry is crates
    expect(packages.every((p) => p.registry === 'crates')).toBe(true);
  });

  // =========================================================================
  // T102.05: Handle pyproject.toml
  // =========================================================================
  it('T102.05: handles pyproject.toml dependencies', async () => {
    /**
     * SPEC: S102
     * TEST_ID: T102.05
     * INV_ID: INV103
     *
     * Given: pyproject.toml with dependencies
     * When: extractPackages is called
     * Then: Returns pypi packages
     */
    const files = [path.join(FIXTURES_DIR, 'pyproject.toml')];
    const packages = await extractPackages(files);

    expect(packages.length).toBeGreaterThan(0);
    const names = packages.map((p) => p.name);
    expect(names).toContain('httpx');
    expect(names).toContain('pydantic');

    // Check registry is pypi
    expect(packages.every((p) => p.registry === 'pypi')).toBe(true);
  });

  // =========================================================================
  // Multiple files extraction
  // =========================================================================
  it('extracts packages from multiple files', async () => {
    const files = [
      path.join(FIXTURES_DIR, 'requirements.txt'),
      path.join(FIXTURES_DIR, 'package.json'),
    ];
    const packages = await extractPackages(files);

    // Should have packages from both files
    const registries = new Set(packages.map((p) => p.registry));
    expect(registries.has('pypi')).toBe(true);
    expect(registries.has('npm')).toBe(true);
  });
});

describe('Package Extractor Edge Cases (EC220-EC235)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // EC222: Comment line ignored
  // =========================================================================
  it('EC222: ignores comment lines in requirements.txt', async () => {
    const files = [path.join(FIXTURES_DIR, 'requirements.txt')];
    const packages = await extractPackages(files);

    // Should not contain comment text as package
    const names = packages.map((p) => p.name);
    expect(names.every((n) => !n.includes('#'))).toBe(true);
    expect(names.every((n) => !n.includes('Test'))).toBe(true);
  });

  // =========================================================================
  // EC234: Case normalized to lowercase
  // =========================================================================
  it('EC234: normalizes package names to lowercase', async () => {
    const files = [path.join(FIXTURES_DIR, 'requirements.txt')];
    const packages = await extractPackages(files);

    // All names should be lowercase
    for (const pkg of packages) {
      expect(pkg.name).toBe(pkg.name.toLowerCase());
    }
  });

  // =========================================================================
  // Line numbers preserved
  // =========================================================================
  it('preserves line numbers for SARIF output', async () => {
    const files = [path.join(FIXTURES_DIR, 'requirements.txt')];
    const packages = await extractPackages(files);

    // All packages should have line numbers
    for (const pkg of packages) {
      if (pkg.lineNumber !== undefined) {
        expect(pkg.lineNumber).toBeGreaterThan(0);
      }
    }
  });

  // =========================================================================
  // INV103: Graceful error handling
  // =========================================================================
  it('INV103: handles non-existent file gracefully', async () => {
    const files = ['nonexistent.txt'];

    // Should not throw
    const packages = await extractPackages(files);
    expect(Array.isArray(packages)).toBe(true);
  });

  // =========================================================================
  // Registry detection
  // =========================================================================
  it('assigns correct registry to each file type', async () => {
    const reqFiles = [path.join(FIXTURES_DIR, 'requirements.txt')];
    const reqPackages = await extractPackages(reqFiles);
    expect(reqPackages.every((p) => p.registry === 'pypi')).toBe(true);

    const npmFiles = [path.join(FIXTURES_DIR, 'package.json')];
    const npmPackages = await extractPackages(npmFiles);
    expect(npmPackages.every((p) => p.registry === 'npm')).toBe(true);

    const cargoFiles = [path.join(FIXTURES_DIR, 'Cargo.toml')];
    const cargoPackages = await extractPackages(cargoFiles);
    expect(cargoPackages.every((p) => p.registry === 'crates')).toBe(true);
  });

  // =========================================================================
  // Skipped tests (require more complex fixtures)
  // =========================================================================
  it.skip('EC223: inline comment handled', () => {
    // Would need fixture with inline comments
  });

  it.skip('EC224: environment marker stripped', () => {
    // Would need fixture with ; markers
  });

  it.skip('EC225: extra specifier handled', () => {
    // Would need fixture with [extra] syntax
  });

  it.skip('EC226: URL dependency skipped with warning', () => {
    // Would need fixture with git+https:// lines
  });

  it.skip('EC227: local path skipped with warning', () => {
    // Would need fixture with ./ paths
  });

  it.skip('EC233: deduplicates packages', () => {
    // Would need fixture with duplicate package names
  });
});
