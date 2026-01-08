# Phantom Guard — Specification v0.2.0

> **Version**: 0.2.0
> **Date**: 2026-01-04
> **Status**: APPROVED
> **Approver**: HOSTILE_VALIDATOR
> **Gate**: 2 of 6 - COMPLETE
> **Base**: Extends SPECIFICATION.md (v0.1.0)
> **Review**: .fortress/reports/validation/HOSTILE_REVIEW_SPEC_V0.2.0_FINAL_2026-01-04.md

---

## 1. Invariant Registry (v0.2.0 Additions)

### 1.1 GitHub Action Invariants (INV100-INV108)

| INV_ID | Statement | Source | Enforcement | Test Type |
|:-------|:----------|:-------|:------------|:----------|
| INV100 | Action always produces valid output (never throws uncaught) | S100 | try/catch wrapper + default output | integration |
| INV101 | Exit code matches report status exactly | S106 | assertion in determineExitCode | unit |
| INV102 | File discovery never throws on invalid glob pattern | S101 | try/catch with empty array fallback | unit |
| INV103 | Package extraction handles all malformed file formats gracefully | S102 | graceful parsing with warnings | unit |
| INV104 | Validation timeout prevents hanging (batch <30s total; 60s circuit breaker for single stuck package) | S103 | AbortController + timeout | integration |
| INV105 | PR comment fits GitHub size limit (<65535 chars) | S104 | truncation with "..." indicator | unit |
| INV106 | Comment update is idempotent (same input = same output) | S104 | sticky comment ID pattern | integration |
| INV107 | SARIF output is schema-valid per SARIF 2.1.0 | S105 | JSON schema validation | unit |
| INV108 | Exit codes are always in range [0-5] | S106 | enum constraint in TypeScript | unit |

### 1.2 VS Code Extension Invariants (INV120-INV128)

| INV_ID | Statement | Source | Enforcement | Test Type |
|:-------|:----------|:-------|:------------|:----------|
| INV120 | Extension never blocks UI thread (all I/O is async) | S120 | async/await pattern | integration |
| INV121 | Activation completes within 500ms or times out gracefully | S120 | timeout wrapper with fallback | integration |
| INV122 | Diagnostics are cleared when document is closed | S121 | dispose handler registration | unit |
| INV123 | Hover provider returns null on non-package lines | S122 | position boundary check | unit |
| INV124 | Code actions only appear for Phantom Guard diagnostics | S123 | source === 'phantom-guard' check | unit |
| INV125 | Status bar reflects most recent validation result | S124 | update ordering guarantee | unit |
| INV126 | Configuration changes trigger re-validation of open documents | S125 | onDidChangeConfiguration listener | integration |
| INV127 | Core integration fails gracefully on subprocess spawn error | S126 | error handling with fallback | unit |
| INV128 | No shell injection via package names | S126 | execFile with array args + regex validation | security |

### 1.3 New Detection Signal Invariants (INV060-INV076)

| INV_ID | Statement | Source | Enforcement | Test Type |
|:-------|:----------|:-------|:------------|:----------|
| INV060 | Namespace extraction handles all registry formats correctly | S060 | pattern tests for each registry | unit |
| INV061 | Namespace check never flags legitimate org packages (FP < 0.1%) | S060 | allowlist + integration tests | integration |
| INV062 | Namespace signal returns None on API failure (not exception) | S060 | try/except with None return | unit |
| INV065 | Download inflation uses age-adjusted threshold (not absolute) | S065 | formula verification test | unit |
| INV066 | Zero-dependent check handles API failures gracefully | S065 | fallback to None | unit |
| INV067 | libraries.io fallback is optional (failure = skip signal) | S065 | try/except with None return | unit |
| INV070 | Ownership transfer defaults to safe on missing data | S070 | null handling with safe default | unit |
| INV071 | Single-maintainer flag alone is never HIGH_RISK | S070 | weight check (0.15 max) | unit |
| INV072 | Ownership signal returns None when all data missing | S070 | conditional return | unit |
| INV075 | Version spike uses UTC timestamps consistently | S075 | timezone handling tests | unit |
| INV076 | Rapid release detection excludes known CI packages | S075 | exception list check | unit |
| INV077 | Version timestamps are parsed correctly for all registries | S075 | format tests per registry | unit |

### 1.4 Pattern Database Invariants (INV058-INV059)

| INV_ID | Statement | Source | Enforcement | Test Type |
|:-------|:----------|:-------|:------------|:----------|
| INV058 | Community patterns are validated before loading | S058 | validate_pattern call | unit |
| INV059 | Pattern confidence is always in [0.0, 1.0] | S059 | range check in validation | unit |
| INV058a | Pattern updates require explicit user consent | S058 | config flag check | integration |
| INV059a | Invalid patterns are rejected with clear error messages | S059 | validation result with errors | unit |

### 1.5 Scoring Formula Update (P0-DESIGN-002)

**Updated formula for v0.2.0 with 4 new signals:**

```
v0.2.0 Signal Weights:
  Existing signals (from v0.1.x):
    TYPOSQUAT:             +50 points
    HALLUCINATION_PATTERN: +40 points
    NEW_PACKAGE:           +30 points
    LOW_DOWNLOADS:         +20 points
    NO_REPOSITORY:         +20 points
    FEW_RELEASES:          +15 points
    NO_AUTHOR:             +10 points
    SHORT_DESCRIPTION:     +10 points

  New signals (v0.2.0):
    VERSION_SPIKE:         +45 points (5+ versions in 24h)
    NAMESPACE_SQUATTING:   +35 points
    DOWNLOAD_INFLATION:    +30 points
    OWNERSHIP_TRANSFER:    +15 points (reduced per P0-DESIGN-001)

Raw score range: [-100, +285]
Formula: normalized = (raw_score + 100) / 385
Clamping: result = max(0.0, min(1.0, normalized))
```

---

## 2. Error Type Definitions (v0.2.0 Additions)

### 2.1 GitHub Action Errors

