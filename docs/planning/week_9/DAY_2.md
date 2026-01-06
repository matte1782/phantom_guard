# Week 9, Day 2 — Diagnostic Provider

> **Date**: Day 2 of Week 9
> **Focus**: W9.2 — Diagnostic provider (S121)
> **Hours**: 6
> **Prerequisites**: Day 1 complete (extension activation + core integration)

---

## Goals

1. Implement diagnostic provider for requirements.txt, package.json, Cargo.toml
2. Real-time validation with debouncing
3. Proper diagnostic severity mapping
4. Document lifecycle handling (clear on close)

---

## Morning Session (3 hours)

### Task: W9.2 — Diagnostic Provider

**SPEC**: S121
**INVARIANTS**: INV122
**TESTS**: T121.01-T121.05
**EDGE CASES**: EC320-EC335

#### Implementation: src/diagnostics.ts

```typescript
/**
 * IMPLEMENTS: S121
 * INVARIANTS: INV122 (clear on close)
 * TESTS: T121.01-T121.05
 * EDGE CASES: EC320-EC335
 */

import * as vscode from 'vscode';
import { PhantomGuardCore } from './core';
import { PackageRisk, RiskLevel } from './types';

const DIAGNOSTIC_SOURCE = 'phantom-guard';
const DEBOUNCE_MS = 500;

export class DiagnosticProvider implements vscode.Disposable {
  private diagnosticCollection: vscode.DiagnosticCollection;
  private core: PhantomGuardCore;
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private disposables: vscode.Disposable[] = [];

  constructor(core: PhantomGuardCore) {
    this.core = core;
    this.diagnosticCollection = vscode.languages.createDiagnosticCollection(DIAGNOSTIC_SOURCE);

    // Register document listeners
    this.disposables.push(
      vscode.workspace.onDidOpenTextDocument(doc => this.onDocumentOpen(doc)),
      vscode.workspace.onDidChangeTextDocument(event => this.onDocumentChange(event)),
      vscode.workspace.onDidCloseTextDocument(doc => this.onDocumentClose(doc))
    );

    // Validate already open documents
    vscode.workspace.textDocuments.forEach(doc => this.onDocumentOpen(doc));
  }

  /**
   * Check if document should be validated
   */
  private shouldValidate(document: vscode.TextDocument): boolean {
    const fileName = document.fileName.toLowerCase();
    return (
      fileName.endsWith('requirements.txt') ||
      fileName.endsWith('package.json') ||
      fileName.endsWith('cargo.toml') ||
      fileName.includes('requirements/') // requirements/*.txt
    );
  }

  /**
   * Determine registry from document
   */
  private getRegistry(document: vscode.TextDocument): string {
    const fileName = document.fileName.toLowerCase();
    if (fileName.endsWith('package.json')) return 'npm';
    if (fileName.endsWith('cargo.toml')) return 'crates';
    return 'pypi';
  }

  /**
   * Handle document open - trigger initial validation
   */
  private onDocumentOpen(document: vscode.TextDocument): void {
    if (this.shouldValidate(document)) {
      this.validateDocument(document);
    }
  }

  /**
   * Handle document change - debounced validation
   * EC327: Rapid edits are debounced (500ms)
   */
  private onDocumentChange(event: vscode.TextDocumentChangeEvent): void {
    const document = event.document;
    if (!this.shouldValidate(document)) return;

    // Clear existing timer for this document
    const uri = document.uri.toString();
    const existingTimer = this.debounceTimers.get(uri);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    // Set new debounced timer
    const timer = setTimeout(() => {
      this.debounceTimers.delete(uri);
      this.validateDocument(document);
    }, DEBOUNCE_MS);

    this.debounceTimers.set(uri, timer);
  }

  /**
   * Handle document close - clear diagnostics
   * INV122: Diagnostics are cleared when document is closed
   */
  private onDocumentClose(document: vscode.TextDocument): void {
    // INV122: Always clear diagnostics on close
    this.diagnosticCollection.delete(document.uri);

    // Clear any pending debounce timer
    const uri = document.uri.toString();
    const timer = this.debounceTimers.get(uri);
    if (timer) {
      clearTimeout(timer);
      this.debounceTimers.delete(uri);
    }
  }

  /**
   * Validate document and create diagnostics
   */
  async validateDocument(document: vscode.TextDocument): Promise<void> {
    const packages = this.extractPackages(document);
    if (packages.length === 0) {
      this.diagnosticCollection.set(document.uri, []);
      return;
    }

    const registry = this.getRegistry(document);
    const diagnostics: vscode.Diagnostic[] = [];

    // Validate each package
    for (const pkg of packages) {
      try {
        const result = await this.core.validatePackage(pkg.name, registry);
        if (result) {
          const diagnostic = this.createDiagnostic(pkg, result, document);
          if (diagnostic) {
            diagnostics.push(diagnostic);
          }
        }
      } catch (error) {
        console.error(`Validation error for ${pkg.name}:`, error);
        // Continue with other packages
      }
    }

    this.diagnosticCollection.set(document.uri, diagnostics);
  }

  /**
   * Extract package names and their line positions from document
   */
  private extractPackages(document: vscode.TextDocument): Array<{ name: string; line: number; range: vscode.Range }> {
    const packages: Array<{ name: string; line: number; range: vscode.Range }> = [];
    const fileName = document.fileName.toLowerCase();

    if (fileName.endsWith('requirements.txt') || fileName.includes('requirements/')) {
      return this.extractRequirementsTxt(document);
    } else if (fileName.endsWith('package.json')) {
      return this.extractPackageJson(document);
    } else if (fileName.endsWith('cargo.toml')) {
      return this.extractCargoToml(document);
    }

    return packages;
  }

  /**
   * Extract packages from requirements.txt
   * EC320-EC335: Handle various formats
   */
  private extractRequirementsTxt(document: vscode.TextDocument): Array<{ name: string; line: number; range: vscode.Range }> {
    const packages: Array<{ name: string; line: number; range: vscode.Range }> = [];

    for (let i = 0; i < document.lineCount; i++) {
      const line = document.lineAt(i);
      const text = line.text.trim();

      // EC332: Skip comments
      if (text.startsWith('#') || text === '') continue;

      // EC226, EC227: Skip URLs and local paths
      if (text.startsWith('git+') || text.startsWith('./') || text.startsWith('/')) continue;

      // Extract package name (strip version specifiers, extras, markers)
      const match = text.match(/^([a-zA-Z0-9][-a-zA-Z0-9._]*)/);
      if (match) {
        const name = match[1].toLowerCase();
        const startChar = line.text.indexOf(match[1]);
        const range = new vscode.Range(i, startChar, i, startChar + match[1].length);
        packages.push({ name, line: i, range });
      }
    }

    return packages;
  }

  /**
   * Extract packages from package.json
   */
  private extractPackageJson(document: vscode.TextDocument): Array<{ name: string; line: number; range: vscode.Range }> {
    const packages: Array<{ name: string; line: number; range: vscode.Range }> = [];

    try {
      const json = JSON.parse(document.getText());
      const deps = { ...json.dependencies, ...json.devDependencies };

      for (const name of Object.keys(deps)) {
        // Find line number for this dependency
        const lineInfo = this.findPackageLineInJson(document, name);
        if (lineInfo) {
          packages.push({ name, line: lineInfo.line, range: lineInfo.range });
        }
      }
    } catch {
      // EC329: Parse error - return empty
    }

    return packages;
  }

  /**
   * Extract packages from Cargo.toml
   */
  private extractCargoToml(document: vscode.TextDocument): Array<{ name: string; line: number; range: vscode.Range }> {
    const packages: Array<{ name: string; line: number; range: vscode.Range }> = [];
    let inDependencies = false;

    for (let i = 0; i < document.lineCount; i++) {
      const line = document.lineAt(i);
      const text = line.text.trim();

      if (text === '[dependencies]' || text.startsWith('[dependencies.')) {
        inDependencies = true;
        continue;
      }
      if (text.startsWith('[') && !text.includes('dependencies')) {
        inDependencies = false;
        continue;
      }

      if (inDependencies && text.includes('=')) {
        const match = text.match(/^([a-zA-Z0-9][-a-zA-Z0-9_]*)\s*=/);
        if (match) {
          const name = match[1];
          const startChar = line.text.indexOf(match[1]);
          const range = new vscode.Range(i, startChar, i, startChar + match[1].length);
          packages.push({ name, line: i, range });
        }
      }
    }

    return packages;
  }

  /**
   * Find package line in JSON document
   */
  private findPackageLineInJson(document: vscode.TextDocument, packageName: string): { line: number; range: vscode.Range } | null {
    const searchPattern = `"${packageName}"`;

    for (let i = 0; i < document.lineCount; i++) {
      const line = document.lineAt(i);
      const index = line.text.indexOf(searchPattern);
      if (index !== -1) {
        const range = new vscode.Range(i, index + 1, i, index + 1 + packageName.length);
        return { line: i, range };
      }
    }

    return null;
  }

  /**
   * Create diagnostic from validation result
   * EC320: Safe = no diagnostic
   * EC321: Suspicious = warning
   * EC322: High risk = error
   */
  private createDiagnostic(
    pkg: { name: string; line: number; range: vscode.Range },
    result: PackageRisk,
    document: vscode.TextDocument
  ): vscode.Diagnostic | null {

    // EC320: Safe packages get no diagnostic
    if (result.risk_level === 'SAFE') {
      return null;
    }

    // Map risk level to severity
    let severity: vscode.DiagnosticSeverity;
    switch (result.risk_level) {
      case 'HIGH_RISK':
        severity = vscode.DiagnosticSeverity.Error;
        break;
      case 'SUSPICIOUS':
        severity = vscode.DiagnosticSeverity.Warning;
        break;
      case 'NOT_FOUND':
        severity = vscode.DiagnosticSeverity.Error;
        break;
      default:
        severity = vscode.DiagnosticSeverity.Information;
    }

    // Create diagnostic message
    const signals = result.signals.join(', ');
    const message = `${result.risk_level}: ${pkg.name} (score: ${result.risk_score.toFixed(2)})${signals ? ` - ${signals}` : ''}`;

    const diagnostic = new vscode.Diagnostic(pkg.range, message, severity);
    diagnostic.source = DIAGNOSTIC_SOURCE;
    diagnostic.code = result.risk_level;

    return diagnostic;
  }

  dispose(): void {
    this.diagnosticCollection.dispose();
    this.disposables.forEach(d => d.dispose());
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();
  }
}
```

