"use strict";
/**
 * IMPLEMENTS: S126
 * INVARIANTS: INV127 (graceful spawn error), INV128 (no shell injection)
 * TESTS: T126.01, T126.02, T126.03, T126.04
 * SECURITY: Uses execFile (not exec), validates package names
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.PhantomGuardCore = void 0;
const child_process_1 = require("child_process");
const util_1 = require("util");
const errors_1 = require("./errors");
const execFileAsync = (0, util_1.promisify)(child_process_1.execFile);
// SECURITY: Package name validation regex
// Prevents shell injection by only allowing safe characters
// Supports: alphanumeric, hyphen, underscore, dot, @ and / for scoped packages
const PACKAGE_NAME_REGEX = /^[@a-z0-9][a-z0-9._\/-]*$/i;
// SECURITY: Forbidden shell metacharacters
const SHELL_METACHARACTERS = /[;|&$`\\"'<>(){}[\]\n\r]/;
class PhantomGuardCore {
    pythonPath = 'python';
    timeout = 5000; // 5 seconds per package
    /**
     * Set Python executable path
     */
    setPythonPath(path) {
        if (path && path.trim()) {
            this.pythonPath = path.trim();
        }
    }
    /**
     * SECURITY: Validate package name before subprocess call
     * INV128: No shell injection via package names
     */
    validatePackageName(name) {
        // Reject empty or whitespace-only names
        if (!name || !name.trim()) {
            console.warn('Rejected empty package name');
            return false;
        }
        // SECURITY: Check for shell metacharacters first
        if (SHELL_METACHARACTERS.test(name)) {
            console.warn(`Rejected package name with shell metacharacters: ${name}`);
            return false;
        }
        // SECURITY: Validate against allowed character pattern
        if (!PACKAGE_NAME_REGEX.test(name)) {
            console.warn(`Rejected invalid package name: ${name}`);
            return false;
        }
        // SECURITY: Reject names that are too long (prevent buffer overflow attempts)
        if (name.length > 214) { // npm limit
            console.warn(`Rejected package name exceeding max length: ${name}`);
            return false;
        }
        return true;
    }
    /**
     * Check if phantom-guard CLI is available
     */
    async checkAvailability() {
        try {
            // SECURITY: execFile with array args, no shell
            await execFileAsync(this.pythonPath, ['-m', 'phantom_guard', '--version'], {
                timeout: this.timeout
            });
            return true;
        }
        catch (error) {
            const execError = error;
            if (execError.code === 'ENOENT') {
                throw new errors_1.PythonNotFoundError();
            }
            return false;
        }
    }
    /**
     * Validate a single package
     * INV127: Fails gracefully on spawn error
     * INV128: Uses execFile with array args (no shell)
     */
    async validatePackage(name, registry = 'pypi') {
        // SECURITY: Validate package name first
        if (!this.validatePackageName(name)) {
            return null;
        }
        // SECURITY: Also validate registry
        const allowedRegistries = ['pypi', 'npm', 'crates'];
        if (!allowedRegistries.includes(registry.toLowerCase())) {
            console.warn(`Rejected invalid registry: ${registry}`);
            return null;
        }
        try {
            // SECURITY: execFile with array arguments - NO SHELL
            const { stdout } = await execFileAsync(this.pythonPath, ['-m', 'phantom_guard', 'validate', name, '--registry', registry, '--output', 'json'], { timeout: this.timeout });
            return this.parseOutput(stdout);
        }
        catch (error) {
            // INV127: Graceful spawn error handling
            const execError = error;
            if (execError.killed) {
                throw new errors_1.CoreTimeoutError(this.timeout);
            }
            if (execError.code === 'ENOENT') {
                throw new errors_1.CoreSpawnError('Python executable not found');
            }
            // Log and return null for other errors (graceful degradation)
            console.error(`Validation error for ${name}:`, error);
            return null;
        }
    }
    /**
     * Validate multiple packages
     */
    async validatePackages(packages, registry = 'pypi') {
        const results = new Map();
        // Validate all packages (could be parallelized in future)
        for (const pkg of packages) {
            if (this.validatePackageName(pkg)) {
                results.set(pkg, await this.validatePackage(pkg, registry));
            }
            else {
                results.set(pkg, null);
            }
        }
        return results;
    }
    /**
     * Parse JSON output from phantom-guard CLI
     */
    parseOutput(stdout) {
        try {
            const result = JSON.parse(stdout);
            return {
                name: result.name,
                risk_level: result.risk_level,
                risk_score: result.risk_score,
                signals: result.signals || [],
                recommendation: result.recommendation
            };
        }
        catch {
            throw new errors_1.CoreParseError(stdout);
        }
    }
    dispose() {
        // Cleanup if needed
    }
}
exports.PhantomGuardCore = PhantomGuardCore;
//# sourceMappingURL=core.js.map