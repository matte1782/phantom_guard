# Week 9, Day 1 — Extension Activation and Core Integration

> **Date**: Day 1 of Week 9
> **Focus**: W9.1 (Extension activation) + W9.6 (Core integration) - SECURITY CRITICAL
> **Hours**: 8 (4 + 4)
> **Prerequisites**: Day 0 prep complete (scaffold exists), test stubs in vscode/tests/

---

## Goals

1. Implement extension activation (S120) with timeout handling
2. Implement core integration with phantom-guard CLI (S126) - SECURITY CRITICAL
3. All Day 1 tests passing (T120.*, T126.*)

---

## Pre-Flight Check

Before starting Day 1, verify Day 0 prep is complete:

```bash
cd vscode
npm install        # Should succeed
npm run compile    # Should succeed (with stub files)
```

If these fail, complete DAY_0_PREP.md first.

---

## Morning Session (4 hours)

### Task 1: W9.1 — Extension Activation (4 hours)

**SPEC**: S120
**INVARIANTS**: INV120, INV121
**TESTS**: T120.01-T120.04

#### Implementation: src/extension.ts

```typescript
/**
 * IMPLEMENTS: S120
 * INVARIANTS: INV120 (async I/O), INV121 (500ms timeout)
 * TESTS: T120.01, T120.02, T120.03, T120.04
 */

import * as vscode from 'vscode';
import { PhantomGuardCore, CoreError } from './core';
import { ActivationError, PythonNotFoundError } from './errors';

let core: PhantomGuardCore | undefined;

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  const startTime = Date.now();

  try {
    // INV121: Timeout after 500ms
    const activationPromise = doActivation(context);
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new ActivationError('Activation timeout')), 500);
    });

    await Promise.race([activationPromise, timeoutPromise]);

    const elapsed = Date.now() - startTime;
    console.log(`Phantom Guard activated in ${elapsed}ms`);

  } catch (error) {
    if (error instanceof PythonNotFoundError) {
      vscode.window.showErrorMessage(
        'Phantom Guard: Python 3.11+ not found. Please install Python.',
        'Install Python'
      ).then(selection => {
        if (selection === 'Install Python') {
          vscode.env.openExternal(vscode.Uri.parse('https://python.org'));
        }
      });
    } else if (error instanceof ActivationError) {
      vscode.window.showWarningMessage(`Phantom Guard: ${error.message}`);
    }
    // Don't throw - graceful degradation
  }
}

async function doActivation(context: vscode.ExtensionContext): Promise<void> {
  // INV120: All I/O is async
  core = new PhantomGuardCore();

  // Check phantom-guard availability
  const isAvailable = await core.checkAvailability();
  if (!isAvailable) {
    throw new ActivationError('phantom-guard CLI not found');
  }

  // Register disposables
  context.subscriptions.push(core);
}

export function deactivate(): void {
  core?.dispose();
  core = undefined;
}

export function getCore(): PhantomGuardCore | undefined {
  return core;
}
```

#### Tests to Enable

```bash
# Remove @skip from tests/extension.test.ts
T120.01 - Activation < 500ms
T120.02 - Timeout handled gracefully
T120.03 - Python not found shows error
T120.04 - phantom-guard not installed shows prompt
```

#### Acceptance Criteria (W9.1)
- [ ] T120.01 passes (activation < 500ms)
- [ ] T120.02 passes (timeout handled)
- [ ] T120.03 passes (Python not found)
- [ ] T120.04 passes (phantom-guard not installed)
- [ ] INV120 enforced (async I/O)
- [ ] INV121 enforced (500ms timeout)
- [ ] Extension loads in VS Code debug host

---

## Afternoon Session (4 hours)

### Task 3: W9.6 — Core Integration (4 hours) - SECURITY CRITICAL

**SPEC**: S126
**INVARIANTS**: INV127, INV128
**TESTS**: T126.01-T126.04
**SECURITY**: Shell injection prevention

#### Implementation: src/core.ts

```typescript
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
import { ValidationResult, PackageRisk } from './types';

const execFileAsync = promisify(execFile);

// SECURITY: Package name validation regex
// Prevents shell injection by only allowing safe characters
const PACKAGE_NAME_REGEX = /^[@a-z0-9][a-z0-9._-]*$/i;

// SECURITY: Forbidden shell metacharacters
const SHELL_METACHARACTERS = /[;|&$`\\"']/;

