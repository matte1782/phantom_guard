/**
 * IMPLEMENTS: S101
 * INVARIANTS: INV102
 * TESTS: T101.01-T101.05
 *
 * File discovery for Phantom Guard GitHub Action.
 *
 * Discovers dependency files using glob patterns.
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
 * IMPLEMENTS: S101
 * INVARIANT: INV102 - Only returns existing files
 *
 * Discover dependency files matching the given patterns.
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
    const globber = await glob.create(pattern, {
      followSymbolicLinks: false,
      implicitDescendants: true,
    });

    for await (const file of globber.globGenerator()) {
      // INV102: Only return existing files
      if (fs.existsSync(file) && fs.statSync(file).isFile()) {
        const normalized = path.normalize(file);
        if (!seen.has(normalized)) {
          seen.add(normalized);
          files.push(normalized);
        }
      }
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
