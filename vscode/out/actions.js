"use strict";
/**
 * IMPLEMENTS: S123
 * INVARIANTS: INV124 (only for phantom-guard diagnostics)
 * TESTS: T123.01, T123.02
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
exports.PhantomGuardCodeActionProvider = void 0;
const vscode = __importStar(require("vscode"));
// Known typosquat corrections
const TYPOSQUAT_CORRECTIONS = {
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
class PhantomGuardCodeActionProvider {
    static providedCodeActionKinds = [
        vscode.CodeActionKind.QuickFix,
    ];
    /**
     * Provide code actions for diagnostics
     * INV124: Only for phantom-guard diagnostics
     */
    provideCodeActions(document, range, context, _token) {
        const actions = [];
        // INV124: Only process phantom-guard diagnostics
        const phantomGuardDiagnostics = context.diagnostics.filter(d => d.source === 'phantom-guard');
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
    createTyposquatFix(document, diagnostic, packageName) {
        const correction = TYPOSQUAT_CORRECTIONS[packageName.toLowerCase()];
        if (!correction) {
            return null;
        }
        const action = new vscode.CodeAction(`Replace with '${correction}'`, vscode.CodeActionKind.QuickFix);
        action.edit = new vscode.WorkspaceEdit();
        action.edit.replace(document.uri, diagnostic.range, correction);
        action.isPreferred = true;
        action.diagnostics = [diagnostic];
        return action;
    }
    /**
     * Create remove package action
     */
    createRemoveAction(document, diagnostic, packageName) {
        const action = new vscode.CodeAction(`Remove '${packageName}'`, vscode.CodeActionKind.QuickFix);
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
    createOpenInRegistryAction(packageName, uri) {
        const registry = this.getRegistry(uri);
        const registryUrl = this.getRegistryUrl(packageName, registry);
        const action = new vscode.CodeAction(`Open '${packageName}' in ${registry}`, vscode.CodeActionKind.QuickFix);
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
    createSuppressAction(document, diagnostic, packageName) {
        const action = new vscode.CodeAction(`Ignore '${packageName}' for this file`, vscode.CodeActionKind.QuickFix);
        // Add a comment above the line
        const line = document.lineAt(diagnostic.range.start.line);
        const indent = line.text.match(/^\s*/)?.[0] || '';
        action.edit = new vscode.WorkspaceEdit();
        action.edit.insert(document.uri, new vscode.Position(diagnostic.range.start.line, 0), `${indent}# phantom-guard: ignore ${packageName}\n`);
        action.diagnostics = [diagnostic];
        return action;
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
            return 'crates.io';
        }
        return 'PyPI';
    }
    /**
     * Get registry URL for package
     * SECURITY: URL-encode package name to prevent injection
     */
    getRegistryUrl(packageName, registry) {
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
    isKnownTyposquat(packageName) {
        return packageName.toLowerCase() in TYPOSQUAT_CORRECTIONS;
    }
    /**
     * Get correction for typosquat
     */
    getTyposquatCorrection(packageName) {
        return TYPOSQUAT_CORRECTIONS[packageName.toLowerCase()];
    }
}
exports.PhantomGuardCodeActionProvider = PhantomGuardCodeActionProvider;
//# sourceMappingURL=actions.js.map