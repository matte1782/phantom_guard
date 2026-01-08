# Phantom Guard — System Architecture v0.2.0

> **Version**: 0.2.0
> **Date**: 2026-01-04
> **Status**: CONDITIONAL_GO (P0 fixes applied)
> **Approver**: HOSTILE_VALIDATOR
> **Gate**: 1 of 6 - COMPLETE (pending final review)
> **Base**: Extends ARCHITECTURE.md (v0.1.0)
> **Review**: See .fortress/reports/validation/HOSTILE_REVIEW_ARCH_V0.2.0_2026-01-04.md

---

## 1. Overview

### 1.1 System Purpose

Phantom Guard v0.2.0 extends the core detection engine with developer workflow integrations:

1. **GitHub Action** — CI/CD integration via GitHub Marketplace
2. **VS Code Extension** — Real-time IDE validation
3. **4 New Detection Signals** — Namespace squatting, download inflation, ownership transfer, version spike
4. **Enhanced Pattern Database** — Community contribution system

**Theme**: "Developer Workflow Integration"

### 1.2 Success Criteria (from V0.2.0_MARKET_RESEARCH.md)

| Criterion | v0.1.x Baseline | v0.2.0 Target | Measurement |
|:----------|:----------------|:--------------|:------------|
| Detection signals | 11 | 15 | Signal count |
| False positive rate | 0.08% | <0.5% | Real-world testing |
| GitHub stars | 0 | 500 (3mo) / 2000 (6mo) | GitHub API |
| VS Code installs | 0 | 1000 (6mo) | Marketplace |
| GitHub Action repos | 0 | 500 (6mo) | Marketplace |

### 1.3 Architecture Diagram (v0.2.0)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PHANTOM GUARD v0.2.0                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                   INTEGRATION LAYER (NEW IN v0.2.0)                        │  │
│  │  ┌─────────────────────────┐  ┌─────────────────────────────────────────┐ │  │
│  │  │    GitHub Action        │  │         VS Code Extension                │ │  │
│  │  │    (S100-S119)          │  │         (S120-S149)                      │ │  │
│  │  │                         │  │                                          │ │  │
│  │  │  - YAML workflow        │  │  - DiagnosticCollection                  │ │  │
│  │  │  - PR comments          │  │  - HoverProvider                         │ │  │
│  │  │  - SARIF output         │  │  - CodeActionProvider                    │ │  │
│  │  │  - Exit codes           │  │  - StatusBarItem                         │ │  │
│  │  └────────────┬────────────┘  └─────────────────┬───────────────────────┘ │  │
│  └───────────────┼─────────────────────────────────┼─────────────────────────┘  │
│                  │                                 │                             │
│                  ▼                                 ▼                             │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                        CLI LAYER (S010-S019)                               │  │
│  │  ├── phantom-guard check <file>      # Validate dependency file            │  │
│  │  ├── phantom-guard validate <pkg>    # Check single package                │  │
│  │  └── phantom-guard cache             # Cache management                    │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                             │
│                                    ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                       CORE LAYER (S001-S009)                               │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │    Detector     │  │    Analyzer     │  │     Scorer      │            │  │
│  │  │   (S001-S003)   │  │   (S004-S006)   │  │   (S007-S009)   │            │  │
│  │  │                 │  │                 │  │                 │            │  │
│  │  │ - Orchestration │  │ - Pattern match │  │ - Risk scoring  │            │  │
│  │  │ - Batch process │  │ - Signal extract│  │ - Thresholds    │            │  │
│  │  │ - Result merge  │  │ - Heuristics    │  │ - Recommendations│           │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘            │  │
│  └───────────┼────────────────────┼────────────────────┼─────────────────────┘  │
│              │                    │                    │                        │
│              ▼                    ▼                    ▼                        │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │               NEW DETECTION SIGNALS (S060-S079) v0.2.0                     │  │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │  │
│  │  │  Namespace    │  │   Download    │  │   Ownership   │  │   Version   │ │  │
│  │  │  Squatting    │  │   Inflation   │  │   Transfer    │  │    Spike    │ │  │
│  │  │  (S060-S064)  │  │  (S065-S069)  │  │  (S070-S074)  │  │ (S075-S079) │ │  │
│  │  └───────────────┘  └───────────────┘  └───────────────┘  └─────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                             │
│                                    ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                     REGISTRY LAYER (S020-S039)                             │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │   PyPI Client   │  │   npm Client    │  │ crates.io Client│            │  │
│  │  │   (S020-S026)   │  │   (S027-S032)   │  │   (S033-S039)   │            │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘            │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                    │                                             │
│                                    ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                     CACHE LAYER (S040-S049)                                │  │
│  │  ├── In-memory LRU cache (hot packages)                                    │  │
│  │  ├── SQLite persistent cache (cold storage)                                │  │
│  │  └── TTL management (configurable expiry)                                  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                     PATTERNS LAYER (S050-S059)                             │  │
│  │  ├── Hallucination pattern database (ENHANCED in v0.2.0)                   │  │
│  │  ├── Typosquatting detection                                               │  │
│  │  ├── Popular package registry (allowlist)                                  │  │
│  │  └── Community patterns (S058-S059) NEW                                    │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Requirement Extraction

### 2.1 Functional Requirements (v0.2.0 Additions)

| ID | Requirement | Source | Priority |
|:---|:------------|:-------|:---------|
| FR013 | GitHub Action for PR validation | V0.2.0_MARKET_RESEARCH | P0 |
| FR014 | PR comment with validation results | V0.2.0_MARKET_RESEARCH | P0 |
| FR015 | SARIF output for GitHub Code Scanning | V0.2.0_MARKET_RESEARCH | P1 |
| FR016 | VS Code extension with real-time validation | V0.2.0_MARKET_RESEARCH | P1 |
| FR017 | Diagnostics panel integration | V0.2.0_MARKET_RESEARCH | P1 |
| FR018 | Hover tooltips with risk scores | V0.2.0_MARKET_RESEARCH | P1 |
| FR019 | Quick fix suggestions | V0.2.0_MARKET_RESEARCH | P2 |
| FR020 | Namespace squatting detection | V0.2.0_MARKET_RESEARCH | P0 |
| FR021 | Download inflation detection | V0.2.0_MARKET_RESEARCH | P0 |
| FR022 | Ownership transfer detection | V0.2.0_MARKET_RESEARCH | P0 |
| FR023 | Version spike detection | V0.2.0_MARKET_RESEARCH | P0 |
| FR024 | Community pattern contributions | V0.2.0_MARKET_RESEARCH | P2 |

