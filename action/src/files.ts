/**
 * IMPLEMENTS: S101
 * INVARIANTS: INV102
 * TESTS: T101.01-T101.05
 * EDGE_CASES: EC200-EC215
 *
 * File discovery for Phantom Guard GitHub Action.
 *
 * Discovers dependency files using glob patterns.
 * P1-EC206: Follows valid symlinks
 * P1-EC207: Skips broken symlinks with warning
 */

import * as glob from '@actions/glob';
import * as core from '@actions/core';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Default file patterns for dependency discovery.
 */
export const DEFAULT_PATTERNS = [
  'requirements.txt',
  'requirements/*.txt',
  'requirements-*.txt',
  'package.json',
  'package-lock.json',
  'Cargo.toml',
  'Cargo.lock',
  'pyproject.toml',
  'poetry.lock',
  'Pipfile',
  'Pipfile.lock',
  'setup.py',
  'setup.cfg',
];

/**
 * Known dependency file patterns and their registries.
 */
export const FILE_REGISTRY_MAP: Record<string, string> = {
  'requirements.txt': 'pypi',
  'pyproject.toml': 'pypi',
  'poetry.lock': 'pypi',
  'Pipfile': 'pypi',
  'Pipfile.lock': 'pypi',
  'setup.py': 'pypi',
  'setup.cfg': 'pypi',
  'package.json': 'npm',
  'package-lock.json': 'npm',
  'Cargo.toml': 'crates',
  'Cargo.lock': 'crates',
};

/**
 * P1-EC206: Check if path is a valid file (follows symlinks)
 * P1-EC207: Skip broken symlinks with warning
 *
 * @param filePath - Path to check
 * @returns true if valid file, false otherwise
 */
function isValidFile(filePath: string): boolean {
  try {
    // fs.statSync follows symlinks, throws if broken
    const stats = fs.statSync(filePath);
    return stats.isFile();
  } catch {
    // P1-EC207: Check if it's a broken symlink
    try {
      const lstats = fs.lstatSync(filePath);
      if (lstats.isSymbolicLink()) {
        core.warning(`Skipping broken symlink: ${filePath}`);
      }
    } catch {
      // File doesn't exist at all
    }
    return false;
  }
}

/**
 * Get the resolved real path for deduplication (resolves symlinks)
 *
 * @param filePath - Path to resolve
 * @returns Real path or original path if resolution fails
 */
function getRealPath(filePath: string): string {
  try {
    return fs.realpathSync(filePath);
  } catch {
    return filePath;
  }
}

/**
 * IMPLEMENTS: S101
 * INVARIANT: INV102 - Only returns existing files, graceful error handling
 *
 * Discover dependency files matching the given patterns.
 * P1-EC206: Follows valid symlinks
 * P1-EC207: Skips broken symlinks with warning
 *
 * @param patterns - Comma-separated glob patterns or file names
 * @returns Array of absolute file paths
 */
export async function discoverFiles(patterns: string): Promise<string[]> {
  const patternList = parsePatterns(patterns);
  core.debug(`Searching with patterns: ${patternList.join(', ')}`);

  const files: string[] = [];
  const seen = new Set<string>();

  for (const pattern of patternList) {
    try {
      const globber = await glob.create(pattern, {
        followSymbolicLinks: true, // P1-EC206: Follow symlinks
        implicitDescendants: true,
      });

      for await (const file of globber.globGenerator()) {
        // P1-EC206/207: Validate file (handles symlinks)
        if (!isValidFile(file)) {
          continue;
        }

        // Deduplicate by resolved real path (handles symlinks pointing to same file)
        const realPath = getRealPath(file);
        if (!seen.has(realPath)) {
          seen.add(realPath);
          files.push(path.normalize(file));
        }
      }
    } catch (error) {
      // INV102: Graceful fallback on invalid glob
      core.warning(
        `Pattern '${pattern}' error: ${error instanceof Error ? error.message : 'unknown error'}`
      );
    }
  }

  return files.sort();
}

/**
 * Parse comma-separated pattern string into array.
 *
 * @param patterns - Comma-separated patterns
 * @returns Array of individual patterns
 */
function parsePatterns(patterns: string): string[] {
  if (!patterns || patterns.trim() === '') {
    return DEFAULT_PATTERNS;
  }

  return patterns
    .split(',')
    .map((p) => p.trim())
    .filter((p) => p.length > 0);
}

/**
 * IMPLEMENTS: S101
 *
 * Get the registry type for a file based on its name.
 *
 * @param filePath - Path to the dependency file
 * @returns Registry name (pypi, npm, crates) or 'unknown'
 */
export function getRegistryForFile(filePath: string): string {
  const basename = path.basename(filePath);

  // Direct match
  if (basename in FILE_REGISTRY_MAP) {
    return FILE_REGISTRY_MAP[basename];
  }

  // Pattern match for requirements-*.txt
  if (basename.startsWith('requirements') && basename.endsWith('.txt')) {
    return 'pypi';
  }

  return 'unknown';
}

/**
 * Check if a file is a valid dependency file.
 *
 * @param filePath - Path to check
 * @returns true if it's a recognized dependency file
 */
export function isDependencyFile(filePath: string): boolean {
  return getRegistryForFile(filePath) !== 'unknown';
}
