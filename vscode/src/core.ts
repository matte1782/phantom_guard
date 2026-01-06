/**
 * IMPLEMENTS: S126
 * INVARIANTS: INV127 (graceful spawn error), INV128 (no shell injection)
 * TESTS: T126.01, T126.02, T126.03, T126.04
 * SECURITY: Uses execFile (not exec), validates package names
 */

import { execFile, ExecFileException } from 'child_process';
import { promisify } from 'util';
import * as vscode from 'vscode';
import { CoreSpawnError, CoreTimeoutError, CoreParseError, PythonNotFoundError } from './errors';
import { PackageRisk } from './types';

const execFileAsync = promisify(execFile);

// SECURITY: Package name validation regex
// Prevents shell injection by only allowing safe characters
// Supports: alphanumeric, hyphen, underscore, dot, @ and / for scoped packages
const PACKAGE_NAME_REGEX = /^[@a-z0-9][a-z0-9._\/-]*$/i;

// SECURITY: Forbidden shell metacharacters
const SHELL_METACHARACTERS = /[;|&$`\\"'<>(){}[\]\n\r]/;

export class PhantomGuardCore implements vscode.Disposable {
  private pythonPath: string = 'python';
  private timeout: number = 5000; // 5 seconds per package

  /**
   * Set Python executable path
   */
  setPythonPath(path: string): void {
    if (path && path.trim()) {
      this.pythonPath = path.trim();
    }
  }

  /**
   * SECURITY: Validate package name before subprocess call
   * INV128: No shell injection via package names
   */
  private validatePackageName(name: string): boolean {
    // Reject empty or whitespace-only names
    if (!name || !name.trim()) {
      console.warn('Rejected empty package name');
      return false;
    }

    // SECURITY: Check for shell metacharacters first
    if (SHELL_METACHARACTERS.test(name)) {
      console.warn(`Rejected package name with shell metacharacters: ${name}`);
      return false;
    }

    // SECURITY: Validate against allowed character pattern
    if (!PACKAGE_NAME_REGEX.test(name)) {
      console.warn(`Rejected invalid package name: ${name}`);
      return false;
    }

    // SECURITY: Reject names that are too long (prevent buffer overflow attempts)
    if (name.length > 214) { // npm limit
      console.warn(`Rejected package name exceeding max length: ${name}`);
      return false;
    }

    return true;
  }

  /**
   * Check if phantom-guard CLI is available
   */
  async checkAvailability(): Promise<boolean> {
    try {
      // SECURITY: execFile with array args, no shell
      await execFileAsync(this.pythonPath, ['-m', 'phantom_guard', '--version'], {
        timeout: this.timeout
      });
      return true;
    } catch (error) {
      const execError = error as ExecFileException;
      if (execError.code === 'ENOENT') {
        throw new PythonNotFoundError();
      }
      return false;
    }
  }

  /**
   * Validate a single package
   * INV127: Fails gracefully on spawn error
   * INV128: Uses execFile with array args (no shell)
   */
  async validatePackage(name: string, registry: string = 'pypi'): Promise<PackageRisk | null> {
    // SECURITY: Validate package name first
    if (!this.validatePackageName(name)) {
      return null;
    }

    // SECURITY: Also validate registry
    const allowedRegistries = ['pypi', 'npm', 'crates'];
    if (!allowedRegistries.includes(registry.toLowerCase())) {
      console.warn(`Rejected invalid registry: ${registry}`);
      return null;
    }

    try {
      // SECURITY: execFile with array arguments - NO SHELL
      const { stdout } = await execFileAsync(
        this.pythonPath,
        ['-m', 'phantom_guard', 'validate', name, '--registry', registry, '--output', 'json'],
        { timeout: this.timeout }
      );

      return this.parseOutput(stdout);

    } catch (error) {
      // INV127: Graceful spawn error handling
      const execError = error as ExecFileException;

      if (execError.killed) {
        throw new CoreTimeoutError(this.timeout);
      }
      if (execError.code === 'ENOENT') {
        throw new CoreSpawnError('Python executable not found');
      }

      // Log and return null for other errors (graceful degradation)
      console.error(`Validation error for ${name}:`, error);
      return null;
    }
  }

  /**
   * Validate multiple packages
   */
  async validatePackages(packages: string[], registry: string = 'pypi'): Promise<Map<string, PackageRisk | null>> {
    const results = new Map<string, PackageRisk | null>();

    // Validate all packages (could be parallelized in future)
    for (const pkg of packages) {
      if (this.validatePackageName(pkg)) {
        results.set(pkg, await this.validatePackage(pkg, registry));
      } else {
        results.set(pkg, null);
      }
    }

    return results;
  }

  /**
   * Parse JSON output from phantom-guard CLI
   */
  private parseOutput(stdout: string): PackageRisk {
    try {
      const result = JSON.parse(stdout);
      return {
        name: result.name,
        risk_level: result.risk_level,
        risk_score: result.risk_score,
        signals: result.signals || [],
        recommendation: result.recommendation
      };
    } catch {
      throw new CoreParseError(stdout);
    }
  }

  dispose(): void {
    // Cleanup if needed
  }
}