### 2.2 Non-Functional Requirements (v0.2.0 Additions)

| ID | Requirement | Target | Measurement |
|:---|:------------|:-------|:------------|
| NFR009 | GitHub Action cold start | <5s | CI timing |
| NFR010 | VS Code extension activation | <500ms | Extension timing |
| NFR011 | VS Code validation latency | <500ms first, <200ms cached | Per-file |
| NFR012 | New signals false positive rate | <0.5% | Testing |
| NFR013 | Extension memory footprint | <50MB | VS Code profiler |
| NFR014 | Action workflow overhead | <30s | For 50 packages |

### 2.3 Constraints (v0.2.0 Additions)

| ID | Constraint | Rationale |
|:---|:-----------|:----------|
| CON007 | GitHub Action: JavaScript (node20) | Fast startup, native support |
| CON008 | VS Code extension: TypeScript | Best practice, type safety |
| CON009 | VS Code extension: No shell execution | Security requirement |
| CON010 | VS Code extension: Minimal permissions | Security best practice |
| CON011 | GitHub Action: No secrets required | Easy adoption |
| CON012 | Extension must be open source | Trust requirement |

---

## 3. Component Specifications (v0.2.0 NEW)

### 3.1 GitHub Action (S100-S119)

#### S100: Action Entry Point

```typescript
// SPEC_ID: S100
// IMPLEMENTS: FR013, FR014
// INVARIANTS: INV100, INV101

/**
 * GitHub Action entry point.
 *
 * action.yml configuration:
 *   name: 'Phantom Guard'
 *   description: 'Detect AI-hallucinated package attacks'
 *   inputs:
 *     files: File patterns to validate
 *     fail-on: 'high-risk' | 'suspicious' | 'none'
 *     output: 'github-comment' | 'sarif' | 'json' | 'none'
 *   outputs:
 *     safe-count: Number of safe packages
 *     suspicious-count: Number of suspicious packages
 *     high-risk-count: Number of high-risk packages
 *     report-json: Full JSON report
 *
 * Performance:
 *   - Cold start: <5s
 *   - 50 packages: <30s total
 */
async function run(): Promise<void>;
```

#### S101: File Discovery

```typescript
// SPEC_ID: S101
// IMPLEMENTS: FR013
// INVARIANTS: INV102

/**
 * Discover dependency files matching input patterns.
 *
 * Supported patterns:
 *   - requirements.txt, requirements/*.txt
 *   - package.json, package-lock.json
 *   - Cargo.toml
 *   - pyproject.toml
 *
 * Returns:
 *   Array of file paths with detected registry type
 */
async function discoverFiles(
  patterns: string[]
): Promise<DependencyFile[]>;
```

#### S102: Package Extractor

```typescript
// SPEC_ID: S102
// IMPLEMENTS: FR013
// INVARIANTS: INV103

/**
 * Extract package names from dependency files.
 *
 * Handles:
 *   - Version specifiers (flask>=2.0)
 *   - Comments (# ignored)
 *   - Environment markers (flask; python_version >= "3.8")
 *   - npm scoped packages (@scope/package)
 *
 * Returns:
 *   Array of package names with source file info
 */
function extractPackages(
  file: DependencyFile
): PackageReference[];
```

#### S103: Validation Orchestrator

```typescript
// SPEC_ID: S103
// IMPLEMENTS: FR013
// INVARIANTS: INV104

/**
 * Orchestrate validation using phantom-guard-core.
 *
 * Strategy:
 *   1. Group packages by registry
 *   2. Validate in parallel (concurrency=10)
 *   3. Aggregate results
 *   4. Generate output
 *
 * Performance:
 *   - Leverages core library caching
 *   - Concurrent validation
 */
async function validatePackages(
  packages: PackageReference[],
  config: ActionConfig
): Promise<ValidationReport>;
```

#### S104: PR Comment Generator

```typescript
// SPEC_ID: S104
// IMPLEMENTS: FR014
// INVARIANTS: INV105, INV106

/**
 * Generate markdown PR comment with results.
 *
 * Comment structure:
 *   ## Phantom Guard Report
 *
 *   | Status | Count |
 *   |--------|-------|
 *   | Safe | X |
 *   | Suspicious | Y |
 *   | High Risk | Z |
 *
 *   ### High Risk Packages
 *   - `package-name` (score: 0.85) - Signals: [...]
 *
 *   ### Suspicious Packages
 *   - `package-name` (score: 0.45) - Signals: [...]
 *
 * Features:
 *   - Sticky comment (updates existing)
 *   - Collapsible sections for long lists
 *   - Links to documentation
 */
function generateComment(
  report: ValidationReport
): string;
```

#### S105: SARIF Output Generator

```typescript
// SPEC_ID: S105
// IMPLEMENTS: FR015
// INVARIANTS: INV107

/**
 * Generate SARIF output for GitHub Code Scanning.
 *
 * SARIF structure:
 *   - tool: { driver: { name: "Phantom Guard", version } }
 *   - runs[0].results: Array of findings
 *   - Each result: { ruleId, message, locations, level }
 *
 * Rule IDs:
 *   - PG001: HIGH_RISK package detected
 *   - PG002: SUSPICIOUS package detected
 *   - PG003: NOT_FOUND package
 *
 * Integration:
 *   - Upload via github/codeql-action/upload-sarif
 */
function generateSarif(
  report: ValidationReport,
  files: DependencyFile[]
): SarifLog;
```

#### S106: Exit Code Handler

```typescript
// SPEC_ID: S106
// IMPLEMENTS: FR013
// INVARIANTS: INV108

/**
 * Determine exit code based on results and config.
 *
 * Exit codes (matching CLI):
 *   0: All packages safe
 *   1: Suspicious packages found (if fail-on=suspicious)
 *   2: High-risk packages found (if fail-on=high-risk)
 *   3: Validation errors
 *   4: Configuration errors
 *   5: Network errors
 *
 * fail-on behavior:
 *   - 'none': Always exit 0 (unless errors)
 *   - 'high-risk': Exit non-zero only on HIGH_RISK
 *   - 'suspicious': Exit non-zero on SUSPICIOUS or HIGH_RISK
 */
function determineExitCode(
  report: ValidationReport,
  failOn: 'none' | 'suspicious' | 'high-risk'
): number;
```

