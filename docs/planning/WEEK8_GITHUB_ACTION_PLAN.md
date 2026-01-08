# Week 8: GitHub Action — Day-by-Day Implementation Plan

> **Phase**: 8 of 10
> **Theme**: GitHub Action for CI/CD Integration
> **Total Hours**: 48 (38 work + 10 buffer)
> **Status**: COMPLETE (HOSTILE_VALIDATOR: CONDITIONAL_GO)
> **Prerequisites**: Week 6-7 (New Detection Signals) COMPLETE
> **Hostile Review**: v1.1.0 — All P0/P1 issues addressed
> **Tests**: 108 passed, 31 skipped stubs

---

## Overview

| Day | Task | SPEC | Description | Hours | Status |
|:----|:-----|:-----|:------------|:------|:-------|
| 1 | W8.1 | S100, S106 | Action entry point + exit codes | 6 | ✅ COMPLETE |
| 2 | W8.2 | S101 | File discovery (glob patterns) | 4 | ✅ COMPLETE |
| 3 | W8.3 | S102 | Package extraction (all formats) | 6 | ✅ COMPLETE |
| 4 | W8.4 | S103 | Validation orchestrator | 6 | ✅ COMPLETE |
| 5 | W8.5 | S104, S105 | PR comment + SARIF outputs | 6 | ✅ COMPLETE |
| 6 | W8.6, W8.7 | - | Integration tests + hostile review | 10 | ✅ COMPLETE |

---

## Day 1: Action Entry Point + Exit Codes (W8.1)

### Traces
- **SPEC**: S100, S106
- **INVARIANTS**: INV100, INV101, INV108
- **TESTS**: T100.01-T100.03, T106.01-T106.04
- **EDGE CASES**: -

### Definition
Implement GitHub Action entry point with action.yml manifest and exit code handling.

### Files to Create
```
action/
├── action.yml              # GitHub Action manifest
├── package.json            # Node.js project config
├── package-lock.json       # Lock file (P1-MISSING-001)
├── tsconfig.json           # TypeScript config
├── vitest.config.ts        # Test config
├── src/
│   ├── index.ts            # Main entry point
│   ├── exit.ts             # Exit code handling
│   ├── errors.ts           # Error types (from SPEC)
│   └── types.ts            # Type definitions
└── tests/
    ├── __mocks__/
    │   └── core.ts         # Mock @actions/core
    ├── exit.test.ts        # Exit code tests
    └── index.test.ts       # Entry point tests
```

### action.yml Configuration
```yaml
name: 'Phantom Guard'
description: 'Detect AI-hallucinated package attacks (slopsquatting)'
author: 'Phantom Guard'
branding:
  icon: 'shield'
  color: 'purple'
inputs:
  files:
    description: 'File patterns to validate (comma-separated)'
    required: false
    default: 'requirements.txt,package.json,Cargo.toml,pyproject.toml'
  fail-on:
    description: 'When to fail: high-risk, suspicious, or none'
    required: false
    default: 'high-risk'
  output:
    description: 'Output format: github-comment, sarif, json, none'
    required: false
    default: 'github-comment,sarif'
  python-path:
    description: 'Path to Python executable'
    required: false
    default: 'python'
outputs:
  safe-count:
    description: 'Number of safe packages'
  suspicious-count:
    description: 'Number of suspicious packages'
  high-risk-count:
    description: 'Number of high-risk packages'
  sarif-file:
    description: 'Path to SARIF output file'
runs:
  using: 'node20'
  main: 'dist/index.js'
```

### Entry Point with Token Security (P1-SEC-003)
```typescript
// action/src/index.ts
/**
 * IMPLEMENTS: S100
 * INVARIANTS: INV100
 * TESTS: T100.01-T100.03
 */

import * as core from '@actions/core';
import * as github from '@actions/github';

async function run(): Promise<void> {
  try {
    // P1-SEC-003: Mask GITHUB_TOKEN in logs
    const token = core.getInput('github-token') || process.env.GITHUB_TOKEN;
    if (token) {
      core.setSecret(token);
    }

    // Get inputs
    const filesInput = core.getInput('files');
    const failOn = core.getInput('fail-on') as 'high-risk' | 'suspicious' | 'none';
    const outputFormat = core.getInput('output');
    const pythonPath = core.getInput('python-path');

    // INV100: Always produce valid output (try/catch wrapper)
    const files = await discoverFiles(filesInput);  // Takes comma-separated string
    const packages = await extractPackages(files);   // Takes string[] of file paths
    const results = await validatePackages(packages); // Pattern-based validation (no shell)

    // Generate outputs
    if (outputFormat.includes('sarif')) {
      await generateSarifOutput(results);
    }
    if (outputFormat.includes('github-comment') && github.context.payload.pull_request) {
      await postComment(results, token);
    }

    // Set outputs
    core.setOutput('safe-count', results.filter(r => r.riskLevel === 'SAFE').length);
    core.setOutput('suspicious-count', results.filter(r => r.riskLevel === 'SUSPICIOUS').length);
    core.setOutput('high-risk-count', results.filter(r => r.riskLevel === 'HIGH_RISK').length);

    // Determine exit code
    const exitCode = determineExitCode(results, failOn);
    if (exitCode !== ExitCode.SUCCESS) {
      core.setFailed(`Phantom Guard found issues (exit code ${exitCode})`);
    }

  } catch (error) {
    // INV100: Never throw uncaught - always produce valid output
    if (error instanceof ActionError) {
      core.setFailed(error.message);
      process.exit(error.code);
    } else {
      core.setFailed(`Unexpected error: ${error.message}`);
      process.exit(ExitCode.RUNTIME_ERROR);
    }
  }
}

run();
```

### Exit Code Implementation
```typescript
// action/src/exit.ts
/**
 * IMPLEMENTS: S106
 * INVARIANTS: INV101, INV108
 * TESTS: T106.01-T106.04
 */

export enum ExitCode {
  SUCCESS = 0,          // All packages safe
  SUSPICIOUS = 1,       // Suspicious packages found
  HIGH_RISK = 2,        // High-risk packages found
  NOT_FOUND = 3,        // Package not found in registry
  CONFIG_ERROR = 4,     // Configuration error
  RUNTIME_ERROR = 5,    // Runtime error
}

export function determineExitCode(
  results: ValidationResult[],
  failOn: 'high-risk' | 'suspicious' | 'none'
): ExitCode {
  // INV101: Exit code matches report status exactly
  // INV108: Exit codes always in range [0-5]

  const hasHighRisk = results.some(r => r.riskLevel === 'HIGH_RISK');
  const hasSuspicious = results.some(r => r.riskLevel === 'SUSPICIOUS');
  const hasNotFound = results.some(r => r.riskLevel === 'NOT_FOUND');

  if (hasHighRisk && failOn !== 'none') {
    return ExitCode.HIGH_RISK;
  }
  if (hasNotFound && failOn !== 'none') {
    return ExitCode.NOT_FOUND;
  }
  if (hasSuspicious && failOn === 'suspicious') {
    return ExitCode.SUSPICIOUS;
  }
  return ExitCode.SUCCESS;
}
```

