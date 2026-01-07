/**
 * IMPLEMENTS: S103
 * INVARIANTS: INV104
 * TESTS: T103.01-T103.03
 * SECURITY: P0-SEC-001 (no shell execution - pattern-based validation)
 *
 * Package validation orchestrator for Phantom Guard GitHub Action.
 *
 * Uses built-in validation patterns - no shell execution required.
 * This avoids any command injection risks entirely by design.
 *
 * Security approach:
 * - All validation is done in-process using TypeScript regex patterns
 * - No subprocess calls, no shell execution, no command injection risk
 * - Package names were already validated by isValidPackageName()
 */

import * as core from '@actions/core';
import { ExtractedPackage } from './extract';

/**
 * Risk level for a package.
 */
export type RiskLevel = 'safe' | 'suspicious' | 'high-risk';

/**
 * Validation result for a package.
 */
export interface ValidationResult {
  /** Package name */
  package: string;
  /** Risk level (safe, suspicious, high-risk) */
  riskLevel: RiskLevel;
  /** Risk score (0.0 - 1.0) */
  riskScore: number;
  /** Detection signals that fired */
  signals: string[];
  /** Source file */
  sourceFile: string;
  /** Line number in source */
  lineNumber?: number;
  /** Error message if validation failed */
  error?: string;
  /** Registry type */
  registry: string;
}

/**
 * Hallucination detection patterns.
 * These are common patterns found in AI-generated package names.
 */