### 3.2 VS Code Extension (S120-S149)

#### S120: Extension Activation

```typescript
// SPEC_ID: S120
// IMPLEMENTS: FR016
// INVARIANTS: INV120, INV121

/**
 * Extension activation handler.
 *
 * Activation events:
 *   - onLanguage:pip-requirements
 *   - onLanguage:json (package.json)
 *   - onLanguage:toml (Cargo.toml, pyproject.toml)
 *   - workspaceContains:requirements.txt
 *   - workspaceContains:package.json
 *   - workspaceContains:Cargo.toml
 *
 * Initialization:
 *   1. Load configuration
 *   2. Initialize phantom-guard-core (bundled WASM or spawn subprocess)
 *   3. Register providers
 *   4. Initialize status bar
 *
 * Performance:
 *   - Activation: <500ms
 */
async function activate(
  context: vscode.ExtensionContext
): Promise<void>;
```

#### S121: Diagnostic Provider

```typescript
// SPEC_ID: S121
// IMPLEMENTS: FR017
// INVARIANTS: INV122

/**
 * Provides diagnostics for Problems panel.
 *
 * Diagnostic mapping:
 *   - HIGH_RISK → DiagnosticSeverity.Error
 *   - SUSPICIOUS → DiagnosticSeverity.Warning
 *   - SAFE → (no diagnostic)
 *   - NOT_FOUND → DiagnosticSeverity.Error
 *
 * Message format:
 *   "Package '{name}' is {recommendation} (risk: {score}). Signals: {signals}"
 *
 * Trigger:
 *   - On document open
 *   - On document save
 *   - On configuration change
 *
 * Debounce:
 *   - 500ms after last keystroke (if live validation enabled)
 */
class PhantomGuardDiagnosticProvider
  implements vscode.Disposable {

  private diagnosticCollection: vscode.DiagnosticCollection;

  async validateDocument(
    document: vscode.TextDocument
  ): Promise<void>;
}
```

#### S122: Hover Provider

```typescript
// SPEC_ID: S122
// IMPLEMENTS: FR018
// INVARIANTS: INV123

/**
 * Provides hover tooltips with risk information.
 *
 * Hover content (MarkdownString):
 *   **Package**: {name}
 *   **Risk Score**: {score} ({recommendation})
 *   **Registry**: {registry}
 *
 *   **Signals**:
 *   - {signal1}
 *   - {signal2}
 *
 *   [View Details](command:phantomGuard.showDetails)
 *
 * Position detection:
 *   - requirements.txt: line = package name
 *   - package.json: within "dependencies" or "devDependencies"
 *   - Cargo.toml: within [dependencies]
 */
class PhantomGuardHoverProvider
  implements vscode.HoverProvider {

  provideHover(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken
  ): vscode.ProviderResult<vscode.Hover>;
}
```

#### S123: Code Action Provider

```typescript
// SPEC_ID: S123
// IMPLEMENTS: FR019
// INVARIANTS: INV124

/**
 * Provides quick fix suggestions.
 *
 * Actions:
 *   1. "Did you mean '{correct}'?" - Typosquat fix
 *   2. "Add to allowlist" - Dismiss warning
 *   3. "View package on {registry}" - Open browser
 *   4. "Report false positive" - Open GitHub issue
 *
 * Applicability:
 *   - Only on lines with diagnostics
 *   - Typosquat fix only if confident match exists
 */
class PhantomGuardCodeActionProvider
  implements vscode.CodeActionProvider {

  provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range | vscode.Selection,
    context: vscode.CodeActionContext,
    token: vscode.CancellationToken
  ): vscode.ProviderResult<vscode.CodeAction[]>;
}
```

#### S124: Status Bar Item

```typescript
// SPEC_ID: S124
// IMPLEMENTS: FR016
// INVARIANTS: INV125

/**
 * Status bar item showing validation status.
 *
 * States:
 *   - $(shield) Phantom Guard - No issues found (green)
 *   - $(shield) Phantom Guard: 2 warnings (yellow)
 *   - $(shield) Phantom Guard: 1 high risk! (red)
 *   - $(sync~spin) Validating... (blue)
 *   - $(error) Phantom Guard: Error (red)
 *
 * Click action:
 *   - Opens Problems panel filtered to Phantom Guard
 */
class StatusBarManager implements vscode.Disposable {
  update(report: ExtensionReport): void;
}
```

#### S125: Configuration Handler

```typescript
// SPEC_ID: S125
// IMPLEMENTS: FR016
// INVARIANTS: INV126

/**
 * Extension configuration schema.
 *
 * Settings:
 *   phantomGuard.enabled: boolean (default: true)
 *   phantomGuard.threshold: number (default: 0.3)
 *   phantomGuard.validateOnSave: boolean (default: true)
 *   phantomGuard.validateOnOpen: boolean (default: true)
 *   phantomGuard.registries: string[] (default: ["pypi", "npm", "crates"])
 *   phantomGuard.allowlist: string[] (default: [])
 *   phantomGuard.cacheEnabled: boolean (default: true)
 *
 * Configuration change handling:
 *   - Re-validate all open documents on threshold change
 *   - Clear cache on registries change
 */
interface PhantomGuardConfig {
  enabled: boolean;
  threshold: number;
  validateOnSave: boolean;
  validateOnOpen: boolean;
  registries: ('pypi' | 'npm' | 'crates')[];
  allowlist: string[];
  cacheEnabled: boolean;
}
```

#### S126: Core Integration