---

## Afternoon Session (3 hours)

### Integration with Extension

Update `src/extension.ts` to register the diagnostic provider:

```typescript
import { DiagnosticProvider } from './diagnostics';

let diagnosticProvider: DiagnosticProvider | undefined;

async function doActivation(context: vscode.ExtensionContext): Promise<void> {
  core = new PhantomGuardCore();

  const isAvailable = await core.checkAvailability();
  if (!isAvailable) {
    throw new ActivationError('phantom-guard CLI not found');
  }

  // Register diagnostic provider
  diagnosticProvider = new DiagnosticProvider(core);
  context.subscriptions.push(diagnosticProvider);
}
```

### Tests to Enable

```typescript
// tests/diagnostics.test.ts

describe('T121.01 - Safe package = no diagnostic', () => {
  it('should not create diagnostic for safe package', async () => {
    // Mock core to return SAFE result
    // Verify no diagnostic created
  });
});

describe('T121.02 - Suspicious = warning', () => {
  it('should create warning diagnostic for suspicious package', async () => {
    // Mock core to return SUSPICIOUS result
    // Verify warning severity diagnostic created
  });
});

describe('T121.03 - High risk = error', () => {
  it('should create error diagnostic for high-risk package', async () => {
    // Mock core to return HIGH_RISK result
    // Verify error severity diagnostic created
  });
});

describe('T121.04 - Diagnostics cleared on close', () => {
  it('should clear diagnostics when document is closed', async () => {
    // INV122 verification
    // Open document, create diagnostic, close document
    // Verify diagnostic collection is empty
  });
});

describe('T121.05 - Debounce works', () => {
  it('should debounce rapid document changes', async () => {
    // EC327 verification
    // Trigger multiple rapid changes
    // Verify validation only called once after debounce
  });
});
```

