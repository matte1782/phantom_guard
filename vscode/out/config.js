"use strict";
/**
 * IMPLEMENTS: S125
 * INVARIANTS: INV126 (config changes trigger re-validation)
 * TESTS: T125.01-T125.02
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
exports.ConfigProvider = void 0;
exports.getConfigProvider = getConfigProvider;
exports.disposeConfigProvider = disposeConfigProvider;
const vscode = __importStar(require("vscode"));
const DEFAULT_CONFIG = {
    enabled: true,
    pythonPath: '',
    threshold: 0.5,
    ignoredPackages: [],
    debounceMs: 500,
    registries: ['pypi', 'npm', 'crates'],
};
/**
 * Configuration provider for Phantom Guard extension
 *
 * SPEC: S125
 * INV126: Configuration changes trigger re-validation
 */
class ConfigProvider {
    config;
    disposables = [];
    onConfigChangeEmitter = new vscode.EventEmitter();
    /**
     * Event fired when configuration changes
     * INV126: Configuration changes trigger re-validation
     */
    onConfigChange = this.onConfigChangeEmitter.event;
    constructor() {
        this.config = this.loadConfig();
        // Watch for configuration changes
        this.disposables.push(vscode.workspace.onDidChangeConfiguration(event => {
            if (event.affectsConfiguration('phantomGuard')) {
                const oldConfig = this.config;
                this.config = this.loadConfig();
                // INV126: Fire change event to trigger re-validation
                this.onConfigChangeEmitter.fire(this.config);
                // Log significant changes
                if (oldConfig.threshold !== this.config.threshold) {
                    console.log(`Phantom Guard threshold changed: ${oldConfig.threshold} -> ${this.config.threshold}`);
                }
                if (oldConfig.enabled !== this.config.enabled) {
                    console.log(`Phantom Guard enabled: ${this.config.enabled}`);
                }
            }
        }));
    }
    /**
     * Load configuration from VS Code settings
     */
    loadConfig() {
        const config = vscode.workspace.getConfiguration('phantomGuard');
        // Get values with validation
        const threshold = config.get('threshold', DEFAULT_CONFIG.threshold);
        const debounceMs = config.get('debounceMs', DEFAULT_CONFIG.debounceMs);
        return {
            enabled: config.get('enabled', DEFAULT_CONFIG.enabled),
            pythonPath: config.get('pythonPath', DEFAULT_CONFIG.pythonPath),
            threshold: this.clamp(threshold, 0, 1),
            ignoredPackages: config.get('ignoredPackages', DEFAULT_CONFIG.ignoredPackages),
            debounceMs: Math.max(0, debounceMs),
            registries: config.get('registries', DEFAULT_CONFIG.registries),
        };
    }
    /**
     * Clamp value between min and max
     */
    clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }
    /**
     * Get current configuration
     */
    getConfig() {
        return { ...this.config };
    }
    /**
     * Check if extension is enabled
     */
    isEnabled() {
        return this.config.enabled;
    }
    /**
     * Get Python path (or default)
     */
    getPythonPath() {
        return this.config.pythonPath || 'python';
    }
    /**
     * Get risk threshold
     */
    getThreshold() {
        return this.config.threshold;
    }
    /**
     * Get debounce time in milliseconds
     */
    getDebounceMs() {
        return this.config.debounceMs;
    }
    /**
     * Get enabled registries
     */
    getRegistries() {
        return [...this.config.registries];
    }
    /**
     * Check if package is ignored
     */
    isIgnored(packageName) {
        const normalized = packageName.toLowerCase();
        return this.config.ignoredPackages.some(ignored => ignored.toLowerCase() === normalized);
    }
    /**
     * Add package to ignore list
     */
    async ignorePackage(packageName) {
        const config = vscode.workspace.getConfiguration('phantomGuard');
        const current = config.get('ignoredPackages', []);
        const normalized = packageName.toLowerCase();
        if (!current.some(p => p.toLowerCase() === normalized)) {
            await config.update('ignoredPackages', [...current, normalized], vscode.ConfigurationTarget.Workspace);
        }
    }
    /**
     * Remove package from ignore list
     */
    async unignorePackage(packageName) {
        const config = vscode.workspace.getConfiguration('phantomGuard');
        const current = config.get('ignoredPackages', []);
        const normalized = packageName.toLowerCase();
        const filtered = current.filter(p => p.toLowerCase() !== normalized);
        if (filtered.length !== current.length) {
            await config.update('ignoredPackages', filtered, vscode.ConfigurationTarget.Workspace);
        }
    }
    dispose() {
        this.onConfigChangeEmitter.dispose();
        this.disposables.forEach(d => d.dispose());
    }
}
exports.ConfigProvider = ConfigProvider;
/**
 * Singleton instance for easy access
 */
let configProviderInstance;
function getConfigProvider() {
    if (!configProviderInstance) {
        configProviderInstance = new ConfigProvider();
    }
    return configProviderInstance;
}
function disposeConfigProvider() {
    if (configProviderInstance) {
        configProviderInstance.dispose();
        configProviderInstance = undefined;
    }
}
//# sourceMappingURL=config.js.map