```typescript
// SPEC_ID: S126
// IMPLEMENTS: FR016
// INVARIANTS: INV127, INV128

/**
 * Integration with phantom-guard-core.
 *
 * Strategy decision (see ADR-007):
 *   Option A: WASM bundle (preferred for performance)
 *   Option B: Subprocess spawn (fallback)
 *   Option C: HTTP to local server (not recommended)
 *
 * Implementation (Option B - subprocess):
 *   1. Bundle phantom-guard CLI in extension
 *   2. Spawn: `phantom-guard validate --output json {packages}`
 *   3. Parse JSON output
 *   4. Cache results in ExtensionContext.globalState
 *
 * Performance:
 *   - First call: <500ms (subprocess startup)
 *   - Subsequent: <100ms (process reuse)
 */
class CoreIntegration implements vscode.Disposable {
  async validatePackages(
    packages: string[],
    registry: Registry
  ): Promise<ValidationResult>;
}

/**
 * Security Requirements (P0-SEC-001):
 *   - NEVER use shell string interpolation for commands
 *   - ALWAYS use execFile() with array arguments (no shell)
 *   - Validate package names before subprocess: /^[@a-z0-9][a-z0-9._-]*$/i
 *   - Reject packages with shell metacharacters: ; | & $ ` \ " '
 *   - Use child_process.spawn with shell: false (default)
 */
```

### 3.3 New Detection Signals (S060-S079)

#### S060: Namespace Squatting Detector

```python
# SPEC_ID: S060
# IMPLEMENTS: FR020
# INVARIANTS: INV060, INV061

async def detect_namespace_squatting(
    package: str,
    metadata: PackageMetadata,
    registry: Registry,
) -> NamespaceSquatSignal | None:
    """
    Detect namespace squatting attempts.

    Definition:
        Package claims a namespace (prefix/scope) without legitimate ownership.
        Example: "@microsoft/ai-helper" by unknown maintainer.

    Detection logic:
        1. Extract namespace prefix:
           - npm: @scope/package → @scope
           - PyPI: company-package → company (if in known orgs)
           - crates.io: crate_name prefix patterns

        2. Check maintainer legitimacy:
           - npm: Verify @scope ownership via registry.npmjs.org/-/org/{org}/user
           - PyPI: Cross-reference with known org packages
           - crates.io: Check owner teams via /owners endpoint

        3. Score:
           - Claimed high-value namespace + unknown maintainer = 0.35 weight
           - Known org namespace + verified maintainer = 0.0 (safe)

    API endpoints:
        - npm: GET https://registry.npmjs.org/-/org/{org}/user
        - PyPI: No direct API (heuristic based on package patterns)
        - crates.io: GET https://crates.io/api/v1/crates/{crate}/owner_team

    Performance:
        - <100ms additional latency
    """
```

#### S065: Download Inflation Detector

```python
# SPEC_ID: S065
# IMPLEMENTS: FR021
# INVARIANTS: INV065, INV066

async def detect_download_inflation(
    package: str,
    metadata: PackageMetadata,
    registry: Registry,
) -> DownloadInflationSignal | None:
    """
    Detect artificially inflated download counts.

    Definition:
        Package has suspiciously high downloads relative to its age,
        dependents, or ecosystem presence.

    Detection logic:
        1. Calculate downloads per day since creation:
           downloads_per_day = total_downloads / days_since_created

        2. Compare to typical package growth:
           - Top 1%: >10,000 downloads/day (legitimate viral)
           - Normal: 1-1,000 downloads/day
           - Suspicious: >1,000/day AND zero dependents AND <10 stars

        3. Check dependent count:
           - npm: GET https://registry.npmjs.org/-/v1/search?text=depends:{package}
           - PyPI: No direct API (use libraries.io fallback)
           - crates.io: GET https://crates.io/api/v1/crates/{crate}/reverse_dependencies

        4. Score:
           - High downloads + zero dependents + no stars = 0.30 weight
           - High downloads + many dependents = 0.0 (legitimate)

    Thresholds:
        - Suspicious downloads/day: >5,000
        - Minimum age for check: 30 days
        - Zero dependent threshold: 0 reverse deps

    Performance:
        - <200ms additional latency (extra API call)
    """
```

#### S070: Ownership Transfer Detector

```python
# SPEC_ID: S070
# IMPLEMENTS: FR022
# INVARIANTS: INV070, INV071

async def detect_ownership_transfer(
    package: str,
    metadata: PackageMetadata,
    registry: Registry,
) -> OwnershipTransferSignal | None:
    """
    Detect recent suspicious ownership transfers.

    Definition:
        Package maintainer changed recently, potentially indicating
        a hijacked or sold package.

    CRITICAL LIMITATION:
        No public API exposes ownership history. Detection requires
        our own historical snapshots.

    Implementation strategy:
        Phase 1 (v0.2.0): Flag packages with single maintainer + no history
        Phase 2 (v0.3.0): Build ownership snapshot service

        Phase 1 detection:
            1. Check current maintainer count:
               - Single maintainer: minor flag
               - No maintainer info: major flag

            2. Check maintainer account age (if available):
               - npm: User profile has created date
               - PyPI: No public API
               - crates.io: No public API

            3. Cross-reference maintainer across packages:
               - New maintainer with only this one package = suspicious

    Score (P0-DESIGN-001 - reduced from 0.40):
        - Single new maintainer + new package = 0.15 weight
        - Established maintainer + many packages = 0.0 (safe)
        - NOTE: Weight intentionally low due to API limitations

    Performance:
        - <50ms (uses existing metadata)

    Future (Phase 2):
        - Maintain ownership snapshot database
        - Compare current vs historical owners
        - Alert on any ownership change
    """
```

#### S075: Version Spike Detector

```python
# SPEC_ID: S075
# IMPLEMENTS: FR023
# INVARIANTS: INV075, INV076

async def detect_version_spike(
    package: str,
    metadata: PackageMetadata,
    registry: Registry,
) -> VersionSpikeSignal | None:
    """
    Detect suspicious version release patterns.

    Definition:
        Package released many versions in short time, potentially
        indicating malicious rapid iteration or version squatting.

    Detection logic:
        1. Extract version timestamps:
           - PyPI: releases[version].upload_time
           - npm: time[version] in package metadata
           - crates.io: versions[].created_at

        2. Calculate release frequency:
           - Versions in last 24h
           - Versions in last 7 days
           - Average time between versions

        3. Flag patterns:
           - 5+ versions in 24h = suspicious
           - 20+ versions in 7 days with no changelog = suspicious
           - Rapid minor bumps (1.0.0 → 1.0.99) = suspicious

    Score:
        - 5+ versions in 24h = 0.45 weight
        - 20+ versions in 7 days = 0.30 weight
        - Normal release cadence = 0.0

    Exceptions:
        - CI/CD packages often have rapid releases
        - Check for meaningful version increments

    Performance:
        - <10ms (uses existing version metadata)
    """