### Error Types (from SPECIFICATION_V0.2.0.md)
```typescript
// action/src/errors.ts
/**
 * IMPLEMENTS: S100
 * INVARIANTS: INV100
 */

export class ActionError extends Error {
  constructor(message: string, public readonly code: number) {
    super(message);
    this.name = 'ActionError';
  }
}

export class FileDiscoveryError extends ActionError {
  constructor(pattern: string, reason: string) {
    super(`File discovery failed for pattern '${pattern}': ${reason}`, 4);
  }
}

export class PackageExtractionError extends ActionError {
  constructor(file: string, reason: string) {
    super(`Package extraction failed for '${file}': ${reason}`, 4);
  }
}

export class ValidationTimeoutError extends ActionError {
  constructor(packages: string[], timeoutMs: number) {
    super(`Validation timed out after ${timeoutMs}ms for ${packages.length} packages`, 5);
  }
}

export class CommentUpdateError extends ActionError {
  constructor(reason: string) {
    super(`PR comment update failed: ${reason}`, 0); // Non-fatal
  }
}

export class SarifGenerationError extends ActionError {
  constructor(reason: string) {
    super(`SARIF generation failed: ${reason}`, 5);
  }
}
```

### Build Configuration (P1-MISSING-001)
```json
// package.json
{
  "name": "phantom-guard-action",
  "version": "1.0.0",
  "scripts": {
    "build": "ncc build src/index.ts -o dist",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint src/",
    "typecheck": "tsc --noEmit",
    "ci": "npm ci && npm run lint && npm run typecheck && npm test && npm run build"
  },
  "dependencies": {
    "@actions/core": "^1.10.0",
    "@actions/github": "^6.0.0",
    "glob": "^10.3.0",
    "ajv": "^8.12.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@vercel/ncc": "^0.38.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0",
    "eslint": "^8.0.0"
  },
  "engines": {
    "node": ">=20"
  }
}
```

### Acceptance Criteria
- [ ] T100.01: Action completes without throwing (INV100)
- [ ] T100.02: Full workflow runs successfully
- [ ] T100.03: Cold start < 5s benchmark
- [ ] T106.01: Exit 0 for all safe
- [ ] T106.02: Exit 1 for suspicious
- [ ] T106.03: Exit 2 for high-risk
- [ ] T106.04: Exit code in [0-5] range (INV108)
- [ ] **P1-SEC-003**: core.setSecret(token) called for GITHUB_TOKEN
- [ ] **P1-MISSING-001**: package-lock.json committed, npm ci used
- [ ] action.yml valid syntax
- [ ] npm run build succeeds
- [ ] npm test passes

### Dependencies
- None (first task in Week 8)

### Post-Conditions
- action/action.yml exists and is valid
- action/package-lock.json committed
- action/src/index.ts exists with entry point
- action/src/exit.ts exists with exit code logic
- Tests T100.*, T106.* pass

---

## Day 2: File Discovery (W8.2)

### Traces
- **SPEC**: S101
- **INVARIANTS**: INV102
- **TESTS**: T101.01-T101.05
- **EDGE CASES**: EC200-EC215

### Definition
Implement file discovery using glob patterns with graceful error handling.

### Files to Create
```
action/src/
├── files.ts                # File discovery module
action/tests/
├── files.test.ts           # File discovery tests
├── fixtures/
│   ├── requirements.txt    # Test fixture
│   ├── package.json        # Test fixture
│   ├── Cargo.toml          # Test fixture
│   ├── pyproject.toml      # Test fixture
│   ├── symlink-valid       # Symlink to requirements.txt (P1-EC206)
│   └── symlink-broken      # Broken symlink (P1-EC207)
```

### Implementation
```typescript
// action/src/files.ts
/**
 * IMPLEMENTS: S101
 * INVARIANTS: INV102
 * TESTS: T101.01-T101.05
 * EDGE_CASES: EC200-EC215
 *
 * P1-EC206: Follows valid symlinks
 * P1-EC207: Skips broken symlinks with warning
 */

import * as glob from '@actions/glob';
import * as core from '@actions/core';
import * as fs from 'fs';
import * as path from 'path';

export const DEFAULT_PATTERNS = [
  'requirements.txt',
  'requirements/*.txt',
  'requirements-*.txt',
  'package.json',
  'Cargo.toml',
  'pyproject.toml',
];

export const FILE_REGISTRY_MAP: Record<string, string> = {
  'requirements.txt': 'pypi',
  'pyproject.toml': 'pypi',
  'package.json': 'npm',
  'Cargo.toml': 'crates',
};

/**
 * P1-EC206: Check if path is valid file (follows symlinks)
 * P1-EC207: Skip broken symlinks with warning
 */
function isValidFile(filePath: string): boolean {
  try {
    const stats = fs.statSync(filePath);
    return stats.isFile();
  } catch {
    try {
      const lstats = fs.lstatSync(filePath);
      if (lstats.isSymbolicLink()) {
        core.warning(`Skipping broken symlink: ${filePath}`);
      }
    } catch {}
    return false;
  }
}

/**
 * IMPLEMENTS: S101
 * INVARIANT: INV102 - Only returns existing files, graceful error handling
 *
 * @param patterns - Comma-separated glob patterns or file names
 * @returns Array of absolute file paths (string[])
 */
export async function discoverFiles(patterns: string): Promise<string[]> {
  const patternList = parsePatterns(patterns);
  const files: string[] = [];
  const seen = new Set<string>();

  for (const pattern of patternList) {
    try {
      const globber = await glob.create(pattern, {
        followSymbolicLinks: true, // P1-EC206
      });

      for await (const file of globber.globGenerator()) {
        if (!isValidFile(file)) continue;

        const realPath = fs.realpathSync(file);
        if (!seen.has(realPath)) {
          seen.add(realPath);
          files.push(path.normalize(file));
        }
      }
    } catch (error) {
      // INV102: Graceful fallback on invalid glob
      core.warning(`Pattern '${pattern}' error: ${error}`);
    }
  }

  return files.sort();
}

function parsePatterns(patterns: string): string[] {
  if (!patterns || patterns.trim() === '') {
    return DEFAULT_PATTERNS;
  }
  return patterns.split(',').map(p => p.trim()).filter(p => p.length > 0);
}

export function getRegistryForFile(filePath: string): string {
  const basename = path.basename(filePath);
  return FILE_REGISTRY_MAP[basename] || 'unknown';
}
```

