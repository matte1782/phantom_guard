/**
 * IMPLEMENTS: S120, S121, S122
 * INVARIANTS: INV120 (async I/O), INV121 (500ms timeout), INV122 (diagnostics cleared), INV123 (hover null check)
 * TESTS: T120.01, T120.02, T120.03, T120.04
 */

import * as vscode from 'vscode';
import { PhantomGuardCore } from './core';
import { DiagnosticProvider } from './diagnostics';
import { PhantomGuardHoverProvider } from './hover';
import { ActivationError, PythonNotFoundError } from './errors';

let core: PhantomGuardCore | undefined;
let diagnosticProvider: DiagnosticProvider | undefined;
let hoverProvider: vscode.Disposable | undefined;

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

  // S121: Create diagnostic provider
  diagnosticProvider = new DiagnosticProvider(core);

  // S122: Register hover provider
  hoverProvider = vscode.languages.registerHoverProvider(
    DOCUMENT_SELECTORS,
    new PhantomGuardHoverProvider(core)
  );

  // Register disposables
  context.subscriptions.push(core);
  context.subscriptions.push(diagnosticProvider);
  context.subscriptions.push(hoverProvider);
}

export function deactivate(): void {
  hoverProvider?.dispose();
  hoverProvider = undefined;
  diagnosticProvider?.dispose();
  diagnosticProvider = undefined;
  core?.dispose();
  core = undefined;
}

export function getCore(): PhantomGuardCore | undefined {
  return core;
}

export function getDiagnosticProvider(): DiagnosticProvider | undefined {
  return diagnosticProvider;
}