```

### 3.4 Enhanced Pattern Database (S058-S059)

#### S058: Community Pattern Manager

```python
# SPEC_ID: S058
# IMPLEMENTS: FR024
# INVARIANTS: INV058

class CommunityPatternManager:
    """
    Manage community-contributed patterns.

    Storage:
        - Built-in: src/phantom_guard/patterns/builtin.py
        - User: ~/.phantom-guard/patterns.yaml
        - Community: ~/.phantom-guard/community-patterns.json (downloaded)

    Pattern format:
        patterns:
          - id: "flask-ai-suffix"
            type: "suffix"
            base: "flask"
            suffixes: ["-gpt", "-ai", "-llm", "-chatgpt"]
            confidence: 0.7
            source: "community"
            added: "2026-01-04"

    Update mechanism:
        - Check GitHub releases for new patterns
        - Auto-update with user consent
        - Manual: phantom-guard patterns update

    Contribution:
        - Submit via GitHub PR to patterns repository
        - Review process before inclusion
    """

    def load_patterns(self) -> list[Pattern]: ...
    def add_user_pattern(self, pattern: Pattern) -> None: ...
    async def check_for_updates(self) -> bool: ...
    async def download_community_patterns(self) -> None: ...
```

#### S059: Pattern Validation

```python
# SPEC_ID: S059
# IMPLEMENTS: FR024
# INVARIANTS: INV059

def validate_pattern(pattern: Pattern) -> ValidationResult:
    """
    Validate pattern before addition to database.

    Checks:
        1. Format validity:
           - Required fields present
           - Type is valid (prefix, suffix, compound, regex)
           - Confidence in [0.0, 1.0]

        2. Conflict detection:
           - No duplicate IDs
           - No overlapping patterns that could cause FP

        3. Performance check:
           - Regex patterns compile
           - Pattern doesn't match top 1000 packages (FP check)

    Returns:
        ValidationResult with success/failure and errors
    """
```

---

## 4. Data Structures (v0.2.0 Additions)

### 4.1 GitHub Action Types

```typescript
// Size estimates in comments

interface ActionConfig {
  files: string[];           // 8 bytes (pointer) + array
  failOn: FailOnLevel;       // 1 byte (enum)
  output: OutputFormat;      // 1 byte (enum)
  token: string;             // 8 bytes (pointer) - from GITHUB_TOKEN
}

interface DependencyFile {
  path: string;              // 8 bytes + string
  registry: Registry;        // 1 byte
  packages: string[];        // 8 bytes + array
}

interface PackageReference {
  name: string;              // 8 bytes + string
  version?: string;          // 8 bytes + string | undefined
  file: string;              // 8 bytes (source file path)
  line: number;              // 4 bytes
  registry: Registry;        // 1 byte
}

interface ValidationReport {
  safe: PackageResult[];     // 8 bytes + array
  suspicious: PackageResult[];
  highRisk: PackageResult[];
  notFound: string[];
  scanDurationMs: number;    // 4 bytes
  packagesScanned: number;   // 4 bytes
}

// Total ActionConfig: ~50 bytes typical
// Total ValidationReport: ~1KB typical (50 packages)
```

### 4.2 VS Code Extension Types

```typescript
interface ExtensionReport {
  document: vscode.Uri;      // 8 bytes (pointer)
  diagnostics: vscode.Diagnostic[];  // 8 bytes + array
  summary: {
    safe: number;            // 4 bytes
    suspicious: number;      // 4 bytes
    highRisk: number;        // 4 bytes
    notFound: number;        // 4 bytes
  };
  cachedAt: Date;            // 8 bytes
}

interface PackagePosition {
  name: string;              // 8 bytes + string
  range: vscode.Range;       // 16 bytes (4 x 4-byte numbers)
  registry: Registry;        // 1 byte
}

// Memory budget per open document: ~10KB typical
// Extension total memory budget: <50MB
```

### 4.3 New Signal Types

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class NamespaceSquatSignal:
    """
    SPEC: S060
    Size: ~100 bytes
    """
    namespace: str           # Claimed namespace
    expected_owner: str | None  # Who should own it
    actual_owner: str | None    # Who does own it
    confidence: float        # 0.0 - 1.0


@dataclass(frozen=True, slots=True)
class DownloadInflationSignal:
    """
    SPEC: S065
    Size: ~80 bytes
    """
    downloads_per_day: float
    dependent_count: int
    age_days: int
    suspicion_reason: str    # "zero_dependents", "anomalous_growth"


@dataclass(frozen=True, slots=True)
class OwnershipTransferSignal:
    """
    SPEC: S070
    Size: ~120 bytes
    """
    current_owner: str
    owner_account_age_days: int | None
    owner_package_count: int
    single_maintainer: bool


@dataclass(frozen=True, slots=True)
class VersionSpikeSignal:
    """
    SPEC: S075
    Size: ~60 bytes
    """
    versions_24h: int
    versions_7d: int
    avg_time_between_versions_hours: float
    rapid_pattern: str | None  # "burst", "sequential", None
```

### 4.4 Updated Signal Enum

```python
class Signal(Enum):
    """
    SPEC: S004 (extended in v0.2.0)
    """
    # v0.1.x signals
    NEW_PACKAGE = "new_package"
    LOW_DOWNLOADS = "low_downloads"
    NO_REPOSITORY = "no_repository"
    FEW_RELEASES = "few_releases"
    NO_AUTHOR = "no_author"
    SHORT_DESCRIPTION = "short_description"
    HALLUCINATION_PATTERN = "hallucination_pattern"
    TYPOSQUAT = "typosquat"

    # v0.2.0 NEW signals
    NAMESPACE_SQUATTING = "namespace_squatting"      # S060
    DOWNLOAD_INFLATION = "download_inflation"        # S065
    OWNERSHIP_TRANSFER = "ownership_transfer"        # S070
    VERSION_SPIKE = "version_spike"                  # S075
```

---

## 5. Performance Budget (v0.2.0)

### 5.1 GitHub Action Budgets