```typescript
// action/src/errors.ts

class ActionError extends Error {
  constructor(message: string, public readonly code: number) {
    super(message);
  }
}

class FileDiscoveryError extends ActionError {
  // code = 4 (configuration error)
  constructor(pattern: string, reason: string) {
    super(`File discovery failed for pattern '${pattern}': ${reason}`, 4);
  }
}

class PackageExtractionError extends ActionError {
  // code = 4 (configuration error)
  constructor(file: string, reason: string) {
    super(`Package extraction failed for '${file}': ${reason}`, 4);
  }
}

class ValidationTimeoutError extends ActionError {
  // code = 5 (runtime error)
  constructor(packages: string[], timeoutMs: number) {
    super(`Validation timed out after ${timeoutMs}ms for ${packages.length} packages`, 5);
  }
}

class CommentUpdateError extends ActionError {
  // Non-fatal, log and continue
  constructor(reason: string) {
    super(`PR comment update failed: ${reason}`, 0);
  }
}

class SarifGenerationError extends ActionError {
  // code = 5 (runtime error)
  constructor(reason: string) {
    super(`SARIF generation failed: ${reason}`, 5);
  }
}
```

### 2.2 VS Code Extension Errors

```typescript
// vscode/src/errors.ts

class ExtensionError extends Error {
  constructor(message: string, public readonly recoverable: boolean = true) {
    super(message);
  }
}

class ActivationError extends ExtensionError {
  constructor(reason: string) {
    super(`Extension activation failed: ${reason}`, false);
  }
}

class CoreSpawnError extends ExtensionError {
  constructor(reason: string) {
    super(`Failed to spawn phantom-guard process: ${reason}`, true);
  }
}

class CoreTimeoutError extends ExtensionError {
  constructor(timeoutMs: number) {
    super(`Core process timed out after ${timeoutMs}ms`, true);
  }
}

class CoreParseError extends ExtensionError {
  constructor(output: string) {
    super(`Failed to parse core output: ${output.slice(0, 100)}...`, true);
  }
}

class PythonNotFoundError extends ExtensionError {
  constructor() {
    super('Python 3.11+ not found. Please install Python or configure path.', false);
  }
}
```

### 2.3 New Signal Errors

```python
# src/phantom_guard/core/signals/errors.py

class SignalError(PhantomGuardError):
    """Base exception for signal detection errors."""
    pass

class NamespaceCheckError(SignalError):
    """Namespace squatting check failed."""
    pass

class DependentCountError(SignalError):
    """Failed to fetch dependent count."""
    registry: str
    package: str

class OwnershipDataError(SignalError):
    """Failed to fetch ownership data."""
    pass

class VersionHistoryError(SignalError):
    """Failed to parse version history."""
    pass
```

### 2.4 Error Handling Rules (v0.2.0)

| Error | Component | Behavior | User Message |
|:------|:----------|:---------|:-------------|
| FileDiscoveryError | Action | Log warning, continue | "Warning: Pattern matched no files" |
| PackageExtractionError | Action | Log warning, skip file | "Warning: Could not parse {file}" |
| ValidationTimeoutError | Action | Partial results + warning | "Timeout: {n} packages not validated" |
| CoreSpawnError | Extension | Show error, disable validation | "Phantom Guard unavailable" |
| PythonNotFoundError | Extension | Show install prompt | "Install Python 3.11+" |
| NamespaceCheckError | Signal | Skip signal, continue | (silent) |
| DependentCountError | Signal | Skip signal, continue | (silent) |

---

## 3. Edge Case Catalog (v0.2.0)

### 3.1 GitHub Action File Discovery (EC200-EC215)

| EC_ID | Scenario | Input | Expected | Test Type |
|:------|:---------|:------|:---------|:----------|
| EC200 | Valid requirements.txt | `requirements.txt` exists | File found, pypi registry | unit |
| EC201 | Valid package.json | `package.json` exists | File found, npm registry | unit |
| EC202 | Valid Cargo.toml | `Cargo.toml` exists | File found, crates registry | unit |
| EC203 | Glob pattern | `requirements/*.txt` | All matching files | unit |
| EC204 | No matches | `*.nonexistent` | Empty array, no error | unit |
| EC205 | Invalid glob syntax | `[invalid` | Empty array, warning logged | unit |
| EC206 | Symlink to file | `symlink -> requirements.txt` | File followed | integration |
| EC207 | Broken symlink | `broken -> nonexistent` | Skipped with warning | unit |
| EC208 | Directory instead of file | `requirements/` (dir) | Skipped | unit |
| EC209 | Binary file | `requirements.bin` | Parse fails gracefully | unit |
| EC210 | Very large file | `10MB requirements.txt` | Parsed with warning | integration |
| EC211 | Empty file | `empty.txt` (0 bytes) | Empty package list | unit |
| EC212 | UTF-8 BOM | `\ufeff` at start | BOM stripped | unit |
| EC213 | CRLF line endings | Windows line endings | Parsed correctly | unit |
| EC214 | Mixed registries | `package.json` + `requirements.txt` | Both detected | integration |
| EC215 | Nested directories | `**/requirements.txt` | Recursive discovery | integration |

### 3.2 GitHub Action Package Extraction (EC220-EC235)

| EC_ID | Scenario | Input | Expected | Test Type |
|:------|:---------|:------|:---------|:----------|
| EC220 | Simple package | `flask` | Package: flask | unit |
| EC221 | Version specifier | `flask>=2.0` | Package: flask (version stripped) | unit |
| EC222 | Comment line | `# flask` | Ignored | unit |
| EC223 | Inline comment | `flask # web framework` | Package: flask | unit |
| EC224 | Environment marker | `flask; python_version >= "3.8"` | Package: flask | unit |
| EC225 | Extra specifier | `flask[async]` | Package: flask | unit |
| EC226 | URL dependency | `git+https://...` | Skipped with warning | unit |
| EC227 | Local path | `./local_package` | Skipped with warning | unit |
| EC228 | Scoped npm | `@scope/package` | Package: @scope/package | unit |
| EC229 | npm version | `"express": "^4.0"` | Package: express | unit |
| EC230 | npm dev dependency | devDependencies section | Included | unit |
| EC231 | Cargo inline table | `flask = { version = "2.0" }` | Package: flask | unit |
| EC232 | Cargo features | `flask = { features = ["..."] }` | Package: flask | unit |
| EC233 | Duplicate package | `flask` twice | Deduplicated | unit |
| EC234 | Case sensitivity | `Flask` vs `flask` | Normalized to lowercase | unit |
| EC235 | Empty line | blank line | Ignored | unit |

