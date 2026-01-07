/**
 * IMPLEMENTS: S122
 * INVARIANTS: INV123 (returns null on non-package lines)
 * TESTS: T122.01, T122.02, T122.03
 */

import * as vscode from 'vscode';
import { PhantomGuardCore } from './core';
import { PackageRisk, RiskLevel } from './types';

/**
 * HoverProvider for Phantom Guard
 * Shows package risk information on hover
 * IMPLEMENTS: S122
 */
export class PhantomGuardHoverProvider implements vscode.HoverProvider {
  // Cache for validation results to provide instant hover
  private cache: Map<string, PackageRisk> = new Map();

  constructor(private core: PhantomGuardCore) {}

  /**
   * Provide hover information for a position in a document
   * INV123: Returns null on non-package lines
   */
  async provideHover(
    document: vscode.TextDocument,
    position: vscode.Position,
    _token: vscode.CancellationToken
  ): Promise<vscode.Hover | null> {
    // Check if this is a supported file
    if (!this.isSupportedFile(document.uri)) {
      return null;
    }

    // Get the line text
    const line = document.lineAt(position.line);
    const lineText = line.text;

    // INV123: Return null for empty lines
    if (!lineText.trim()) {
      return null;
    }

    // INV123: Return null for comment lines
    if (this.isCommentLine(lineText, document.uri)) {
      return null;
    }

    // Parse package name from line
    const packageInfo = this.parsePackageFromLine(lineText, document.uri);
    if (!packageInfo) {
      return null;
    }

    // INV123: Return null if position is outside package name range
    const { name, startIndex, endIndex } = packageInfo;
    if (position.character < startIndex || position.character > endIndex) {
      return null;
    }

    // Get risk info (from cache or fetch)
    const risk = await this.getPackageRisk(name, document.uri);
    if (!risk) {
      return null;
    }

    // Create hover content
    const content = this.createHoverContent(risk);
    const range = new vscode.Range(
      position.line,
      startIndex,
      position.line,
      endIndex
    );

    return new vscode.Hover(content, range);
  }

  /**
   * Check if file is supported
   */
  private isSupportedFile(uri: vscode.Uri): boolean {
    const path = uri.fsPath.toLowerCase();
    return (
      path.endsWith('requirements.txt') ||
      path.includes('requirements') && path.endsWith('.txt') ||
      path.endsWith('pyproject.toml') ||
      path.endsWith('package.json') ||
      path.endsWith('cargo.toml')
    );
  }

  /**
   * Check if line is a comment
   */
  isCommentLine(lineText: string, uri: vscode.Uri): boolean {
    const trimmed = lineText.trim();
    const path = uri.fsPath.toLowerCase();

    // requirements.txt comments
    if (path.endsWith('.txt')) {
      return trimmed.startsWith('#');
    }

    // TOML comments
    if (path.endsWith('.toml')) {
      return trimmed.startsWith('#');
    }

    // JSON doesn't have comments, but empty lines should return null
    return false;
  }

