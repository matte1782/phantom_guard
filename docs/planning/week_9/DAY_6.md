# Week 9, Day 6 — Integration Tests Part 2 + Hostile Review Prep

> **Date**: Day 6 of Week 9
> **Focus**: W9.7 — Complete integration tests + Hostile review preparation
> **Hours**: 8 (5 tests + 3 review prep)
> **Prerequisites**: Day 5 complete (test infrastructure, activation/diagnostic tests)

---

## Goals

1. Complete hover and code action integration tests
2. Write end-to-end workflow tests
3. Verify all acceptance criteria met
4. Prepare for hostile review

---

## Morning Session (5 hours)

### Task: Hover Integration Tests

#### tests/integration/hover.test.ts

```typescript
/**
 * TESTS: T122.01-T122.03 (integration)
 * Verifies hover provider in real VS Code environment
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';

suite('Hover Integration', () => {
  const fixturesPath = path.resolve(__dirname, '../fixtures');
  let document: vscode.TextDocument;

  suiteSetup(async function() {
    this.timeout(10000);
    const extension = vscode.extensions.getExtension('phantom-guard.phantom-guard');
    await extension?.activate();
  });

  setup(async function() {
    const uri = vscode.Uri.file(path.join(fixturesPath, 'requirements.txt'));
    document = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(document);
    await sleep(1000); // Wait for validation
  });

  teardown(async function() {
    await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
  });

  /**
   * T122.01: Hover on package line shows risk tooltip
   */
  test('shows risk tooltip on package hover', async function() {
    this.timeout(5000);

    // Find line with 'flask'
    let flaskLine = -1;
    for (let i = 0; i < document.lineCount; i++) {
      if (document.lineAt(i).text.startsWith('flask')) {
        flaskLine = i;
        break;
      }
    }
    assert.ok(flaskLine >= 0, 'Should find flask line');

    // Request hover at flask position
    const position = new vscode.Position(flaskLine, 2);
    const hovers = await vscode.commands.executeCommand<vscode.Hover[]>(
      'vscode.executeHoverProvider',
      document.uri,
      position
    );

    assert.ok(hovers && hovers.length > 0, 'Should have hover results');

    // Check hover content
    const content = hovers[0].contents[0];
    assert.ok(content, 'Should have hover content');

    const text = typeof content === 'string' ? content :
                 (content as vscode.MarkdownString).value;
    assert.ok(text.includes('Risk'), 'Hover should mention risk');
  });

  /**
   * T122.02: No hover on comment line
   * INV123 verification
   */
  test('returns null for comment lines', async function() {
    // Find comment line
    let commentLine = -1;
    for (let i = 0; i < document.lineCount; i++) {
      if (document.lineAt(i).text.trim().startsWith('#')) {
        commentLine = i;
        break;
      }
    }
    assert.ok(commentLine >= 0, 'Should find comment line');

    const position = new vscode.Position(commentLine, 2);
    const hovers = await vscode.commands.executeCommand<vscode.Hover[]>(
      'vscode.executeHoverProvider',
      document.uri,
      position
    );

    // Should have no hovers or empty array
    const hasPhantomGuardHover = hovers?.some(h => {
      const text = typeof h.contents[0] === 'string' ? h.contents[0] :
                   (h.contents[0] as vscode.MarkdownString).value;
      return text.includes('Phantom Guard') || text.includes('Risk');
    });

    assert.ok(!hasPhantomGuardHover, 'Should not have Phantom Guard hover on comment');
  });

  /**
   * T122.03: Safe package shows safe tooltip
   */
  test('shows safe status for verified packages', async function() {
    this.timeout(5000);

    // Find flask line (should be safe)
    let flaskLine = -1;
    for (let i = 0; i < document.lineCount; i++) {
      const text = document.lineAt(i).text;
      if (text.startsWith('flask') && !text.includes('flask-')) {
        flaskLine = i;
        break;
      }
    }
    assert.ok(flaskLine >= 0, 'Should find flask line');

    const position = new vscode.Position(flaskLine, 2);
    const hovers = await vscode.commands.executeCommand<vscode.Hover[]>(
      'vscode.executeHoverProvider',
      document.uri,
      position
    );

    assert.ok(hovers && hovers.length > 0, 'Should have hover');

    const content = hovers[0].contents[0];
    const text = typeof content === 'string' ? content :
                 (content as vscode.MarkdownString).value;

    // Flask should show as SAFE
    assert.ok(
      text.includes('SAFE') || text.includes('safe'),
      'Flask should show as safe'
    );
  });
});

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Task: End-to-End Workflow Tests

#### tests/integration/workflow.test.ts

```typescript
/**
 * End-to-end workflow tests
 * Verifies complete user workflows
 */

import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