### 3.3 GitHub Action PR Comments (EC240-EC255)

| EC_ID | Scenario | Condition | Expected | Test Type |
|:------|:---------|:----------|:---------|:----------|
| EC240 | No existing comment | First run | Create new comment | integration |
| EC241 | Existing comment | Second run | Update existing | integration |
| EC242 | All safe | No issues | Summary only | unit |
| EC243 | Some suspicious | Mixed results | Collapsible details | unit |
| EC244 | Many packages | 100+ packages | Truncated with count | unit |
| EC245 | Comment too long | >65535 chars | Truncated with "..." | unit |
| EC246 | No PR context | Push event | Skip comment, SARIF only | integration |
| EC247 | Permission denied | No write access | Log warning, continue | integration |
| EC248 | Rate limited | GitHub 429 | Retry with backoff | integration |
| EC249 | Network error | Connection failed | Log error, continue | integration |
| EC250 | Markdown injection | Package name with `\`\`\`` | Escaped properly | security |
| EC251 | Unicode in name | `flask-помощник` | Rendered correctly | unit |
| EC252 | Long package name | 100+ char name | Truncated in display | unit |
| EC253 | High risk details | HIGH_RISK package | Prominent warning | unit |
| EC254 | Empty results | No packages found | "No packages to validate" | unit |
| EC255 | Partial failure | Some packages failed | Show succeeded + failures | unit |

### 3.4 GitHub Action SARIF Output (EC260-EC270)

| EC_ID | Scenario | Input | Expected | Test Type |
|:------|:---------|:------|:---------|:----------|
| EC260 | Valid SARIF | Normal results | Schema-valid SARIF 2.1.0 | unit |
| EC261 | High risk finding | HIGH_RISK package | level: "error" | unit |
| EC262 | Suspicious finding | SUSPICIOUS package | level: "warning" | unit |
| EC263 | Not found finding | NOT_FOUND package | level: "error" with PG003 | unit |
| EC264 | Location mapping | package.json:10 | Correct line reference | unit |
| EC265 | Multiple files | 3 dependency files | Multiple physicalLocation | unit |
| EC266 | No findings | All safe | Empty results array | unit |
| EC267 | Rule definitions | All rule IDs | PG001, PG002, PG003 defined | unit |
| EC268 | Tool info | Version metadata | Correct tool.driver | unit |
| EC269 | Large results | 500+ findings | Valid structure | integration |
| EC270 | Special characters | `@scope/pkg` in name | Properly escaped | unit |

### 3.5 VS Code Extension Activation (EC300-EC315)

| EC_ID | Scenario | Condition | Expected | Test Type |
|:------|:---------|:----------|:---------|:----------|
| EC300 | Normal activation | Python available | Activate < 500ms | integration |
| EC301 | Python not found | No python in PATH | Error message, disabled | integration |
| EC302 | Wrong Python version | Python 3.9 | Error message, disabled | integration |
| EC303 | phantom-guard not installed | pip list empty | Install prompt | integration |
| EC304 | Workspace without deps | No requirements.txt | Lazy activation | unit |
| EC305 | Multiple workspaces | Multi-root workspace | Activate for each | integration |
| EC306 | Slow activation | >500ms | Timeout warning | integration |
| EC307 | Crash during activation | Exception thrown | Graceful failure | unit |
| EC308 | Extension disabled | User disabled | No activation | unit |
| EC309 | Reload after crash | Previous crash | Clean restart | integration |
| EC310 | Low memory | <100MB available | Reduced functionality | integration |
| EC311 | Extension update | New version | Reactivate cleanly | integration |
| EC312 | Conflicting extension | Similar extension | Warning message | integration |
| EC313 | Remote workspace | SSH/WSL | Works correctly | integration |
| EC314 | Container workspace | Dev Container | Works correctly | integration |
| EC315 | Virtual environment | venv active | Use venv python | integration |

### 3.6 VS Code Diagnostics (EC320-EC335)

| EC_ID | Scenario | Input | Expected | Test Type |
|:------|:---------|:------|:---------|:----------|
| EC320 | Safe package | `flask` in requirements.txt | No diagnostic | unit |
| EC321 | Suspicious package | `flask-gpt` | Warning diagnostic | unit |
| EC322 | High risk package | known malware | Error diagnostic | unit |
| EC323 | Not found package | `nonexistent123` | Error diagnostic | unit |
| EC324 | Multiple issues | 3 suspicious packages | 3 diagnostics | unit |
| EC325 | Document close | Close file | Diagnostics cleared | unit |
| EC326 | Document edit | Add new package | Re-validate | integration |
| EC327 | Rapid edits | Type quickly | Debounced (500ms) | integration |
| EC328 | Large file | 500 packages | All validated | integration |
| EC329 | Syntax error in file | Malformed JSON | Parse error shown | unit |
| EC330 | Diagnostic range | Line with package | Correct line highlight | unit |
| EC331 | Version in range | `flask>=2.0` | Range covers `flask` only | unit |
| EC332 | Comment line | `# flask` | No diagnostic | unit |
| EC333 | Multiple files open | 3 files | Independent diagnostics | integration |
| EC334 | File rename | Rename requirements.txt | Diagnostics transfer | integration |
| EC335 | External edit | Edit outside VS Code | Re-validate on focus | integration |

### 3.7 VS Code Hover Provider (EC340-EC350)

| EC_ID | Scenario | Position | Expected | Test Type |
|:------|:---------|:---------|:---------|:----------|
| EC340 | Package line | On `flask` | Risk tooltip | unit |
| EC341 | Comment line | On `# comment` | No hover | unit |
| EC342 | Empty line | On blank line | No hover | unit |
| EC343 | Version specifier | On `>=2.0` | Package tooltip (flask) | unit |
| EC344 | JSON key | On `"flask":` | Package tooltip | unit |
| EC345 | JSON value | On `"^2.0"` | No hover (or package) | unit |
| EC346 | Multiple signals | HIGH_RISK package | All signals listed | unit |
| EC347 | Safe package | On `flask` | "Safe" status | unit |
| EC348 | Cached result | Second hover | Instant response | unit |
| EC349 | Pending validation | During validation | "Validating..." | unit |
| EC350 | Long signal list | 5+ signals | Scrollable/truncated | unit |

