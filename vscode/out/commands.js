"use strict";
/**
 * IMPLEMENTS: S127
 * INVARIANTS: INV127 (commands only affect phantom-guard state)
 * TESTS: T127.01, T127.02, T127.03
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
exports.showSummaryCommand = showSummaryCommand;
exports.ignorePackageCommand = ignorePackageCommand;
exports.revalidateCommand = revalidateCommand;
exports.registerCommands = registerCommands;
const vscode = __importStar(require("vscode"));
/**
 * Command handler for phantom-guard.showSummary
 * T127.01: Shows summary of validation results
 */
async function showSummaryCommand(diagnosticProvider) {
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
    }
    else if (summary.suspicious > 0) {
        vscode.window.showWarningMessage(message);
    }
    else {
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
function isValidPackageName(name) {
    const trimmed = name.trim();
    return trimmed.length > 0 && PACKAGE_NAME_REGEX.test(trimmed);
}
/**
 * Command handler for phantom-guard.ignorePackage
 * T127.02: Adds package to ignored list
 */
async function ignorePackageCommand(configProvider, packageName) {
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
async function revalidateCommand(diagnosticProvider) {
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
        vscode.window.showWarningMessage('Current file is not a supported dependency file');
        return;
    }
    // Show progress
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Phantom Guard: Revalidating...',
        cancellable: false,
    }, async () => {
        await diagnosticProvider.validateDocument(document);
    });
    // Get result count
    const diagnostics = diagnosticProvider.getDiagnostics(document.uri);
    const count = diagnostics.length;
    if (count === 0) {
        vscode.window.showInformationMessage('Phantom Guard: All packages look safe');
    }
    else {
        vscode.window.showWarningMessage(`Phantom Guard: Found ${count} issue${count > 1 ? 's' : ''}`);
    }
}
/**
 * Check if file is a supported dependency file
 */
function isSupportedFile(uri) {
    const path = uri.fsPath.toLowerCase();
    return (path.endsWith('requirements.txt') ||
        (path.includes('requirements') && path.endsWith('.txt')) ||
        path.endsWith('pyproject.toml') ||
        path.endsWith('package.json') ||
        path.endsWith('cargo.toml'));
}
/**
 * Collect diagnostic summary across all open files
 */
function collectDiagnosticSummary(diagnosticProvider) {
    const summary = {
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
            const code = diagnostic.code;
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
function formatSummaryMessage(summary) {
    const parts = [
        `Checked ${summary.filesChecked} file${summary.filesChecked > 1 ? 's' : ''}`,
    ];
    if (summary.total === 0) {
        parts.push('all packages look safe');
    }
    else {
        const issues = [];
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
function registerCommands(context, configProvider, diagnosticProvider) {
    const disposables = [];
    // phantom-guard.showSummary
    disposables.push(vscode.commands.registerCommand('phantom-guard.showSummary', () => showSummaryCommand(diagnosticProvider)));
    // phantom-guard.ignorePackage
    disposables.push(vscode.commands.registerCommand('phantom-guard.ignorePackage', (packageName) => ignorePackageCommand(configProvider, packageName)));
    // phantom-guard.revalidate
    disposables.push(vscode.commands.registerCommand('phantom-guard.revalidate', () => revalidateCommand(diagnosticProvider)));
    return disposables;
}
//# sourceMappingURL=commands.js.map