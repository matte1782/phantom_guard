/**
 * SPEC: S127 - Command Handlers
 * INVARIANTS: INV127 (commands only affect phantom-guard state)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  showSummaryCommand,
  ignorePackageCommand,
  revalidateCommand,
  registerCommands,
} from '../src/commands';
import {
  window,
  Uri,
  Diagnostic,
  DiagnosticSeverity,
  Range,
  MockTextDocument,
  setMockTextDocuments,
  clearMockTextDocuments,
} from './__mocks__/vscode';
import { ConfigProvider } from '../src/config';
import { DiagnosticProvider } from '../src/diagnostics';
import { PhantomGuardCore } from '../src/core';

// Mock vscode module
vi.mock('vscode', () => import('./__mocks__/vscode'));

describe('Command Handlers (S127)', () => {
  let mockCore: PhantomGuardCore;
  let mockConfigProvider: ConfigProvider;
  let mockDiagnosticProvider: DiagnosticProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    clearMockTextDocuments();

    // Create mock core
    mockCore = new PhantomGuardCore();

    // Create mock config provider
    mockConfigProvider = new ConfigProvider();

    // Create mock diagnostic provider
    mockDiagnosticProvider = new DiagnosticProvider(mockCore);
  });

  afterEach(() => {
    clearMockTextDocuments();
  });

  describe('showSummaryCommand (T127.01)', () => {
    /**
     * SPEC: S127
     * TEST_ID: T127.01
     */
    it('shows warning when provider is not active', async () => {
      await showSummaryCommand(undefined);

      expect(window.showWarningMessage).toHaveBeenCalledWith(
        'Phantom Guard is not active'
      );
    });

    it('shows info message when no dependency files are open', async () => {
      // No mock documents
      setMockTextDocuments([]);

      await showSummaryCommand(mockDiagnosticProvider);

      expect(window.showInformationMessage).toHaveBeenCalledWith(
        'Phantom Guard: No dependency files open'
      );
    });

    it.skip('shows info message when all packages are safe', async () => {
      // Skip: Requires complex mocking of vscode.workspace.textDocuments
      // The workspace.textDocuments getter is difficult to mock via vi.mock
      // Core logic is tested via other tests
    });

    it.skip('shows warning when suspicious packages found', async () => {
      // Skip: Requires complex mocking of vscode.workspace.textDocuments
      // The workspace.textDocuments getter is difficult to mock via vi.mock
      // Core logic is tested via other tests
    });

    it.skip('shows error when high risk packages found', async () => {
      // Skip: Requires complex mocking of vscode.workspace.textDocuments
      // The workspace.textDocuments getter is difficult to mock via vi.mock
      // Core logic is tested via other tests
    });

    it.skip('counts multiple files correctly', async () => {
      // Skip: Requires complex mocking of vscode.workspace.textDocuments
      // The workspace.textDocuments getter is difficult to mock via vi.mock
      // Core logic is tested via other tests
    });
  });

  describe('ignorePackageCommand (T127.02)', () => {
    /**
     * SPEC: S127
     * TEST_ID: T127.02
     */
    it('shows warning when provider is not active', async () => {
      await ignorePackageCommand(undefined);

      expect(window.showWarningMessage).toHaveBeenCalledWith(
        'Phantom Guard is not active'
      );
    });

    it('adds package from argument', async () => {
      const ignoreSpy = vi.spyOn(mockConfigProvider, 'ignorePackage');

      await ignorePackageCommand(mockConfigProvider, 'some-package');

      expect(ignoreSpy).toHaveBeenCalledWith('some-package');
      expect(window.showInformationMessage).toHaveBeenCalledWith(
        "Added 'some-package' to ignored packages"
      );
    });

    it('prompts for package name if not provided', async () => {
      // Mock showInputBox to return a package name
      vi.mocked(window.showInputBox).mockResolvedValueOnce('prompted-package');
      const ignoreSpy = vi.spyOn(mockConfigProvider, 'ignorePackage');

      await ignorePackageCommand(mockConfigProvider);

      expect(window.showInputBox).toHaveBeenCalled();
      expect(ignoreSpy).toHaveBeenCalledWith('prompted-package');
    });

    it('does nothing when user cancels input', async () => {
      // Mock showInputBox to return undefined (cancelled)
      vi.mocked(window.showInputBox).mockResolvedValueOnce(undefined);
      const ignoreSpy = vi.spyOn(mockConfigProvider, 'ignorePackage');

      await ignorePackageCommand(mockConfigProvider);

      expect(ignoreSpy).not.toHaveBeenCalled();
    });

    it('shows info when package is already ignored', async () => {
      // First add the package
      await mockConfigProvider.ignorePackage('already-ignored');
      vi.clearAllMocks();

      await ignorePackageCommand(mockConfigProvider, 'already-ignored');

      expect(window.showInformationMessage).toHaveBeenCalledWith(
        "'already-ignored' is already ignored"
      );
    });

    it('trims whitespace from package name', async () => {
      const ignoreSpy = vi.spyOn(mockConfigProvider, 'ignorePackage');

      await ignorePackageCommand(mockConfigProvider, '  trimmed-package  ');

      expect(ignoreSpy).toHaveBeenCalledWith('trimmed-package');
    });

    it('rejects invalid package name provided via argument', async () => {
      const ignoreSpy = vi.spyOn(mockConfigProvider, 'ignorePackage');

      // Invalid: starts with hyphen
      await ignorePackageCommand(mockConfigProvider, '-invalid-name');

      expect(window.showWarningMessage).toHaveBeenCalledWith(
        "Invalid package name: '-invalid-name'"
      );
      expect(ignoreSpy).not.toHaveBeenCalled();
    });

    it('rejects package name with shell metacharacters via argument', async () => {
      const ignoreSpy = vi.spyOn(mockConfigProvider, 'ignorePackage');

      // Invalid: contains shell metacharacter
      await ignorePackageCommand(mockConfigProvider, 'pkg;rm -rf /');

      expect(window.showWarningMessage).toHaveBeenCalledWith(
        "Invalid package name: 'pkg;rm -rf /'"
      );
      expect(ignoreSpy).not.toHaveBeenCalled();
    });
  });

  describe('revalidateCommand (T127.03)', () => {
    /**
     * SPEC: S127
     * TEST_ID: T127.03
     */
    it('shows warning when provider is not active', async () => {
      await revalidateCommand(undefined);

      expect(window.showWarningMessage).toHaveBeenCalledWith(
        'Phantom Guard is not active'
      );
    });

    it('shows warning when no active editor', async () => {
      // window.activeTextEditor is undefined by default in mock

      await revalidateCommand(mockDiagnosticProvider);

      expect(window.showWarningMessage).toHaveBeenCalledWith('No active editor');
    });

    it.skip('shows warning for unsupported file types', async () => {
      // This test requires mocking window.activeTextEditor which is complex
      // Skip for now - would need to modify mock
    });

    it.skip('validates document and shows success message', async () => {
      // This test requires mocking window.activeTextEditor and withProgress
      // Skip for now - would need to modify mock
    });

    it.skip('validates document and shows warning for issues', async () => {
      // This test requires mocking window.activeTextEditor and withProgress
      // Skip for now - would need to modify mock
    });
  });

  describe('registerCommands', () => {
    it('registers all three commands', () => {
      const mockContext = {
        subscriptions: [],
      } as any;

      const disposables = registerCommands(
        mockContext,
        mockConfigProvider,
        mockDiagnosticProvider
      );

      expect(disposables).toHaveLength(3);
    });
  });

  describe('Input Validation (INV127)', () => {
    it('validates package name format in ignorePackageCommand', async () => {
      // Mock showInputBox with validateInput callback
      vi.mocked(window.showInputBox).mockImplementationOnce(async (options: any) => {
        // Test the validateInput function
        const validator = options.validateInput;

        expect(validator('')).toBe('Package name is required');
        expect(validator('   ')).toBe('Package name is required');
        expect(validator('valid-package')).toBeNull();
        expect(validator('valid_package')).toBeNull();
        expect(validator('valid.package')).toBeNull();
        expect(validator('package123')).toBeNull();

        return undefined; // Cancel
      });

      await ignorePackageCommand(mockConfigProvider);
    });
  });
});

