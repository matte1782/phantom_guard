/**
 * IMPLEMENTS: S105
 * INVARIANTS: INV107
 * TESTS: T105.01-T105.03
 *
 * SARIF output generation for Phantom Guard GitHub Action.
 *
 * Generates SARIF (Static Analysis Results Interchange Format) output
 * for integration with GitHub Code Scanning.
 */

import * as core from '@actions/core';
import * as fs from 'fs';
import * as path from 'path';
import { ValidationResult } from './validate';

/**
 * SARIF schema version.
 */
const SARIF_VERSION = '2.1.0';

/**
 * SARIF schema URL.
 */
const SARIF_SCHEMA =
  'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json';

/**
 * SARIF rule metadata.
 */
interface SarifRule {
  id: string;
  name: string;
  shortDescription: { text: string };
  fullDescription: { text: string };
  helpUri: string;
  defaultConfiguration: {
    level: 'error' | 'warning' | 'note';
  };
}

/**
 * Map signals to SARIF rule IDs.
 */
const SIGNAL_TO_RULE: Record<string, SarifRule> = {
  AI_MODEL_NAME: {
    id: 'PG001',
    name: 'AI Model Name Detected',
    shortDescription: { text: 'Package name contains AI model reference' },
    fullDescription: {
      text: 'The package name contains a reference to an AI model (GPT, Claude, etc.), which is a common pattern in AI-hallucinated package names.',
    },
    helpUri: 'https://github.com/phantom-guard/phantom-guard/wiki/AI-Model-Names',
    defaultConfiguration: { level: 'error' },
  },
  HALLUCINATION_COMBO: {
    id: 'PG002',
    name: 'Hallucination Pattern Combination',
    shortDescription: { text: 'Package name matches hallucination pattern' },
    fullDescription: {
      text: 'The package name combines a well-known framework with an AI-related term, which is a strong indicator of a hallucinated package.',
    },
    helpUri: 'https://github.com/phantom-guard/phantom-guard/wiki/Hallucination-Patterns',
    defaultConfiguration: { level: 'error' },
  },
  NAMESPACE_SQUAT: {
    id: 'PG003',
    name: 'Namespace Squatting Detected',
    shortDescription: { text: 'Suspicious namespace or prefix detected' },
    fullDescription: {
      text: 'The package uses a namespace or prefix that mimics a well-known organization without verified ownership.',
    },
    helpUri: 'https://github.com/phantom-guard/phantom-guard/wiki/Namespace-Squatting',
    defaultConfiguration: { level: 'error' },
  },
  SUSPICIOUS_PREFIX: {
    id: 'PG004',
    name: 'Suspicious Prefix',
    shortDescription: { text: 'Package has suspicious prefix' },
    fullDescription: {
      text: 'The package name starts with a prefix commonly used in hallucinated package names (easy-, simple-, auto-, etc.).',
    },
    helpUri: 'https://github.com/phantom-guard/phantom-guard/wiki/Suspicious-Prefixes',
    defaultConfiguration: { level: 'warning' },
  },
  SUSPICIOUS_SUFFIX: {
    id: 'PG005',
    name: 'Suspicious Suffix',
    shortDescription: { text: 'Package has suspicious suffix' },
    fullDescription: {
      text: 'The package name ends with a suffix commonly used in hallucinated package names (-helper, -wrapper, -utils, etc.).',
    },
    helpUri: 'https://github.com/phantom-guard/phantom-guard/wiki/Suspicious-Suffixes',
    defaultConfiguration: { level: 'warning' },
  },
};

/**
 * Default rule for unknown signals.
 */
const DEFAULT_RULE: SarifRule = {
  id: 'PG999',
  name: 'Unknown Signal',
  shortDescription: { text: 'Unknown detection signal' },
  fullDescription: { text: 'An unknown detection signal was triggered.' },
  helpUri: 'https://github.com/phantom-guard/phantom-guard',
  defaultConfiguration: { level: 'note' },
};

/**
 * IMPLEMENTS: S105
 * INVARIANT: INV107 - SARIF output validates against schema
 *
 * Generate SARIF output file for GitHub Code Scanning.
 *
 * @param results - Validation results for all packages
 */
export async function generateSARIF(results: ValidationResult[]): Promise<void> {
  // Filter to only packages with issues
  const issues = results.filter((r) => r.riskLevel !== 'safe');

  if (issues.length === 0) {
    core.info('No issues found, SARIF output will be empty');
  }

  // Collect all unique rules used
  const usedRules = new Set<string>();
  for (const result of issues) {
    for (const signal of result.signals) {
      usedRules.add(signal);
    }
  }

  // Build rules array
  const rules: SarifRule[] = [];
  for (const signal of usedRules) {
    rules.push(SIGNAL_TO_RULE[signal] || { ...DEFAULT_RULE, id: `PG-${signal}` });
  }

  // Build results array
  const sarifResults = issues.map((result) => buildSarifResult(result));

  // Build complete SARIF document
  const sarif = {
    $schema: SARIF_SCHEMA,
    version: SARIF_VERSION,
    runs: [
      {
        tool: {
          driver: {
            name: 'Phantom Guard',
            version: '0.2.0',
            informationUri: 'https://github.com/phantom-guard/phantom-guard',
            rules,
          },
        },
        results: sarifResults,
      },
    ],
  };

  // Write SARIF file
  const outputPath = path.join(process.cwd(), 'phantom-guard-results.sarif');
  fs.writeFileSync(outputPath, JSON.stringify(sarif, null, 2));
  core.info(`SARIF output written to: ${outputPath}`);

  // Set output for upload-sarif action
  core.setOutput('sarif-file', outputPath);
}

/**
 * Build a SARIF result from a validation result.
 */
function buildSarifResult(result: ValidationResult): object {
  const ruleId = result.signals[0]
    ? SIGNAL_TO_RULE[result.signals[0]]?.id || 'PG999'
    : 'PG999';

  const level =
    result.riskLevel === 'high-risk'
      ? 'error'
      : result.riskLevel === 'suspicious'
        ? 'warning'
        : 'note';

  return {
    ruleId,
    level,
    message: {
      text: `Package "${result.package}" flagged as ${result.riskLevel} (score: ${(result.riskScore * 100).toFixed(0)}%). Signals: ${result.signals.join(', ')}`,
    },
    locations: [
      {
        physicalLocation: {
          artifactLocation: {
            uri: result.sourceFile,
          },
          region: result.lineNumber
            ? {
                startLine: result.lineNumber,
                startColumn: 1,
              }
            : undefined,
        },
      },
    ],
    properties: {
      package: result.package,
      registry: result.registry,
      riskScore: result.riskScore,
      signals: result.signals,
    },
  };
}
