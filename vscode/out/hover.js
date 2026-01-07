"use strict";
/**
 * IMPLEMENTS: S122
 * INVARIANTS: INV123 (returns null on non-package lines)
 * TESTS: T122.01, T122.02, T122.03
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.PhantomGuardHoverProvider = void 0;
const vscode = __importStar(require("vscode"));
/**
 * HoverProvider for Phantom Guard
 * Shows package risk information on hover
 * IMPLEMENTS: S122
 */
class PhantomGuardHoverProvider {
    core;
    // Cache for validation results to provide instant hover
    cache = new Map();
    constructor(core) {
        this.core = core;
    }
    /**
     * Provide hover information for a position in a document
     * INV123: Returns null on non-package lines
     */
    async provideHover(document, position, _token) {
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
        const range = new vscode.Range(position.line, startIndex, position.line, endIndex);
        return new vscode.Hover(content, range);
    }
    /**
     * Check if file is supported
     */
    isSupportedFile(uri) {
        const path = uri.fsPath.toLowerCase();
        return (path.endsWith('requirements.txt') ||
            path.includes('requirements') && path.endsWith('.txt') ||
            path.endsWith('pyproject.toml') ||
            path.endsWith('package.json') ||
            path.endsWith('cargo.toml'));
    }
    /**
     * Check if line is a comment
     */
    isCommentLine(lineText, uri) {
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
    parsePackageFromLine(lineText, uri) {
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
        }
        else if (path.endsWith('package.json')) {
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
        }
        else if (path.endsWith('.toml')) {
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
    async getPackageRisk(name, uri) {
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
    getRegistry(uri) {
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
    createHoverContent(risk) {
        const md = new vscode.MarkdownString();
        md.isTrusted = true;
        // Header with status icon
        const icon = this.getStatusIcon(risk.risk_level);
        md.appendMarkdown(`## ${icon} ${risk.name}\n\n`);
        // Risk classification
        md.appendMarkdown(`**Status:** ${this.formatRiskLevel(risk.risk_level)}\n\n`);
        // Risk score (as percentage)
        const scorePercent = Math.round(risk.risk_score * 100);
        md.appendMarkdown(`**Risk Score:** ${scorePercent}%\n\n`);
        // Signals (if any)
        if (risk.signals && risk.signals.length > 0) {
            md.appendMarkdown(`**Signals:**\n`);
            for (const signal of risk.signals.slice(0, 5)) {
                md.appendMarkdown(`- ${signal}\n`);
            }
            if (risk.signals.length > 5) {
                md.appendMarkdown(`- _...and ${risk.signals.length - 5} more_\n`);
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
    getStatusIcon(level) {
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
    formatRiskLevel(level) {
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
    updateCache(name, risk) {
        this.cache.set(name, risk);
    }
    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
    }
}
exports.PhantomGuardHoverProvider = PhantomGuardHoverProvider;
//# sourceMappingURL=hover.js.map