---

## Edge Case Handling

| EC_ID | Scenario | Implementation |
|:------|:---------|:---------------|
| EC320 | Safe package | No diagnostic created |
| EC321 | Suspicious | Warning severity |
| EC322 | High risk | Error severity |
| EC323 | Not found | Error severity |
| EC324 | Multiple issues | Multiple diagnostics |
| EC325 | Document close | Clear all diagnostics |
| EC326 | Document edit | Re-validate |
| EC327 | Rapid edits | 500ms debounce |
| EC328 | Large file | All packages validated |
| EC329 | Syntax error | Return empty list |
| EC330 | Diagnostic range | Highlight package name only |
| EC331 | Version in range | Range covers name only |
| EC332 | Comment line | Skip line |

---

## End of Day Checklist

### Tests Status
- [ ] T121.01 passing (safe = no diagnostic)
- [ ] T121.02 passing (suspicious = warning)
- [ ] T121.03 passing (high risk = error)
- [ ] T121.04 passing (clear on close) - INV122
- [ ] T121.05 passing (debounce)

### Code Quality
- [ ] npm run compile succeeds
- [ ] No TypeScript errors
- [ ] Diagnostic messages are clear and helpful

### Manual Testing
- [ ] Open requirements.txt - diagnostics appear
- [ ] Edit requirements.txt - diagnostics update (debounced)
- [ ] Close requirements.txt - diagnostics clear
- [ ] Open package.json - diagnostics appear
- [ ] Open Cargo.toml - diagnostics appear

### Commits
```bash
git add vscode/src/diagnostics.ts vscode/tests/diagnostics.test.ts
git commit -m "feat(S121): Implement VS Code diagnostic provider

IMPLEMENTS: S121
INVARIANTS: INV122 (clear on close)
TESTS: T121.01-T121.05
EDGE CASES: EC320-EC332

- Add DiagnosticProvider class with document lifecycle handling
- Implement package extraction for requirements.txt, package.json, Cargo.toml
- Add debounced validation (500ms) for document changes
- Map risk levels to appropriate diagnostic severities

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Dependencies for Day 3

Day 3 (Hover + Code actions) requires:
- [ ] Diagnostic provider working
- [ ] Package extraction working
- [ ] Risk level mapping working

---

**Day 2 Focus**: Real-time diagnostics with proper UX (debouncing, clear messages, lifecycle handling).