| Operation | Budget | Constraint | SPEC_ID | Measurement |
|:----------|:-------|:-----------|:--------|:------------|
| Action cold start | <5s | P99 | S100 | CI timing |
| File discovery | <1s | P99 | S101 | glob timing |
| Package extraction | <100ms | Per file | S102 | parse timing |
| Full workflow (50 pkgs) | <30s | P99 | S103 | CI timing |
| PR comment generation | <100ms | P99 | S104 | timing |
| SARIF generation | <100ms | P99 | S105 | timing |

### 5.2 VS Code Extension Budgets

| Operation | Budget | Constraint | SPEC_ID | Measurement |
|:----------|:-------|:-----------|:--------|:------------|
| Extension activation | <500ms | P99 | S120 | activation timing |
| Document validation | <200ms | Per file | S121 | validation timing |
| Hover tooltip | <50ms | P99 | S122 | hover timing |
| Code action compute | <50ms | P99 | S123 | action timing |
| Status bar update | <10ms | P99 | S124 | UI timing |
| Core subprocess call | <500ms | First call | S126 | IPC timing |

### 5.3 New Detection Signal Budgets

| Operation | Budget | Constraint | SPEC_ID | Measurement |
|:----------|:-------|:-----------|:--------|:------------|
| Namespace squatting | <100ms | P99 | S060 | API + compute |
| Download inflation | <200ms | P99 | S065 | API + compute |
| Ownership transfer | <50ms | P99 | S070 | compute only |
| Version spike | <10ms | P99 | S075 | compute only |
| All 4 signals (cached) | <50ms | P99 | S060-S079 | aggregate |
| All 4 signals (uncached) | <300ms | P99 | S060-S079 | with API calls |

### 5.4 Memory Budgets (v0.2.0)

| Component | Budget | Measurement |
|:----------|:-------|:------------|
| VS Code extension total | <50MB | VS Code profiler |
| Extension per document | <10KB | Memory delta |
| GitHub Action peak | <200MB | Node.js heap |
| Pattern database | <10MB | Loaded size |
| New signal caches | <5MB | Per registry |

---

## 6. Invariant Registry (v0.2.0 Additions)

### 6.1 GitHub Action Invariants

| INV_ID | Statement | Component | Enforcement | Test Type |
|:-------|:----------|:----------|:------------|:----------|
| INV100 | Action always produces valid output | S100 | try/catch + default | integration |
| INV101 | Exit code matches report status | S106 | assertion | unit |
| INV102 | File discovery never throws on invalid glob | S101 | try/catch | unit |
| INV103 | Package extraction handles malformed files | S102 | graceful parsing | unit |
| INV104 | Validation timeout prevents hanging | S103 | AbortController | integration |
| INV105 | PR comment fits GitHub size limit (<65535 chars) | S104 | truncation | unit |
| INV106 | Comment update is idempotent | S104 | sticky comment ID | integration |
| INV107 | SARIF output is schema-valid | S105 | JSON schema validation | unit |
| INV108 | Exit codes are in range [0-5] | S106 | enum constraint | unit |

### 6.2 VS Code Extension Invariants

| INV_ID | Statement | Component | Enforcement | Test Type |
|:-------|:----------|:----------|:------------|:----------|
| INV120 | Extension never blocks UI thread | S120 | async/await | integration |
| INV121 | Activation completes or times out | S120 | timeout wrapper | integration |
| INV122 | Diagnostics are cleared on document close | S121 | dispose handler | unit |
| INV123 | Hover provider returns null on non-package lines | S122 | position check | unit |
| INV124 | Code actions are only for Phantom Guard diagnostics | S123 | source check | unit |
| INV125 | Status bar reflects most recent validation | S124 | update ordering | unit |
| INV126 | Configuration changes trigger re-validation | S125 | event listener | integration |
| INV127 | Core integration fails gracefully on spawn error | S126 | error handling | unit |
| INV128 | No shell injection via package names | S126 | argument escaping | security |

### 6.3 New Detection Signal Invariants

| INV_ID | Statement | Component | Enforcement | Test Type |
|:-------|:----------|:----------|:------------|:----------|
| INV060 | Namespace extraction handles all registry formats | S060 | pattern tests | unit |
| INV061 | Namespace check doesn't flag legitimate org packages | S060 | allowlist | integration |
| INV065 | Download inflation uses age-adjusted threshold | S065 | formula check | unit |
| INV066 | Zero-dependent check handles API failures gracefully | S065 | fallback | unit |
| INV070 | Ownership transfer defaults to safe on missing data | S070 | null handling | unit |
| INV071 | Single-maintainer flag alone is not HIGH_RISK | S070 | weight check | unit |
| INV075 | Version spike uses UTC timestamps consistently | S075 | timezone handling | unit |
| INV076 | Rapid release detection excludes CI packages | S075 | exception list | unit |

---

## 7. Architectural Decisions (v0.2.0)

### ADR-006: JavaScript GitHub Action over Docker

**SPEC_ID**: ADR006

#### Context

GitHub Actions can be JavaScript (node20) or Docker-based. Need to decide for phantom-guard-action.

#### Options Considered

1. **JavaScript/TypeScript (node20)** - Native GitHub support, fast startup
2. **Docker** - Any language, more isolation, slower startup
3. **Composite** - Shell scripts, limited functionality

#### Decision

**JavaScript/TypeScript with node20** runtime.

#### Consequences

- Positive: <5s cold start (vs 30-60s for Docker)
- Positive: Native GitHub API access via @actions/core
- Positive: Easy SARIF generation with existing JS libraries
- Negative: Must bundle phantom-guard-core as subprocess or WASM
- Negative: TypeScript compilation step required

#### Verification

- Cold start benchmark: Must be <5s
- Feature parity: All CLI features available

---

### ADR-007: VS Code Extension Core Integration Strategy

**SPEC_ID**: ADR007

#### Context

VS Code extension needs to call phantom-guard-core. Three strategies possible.

#### Options Considered

1. **WASM bundle** - Compile Python to WASM, bundle in extension
2. **Subprocess spawn** - Bundle CLI, spawn process
3. **HTTP local server** - Start server, make HTTP calls

#### Decision

**Subprocess spawn** for v0.2.0, with WASM as future optimization.

