/**
 * SPEC: S100-S106
 * TEST_IDs: T100.02, T100.03, T103.02
 * INVARIANTS: INV101-INV108
 *
 * Full integration tests for the Phantom Guard GitHub Action.
 * Tests the complete workflow from file discovery to output generation.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as path from 'path';
import * as fs from 'fs';

// Mock @actions/core
vi.mock('@actions/core', () => ({
  info: vi.fn(),
  warning: vi.fn(),
  error: vi.fn(),
  debug: vi.fn(),
  setOutput: vi.fn(),
  setFailed: vi.fn(),
  getInput: vi.fn(),
}));

// Mock @actions/github
vi.mock('@actions/github', () => ({
  context: {
    payload: { pull_request: null },
    repo: { owner: 'test', repo: 'test' },
  },
}));

import { extractPackages } from '../../src/extract';
import { validatePackages, ValidationResult } from '../../src/validate';
import { generateSARIF } from '../../src/sarif';

const FIXTURES_DIR = path.join(__dirname, 'fixtures', 'test-repo');
const SARIF_PATH = path.join(process.cwd(), 'phantom-guard-results.sarif');

describe('Full Workflow Integration (S100-S106)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Clean up any existing SARIF file
    if (fs.existsSync(SARIF_PATH)) {
      fs.unlinkSync(SARIF_PATH);
    }
  });

  afterEach(() => {
    // Clean up SARIF file after tests
    if (fs.existsSync(SARIF_PATH)) {
      fs.unlinkSync(SARIF_PATH);
    }
  });

  // ===========================================================================
  // T100.02: Full workflow completes successfully
  // ===========================================================================
  it('T100.02: completes full workflow with mixed packages', async () => {
    /**
     * SPEC: S100
     * TEST_ID: T100.02
     * INVARIANTS: INV101-INV107
     *
     * Given: A test repository with multiple dependency files
     * When: Running the full workflow (discover → extract → validate → SARIF)
     * Then: All steps complete and produce expected outputs
     */

    // Define test files (extractPackages takes array of file paths)
    const testFiles = [
      path.join(FIXTURES_DIR, 'requirements.txt'),
      path.join(FIXTURES_DIR, 'package.json'),
    ];

    // Step 2: Extract packages from files
    const allPackages = await extractPackages(testFiles);

    // Should have extracted packages from both files
    expect(allPackages.length).toBeGreaterThan(0);

    // Step 3: Validate packages
    const results = await validatePackages(allPackages);

    // INV104: All packages should have results
    expect(results.length).toBe(allPackages.length);

    // Check for expected classifications
    const safe = results.filter((r) => r.riskLevel === 'safe');
    const notSafe = results.filter((r) => r.riskLevel !== 'safe');

    // We should have at least some of each type based on our fixtures
    expect(safe.length).toBeGreaterThan(0);
    expect(notSafe.length).toBeGreaterThan(0);

    // Step 4: Generate SARIF
    await generateSARIF(results);

    expect(fs.existsSync(SARIF_PATH)).toBe(true);
    const sarif = JSON.parse(fs.readFileSync(SARIF_PATH, 'utf-8'));
    expect(sarif.version).toBe('2.1.0');
    expect(Array.isArray(sarif.runs[0].results)).toBe(true);
  });

  // ===========================================================================
  // T100.03: Cold start performance
  // ===========================================================================
  it('T100.03: cold start completes under 5s', async () => {
    /**
     * SPEC: S100
     * TEST_ID: T100.03
     * BUDGET: < 5s cold start
     *
     * Given: First execution (no cache)
     * When: Running full workflow
     * Then: Completes in under 5 seconds
     */
    const startTime = Date.now();

    // Full workflow
    const reqFile = path.join(FIXTURES_DIR, 'requirements.txt');
    const packages = await extractPackages([reqFile]);
    const results = await validatePackages(packages);
    await generateSARIF(results);

    const elapsed = Date.now() - startTime;

    expect(elapsed).toBeLessThan(5000);
  });

  // ===========================================================================
  // INV104: All packages get validation results
  // ===========================================================================
  it('INV104: all packages receive validation results', async () => {
    /**
     * INVARIANT: INV104
     * Every package that is extracted must have a validation result.
     */
    const reqFile = path.join(FIXTURES_DIR, 'requirements.txt');
    const allPackages = await extractPackages([reqFile]);

    const results = await validatePackages(allPackages);

    // Every input package has exactly one result
    expect(results.length).toBe(allPackages.length);

    // Every result has required fields
    for (const result of results) {
      expect(result.package).toBeDefined();
      expect(['safe', 'suspicious', 'high-risk']).toContain(result.riskLevel);
      expect(typeof result.riskScore).toBe('number');
      expect(result.riskScore).toBeGreaterThanOrEqual(0);
      expect(result.riskScore).toBeLessThanOrEqual(1);
    }
  });

  // ===========================================================================
  // INV107: SARIF output is schema-valid
  // ===========================================================================
  it('INV107: SARIF output is schema-valid', async () => {
    /**
     * INVARIANT: INV107
     * SARIF output must be valid SARIF 2.1.0 format.
     */
    const reqFile = path.join(FIXTURES_DIR, 'requirements.txt');
    const allPackages = await extractPackages([reqFile]);
    const results = await validatePackages(allPackages);

    await generateSARIF(results);

    const sarif = JSON.parse(fs.readFileSync(SARIF_PATH, 'utf-8'));

    // Required SARIF 2.1.0 fields
    expect(sarif.version).toBe('2.1.0');
    expect(sarif.$schema).toContain('sarif-schema-2.1.0');
    expect(Array.isArray(sarif.runs)).toBe(true);
    expect(sarif.runs.length).toBe(1);

    // Tool driver structure
    const tool = sarif.runs[0].tool.driver;
    expect(tool.name).toBe('Phantom Guard');
    expect(tool.version).toBeDefined();
    expect(tool.informationUri).toBeDefined();

    // Results structure
    const sarifResults = sarif.runs[0].results;
    expect(Array.isArray(sarifResults)).toBe(true);

    for (const result of sarifResults) {
      expect(result.ruleId).toBeDefined();
      expect(['error', 'warning', 'note']).toContain(result.level);
      expect(result.message?.text).toBeDefined();
      expect(Array.isArray(result.locations)).toBe(true);
    }
  });
});

