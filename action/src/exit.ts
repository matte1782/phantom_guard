/**
 * IMPLEMENTS: S106
 * INVARIANTS: INV108
 * TESTS: T106.01-T106.04
 *
 * Exit code handling for Phantom Guard GitHub Action.
 *
 * Exit codes match CLI behavior:
 * - 0: All packages safe
 * - 1: Suspicious packages found
 * - 2: High-risk packages found
 * - 3: Runtime error
 * - 4: No packages found
 * - 5: Configuration error
 */

/**
 * Exit codes for the GitHub Action.
 * INV108: Exit codes are always in range [0, 5]
 */
export enum ExitCode {
  /** All packages validated as safe */
  SAFE = 0,
  /** Suspicious packages found (low-medium risk) */
  SUSPICIOUS = 1,
  /** High-risk packages found */
  HIGH_RISK = 2,
  /** Runtime error during execution */
  ERROR = 3,
  /** No packages found in files */
  NO_PACKAGES = 4,
  /** Configuration error (invalid inputs) */
  CONFIG_ERROR = 5,
}

/**
 * Validation result summary.
 */
export interface ValidationSummary {
  safeCount: number;
  suspiciousCount: number;
  highRiskCount: number;
  totalPackages: number;
  errors: string[];
}

/**
 * Fail-on threshold configuration.
 */
export type FailOnThreshold = 'none' | 'suspicious' | 'high-risk';

/**
 * IMPLEMENTS: S106
 * INVARIANT: INV108 - Exit codes always in range [0, 5]
 *
 * Determine the exit code based on validation results and fail-on threshold.
 *
 * @param summary - Validation result summary
 * @param failOn - When to fail the action
 * @returns Exit code in range [0, 5]
 */
export function determineExitCode(
  summary: ValidationSummary,
  failOn: FailOnThreshold
): ExitCode {
  // INV108: All return paths produce valid exit codes

  // Configuration/runtime errors take precedence
  if (summary.errors.length > 0) {
    return ExitCode.ERROR;
  }

  // No packages found
  if (summary.totalPackages === 0) {
    return ExitCode.NO_PACKAGES;
  }

  // Check based on fail-on threshold
  if (failOn === 'none') {
    // Never fail, just report
    return ExitCode.SAFE;
  }

  if (summary.highRiskCount > 0) {
    return ExitCode.HIGH_RISK;
  }

  if (failOn === 'suspicious' && summary.suspiciousCount > 0) {
    return ExitCode.SUSPICIOUS;
  }

  if (failOn === 'high-risk' && summary.suspiciousCount > 0) {
    // High-risk threshold: suspicious doesn't fail, just return SAFE
    // But we still want to indicate there were issues
    return ExitCode.SAFE;
  }

  return ExitCode.SAFE;
}

/**
 * IMPLEMENTS: S106
 *
 * Get human-readable description for an exit code.
 *
 * @param code - The exit code
 * @returns Human-readable description
 */
export function getExitCodeDescription(code: ExitCode): string {
  switch (code) {
    case ExitCode.SAFE:
      return 'All packages validated as safe';
    case ExitCode.SUSPICIOUS:
      return 'Suspicious packages found';
    case ExitCode.HIGH_RISK:
      return 'High-risk packages found';
    case ExitCode.ERROR:
      return 'Runtime error during execution';
    case ExitCode.NO_PACKAGES:
      return 'No packages found in dependency files';
    case ExitCode.CONFIG_ERROR:
      return 'Configuration error in action inputs';
    default:
      // INV108: Ensure we never return an unknown code
      return `Unknown exit code: ${code}`;
  }
}

/**
 * IMPLEMENTS: S106
 * INVARIANT: INV108
 *
 * Validate that a fail-on value is valid.
 *
 * @param value - The fail-on value to validate
 * @returns true if valid, false otherwise
 */
export function isValidFailOnThreshold(value: string): value is FailOnThreshold {
  return value === 'none' || value === 'suspicious' || value === 'high-risk';
}

/**
 * Parse and validate fail-on input.
 *
 * @param input - Raw input string
 * @returns Validated threshold or throws on invalid input
 */
export function parseFailOnThreshold(input: string): FailOnThreshold {
  const normalized = input.toLowerCase().trim();
  if (isValidFailOnThreshold(normalized)) {
    return normalized;
  }
  throw new Error(
    `Invalid fail-on value: "${input}". Must be one of: none, suspicious, high-risk`
  );
}