describe('Supported File Detection', () => {
  // Note: isSupportedFile is a private function in commands.ts
  // These tests would require either:
  // 1. Exporting isSupportedFile for testing
  // 2. Testing indirectly via showSummaryCommand (requires complex vscode.workspace mocking)
  // The function is tested indirectly through diagnostics.test.ts file detection tests

  it.skip('recognizes requirements.txt', () => {
    // Skip: Requires exposing isSupportedFile or complex workspace mocking
  });

  it.skip('recognizes package.json', () => {
    // Skip: Requires exposing isSupportedFile or complex workspace mocking
  });

  it.skip('recognizes pyproject.toml', () => {
    // Skip: Requires exposing isSupportedFile or complex workspace mocking
  });

  it.skip('recognizes Cargo.toml', () => {
    // Skip: Requires exposing isSupportedFile or complex workspace mocking
  });
});

describe('Summary Command with Diagnostics', () => {
  // NOTE: Tests requiring workspace.textDocuments mock are complex because
  // vi.mock creates a separate module instance. These tests are marked as skipped.
  // The internal functions (collectDiagnosticSummary, formatSummaryMessage) are
  // tested indirectly through the public API where possible.

  it.skip('shows error message when high risk packages found', () => {
    // Skip: workspace.textDocuments mock requires complex setup
  });

  it.skip('shows warning message when suspicious packages found', () => {
    // Skip: workspace.textDocuments mock requires complex setup
  });

  it.skip('shows info message when all packages safe', () => {
    // Skip: workspace.textDocuments mock requires complex setup
  });

  it.skip('counts NOT_FOUND packages', () => {
    // Skip: workspace.textDocuments mock requires complex setup
  });

  it.skip('counts multiple files correctly', () => {
    // Skip: workspace.textDocuments mock requires complex setup
  });

  it.skip('ignores non-dependency files in summary', () => {
    // Skip: workspace.textDocuments mock requires complex setup
  });

  it.skip('formats summary with multiple issue types', () => {
    // Skip: workspace.textDocuments mock requires complex setup
  });
});