  /**
   * Parse package name from line
   */
  parsePackageFromLine(
    lineText: string,
    uri: vscode.Uri
  ): { name: string; startIndex: number; endIndex: number } | null {
    const path = uri.fsPath.toLowerCase();

    if (path.endsWith('.txt')) {
      // requirements.txt: flask==2.0.0 or flask>=1.0
      const match = lineText.match(/^([a-zA-Z0-9][\w\-._]*)/);
      if (match) {
        return {
          name: match[1],
          startIndex: 0,
          endIndex: match[1].length,
        };
      }
    } else if (path.endsWith('package.json')) {
      // package.json: "package-name": "^1.0.0"
      const match = lineText.match(/"([^"]+)":\s*"/);
      if (match) {
        const startIndex = lineText.indexOf(`"${match[1]}"`) + 1;
        return {
          name: match[1],
          startIndex,
          endIndex: startIndex + match[1].length,
        };
      }
    } else if (path.endsWith('.toml')) {
      // pyproject.toml: "flask>=2.0" or flask = "^2.0"
      const quotedMatch = lineText.match(/["']([a-zA-Z0-9][\w\-._]*)(?:\[.*?\])?/);
      if (quotedMatch) {
        const startIndex = lineText.indexOf(quotedMatch[0]) + 1;
        return {
          name: quotedMatch[1],
          startIndex,
          endIndex: startIndex + quotedMatch[1].length,
        };
      }
      // TOML table key style: flask = "^2.0"
      const keyMatch = lineText.match(/^([a-zA-Z0-9][\w\-._]*)\s*=/);
      if (keyMatch) {
        return {
          name: keyMatch[1],
          startIndex: 0,
          endIndex: keyMatch[1].length,
        };
      }
    }

    return null;
  }

  /**
   * Get package risk from cache or fetch
   */
  private async getPackageRisk(name: string, uri: vscode.Uri): Promise<PackageRisk | null> {
    // Check cache first
    const cached = this.cache.get(name);
    if (cached) {
      return cached;
    }

    // Determine registry
    const registry = this.getRegistry(uri);

    // Fetch from core
    const risk = await this.core.validatePackage(name, registry);
    if (risk) {
      this.cache.set(name, risk);
    }

    return risk;
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
      return 'crates';
    }
    return 'pypi';
  }

  /**
   * Create hover content with markdown
   */
  createHoverContent(risk: PackageRisk): vscode.MarkdownString {
    const md = new vscode.MarkdownString();
    md.isTrusted = true;

    // Header with status icon
    const icon = this.getStatusIcon(risk.risk_level);
    md.appendMarkdown(`## ${icon} ${risk.name}\n\n`);

    // Risk classification
    md.appendMarkdown(`**Status:** ${this.formatRiskLevel(risk.risk_level)}\n\n`);

    // Risk score (as percentage)
    // SAFETY: Handle undefined risk_score
    const scorePercent = typeof risk.risk_score === 'number' ? Math.round(risk.risk_score * 100) : 0;
    md.appendMarkdown(`**Risk Score:** ${scorePercent}%\n\n`);

    // Signals (if any)
    // SAFETY: Null-safe access to signals array
    const signals = risk.signals || [];
    if (signals.length > 0) {
      md.appendMarkdown(`**Signals:**\n`);
      for (const signal of signals.slice(0, 5)) {
        md.appendMarkdown(`- ${signal}\n`);
      }
      if (signals.length > 5) {
        md.appendMarkdown(`- _...and ${signals.length - 5} more_\n`);
      }
      md.appendMarkdown('\n');
    }

    // Recommendation (if any)
    if (risk.recommendation) {
      md.appendMarkdown(`**Recommendation:** ${risk.recommendation}\n`);
    }

    return md;
  }

  /**
   * Get status icon for risk level
   */
  getStatusIcon(level: RiskLevel): string {
    switch (level) {
      case 'SAFE':
        return '✅';
      case 'SUSPICIOUS':
        return '⚠️';
      case 'HIGH_RISK':
        return '🚨';
      case 'NOT_FOUND':
        return '❓';
      case 'ERROR':
        return '❌';
      default:
        return '❔';
    }
  }

  /**
   * Format risk level for display
   */
  private formatRiskLevel(level: RiskLevel): string {
    switch (level) {
      case 'SAFE':
        return 'Safe';
      case 'SUSPICIOUS':
        return 'Suspicious';
      case 'HIGH_RISK':
        return 'High Risk';
      case 'NOT_FOUND':
        return 'Not Found';
      case 'ERROR':
        return 'Error';
      default:
        return 'Unknown';
    }
  }

  /**
   * Update cache with validation result
   */
  updateCache(name: string, risk: PackageRisk): void {
    this.cache.set(name, risk);
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }
}
