"use strict";
/**
 * IMPLEMENTS: S120, S121, S122, S123, S124
 * INVARIANTS: INV120-INV125
 * TESTS: T120.01-T120.04, T121.01-T121.05, T122.01-T122.03, T123.01-T123.02, T124.01-T124.02
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
exports.getStatusBar = getStatusBar;
const vscode = __importStar(require("vscode"));
const core_1 = require("./core");
const diagnostics_1 = require("./diagnostics");
const hover_1 = require("./hover");
const actions_1 = require("./actions");
const statusbar_1 = require("./statusbar");
const errors_1 = require("./errors");
let core;
let diagnosticProvider;
let hoverProvider;
let codeActionProvider;
let statusBar;
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
    // S123: Register code action provider
    codeActionProvider = vscode.languages.registerCodeActionsProvider(DOCUMENT_SELECTORS, new actions_1.PhantomGuardCodeActionProvider(), { providedCodeActionKinds: actions_1.PhantomGuardCodeActionProvider.providedCodeActionKinds });
    // S124: Create status bar
    statusBar = new statusbar_1.PhantomGuardStatusBar();
    // Register disposables
    context.subscriptions.push(core);
    context.subscriptions.push(diagnosticProvider);
    context.subscriptions.push(hoverProvider);
    context.subscriptions.push(codeActionProvider);
    context.subscriptions.push(statusBar);
}
function deactivate() {
    statusBar?.dispose();
    statusBar = undefined;
    codeActionProvider?.dispose();
    codeActionProvider = undefined;
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
function getStatusBar() {
    return statusBar;
}
//# sourceMappingURL=extension.js.map