suite('End-to-End Workflows', () => {
  const fixturesPath = path.resolve(__dirname, '../fixtures');

  suiteSetup(async function() {
    this.timeout(10000);
    const extension = vscode.extensions.getExtension('phantom-guard.phantom-guard');
    await extension?.activate();
  });

  /**
   * Workflow: Open file -> See diagnostics -> Hover for details
   */
  test('complete validation workflow', async function() {
    this.timeout(15000);

    // Step 1: Open requirements.txt
    const uri = vscode.Uri.file(path.join(fixturesPath, 'requirements.txt'));
    const document = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(document);

    // Step 2: Wait for diagnostics
    await waitForDiagnostics(document.uri, 5000);

    // Step 3: Verify diagnostics exist
    const diagnostics = vscode.languages.getDiagnostics(document.uri);
    assert.ok(diagnostics.length > 0, 'Should have diagnostics');

    // Step 4: Find a diagnostic and hover
    const firstDiag = diagnostics[0];
    const hovers = await vscode.commands.executeCommand<vscode.Hover[]>(
      'vscode.executeHoverProvider',
      document.uri,
      firstDiag.range.start
    );

    // Step 5: Verify hover provides additional info
    assert.ok(hovers && hovers.length > 0, 'Should have hover info');

    // Cleanup
    await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
  });

  /**
   * Workflow: Typosquat detected -> Quick fix available -> Apply fix
   */
  test('typosquat fix workflow', async function() {
    this.timeout(15000);

    // Create temp file with typosquat
    const tempFile = path.join(fixturesPath, 'temp_requirements.txt');
    fs.writeFileSync(tempFile, 'reqeusts>=2.0\n');

    try {
      // Open the file
      const uri = vscode.Uri.file(tempFile);
      const document = await vscode.workspace.openTextDocument(uri);
      await vscode.window.showTextDocument(document);

      // Wait for diagnostics
      await waitForDiagnostics(document.uri, 5000);

      // Verify typosquat diagnostic
      const diagnostics = vscode.languages.getDiagnostics(document.uri);
      const typosquatDiag = diagnostics.find(d =>
        d.message.includes('HIGH_RISK') || d.message.includes('reqeusts')
      );
      assert.ok(typosquatDiag, 'Should have typosquat diagnostic');

      // Get code actions
      const actions = await vscode.commands.executeCommand<vscode.CodeAction[]>(
        'vscode.executeCodeActionProvider',
        document.uri,
        typosquatDiag.range
      );

      // Verify fix action exists
      const fixAction = actions?.find(a =>
        a.title.includes('Replace') && a.title.includes('requests')
      );
      assert.ok(fixAction, 'Should have fix action for typosquat');

      // Apply the fix
      if (fixAction?.edit) {
        await vscode.workspace.applyEdit(fixAction.edit);

        // Verify content changed
        const newContent = document.getText();
        assert.ok(
          newContent.includes('requests'),
          'Content should have correct package name after fix'
        );
      }

    } finally {
      // Cleanup
      await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
      if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile);
      }
    }
  });

  /**
   * Workflow: Configure threshold -> Verify diagnostics change
   */
  test('configuration change workflow', async function() {
    this.timeout(15000);

    // Open file
    const uri = vscode.Uri.file(path.join(fixturesPath, 'requirements.txt'));
    const document = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(document);

    await waitForDiagnostics(document.uri, 5000);

    // Get initial diagnostic count
    const initialDiags = vscode.languages.getDiagnostics(document.uri);
    const initialCount = initialDiags.length;

    // Change threshold to very high (should reduce warnings)
    const config = vscode.workspace.getConfiguration('phantomGuard');
    const originalThreshold = config.get<number>('threshold');

    try {
      await config.update('threshold', 0.95, vscode.ConfigurationTarget.Workspace);

      // Wait for re-validation
      await sleep(2000);

      // Check if diagnostic count changed
      const newDiags = vscode.languages.getDiagnostics(document.uri);

      // With higher threshold, should have fewer or equal warnings
      assert.ok(
        newDiags.length <= initialCount,
        'Higher threshold should not increase warnings'
      );

    } finally {
      // Restore original threshold
      await config.update('threshold', originalThreshold, vscode.ConfigurationTarget.Workspace);
      await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
    }
  });

  /**
   * Workflow: Status bar shows summary
   */
  test('status bar workflow', async function() {
    this.timeout(10000);

    // Open file
    const uri = vscode.Uri.file(path.join(fixturesPath, 'requirements.txt'));
    const document = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(document);

    await waitForDiagnostics(document.uri, 5000);

    // Execute show summary command
    await vscode.commands.executeCommand('phantom-guard.showSummary');

    // If we got here without error, command works
    // (Information message shown to user)

    await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
  });
});

async function waitForDiagnostics(uri: vscode.Uri, timeout: number): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('Timeout')), timeout);
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

## Afternoon Session (3 hours)

### Task: Hostile Review Preparation

#### 1. Run All Tests

```bash
cd vscode

# Unit tests
npm run test:unit

# Integration tests (requires VS Code)
npm run test:integration

# Check coverage
npm run test -- --coverage
```

#### 2. Quality Checks

```bash
# TypeScript compilation
npm run compile

# Lint check (if configured)
npm run lint

# Type check
npx tsc --noEmit
```

#### 3. Create Test Summary Document

Create `vscode/TEST_SUMMARY.md`:

```markdown
# VS Code Extension Test Summary

## Test Counts

| Category | Tests | Passing | Failing |
|:---------|:------|:--------|:--------|
| Unit Tests | XX | XX | 0 |
| Integration | XX | XX | 0 |
| **Total** | XX | XX | **0** |

## Coverage

| Module | Line % | Branch % | Target |
|:-------|:-------|:---------|:-------|
| extension.ts | XX% | XX% | 80% |
| core.ts | XX% | XX% | 80% |
| diagnostics.ts | XX% | XX% | 80% |
| hover.ts | XX% | XX% | 80% |
| actions.ts | XX% | XX% | 80% |
| statusbar.ts | XX% | XX% | 80% |
| config.ts | XX% | XX% | 80% |
| **Overall** | XX% | XX% | **80%** |

## Security Tests

| Test | Status |
|:-----|:-------|
| T126.02 - Shell injection prevention | PASS |
| T126.03 - Package name validation | PASS |

## Performance Tests

| Test | Result | Budget |
|:-----|:-------|:-------|
| T120.01 - Activation time | XXms | <500ms |
| T126.04 - First validation | XXms | <500ms |

## Invariant Verification

| INV_ID | Test | Status |
|:-------|:-----|:-------|
| INV120 | Async I/O | PASS |
| INV121 | 500ms timeout | PASS |
| INV122 | Clear on close | PASS |
| INV123 | Null on non-package | PASS |
| INV124 | Source check | PASS |
| INV125 | Most recent result | PASS |
| INV126 | Config trigger | PASS |
| INV127 | Graceful spawn | PASS |
| INV128 | No shell injection | PASS |
```

#### 4. Pre-Review Checklist

```markdown
## Week 9 Completion Checklist

### Implementation Complete
- [ ] W9.1 - Extension activation (S120)
- [ ] W9.2 - Diagnostic provider (S121)
- [ ] W9.3 - Hover provider (S122)
- [ ] W9.4 - Code action provider (S123)
- [ ] W9.5 - Status bar (S124) + Configuration (S125)
- [ ] W9.6 - Core integration (S126)
- [ ] W9.7 - Integration tests

### Tests Passing
- [ ] T120.01-T120.04 (Activation)
- [ ] T121.01-T121.05 (Diagnostics)
- [ ] T122.01-T122.03 (Hover)
- [ ] T123.01-T123.02 (Code Actions)
- [ ] T124.01-T124.02 (Status Bar)
- [ ] T125.01-T125.02 (Configuration)
- [ ] T126.01-T126.04 (Core Integration)

### Quality Gates
- [ ] npm run compile passes
- [ ] Coverage >= 80%
- [ ] All security tests pass
- [ ] Performance budgets met

### Documentation
- [ ] package.json complete
- [ ] README.md written
- [ ] CHANGELOG entry added
```

---

## End of Day Checklist

### Tests Status
- [ ] T122.01-T122.03 passing (hover)
- [ ] T123.01-T123.02 passing (code actions)
- [ ] All workflow tests passing
- [ ] Total: 89 tests passing (per SPECIFICATION_V0.2.0)

### Coverage
- [ ] Overall >= 80%
- [ ] All modules >= 75%

### Security
- [ ] Shell injection tests pass
- [ ] Package validation tests pass

### Performance
- [ ] Activation < 500ms
- [ ] First validation < 500ms

### Commits
```bash
git add vscode/tests/ vscode/TEST_SUMMARY.md
git commit -m "test(S122-S126): Complete VS Code extension integration tests

TESTS: T122.01-T122.03, T123.01-T123.02, workflow tests
COVERAGE: 80%+ across all modules

- Add hover integration tests
- Add code action integration tests
- Add end-to-end workflow tests
- Add test summary documentation
- Prepare for hostile review

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Ready for Hostile Review

After completing Day 6:

```bash
/hostile-review
```

### Expected Review Focus

1. **Security**: Shell injection prevention (T126.02, T126.03)
2. **Performance**: Activation and validation timing
3. **Reliability**: Error handling, graceful degradation
4. **UX**: Diagnostic clarity, hover usefulness
5. **Code Quality**: Coverage, type safety

### Potential Issues to Address

| Risk | Mitigation |
|:-----|:-----------|
| Coverage < 80% | Add more unit tests |
| Security test gaps | Review core.ts thoroughly |
| Slow activation | Profile and optimize |
| Flaky integration tests | Add retries, increase timeouts |

---

## Week 9 Summary

| Day | Focus | Hours | Status |
|:----|:------|:------|:-------|
| Day 1 | Scaffold + Activation + Core | 8 | |
| Day 2 | Diagnostic Provider | 6 | |
| Day 3 | Hover + Code Actions | 8 | |
| Day 4 | Status Bar + Config | 6 | |
| Day 5 | Integration Tests (Part 1) | 8 | |
| Day 6 | Integration Tests (Part 2) + Review | 8 | |
| **Total** | | **44** | |
| Buffer | | 4 | |
| **Week Total** | | **48** | |

---

**Day 6 Focus**: Complete testing and prepare for hostile validation. No new features - just quality assurance.

**Next Step**: Run `/hostile-review` for Week 9 approval.