### 3.8 Namespace Squatting Detection (EC400-EC415)

| EC_ID | Scenario | Package | Expected | Test Type |
|:------|:---------|:--------|:---------|:----------|
| EC400 | Legitimate npm scope | `@babel/core` | No signal (verified owner) | integration |
| EC401 | Fake npm scope | `@microsoft/fake-pkg` | NAMESPACE_SQUATTING | integration |
| EC402 | PyPI company prefix | `google-cloud-storage` | No signal (verified) | integration |
| EC403 | PyPI fake company | `google-ai-helper` | NAMESPACE_SQUATTING | unit |
| EC404 | crates.io team package | `tokio-*` | No signal (verified) | integration |
| EC405 | Unknown namespace | `@unknown/pkg` | Minor flag only | unit |
| EC406 | No namespace | `flask` | No signal | unit |
| EC407 | Nested scope | `@org/sub/pkg` | Scope extracted correctly | unit |
| EC408 | API unavailable | npm org API 500 | Skip signal | unit |
| EC409 | Rate limited | npm org API 429 | Skip signal, log | unit |
| EC410 | Known org list | `@angular/core` | No API call needed | unit |
| EC411 | Case sensitivity | `@Microsoft/pkg` | Normalized to lowercase | unit |
| EC412 | Empty scope | `@/package` | InvalidPackageNameError | unit |
| EC413 | Numeric scope | `@123/package` | Valid, check ownership | unit |
| EC414 | Hyphenated scope | `@my-org/package` | Valid, check ownership | unit |
| EC415 | Unicode in scope | `@орг/package` | InvalidPackageNameError | unit |

### 3.9 Download Inflation Detection (EC420-EC435)

| EC_ID | Scenario | Downloads/Age | Expected | Test Type |
|:------|:---------|:--------------|:---------|:----------|
| EC420 | Legitimate viral | 1M downloads, 1000 dependents | No signal | unit |
| EC421 | Inflated downloads | 100K downloads, 0 dependents | DOWNLOAD_INFLATION | unit |
| EC422 | New package | 100 downloads, 7 days old | No signal (too new) | unit |
| EC423 | Normal growth | 10K downloads, 100 days | No signal | unit |
| EC424 | Zero dependents check | 50K/day, 0 deps | Signal triggered | unit |
| EC425 | API unavailable | npm search fails | Skip signal | unit |
| EC426 | libraries.io fallback | PyPI, no native API | Use libraries.io | integration |
| EC427 | libraries.io unavailable | Fallback fails | Skip signal | unit |
| EC428 | Stale data | libraries.io 7 days old | Use with warning | unit |
| EC429 | Very old package | 5 years old, low downloads | No signal | unit |
| EC430 | Just viral | Trending package | Check GitHub stars | unit |
| EC431 | Bot downloads | Periodic spikes | Pattern detection | unit |
| EC432 | Threshold edge | Exactly 5000/day | No signal (boundary) | unit |
| EC433 | Missing download data | No stats available | Skip signal | unit |
| EC434 | crates.io reverse deps | Native API available | Use native API | integration |
| EC435 | npm dependents search | Search API used | Correct query | integration |

### 3.10 Ownership Transfer Detection (EC440-EC455)

| EC_ID | Scenario | Metadata | Expected | Test Type |
|:------|:---------|:---------|:---------|:----------|
| EC440 | Single maintainer | 1 maintainer, 50 packages | No signal | unit |
| EC441 | New single maintainer | 1 maintainer, 1 package | Minor flag (0.15) | unit |
| EC442 | Multiple maintainers | 3 maintainers | No signal | unit |
| EC443 | No maintainer info | Field missing | No signal (default safe) | unit |
| EC444 | npm user profile | User created 2020 | Established, no signal | unit |
| EC445 | New npm user | User created last month | Flag | unit |
| EC446 | Cross-reference check | User has 1 package only | Flag | integration |
| EC447 | Cross-reference pass | User has 50 packages | No signal | integration |
| EC448 | PyPI no user API | No user metadata | Skip maintainer age check | unit |
| EC449 | crates.io teams | Team ownership | No signal (org) | unit |
| EC450 | Combined signals | Single + new + 1 pkg | Full 0.15 weight | unit |
| EC451 | Historical data | v0.3.0 future | Not implemented | - |
| EC452 | Partial data | Only maintainer count | Use available data | unit |
| EC453 | Orphaned package | No active maintainer | Flag | unit |
| EC454 | Transfer detected | Owner changed (future) | HIGH alert (v0.3.0) | - |
| EC455 | API rate limit | npm user API 429 | Skip check | unit |

### 3.11 Version Spike Detection (EC460-EC475)

| EC_ID | Scenario | Versions | Expected | Test Type |
|:------|:---------|:---------|:---------|:----------|
| EC460 | Normal release | 1 version/week | No signal | unit |
| EC461 | Spike 24h | 5 versions in 24h | VERSION_SPIKE (0.45) | unit |
| EC462 | Spike 7d | 20 versions in 7d | VERSION_SPIKE (0.30) | unit |
| EC463 | CI package | Known CI tool | Excluded from check | unit |
| EC464 | Meaningful versions | 1.0 → 1.1 → 2.0 | No signal | unit |
| EC465 | Micro bumps | 1.0.0 → 1.0.99 | Suspicious pattern | unit |
| EC466 | Pre-release spam | 1.0.0-alpha.1 through .50 | Flag | unit |
| EC467 | Single version | Only 1 release ever | No signal | unit |
| EC468 | Old package | No versions in 1 year | No signal | unit |
| EC469 | Timezone handling | UTC timestamps | Consistent calculation | unit |
| EC470 | PyPI timestamps | upload_time format | Parsed correctly | unit |
| EC471 | npm timestamps | time object format | Parsed correctly | unit |
| EC472 | crates.io timestamps | created_at format | Parsed correctly | unit |
| EC473 | Missing timestamps | Some versions undated | Use available data | unit |
| EC474 | Future timestamp | Clock skew | Handled gracefully | unit |
| EC475 | Rapid then stable | Burst, then normal | Flag during burst | unit |

