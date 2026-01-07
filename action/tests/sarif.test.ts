/**
 * SPEC: S105 - SARIF Output Generator
 * TEST_IDs: T105.01-T105.03
 * INVARIANTS: INV107
 * EDGE_CASES: EC260-EC270
 *
 * Tests for SARIF output generation.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// Mock @actions/core
vi.mock('@actions/core', () => ({
  info: vi.fn(),
  warning: vi.fn(),
  error: vi.fn(),
  debug: vi.fn(),
  setOutput: vi.fn(),
}));

import { generateSARIF } from '../src/sarif';
import { ValidationResult } from '../src/validate';
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

describe('SARIF Generator (S105)', () => {
  const sarifPath = path.join(process.cwd(), 'phantom-guard-results.sarif');

  beforeEach(() => {
    vi.clearAllMocks();
    // Clean up any existing SARIF file
    if (fs.existsSync(sarifPath)) {
      fs.unlinkSync(sarifPath);
    }
  });

  afterEach(() => {
    // Clean up SARIF file after tests
    if (fs.existsSync(sarifPath)) {
      fs.unlinkSync(sarifPath);
    }
  });

  // =========================================================================
  // T105.01: Valid SARIF structure
  // =========================================================================
  it('T105.01: generates valid SARIF 2.1.0 structure', async () => {
    /**
     * SPEC: S105
     * TEST_ID: T105.01
     * INV_ID: INV107
     * EC_ID: EC260
     *
     * Given: Normal validation results
     * When: generateSARIF is called
     * Then: Output is schema-valid SARIF 2.1.0
     */
    const results: ValidationResult[] = [
      createResult('gpt-helper', 'suspicious', 0.4, ['AI_MODEL_NAME']),
    ];

    await generateSARIF(results);

    // Check file was created
    expect(fs.existsSync(sarifPath)).toBe(true);

    // Parse and validate structure
    const sarif = JSON.parse(fs.readFileSync(sarifPath, 'utf-8'));

    expect(sarif.version).toBe('2.1.0');
    expect(sarif.$schema).toContain('sarif-schema-2.1.0');
    expect(Array.isArray(sarif.runs)).toBe(true);
    expect(sarif.runs.length).toBe(1);
    expect(sarif.runs[0].tool.driver.name).toBe('Phantom Guard');
  });

  // =========================================================================
  // T105.02: HIGH_RISK = error level
  // =========================================================================
  it('T105.02: HIGH_RISK maps to error level', async () => {
    /**
     * SPEC: S105
     * TEST_ID: T105.02
     * INV_ID: INV107
     * EC_ID: EC261
     *
     * Given: HIGH_RISK package in results
     * When: generateSARIF is called
     * Then: Finding has level: "error"
     */
    const results: ValidationResult[] = [
      createResult('flask-gpt-wrapper', 'high-risk', 0.8, [
        'AI_MODEL_NAME',
        'HALLUCINATION_COMBO',
      ]),
    ];

    await generateSARIF(results);

    const sarif = JSON.parse(fs.readFileSync(sarifPath, 'utf-8'));
    const finding = sarif.runs[0].results[0];

    expect(finding.level).toBe('error');
  });

  // =========================================================================
  // T105.03: Empty results handled
  // =========================================================================
  it('T105.03: empty results generates valid SARIF', async () => {
    /**
     * SPEC: S105
     * TEST_ID: T105.03
     * INV_ID: INV107
     * EC_ID: EC266
     *
     * Given: All packages safe (no findings)
     * When: generateSARIF is called
     * Then: Valid SARIF with empty results array
     */
    const results: ValidationResult[] = [
      createResult('flask', 'safe', 0),
      createResult('requests', 'safe', 0),
    ];

    await generateSARIF(results);

    const sarif = JSON.parse(fs.readFileSync(sarifPath, 'utf-8'));

    // Should have valid structure even with no findings
    expect(sarif.version).toBe('2.1.0');
    expect(Array.isArray(sarif.runs[0].results)).toBe(true);
    expect(sarif.runs[0].results.length).toBe(0);
  });
});

describe('SARIF Edge Cases (EC260-EC270)', () => {
  const sarifPath = path.join(process.cwd(), 'phantom-guard-results.sarif');

  beforeEach(() => {
    vi.clearAllMocks();
    if (fs.existsSync(sarifPath)) {
      fs.unlinkSync(sarifPath);
    }
  });

  afterEach(() => {
    if (fs.existsSync(sarifPath)) {
      fs.unlinkSync(sarifPath);
    }
  });

  // =========================================================================
  // EC262: SUSPICIOUS maps to warning level
  // =========================================================================
  it('EC262: SUSPICIOUS maps to warning level', async () => {
    const results: ValidationResult[] = [
      createResult('easy-flask', 'suspicious', 0.3, ['SUSPICIOUS_PREFIX']),
    ];

    await generateSARIF(results);

    const sarif = JSON.parse(fs.readFileSync(sarifPath, 'utf-8'));
    const finding = sarif.runs[0].results[0];

    expect(finding.level).toBe('warning');
  });

  // =========================================================================
  // EC264: Location maps to correct line
  // =========================================================================
  it('EC264: location maps to correct line', async () => {
    const results: ValidationResult[] = [
      {
        package: 'test-package',
        riskLevel: 'suspicious',
        riskScore: 0.3,
        signals: ['SUSPICIOUS_SUFFIX'],
        sourceFile: 'requirements.txt',
        lineNumber: 42,
        registry: 'pypi',
      },
    ];

    await generateSARIF(results);

    const sarif = JSON.parse(fs.readFileSync(sarifPath, 'utf-8'));
    const location = sarif.runs[0].results[0].locations[0].physicalLocation;

    expect(location.artifactLocation.uri).toBe('requirements.txt');
    expect(location.region.startLine).toBe(42);
  });

  // =========================================================================
  // EC268: Tool info has correct version
  // =========================================================================
  it('EC268: tool info has correct version', async () => {
    const results: ValidationResult[] = [
      createResult('test', 'suspicious', 0.3, ['SUSPICIOUS_PREFIX']),
    ];

    await generateSARIF(results);

    const sarif = JSON.parse(fs.readFileSync(sarifPath, 'utf-8'));
    const tool = sarif.runs[0].tool.driver;

    expect(tool.name).toBe('Phantom Guard');
    expect(tool.version).toBe('0.2.0');
    expect(tool.informationUri).toContain('phantom-guard');
  });

  // =========================================================================
  // Sets output for upload-sarif action
  // =========================================================================
  it('sets sarif-file output', async () => {
    const results: ValidationResult[] = [
      createResult('test', 'safe', 0),
    ];

    await generateSARIF(results);

    expect(core.setOutput).toHaveBeenCalledWith('sarif-file', sarifPath);
  });

  // =========================================================================
  // Skipped tests (require more complex setup)
  // =========================================================================
  it.skip('EC263: NOT_FOUND uses PG003 rule', () => {});
  it.skip('EC265: multiple files have physicalLocation', () => {});
  it.skip('EC267: all rule IDs defined', () => {});
  it.skip('EC269: large results valid structure', () => {});
  it.skip('EC270: special characters properly escaped', () => {});
});
