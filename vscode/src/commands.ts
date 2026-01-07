/**
 * IMPLEMENTS: S127
 * INVARIANTS: INV127 (commands only affect phantom-guard state)
 * TESTS: T127.01, T127.02, T127.03
 */

import * as vscode from 'vscode';
import { ConfigProvider } from './config';
import { DiagnosticProvider } from './diagnostics';
import { RiskLevel } from './types';

/**
 * Command handler for phantom-guard.showSummary
 * T127.01: Shows summary of validation results
 */
export async function showSummaryCommand(
  diagnosticProvider: DiagnosticProvider | undefined
): Promise<void> {
  if (!diagnosticProvider) {
    vscode.window.showWarningMessage('Phantom Guard is not active');
    return;
  }

  // Get all open documents and collect diagnostics
  const summary = collectDiagnosticSummary(diagnosticProvider);

  if (summary.total === 0) {
    vscode.window.showInformationMessage('Phantom Guard: No dependency files open');
    return;
  }

  // Format summary message
  const message = formatSummaryMessage(summary);

  if (summary.highRisk > 0) {
    vscode.window.showErrorMessage(message);
  } else if (summary.suspicious > 0) {
    vscode.window.showWarningMessage(message);
  } else {
    vscode.window.showInformationMessage(message);
  }
}

// Package name validation regex
// SECURITY: Must start with alphanumeric, then alphanumeric, hyphens, underscores, dots
const PACKAGE_NAME_REGEX = /^[a-zA-Z0-9][\w\-._]*$/;

/**
 * Validate package name format
 * SECURITY: Prevents invalid/malicious package names
 */
function isValidPackageName(name: string): boolean {
  const trimmed = name.trim();
  return trimmed.length > 0 && PACKAGE_NAME_REGEX.test(trimmed);
}

/**
 * Command handler for phantom-guard.ignorePackage
 * T127.02: Adds package to ignored list
 */
export async function ignorePackageCommand(
  configProvider: ConfigProvider | undefined,
  packageName?: string
): Promise<void> {
  if (!configProvider) {
    vscode.window.showWarningMessage('Phantom Guard is not active');
    return;
  }

  // Get package name from argument or prompt user
  let name = packageName;

  // SECURITY: Validate package name even when provided via argument
  if (name && !isValidPackageName(name)) {
    vscode.window.showWarningMessage(`Invalid package name: '${name}'`);
    return;
  }

  if (!name) {
    name = await vscode.window.showInputBox({
      prompt: 'Enter package name to ignore',
      placeHolder: 'package-name',
      validateInput: (value) => {
        if (!value || !value.trim()) {
          return 'Package name is required';
        }
        // Basic validation: alphanumeric, hyphens, underscores, dots
        if (!isValidPackageName(value)) {
          return 'Invalid package name format';
        }
        return null;
      }
    });
  }

  if (!name) {
    return; // User cancelled
  }

  name = name.trim();

  // Check if already ignored
  if (configProvider.isIgnored(name)) {
    vscode.window.showInformationMessage(`'${name}' is already ignored`);
    return;
  }

  // Add to ignored list
  await configProvider.ignorePackage(name);
  vscode.window.showInformationMessage(`Added '${name}' to ignored packages`);
}

/**
 * Command handler for phantom-guard.revalidate
 * T127.03: Revalidates current file
 */
export async function revalidateCommand(
  diagnosticProvider: DiagnosticProvider | undefined
): Promise<void> {
  if (!diagnosticProvider) {
    vscode.window.showWarningMessage('Phantom Guard is not active');
    return;
  }

  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage('No active editor');
    return;
  }

  const document = editor.document;

  // Check if it's a supported file
  if (!isSupportedFile(document.uri)) {
    vscode.window.showWarningMessage(
      'Current file is not a supported dependency file'
    );
    return;
  }

  // Show progress
  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Phantom Guard: Revalidating...',
      cancellable: false,
    },
    async () => {
      await diagnosticProvider.validateDocument(document);
    }
  );

  // Get result count
  const diagnostics = diagnosticProvider.getDiagnostics(document.uri);
  const count = diagnostics.length;

  if (count === 0) {
    vscode.window.showInformationMessage('Phantom Guard: All packages look safe');
  } else {
    vscode.window.showWarningMessage(
      `Phantom Guard: Found ${count} issue${count > 1 ? 's' : ''}`
    );
  }
}