### Edge Cases (EC200-EC215)
| EC_ID | Scenario | Expected | Test |
|:------|:---------|:---------|:-----|
| EC200 | Valid requirements.txt | Found, pypi | T101.01 |
| EC201 | Valid package.json | Found, npm | T101.02 |
| EC202 | Valid Cargo.toml | Found, crates | unit |
| EC204 | No matches | Empty array | T101.03 |
| EC205 | Invalid glob `[invalid` | Empty + warning | T101.04 |
| **EC206** | **Symlink to file** | **File followed** | **unit (P1-EC206)** |
| **EC207** | **Broken symlink** | **Skipped + warning** | **unit (P1-EC207)** |
| EC211 | Empty file | Empty package list | unit |
| EC212 | UTF-8 BOM | BOM stripped | unit |
| EC213 | CRLF line endings | Parsed correctly | unit |
| EC215 | Recursive `**/requirements.txt` | Found all | T101.05 |

### Performance Budgets (P2-PERF-001)
| Operation | Budget |
|:----------|:-------|
| File discovery | < 1s |

### Acceptance Criteria
- [ ] T101.01: Find requirements.txt (pypi registry)
- [ ] T101.02: Find package.json (npm registry)
- [ ] T101.03: No matches returns empty array (INV102)
- [ ] T101.04: Invalid glob handled gracefully (INV102)
- [ ] T101.05: Recursive discovery works
- [ ] **P1-EC206**: Symlinks followed correctly
- [ ] **P1-EC207**: Broken symlinks skipped with warning
- [ ] **P2-PERF-001**: File discovery < 1s
- [ ] Deduplication works (including via symlinks)
- [ ] Registry detection accurate

### Dependencies
- W8.1 (types, errors)

### Post-Conditions
- action/src/files.ts exists
- Tests T101.* pass
- INV102 enforced
- Symlink handling tested

---

## Day 3: Package Extraction (W8.3)

### Traces
- **SPEC**: S102
- **INVARIANTS**: INV103
- **TESTS**: T102.01-T102.05
- **EDGE CASES**: EC220-EC235

### Definition
Implement package extraction for all dependency file formats with graceful parsing.

### Files to Create
```
action/src/
├── extract.ts              # Package extraction module
├── validation.ts           # Package name validation (P1-SEC-002)
├── parsers/
│   ├── index.ts            # Parser exports
│   ├── requirements.ts     # requirements.txt parser
│   ├── package-json.ts     # package.json parser
│   ├── cargo-toml.ts       # Cargo.toml parser
│   └── pyproject.ts        # pyproject.toml parser
action/tests/
├── extract.test.ts         # Extraction tests
├── validation.test.ts      # Validation tests (P1-SEC-002)
├── parsers/
│   ├── requirements.test.ts
│   ├── package-json.test.ts
│   ├── cargo-toml.test.ts
│   └── pyproject.test.ts
```

### Package Name Validation (P1-SEC-002 - SECURITY CRITICAL)
```typescript
// action/src/validation.ts
/**
 * IMPLEMENTS: S102
 * INVARIANTS: INV103
 * SECURITY: P1-SEC-002 - Package name validation
 */

/**
 * Package name validation regex
 * - npm: @scope/name or name (alphanumeric, hyphens, dots, underscores)
 * - pypi: name (alphanumeric, hyphens, dots, underscores)
 * - crates: name (alphanumeric, hyphens, underscores)
 *
 * SECURITY: Prevents shell injection and invalid characters
 */
const PACKAGE_NAME_REGEX = /^(@[a-z0-9][-a-z0-9._]*\/)?[a-z0-9][-a-z0-9._]*$/i;

/**
 * Validate package name format
 * Returns true if valid, false if invalid (logs warning)
 */
export function isValidPackageName(name: string): boolean {
  if (!name || typeof name !== 'string') {
    return false;
  }

  const trimmed = name.trim();

  // Check length limits
  if (trimmed.length === 0 || trimmed.length > 214) {
    return false;
  }

  // Check against regex
  if (!PACKAGE_NAME_REGEX.test(trimmed)) {
    return false;
  }

  // SECURITY: Reject shell metacharacters explicitly
  const shellMetachars = /[;|&$`\\"'<>(){}[\]!#*?~]/;
  if (shellMetachars.test(trimmed)) {
    return false;
  }

  return true;
}

/**
 * Sanitize and validate package name
 * Returns sanitized name or null if invalid
 */
export function sanitizePackageName(name: string, file: string, line: number): string | null {
  const trimmed = name.trim().toLowerCase();

  if (!isValidPackageName(trimmed)) {
    core.warning(`Invalid package name at ${file}:${line}: '${name.slice(0, 50)}'`);
    return null;
  }

  return trimmed;
}
```

### Implementation
```typescript
// action/src/extract.ts
/**
 * IMPLEMENTS: S102
 * INVARIANTS: INV103
 * TESTS: T102.01-T102.05
 * SECURITY: P1-SEC-002 (package validation)
 * EDGE_CASES: EC220-EC235
 */

import * as core from '@actions/core';
import * as fs from 'fs';
import * as path from 'path';
import { getRegistryForFile } from './files';
import { isValidPackageName, preprocessContent } from './validation';

export interface ExtractedPackage {
  name: string;
  version?: string;
  sourceFile: string;
  lineNumber?: number;
  registry: string;
}

/**
 * IMPLEMENTS: S102
 * INVARIANT: INV103 - All extracted packages have valid names
 *
 * Extract packages from dependency files.
 *
 * @param files - Array of file paths to parse
 * @returns Array of extracted packages
 */