### 3.12 Signal Combinations (EC500-EC510)

| EC_ID | Scenario | Signals | Expected | Test Type |
|:------|:---------|:--------|:---------|:----------|
| EC500 | Two signals fire | VERSION_SPIKE + NAMESPACE | Combined weight applied (0.45 + 0.35 = 0.80) | unit |
| EC501 | Three signals fire | VERSION + NAMESPACE + DOWNLOAD | Combined weight applied (0.45 + 0.35 + 0.30 = 1.10) | unit |
| EC502 | All four new signals fire | VERSION + NAMESPACE + DOWNLOAD + OWNERSHIP | Sum of weights (0.45 + 0.35 + 0.30 + 0.15 = 1.25), clamped | unit |
| EC503 | New + old signals | VERSION_SPIKE + TYPOSQUAT | Both contribute to score | unit |
| EC504 | Conflicting signals | Safe by ownership, risky by version | Version signal takes precedence (higher weight) | unit |
| EC505 | Signal with API failure | NAMESPACE ok, DOWNLOAD API fails | Use available signal only | unit |
| EC506 | All API failures | All 4 new signal APIs fail | Fall back to v0.1.x signals only | unit |
| EC507 | Partial data | Some signals return None | Use non-None signals, skip None | unit |
| EC508 | Score overflow | Many signals fire pushing raw >285 | Clamped to 1.0 | unit |
| EC509 | Parallel execution | 4 signals computed together | <300ms total | bench |
| EC510 | Signal ordering | Multiple signals with same weight | Consistent alphabetical ordering | unit |

### 3.13 Community Patterns (EC480-EC495)

| EC_ID | Scenario | Pattern | Expected | Test Type |
|:------|:---------|:--------|:---------|:----------|
| EC480 | Load built-in | Default patterns | All loaded | unit |
| EC481 | Load user patterns | ~/.phantom-guard/patterns.yaml | Merged with built-in | unit |
| EC482 | Load community | Downloaded patterns | Merged after validation | unit |
| EC483 | Invalid pattern ID | Duplicate ID | Rejected with error | unit |
| EC484 | Invalid confidence | confidence = 1.5 | Rejected | unit |
| EC485 | Invalid type | type = "unknown" | Rejected | unit |
| EC486 | Regex pattern | Valid regex | Compiled and used | unit |
| EC487 | Invalid regex | `[invalid` | Rejected with error | unit |
| EC488 | FP check | Pattern matches "requests" | Rejected | unit |
| EC489 | Update available | New version on GitHub | User prompted | integration |
| EC490 | Update download | User accepts | Downloaded + validated | integration |
| EC491 | Update rejected | Invalid signature | Rejected | security |
| EC492 | Offline mode | No network | Use cached patterns | unit |
| EC493 | Pattern conflict | Overlapping patterns | Warning logged | unit |
| EC494 | Empty pattern file | 0 patterns | Use built-in only | unit |
| EC495 | Large pattern file | 10000 patterns | Performance check | bench |

---

## 4. Acceptance Matrix (v0.2.0)

### 4.1 SPEC_ID to Test Count

| SPEC_ID | Description | Unit | Property | Fuzz | Integration | Bench | Security | Total |
|:--------|:------------|:-----|:---------|:-----|:------------|:------|:---------|:------|
| S100 | Action entry point | 5 | 0 | 0 | 3 | 1 | 0 | 9 |
| S101 | File discovery | 12 | 0 | 1 | 2 | 0 | 0 | 15 |
| S102 | Package extractor | 16 | 0 | 1 | 0 | 0 | 0 | 17 |
| S103 | Validation orchestrator | 6 | 0 | 0 | 3 | 1 | 0 | 10 |
| S104 | PR comment generator | 12 | 0 | 0 | 4 | 0 | 1 | 17 |
| S105 | SARIF generator | 10 | 0 | 0 | 1 | 0 | 0 | 11 |
| S106 | Exit code handler | 6 | 1 | 0 | 0 | 0 | 0 | 7 |
| S120 | Extension activation | 8 | 0 | 0 | 8 | 1 | 0 | 17 |
| S121 | Diagnostic provider | 14 | 0 | 0 | 4 | 0 | 0 | 18 |
| S122 | Hover provider | 10 | 0 | 0 | 1 | 0 | 0 | 11 |
| S123 | Code action provider | 8 | 0 | 0 | 2 | 0 | 0 | 10 |
| S124 | Status bar | 6 | 0 | 0 | 2 | 0 | 0 | 8 |
| S125 | Configuration | 8 | 0 | 0 | 2 | 0 | 0 | 10 |
| S126 | Core integration | 8 | 0 | 1 | 3 | 1 | 2 | 15 |
| S060 | Namespace squatting | 12 | 1 | 0 | 4 | 0 | 0 | 17 |
| S065 | Download inflation | 14 | 1 | 0 | 3 | 0 | 0 | 18 |
| S070 | Ownership transfer | 12 | 1 | 0 | 2 | 0 | 0 | 15 |
| S075 | Version spike | 14 | 1 | 0 | 0 | 0 | 0 | 15 |
| S058 | Community patterns | 10 | 0 | 0 | 3 | 1 | 1 | 15 |
| S059 | Pattern validation | 10 | 1 | 1 | 0 | 0 | 0 | 12 |
| S080 | Signal combinations | 10 | 0 | 0 | 0 | 1 | 0 | 11 |
| **TOTAL** | | **201** | **6** | **5** | **47** | **6** | **4** | **269** |

### 4.2 Test ID Registry (v0.2.0)

#### GitHub Action Tests (T100-T106)