/**
 * Check if file is a supported dependency file
 */
function isSupportedFile(uri: vscode.Uri): boolean {
  const path = uri.fsPath.toLowerCase();
  return (
    path.endsWith('requirements.txt') ||
    (path.includes('requirements') && path.endsWith('.txt')) ||
    path.endsWith('pyproject.toml') ||
    path.endsWith('package.json') ||
    path.endsWith('cargo.toml')
  );
}

/**
 * Diagnostic summary structure
 */
interface DiagnosticSummary {
  total: number;
  safe: number;
  suspicious: number;
  highRisk: number;
  notFound: number;
  filesChecked: number;
}

/**
 * Collect diagnostic summary across all open files
 */
function collectDiagnosticSummary(
  diagnosticProvider: DiagnosticProvider
): DiagnosticSummary {
  const summary: DiagnosticSummary = {
    total: 0,
    safe: 0,
    suspicious: 0,
    highRisk: 0,
    notFound: 0,
    filesChecked: 0,
  };

  // Iterate over all open text documents
  for (const document of vscode.workspace.textDocuments) {
    if (!isSupportedFile(document.uri)) {
      continue;
    }

    summary.filesChecked++;
    const diagnostics = diagnosticProvider.getDiagnostics(document.uri);

    for (const diagnostic of diagnostics) {
      summary.total++;

      // Check diagnostic code for risk level
      const code = diagnostic.code as RiskLevel | undefined;
      switch (code) {
        case 'SUSPICIOUS':
          summary.suspicious++;
          break;
        case 'HIGH_RISK':
          summary.highRisk++;
          break;
        case 'NOT_FOUND':
          summary.notFound++;
          break;
        default:
          // Unknown or safe
          break;
      }
    }
  }

  return summary;
}

/**
 * Format summary message
 */
function formatSummaryMessage(summary: DiagnosticSummary): string {
  const parts: string[] = [
    `Checked ${summary.filesChecked} file${summary.filesChecked > 1 ? 's' : ''}`,
  ];

  if (summary.total === 0) {
    parts.push('all packages look safe');
  } else {
    const issues: string[] = [];
    if (summary.highRisk > 0) {
      issues.push(`${summary.highRisk} high risk`);
    }
    if (summary.suspicious > 0) {
      issues.push(`${summary.suspicious} suspicious`);
    }
    if (summary.notFound > 0) {
      issues.push(`${summary.notFound} not found`);
    }
    parts.push(`found ${issues.join(', ')}`);
  }

  return `Phantom Guard: ${parts.join(', ')}`;
}

/**
 * Register all Phantom Guard commands
 * Returns disposables for cleanup
 */
export function registerCommands(
  context: vscode.ExtensionContext,
  configProvider: ConfigProvider | undefined,
  diagnosticProvider: DiagnosticProvider | undefined
): vscode.Disposable[] {
  const disposables: vscode.Disposable[] = [];

  // phantom-guard.showSummary
  disposables.push(
    vscode.commands.registerCommand('phantom-guard.showSummary', () =>
      showSummaryCommand(diagnosticProvider)
    )
  );

  // phantom-guard.ignorePackage
  disposables.push(
    vscode.commands.registerCommand(
      'phantom-guard.ignorePackage',
      (packageName?: string) => ignorePackageCommand(configProvider, packageName)
    )
  );

  // phantom-guard.revalidate
  disposables.push(
    vscode.commands.registerCommand('phantom-guard.revalidate', () =>
      revalidateCommand(diagnosticProvider)
    )
  );

  return disposables;
}