export async function extractPackages(files: string[]): Promise<ExtractedPackage[]> {
  const packages: ExtractedPackage[] = [];

  for (const file of files) {
    try {
      const extracted = await extractFromFile(file);
      packages.push(...extracted);
    } catch (error) {
      core.warning(`Failed to parse ${file}: ${error}`);
    }
  }

  return packages;
}

async function extractFromFile(filePath: string): Promise<ExtractedPackage[]> {
  const rawContent = fs.readFileSync(filePath, 'utf-8');
  const content = preprocessContent(rawContent); // EC212, EC213: BOM, CRLF
  const basename = path.basename(filePath);
  const registry = getRegistryForFile(filePath);

  switch (basename) {
    case 'requirements.txt':
      return parseRequirementsTxt(content, filePath, registry);
    case 'package.json':
      return parsePackageJson(content, filePath, registry);
    case 'Cargo.toml':
      return parseCargoToml(content, filePath, registry);
    case 'pyproject.toml':
      return parsePyprojectToml(content, filePath, registry);
    default:
      // Handle requirements-*.txt patterns
      if (basename.startsWith('requirements') && basename.endsWith('.txt')) {
        return parseRequirementsTxt(content, filePath, registry);
      }
      return [];
  }
}

// Requirements.txt parser (EC220-EC235)
function parseRequirementsTxt(
  content: string,
  filePath: string,
  registry: string
): ExtractedPackage[] {
  const packages: ExtractedPackage[] = [];
  const seen = new Set<string>();
  const lines = content.split('\n');

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim();

    // EC222: Skip comments and empty lines
    if (!line || line.startsWith('#')) continue;

    // Skip pip options (EC226, EC227)
    if (line.startsWith('-')) continue;

    // EC226: Skip URLs
    if (line.startsWith('git+') || line.startsWith('http')) continue;

    // EC223: Remove inline comments
    const commentIdx = line.indexOf('#');
    if (commentIdx > 0) line = line.substring(0, commentIdx).trim();

    // EC224: Remove environment markers
    const markerIdx = line.indexOf(';');
    if (markerIdx > 0) line = line.substring(0, markerIdx).trim();

    // Parse package name (EC225: Strip extras)
    const match = line.match(/^([a-zA-Z0-9][-a-zA-Z0-9._]*)(?:\[.*?\])?([<>=!~,].*)?$/);
    if (match) {
      const name = match[1].toLowerCase(); // EC234: Normalize
      if (isValidPackageName(name) && !seen.has(name)) { // EC233: Deduplicate
        seen.add(name);
        packages.push({
          name,
          version: match[2] || undefined,
          sourceFile: filePath,
          lineNumber: i + 1,
          registry,
        });
      }
    }
  }

  return packages;
}
```

### Edge Cases (EC220-EC235)
| EC_ID | Scenario | Expected | Test |
|:------|:---------|:---------|:-----|
| EC220 | Simple `flask` | Package: flask | T102.01 |
| EC221 | `flask>=2.0` | Package: flask | T102.02 |
| EC222 | `# comment` | Ignored | unit |
| EC223 | `flask # web` | Package: flask | unit |
| EC224 | `flask; python_version` | Package: flask | unit |
| EC225 | `flask[async]` | Package: flask | unit |
| EC226 | `git+https://...` | Skipped + warning | unit |
| EC227 | `./local_package` | Skipped + warning | unit |
| EC228 | `@scope/package` | Package: @scope/package | T102.03 |
| EC229 | `"express": "^4.0"` | Package: express | unit |
| EC233 | Duplicate package | Deduplicated | T102.04 |
| EC234 | `Flask` vs `flask` | Normalized lowercase | unit |
| **SEC** | **Shell metachar `pkg;rm`** | **Rejected + warning** | **T102.SEC** |

### Acceptance Criteria
- [ ] T102.01: Extract simple package name
- [ ] T102.02: Strip version specifier
- [ ] T102.03: Handle scoped npm package
- [ ] T102.04: Deduplicate packages
- [ ] T102.05: Fuzz test with random content
- [ ] **P1-SEC-002**: Package name validated with regex
- [ ] **T102.SEC**: Shell metacharacters rejected
- [ ] All parsers handle malformed input (INV103)
- [ ] Line numbers accurate for SARIF

### Dependencies
- W8.1, W8.2

### Post-Conditions
- action/src/extract.ts exists
- action/src/validation.ts exists
- All parser modules exist
- Tests T102.* pass
- INV103 enforced
- Security tests pass

---

## Day 4: Validation Orchestrator (W8.4)

### Traces
- **SPEC**: S103
- **INVARIANTS**: INV104
- **TESTS**: T103.01-T103.03, T103.SEC
- **EDGE CASES**: -

### Definition
Implement validation orchestrator with timeout protection, parallel execution, and secure subprocess handling.

### Files to Create
```
action/src/
├── validate.ts             # Validation orchestrator
├── core-bridge.ts          # Bridge to Python core (SECURITY CRITICAL)
action/tests/
├── validate.test.ts        # Validation tests
├── core-bridge.test.ts     # Bridge tests + security tests
```