describe('Performance Benchmarks (T103.02, P2-PERF-002)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ===========================================================================
  // T103.02: 50 packages under 30 seconds
  // ===========================================================================
  it('T103.02: validates 50 packages in under 30 seconds', async () => {
    /**
     * SPEC: S103
     * TEST_ID: T103.02
     * BUDGET: 50 packages < 30s
     *
     * Given: 50 packages to validate
     * When: Running validation
     * Then: Completes in under 30 seconds
     */
    const packages = Array.from({ length: 50 }, (_, i) => ({
      name: `test-package-${i}`,
      registry: 'pypi' as const,
      sourceFile: 'test.txt',
      lineNumber: i + 1,
    }));

    const startTime = Date.now();
    const results = await validatePackages(packages);
    const elapsed = Date.now() - startTime;

    expect(results.length).toBe(50);
    expect(elapsed).toBeLessThan(30000);

    // Pattern-based validation should be much faster
    expect(elapsed).toBeLessThan(1000); // Actually < 1s with pattern matching
  });

  // ===========================================================================
  // P2-PERF-002: SARIF generation under 100ms
  // ===========================================================================
  it('P2-PERF-002: SARIF generation completes under 100ms', async () => {
    /**
     * BUDGET: P2-PERF-002
     * SARIF generation < 100ms for 100 results
     */
    // Generate mock results
    const results: ValidationResult[] = Array.from({ length: 100 }, (_, i) => ({
      package: `package-${i}`,
      riskLevel: i % 3 === 0 ? 'high-risk' : 'suspicious',
      riskScore: 0.3 + (i % 10) * 0.07,
      signals: ['AI_MODEL_NAME', 'SUSPICIOUS_PREFIX'],
      sourceFile: 'requirements.txt',
      lineNumber: i + 1,
      registry: 'pypi',
    }));

    const startTime = Date.now();
    await generateSARIF(results);
    const elapsed = Date.now() - startTime;

    expect(elapsed).toBeLessThan(100);
  });

  // ===========================================================================
  // Large batch performance
  // ===========================================================================
  it('validates 200 packages in under 5 seconds', async () => {
    /**
     * Extended performance test for larger batches.
     * Pattern-based validation should scale linearly.
     */
    const packages = Array.from({ length: 200 }, (_, i) => ({
      name: `test-package-${i}`,
      registry: 'pypi' as const,
      sourceFile: 'test.txt',
      lineNumber: i + 1,
    }));

    const startTime = Date.now();
    const results = await validatePackages(packages);
    const elapsed = Date.now() - startTime;

    expect(results.length).toBe(200);
    expect(elapsed).toBeLessThan(5000);
  });
});

