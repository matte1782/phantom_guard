# Week 9, Day 5 — Integration Tests Part 1

> **Date**: Day 5 of Week 9
> **Focus**: W9.7 — Extension integration tests (Part 1)
> **Hours**: 8
> **Prerequisites**: Days 1-4 complete (all providers implemented)

---

## Goals

1. Set up VS Code extension testing infrastructure
2. Write integration tests for activation and core
3. Write integration tests for diagnostics
4. Achieve 60% of integration test coverage

---

## Morning Session (4 hours)

### Task: Testing Infrastructure Setup

#### Test Framework Choice

Based on Gate 3 decisions:
- Use `@vscode/test-electron` for true VS Code environment tests
- Use `vitest` for unit tests with mocked VS Code API
- Use mock-based approach for CI (faster, more reliable)

#### Test Structure

```
vscode/
├── tests/
│   ├── unit/                    # Unit tests (vitest)
│   │   ├── extension.test.ts
│   │   ├── core.test.ts
│   │   ├── diagnostics.test.ts
│   │   ├── hover.test.ts
│   │   ├── actions.test.ts
│   │   ├── statusbar.test.ts
│   │   └── config.test.ts
│   ├── integration/             # Integration tests (electron)
│   │   ├── setup.ts
│   │   ├── activation.test.ts
│   │   ├── diagnostics.test.ts
│   │   ├── hover.test.ts
│   │   └── workflow.test.ts
│   └── fixtures/                # Test fixtures
│       ├── requirements.txt
│       ├── package.json
│       └── Cargo.toml
└── .vscode-test/               # Test workspace
```

#### Test Setup: tests/integration/setup.ts

```typescript
/**
 * Integration test setup for VS Code extension
 */

import * as path from 'path';
import { runTests } from '@vscode/test-electron';

async function main() {
  try {
    const extensionDevelopmentPath = path.resolve(__dirname, '../../');
    const extensionTestsPath = path.resolve(__dirname, './index');
    const testWorkspace = path.resolve(__dirname, '../fixtures');

    await runTests({
      extensionDevelopmentPath,
      extensionTestsPath,
      launchArgs: [testWorkspace, '--disable-extensions']
    });
  } catch (err) {
    console.error('Failed to run tests');
    process.exit(1);
  }
}

main();
```

#### Test Fixtures

Create `tests/fixtures/requirements.txt`:
```
# Safe packages
flask==2.0.0
requests>=2.28.0

# Suspicious (for testing)
flask-gpt-helper
django-ai-utils

# Typosquat
reqeusts
```

Create `tests/fixtures/package.json`:
```json
{
  "name": "test-project",
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0"
  }
}
```

---

### Task: Activation Integration Tests

#### tests/integration/activation.test.ts

```typescript
/**
 * TESTS: T120.01-T120.04 (integration)
 * Verifies extension activation in real VS Code environment
 */

import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Activation Integration', () => {
  const extensionId = 'phantom-guard.phantom-guard';

  /**
   * T120.01: Activation < 500ms
   */
  test('activates within 500ms', async function() {
    this.timeout(5000);

    const start = Date.now();

    const extension = vscode.extensions.getExtension(extensionId);
    assert.ok(extension, 'Extension should be installed');

    await extension.activate();

    const elapsed = Date.now() - start;
    assert.ok(elapsed < 500, `Activation took ${elapsed}ms, expected < 500ms`);
  });

  /**
   * T120.02: Timeout handled gracefully
   */
  test('handles activation timeout gracefully', async function() {
    this.timeout(10000);

    // This test verifies that slow activation doesn't crash
    // The extension should show a warning but continue
    const extension = vscode.extensions.getExtension(extensionId);
    assert.ok(extension);

    // Should not throw
    await extension.activate();
  });

  /**
   * Verify extension is active after activation
   */
  test('extension is active after activation', async function() {
    const extension = vscode.extensions.getExtension(extensionId);
    assert.ok(extension);

    await extension.activate();

    assert.ok(extension.isActive, 'Extension should be active');
  });

  /**
   * Verify commands are registered
   */
  test('commands are registered', async function() {
    const extension = vscode.extensions.getExtension(extensionId);
    await extension?.activate();

    const commands = await vscode.commands.getCommands(true);

    assert.ok(
      commands.includes('phantom-guard.showSummary'),
      'showSummary command should be registered'
    );
    assert.ok(
      commands.includes('phantom-guard.ignorePackage'),
      'ignorePackage command should be registered'
    );
  });
});
```

---

## Afternoon Session (4 hours)

### Task: Diagnostics Integration Tests

#### tests/integration/diagnostics.test.ts