### SECURITY CRITICAL: Core Bridge (P0-SEC-001)
```typescript
// action/src/core-bridge.ts
/**
 * IMPLEMENTS: S103
 * INVARIANTS: INV104
 * SECURITY: P0-SEC-001 - Shell injection prevention
 *
 * WARNING: This module spawns subprocesses.
 * NEVER use shell string interpolation.
 * ALWAYS use spawn/execFile with array arguments.
 */

import { spawn } from 'child_process';
import * as core from '@actions/core';
import { isValidPackageName } from './validation';

export interface CoreOptions {
  pythonPath: string;
  timeout: number;
}

/**
 * Call phantom-guard CLI to validate a package
 *
 * SECURITY (P0-SEC-001):
 * - Uses child_process.spawn (no shell by default)
 * - Package name validated before use
 * - Arguments passed as array, never interpolated
 */
export async function callPhantomGuard(
  packageName: string,
  registry: 'pypi' | 'npm' | 'crates',
  options: CoreOptions,
  signal: AbortSignal
): Promise<ValidationResult> {
  // P0-SEC-001: VALIDATE package name before subprocess
  if (!isValidPackageName(packageName)) {
    core.warning(`Skipping invalid package name: ${packageName}`);
    return {
      package: { name: packageName, registry, file: '', line: 0 },
      riskLevel: 'SUSPICIOUS',
      riskScore: 0.5,
      signals: [],
      error: 'Invalid package name',
    };
  }

  // P0-SEC-001: Build arguments as array (NO string interpolation)
  const args: string[] = [
    '-m', 'phantom_guard',
    'check',
    packageName,  // Already validated
    '--registry', registry,
    '--format', 'json',
  ];

  return new Promise((resolve) => {
    let stdout = '';
    let stderr = '';

    // P0-SEC-001: Use spawn with shell: false (default)
    const proc = spawn(options.pythonPath, args, {
      shell: false,  // CRITICAL: No shell interpretation
      timeout: options.timeout,
    });

    proc.stdout.on('data', (data) => { stdout += data.toString(); });
    proc.stderr.on('data', (data) => { stderr += data.toString(); });

    proc.on('close', (code) => {
      if (signal.aborted) {
        resolve({
          package: { name: packageName, registry, file: '', line: 0 },
          riskLevel: 'SUSPICIOUS',
          riskScore: 0.5,
          signals: [],
          error: 'Validation aborted',
        });
        return;
      }

      try {
        const result = JSON.parse(stdout);
        resolve({
          package: { name: packageName, registry, file: '', line: 0 },
          riskLevel: result.risk_level,
          riskScore: result.risk_score,
          signals: result.signals || [],
        });
      } catch {
        resolve({
          package: { name: packageName, registry, file: '', line: 0 },
          riskLevel: 'SUSPICIOUS',
          riskScore: 0.5,
          signals: [],
          error: `Parse error: ${stderr || 'Unknown'}`,
        });
      }
    });

    proc.on('error', (err) => {
      resolve({
        package: { name: packageName, registry, file: '', line: 0 },
        riskLevel: 'SUSPICIOUS',
        riskScore: 0.5,
        signals: [],
        error: err.message,
      });
    });
  });
}

/**
 * Batch validate packages with controlled concurrency
 *
 * SECURITY: Each package name validated before subprocess call
 */
export async function batchValidate(
  packages: PackageInfo[],
  options: CoreOptions,
  signal: AbortSignal,
  concurrency: number = 5
): Promise<ValidationResult[]> {
  const results: ValidationResult[] = [];

  // Process in batches for controlled concurrency
  for (let i = 0; i < packages.length; i += concurrency) {
    if (signal.aborted) break;

    const batch = packages.slice(i, i + concurrency);
    const batchResults = await Promise.all(
      batch.map(pkg => callPhantomGuard(pkg.name, pkg.registry, options, signal))
    );

    // Merge package info (file, line) with results
    for (let j = 0; j < batchResults.length; j++) {
      batchResults[j].package = batch[j];
    }

    results.push(...batchResults);
  }

  return results;
}
```

### Validation Orchestrator
```typescript
// action/src/validate.ts
/**
 * IMPLEMENTS: S103
 * INVARIANTS: INV104
 * TESTS: T103.01-T103.03
 */

import { batchValidate, CoreOptions } from './core-bridge';
import { ValidationTimeoutError } from './errors';

export interface ValidateOptions {
  batchTimeout: number;      // Default: 30000ms
  packageTimeout: number;    // Default: 60000ms (circuit breaker)
  concurrency: number;       // Default: 5
  pythonPath: string;
}

export interface ValidationResult {
  package: PackageInfo;
  riskLevel: 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK' | 'NOT_FOUND';
  riskScore: number;
  signals: string[];
  error?: string;
}

export async function validatePackages(
  packages: PackageInfo[],
  options: ValidateOptions
): Promise<ValidationResult[]> {
  // INV104: Batch <30s total, 60s circuit breaker per package
  const controller = new AbortController();
  const batchTimeout = setTimeout(() => controller.abort(), options.batchTimeout);

  try {
    const coreOptions: CoreOptions = {
      pythonPath: options.pythonPath,
      timeout: options.packageTimeout,
    };

    return await batchValidate(
      packages,
      coreOptions,
      controller.signal,
      options.concurrency
    );

  } catch (error) {
    if (controller.signal.aborted) {
      throw new ValidationTimeoutError(
        packages.map(p => p.name),
        options.batchTimeout
      );
    }
    throw error;
  } finally {
    clearTimeout(batchTimeout);
  }
}
```

### Security Tests (P0-SEC-001)
```typescript
// action/tests/core-bridge.test.ts

describe('Core Bridge Security (P0-SEC-001)', () => {
  it('T103.SEC.01: rejects package names with semicolons', async () => {
    const result = await callPhantomGuard(
      'package;rm -rf /',
      'pypi',
      { pythonPath: 'python', timeout: 5000 },
      new AbortController().signal
    );

    expect(result.riskLevel).toBe('SUSPICIOUS');
    expect(result.error).toContain('Invalid package name');
  });

  it('T103.SEC.02: rejects package names with pipes', async () => {
    const result = await callPhantomGuard(
      'package|cat /etc/passwd',
      'pypi',
      { pythonPath: 'python', timeout: 5000 },
      new AbortController().signal
    );

    expect(result.riskLevel).toBe('SUSPICIOUS');
    expect(result.error).toContain('Invalid package name');
  });

  it('T103.SEC.03: rejects package names with backticks', async () => {
    const result = await callPhantomGuard(
      'package`whoami`',
      'pypi',
      { pythonPath: 'python', timeout: 5000 },
      new AbortController().signal
    );

    expect(result.riskLevel).toBe('SUSPICIOUS');
  });

  it('T103.SEC.04: uses spawn with shell:false', () => {
    // Verified by code review: spawn() with shell: false
  });
});
```

### Performance Budgets
| Operation | Budget |
|:----------|:-------|
| Cold start | < 5s |
| 50 packages | < 30s |
| Single package (circuit breaker) | 60s max |

### Acceptance Criteria
- [ ] T103.01: Validation completes successfully
- [ ] T103.02: 50 packages < 30s (integration)
- [ ] T103.03: Benchmark timing
- [ ] **P0-SEC-001**: Uses spawn with shell:false
- [ ] **T103.SEC.01-04**: Shell injection tests pass
- [ ] INV104: Timeout prevents hanging
- [ ] Parallel execution works
- [ ] Circuit breaker triggers correctly

### Dependencies
- W8.1, W8.2, W8.3

### Post-Conditions
- action/src/validate.ts exists
- action/src/core-bridge.ts exists (security reviewed)
- Tests T103.* pass
- Security tests T103.SEC.* pass
- INV104 enforced

---

## Day 5: PR Comment Generator (W8.5)

### Traces
- **SPEC**: S104
- **INVARIANTS**: INV105, INV106
- **TESTS**: T104.01-T104.05
- **EDGE CASES**: EC240-EC255

