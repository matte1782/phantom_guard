/**
 * IMPLEMENTS: S102
 * INVARIANTS: INV103
 * TESTS: T102.01-T102.05
 * SECURITY: P1-SEC-002 (package validation)
 * EDGE_CASES: EC220-EC235
 *
 * Package extraction for Phantom Guard GitHub Action.
 *
 * Extracts package names from various dependency file formats.
 */

import * as core from '@actions/core';
import * as fs from 'fs';
import * as path from 'path';
import { getRegistryForFile } from './files';
import { isValidPackageName, preprocessContent } from './validation';

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
 * EC212: UTF-8 BOM stripped
 * EC213: CRLF line endings parsed correctly
 */
async function extractFromFile(filePath: string): Promise<ExtractedPackage[]> {
  const rawContent = fs.readFileSync(filePath, 'utf-8');
  // EC212, EC213: Preprocess content (BOM, CRLF)
  const content = preprocessContent(rawContent);
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
 * EC220: Simple `flask`
 * EC221: `flask>=2.0`
 * EC222: `# comment` - ignored
 * EC223: `flask # web` - inline comment stripped
 * EC224: `flask; python_version` - markers stripped
 * EC225: `flask[async]` - extras stripped
 * EC226: `git+https://...` - URLs skipped with warning
 * EC227: `./local_package` - local paths skipped with warning
 * EC233: Deduplication
 * EC234: Case normalization
 */
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

    // EC222: Skip full-line comments and empty lines
    if (!line || line.startsWith('#')) {
      continue;
    }

    // Skip pip options (EC226, EC227)
    if (line.startsWith('-')) {
      continue;
    }

    // EC226: Skip URLs
    if (line.startsWith('git+') || line.startsWith('http://') || line.startsWith('https://')) {
      core.debug(`Skipping URL at ${filePath}:${i + 1}: ${line.slice(0, 50)}`);
      continue;
    }

    // EC227: Skip local paths
    if (line.startsWith('./') || line.startsWith('../') || line.startsWith('/')) {
      core.debug(`Skipping local path at ${filePath}:${i + 1}: ${line.slice(0, 50)}`);
      continue;
    }

    // EC223: Remove inline comments
    const commentIdx = line.indexOf('#');
    if (commentIdx > 0) {
      line = line.substring(0, commentIdx).trim();
    }

    // EC224: Remove environment markers (after ;)
    const markerIdx = line.indexOf(';');
    if (markerIdx > 0) {
      line = line.substring(0, markerIdx).trim();
    }

    // Parse package name and version
    // Formats: package, package==1.0.0, package>=1.0.0, package[extra]
    // EC225: Strip extras in brackets
    const match = line.match(/^([a-zA-Z0-9][-a-zA-Z0-9._]*)(?:\[.*?\])?([<>=!~,].*)?$/);
    if (match) {
      // EC234: Normalize to lowercase
      const name = match[1].toLowerCase();
      const version = match[2] || undefined;

      // INV103: Validate package name
      if (isValidPackageName(name)) {
        // EC233: Deduplicate
        if (!seen.has(name)) {
          seen.add(name);
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