```typescript
/**
 * TESTS: T121.01-T121.05 (integration)
 * Verifies diagnostic provider in real VS Code environment
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';

suite('Diagnostics Integration', () => {
  const fixturesPath = path.resolve(__dirname, '../fixtures');
  let document: vscode.TextDocument;

  suiteSetup(async function() {
    this.timeout(10000);

    // Ensure extension is activated
    const extension = vscode.extensions.getExtension('phantom-guard.phantom-guard');
    await extension?.activate();
  });

  setup(async function() {
    // Open requirements.txt fixture
    const uri = vscode.Uri.file(path.join(fixturesPath, 'requirements.txt'));
    document = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(document);

    // Wait for diagnostics to be computed
    await waitForDiagnostics(document.uri, 5000);
  });

  teardown(async function() {
    await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
  });

  /**
   * T121.01: Safe package = no diagnostic
   */
  test('safe packages have no diagnostics', async function() {
    const diagnostics = vscode.languages.getDiagnostics(document.uri);

    // flask and requests should not have diagnostics
    const flaskDiag = diagnostics.find(d =>
      document.getText(d.range).toLowerCase().includes('flask') &&
      !document.getText(d.range).includes('flask-')
    );

    assert.ok(!flaskDiag, 'flask should not have a diagnostic');
  });

  /**
   * T121.02: Suspicious = warning
   */
  test('suspicious packages have warning diagnostics', async function() {
    const diagnostics = vscode.languages.getDiagnostics(document.uri);

    const suspicious = diagnostics.filter(d =>
      d.severity === vscode.DiagnosticSeverity.Warning
    );

    assert.ok(suspicious.length > 0, 'Should have warning diagnostics');
  });

  /**
   * T121.03: High risk = error
   */
  test('high-risk packages have error diagnostics', async function() {
    const diagnostics = vscode.languages.getDiagnostics(document.uri);

    // reqeusts should be high-risk (typosquat)
    const highRisk = diagnostics.filter(d =>
      d.severity === vscode.DiagnosticSeverity.Error
    );

    assert.ok(highRisk.length > 0, 'Should have error diagnostics for typosquats');
  });

  /**
   * T121.04: Diagnostics cleared on close
   * INV122 verification
   */
  test('diagnostics are cleared when document is closed', async function() {
    // Verify diagnostics exist
    let diagnostics = vscode.languages.getDiagnostics(document.uri);
    assert.ok(diagnostics.length > 0, 'Should have diagnostics before close');

    // Close document
    await vscode.commands.executeCommand('workbench.action.closeActiveEditor');

    // Wait a bit for cleanup
    await sleep(500);

    // Verify diagnostics are cleared
    diagnostics = vscode.languages.getDiagnostics(document.uri);
    assert.strictEqual(diagnostics.length, 0, 'Diagnostics should be cleared after close');
  });

  /**
   * T121.05: Debounce works
   * EC327 verification
   */
  test('rapid edits are debounced', async function() {
    this.timeout(10000);

    // Make rapid edits
    const editor = vscode.window.activeTextEditor;
    assert.ok(editor);

    const validationCounts: number[] = [];

    // Monitor diagnostic changes
    const disposable = vscode.languages.onDidChangeDiagnostics(e => {
      if (e.uris.some(u => u.toString() === document.uri.toString())) {
        validationCounts.push(Date.now());
      }
    });

    try {
      // Make 5 rapid edits
      for (let i = 0; i < 5; i++) {
        await editor.edit(eb => {
          eb.insert(new vscode.Position(0, 0), `# Edit ${i}\n`);
        });
        await sleep(50); // 50ms between edits
      }

      // Wait for debounce to complete
      await sleep(1000);

      // Should have fewer than 5 validation events due to debouncing
      assert.ok(
        validationCounts.length < 5,
        `Expected debouncing, got ${validationCounts.length} validations`
      );
    } finally {
      disposable.dispose();
    }
  });
});

// Helper functions
async function waitForDiagnostics(uri: vscode.Uri, timeout: number): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('Timeout waiting for diagnostics')), timeout);

    const check = () => {
      const diagnostics = vscode.languages.getDiagnostics(uri);
      if (diagnostics.length > 0) {
        clearTimeout(timer);
        resolve();
      } else {
        setTimeout(check, 100);
      }
    };

    check();
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

---

## Package.json Test Scripts

Update `vscode/package.json`:

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:unit": "vitest run tests/unit",
    "test:integration": "node ./out/tests/integration/setup.js",
    "pretest:integration": "npm run compile"
  },
  "devDependencies": {
    "@vscode/test-electron": "^2.3.0",
    "vitest": "^1.0.0",
    "@vitest/coverage-v8": "^1.0.0"
  }
}
```

---

## End of Day Checklist

### Tests Status
- [ ] Integration test infrastructure set up
- [ ] T120.01-T120.04 integration tests written
- [ ] T121.01-T121.05 integration tests written
- [ ] All integration tests pass in local VS Code
- [ ] 60%+ of integration tests complete

### Test Fixtures
- [ ] requirements.txt with safe/suspicious/typosquat packages
- [ ] package.json with npm dependencies
- [ ] Cargo.toml with crates dependencies

### Code Quality
- [ ] Tests are isolated and repeatable
- [ ] Proper setup/teardown in each suite
- [ ] Timeouts set appropriately

### Commits
```bash
git add vscode/tests/integration/ vscode/tests/fixtures/
git commit -m "test(S120,S121): Add extension integration tests

TESTS: T120.01-T120.04, T121.01-T121.05
COVERAGE: Extension activation, diagnostic provider

- Add integration test infrastructure with @vscode/test-electron
- Add test fixtures for requirements.txt, package.json, Cargo.toml
- Implement activation tests (timing, commands)
- Implement diagnostic tests (severity mapping, cleanup, debounce)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Dependencies for Day 6

Day 6 (Integration tests Part 2) requires:
- [ ] Test infrastructure working
- [ ] Fixtures created
- [ ] Activation and diagnostic tests passing

---

**Day 5 Focus**: Testing infrastructure and core integration tests. Solid test foundation enables confident Day 6 completion.
