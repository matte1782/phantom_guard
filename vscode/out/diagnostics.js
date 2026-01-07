"use strict";
/**
 * IMPLEMENTS: S121
 * INVARIANTS: INV122 (diagnostics cleared on close)
 * TESTS: T121.01, T121.02, T121.03, T121.04, T121.05
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
exports.DiagnosticProvider = void 0;
const vscode = __importStar(require("vscode"));
// Supported file patterns for dependency files
const SUPPORTED_FILE_PATTERNS = [
    '**/requirements*.txt',
    '**/pyproject.toml',
    '**/package.json',
    '**/Cargo.toml',
];
// Debounce delay for validation (ms)
const DEBOUNCE_DELAY = 500;
/**
 * DiagnosticProvider for Phantom Guard
 * IMPLEMENTS: S121
 */
class DiagnosticProvider {
    core;
    diagnosticCollection;
    debounceTimers = new Map();
    disposables = [];
    constructor(core) {
        this.core = core;
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('phantom-guard');
        this.disposables.push(this.diagnosticCollection);
        // Register document event handlers
        this.registerEventHandlers();
    }
    /**
     * Register event handlers for document changes
     */
    registerEventHandlers() {
        // INV122: Clear diagnostics when document is closed
        this.disposables.push(vscode.workspace.onDidCloseTextDocument(doc => {
            this.clearDiagnostics(doc.uri);
        }));
        // Trigger validation on document save
        this.disposables.push(vscode.workspace.onDidSaveTextDocument(doc => {
            if (this.isSupportedFile(doc.uri)) {
                this.validateDocument(doc);
            }
        }));
        // Trigger validation on document change (debounced)
        this.disposables.push(vscode.workspace.onDidChangeTextDocument(event => {
            if (this.isSupportedFile(event.document.uri)) {
                this.validateDocumentDebounced(event.document);
            }
        }));
        // Trigger validation on document open
        this.disposables.push(vscode.workspace.onDidOpenTextDocument(doc => {
            if (this.isSupportedFile(doc.uri)) {
                this.validateDocument(doc);
            }
        }));
    }
    /**
     * Check if file is a supported dependency file
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
     * Validate document with debounce
     * T121.05: Rapid edits are debounced
     */
    validateDocumentDebounced(document) {
        const key = document.uri.toString();
        // Clear existing timer
        const existingTimer = this.debounceTimers.get(key);
        if (existingTimer) {
            clearTimeout(existingTimer);
        }
        // Set new timer
        const timer = setTimeout(() => {
            this.debounceTimers.delete(key);
            this.validateDocument(document);
        }, DEBOUNCE_DELAY);
        this.debounceTimers.set(key, timer);
    }
    /**
     * Validate a document and create diagnostics
     */
    async validateDocument(document) {
        const packages = this.parsePackages(document);
        if (packages.length === 0) {
            this.diagnosticCollection.set(document.uri, []);
            return;
        }
        // Determine registry based on file type
        const registry = this.getRegistry(document.uri);
        // Validate packages
        const results = await this.core.validatePackages(packages.map(p => p.name), registry);
        // Create diagnostics
        const diagnostics = [];
        for (const pkg of packages) {
            const risk = results.get(pkg.name);
            if (risk) {
                const diagnostic = this.createDiagnostic(pkg, risk);
                if (diagnostic) {
                    diagnostics.push(diagnostic);
                }
            }
        }
        this.diagnosticCollection.set(document.uri, diagnostics);
    }
    /**
     * Parse packages from document
     */
    parsePackages(document) {
        const packages = [];
        const text = document.getText();
        const lines = text.split('\n');
        const fileName = document.uri.fsPath.toLowerCase();
        if (fileName.endsWith('.txt')) {
            // requirements.txt format
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i].trim();
                if (line && !line.startsWith('#') && !line.startsWith('-')) {
                    const match = line.match(/^([a-zA-Z0-9][\w\-._]*)/);
                    if (match) {
                        const name = match[1];
                        const startChar = lines[i].indexOf(name);
                        packages.push({
                            name,
                            line: i,
                            range: new vscode.Range(i, startChar, i, startChar + name.length),
                        });
                    }
                }
            }
        }
        else if (fileName.endsWith('pyproject.toml')) {
            // pyproject.toml format (simplified)
            let inDependencies = false;
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                if (line.includes('[project.dependencies]') || line.includes('[tool.poetry.dependencies]')) {
                    inDependencies = true;
                    continue;
                }
                if (line.startsWith('[') && inDependencies) {
                    inDependencies = false;
                    continue;
                }
                if (inDependencies) {
                    // Match quoted package names
                    const match = line.match(/["']([a-zA-Z0-9][\w\-._]*)(?:\[.*?\])?/);
                    if (match) {
                        const name = match[1];
                        const startChar = line.indexOf(match[0]) + 1;
                        packages.push({
                            name,
                            line: i,
                            range: new vscode.Range(i, startChar, i, startChar + name.length),
                        });
                    }
                }
            }
        }
        else if (fileName.endsWith('package.json')) {
            // package.json format (simplified)
            let inDependencies = false;
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                if (line.includes('"dependencies"') || line.includes('"devDependencies"')) {
                    inDependencies = true;
                    continue;
                }
                if (line.includes('}') && inDependencies) {
                    inDependencies = false;
                    continue;
                }
                if (inDependencies) {
                    const match = line.match(/"([^"]+)":\s*"/);
                    if (match) {
                        const name = match[1];
                        const startChar = line.indexOf(`"${name}"`) + 1;
                        packages.push({
                            name,
                            line: i,
                            range: new vscode.Range(i, startChar, i, startChar + name.length),
                        });
                    }
                }
            }
        }
        return packages;
    }
    /**
     * Get registry type from file
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
     * Create diagnostic from package risk
     * T121.01: Safe package = no diagnostic
     * T121.02: Suspicious = warning
     * T121.03: High risk = error
     */
    createDiagnostic(pkg, risk) {
        // T121.01: Safe packages produce no diagnostic
        if (risk.risk_level === 'SAFE') {
            return null;
        }
        const severity = this.getSeverity(risk.risk_level);
        const message = this.getMessage(risk);
        const diagnostic = new vscode.Diagnostic(pkg.range, message, severity);
        diagnostic.source = 'phantom-guard';
        diagnostic.code = risk.risk_level;
        return diagnostic;
    }
    /**
     * Map risk level to diagnostic severity
     */
    getSeverity(riskLevel) {
        switch (riskLevel) {
            case 'SUSPICIOUS':
                return vscode.DiagnosticSeverity.Warning;
            case 'HIGH_RISK':
            case 'NOT_FOUND':
            case 'ERROR':
                return vscode.DiagnosticSeverity.Error;
            default:
                return vscode.DiagnosticSeverity.Information;
        }
    }
    /**
     * Generate diagnostic message
     * SAFETY: Null-safe access to optional fields
     */
    getMessage(risk) {
        switch (risk.risk_level) {
            case 'SUSPICIOUS':
                // SAFETY: Handle undefined risk_score
                const score = typeof risk.risk_score === 'number' ? risk.risk_score.toFixed(2) : '?';
                return `Suspicious package: ${risk.name} (score: ${score})`;
            case 'HIGH_RISK':
                // SAFETY: Handle undefined/empty signals array
                const signals = (risk.signals || []).slice(0, 3).join(', ') || 'multiple risk factors';
                return `High risk package: ${risk.name} - ${signals}`;
            case 'NOT_FOUND':
                return `Package not found: ${risk.name} - may be hallucinated`;
            case 'ERROR':
                return `Error validating package: ${risk.name}`;
            default:
                return `Unknown risk for package: ${risk.name}`;
        }
    }
    /**
     * Clear diagnostics for a document
     * INV122: Diagnostics cleared when document is closed
     */
    clearDiagnostics(uri) {
        this.diagnosticCollection.delete(uri);
        // Also clear any pending debounce timer
        const key = uri.toString();
        const timer = this.debounceTimers.get(key);
        if (timer) {
            clearTimeout(timer);
            this.debounceTimers.delete(key);
        }
    }
    /**
     * Get all diagnostics (for testing)
     */
    getDiagnostics(uri) {
        return this.diagnosticCollection.get(uri) || [];
    }
    /**
     * Re-validate all open documents
     * INV126: Configuration changes trigger re-validation
     */
    revalidateAllDocuments() {
        // Get all open text documents that are supported files
        for (const document of vscode.workspace.textDocuments) {
            if (this.isSupportedFile(document.uri)) {
                this.validateDocument(document);
            }
        }
    }
    /**
     * Dispose resources
     */
    dispose() {
        // Clear all debounce timers
        for (const timer of this.debounceTimers.values()) {
            clearTimeout(timer);
        }
        this.debounceTimers.clear();
        // Dispose all disposables
        for (const disposable of this.disposables) {
            disposable.dispose();
        }
        this.disposables = [];
    }
}
exports.DiagnosticProvider = DiagnosticProvider;
//# sourceMappingURL=diagnostics.js.map