| TEST_ID | SPEC_ID | INV_ID | EC_ID | Type | Description |
|:--------|:--------|:-------|:------|:-----|:------------|
| T100.01 | S100 | INV100 | - | unit | Action completes without throwing |
| T100.02 | S100 | INV100 | - | integration | Full workflow runs successfully |
| T100.03 | S100 | - | - | bench | Cold start < 5s |
| T101.01 | S101 | INV102 | EC200 | unit | Find requirements.txt |
| T101.02 | S101 | INV102 | EC201 | unit | Find package.json |
| T101.03 | S101 | INV102 | EC204 | unit | No matches returns empty array |
| T101.04 | S101 | INV102 | EC205 | unit | Invalid glob handled |
| T101.05 | S101 | - | EC215 | integration | Recursive discovery works |
| T102.01 | S102 | INV103 | EC220 | unit | Extract simple package |
| T102.02 | S102 | INV103 | EC221 | unit | Strip version specifier |
| T102.03 | S102 | INV103 | EC228 | unit | Handle scoped npm package |
| T102.04 | S102 | INV103 | EC233 | unit | Deduplicate packages |
| T102.05 | S102 | - | - | fuzz | Random file content |
| T103.01 | S103 | INV104 | - | unit | Validation completes |
| T103.02 | S103 | INV104 | - | integration | 50 packages < 30s |
| T103.03 | S103 | INV104 | - | bench | Measure timing |
| T104.01 | S104 | INV105 | EC242 | unit | Generate safe summary |
| T104.02 | S104 | INV105 | EC243 | unit | Generate suspicious details |
| T104.03 | S104 | INV105 | EC245 | unit | Truncate long comment |
| T104.04 | S104 | INV106 | EC241 | integration | Update existing comment |
| T104.05 | S104 | - | EC250 | security | Escape markdown injection |
| T105.01 | S105 | INV107 | EC260 | unit | Valid SARIF structure |
| T105.02 | S105 | INV107 | EC261 | unit | HIGH_RISK = error level |
| T105.03 | S105 | INV107 | EC266 | unit | Empty results handled |
| T106.01 | S106 | INV101 | - | unit | Exit 0 for all safe |
| T106.02 | S106 | INV101 | - | unit | Exit 1 for suspicious |
| T106.03 | S106 | INV101 | - | unit | Exit 2 for high-risk |
| T106.04 | S106 | INV108 | - | proptest | Exit code in [0-5] |

#### VS Code Extension Tests (T120-T126)

| TEST_ID | SPEC_ID | INV_ID | EC_ID | Type | Description |
|:--------|:--------|:-------|:------|:-----|:------------|
| T120.01 | S120 | INV120 | EC300 | integration | Activation < 500ms |
| T120.02 | S120 | INV121 | EC306 | integration | Timeout handled |
| T120.03 | S120 | - | EC301 | integration | Python not found error |
| T120.04 | S120 | - | EC303 | integration | phantom-guard not installed |
| T121.01 | S121 | INV122 | EC320 | unit | Safe package = no diagnostic |
| T121.02 | S121 | INV122 | EC321 | unit | Suspicious = warning |
| T121.03 | S121 | INV122 | EC322 | unit | High risk = error |
| T121.04 | S121 | INV122 | EC325 | unit | Diagnostics cleared on close |
| T121.05 | S121 | - | EC327 | integration | Debounce works |
| T122.01 | S122 | INV123 | EC340 | unit | Hover on package line |
| T122.02 | S122 | INV123 | EC341 | unit | No hover on comment |
| T122.03 | S122 | INV123 | EC347 | unit | Safe package tooltip |
| T123.01 | S123 | INV124 | - | unit | Code action for diagnostic |
| T123.02 | S123 | INV124 | - | unit | Typosquat fix suggestion |
| T124.01 | S124 | INV125 | - | unit | Status bar updates |
| T124.02 | S124 | INV125 | - | unit | Shows error count |
| T125.01 | S125 | INV126 | - | unit | Config change triggers revalidate |
| T125.02 | S125 | - | - | integration | Threshold config works |
| T126.01 | S126 | INV127 | - | unit | Spawn error handled |
| T126.02 | S126 | INV128 | - | security | Shell injection prevented |
| T126.03 | S126 | INV128 | - | security | Package name validated |
| T126.04 | S126 | - | - | bench | First call < 500ms |

#### New Signal Tests (T060-T075)

| TEST_ID | SPEC_ID | INV_ID | EC_ID | Type | Description |
|:--------|:--------|:-------|:------|:-----|:------------|
| T060.01 | S060 | INV060 | EC400 | integration | Legitimate npm scope |
| T060.02 | S060 | INV060 | EC401 | integration | Fake npm scope detected |
| T060.03 | S060 | INV061 | EC402 | integration | Legitimate PyPI company |
| T060.04 | S060 | INV061 | EC403 | unit | Fake company prefix |
| T060.05 | S060 | INV062 | EC408 | unit | API failure = no signal |
| T060.06 | S060 | - | - | proptest | Namespace extraction |
| T065.01 | S065 | INV065 | EC420 | unit | Legitimate viral package |
| T065.02 | S065 | INV065 | EC421 | unit | Inflated downloads detected |
| T065.03 | S065 | INV066 | EC425 | unit | API failure = skip signal |
| T065.04 | S065 | INV067 | EC426 | integration | libraries.io fallback |
| T065.05 | S065 | - | EC432 | unit | Threshold boundary |
| T065.06 | S065 | - | - | proptest | Age-adjusted calculation |
| T070.01 | S070 | INV070 | EC443 | unit | Missing data = safe |
| T070.02 | S070 | INV071 | EC441 | unit | Single maintainer = 0.15 max |
| T070.03 | S070 | INV072 | EC452 | unit | Partial data handled |
| T070.04 | S070 | - | EC446 | integration | Cross-reference check |
| T070.05 | S070 | - | - | proptest | Weight never exceeds 0.15 |
| T075.01 | S075 | INV075 | EC461 | unit | 5 versions in 24h detected |
| T075.02 | S075 | INV075 | EC462 | unit | 20 versions in 7d detected |
| T075.03 | S075 | INV076 | EC463 | unit | CI package excluded |
| T075.04 | S075 | INV077 | EC470 | unit | PyPI timestamp parsed |
| T075.05 | S075 | INV077 | EC471 | unit | npm timestamp parsed |
| T075.06 | S075 | INV077 | EC472 | unit | crates.io timestamp parsed |
| T075.07 | S075 | - | - | proptest | UTC consistency |