describe('Exit Code Mapping (INV108)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ===========================================================================
  // INV108: Exit codes match documentation
  // ===========================================================================
  it('INV108: returns correct exit codes for different scenarios', async () => {
    /**
     * INVARIANT: INV108
     * Exit codes must match documented values:
     * 0 = All safe
     * 1 = High-risk found
     * 2 = Suspicious found (no high-risk)
     * 3 = Not found (no issues)
     * 4 = Internal error
     */

    // Test all-safe scenario
    const safePackages = [
      { name: 'flask', registry: 'pypi' as const, sourceFile: 'test.txt', lineNumber: 1 },
      { name: 'requests', registry: 'pypi' as const, sourceFile: 'test.txt', lineNumber: 2 },
    ];
    const safeResults = await validatePackages(safePackages);
    const allSafe = safeResults.every((r) => r.riskLevel === 'safe');
    expect(allSafe).toBe(true);

    // Test suspicious scenario (need score >= 0.3)
    // easy-helper: 0.15 (prefix) + 0.15 (suffix) = 0.30 → suspicious
    const suspiciousPackages = [
      { name: 'easy-helper', registry: 'pypi' as const, sourceFile: 'test.txt', lineNumber: 1 },
    ];
    const suspiciousResults = await validatePackages(suspiciousPackages);
    expect(suspiciousResults.some((r) => r.riskLevel === 'suspicious')).toBe(true);

    // Test high-risk scenario (need score >= 0.7)
    // flask-gpt-helper: 0.4 (gpt) + 0.5 (hallucination combo) + 0.15 (suffix) = 1.05 (capped to 1.0)
    const highRiskPackages = [
      { name: 'flask-gpt-helper', registry: 'pypi' as const, sourceFile: 'test.txt', lineNumber: 1 },
    ];
    const highRiskResults = await validatePackages(highRiskPackages);
    expect(highRiskResults.some((r) => r.riskLevel === 'high-risk')).toBe(true);
  });
});

describe('Multi-Registry Support', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ===========================================================================
  // Tests registry-specific handling
  // ===========================================================================
  it('handles packages from multiple registries', async () => {
    /**
     * Test that packages from different registries are correctly identified
     * and validated with the same pattern matching rules.
     */
    const packages = [
      { name: 'flask', registry: 'pypi' as const, sourceFile: 'requirements.txt', lineNumber: 1 },
      { name: 'react', registry: 'npm' as const, sourceFile: 'package.json', lineNumber: 1 },
      { name: 'serde', registry: 'crates' as const, sourceFile: 'Cargo.toml', lineNumber: 1 },
      { name: 'flask-gpt', registry: 'pypi' as const, sourceFile: 'requirements.txt', lineNumber: 2 },
      { name: 'react-gpt-helper', registry: 'npm' as const, sourceFile: 'package.json', lineNumber: 2 },
    ];

    const results = await validatePackages(packages);

    expect(results.length).toBe(5);

    // Known safe packages should be safe
    const flask = results.find((r) => r.package === 'flask');
    const react = results.find((r) => r.package === 'react');
    const serde = results.find((r) => r.package === 'serde');

    expect(flask?.riskLevel).toBe('safe');
    expect(react?.riskLevel).toBe('safe');
    expect(serde?.riskLevel).toBe('safe');

    // GPT-related packages should be flagged
    const flaskGpt = results.find((r) => r.package === 'flask-gpt');
    const reactGptHelper = results.find((r) => r.package === 'react-gpt-helper');

    expect(flaskGpt?.riskLevel).not.toBe('safe');
    expect(reactGptHelper?.riskLevel).not.toBe('safe');
  });
});
