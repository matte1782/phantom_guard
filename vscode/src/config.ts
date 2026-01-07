/**
 * IMPLEMENTS: S125
 * INVARIANTS: INV126 (config changes trigger re-validation)
 * TESTS: T125.01-T125.02
 */

import * as vscode from 'vscode';

/**
 * Configuration interface for Phantom Guard extension
 */
export interface PhantomGuardConfig {
  /** Whether the extension is enabled */
  enabled: boolean;
  /** Custom Python path (empty = use system Python) */
  pythonPath: string;
  /** Risk threshold for warnings (0.0 - 1.0) */
  threshold: number;
  /** Packages to ignore during validation */
  ignoredPackages: string[];
  /** Debounce time for validation (ms) */
  debounceMs: number;
  /** Registries to check */
  registries: string[];
}

const DEFAULT_CONFIG: PhantomGuardConfig = {
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
export class ConfigProvider implements vscode.Disposable {
  private config: PhantomGuardConfig;
  private disposables: vscode.Disposable[] = [];
  private onConfigChangeEmitter = new vscode.EventEmitter<PhantomGuardConfig>();

  /**
   * Event fired when configuration changes
   * INV126: Configuration changes trigger re-validation
   */
  readonly onConfigChange = this.onConfigChangeEmitter.event;

  constructor() {
    this.config = this.loadConfig();

    // Watch for configuration changes
    this.disposables.push(
      vscode.workspace.onDidChangeConfiguration(event => {
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
      })
    );
  }

  /**
   * Load configuration from VS Code settings
   */
  private loadConfig(): PhantomGuardConfig {
    const config = vscode.workspace.getConfiguration('phantomGuard');

    // Get values with validation
    const threshold = config.get<number>('threshold', DEFAULT_CONFIG.threshold);
    const debounceMs = config.get<number>('debounceMs', DEFAULT_CONFIG.debounceMs);

    return {
      enabled: config.get<boolean>('enabled', DEFAULT_CONFIG.enabled),
      pythonPath: config.get<string>('pythonPath', DEFAULT_CONFIG.pythonPath),
      threshold: this.clamp(threshold, 0, 1),
      ignoredPackages: config.get<string[]>('ignoredPackages', DEFAULT_CONFIG.ignoredPackages),
      debounceMs: Math.max(0, debounceMs),
      registries: config.get<string[]>('registries', DEFAULT_CONFIG.registries),
    };
  }

  /**
   * Clamp value between min and max
   */
  private clamp(value: number, min: number, max: number): number {
    return Math.max(min, Math.min(max, value));
  }

  /**
   * Get current configuration
   */
  getConfig(): PhantomGuardConfig {
    return { ...this.config };
  }

  /**
   * Check if extension is enabled
   */
  isEnabled(): boolean {
    return this.config.enabled;
  }

  /**
   * Get Python path (or default)
   */
  getPythonPath(): string {
    return this.config.pythonPath || 'python';
  }

  /**
   * Get risk threshold
   */
  getThreshold(): number {
    return this.config.threshold;
  }

  /**
   * Get debounce time in milliseconds
   */
  getDebounceMs(): number {
    return this.config.debounceMs;
  }

  /**
   * Get enabled registries
   */
  getRegistries(): string[] {
    return [...this.config.registries];
  }

  /**
   * Check if package is ignored
   */
  isIgnored(packageName: string): boolean {
    const normalized = packageName.toLowerCase();
    return this.config.ignoredPackages.some(
      ignored => ignored.toLowerCase() === normalized
    );
  }

  /**
   * Add package to ignore list
   */
  async ignorePackage(packageName: string): Promise<void> {
    const config = vscode.workspace.getConfiguration('phantomGuard');
    const current = config.get<string[]>('ignoredPackages', []);
    const normalized = packageName.toLowerCase();

    if (!current.some(p => p.toLowerCase() === normalized)) {
      await config.update(
        'ignoredPackages',
        [...current, normalized],
        vscode.ConfigurationTarget.Workspace
      );
    }
  }

  /**
   * Remove package from ignore list
   */
  async unignorePackage(packageName: string): Promise<void> {
    const config = vscode.workspace.getConfiguration('phantomGuard');
    const current = config.get<string[]>('ignoredPackages', []);
    const normalized = packageName.toLowerCase();

    const filtered = current.filter(p => p.toLowerCase() !== normalized);
    if (filtered.length !== current.length) {
      await config.update(
        'ignoredPackages',
        filtered,
        vscode.ConfigurationTarget.Workspace
      );
    }
  }

  dispose(): void {
    this.onConfigChangeEmitter.dispose();
    this.disposables.forEach(d => d.dispose());
  }
}

/**
 * Singleton instance for easy access
 */
let configProviderInstance: ConfigProvider | undefined;

export function getConfigProvider(): ConfigProvider {
  if (!configProviderInstance) {
    configProviderInstance = new ConfigProvider();
  }
  return configProviderInstance;
}

export function disposeConfigProvider(): void {
  if (configProviderInstance) {
    configProviderInstance.dispose();
    configProviderInstance = undefined;
  }
}
