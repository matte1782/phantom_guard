/**
 * IMPLEMENTS: S124
 * INVARIANTS: INV125 (reflects most recent validation result)
 * TESTS: T124.01, T124.02
 */

import * as vscode from 'vscode';

export type StatusBarState = 'idle' | 'validating' | 'success' | 'warning' | 'error';

export interface ValidationSummary {
  total: number;
  safe: number;
  suspicious: number;
  highRisk: number;
  notFound: number;
}

/**
 * StatusBar for Phantom Guard
 * Shows validation status and issue count
 * IMPLEMENTS: S124
 */
export class PhantomGuardStatusBar implements vscode.Disposable {
  private statusBarItem: vscode.StatusBarItem;
  private currentState: StatusBarState = 'idle';
  private validationSequence: number = 0; // INV125: Track ordering

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBarItem.command = 'workbench.actions.view.problems';
    this.setIdle();
    this.statusBarItem.show();
  }

  /**
   * Set idle state (no validation done)
   */
  setIdle(): void {
    this.currentState = 'idle';
    this.statusBarItem.text = '$(shield) Phantom Guard';
    this.statusBarItem.tooltip = 'Phantom Guard: Ready';
    this.statusBarItem.backgroundColor = undefined;
  }

  /**
   * Set validating state (in progress)
   */
  setValidating(): number {
    this.currentState = 'validating';
    this.validationSequence++;
    const sequence = this.validationSequence;

    this.statusBarItem.text = '$(loading~spin) Validating...';
    this.statusBarItem.tooltip = 'Phantom Guard: Validating packages...';
    this.statusBarItem.backgroundColor = undefined;

    return sequence;
  }

  /**
   * Update with validation results
   * INV125: Only update if this is the most recent validation
   * T124.01: Status bar updates after validation
   * T124.02: Shows error count
   */
  update(summary: ValidationSummary, sequence: number): void {
    // INV125: Ignore outdated results
    if (sequence !== this.validationSequence) {
      return;
    }

    const issues = summary.suspicious + summary.highRisk + summary.notFound;

    if (summary.highRisk > 0) {
      this.setError(issues, summary);
    } else if (summary.suspicious > 0 || summary.notFound > 0) {
      this.setWarning(issues, summary);
    } else {
      this.setSuccess(summary);
    }
  }

  /**
   * Set success state (all safe)
   */
  private setSuccess(summary: ValidationSummary): void {
    this.currentState = 'success';
    this.statusBarItem.text = `$(shield) ${summary.safe} safe`;
    this.statusBarItem.tooltip = this.createTooltip(summary);
    this.statusBarItem.backgroundColor = undefined;
  }

  /**
   * Set warning state (suspicious found)
   */
  private setWarning(issues: number, summary: ValidationSummary): void {
    this.currentState = 'warning';
    this.statusBarItem.text = `$(warning) ${issues} issue${issues !== 1 ? 's' : ''}`;
    this.statusBarItem.tooltip = this.createTooltip(summary);
    this.statusBarItem.backgroundColor = new vscode.ThemeColor(
      'statusBarItem.warningBackground'
    );
  }

  /**
   * Set error state (high risk found)
   */
  private setError(issues: number, summary: ValidationSummary): void {
    this.currentState = 'error';
    this.statusBarItem.text = `$(error) ${issues} issue${issues !== 1 ? 's' : ''}`;
    this.statusBarItem.tooltip = this.createTooltip(summary);
    this.statusBarItem.backgroundColor = new vscode.ThemeColor(
      'statusBarItem.errorBackground'
    );
  }

  /**
   * Create detailed tooltip
   */
  private createTooltip(summary: ValidationSummary): string {
    const lines = ['Phantom Guard Validation Results', ''];

    if (summary.safe > 0) {
      lines.push(`✅ ${summary.safe} safe`);
    }
    if (summary.suspicious > 0) {
      lines.push(`⚠️ ${summary.suspicious} suspicious`);
    }
    if (summary.highRisk > 0) {
      lines.push(`🚨 ${summary.highRisk} high risk`);
    }
    if (summary.notFound > 0) {
      lines.push(`❓ ${summary.notFound} not found`);
    }

    lines.push('', 'Click to open Problems panel');

    return lines.join('\n');
  }

  /**
   * Clear status (no document open)
   */
  clear(): void {
    this.setIdle();
  }

  /**
   * Get current state
   */
  getState(): StatusBarState {
    return this.currentState;
  }

  /**
   * Get current text (for testing)
   */
  getText(): string {
    return this.statusBarItem.text;
  }

  /**
   * Dispose resources
   */
  dispose(): void {
    this.statusBarItem.dispose();
  }
}
