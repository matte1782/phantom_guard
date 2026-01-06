# Week 9, Day 3 — Hover and Code Action Providers

> **Date**: Day 3 of Week 9
> **Focus**: W9.3 — Hover provider (S122) + W9.4 — Code action provider (S123)
> **Hours**: 8 (4 + 4)
> **Prerequisites**: Day 2 complete (diagnostic provider working)

---

## Goals

1. Implement hover provider showing package risk details
2. Implement code action provider for quick fixes
3. Typosquat fix suggestions
4. All Day 3 tests passing

---

## Morning Session (4 hours)

### Task: W9.3 — Hover Provider

**SPEC**: S122
**INVARIANTS**: INV123
**TESTS**: T122.01-T122.03
**EDGE CASES**: EC340-EC350

#### Implementation: src/hover.ts

```typescript
/**
 * IMPLEMENTS: S122
 * INVARIANTS: INV123 (null on non-package lines)
 * TESTS: T122.01-T122.03
 * EDGE CASES: EC340-EC350
 */

import * as vscode from 'vscode';
import { PhantomGuardCore } from './core';
import { PackageRisk } from './types';

export class HoverProvider implements vscode.HoverProvider, vscode.Disposable {
  private core: PhantomGuardCore;
  private cache: Map<string, PackageRisk> = new Map();
  private disposables: vscode.Disposable[] = [];

  constructor(core: PhantomGuardCore) {
    this.core = core;

    // Register for supported file types
    this.disposables.push(
      vscode.languages.registerHoverProvider(
        [
          { pattern: '**/requirements.txt' },
          { pattern: '**/requirements/*.txt' },
          { pattern: '**/package.json' },
          { pattern: '**/Cargo.toml' }
        ],
        this
      )
    );
  }

  /**
   * Provide hover information
   * INV123: Returns null on non-package lines
   */
  async provideHover(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken
  ): Promise<vscode.Hover | null> {
    // Extract package at position
    const packageInfo = this.getPackageAtPosition(document, position);

    // INV123: Return null if not on a package line
    if (!packageInfo) {
      return null;
    }

    // Check cache first
    const cacheKey = `${packageInfo.name}:${this.getRegistry(document)}`;
    let result = this.cache.get(cacheKey);

    if (!result) {
      // EC349: Show "Validating..." while checking
      if (token.isCancellationRequested) return null;

      try {
        result = await this.core.validatePackage(
          packageInfo.name,
          this.getRegistry(document)
        ) ?? undefined;

        if (result) {
          // EC348: Cache result for instant response on second hover
          this.cache.set(cacheKey, result);
        }
      } catch (error) {
        console.error(`Hover validation error for ${packageInfo.name}:`, error);
        return null;
      }
    }

    if (!result) {
      return null;
    }

    // Build hover content
    const markdown = this.buildHoverContent(result);
    return new vscode.Hover(markdown, packageInfo.range);
  }

  /**
   * Get package name and range at cursor position
   * Returns null if cursor is not on a package name
   */
  private getPackageAtPosition(
    document: vscode.TextDocument,
    position: vscode.Position
  ): { name: string; range: vscode.Range } | null {
    const line = document.lineAt(position.line);
    const text = line.text;

    // EC341, EC342: Skip comment and empty lines
    const trimmed = text.trim();
    if (trimmed.startsWith('#') || trimmed === '') {
      return null;
    }

    const fileName = document.fileName.toLowerCase();

    if (fileName.endsWith('requirements.txt') || fileName.includes('requirements/')) {
      return this.getPackageFromRequirements(text, position);
    } else if (fileName.endsWith('package.json')) {
      return this.getPackageFromJson(text, position);
    } else if (fileName.endsWith('cargo.toml')) {
      return this.getPackageFromToml(text, position);
    }

    return null;
  }

  /**
   * Extract package from requirements.txt line
   */
  private getPackageFromRequirements(
    text: string,
    position: vscode.Position
  ): { name: string; range: vscode.Range } | null {
    // Match package name at start of line
    const match = text.match(/^([a-zA-Z0-9][-a-zA-Z0-9._]*)/);
    if (!match) return null;

    const name = match[1].toLowerCase();
    const startChar = text.indexOf(match[1]);
    const endChar = startChar + match[1].length;

    // EC343: Also match if cursor is on version specifier after package name
    // But return the package name range
    if (position.character >= startChar && position.character <= text.length) {
      return {
        name,
        range: new vscode.Range(position.line, startChar, position.line, endChar)
      };
    }

    return null;
  }

  /**
   * Extract package from package.json line
   */
  private getPackageFromJson(
    text: string,
    position: vscode.Position
  ): { name: string; range: vscode.Range } | null {
    // EC344, EC345: Match on dependency key
    const match = text.match(/"([^"]+)"\s*:/);
    if (!match) return null;

    const name = match[1];
    const startChar = text.indexOf(`"${name}"`) + 1;
    const endChar = startChar + name.length;

    // Check if cursor is within the key
    if (position.character >= startChar && position.character <= endChar) {
      return {
        name,
        range: new vscode.Range(position.line, startChar, position.line, endChar)
      };
    }

    return null;
  }

  /**
   * Extract package from Cargo.toml line
   */
  private getPackageFromToml(
    text: string,
    position: vscode.Position
  ): { name: string; range: vscode.Range } | null {
    const match = text.match(/^([a-zA-Z0-9][-a-zA-Z0-9_]*)\s*=/);
    if (!match) return null;

    const name = match[1];
    const startChar = text.indexOf(match[1]);
    const endChar = startChar + match[1].length;

    if (position.character >= startChar && position.character <= endChar) {
      return {
        name,
        range: new vscode.Range(position.line, startChar, position.line, endChar)
      };
    }

    return null;
  }

  /**
   * Build hover content markdown
   */
  private buildHoverContent(result: PackageRisk): vscode.MarkdownString {
    const md = new vscode.MarkdownString();
    md.isTrusted = true;

    // Header with status icon
    const icon = this.getStatusIcon(result.risk_level);
    md.appendMarkdown(`## ${icon} ${result.name}\n\n`);

    // Risk level and score
    md.appendMarkdown(`**Risk Level**: ${result.risk_level}\n\n`);
    md.appendMarkdown(`**Risk Score**: ${result.risk_score.toFixed(2)}\n\n`);

    // EC346, EC350: List all signals
    if (result.signals.length > 0) {
      md.appendMarkdown(`**Signals Detected**:\n`);
      for (const signal of result.signals) {
        md.appendMarkdown(`- ${signal}\n`);
      }
      md.appendMarkdown('\n');
    }

    // Recommendation
    if (result.recommendation) {
      md.appendMarkdown(`**Recommendation**: ${result.recommendation}\n`);
    }

    return md;
  }

  private getStatusIcon(riskLevel: string): string {
    switch (riskLevel) {
      case 'SAFE': return '$(check)';  // EC347
      case 'SUSPICIOUS': return '$(warning)';
      case 'HIGH_RISK': return '$(error)';
      case 'NOT_FOUND': return '$(question)';
      default: return '$(info)';
    }
  }

  private getRegistry(document: vscode.TextDocument): string {
    const fileName = document.fileName.toLowerCase();
    if (fileName.endsWith('package.json')) return 'npm';
    if (fileName.endsWith('cargo.toml')) return 'crates';
    return 'pypi';
  }

  dispose(): void {
    this.cache.clear();
    this.disposables.forEach(d => d.dispose());
  }
}
```

### Tests to Enable (Hover)

```typescript
// tests/hover.test.ts