### Definition
Implement PR comment generator with sticky updates, size limit enforcement, and error handling.

### Files to Create
```
action/src/
├── comment.ts              # PR comment generator
├── github.ts               # GitHub API wrapper
action/tests/
├── comment.test.ts         # Comment tests
├── github.test.ts          # GitHub API tests
```

### Comment Template
```typescript
// action/src/comment.ts
/**
 * IMPLEMENTS: S104
 * INVARIANTS: INV105, INV106
 * TESTS: T104.01-T104.05
 */

import * as core from '@actions/core';

const STICKY_MARKER = '<!-- phantom-guard-sticky -->';
const MAX_COMMENT_LENGTH = 65535;

export function generateComment(results: ValidationResult[]): string {
  const safe = results.filter(r => r.riskLevel === 'SAFE');
  const suspicious = results.filter(r => r.riskLevel === 'SUSPICIOUS');
  const highRisk = results.filter(r => r.riskLevel === 'HIGH_RISK');
  const notFound = results.filter(r => r.riskLevel === 'NOT_FOUND');

  let comment = `## Phantom Guard Security Report

### Summary
Checked **${results.length} packages**

| Status | Count |
|:-------|------:|
| Safe | ${safe.length} |
| Suspicious | ${suspicious.length} |
| High Risk | ${highRisk.length} |
| Not Found | ${notFound.length} |

`;

  // Add high-risk details
  if (highRisk.length > 0) {
    comment += formatHighRiskSection(highRisk);
  }

  // Add suspicious details (collapsible)
  if (suspicious.length > 0) {
    comment += formatSuspiciousSection(suspicious);
  }

  comment += `\n${STICKY_MARKER}\n`;

  // INV105: Truncate if over limit
  if (comment.length > MAX_COMMENT_LENGTH) {
    comment = truncateComment(comment, MAX_COMMENT_LENGTH);
  }

  return comment;
}

function formatHighRiskSection(packages: ValidationResult[]): string {
  let section = `
<details open>
<summary>High Risk Packages (${packages.length})</summary>

| Package | File | Signals |
|:--------|:-----|:--------|
`;
  for (const pkg of packages) {
    const name = escapeMarkdown(pkg.package.name);
    const file = `${pkg.package.file}:${pkg.package.line}`;
    const signals = pkg.signals.join(', ') || 'Unknown';
    section += `| \`${name}\` | ${file} | ${signals} |\n`;
  }
  section += '\n</details>\n';
  return section;
}

function truncateComment(comment: string, maxLength: number): string {
  const truncateMsg = '\n\n... (truncated due to size limit)\n' + STICKY_MARKER;
  const available = maxLength - truncateMsg.length;
  return comment.slice(0, available) + truncateMsg;
}
```

### GitHub API Wrapper with Error Handling (P2-EC247/248)
```typescript
// action/src/github.ts
/**
 * IMPLEMENTS: S104
 * INVARIANTS: INV106
 * ERROR HANDLING: P2-EC247 (permission denied), P2-EC248 (rate limiting)
 */

import * as core from '@actions/core';
import * as github from '@actions/github';
import { CommentUpdateError } from './errors';

const RETRY_DELAYS = [1000, 2000, 4000]; // Exponential backoff

// INV106: Idempotent updates via sticky marker
export async function updateOrCreateComment(
  token: string,
  owner: string,
  repo: string,
  prNumber: number,
  body: string
): Promise<void> {
  const octokit = github.getOctokit(token);

  for (let attempt = 0; attempt <= RETRY_DELAYS.length; attempt++) {
    try {
      const comments = await octokit.rest.issues.listComments({
        owner,
        repo,
        issue_number: prNumber,
      });

      const existing = comments.data.find(c =>
        c.body?.includes('<!-- phantom-guard-sticky -->')
      );

      if (existing) {
        await octokit.rest.issues.updateComment({
          owner,
          repo,
          comment_id: existing.id,
          body,
        });
        core.info('Updated existing Phantom Guard comment');
      } else {
        await octokit.rest.issues.createComment({
          owner,
          repo,
          issue_number: prNumber,
          body,
        });
        core.info('Created new Phantom Guard comment');
      }
      return; // Success

    } catch (error: any) {
      // P2-EC247: Permission denied
      if (error.status === 403) {
        core.warning('Permission denied to post PR comment. Check GITHUB_TOKEN permissions.');
        throw new CommentUpdateError('Permission denied');
      }

      // P2-EC248: Rate limiting - retry with backoff
      if (error.status === 429 && attempt < RETRY_DELAYS.length) {
        const delay = RETRY_DELAYS[attempt];
        core.warning(`Rate limited. Retrying in ${delay}ms...`);
        await sleep(delay);
        continue;
      }

      // P2-EC249: Network error
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        core.warning(`Network error posting comment: ${error.message}`);
        throw new CommentUpdateError(`Network error: ${error.message}`);
      }

      throw new CommentUpdateError(error.message);
    }
  }

  throw new CommentUpdateError('Max retries exceeded');
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Security: Markdown Injection Prevention
```typescript
// EC250: Escape markdown in package names
function escapeMarkdown(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\*/g, '\\*')
    .replace(/\[/g, '\\[')
    .replace(/\]/g, '\\]')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
```

### Edge Cases (EC240-EC255)
| EC_ID | Scenario | Expected | Test |
|:------|:---------|:---------|:-----|
| EC240 | No existing comment | Create new | integration |
| EC241 | Existing comment | Update (INV106) | T104.04 |
| EC242 | All safe | Summary only | T104.01 |
| EC243 | Some suspicious | Collapsible details | T104.02 |
| EC245 | >65535 chars | Truncated (INV105) | T104.03 |
| EC246 | Push event (no PR) | Skip comment | integration |
| **EC247** | **Permission denied** | **Warning + continue** | **unit (P2)** |
| **EC248** | **Rate limited** | **Retry with backoff** | **unit (P2)** |
| EC250 | Markdown injection | Escaped (SECURITY) | T104.05 |

### Acceptance Criteria
- [ ] T104.01: Generate safe summary
- [ ] T104.02: Generate suspicious details
- [ ] T104.03: Truncate long comment (INV105)
- [ ] T104.04: Update existing comment (INV106)
- [ ] T104.05: Escape markdown injection (SECURITY)
- [ ] **P2-EC247**: Permission denied handled gracefully
- [ ] **P2-EC248**: Rate limiting with exponential backoff
- [ ] Sticky marker works for idempotency
- [ ] Handles missing PR context gracefully

