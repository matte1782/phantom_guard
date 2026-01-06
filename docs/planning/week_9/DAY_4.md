# Week 9, Day 4 — Status Bar and Configuration

> **Date**: Day 4 of Week 9
> **Focus**: W9.5 — Status bar (S124) + Configuration (S125)
> **Hours**: 6 (3 + 3)
> **Prerequisites**: Day 3 complete (hover and code actions working)

---

## Goals

1. Implement status bar showing validation status
2. Implement configuration handling
3. Support for user preferences (threshold, enabled, pythonPath)
4. All Day 4 tests passing

---

## Morning Session (3 hours)

### Task: S124 — Status Bar

**SPEC**: S124
**INVARIANTS**: INV125
**TESTS**: T124.01-T124.02

#### Implementation: src/statusbar.ts

```typescript
/**
 * IMPLEMENTS: S124
 * INVARIANTS: INV125 (reflects most recent result)
 * TESTS: T124.01-T124.02
 */

import * as vscode from 'vscode';

export interface ValidationSummary {
  safe: number;
  suspicious: number;
  highRisk: number;
  notFound: number;
  validating: boolean;
}

export class StatusBarProvider implements vscode.Disposable {
  private statusBarItem: vscode.StatusBarItem;
  private summary: ValidationSummary = {
    safe: 0,
    suspicious: 0,
    highRisk: 0,
    notFound: 0,
    validating: false
  };

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBarItem.command = 'phantom-guard.showSummary';
    this.updateDisplay();
    this.statusBarItem.show();
  }

  /**
   * Update status bar with new summary
   * INV125: Reflects most recent validation result
   */
  update(summary: ValidationSummary): void {
    this.summary = { ...summary };
    this.updateDisplay();
  }

  /**
   * Set validating state
   */
  setValidating(validating: boolean): void {
    this.summary.validating = validating;
    this.updateDisplay();
  }

  /**
   * Update the display based on current state
   */
  private updateDisplay(): void {
    if (this.summary.validating) {
      this.statusBarItem.text = '$(loading~spin) Phantom Guard';
      this.statusBarItem.tooltip = 'Validating packages...';
      this.statusBarItem.backgroundColor = undefined;
      return;
    }

    const total = this.summary.safe + this.summary.suspicious +
                  this.summary.highRisk + this.summary.notFound;

    if (total === 0) {
      this.statusBarItem.text = '$(shield) Phantom Guard';
      this.statusBarItem.tooltip = 'No packages validated';
      this.statusBarItem.backgroundColor = undefined;
      return;
    }

    // T124.02: Shows error count
    if (this.summary.highRisk > 0) {
      this.statusBarItem.text = `$(error) ${this.summary.highRisk} high-risk`;
      this.statusBarItem.tooltip = this.buildTooltip();
      this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
      return;
    }

    if (this.summary.suspicious > 0) {
      this.statusBarItem.text = `$(warning) ${this.summary.suspicious} suspicious`;
      this.statusBarItem.tooltip = this.buildTooltip();
      this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
      return;
    }

    // All safe
    this.statusBarItem.text = `$(check) ${this.summary.safe} safe`;
    this.statusBarItem.tooltip = this.buildTooltip();
    this.statusBarItem.backgroundColor = undefined;
  }

  /**
   * Build detailed tooltip
   */
  private buildTooltip(): string {
    const lines = ['Phantom Guard Summary:'];
    if (this.summary.safe > 0) lines.push(`  $(check) ${this.summary.safe} safe`);
    if (this.summary.suspicious > 0) lines.push(`  $(warning) ${this.summary.suspicious} suspicious`);
    if (this.summary.highRisk > 0) lines.push(`  $(error) ${this.summary.highRisk} high-risk`);
    if (this.summary.notFound > 0) lines.push(`  $(question) ${this.summary.notFound} not found`);
    lines.push('', 'Click for details');
    return lines.join('\n');
  }

  /**
   * Get current summary
   */
  getSummary(): ValidationSummary {
    return { ...this.summary };
  }

  dispose(): void {
    this.statusBarItem.dispose();
  }
}
```

### Tests to Enable (Status Bar)