describe('T122.01 - Hover on package line', () => {
  it('shows risk tooltip when hovering on package name', async () => {
    // Create document with package
    // Hover on package name
    // Verify hover content includes risk level and signals
  });
});

describe('T122.02 - No hover on comment', () => {
  it('returns null when hovering on comment line', async () => {
    // INV123 verification
    // Create document with comment
    // Hover on comment line
    // Verify null returned
  });
});

describe('T122.03 - Safe package tooltip', () => {
  it('shows safe status for verified packages', async () => {
    // EC347 verification
    // Create document with flask
    // Mock core to return SAFE
    // Verify hover shows check icon and SAFE
  });
});
```

---

## Afternoon Session (4 hours)

### Task: W9.4 — Code Action Provider

**SPEC**: S123
**INVARIANTS**: INV124
**TESTS**: T123.01-T123.02

#### Implementation: src/actions.ts

```typescript
/**
 * IMPLEMENTS: S123
 * INVARIANTS: INV124 (only for phantom-guard diagnostics)
 * TESTS: T123.01-T123.02
 */

import * as vscode from 'vscode';

const DIAGNOSTIC_SOURCE = 'phantom-guard';

export class CodeActionProvider implements vscode.CodeActionProvider, vscode.Disposable {
  private disposables: vscode.Disposable[] = [];