#### Signal Combination Tests (T080)

| TEST_ID | SPEC_ID | INV_ID | EC_ID | Type | Description |
|:--------|:--------|:-------|:------|:-----|:------------|
| T080.01 | S060,S075 | - | EC500 | unit | Two signals combine correctly |
| T080.02 | S060,S065,S075 | - | EC501 | unit | Three signals combine correctly |
| T080.03 | S060,S065,S070,S075 | - | EC502 | unit | All four signals combine + clamp |
| T080.04 | S075 | - | EC503 | unit | New + old signals combine |
| T080.05 | S070,S075 | - | EC504 | unit | Higher weight takes precedence |
| T080.06 | S060,S065 | INV062,INV066 | EC505 | unit | API failure skips signal |
| T080.07 | S060,S065,S070,S075 | - | EC506 | unit | All API failures = v0.1.x only |
| T080.08 | S060,S065,S070,S075 | - | EC507 | unit | Partial data handled |
| T080.09 | S060,S065,S070,S075 | - | EC508 | unit | Score clamped to 1.0 |
| T080.10 | S060,S065,S070,S075 | - | EC509 | bench | Parallel execution <300ms |
| T080.11 | S060,S065,S070,S075 | - | EC510 | unit | Consistent signal ordering |

#### Pattern Database Tests (T058-T059)

| TEST_ID | SPEC_ID | INV_ID | EC_ID | Type | Description |
|:--------|:--------|:-------|:------|:-----|:------------|
| T058.01 | S058 | INV058 | EC480 | unit | Built-in patterns loaded |
| T058.02 | S058 | INV058 | EC481 | unit | User patterns merged |
| T058.03 | S058 | INV058a | EC489 | integration | Update prompt shown |
| T058.04 | S058 | - | EC491 | security | Invalid signature rejected |
| T058.05 | S058 | - | EC495 | bench | Large pattern performance |
| T059.01 | S059 | INV059 | EC484 | unit | Invalid confidence rejected |
| T059.02 | S059 | INV059 | EC485 | unit | Invalid type rejected |
| T059.03 | S059 | INV059a | EC488 | unit | FP check catches issues |
| T059.04 | S059 | - | EC487 | unit | Invalid regex rejected |
| T059.05 | S059 | - | - | fuzz | Random pattern input |
| T059.06 | S059 | - | - | proptest | Confidence bounds |

---

## 5. Failure Mode Analysis (v0.2.0)

### 5.1 Critical Failures (Must Not Happen)

| FM_ID | Failure | Impact | Prevention | Detection | Recovery |
|:------|:--------|:-------|:-----------|:----------|:---------|
| FM100 | Action exits non-zero when all safe | CI breaks unnecessarily | Exit code testing | CI monitoring | Fix and release patch |
| FM101 | Shell injection via package name | Remote code execution | execFile + regex validation | Security testing | Emergency patch |
| FM102 | Extension crashes VS Code | User loses work | Exception handling | Crash reports | Auto-disable |
| FM103 | False positive on @babel/core | Major org flagged | Verified namespace list | Integration tests | Add to allowlist |
| FM104 | Score formula produces >1.0 | Invalid recommendations | Clamping + property tests | Unit tests | Fix normalization |
| FM105 | SARIF invalid schema | GitHub rejects upload | Schema validation | CI testing | Fix generator |

### 5.2 Recoverable Failures

| FM_ID | Failure | Impact | Recovery | User Experience |
|:------|:--------|:-------|:---------|:----------------|
| FM110 | PR comment API fails | No comment | SARIF only + log warning | "SARIF uploaded, comment failed" |
| FM111 | Python subprocess timeout | Validation incomplete | Partial results + timeout warning | "Timeout: N packages not checked" |
| FM112 | npm org API unavailable | Namespace signal missing | Skip signal, continue | (silent) |
| FM113 | libraries.io unavailable | Download inflation signal missing | Skip signal, continue | (silent) |
| FM114 | VS Code validation slow | UX degradation | Progress indicator | "Validating 50 packages..." |
| FM115 | Pattern update fails | Stale patterns | Use cached patterns | "Update failed, using cached" |
| FM116 | Extension activation slow | First run delay | Background loading | Status bar: "Loading..." |

### 5.3 Degraded Operation Modes

| Condition | Component | Behavior | User Impact | How to Exit |
|:----------|:----------|:---------|:------------|:------------|
| Python not installed | Extension | Disabled with message | No validation | Install Python |
| phantom-guard not installed | Extension | Install prompt | No validation | pip install |
| GitHub token missing | Action | Limited API access | No comments | Add GITHUB_TOKEN |
| Offline mode | All | Cache only | Stale data possible | Network restored |
| Rate limited | All | Exponential backoff | Slower checks | Wait for reset |
| All APIs down | All | Pattern matching only | Reduced accuracy | APIs recover |

---

## 6. Security Verification Matrix (v0.2.0)

### 6.1 GitHub Action Security

| Requirement | Implementation | Test | Status |
|:------------|:---------------|:-----|:-------|
| No hardcoded secrets | Environment variables only | Code scan | Required |
| Token never logged | Mask in output | Log inspection | Required |
| Input validation | Regex for package names | T102.* | Required |
| Dependency pinning | lockfile + audit | CI check | Required |
| No shell interpretation | execFile with array | T126.02 | Required |

### 6.2 VS Code Extension Security

| Requirement | Implementation | Test | Status |
|:------------|:---------------|:-----|:-------|
| No secrets in code | SecretStorage API | Code review | Required |
| Shell injection prevention | execFile + validation | T126.02-03 | Required |
| Minimal permissions | Only file read | Manifest review | Required |
| No network to unknown | Registry allowlist | Network mock | Required |
| No eval/Function | Code scan | Static analysis | Required |
| npm audit clean | CI pipeline | Audit check | Required |

### 6.3 Pattern Update Security