```typescript
// tests/statusbar.test.ts

describe('T124.01 - Status bar updates', () => {
  it('updates display when summary changes', () => {
    const provider = new StatusBarProvider();

    provider.update({ safe: 5, suspicious: 0, highRisk: 0, notFound: 0, validating: false });

    // Verify text shows "5 safe"
    // Verify no error background
  });

  it('shows validating state', () => {
    const provider = new StatusBarProvider();

    provider.setValidating(true);

    // Verify shows loading spinner
    // Verify tooltip says "Validating..."
  });
});

describe('T124.02 - Shows error count', () => {
  it('shows high-risk count with error background', () => {
    const provider = new StatusBarProvider();

    provider.update({ safe: 3, suspicious: 1, highRisk: 2, notFound: 0, validating: false });

    // Verify text shows "2 high-risk"
    // Verify error background color
  });

  it('shows suspicious count when no high-risk', () => {
    const provider = new StatusBarProvider();

    provider.update({ safe: 3, suspicious: 2, highRisk: 0, notFound: 0, validating: false });

    // Verify text shows "2 suspicious"
    // Verify warning background color
  });
});
```

---

## Afternoon Session (3 hours)

### Task: S125 — Configuration

**SPEC**: S125
**INVARIANTS**: INV126
**TESTS**: T125.01-T125.02

#### Implementation: src/config.ts

```typescript
/**
 * IMPLEMENTS: S125
 * INVARIANTS: INV126 (config changes trigger re-validation)
 * TESTS: T125.01-T125.02
 */

import * as vscode from 'vscode';

export interface PhantomGuardConfig {
  enabled: boolean;
  pythonPath: string;
  threshold: number;
  ignoredPackages: string[];
}

export class ConfigProvider implements vscode.Disposable {
  private config: PhantomGuardConfig;
  private disposables: vscode.Disposable[] = [];
  private onConfigChangeEmitter = new vscode.EventEmitter<PhantomGuardConfig>();

  /**
   * Event fired when configuration changes
   * INV126: Configuration changes trigger re-validation
   */
  readonly onConfigChange = this.onConfigChangeEmitter.event;

  constructor() {
    this.config = this.loadConfig();

    // Watch for configuration changes
    this.disposables.push(
      vscode.workspace.onDidChangeConfiguration(event => {
        if (event.affectsConfiguration('phantomGuard')) {
          const oldConfig = this.config;
          this.config = this.loadConfig();

          // INV126: Fire change event to trigger re-validation
          this.onConfigChangeEmitter.fire(this.config);

          // Log significant changes
          if (oldConfig.threshold !== this.config.threshold) {
            console.log(`Phantom Guard threshold changed: ${oldConfig.threshold} -> ${this.config.threshold}`);
          }
          if (oldConfig.enabled !== this.config.enabled) {
            console.log(`Phantom Guard enabled: ${this.config.enabled}`);
          }
        }
      })
    );
  }

  /**
   * Load configuration from VS Code settings
   */
  private loadConfig(): PhantomGuardConfig {
    const config = vscode.workspace.getConfiguration('phantomGuard');

    return {
      enabled: config.get<boolean>('enabled', true),
      pythonPath: config.get<string>('pythonPath', ''),
      threshold: config.get<number>('threshold', 0.5),
      ignoredPackages: config.get<string[]>('ignoredPackages', [])
    };
  }

  /**
   * Get current configuration
   */
  getConfig(): PhantomGuardConfig {
    return { ...this.config };
  }

  /**
   * Check if extension is enabled
   */
  isEnabled(): boolean {
    return this.config.enabled;
  }

  /**
   * Get Python path (or default)
   */
  getPythonPath(): string {
    return this.config.pythonPath || 'python';
  }

  /**
   * Get risk threshold
   */
  getThreshold(): number {
    return this.config.threshold;
  }

  /**
   * Check if package is ignored
   */
  isIgnored(packageName: string): boolean {
    return this.config.ignoredPackages.includes(packageName.toLowerCase());
  }

  /**
   * Add package to ignore list
   */
  async ignorePackage(packageName: string): Promise<void> {
    const config = vscode.workspace.getConfiguration('phantomGuard');
    const current = config.get<string[]>('ignoredPackages', []);

    if (!current.includes(packageName.toLowerCase())) {
      await config.update(
        'ignoredPackages',
        [...current, packageName.toLowerCase()],
        vscode.ConfigurationTarget.Workspace
      );
    }
  }

  dispose(): void {
    this.onConfigChangeEmitter.dispose();
    this.disposables.forEach(d => d.dispose());
  }
}
```

### Tests to Enable (Configuration)

```typescript
// tests/config.test.ts

describe('T125.01 - Config change triggers revalidate', () => {
  it('fires onConfigChange when settings update', async () => {
    const provider = new ConfigProvider();
    let changeCount = 0;

    provider.onConfigChange(() => changeCount++);

    // Simulate config change
    // Verify changeCount increased
    // INV126 verification
  });
});

describe('T125.02 - Threshold config works', () => {
  it('respects threshold setting', () => {
    const provider = new ConfigProvider();

    // Mock config with threshold = 0.7
    // Verify getThreshold() returns 0.7
  });

  it('defaults to 0.5 when not set', () => {
    const provider = new ConfigProvider();

    // Verify default threshold is 0.5
  });
});
```

