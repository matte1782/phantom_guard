"use strict";
/**
 * IMPLEMENTS: S120, S121, S122
 * INVARIANTS: INV120 (async I/O), INV121 (500ms timeout), INV122 (diagnostics cleared), INV123 (hover null check)
 * TESTS: T120.01, T120.02, T120.03, T120.04
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
exports.activate = activate;
exports.deactivate = deactivate;
exports.getCore = getCore;
exports.getDiagnosticProvider = getDiagnosticProvider;
const vscode = __importStar(require("vscode"));
const core_1 = require("./core");
const diagnostics_1 = require("./diagnostics");
const hover_1 = require("./hover");
const errors_1 = require("./errors");
let core;
let diagnosticProvider;
let hoverProvider;
async function activate(context) {
    const startTime = Date.now();
    try {
        // INV121: Timeout after 500ms
        const activationPromise = doActivation(context);
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new errors_1.ActivationError('Activation timeout')), 500);
        });
        await Promise.race([activationPromise, timeoutPromise]);
        const elapsed = Date.now() - startTime;
        console.log(`Phantom Guard activated in ${elapsed}ms`);
    }
    catch (error) {
        if (error instanceof errors_1.PythonNotFoundError) {
            vscode.window.showErrorMessage('Phantom Guard: Python 3.11+ not found. Please install Python.', 'Install Python').then(selection => {
                if (selection === 'Install Python') {
                    vscode.env.openExternal(vscode.Uri.parse('https://python.org'));
                }
            });
        }
        else if (error instanceof errors_1.ActivationError) {
            vscode.window.showWarningMessage(`Phantom Guard: ${error.message}`);
        }
        // Don't throw - graceful degradation
    }
}
// Document selectors for supported file types
const DOCUMENT_SELECTORS = [
    { scheme: 'file', pattern: '**/requirements*.txt' },
    { scheme: 'file', pattern: '**/pyproject.toml' },
    { scheme: 'file', pattern: '**/package.json' },
    { scheme: 'file', pattern: '**/Cargo.toml' },
];
async function doActivation(context) {
    // INV120: All I/O is async
    core = new core_1.PhantomGuardCore();
    // Check phantom-guard availability
    const isAvailable = await core.checkAvailability();
    if (!isAvailable) {
        throw new errors_1.ActivationError('phantom-guard CLI not found');
    }
    // S121: Create diagnostic provider
    diagnosticProvider = new diagnostics_1.DiagnosticProvider(core);
    // S122: Register hover provider
    hoverProvider = vscode.languages.registerHoverProvider(DOCUMENT_SELECTORS, new hover_1.PhantomGuardHoverProvider(core));
    // Register disposables
    context.subscriptions.push(core);
    context.subscriptions.push(diagnosticProvider);
    context.subscriptions.push(hoverProvider);
}
function deactivate() {
    hoverProvider?.dispose();
    hoverProvider = undefined;
    diagnosticProvider?.dispose();
    diagnosticProvider = undefined;
    core?.dispose();
    core = undefined;
}
function getCore() {
    return core;
}
function getDiagnosticProvider() {
    return diagnosticProvider;
}
//# sourceMappingURL=extension.js.map