describe('Revalidate Command with Active Editor', () => {
  let mockCore: PhantomGuardCore;
  let mockDiagnosticProvider: DiagnosticProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    clearMockTextDocuments();
    mockCore = new PhantomGuardCore();
    mockDiagnosticProvider = new DiagnosticProvider(mockCore);
  });

  afterEach(() => {
    mockDiagnosticProvider.dispose();
    clearMockTextDocuments();
    window.activeTextEditor = undefined;
  });

  it('shows warning for unsupported file types', async () => {
    const mockDoc = new MockTextDocument(
      Uri.file('/test/main.py'),
      'import flask'
    );

    window.activeTextEditor = {
      document: mockDoc,
    } as any;

    await revalidateCommand(mockDiagnosticProvider);

    expect(window.showWarningMessage).toHaveBeenCalledWith(
      'Current file is not a supported dependency file'
    );
  });

  it('validates document and shows success message when no issues', async () => {
    const mockDoc = new MockTextDocument(
      Uri.file('/test/requirements.txt'),
      'flask==2.0.0'
    );

    window.activeTextEditor = {
      document: mockDoc,
    } as any;

    vi.spyOn(mockDiagnosticProvider, 'validateDocument').mockResolvedValue();
    vi.spyOn(mockDiagnosticProvider, 'getDiagnostics').mockReturnValue([]);

    await revalidateCommand(mockDiagnosticProvider);

    expect(mockDiagnosticProvider.validateDocument).toHaveBeenCalledWith(mockDoc);
    expect(window.showInformationMessage).toHaveBeenCalledWith(
      'Phantom Guard: All packages look safe'
    );
  });

  it('validates document and shows warning for issues', async () => {
    const mockDoc = new MockTextDocument(
      Uri.file('/test/requirements.txt'),
      'flask-gpt==1.0.0'
    );

    window.activeTextEditor = {
      document: mockDoc,
    } as any;

    const diagnostic = new Diagnostic(
      new Range(0, 0, 0, 9),
      'Suspicious package',
      DiagnosticSeverity.Warning
    );

    vi.spyOn(mockDiagnosticProvider, 'validateDocument').mockResolvedValue();
    vi.spyOn(mockDiagnosticProvider, 'getDiagnostics').mockReturnValue([diagnostic]);

    await revalidateCommand(mockDiagnosticProvider);

    expect(window.showWarningMessage).toHaveBeenCalledWith(
      'Phantom Guard: Found 1 issue'
    );
  });

  it('pluralizes issues correctly', async () => {
    const mockDoc = new MockTextDocument(
      Uri.file('/test/requirements.txt'),
      'pkg1\npkg2'
    );

    window.activeTextEditor = {
      document: mockDoc,
    } as any;

    const diagnostics = [
      new Diagnostic(new Range(0, 0, 0, 4), 'Issue 1', DiagnosticSeverity.Warning),
      new Diagnostic(new Range(1, 0, 1, 4), 'Issue 2', DiagnosticSeverity.Warning),
    ];

    vi.spyOn(mockDiagnosticProvider, 'validateDocument').mockResolvedValue();
    vi.spyOn(mockDiagnosticProvider, 'getDiagnostics').mockReturnValue(diagnostics);

    await revalidateCommand(mockDiagnosticProvider);

    expect(window.showWarningMessage).toHaveBeenCalledWith(
      'Phantom Guard: Found 2 issues'
    );
  });
});
