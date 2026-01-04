/**
 * IMPLEMENTS: S102
 * INVARIANTS: INV103
 * TESTS: T102.01-T102.05
 *
 * Package extraction for Phantom Guard GitHub Action.
 *
 * Extracts package names from various dependency file formats.
 */

import * as core from '@actions/core';
import * as fs from 'fs';
import * as path from 'path';
import { getRegistryForFile } from './files';

/**
 * Extracted package information.
 */
export interface ExtractedPackage {
  /** Package name */
  name: string;
  /** Optional version specifier */
  version?: string;
  /** Source file path */
  sourceFile: string;
  /** Line number in source file (1-indexed) */
  lineNumber?: number;
  /** Registry type (pypi, npm, crates) */
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
      core.warning(`Failed to parse ${file}: ${error instanceof Error ? error.message : error}`);
    }
  }

  return packages;
}

/**
 * Extract packages from a single file.
 */
async function extractFromFile(filePath: string): Promise<ExtractedPackage[]> {
  const content = fs.readFileSync(filePath, 'utf-8');
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
      // Handle pattern matches like requirements-dev.txt
      if (basename.endsWith('.txt') && basename.startsWith('requirements')) {
        return parseRequirementsTxt(content, filePath, registry);
      }
      core.debug(`Unknown file format: ${basename}`);
      return [];
  }
}

/**
 * Parse requirements.txt format.
 */
function parseRequirementsTxt(
  content: string,
  filePath: string,
  registry: string
): ExtractedPackage[] {
  const packages: ExtractedPackage[] = [];
  const lines = content.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Skip comments and empty lines
    if (!line || line.startsWith('#') || line.startsWith('-')) {
      continue;
    }

    // Parse package name and version
    // Formats: package, package==1.0.0, package>=1.0.0, package[extra]
    const match = line.match(/^([a-zA-Z0-9][-a-zA-Z0-9._]*)(\[.*\])?([<>=!~].*)?$/);
    if (match) {
      const name = match[1].toLowerCase();
      const version = match[3] || undefined;

      // INV103: Validate package name
      if (isValidPackageName(name)) {
        packages.push({
          name,
          version,
          sourceFile: filePath,
          lineNumber: i + 1,
          registry,
        });
      }
    }
  }

  return packages;
}

/**
 * Parse package.json format.
 */
function parsePackageJson(
  content: string,
  filePath: string,
  registry: string
): ExtractedPackage[] {
  const packages: ExtractedPackage[] = [];

  try {
    const json = JSON.parse(content);

    // Extract from dependencies
    const deps = { ...json.dependencies, ...json.devDependencies };

    for (const [name, version] of Object.entries(deps)) {
      if (typeof version === 'string' && isValidPackageName(name)) {
        packages.push({
          name,
          version,
          sourceFile: filePath,
          registry,
        });
      }
    }
  } catch (error) {
    core.warning(`Invalid JSON in ${filePath}: ${error instanceof Error ? error.message : error}`);
  }

  return packages;
}

/**
 * Parse Cargo.toml format.
 */
function parseCargoToml(
  content: string,
  filePath: string,
  registry: string
): ExtractedPackage[] {
  const packages: ExtractedPackage[] = [];
  const lines = content.split('\n');

  let inDependencies = false;
  let inDevDependencies = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Track sections
    if (line === '[dependencies]') {
      inDependencies = true;
      inDevDependencies = false;
      continue;
    }
    if (line === '[dev-dependencies]') {
      inDependencies = false;
      inDevDependencies = true;
      continue;
    }
    if (line.startsWith('[') && line.endsWith(']')) {
      inDependencies = false;
      inDevDependencies = false;
      continue;
    }

    // Parse dependencies
    if (inDependencies || inDevDependencies) {
      // Formats: name = "version", name = { version = "..." }
      const simpleMatch = line.match(/^([a-zA-Z0-9_-]+)\s*=\s*"([^"]+)"$/);
      const tableMatch = line.match(/^([a-zA-Z0-9_-]+)\s*=\s*\{/);

      if (simpleMatch) {
        const name = simpleMatch[1];
        const version = simpleMatch[2];
        if (isValidPackageName(name)) {
          packages.push({
            name,
            version,
            sourceFile: filePath,
            lineNumber: i + 1,
            registry,
          });
        }
      } else if (tableMatch) {
        const name = tableMatch[1];
        // Extract version from table format
        const versionMatch = line.match(/version\s*=\s*"([^"]+)"/);
        if (isValidPackageName(name)) {
          packages.push({
            name,
            version: versionMatch?.[1],
            sourceFile: filePath,
            lineNumber: i + 1,
            registry,
          });
        }
      }
    }
  }

  return packages;
}

/**
 * Parse pyproject.toml format.
 */
function parsePyprojectToml(
  content: string,
  filePath: string,
  registry: string
): ExtractedPackage[] {
  const packages: ExtractedPackage[] = [];
  const lines = content.split('\n');

  let inDependencies = false;
  let inDevDependencies = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Track sections
    if (line === 'dependencies = [' || line.startsWith('[project.dependencies]')) {
      inDependencies = true;
      inDevDependencies = false;
      continue;
    }
    if (line.includes('dev-dependencies') || line.includes('dev =')) {
      inDependencies = false;
      inDevDependencies = true;
      continue;
    }
    if (line.startsWith('[') && !line.includes('dependencies')) {
      inDependencies = false;
      inDevDependencies = false;
      continue;
    }
    if (line === ']') {
      inDependencies = false;
      inDevDependencies = false;
      continue;
    }

    // Parse dependencies (PEP 621 style)
    if (inDependencies || inDevDependencies) {
      // Format: "package>=version" or "package"
      const match = line.match(/"([a-zA-Z0-9][-a-zA-Z0-9._]*)([<>=!~].*)?"/);
      if (match) {
        const name = match[1].toLowerCase();
        const version = match[2];
        if (isValidPackageName(name)) {
          packages.push({
            name,
            version,
            sourceFile: filePath,
            lineNumber: i + 1,
            registry,
          });
        }
      }
    }
  }

  return packages;
}

/**
 * INVARIANT: INV103
 *
 * Validate that a package name is valid.
 */
function isValidPackageName(name: string): boolean {
  if (!name || name.length === 0 || name.length > 214) {
    return false;
  }

  // npm scoped packages
  if (name.startsWith('@')) {
    return /^@[a-z0-9][-a-z0-9._]*\/[a-z0-9][-a-z0-9._]*$/i.test(name);
  }

  // Standard package name
  return /^[a-z0-9][-a-z0-9._]*$/i.test(name);
}