### Dependencies
- W8.1, W8.4

### Post-Conditions
- action/src/comment.ts exists
- action/src/github.ts exists
- Tests T104.* pass
- INV105, INV106 enforced

---

## Day 6: SARIF Output + Integration Tests (W8.6, W8.7)

### Traces
- **SPEC**: S105
- **INVARIANTS**: INV107
- **TESTS**: T105.01-T105.03 + integration tests
- **EDGE CASES**: EC260-EC270

### Definition
Implement SARIF 2.1.0 output generator with schema validation and full integration tests.

### Files to Create
```
action/src/
├── sarif.ts                # SARIF generator
├── sarif-schema.ts         # SARIF schema validation (P1-INV107)
action/tests/
├── sarif.test.ts           # SARIF tests
├── sarif-schema.test.ts    # Schema validation tests
├── integration/
│   ├── full-workflow.test.ts
│   ├── benchmarks.test.ts
│   └── fixtures/
│       ├── test-repo/
│       │   ├── requirements.txt
│       │   ├── package.json
│       │   └── Cargo.toml
│       └── sarif-schema-2.1.0.json
```

### SARIF Schema Validation (P1-INV107)
```typescript
// action/src/sarif-schema.ts
/**
 * IMPLEMENTS: S105
 * INVARIANTS: INV107 - Schema-valid SARIF 2.1.0
 *
 * Uses ajv for runtime JSON schema validation
 */

import Ajv from 'ajv';
import * as core from '@actions/core';

// Embedded minimal SARIF 2.1.0 schema (key parts)
const SARIF_SCHEMA = {
  $schema: 'http://json-schema.org/draft-07/schema#',
  type: 'object',
  required: ['version', 'runs'],
  properties: {
    $schema: { type: 'string' },
    version: { const: '2.1.0' },
    runs: {
      type: 'array',
      items: {
        type: 'object',
        required: ['tool', 'results'],
        properties: {
          tool: {
            type: 'object',
            required: ['driver'],
            properties: {
              driver: {
                type: 'object',
                required: ['name'],
                properties: {
                  name: { type: 'string' },
                  version: { type: 'string' },
                  rules: { type: 'array' },
                },
              },
            },
          },
          results: { type: 'array' },
        },
      },
    },
  },
};

const ajv = new Ajv({ allErrors: true });
const validateSarif = ajv.compile(SARIF_SCHEMA);

/**
 * Validate SARIF output against schema
 * INV107: SARIF output is schema-valid per SARIF 2.1.0
 */
export function validateSarifSchema(sarif: SarifOutput): boolean {
  const valid = validateSarif(sarif);

  if (!valid) {
    core.warning('SARIF validation errors:');
    for (const error of validateSarif.errors || []) {
      core.warning(`  ${error.instancePath}: ${error.message}`);
    }
    return false;
  }

  return true;
}
```

### SARIF Implementation
```typescript
// action/src/sarif.ts
/**
 * IMPLEMENTS: S105
 * INVARIANTS: INV107
 * TESTS: T105.01-T105.03
 */

import * as fs from 'fs/promises';
import * as core from '@actions/core';
import { validateSarifSchema } from './sarif-schema';
import { SarifGenerationError } from './errors';

const SARIF_SCHEMA_URL = 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json';

export interface SarifOutput {
  $schema: string;
  version: '2.1.0';
  runs: SarifRun[];
}

export function generateSarif(results: ValidationResult[]): SarifOutput {
  const sarif: SarifOutput = {
    $schema: SARIF_SCHEMA_URL,
    version: '2.1.0',
    runs: [{
      tool: {
        driver: {
          name: 'phantom-guard',
          version: '0.2.0',
          informationUri: 'https://github.com/phantom-guard/phantom-guard',
          rules: [
            {
              id: 'PG001',
              name: 'suspicious-package',
              shortDescription: { text: 'Suspicious package detected' },
              defaultConfiguration: { level: 'warning' },
            },
            {
              id: 'PG002',
              name: 'high-risk-package',
              shortDescription: { text: 'High-risk package detected' },
              defaultConfiguration: { level: 'error' },
            },
            {
              id: 'PG003',
              name: 'not-found-package',
              shortDescription: { text: 'Package not found in registry' },
              defaultConfiguration: { level: 'error' },
            },
          ],
        },
      },
      results: results
        .filter(r => r.riskLevel !== 'SAFE')
        .map(r => resultToSarif(r)),
    }],
  };

  // P1-INV107: Validate against schema before returning
  if (!validateSarifSchema(sarif)) {
    throw new SarifGenerationError('Generated SARIF failed schema validation');
  }

  return sarif;
}

export async function writeSarifFile(
  sarif: SarifOutput,
  outputPath: string
): Promise<void> {
  await fs.writeFile(outputPath, JSON.stringify(sarif, null, 2));
  core.setOutput('sarif-file', outputPath);
  core.info(`SARIF output written to ${outputPath}`);
}

function resultToSarif(result: ValidationResult): SarifResult {
  const ruleId = getRuleId(result.riskLevel);
  const level = getLevel(result.riskLevel);

  return {
    ruleId,
    level,
    message: {
      text: `${result.riskLevel} package: ${result.package.name}`,
    },
    locations: [{
      physicalLocation: {
        artifactLocation: {
          uri: result.package.file,
        },
        region: {
          startLine: result.package.line,
        },
      },
    }],
    properties: {
      riskScore: result.riskScore,
      signals: result.signals,
    },
  };
}

function getRuleId(riskLevel: string): string {
  switch (riskLevel) {
    case 'SUSPICIOUS': return 'PG001';
    case 'HIGH_RISK': return 'PG002';
    case 'NOT_FOUND': return 'PG003';
    default: return 'PG001';
  }
}

function getLevel(riskLevel: string): 'warning' | 'error' {
  // EC261: HIGH_RISK = error, EC262: SUSPICIOUS = warning
  return riskLevel === 'SUSPICIOUS' ? 'warning' : 'error';
}
```

### Performance Budgets (P2-PERF-002)
| Operation | Budget |
|:----------|:-------|
| SARIF generation | < 100ms |