#### Rationale

- WASM: Pyodide (Python WASM) is 10MB+ and slow to load
- HTTP: Requires background process management, port conflicts
- Subprocess: Simple, works with existing CLI, acceptable performance

#### Implementation

```typescript
// spawn phantom-guard validate --output json {packages}
const result = await spawn('phantom-guard', [
  'validate',
  '--output', 'json',
  ...packages
], { timeout: 30000 });
```

#### Consequences

- Positive: Reuses existing CLI code
- Positive: Simple integration
- Positive: No WASM compilation complexity
- Negative: Subprocess overhead (~200-500ms first call)
- Negative: Must bundle Python runtime or assume installed
- Neutral: Can optimize to WASM in v0.3.0 if needed

#### Verification

- Extension activation: <500ms with subprocess
- Document validation: <200ms for cached packages

---

### ADR-008: New Signal Weight Calibration

**SPEC_ID**: ADR008

#### Context

Four new detection signals need weight calibration to maintain <0.5% FP rate.

#### Weight Assignment

Based on V0.2.0_MARKET_RESEARCH.md and risk analysis:

| Signal | Weight | Rationale |
|:-------|:-------|:----------|
| NAMESPACE_SQUATTING | 0.35 | High precision indicator |
| DOWNLOAD_INFLATION | 0.30 | Moderate confidence |
| OWNERSHIP_TRANSFER | 0.15 | Weak signal in v0.2.0 due to API limitations (P0-DESIGN-001) |
| VERSION_SPIKE | 0.45 | Highest correlation with malicious packages |

#### Calibration Method

1. Test against known malicious packages (from security advisories)
2. Test against top 1000 legitimate packages (FP check)
3. Adjust weights until FP <0.5% AND TP >95%

#### Updated Scoring Formula (P0-DESIGN-002)

With 4 new signals, the raw score range changes from v0.1.x:

```
v0.1.x range: [-100, +160]
v0.2.0 additions: +35 (namespace) +30 (downloads) +15 (ownership) +45 (version) = +125
v0.2.0 range: [-100, +285]

Formula: normalized = (raw_score + 100) / 385
Clamping: result = max(0.0, min(1.0, normalized))
```

#### Consequences

- Positive: Data-driven weight assignment
- Positive: Maintains low FP rate
- Negative: Requires continuous calibration as ecosystem changes
- Neutral: Weights are configurable by users

---

### ADR-009: PR Comment Strategy

**SPEC_ID**: ADR009

#### Context

Need to provide validation results in PR. Options: inline annotations, PR comment, check run.

#### Options Considered

1. **Inline annotations** - Via GitHub Check API
2. **PR comment** - Markdown comment on PR
3. **Check run summary** - GitHub Actions summary
4. **All three** - Maximum visibility

#### Decision

**PR comment (sticky)** as primary, with SARIF for Code Scanning integration.

#### Implementation

Use `marocchino/sticky-pull-request-comment` pattern:

```typescript
// Find existing comment
const existingComment = await findComment({
  issue_number: pr,
  body_includes: '<!-- phantom-guard-report -->'
});

// Update or create
if (existingComment) {
  await updateComment(existingComment.id, body);
} else {
  await createComment(pr, body);
}
```

#### Consequences

- Positive: Clear visibility in PR
- Positive: Updates on new pushes (sticky)
- Positive: SARIF provides Security tab integration
- Negative: Comment can be long for many packages
- Neutral: Collapsible sections for large reports

---

### ADR-010: VS Code Security Requirements

**SPEC_ID**: ADR010

#### Context

VS Code marketplace has security concerns (1,283 extensions with malicious deps). Our extension must be exemplary.

#### Security Requirements

| Requirement | Implementation |
|:------------|:---------------|
| No secrets in code | Use SecretStorage API |
| No network to unknown hosts | Only registry APIs |
| No shell execution | Subprocess with escaped args only |
| Minimal permissions | Only file read |
| Open source | Full source on GitHub |
| Verified publisher | Apply for Microsoft verification |
| npm audit clean | CI check on every release |
| SBOM | Generate and publish |

#### Verification

- Security audit before each release
- npm audit in CI pipeline
- No eval/Function constructor usage
- CSP headers if any webviews

#### Consequences

- Positive: Trusted by security-conscious users
- Positive: Differentiation from other extensions
- Positive: Sets example for ecosystem
- Negative: Additional development overhead
- Neutral: Standard security practices

---

## 8. Security Considerations (v0.2.0)

### 8.1 GitHub Action Security

| Concern | Mitigation |
|:--------|:-----------|
| GITHUB_TOKEN exposure | Use secrets, never log |
| Workflow injection | Validate inputs |
| Dependency confusion | Pin all action versions |
| Supply chain | npm audit, lockfile |

### 8.2 VS Code Extension Security

| Concern | Mitigation |
|:--------|:-----------|
| Code execution | No eval, no Function constructor |
| Shell injection | Escape all subprocess arguments |
| Secret storage | Use VS Code SecretStorage API |
| Network calls | Allowlist registries only |
| File access | Read-only, workspace only |

### 8.3 New Signal Security

| Concern | Mitigation |
|:--------|:-----------|
| API abuse | Rate limiting, caching |
| Data poisoning | Validate API responses |
| False positives | Conservative weights |
| Privacy | No user data collection |

---

## 9. Trace Matrix (v0.2.0)

| SPEC_ID | Description | Component | Module | Tests |
|:--------|:------------|:----------|:-------|:------|
| S100 | Action entry point | GitHub Action | action/index.ts | T100.* |
| S101 | File discovery | GitHub Action | action/files.ts | T101.* |
| S102 | Package extractor | GitHub Action | action/extract.ts | T102.* |
| S103 | Validation orchestrator | GitHub Action | action/validate.ts | T103.* |
| S104 | PR comment generator | GitHub Action | action/comment.ts | T104.* |
| S105 | SARIF generator | GitHub Action | action/sarif.ts | T105.* |
| S106 | Exit code handler | GitHub Action | action/exit.ts | T106.* |
| S120 | Extension activation | VS Code | extension/activate.ts | T120.* |
| S121 | Diagnostic provider | VS Code | extension/diagnostics.ts | T121.* |
| S122 | Hover provider | VS Code | extension/hover.ts | T122.* |
| S123 | Code action provider | VS Code | extension/actions.ts | T123.* |
| S124 | Status bar | VS Code | extension/statusbar.ts | T124.* |
| S125 | Configuration | VS Code | extension/config.ts | T125.* |
| S126 | Core integration | VS Code | extension/core.ts | T126.* |
| S060 | Namespace squatting | Detector | core/signals/namespace.py | T060.* |
| S065 | Download inflation | Detector | core/signals/downloads.py | T065.* |
| S070 | Ownership transfer | Detector | core/signals/ownership.py | T070.* |
| S075 | Version spike | Detector | core/signals/versions.py | T075.* |
| S058 | Community patterns | Patterns | patterns/community.py | T058.* |
| S059 | Pattern validation | Patterns | patterns/validate.py | T059.* |