  // Known typosquat corrections
  private typosquatCorrections: Map<string, string> = new Map([
    ['reqeusts', 'requests'],
    ['requets', 'requests'],
    ['requsets', 'requests'],
    ['flaks', 'flask'],
    ['flak', 'flask'],
    ['djano', 'django'],
    ['dango', 'django'],
    ['numoy', 'numpy'],
    ['nuumpy', 'numpy'],
    ['padas', 'pandas'],
    ['pandsa', 'pandas'],
    ['scikitlearn', 'scikit-learn'],
    ['sklean', 'scikit-learn'],
    // Add more common typosquats
  ]);

  constructor() {
    this.disposables.push(
      vscode.languages.registerCodeActionsProvider(
        [
          { pattern: '**/requirements.txt' },
          { pattern: '**/requirements/*.txt' },
          { pattern: '**/package.json' },
          { pattern: '**/Cargo.toml' }
        ],
        this,
        {
          providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
        }
      )
    );
  }

  /**
   * Provide code actions for diagnostics
   * INV124: Only for phantom-guard diagnostics
   */
  provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range | vscode.Selection,
    context: vscode.CodeActionContext,
    token: vscode.CancellationToken
  ): vscode.CodeAction[] {
    const actions: vscode.CodeAction[] = [];

    for (const diagnostic of context.diagnostics) {
      // INV124: Only act on phantom-guard diagnostics
      if (diagnostic.source !== DIAGNOSTIC_SOURCE) {
        continue;
      }

      // Extract package name from diagnostic
      const packageName = this.extractPackageName(document, diagnostic.range);
      if (!packageName) continue;

      // T123.02: Typosquat fix suggestion
      const correction = this.findTyposquatCorrection(packageName);
      if (correction) {
        const fixAction = this.createTyposquatFix(document, diagnostic, packageName, correction);
        actions.push(fixAction);
      }

      // Add "Ignore this package" action
      const ignoreAction = this.createIgnoreAction(packageName);
      actions.push(ignoreAction);

      // Add "Search PyPI" action for not-found packages
      if (diagnostic.code === 'NOT_FOUND') {
        const searchAction = this.createSearchAction(packageName);
        actions.push(searchAction);
      }
    }

    return actions;
  }

  /**
   * Extract package name from document range
   */
  private extractPackageName(document: vscode.TextDocument, range: vscode.Range): string | null {
    const text = document.getText(range);
    return text.trim() || null;
  }

  /**
   * Find typosquat correction for a package name
   * T123.02: Suggest fix for known typosquats
   */
  private findTyposquatCorrection(packageName: string): string | null {
    // Check direct map
    const direct = this.typosquatCorrections.get(packageName.toLowerCase());
    if (direct) return direct;

    // Could add fuzzy matching here in future
    return null;
  }

  /**
   * Create code action to fix typosquat
   */
  private createTyposquatFix(
    document: vscode.TextDocument,
    diagnostic: vscode.Diagnostic,
    wrongName: string,
    correctName: string
  ): vscode.CodeAction {
    const action = new vscode.CodeAction(
      `Replace with '${correctName}'`,
      vscode.CodeActionKind.QuickFix
    );

    action.edit = new vscode.WorkspaceEdit();
    action.edit.replace(document.uri, diagnostic.range, correctName);
    action.diagnostics = [diagnostic];
    action.isPreferred = true;

    return action;
  }

  /**
   * Create code action to ignore package
   */
  private createIgnoreAction(packageName: string): vscode.CodeAction {
    const action = new vscode.CodeAction(
      `Add '${packageName}' to ignore list`,
      vscode.CodeActionKind.QuickFix
    );

    // This would add to configuration
    action.command = {
      command: 'phantom-guard.ignorePackage',
      title: 'Ignore Package',
      arguments: [packageName]
    };

    return action;
  }

  /**
   * Create code action to search PyPI
   */
  private createSearchAction(packageName: string): vscode.CodeAction {
    const action = new vscode.CodeAction(
      `Search PyPI for '${packageName}'`,
      vscode.CodeActionKind.QuickFix
    );

    action.command = {
      command: 'vscode.open',
      title: 'Search PyPI',
      arguments: [vscode.Uri.parse(`https://pypi.org/search/?q=${encodeURIComponent(packageName)}`)]
    };

    return action;
  }

  dispose(): void {
    this.disposables.forEach(d => d.dispose());
  }
}
```

### Tests to Enable (Code Actions)

```typescript
// tests/actions.test.ts