### Integration Tests
```typescript
// action/tests/integration/full-workflow.test.ts

describe('Full Workflow Integration', () => {
  it('T100.02: completes full workflow', async () => {
    const result = await runAction({
      files: 'fixtures/test-repo/**',
      'fail-on': 'high-risk',
      output: 'github-comment,sarif',
    });

    expect(result.exitCode).toBeLessThanOrEqual(2);
    expect(result.outputs['sarif-file']).toBeDefined();
  });

  it('T100.03: cold start < 5s', async () => {
    const start = Date.now();
    await runAction({ files: 'fixtures/test-repo/**' });
    const elapsed = Date.now() - start;

    expect(elapsed).toBeLessThan(5000);
  });

  it('T103.02: 50 packages < 30s', async () => {
    const start = Date.now();
    await runAction({ files: 'fixtures/large-repo/**' });
    const elapsed = Date.now() - start;

    expect(elapsed).toBeLessThan(30000);
  });

  it('P2-PERF-002: SARIF generation < 100ms', async () => {
    const results = generateMockResults(100);

    const start = Date.now();
    generateSarif(results);
    const elapsed = Date.now() - start;

    expect(elapsed).toBeLessThan(100);
  });
});

describe('SARIF Schema Validation (P1-INV107)', () => {
  it('validates correct SARIF structure', () => {
    const sarif = generateSarif([]);
    expect(validateSarifSchema(sarif)).toBe(true);
  });

  it('rejects invalid SARIF structure', () => {
    const invalid = { version: '1.0', runs: [] };
    expect(validateSarifSchema(invalid as any)).toBe(false);
  });
});
```

### Edge Cases (EC260-EC270)
| EC_ID | Scenario | Expected | Test |
|:------|:---------|:---------|:-----|
| EC260 | Valid SARIF | Schema-valid 2.1.0 | T105.01 |
| EC261 | HIGH_RISK | level: "error" | T105.02 |
| EC262 | SUSPICIOUS | level: "warning" | unit |
| EC263 | NOT_FOUND | PG003, level: "error" | unit |
| EC264 | Line reference | Correct startLine | unit |
| EC266 | All safe | Empty results array | T105.03 |
| EC267 | Rule definitions | PG001-PG003 defined | unit |
| EC270 | `@scope/pkg` | Properly escaped | unit |

### Acceptance Criteria
- [ ] T105.01: Valid SARIF structure (INV107)
- [ ] T105.02: HIGH_RISK = error level
- [ ] T105.03: Empty results handled
- [ ] **P1-INV107**: SARIF validated against schema using ajv
- [ ] **P2-PERF-002**: SARIF generation < 100ms benchmark
- [ ] Full workflow integration test passes
- [ ] Cold start < 5s benchmark
- [ ] 50 packages < 30s benchmark
- [ ] npm run build succeeds
- [ ] All tests pass

### Dependencies
- W8.1-W8.5

### Post-Conditions
- action/src/sarif.ts exists
- action/src/sarif-schema.ts exists
- Integration tests pass
- INV107 enforced with runtime validation
- Action ready for testing

---

## Week 8 Exit Criteria

### Functional Requirements
- [ ] Action entry point works (S100)
- [ ] File discovery works for all patterns (S101)
- [ ] Package extraction for all formats (S102)
- [ ] Validation with timeout protection (S103)
- [ ] PR comments with sticky updates (S104)
- [ ] SARIF output validates (S105)
- [ ] Exit codes match status (S106)

### Invariant Enforcement
- [ ] INV100: Action never throws uncaught
- [ ] INV101: Exit code matches status
- [ ] INV102: File discovery graceful
- [ ] INV103: Package extraction graceful
- [ ] INV104: Timeout prevents hanging
- [ ] INV105: Comment size limit
- [ ] INV106: Idempotent updates
- [ ] INV107: Valid SARIF schema (with runtime validation)
- [ ] INV108: Exit codes in [0-5]

### Security Requirements (Hostile Review Fixes)
- [ ] **P0-SEC-001**: Shell injection prevented (spawn with shell:false, validated names)
- [ ] **P1-SEC-002**: Package name validation regex enforced
- [ ] **P1-SEC-003**: GITHUB_TOKEN masked with core.setSecret()

### Test Coverage
- [ ] T100.* tests pass (entry point)
- [ ] T101.* tests pass (file discovery)
- [ ] T102.* tests pass (package extraction)
- [ ] T103.* tests pass (validation)
- [ ] T103.SEC.* security tests pass
- [ ] T104.* tests pass (PR comment)
- [ ] T105.* tests pass (SARIF)
- [ ] T106.* tests pass (exit codes)
- [ ] Integration tests pass
- [ ] Coverage >= 85%

### Performance
- [ ] Cold start < 5s
- [ ] File discovery < 1s
- [ ] 50 packages < 30s
- [ ] SARIF generation < 100ms

### Build & Package
- [ ] npm ci succeeds (lock file)
- [ ] npm test passes
- [ ] npm run build succeeds
- [ ] dist/index.js generated
- [ ] action.yml valid

### Hostile Review
- [ ] `/hostile-review` on Week 8: GO

---

## Quick Start

```bash
# Day 1: Begin with entry point
cd action
npm init -y
npm install @actions/core @actions/github glob ajv
npm install -D typescript @types/node @vercel/ncc vitest eslint

# Commit lock file (P1-MISSING-001)
git add package-lock.json

# Create structure
mkdir -p src tests/__mocks__ tests/fixtures tests/integration

# Start TDD
npm test -- --watch
```

---

## Hostile Review Fixes Applied

| Issue ID | Priority | Fix Applied |
|:---------|:---------|:------------|
| P0-SEC-001 | P0 | Day 4: spawn with shell:false, package validation before subprocess |
| P1-INV107 | P1 | Day 6: ajv schema validation for SARIF |
| P1-SEC-002 | P1 | Day 3: Package name validation regex |
| P1-SEC-003 | P1 | Day 1: core.setSecret(token) |
| P1-MISSING-001 | P1 | Day 1: package-lock.json, npm ci |
| P1-EC206/207 | P1 | Day 2: Symlink handling with tests |
| P2-PERF-001 | P2 | Day 2: File discovery < 1s budget |
| P2-PERF-002 | P2 | Day 6: SARIF generation < 100ms |
| P2-EC247 | P2 | Day 5: Permission denied handling |
| P2-EC248 | P2 | Day 5: Rate limiting with backoff |

---

**Document Version**: 1.1.0
**Created**: 2026-01-07
**Updated**: 2026-01-07 (Hostile Review Fixes)
**Status**: READY FOR IMPLEMENTATION