const HALLUCINATION_PATTERNS: Array<{
  pattern: RegExp;
  signal: string;
  score: number;
  description: string;
}> = [
  // AI model names in packages
  { pattern: /gpt/i, signal: 'AI_MODEL_NAME', score: 0.4, description: 'Contains GPT reference' },
  { pattern: /claude/i, signal: 'AI_MODEL_NAME', score: 0.4, description: 'Contains Claude reference' },
  { pattern: /llama/i, signal: 'AI_MODEL_NAME', score: 0.3, description: 'Contains LLaMA reference' },
  { pattern: /gemini/i, signal: 'AI_MODEL_NAME', score: 0.3, description: 'Contains Gemini reference' },

  // Suspicious prefixes
  { pattern: /^easy-/i, signal: 'SUSPICIOUS_PREFIX', score: 0.15, description: 'Starts with easy-' },
  { pattern: /^simple-/i, signal: 'SUSPICIOUS_PREFIX', score: 0.15, description: 'Starts with simple-' },
  { pattern: /^auto-/i, signal: 'SUSPICIOUS_PREFIX', score: 0.15, description: 'Starts with auto-' },
  { pattern: /^quick-/i, signal: 'SUSPICIOUS_PREFIX', score: 0.15, description: 'Starts with quick-' },
  { pattern: /^smart-/i, signal: 'SUSPICIOUS_PREFIX', score: 0.15, description: 'Starts with smart-' },
  { pattern: /^py-?openai/i, signal: 'SUSPICIOUS_PREFIX', score: 0.35, description: 'Looks like OpenAI typosquat' },

  // Suspicious suffixes
  { pattern: /-helper$/i, signal: 'SUSPICIOUS_SUFFIX', score: 0.15, description: 'Ends with -helper' },
  { pattern: /-wrapper$/i, signal: 'SUSPICIOUS_SUFFIX', score: 0.15, description: 'Ends with -wrapper' },
  { pattern: /-utils$/i, signal: 'SUSPICIOUS_SUFFIX', score: 0.15, description: 'Ends with -utils' },
  { pattern: /-api$/i, signal: 'SUSPICIOUS_SUFFIX', score: 0.1, description: 'Ends with -api' },
  { pattern: /-sdk$/i, signal: 'SUSPICIOUS_SUFFIX', score: 0.1, description: 'Ends with -sdk' },

  // Combined patterns (higher risk)
  { pattern: /flask.*gpt/i, signal: 'HALLUCINATION_COMBO', score: 0.5, description: 'Flask + GPT combination' },
  { pattern: /django.*gpt/i, signal: 'HALLUCINATION_COMBO', score: 0.5, description: 'Django + GPT combination' },
  { pattern: /react.*gpt/i, signal: 'HALLUCINATION_COMBO', score: 0.5, description: 'React + GPT combination' },
  { pattern: /express.*gpt/i, signal: 'HALLUCINATION_COMBO', score: 0.5, description: 'Express + GPT combination' },

  // Namespace squatting patterns
  { pattern: /^@[a-z]+-fake\//i, signal: 'NAMESPACE_SQUAT', score: 0.6, description: 'Suspicious npm scope' },
  { pattern: /google-.*-fake/i, signal: 'NAMESPACE_SQUAT', score: 0.5, description: 'Google typosquat' },
  { pattern: /microsoft-.*-fake/i, signal: 'NAMESPACE_SQUAT', score: 0.5, description: 'Microsoft typosquat' },
];

/**
 * Known safe packages that should never be flagged.
 */
const KNOWN_SAFE_PACKAGES = new Set([
  // Python
  'flask', 'django', 'requests', 'numpy', 'pandas', 'scipy', 'matplotlib',
  'pytorch', 'tensorflow', 'keras', 'openai', 'anthropic', 'langchain',
  // npm
  'react', 'vue', 'angular', 'express', 'lodash', 'axios', 'typescript',
  // crates
  'serde', 'tokio', 'reqwest', 'clap', 'rand',
]);

/**
 * IMPLEMENTS: S103
 * INVARIANT: INV104 - All packages are validated or have error status
 *
 * Validate packages using built-in pattern matching.
 * No shell execution - all validation is done in-process.
 *
 * @param packages - Packages to validate
 * @returns Validation results for all packages
 */
export async function validatePackages(
  packages: ExtractedPackage[]
): Promise<ValidationResult[]> {
  const results: ValidationResult[] = [];

  core.info(`Validating ${packages.length} packages using built-in patterns`);

  for (const pkg of packages) {
    try {
      const result = validatePackage(pkg);
      results.push(result);

      // Log progress
      if (result.riskLevel !== 'safe') {
        core.warning(`${result.riskLevel.toUpperCase()}: ${pkg.name} (score: ${result.riskScore.toFixed(2)})`);
      } else {
        core.debug(`SAFE: ${pkg.name}`);
      }
    } catch (error) {
      // INV104: All packages get a result, even on error
      results.push({
        package: pkg.name,
        riskLevel: 'safe', // Default to safe on error
        riskScore: 0,
        signals: [],
        sourceFile: pkg.sourceFile,
        lineNumber: pkg.lineNumber,
        error: error instanceof Error ? error.message : String(error),
        registry: pkg.registry,
      });
    }
  }

  return results;
}

/**
 * Validate a single package using pattern matching.
 */
function validatePackage(pkg: ExtractedPackage): ValidationResult {
  // Check if known safe package
  if (KNOWN_SAFE_PACKAGES.has(pkg.name.toLowerCase())) {
    return {
      package: pkg.name,
      riskLevel: 'safe',
      riskScore: 0,
      signals: [],
      sourceFile: pkg.sourceFile,
      lineNumber: pkg.lineNumber,
      registry: pkg.registry,
    };
  }

  const signals: string[] = [];
  let riskScore = 0;

  // Check against all patterns
  for (const { pattern, signal, score } of HALLUCINATION_PATTERNS) {
    if (pattern.test(pkg.name)) {
      if (!signals.includes(signal)) {
        signals.push(signal);
      }
      riskScore += score;
    }
  }

  // Cap risk score at 1.0
  riskScore = Math.min(riskScore, 1.0);

  return {
    package: pkg.name,
    riskLevel: scoreToRiskLevel(riskScore),
    riskScore,
    signals,
    sourceFile: pkg.sourceFile,
    lineNumber: pkg.lineNumber,
    registry: pkg.registry,
  };
}

/**
 * Convert risk score to risk level.
 */
function scoreToRiskLevel(score: number): RiskLevel {
  if (score >= 0.7) {
    return 'high-risk';
  }
  if (score >= 0.3) {
    return 'suspicious';
  }
  return 'safe';
}
