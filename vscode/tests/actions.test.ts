/**
 * SPEC: S123 - Code Action Provider
 * TEST_IDs: T123.01-T123.02
 * INVARIANTS: INV124
 *
 * Tests for VS Code quick fix actions.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Uri, Range, Diagnostic, DiagnosticSeverity, CancellationToken } from './__mocks__/vscode';

// Mock vscode module
vi.mock('vscode', () => import('./__mocks__/vscode'));

// Mock TextDocument
function createMockDocument(content: string, fileName: string) {
  const lines = content.split('\n');
  return {
    uri: Uri.file(fileName),
    getText: (range?: Range) => {
      if (range) {
        return lines[range.startLine]?.substring(range.startCharacter, range.endCharacter) || '';
      }
      return content;
    },
    lineAt: (line: number) => ({
      text: lines[line] || '',
      range: new Range(line, 0, line, lines[line]?.length || 0),
      rangeIncludingLineBreak: new Range(line, 0, line + 1, 0),
    }),
    languageId: 'plaintext',
  };
}

describe('Code Action Provider (S123)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // T123.01: Code action for diagnostic
  // =========================================================================
  it('T123.01: provides code action for diagnostic', async () => {
    /**
     * SPEC: S123
     * TEST_ID: T123.01
     * INV_ID: INV124
     *
     * Given: Diagnostic on suspicious package
     * When: User invokes quick fix
     * Then: Code action menu shows relevant actions
     */
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    const document = createMockDocument('flask-gpt==1.0.0\n', '/test/requirements.txt');
    const range = new Range(0, 0, 0, 9);

    const diagnostic = new Diagnostic(range, 'Suspicious package', DiagnosticSeverity.Warning);
    diagnostic.source = 'phantom-guard';

    const context = {
      diagnostics: [diagnostic],
      only: undefined,
      triggerKind: 1,
    };

    const actions = provider.provideCodeActions(
      document as any,
      range,
      context as any,
      CancellationToken as any
    );

    expect(actions.length).toBeGreaterThan(0);
    // Should have remove and open in registry actions
    expect(actions.some(a => a.title.includes('Remove'))).toBe(true);
    expect(actions.some(a => a.title.includes('Open'))).toBe(true);
  });

  // =========================================================================
  // T123.02: Typosquat fix suggestion
  // =========================================================================
  it('T123.02: suggests typosquat fix', async () => {
    /**
     * SPEC: S123
     * TEST_ID: T123.02
     * INV_ID: INV124
     *
     * Given: Typosquat package "reqeusts" detected
     * When: User invokes quick fix
     * Then: "Replace with 'requests'" action available
     */
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    const document = createMockDocument('reqeusts==1.0.0\n', '/test/requirements.txt');
    const range = new Range(0, 0, 0, 8);

    const diagnostic = new Diagnostic(range, 'Possible typosquat', DiagnosticSeverity.Error);
    diagnostic.source = 'phantom-guard';

    const context = {
      diagnostics: [diagnostic],
      only: undefined,
      triggerKind: 1,
    };

    const actions = provider.provideCodeActions(
      document as any,
      range,
      context as any,
      CancellationToken as any
    );

    const typosquatFix = actions.find(a => a.title.includes("Replace with 'requests'"));
    expect(typosquatFix).toBeDefined();
    expect(typosquatFix!.isPreferred).toBe(true);
  });
});

describe('Code Actions Only for Phantom Guard Diagnostics (INV124)', () => {
  it('ignores other diagnostic sources', async () => {
    /**
     * INV124: Code actions only appear for Phantom Guard diagnostics
     * source === 'phantom-guard' check
     */
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    const document = createMockDocument('flask==1.0.0\n', '/test/requirements.txt');
    const range = new Range(0, 0, 0, 5);

    // Create diagnostic from different source
    const diagnostic = new Diagnostic(range, 'Some error', DiagnosticSeverity.Error);
    diagnostic.source = 'pylint'; // Not phantom-guard

    const context = {
      diagnostics: [diagnostic],
      only: undefined,
      triggerKind: 1,
    };

    const actions = provider.provideCodeActions(
      document as any,
      range,
      context as any,
      CancellationToken as any
    );

    expect(actions.length).toBe(0);
  });

  it('actions only when source is phantom-guard', async () => {
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    const document = createMockDocument('flask==1.0.0\n', '/test/requirements.txt');
    const range = new Range(0, 0, 0, 5);

    // Create diagnostic from phantom-guard
    const diagnostic = new Diagnostic(range, 'Risky package', DiagnosticSeverity.Warning);
    diagnostic.source = 'phantom-guard';

    const context = {
      diagnostics: [diagnostic],
      only: undefined,
      triggerKind: 1,
    };

    const actions = provider.provideCodeActions(
      document as any,
      range,
      context as any,
      CancellationToken as any
    );

    expect(actions.length).toBeGreaterThan(0);
  });

  it.skip('no actions for language server diagnostics', () => {});
  it.skip('no actions for linter diagnostics', () => {});
});

