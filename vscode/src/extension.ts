/**
 * IMPLEMENTS: S120, S121, S122, S123, S124, S125, S127
 * INVARIANTS: INV120-INV127
 * TESTS: T120.01-T120.04, T121.01-T121.05, T122.01-T122.03, T123.01-T123.02, T124.01-T124.02, T125.01-T125.02, T127.01-T127.03
 */

import * as vscode from 'vscode';
import { PhantomGuardCore } from './core';
import { DiagnosticProvider } from './diagnostics';
import { PhantomGuardHoverProvider } from './hover';
import { PhantomGuardCodeActionProvider } from './actions';
import { PhantomGuardStatusBar } from './statusbar';
import { ConfigProvider } from './config';
import { registerCommands } from './commands';
import { ActivationError, PythonNotFoundError } from './errors';

let core: PhantomGuardCore | undefined;
let configProvider: ConfigProvider | undefined;
let diagnosticProvider: DiagnosticProvider | undefined;
let hoverProvider: vscode.Disposable | undefined;
let codeActionProvider: vscode.Disposable | undefined;
let statusBar: PhantomGuardStatusBar | undefined;

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

// Document selectors for supported file types
const DOCUMENT_SELECTORS: vscode.DocumentSelector = [
  { scheme: 'file', pattern: '**/requirements*.txt' },
  { scheme: 'file', pattern: '**/pyproject.toml' },
  { scheme: 'file', pattern: '**/package.json' },
  { scheme: 'file', pattern: '**/Cargo.toml' },
];

async function doActivation(context: vscode.ExtensionContext): Promise<void> {
  // INV120: All I/O is async
  core = new PhantomGuardCore();

  // Check phantom-guard availability
  const isAvailable = await core.checkAvailability();
  if (!isAvailable) {
    throw new ActivationError('phantom-guard CLI not found');
  }

  // S125: Create configuration provider
  configProvider = new ConfigProvider();

  // P0-BUG-001 FIX: Wire pythonPath config to core
  core.setPythonPath(configProvider.getPythonPath());

  // S121: Create diagnostic provider
  diagnosticProvider = new DiagnosticProvider(core);

  // S122: Register hover provider
  hoverProvider = vscode.languages.registerHoverProvider(
    DOCUMENT_SELECTORS,
    new PhantomGuardHoverProvider(core)
  );

  // S123: Register code action provider
  codeActionProvider = vscode.languages.registerCodeActionsProvider(
    DOCUMENT_SELECTORS,
    new PhantomGuardCodeActionProvider(),
    { providedCodeActionKinds: PhantomGuardCodeActionProvider.providedCodeActionKinds }
  );

  // S124: Create status bar
  statusBar = new PhantomGuardStatusBar();

  // INV126: Configuration changes trigger re-validation
  const configChangeDisposable = configProvider.onConfigChange(() => {
    // P0-BUG-001 FIX: Update pythonPath on config change
    if (core && configProvider) {
      core.setPythonPath(configProvider.getPythonPath());
    }
    // Re-validate all open documents when config changes
    if (diagnosticProvider) {
      diagnosticProvider.revalidateAllDocuments();
    }
  });

  // S127: Register command handlers
  const commandDisposables = registerCommands(context, configProvider, diagnosticProvider);

  // Register disposables
  context.subscriptions.push(core);
  context.subscriptions.push(configProvider);
  context.subscriptions.push(diagnosticProvider);
  context.subscriptions.push(hoverProvider);
  context.subscriptions.push(codeActionProvider);
  context.subscriptions.push(statusBar);
  context.subscriptions.push(configChangeDisposable);
  context.subscriptions.push(...commandDisposables);
}

export function deactivate(): void {
  statusBar?.dispose();
  statusBar = undefined;
  codeActionProvider?.dispose();
  codeActionProvider = undefined;
  hoverProvider?.dispose();
  hoverProvider = undefined;
  diagnosticProvider?.dispose();
  diagnosticProvider = undefined;
  configProvider?.dispose();
  configProvider = undefined;
  core?.dispose();
  core = undefined;
}

export function getCore(): PhantomGuardCore | undefined {
  return core;
}

export function getConfigProvider(): ConfigProvider | undefined {
  return configProvider;
}

export function getDiagnosticProvider(): DiagnosticProvider | undefined {
  return diagnosticProvider;
}

export function getStatusBar(): PhantomGuardStatusBar | undefined {
  return statusBar;
}