---

## Integration with Extension

Update `src/extension.ts`:

```typescript
import { StatusBarProvider, ValidationSummary } from './statusbar';
import { ConfigProvider } from './config';

let statusBarProvider: StatusBarProvider | undefined;
let configProvider: ConfigProvider | undefined;

async function doActivation(context: vscode.ExtensionContext): Promise<void> {
  core = new PhantomGuardCore();
  configProvider = new ConfigProvider();

  // Check if enabled
  if (!configProvider.isEnabled()) {
    console.log('Phantom Guard is disabled');
    return;
  }

  // Use configured Python path
  core.setPythonPath(configProvider.getPythonPath());

  const isAvailable = await core.checkAvailability();
  if (!isAvailable) {
    throw new ActivationError('phantom-guard CLI not found');
  }

  // Register providers
  statusBarProvider = new StatusBarProvider();
  diagnosticProvider = new DiagnosticProvider(core, configProvider, statusBarProvider);
  hoverProvider = new HoverProvider(core);
  codeActionProvider = new CodeActionProvider();

  // INV126: Re-validate when config changes
  configProvider.onConfigChange(() => {
    diagnosticProvider?.revalidateAll();
  });

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('phantom-guard.showSummary', () => {
      const summary = statusBarProvider?.getSummary();
      if (summary) {
        vscode.window.showInformationMessage(
          `Phantom Guard: ${summary.safe} safe, ${summary.suspicious} suspicious, ${summary.highRisk} high-risk`
        );
      }
    }),
    vscode.commands.registerCommand('phantom-guard.ignorePackage', async (packageName: string) => {
      await configProvider?.ignorePackage(packageName);
      vscode.window.showInformationMessage(`Added '${packageName}' to ignore list`);
    })
  );

  context.subscriptions.push(
    configProvider,
    statusBarProvider,
    diagnosticProvider,
    hoverProvider,
    codeActionProvider
  );
}
```

---

## End of Day Checklist

### Tests Status
- [ ] T124.01 passing (status bar updates)
- [ ] T124.02 passing (shows error count)
- [ ] T125.01 passing (config change triggers revalidate) - INV126
- [ ] T125.02 passing (threshold config works)

### Code Quality
- [ ] npm run compile succeeds
- [ ] No TypeScript errors
- [ ] Status bar is visible and informative
- [ ] Configuration UI works in VS Code settings

### Manual Testing
- [ ] Status bar shows summary
- [ ] Status bar updates after validation
- [ ] Clicking status bar shows details
- [ ] Changing threshold in settings works
- [ ] Disabling extension hides diagnostics
- [ ] Ignore package adds to config

### Package.json Updates

Ensure `contributes.configuration` includes all settings:

```json
{
  "contributes": {
    "configuration": {
      "title": "Phantom Guard",
      "properties": {
        "phantomGuard.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable Phantom Guard validation"
        },
        "phantomGuard.pythonPath": {
          "type": "string",
          "default": "",
          "description": "Path to Python executable"
        },
        "phantomGuard.threshold": {
          "type": "number",
          "default": 0.5,
          "minimum": 0,
          "maximum": 1,
          "description": "Risk score threshold for warnings"
        },
        "phantomGuard.ignoredPackages": {
          "type": "array",
          "items": { "type": "string" },
          "default": [],
          "description": "Packages to ignore"
        }
      }
    },
    "commands": [
      {
        "command": "phantom-guard.showSummary",
        "title": "Phantom Guard: Show Summary"
      },
      {
        "command": "phantom-guard.ignorePackage",
        "title": "Phantom Guard: Ignore Package"
      }
    ]
  }
}
```

### Commits
```bash
git add vscode/src/statusbar.ts vscode/src/config.ts vscode/package.json
git commit -m "feat(S124,S125): Implement status bar and configuration

IMPLEMENTS: S124, S125
INVARIANTS: INV125 (reflects most recent), INV126 (config triggers revalidate)
TESTS: T124.01-T124.02, T125.01-T125.02

- Add StatusBarProvider with validation summary
- Add ConfigProvider with settings management
- Implement ignore package functionality
- Support threshold and pythonPath configuration

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Dependencies for Day 5

Day 5 (Integration tests) requires:
- [ ] All providers implemented
- [ ] Commands registered
- [ ] Configuration working

---

**Day 4 Focus**: User experience polish - visible status and customizable behavior.
