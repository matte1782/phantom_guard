/**
 * IMPLEMENTS: S102
 * INVARIANTS: INV103
 * SECURITY: P1-SEC-002 - Package name validation
 * TESTS: T102.SEC
 *
 * Package name validation and sanitization.
 *
 * SECURITY CRITICAL: This module validates package names to prevent
 * shell injection and other attacks when package names are passed
 * to external processes.
 */

import * as core from '@actions/core';

/**
 * Maximum allowed package name length.
 * npm: 214 characters
 * pypi: no official limit, but we enforce 214 for safety
 * crates: 64 characters, but we use 214 for consistency
 */
const MAX_PACKAGE_NAME_LENGTH = 214;

/**
 * Package name validation regex.
 * - npm: @scope/name or name (alphanumeric, hyphens, dots, underscores)
 * - pypi: name (alphanumeric, hyphens, dots, underscores)
 * - crates: name (alphanumeric, hyphens, underscores)
 *
 * SECURITY: This regex prevents shell injection by only allowing safe characters.
 */
const SCOPED_PACKAGE_REGEX = /^@[a-z0-9][-a-z0-9._]*\/[a-z0-9][-a-z0-9._]*$/i;
const STANDARD_PACKAGE_REGEX = /^[a-z0-9][-a-z0-9._]*$/i;

/**
 * P1-SEC-002: Shell metacharacters that MUST be rejected.
 * These characters could be used for shell injection if passed to subprocess.
 */
const SHELL_METACHAR_REGEX = /[;|&$`\\"'<>(){}[\]!#*?~\n\r\t]/;

/**
 * IMPLEMENTS: S102
 * INVARIANT: INV103
 * SECURITY: P1-SEC-002
 *
 * Validate that a package name is safe and valid.
 *
 * @param name - Package name to validate
 * @returns true if valid, false otherwise
 */
export function isValidPackageName(name: string): boolean {
  if (!name || typeof name !== 'string') {
    return false;
  }

  const trimmed = name.trim();

  // Check length limits
  if (trimmed.length === 0 || trimmed.length > MAX_PACKAGE_NAME_LENGTH) {
    return false;
  }

  // P1-SEC-002: SECURITY - Reject shell metacharacters explicitly
  if (SHELL_METACHAR_REGEX.test(trimmed)) {
    return false;
  }

  // Check against valid package name patterns
  if (trimmed.startsWith('@')) {
    return SCOPED_PACKAGE_REGEX.test(trimmed);
  }

  return STANDARD_PACKAGE_REGEX.test(trimmed);
}

/**
 * IMPLEMENTS: S102
 * SECURITY: P1-SEC-002
 *
 * Sanitize and validate a package name.
 *
 * @param name - Package name to sanitize
 * @param file - Source file (for warning messages)
 * @param line - Line number (for warning messages)
 * @returns Sanitized lowercase name, or null if invalid
 */
export function sanitizePackageName(
  name: string,
  file: string,
  line: number
): string | null {
  if (!name || typeof name !== 'string') {
    return null;
  }

  const trimmed = name.trim().toLowerCase();

  if (!isValidPackageName(trimmed)) {
    // Truncate long/suspicious names in warning for safety
    const displayName = name.length > 50 ? name.slice(0, 50) + '...' : name;
    core.warning(`Invalid package name at ${file}:${line}: '${displayName}'`);
    return null;
  }

  return trimmed;
}

/**
 * Strip UTF-8 BOM from content.
 * EC212: UTF-8 BOM stripped
 *
 * @param content - File content
 * @returns Content without BOM
 */
export function stripBOM(content: string): string {
  if (content.charCodeAt(0) === 0xfeff) {
    return content.slice(1);
  }
  return content;
}

/**
 * Normalize line endings to LF.
 * EC213: CRLF line endings parsed correctly
 *
 * @param content - File content
 * @returns Content with normalized line endings
 */
export function normalizeLineEndings(content: string): string {
  return content.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
}

/**
 * Preprocess file content for parsing.
 * Handles BOM and line endings.
 *
 * @param content - Raw file content
 * @returns Preprocessed content ready for parsing
 */
export function preprocessContent(content: string): string {
  return normalizeLineEndings(stripBOM(content));
}