| Requirement | Implementation | Test | Status |
|:------------|:---------------|:-----|:-------|
| Signature verification | GPG sign patterns | T058.04 | Required |
| HTTPS only | URL validation | Config check | Required |
| User consent | Config flag | T058.03 | Required |
| Rollback capability | Keep previous version | Integration | Required |

---

## 7. Coverage Targets (v0.2.0)

| Component | Line | Branch | Property | Fuzz | Benchmark |
|:----------|:-----|:-------|:---------|:-----|:----------|
| Core signals (Python) | 90% | 85% | 1000 iter | 10 min | Yes |
| GitHub Action (TS) | 85% | 80% | N/A | N/A | Yes |
| VS Code Extension (TS) | 80% | 75% | N/A | N/A | Yes |
| Pattern validation | 95% | 90% | 1000 iter | 30 min | No |

### 7.1 Coverage Exclusions

Files excluded from coverage requirements:
- `action/dist/*` (compiled output)
- `vscode/out/*` (compiled output)
- `**/types.ts`, `**/types.py` (type definitions)
- Test files themselves

---

## 8. Trace Links (v0.2.0)

| SPEC_ID | INV_IDs | EC_IDs | TEST_IDs | Module |
|:--------|:--------|:-------|:---------|:-------|
| S100 | INV100, INV101 | - | T100.* | action/index.ts |
| S101 | INV102 | EC200-EC215 | T101.* | action/files.ts |
| S102 | INV103 | EC220-EC235 | T102.* | action/extract.ts |
| S103 | INV104 | - | T103.* | action/validate.ts |
| S104 | INV105, INV106 | EC240-EC255 | T104.* | action/comment.ts |
| S105 | INV107 | EC260-EC270 | T105.* | action/sarif.ts |
| S106 | INV108 | - | T106.* | action/exit.ts |
| S120 | INV120, INV121 | EC300-EC315 | T120.* | vscode/extension.ts |
| S121 | INV122 | EC320-EC335 | T121.* | vscode/diagnostics.ts |
| S122 | INV123 | EC340-EC350 | T122.* | vscode/hover.ts |
| S123 | INV124 | - | T123.* | vscode/actions.ts |
| S124 | INV125 | - | T124.* | vscode/statusbar.ts |
| S125 | INV126 | - | T125.* | vscode/config.ts |
| S126 | INV127, INV128 | - | T126.* | vscode/core.ts |
| S060 | INV060-INV062 | EC400-EC415 | T060.* | signals/namespace.py |
| S065 | INV065-INV067 | EC420-EC435 | T065.* | signals/downloads.py |
| S070 | INV070-INV072 | EC440-EC455 | T070.* | signals/ownership.py |
| S075 | INV075-INV077 | EC460-EC475 | T075.* | signals/versions.py |
| S058 | INV058, INV058a | EC480-EC495 | T058.* | patterns/community.py |
| S059 | INV059, INV059a | EC480-EC495 | T059.* | patterns/validate.py |
| S080 | INV060-INV077 | EC500-EC510 | T080.* | signals/combination.py |

---

## Appendix A: Open Questions for Gate 3

| Question | Impact | Owner |
|:---------|:-------|:------|
| Should VS Code tests use @vscode/test-electron or mock? | Test strategy | TEST_ARCHITECT |
| How to test GitHub Action without real GitHub? | Test infrastructure | TEST_ARCHITECT |
| Should signal APIs be mocked or use live endpoints? | Test reliability | TEST_ARCHITECT |
| Property test framework for TypeScript: fast-check? | Test tooling | TEST_ARCHITECT |

---

## Appendix B: P1 Issues from Architecture Review

| Issue ID | Description | Resolution in Spec |
|:---------|:------------|:-------------------|
| P1-SPEC-001 | Add error handling specs S110, S130 | Section 2: Error Type Definitions |
| P1-PERF-001 | Specify parallel execution for new signals | EC420+ documents parallel behavior |
| P1-SEC-001 | Add signature verification for community patterns | Section 6.3, INV058a |
| P1-DESIGN-001 | Add Python availability check to ADR-007 | EC301-EC303, T120.03 |
| P1-DESIGN-002 | Add version compatibility check to S126 | EC303, error handling |

---

## Appendix C: CI Package Exception List (EC463)

Packages excluded from version spike detection due to legitimate rapid release patterns:

```yaml
ci_package_exceptions:
  pypi:
    - "pytest-*"
    - "*-nightly"
    - "*-dev"
    - "*-snapshot"
  npm:
    - "@types/*"  # DefinitelyTyped auto-publishes
    - "*-canary"
    - "*-nightly"
    - "*-next"
  crates:
    - "*-sys"  # System bindings often update frequently
    - "*-nightly"
```

---

## Appendix D: Known Namespace Prefixes (EC410)

Verified organization namespaces that skip API checks:

```yaml
verified_namespaces:
  npm_scopes:
    - "@angular"
    - "@babel"
    - "@types"
    - "@microsoft"
    - "@azure"
    - "@google"
    - "@aws-sdk"
    - "@apollo"
    - "@nestjs"
    - "@vue"
    - "@react-native"

  pypi_prefixes:
    - "google-"
    - "azure-"
    - "aws-"
    - "boto3-"
    - "django-"
    - "flask-"
    - "pytest-"
    - "sphinx-"

  crates_prefixes:
    - "tokio-"
    - "serde-"
    - "async-"
    - "futures-"
```

---

**Gate 2 Status**: COMPLETE

**Tests Defined**: 269 total (201 unit, 6 property, 5 fuzz, 47 integration, 6 bench, 4 security)

**Invariants Defined**: 35 new invariants (INV058-INV128)

**Edge Cases Cataloged**: 187 edge cases (EC200-EC510)

**P0 Fixes Applied**:
- P0-INV-001: Fixed INV104 timeout inconsistency (batch <30s, 60s circuit breaker)
- P0-EC-001: Added signal combination edge cases EC500-EC510

**Approval**: HOSTILE_VALIDATOR GO verdict issued 2026-01-04

**Next Step**: Proceed to Gate 3 (Test Design) with `/test`

**Document Version**: 1.0.2