---

## 10. File Structure (v0.2.0)

```
phantom-guard/
├── src/
│   └── phantom_guard/
│       ├── __init__.py
│       ├── py.typed
│       ├── types.py             # Extended with new signals
│       ├── config.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── detector.py
│       │   ├── analyzer.py
│       │   ├── patterns.py
│       │   ├── typosquat.py
│       │   ├── scorer.py
│       │   └── signals/         # NEW in v0.2.0
│       │       ├── __init__.py
│       │       ├── namespace.py  # S060
│       │       ├── downloads.py  # S065
│       │       ├── ownership.py  # S070
│       │       └── versions.py   # S075
│       ├── registry/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── pypi.py
│       │   ├── npm.py
│       │   └── crates.py
│       ├── cache/
│       │   ├── __init__.py
│       │   └── cache.py
│       └── patterns/
│           ├── __init__.py
│           ├── database.py
│           ├── builtin.py
│           ├── community.py      # S058 NEW
│           └── validate.py       # S059 NEW
├── action/                       # GitHub Action - NEW in v0.2.0
│   ├── action.yml                # Action manifest
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts              # S100
│   │   ├── files.ts              # S101
│   │   ├── extract.ts            # S102
│   │   ├── validate.ts           # S103
│   │   ├── comment.ts            # S104
│   │   ├── sarif.ts              # S105
│   │   └── exit.ts               # S106
│   └── dist/                     # Compiled output
│       └── index.js
├── vscode/                       # VS Code Extension - NEW in v0.2.0
│   ├── package.json              # Extension manifest
│   ├── tsconfig.json
│   ├── src/
│   │   ├── extension.ts          # S120
│   │   ├── diagnostics.ts        # S121
│   │   ├── hover.ts              # S122
│   │   ├── actions.ts            # S123
│   │   ├── statusbar.ts          # S124
│   │   ├── config.ts             # S125
│   │   └── core.ts               # S126
│   └── out/                      # Compiled output
├── tests/
│   ├── unit/
│   │   ├── test_signals_namespace.py   # T060.*
│   │   ├── test_signals_downloads.py   # T065.*
│   │   ├── test_signals_ownership.py   # T070.*
│   │   └── test_signals_versions.py    # T075.*
│   ├── integration/
│   └── property/
├── docs/
│   └── architecture/
│       ├── ARCHITECTURE.md       # v0.1.0
│       └── ARCHITECTURE_V0.2.0.md  # This file
└── pyproject.toml
```

---

## Appendix A: Open Questions

| Question | Impact | Resolution Target |
|:---------|:-------|:------------------|
| WASM vs subprocess for VS Code? | Performance | ADR-007 (subprocess chosen) |
| Should action support private registries? | Feature scope | v0.3.0 |
| How to handle npm @scope ownership verification failure? | Accuracy | Gate 2 |
| Should version spike exclude known CI packages? | False positives | Gate 2 |
| Community patterns: manual review or automated? | Scale | Gate 2 |

---

## Appendix B: Dependencies (v0.2.0)

### Python (phantom-guard-core)

```toml
# No new dependencies for core signals
# Using existing httpx, aiosqlite, etc.
```

### GitHub Action (action/)

```json
{
  "dependencies": {
    "@actions/core": "^1.10.0",
    "@actions/github": "^6.0.0",
    "@actions/glob": "^0.4.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "esbuild": "^0.19.0"
  }
}
```

### VS Code Extension (vscode/)

```json
{
  "dependencies": {},
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "typescript": "^5.0.0",
    "esbuild": "^0.19.0",
    "@vscode/test-electron": "^2.3.0"
  }
}
```

---

## Appendix C: API Endpoints for New Signals

### Namespace Squatting (S060)

| Registry | Endpoint | Purpose |
|:---------|:---------|:--------|
| npm | `GET /-/org/{org}/user` | Verify org membership |
| npm | `GET /-/user/org.couchdb.user:{user}` | Get user's orgs |
| PyPI | (heuristic) | No direct namespace API |
| crates.io | `GET /api/v1/crates/{crate}/owner_team` | Get owner teams |

### Download Inflation (S065)

| Registry | Endpoint | Purpose |
|:---------|:---------|:--------|
| npm | `GET /-/v1/search?text=depends:{pkg}` | Count dependents |
| PyPI | (libraries.io fallback) | No native dependent API |
| crates.io | `GET /api/v1/crates/{crate}/reverse_dependencies` | Count dependents |

### Version Spike (S075)

| Registry | Field | Location |
|:---------|:------|:---------|
| PyPI | `releases[version].upload_time` | Package JSON |
| npm | `time[version]` | Package JSON |
| crates.io | `versions[].created_at` | Package JSON |

---

**Gate 1 Status**: CONDITIONAL_GO - P0 fixes applied

**P0 Fixes Applied**:
- P0-PERF-001: Updated NFR011 validation latency to "<500ms first, <200ms cached"
- P0-SEC-001: Added security requirements to S126 (shell injection prevention)
- P0-DESIGN-001: Reduced OWNERSHIP_TRANSFER weight from 0.40 to 0.15
- P0-DESIGN-002: Added updated scoring formula (range [-100, +285], divisor 385)

**P1 Issues Tracked**: See .fortress/reports/validation/HOSTILE_REVIEW_ARCH_V0.2.0_2026-01-04.md

**Next Step**: Run `/spec` to begin Gate 2 (Specification)

**Document Version**: 1.0.1