describe('Code Action Types', () => {
  it('provides remove package action', async () => {
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    const document = createMockDocument('flask==1.0.0\n', '/test/requirements.txt');
    const range = new Range(0, 0, 0, 5);

    const diagnostic = new Diagnostic(range, 'Risky', DiagnosticSeverity.Warning);
    diagnostic.source = 'phantom-guard';

    const context = { diagnostics: [diagnostic], only: undefined, triggerKind: 1 };

    const actions = provider.provideCodeActions(
      document as any,
      range,
      context as any,
      CancellationToken as any
    );

    const removeAction = actions.find(a => a.title.includes('Remove'));
    expect(removeAction).toBeDefined();
    expect(removeAction!.edit).toBeDefined();
  });

  it('provides open in registry action', async () => {
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    const document = createMockDocument('flask==1.0.0\n', '/test/requirements.txt');
    const range = new Range(0, 0, 0, 5);

    const diagnostic = new Diagnostic(range, 'Risky', DiagnosticSeverity.Warning);
    diagnostic.source = 'phantom-guard';

    const context = { diagnostics: [diagnostic], only: undefined, triggerKind: 1 };

    const actions = provider.provideCodeActions(
      document as any,
      range,
      context as any,
      CancellationToken as any
    );

    const openAction = actions.find(a => a.title.includes('Open'));
    expect(openAction).toBeDefined();
    expect(openAction!.command).toBeDefined();
  });

  it('provides suppress action', async () => {
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    const document = createMockDocument('flask==1.0.0\n', '/test/requirements.txt');
    const range = new Range(0, 0, 0, 5);

    const diagnostic = new Diagnostic(range, 'Risky', DiagnosticSeverity.Warning);
    diagnostic.source = 'phantom-guard';

    const context = { diagnostics: [diagnostic], only: undefined, triggerKind: 1 };

    const actions = provider.provideCodeActions(
      document as any,
      range,
      context as any,
      CancellationToken as any
    );

    const suppressAction = actions.find(a => a.title.includes('Ignore'));
    expect(suppressAction).toBeDefined();
  });

  it.skip('suppress warning for line', () => {});
  it.skip('suppress warning for file', () => {});
  it.skip('add to allowlist', () => {});
  it.skip('replace typosquat with correct name', () => {});
  it.skip('remove package from file', () => {});
  it.skip('open package in registry', () => {});
});

describe('Typosquat Detection', () => {
  it('isKnownTyposquat returns true for known typosquats', async () => {
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    expect(provider.isKnownTyposquat('reqeusts')).toBe(true);
    expect(provider.isKnownTyposquat('flaask')).toBe(true);
    expect(provider.isKnownTyposquat('djano')).toBe(true);
  });

  it('isKnownTyposquat returns false for valid packages', async () => {
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    expect(provider.isKnownTyposquat('flask')).toBe(false);
    expect(provider.isKnownTyposquat('requests')).toBe(false);
    expect(provider.isKnownTyposquat('django')).toBe(false);
  });

  it('getTyposquatCorrection returns correct package name', async () => {
    const { PhantomGuardCodeActionProvider } = await import('../src/actions');

    const provider = new PhantomGuardCodeActionProvider();

    expect(provider.getTyposquatCorrection('reqeusts')).toBe('requests');
    expect(provider.getTyposquatCorrection('flaask')).toBe('flask');
    expect(provider.getTyposquatCorrection('djano')).toBe('django');
  });
});

describe('Code Action Behavior', () => {
  it.skip('actions are workspace edits', () => {});
  it.skip('undo works after action', () => {});
});
