/**
 * IMPLEMENTS: S100
 * INVARIANTS: INV100, INV101
 * TESTS: T100.01-T100.03
 * SECURITY: P1-SEC-003 (token masking)
 *
 * Phantom Guard GitHub Action Entry Point.
 *
 * Validates dependency files for AI-hallucinated package attacks.
 */

import * as core from '@actions/core';
import { discoverFiles } from './files';
import { extractPackages } from './extract';
import { validatePackages, type ValidationResult } from './validate';
import { generatePRComment } from './comment';
import { generateSARIF } from './sarif';
import {
  ExitCode,
  determineExitCode,
  getExitCodeDescription,
  parseFailOnThreshold,
  type FailOnThreshold,
  type ValidationSummary,
} from './exit';

/**
 * Output format options.
 */
type OutputFormat = 'github-comment' | 'sarif' | 'json' | 'none';

/**
 * Validate output format input.
 */
function parseOutputFormat(input: string): OutputFormat {
  const normalized = input.toLowerCase().trim();
  if (['github-comment', 'sarif', 'json', 'none'].includes(normalized)) {
    return normalized as OutputFormat;
  }
  throw new Error(
    `Invalid output format: "${input}". Must be one of: github-comment, sarif, json, none`
  );
}

/**
 * IMPLEMENTS: S100
 * INVARIANT: INV100 - Always produces valid output
 * INVARIANT: INV101 - Exit code matches validation status
 *
 * Main entry point for the GitHub Action.
 */
export async function run(): Promise<void> {
  let exitCode = ExitCode.SAFE;

  try {
    // Parse inputs
    const filesInput = core.getInput('files');
    const failOnInput = core.getInput('fail-on');
    const outputInput = core.getInput('output');
    const githubToken = core.getInput('github-token') || process.env.GITHUB_TOKEN || '';
    // pythonPath will be used in Day 4 when calling Python core
    const _pythonPath = core.getInput('python-path') || 'python';
    void _pythonPath; // Suppress unused variable warning until Day 4

    // P1-SEC-003: Mask GITHUB_TOKEN in logs
    if (githubToken) {
      core.setSecret(githubToken);
    }

    core.info('Phantom Guard - Detecting AI-hallucinated package attacks');
    core.info(`Files pattern: ${filesInput}`);
    core.info(`Fail on: ${failOnInput}`);
    core.info(`Output format: ${outputInput}`);

    // Validate inputs
    let failOn: FailOnThreshold;
    let outputFormat: OutputFormat;

    try {
      failOn = parseFailOnThreshold(failOnInput);
      outputFormat = parseOutputFormat(outputInput);
    } catch (error) {
      core.setFailed(`Configuration error: ${error instanceof Error ? error.message : error}`);
      core.setOutput('exit-code', ExitCode.CONFIG_ERROR);
      return;
    }

    // Step 1: Discover dependency files
    core.startGroup('Discovering dependency files');
    const files = await discoverFiles(filesInput);
    core.info(`Found ${files.length} dependency files`);
    for (const file of files) {
      core.info(`  - ${file}`);
    }
    core.endGroup();

    if (files.length === 0) {
      core.warning('No dependency files found matching patterns');
      core.setOutput('safe-count', 0);
      core.setOutput('suspicious-count', 0);
      core.setOutput('high-risk-count', 0);
      core.setOutput('packages-checked', 0);
      core.setOutput('exit-code', ExitCode.NO_PACKAGES);
      return;
    }

    // Step 2: Extract packages from files
    core.startGroup('Extracting packages');
    const packages = await extractPackages(files);
    core.info(`Found ${packages.length} packages to validate`);
    core.endGroup();

    if (packages.length === 0) {
      core.warning('No packages found in dependency files');
      core.setOutput('safe-count', 0);
      core.setOutput('suspicious-count', 0);
      core.setOutput('high-risk-count', 0);
      core.setOutput('packages-checked', 0);
      core.setOutput('exit-code', ExitCode.NO_PACKAGES);
      return;
    }

    // Step 3: Validate packages
    core.startGroup('Validating packages');
    const results = await validatePackages(packages);
    core.info(`Validated ${results.length} packages`);
    core.endGroup();

    // Step 4: Calculate summary
    const summary = calculateSummary(results);
    exitCode = determineExitCode(summary, failOn);

    // Step 5: Set outputs
    core.setOutput('safe-count', summary.safeCount);
    core.setOutput('suspicious-count', summary.suspiciousCount);
    core.setOutput('high-risk-count', summary.highRiskCount);
    core.setOutput('packages-checked', summary.totalPackages);
    core.setOutput('exit-code', exitCode);

    // Step 6: Generate output based on format
    core.startGroup('Generating output');
    await generateOutput(outputFormat, results, summary, githubToken);
    core.endGroup();

    // Step 7: Report status
    core.info('');
    core.info('=== Phantom Guard Summary ===');
    core.info(`Total packages: ${summary.totalPackages}`);
    core.info(`Safe: ${summary.safeCount}`);
    core.info(`Suspicious: ${summary.suspiciousCount}`);
    core.info(`High-risk: ${summary.highRiskCount}`);
    core.info(`Exit code: ${exitCode} (${getExitCodeDescription(exitCode)})`);

    // INV101: Exit code matches validation status
    if (exitCode === ExitCode.HIGH_RISK || exitCode === ExitCode.SUSPICIOUS) {
      core.setFailed(getExitCodeDescription(exitCode));
    }
  } catch (error) {
    exitCode = ExitCode.ERROR;
    core.setOutput('exit-code', exitCode);
    if (error instanceof Error) {
      core.setFailed(`Action failed: ${error.message}`);
    } else {
      core.setFailed(`Action failed: ${error}`);
    }
  }
}

/**
 * Calculate summary from validation results.
 */
function calculateSummary(results: ValidationResult[]): ValidationSummary {
  let safeCount = 0;
  let suspiciousCount = 0;
  let highRiskCount = 0;
  const errors: string[] = [];

  for (const result of results) {
    if (result.error) {
      errors.push(`${result.package}: ${result.error}`);
      continue;
    }

    if (result.riskLevel === 'safe') {
      safeCount++;
    } else if (result.riskLevel === 'suspicious') {
      suspiciousCount++;
    } else if (result.riskLevel === 'high-risk') {
      highRiskCount++;
    }
  }

  return {
    safeCount,
    suspiciousCount,
    highRiskCount,
    totalPackages: results.length,
    errors,
  };
}

/**
 * Generate output based on format.
 */
async function generateOutput(
  format: OutputFormat,
  results: ValidationResult[],
  summary: ValidationSummary,
  githubToken: string
): Promise<void> {
  switch (format) {
    case 'github-comment':
      await generatePRComment(results, summary, githubToken);
      break;
    case 'sarif':
      await generateSARIF(results);
      break;
    case 'json':
      core.info(JSON.stringify({ results, summary }, null, 2));
      break;
    case 'none':
      core.info('Output format set to none, skipping output generation');
      break;
  }
}

// Run the action
run();
