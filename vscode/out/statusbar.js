"use strict";
/**
 * IMPLEMENTS: S124
 * INVARIANTS: INV125 (reflects most recent validation result)
 * TESTS: T124.01, T124.02
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
exports.PhantomGuardStatusBar = void 0;
const vscode = __importStar(require("vscode"));
/**
 * StatusBar for Phantom Guard
 * Shows validation status and issue count
 * IMPLEMENTS: S124
 */
class PhantomGuardStatusBar {
    statusBarItem;
    currentState = 'idle';
    validationSequence = 0; // INV125: Track ordering
    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.command = 'workbench.actions.view.problems';
        this.setIdle();
        this.statusBarItem.show();
    }
    /**
     * Set idle state (no validation done)
     */
    setIdle() {
        this.currentState = 'idle';
        this.statusBarItem.text = '$(shield) Phantom Guard';
        this.statusBarItem.tooltip = 'Phantom Guard: Ready';
        this.statusBarItem.backgroundColor = undefined;
    }
    /**
     * Set validating state (in progress)
     */
    setValidating() {
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
    update(summary, sequence) {
        // INV125: Ignore outdated results
        if (sequence !== this.validationSequence) {
            return;
        }
        const issues = summary.suspicious + summary.highRisk + summary.notFound;
        if (summary.highRisk > 0) {
            this.setError(issues, summary);
        }
        else if (summary.suspicious > 0 || summary.notFound > 0) {
            this.setWarning(issues, summary);
        }
        else {
            this.setSuccess(summary);
        }
    }
    /**
     * Set success state (all safe)
     */
    setSuccess(summary) {
        this.currentState = 'success';
        this.statusBarItem.text = `$(shield) ${summary.safe} safe`;
        this.statusBarItem.tooltip = this.createTooltip(summary);
        this.statusBarItem.backgroundColor = undefined;
    }
    /**
     * Set warning state (suspicious found)
     */
    setWarning(issues, summary) {
        this.currentState = 'warning';
        this.statusBarItem.text = `$(warning) ${issues} issue${issues !== 1 ? 's' : ''}`;
        this.statusBarItem.tooltip = this.createTooltip(summary);
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }
    /**
     * Set error state (high risk found)
     */
    setError(issues, summary) {
        this.currentState = 'error';
        this.statusBarItem.text = `$(error) ${issues} issue${issues !== 1 ? 's' : ''}`;
        this.statusBarItem.tooltip = this.createTooltip(summary);
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
    /**
     * Create detailed tooltip
     */
    createTooltip(summary) {
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
    clear() {
        this.setIdle();
    }
    /**
     * Get current state
     */
    getState() {
        return this.currentState;
    }
    /**
     * Get current text (for testing)
     */
    getText() {
        return this.statusBarItem.text;
    }
    /**
     * Dispose resources
     */
    dispose() {
        this.statusBarItem.dispose();
    }
}
exports.PhantomGuardStatusBar = PhantomGuardStatusBar;
//# sourceMappingURL=statusbar.js.map