describe('T123.01 - Code action for diagnostic', () => {
  it('provides code actions for phantom-guard diagnostics', async () => {
    // Create diagnostic with source = 'phantom-guard'
    // Request code actions
    // Verify actions are provided
  });

  it('does not provide actions for other sources', async () => {
    // INV124 verification
    // Create diagnostic with different source
    // Request code actions
    // Verify empty array
  });
});

describe('T123.02 - Typosquat fix suggestion', () => {
  it('suggests correct package name for typosquat', async () => {
    // Create diagnostic for 'reqeusts'
    // Request code actions
    // Verify 'Replace with requests' action exists
    // Verify action.edit replaces correctly
  });
});
```

---

## Integration with Extension

Update `src/extension.ts`:

```typescript
import { HoverProvider } from './hover';
import { CodeActionProvider } from './actions';

let hoverProvider: HoverProvider | undefined;
let codeActionProvider: CodeActionProvider | undefined;

async function doActivation(context: vscode.ExtensionContext): Promise<void> {
  core = new PhantomGuardCore();

  const isAvailable = await core.checkAvailability();
  if (!isAvailable) {
    throw new ActivationError('phantom-guard CLI not found');
  }

  // Register providers
  diagnosticProvider = new DiagnosticProvider(core);
  hoverProvider = new HoverProvider(core);
  codeActionProvider = new CodeActionProvider();

  context.subscriptions.push(
    diagnosticProvider,
    hoverProvider,
    codeActionProvider
  );
}
```

---

## End of Day Checklist

### Tests Status
- [ ] T122.01 passing (hover on package)
- [ ] T122.02 passing (no hover on comment) - INV123
- [ ] T122.03 passing (safe package tooltip)
- [ ] T123.01 passing (code action for diagnostic)
- [ ] T123.02 passing (typosquat fix)

### Code Quality
- [ ] npm run compile succeeds
- [ ] No TypeScript errors
- [ ] Hover content is informative and well-formatted
- [ ] Code actions are discoverable

### Manual Testing
- [ ] Hover over package shows risk details
- [ ] Hover over comment shows nothing
- [ ] Light bulb appears for diagnostics
- [ ] Typosquat fix works
- [ ] "Search PyPI" opens browser

### Commits
```bash
git add vscode/src/hover.ts vscode/src/actions.ts vscode/tests/
git commit -m "feat(S122,S123): Implement hover and code action providers

IMPLEMENTS: S122, S123
INVARIANTS: INV123 (null on non-package), INV124 (phantom-guard only)
TESTS: T122.01-T122.03, T123.01-T123.02
EDGE CASES: EC340-EC350

- Add HoverProvider with cached validation results
- Add CodeActionProvider with typosquat fix suggestions
- Implement ignore and search actions
- Support requirements.txt, package.json, Cargo.toml

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Dependencies for Day 4

Day 4 (Status bar + Configuration) requires:
- [ ] Extension activation working
- [ ] Diagnostic provider working (for status counts)

---

**Day 3 Focus**: Rich UX features - hover for details, quick fixes for common issues.