export class PhantomGuardCore implements vscode.Disposable {
  private pythonPath: string = 'python';
  private timeout: number = 5000; // 5 seconds per package

  /**
   * SECURITY: Validate package name before subprocess call
   * INV128: No shell injection via package names
   */
  private validatePackageName(name: string): boolean {
    if (SHELL_METACHARACTERS.test(name)) {
      console.warn(`Rejected package name with shell metacharacters: ${name}`);
      return false;
    }
    if (!PACKAGE_NAME_REGEX.test(name)) {
      console.warn(`Rejected invalid package name: ${name}`);
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
```

#### Security Tests (CRITICAL)

```typescript
// tests/core.test.ts

describe('T126.02 - Shell injection prevention', () => {
  it('rejects package names with semicolon', async () => {
    const core = new PhantomGuardCore();
    const result = await core.validatePackage('flask; rm -rf /');
    expect(result).toBeNull();
  });

  it('rejects package names with pipe', async () => {
    const core = new PhantomGuardCore();
    const result = await core.validatePackage('flask | cat /etc/passwd');
    expect(result).toBeNull();
  });

  it('rejects package names with backticks', async () => {
    const core = new PhantomGuardCore();
    const result = await core.validatePackage('flask`whoami`');
    expect(result).toBeNull();
  });
});

describe('T126.03 - Package name validation', () => {
  it('accepts valid package names', async () => {
    const core = new PhantomGuardCore();
    expect(core['validatePackageName']('flask')).toBe(true);
    expect(core['validatePackageName']('@scope/package')).toBe(true);
    expect(core['validatePackageName']('my-package_123')).toBe(true);
  });

  it('rejects invalid package names', async () => {
    const core = new PhantomGuardCore();
    expect(core['validatePackageName']('')).toBe(false);
    expect(core['validatePackageName']('-invalid')).toBe(false);
    expect(core['validatePackageName']('has spaces')).toBe(false);
  });
});
```

#### Tests to Enable

```bash
# Remove @skip from tests/core.test.ts
T126.01 - Spawn error handled gracefully
T126.02 - Shell injection prevented (SECURITY)
T126.03 - Package name validated (SECURITY)
T126.04 - First call < 500ms (benchmark)
```

#### Acceptance Criteria (W9.6)
- [ ] T126.01 passes (spawn error handling)
- [ ] T126.02 passes (shell injection prevention) **SECURITY CRITICAL**
- [ ] T126.03 passes (package name validation) **SECURITY CRITICAL**
- [ ] T126.04 passes (first call < 500ms)
- [ ] INV127 enforced (graceful spawn error)
- [ ] INV128 enforced (no shell injection)
- [ ] Uses execFile, NOT exec
- [ ] Package name regex validation in place

---

## End of Day Checklist

### Tests Status
- [ ] T120.01-T120.04 passing (extension activation)
- [ ] T126.01-T126.04 passing (core integration)
- [ ] All security tests passing

### Code Quality
- [ ] npm run compile succeeds
- [ ] No TypeScript errors
- [ ] Security review of core.ts complete

### Commits
```bash
git add vscode/
git commit -m "feat(S120,S126): VS Code extension scaffold and core integration

IMPLEMENTS: S120, S126
TESTS: T120.01-T120.04, T126.01-T126.04
SECURITY: Shell injection prevention via execFile + regex validation

- Add VS Code extension project structure
- Implement extension activation with 500ms timeout
- Implement core integration with phantom-guard CLI
- Add security validation for package names

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Risk Mitigation

| Risk | Mitigation |
|:-----|:-----------|
| Python not in PATH | Config option for pythonPath |
| Shell injection | execFile + regex validation |
| Slow activation | 500ms timeout with graceful degradation |
| CLI not installed | Clear error message with install prompt |

---

## Dependencies for Day 2

Day 2 (Diagnostic provider) requires:
- [ ] Extension activates successfully
- [ ] Core can validate packages
- [ ] Error types defined

---

**Day 1 Focus**: Foundation + Security. Do not proceed to Day 2 until security tests pass.
