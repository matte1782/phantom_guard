/**
 * IMPLEMENTS: S123
 * INVARIANTS: INV124 (only for phantom-guard diagnostics)
 * TESTS: T123.01, T123.02
 */

import * as vscode from 'vscode';

// Known typosquat corrections
const TYPOSQUAT_CORRECTIONS: Record<string, string> = {
  'reqeusts': 'requests',
  'requets': 'requests',
  'request': 'requests',
  'flaask': 'flask',
  'flasks': 'flask',
  'djano': 'django',
  'djnago': 'django',
  'numpy-': 'numpy',
  'numppy': 'numpy',
  'pandsa': 'pandas',
  'pands': 'pandas',
};

/**
 * CodeActionProvider for Phantom Guard
 * Provides quick fix actions for risky packages
 * IMPLEMENTS: S123
 */
export class PhantomGuardCodeActionProvider implements vscode.CodeActionProvider {
  static readonly providedCodeActionKinds = [
    vscode.CodeActionKind.QuickFix,
  ];

  /**
   * Provide code actions for diagnostics
   * INV124: Only for phantom-guard diagnostics
   */
  provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range,
    context: vscode.CodeActionContext,
    _token: vscode.CancellationToken
  ): vscode.CodeAction[] {
    const actions: vscode.CodeAction[] = [];

    // INV124: Only process phantom-guard diagnostics
    const phantomGuardDiagnostics = context.diagnostics.filter(
      d => d.source === 'phantom-guard'
    );

    for (const diagnostic of phantomGuardDiagnostics) {
      // Get package name from diagnostic range
      const packageName = document.getText(diagnostic.range);

      // Add typosquat fix if available
      const typosquatFix = this.createTyposquatFix(document, diagnostic, packageName);
      if (typosquatFix) {
        actions.push(typosquatFix);
      }

      // Add "Remove package" action
      const removeAction = this.createRemoveAction(document, diagnostic, packageName);
      actions.push(removeAction);

      // Add "Open in registry" action
      const openAction = this.createOpenInRegistryAction(packageName, document.uri);
      actions.push(openAction);

      // Add "Suppress for this line" action
      const suppressAction = this.createSuppressAction(document, diagnostic, packageName);
      actions.push(suppressAction);
    }

    return actions;
  }

  /**
   * Create typosquat fix action
   * T123.02: Suggests typosquat fix
   */
  createTyposquatFix(
    document: vscode.TextDocument,
    diagnostic: vscode.Diagnostic,
    packageName: string
  ): vscode.CodeAction | null {
    const correction = TYPOSQUAT_CORRECTIONS[packageName.toLowerCase()];
    if (!correction) {
      return null;
    }

    const action = new vscode.CodeAction(
      `Replace with '${correction}'`,
      vscode.CodeActionKind.QuickFix
    );

    action.edit = new vscode.WorkspaceEdit();
    action.edit.replace(document.uri, diagnostic.range, correction);
    action.isPreferred = true;
    action.diagnostics = [diagnostic];

    return action;
  }

  /**
   * Create remove package action
   */
  createRemoveAction(
    document: vscode.TextDocument,
    diagnostic: vscode.Diagnostic,
    packageName: string
  ): vscode.CodeAction {
    const action = new vscode.CodeAction(
      `Remove '${packageName}'`,
      vscode.CodeActionKind.QuickFix
    );

    // Get the full line range
    const line = document.lineAt(diagnostic.range.start.line);

    action.edit = new vscode.WorkspaceEdit();
    // Delete the entire line including newline
    action.edit.delete(document.uri, line.rangeIncludingLineBreak);
    action.diagnostics = [diagnostic];

    return action;
  }

  /**
   * Create "Open in registry" action
   */
  createOpenInRegistryAction(
    packageName: string,
    uri: vscode.Uri
  ): vscode.CodeAction {
    const registry = this.getRegistry(uri);
    const registryUrl = this.getRegistryUrl(packageName, registry);

    const action = new vscode.CodeAction(
      `Open '${packageName}' in ${registry}`,
      vscode.CodeActionKind.QuickFix
    );

    action.command = {
      title: 'Open in Registry',
      command: 'vscode.open',
      arguments: [vscode.Uri.parse(registryUrl)],
    };

    return action;
  }

  /**
   * Create suppress action
   */
  createSuppressAction(
    document: vscode.TextDocument,
    diagnostic: vscode.Diagnostic,
    packageName: string
  ): vscode.CodeAction {
    const action = new vscode.CodeAction(
      `Ignore '${packageName}' for this file`,
      vscode.CodeActionKind.QuickFix
    );

    // Add a comment above the line
    const line = document.lineAt(diagnostic.range.start.line);
    const indent = line.text.match(/^\s*/)?.[0] || '';

    action.edit = new vscode.WorkspaceEdit();
    action.edit.insert(
      document.uri,
      new vscode.Position(diagnostic.range.start.line, 0),
      `${indent}# phantom-guard: ignore ${packageName}\n`
    );
    action.diagnostics = [diagnostic];

    return action;
  }

  /**
   * Get registry from file type
   */
  private getRegistry(uri: vscode.Uri): string {
    const path = uri.fsPath.toLowerCase();
    if (path.endsWith('package.json')) {
      return 'npm';
    }
    if (path.endsWith('cargo.toml')) {
      return 'crates.io';
    }
    return 'PyPI';
  }

  /**
   * Get registry URL for package
   * SECURITY: URL-encode package name to prevent injection
   */
  private getRegistryUrl(packageName: string, registry: string): string {
    // SECURITY: URL-encode the package name
    const encodedName = encodeURIComponent(packageName);
    switch (registry) {
      case 'npm':
        return `https://www.npmjs.com/package/${encodedName}`;
      case 'crates.io':
        return `https://crates.io/crates/${encodedName}`;
      default:
        return `https://pypi.org/project/${encodedName}/`;
    }
  }

  /**
   * Check if a package name is a known typosquat
   */
  isKnownTyposquat(packageName: string): boolean {
    return packageName.toLowerCase() in TYPOSQUAT_CORRECTIONS;
  }

  /**
   * Get correction for typosquat
   */
  getTyposquatCorrection(packageName: string): string | undefined {
    return TYPOSQUAT_CORRECTIONS[packageName.toLowerCase()];
  }
}
