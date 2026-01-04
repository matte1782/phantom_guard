# Phantom Guard — Development Roadmap v0.2.0

> **Version**: 0.2.0
> **Created**: 2026-01-04
> **Last Updated**: 2026-01-04
> **Status**: ACTIVE
> **Gate**: 4 of 6 - Planning
> **Base**: Extends ROADMAP.md (v0.1.x complete)

---

## Overview

### v0.2.0 Theme: Developer Workflow Integration

Building on the v0.1.x core engine, v0.2.0 adds:
1. **GitHub Action** — CI/CD integration via GitHub Marketplace
2. **VS Code Extension** — Real-time IDE validation
3. **4 New Detection Signals** — Enhanced threat detection
4. **Enhanced Pattern Database** — Community contribution system

### Success Criteria (from V0.2.0_MARKET_RESEARCH.md)

| Criterion | v0.1.x Baseline | v0.2.0 Target |
|:----------|:----------------|:--------------|
| Detection signals | 11 | 15 (+4 new) |
| False positive rate | 0.08% | <0.5% |
| GitHub stars | 0 | 500 (3mo) |
| VS Code installs | 0 | 1000 (6mo) |
| GitHub Action repos | 0 | 500 (6mo) |

### Total Effort

| Phase | Weeks | Hours (with 20% buffer) |
|:------|:------|:------------------------|
| New Detection Signals | 6-7 | 96 |
| GitHub Action | 8 | 48 |
| VS Code Extension | 9 | 48 |
| Polish & Release | 10 | 40 |
| **Total** | **5 weeks** | **232 hours** |

### Estimation Approach

> **P1-EST-001 Resolution**: This roadmap uses **"Likely + 25% Weekly Buffer"** estimation:
> - Individual tasks use "Likely" estimates from three-point estimation
> - Each week includes 20-25% buffer hours for contingency
> - This provides equivalent padding to the 2.5x multiplier while keeping task granularity visible
> - Total buffer: ~46 hours across 5 weeks (20% of 232 hours)

---

## Phase 6: New Detection Signals - Part 1 (Week 6)

### Goals
- Enhance pattern database with community contribution system
- Implement namespace squatting detection
- Implement download inflation detection

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W6.1 | S058 | Community pattern manager | 6 | ✅ COMPLETE |
| W6.2 | S059 | Pattern validation | 4 | ✅ COMPLETE |
| W6.3 | S060 | Namespace squatting signal | 8 | ✅ COMPLETE |
| W6.4 | S065 | Download inflation signal | 8 | ✅ COMPLETE |
| W6.5 | - | Signal integration tests | 6 | ✅ COMPLETE |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 6 | **40** | - |

### W6.1: Community Pattern Manager

```markdown
## TASK: W6.1 — Community Pattern Manager

### Traces
- SPEC: S058
- INVARIANTS: INV058, INV058a
- TESTS: T058.01-T058.05

### Definition
Implement community pattern contribution system with storage, loading, and update mechanism.

### Acceptance Criteria
- [ ] T058.01 passes (built-in patterns loaded)
- [ ] T058.02 passes (user patterns merged)
- [ ] T058.03 passes (update prompt shown)
- [ ] T058.04 passes (invalid signature rejected)
- [ ] T058.05 passes (large pattern performance <100ms)
- [ ] INV058 enforced (patterns validated before loading)
- [ ] INV058a enforced (update requires user consent)
- [ ] mypy passes with no errors
- [ ] 90% coverage on patterns/community.py

### Estimated Effort
- Optimistic: 3 hours
- Likely: 6 hours
- Pessimistic: 12 hours
- **Planned**: 6 hours

### Dependencies
- None (first task in phase)

### Pre-Conditions
- Test stubs T058.* exist (GATE 3)
- Pattern format defined in architecture

### Post-Conditions
- Tests T058.01-T058.05 pass (not skipped)
- src/phantom_guard/patterns/community.py exists
- Code has IMPLEMENTS: S058 comments
```

### W6.2: Pattern Validation

```markdown
## TASK: W6.2 — Pattern Validation

### Traces
- SPEC: S059
- INVARIANTS: INV059, INV059a
- TESTS: T059.01-T059.06

### Definition
Implement pattern validation with confidence bounds, type checking, and false positive prevention.

### Acceptance Criteria
- [ ] T059.01 passes (invalid confidence rejected)
- [ ] T059.02 passes (invalid type rejected)
- [ ] T059.03 passes (FP check catches issues)
- [ ] T059.04 passes (invalid regex rejected)
- [ ] T059.05 passes (random pattern input fuzz)
- [ ] T059.06 passes (confidence bounds proptest)
- [ ] INV059 enforced (confidence in [0.0, 1.0])
- [ ] INV059a enforced (clear error messages)

### Estimated Effort
- Optimistic: 2 hours
- Likely: 4 hours
- Pessimistic: 8 hours
- **Planned**: 4 hours

### Dependencies
- W6.1 (uses Pattern types)

### Post-Conditions
- Tests T059.01-T059.06 pass
- src/phantom_guard/patterns/validate.py exists
```

### W6.3: Namespace Squatting Signal

```markdown
## TASK: W6.3 — Namespace Squatting Signal

### Traces
- SPEC: S060
- INVARIANTS: INV060, INV061, INV062
- TESTS: T060.01-T060.06

### Definition
Implement namespace squatting detection for npm scopes, PyPI prefixes, and crates.io teams.

### Acceptance Criteria
- [ ] T060.01 passes (legitimate npm scope not flagged)
- [ ] T060.02 passes (fake npm scope detected)
- [ ] T060.03 passes (legitimate PyPI company not flagged)
- [ ] T060.04 passes (fake company prefix detected)
- [ ] T060.05 passes (API failure = no signal)
- [ ] T060.06 passes (namespace extraction proptest)
- [ ] INV060 enforced (handles all registry formats)
- [ ] INV061 enforced (FP < 0.1%)
- [ ] INV062 enforced (returns None on API failure)
- [ ] <100ms additional latency

### Estimated Effort
- Optimistic: 4 hours
- Likely: 8 hours
- Pessimistic: 16 hours
- **Planned**: 8 hours

### Dependencies
- Existing registry clients (S020-S039)

### Post-Conditions
- Tests T060.01-T060.06 pass
- src/phantom_guard/core/signals/namespace.py exists
```

### W6.4: Download Inflation Signal

```markdown
## TASK: W6.4 — Download Inflation Signal

### Traces
- SPEC: S065
- INVARIANTS: INV065, INV066, INV067
- TESTS: T065.01-T065.06

### Definition
Implement download inflation detection using age-adjusted thresholds and dependent count.

### Acceptance Criteria
- [ ] T065.01 passes (legitimate viral not flagged)
- [ ] T065.02 passes (inflated downloads detected)
- [ ] T065.03 passes (API failure = skip signal)
- [ ] T065.04 passes (libraries.io fallback works)
- [ ] T065.05 passes (threshold boundary)
- [ ] T065.06 passes (age-adjusted calculation proptest)
- [ ] INV065 enforced (age-adjusted threshold)
- [ ] INV066 enforced (graceful API failure)
- [ ] INV067 enforced (optional libraries.io)
- [ ] <200ms additional latency

### Estimated Effort
- Optimistic: 4 hours
- Likely: 8 hours
- Pessimistic: 16 hours
- **Planned**: 8 hours

### Dependencies
- Existing registry clients

### Post-Conditions
- Tests T065.01-T065.06 pass
- src/phantom_guard/core/signals/downloads.py exists
```

### Exit Criteria (Week 6)
- [ ] All W6.* tasks complete
- [ ] T058.*, T059.*, T060.*, T065.* tests passing
- [ ] Property tests for INV059, INV060, INV065 passing
- [ ] Integration tests with mocked APIs passing
- [ ] Coverage ≥90% on new modules
- [ ] mypy --strict passes

---

## Phase 7: New Detection Signals - Part 2 (Week 7)

### Goals
- Implement ownership transfer detection
- Implement version spike detection
- Implement signal combination logic with updated scoring formula

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W7.1 | S070 | Ownership transfer signal | 6 | ✅ COMPLETE |
| W7.2 | S075 | Version spike signal | 8 | ✅ COMPLETE |
| W7.3 | S080 | Signal combination + scoring update | 8 | ✅ COMPLETE |
| W7.4 | - | Full signal integration tests | 6 | ✅ COMPLETE |
| W7.5 | - | Performance benchmarks (4 signals <300ms) | 4 | ✅ COMPLETE |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 7 | **40** | - |

### W7.1: Ownership Transfer Signal

```markdown
## TASK: W7.1 — Ownership Transfer Signal

### Traces
- SPEC: S070
- INVARIANTS: INV070, INV071, INV072
- TESTS: T070.01-T070.05

### Definition
Implement ownership transfer detection with maintainer analysis and cross-reference checks.

### Acceptance Criteria
- [ ] T070.01 passes (missing data = safe)
- [ ] T070.02 passes (single maintainer = 0.15 max)
- [ ] T070.03 passes (partial data handled)
- [ ] T070.04 passes (cross-reference check)
- [ ] T070.05 passes (weight never exceeds 0.15 proptest)
- [ ] INV070 enforced (defaults to safe on missing data)
- [ ] INV071 enforced (single-maintainer alone is not HIGH_RISK)
- [ ] INV072 enforced (returns None when all data missing)
- [ ] <50ms latency (uses existing metadata)

### Estimated Effort
- Optimistic: 3 hours
- Likely: 6 hours
- Pessimistic: 12 hours
- **Planned**: 6 hours

### Dependencies
- Existing registry clients

### Post-Conditions
- Tests T070.01-T070.05 pass
- src/phantom_guard/core/signals/ownership.py exists
```

### W7.2: Version Spike Signal

```markdown
## TASK: W7.2 — Version Spike Signal

### Traces
- SPEC: S075
- INVARIANTS: INV075, INV076, INV077
- TESTS: T075.01-T075.07

### Definition
Implement version spike detection with UTC timestamps and CI package exceptions.

### Acceptance Criteria
- [ ] T075.01 passes (5 versions in 24h detected)
- [ ] T075.02 passes (20 versions in 7d detected)
- [ ] T075.03 passes (CI package excluded)
- [ ] T075.04 passes (PyPI timestamp parsed)
- [ ] T075.05 passes (npm timestamp parsed)
- [ ] T075.06 passes (crates.io timestamp parsed)
- [ ] T075.07 passes (UTC consistency proptest)
- [ ] INV075 enforced (UTC timestamps consistently)
- [ ] INV076 enforced (excludes CI packages)
- [ ] INV077 enforced (all registry timestamp formats)
- [ ] <10ms latency (uses existing metadata)

### Estimated Effort
- Optimistic: 4 hours
- Likely: 8 hours
- Pessimistic: 16 hours
- **Planned**: 8 hours

### Dependencies
- Existing registry metadata

### Post-Conditions
- Tests T075.01-T075.07 pass
- src/phantom_guard/core/signals/versions.py exists
```

### W7.3: Signal Combination + Scoring Update

```markdown
## TASK: W7.3 — Signal Combination + Scoring Update

### Traces
- SPEC: S080, S007-S009
- INVARIANTS: INV060-INV077 (all signal invariants)
- TESTS: T080.01-T080.11

### Definition
Implement signal combination logic and update scoring formula per ADR-008 (P0-DESIGN-002).

### Updated Scoring Formula (P0-DESIGN-002)
```
v0.2.0 Signal Weights:
  VERSION_SPIKE:         +45 points
  NAMESPACE_SQUATTING:   +35 points
  DOWNLOAD_INFLATION:    +30 points
  OWNERSHIP_TRANSFER:    +15 points

Raw score range: [-100, +285]
Formula: normalized = (raw_score + 100) / 385
Clamping: result = max(0.0, min(1.0, normalized))
```

### Acceptance Criteria
- [ ] T080.01 passes (two signals combine correctly)
- [ ] T080.02 passes (three signals combine correctly)
- [ ] T080.03 passes (all four signals combine + clamp)
- [ ] T080.04 passes (new + old signals combine)
- [ ] T080.05 passes (higher weight takes precedence)
- [ ] T080.06 passes (API failure skips signal)
- [ ] T080.07 passes (all API failures = v0.1.x only)
- [ ] T080.08 passes (partial data handled)
- [ ] T080.09 passes (score clamped to 1.0)
- [ ] T080.10 passes (parallel execution <300ms bench)
- [ ] T080.11 passes (consistent signal ordering)
- [ ] Updated scoring formula in scorer.py

### Estimated Effort
- Optimistic: 4 hours
- Likely: 8 hours
- Pessimistic: 16 hours
- **Planned**: 8 hours

### Dependencies
- W6.3, W6.4, W7.1, W7.2 (all signals)

### Post-Conditions
- Tests T080.01-T080.11 pass
- src/phantom_guard/core/signals/combination.py exists
- src/phantom_guard/core/scorer.py updated
```

### Exit Criteria (Week 7)
- [ ] All W7.* tasks complete
- [ ] T070.*, T075.*, T080.* tests passing
- [ ] All 4 new signals working in isolation
- [ ] Signal combination working with updated formula
- [ ] All signals parallel execution <300ms
- [ ] Coverage ≥90% on signal modules
- [ ] Hostile review on signals: GO

---

## Phase 8: GitHub Action (Week 8)

### Goals
- Build complete GitHub Action for marketplace
- PR comment integration with sticky updates
- SARIF output for GitHub Code Scanning
- Exit codes matching CLI

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W8.1 | S100, S106 | Action entry point + exit codes | 6 | PENDING |
| W8.2 | S101 | File discovery (glob patterns) | 4 | PENDING |
| W8.3 | S102 | Package extraction (all formats) | 6 | PENDING |
| W8.4 | S103 | Validation orchestrator | 6 | PENDING |
| W8.5 | S104 | PR comment generator (sticky) | 6 | PENDING |
| W8.6 | S105 | SARIF output generator | 4 | PENDING |
| W8.7 | - | Action integration tests | 6 | PENDING |
| **Buffer** | - | Contingency (20%) | 10 | - |
| **Total** | - | Week 8 | **48** | - |

### W8.1: Action Entry Point + Exit Codes

```markdown
## TASK: W8.1 — Action Entry Point + Exit Codes

### Traces
- SPEC: S100, S106
- INVARIANTS: INV100, INV101, INV108
- TESTS: T100.01-T100.03, T106.01-T106.04

### Definition
Implement GitHub Action entry point with action.yml and exit code handling.

### action.yml Configuration
```yaml
name: 'Phantom Guard'
description: 'Detect AI-hallucinated package attacks'
inputs:
  files:
    description: 'File patterns to validate'
    required: false
    default: 'requirements.txt,package.json,Cargo.toml'
  fail-on:
    description: 'When to fail: high-risk, suspicious, or none'
    required: false
    default: 'high-risk'
  output:
    description: 'Output format: github-comment, sarif, json, none'
    required: false
    default: 'github-comment'
outputs:
  safe-count:
    description: 'Number of safe packages'
  suspicious-count:
    description: 'Number of suspicious packages'
  high-risk-count:
    description: 'Number of high-risk packages'
runs:
  using: 'node20'
  main: 'dist/index.js'
```

### Acceptance Criteria
- [ ] T100.01 passes (action completes without throwing)
- [ ] T100.02 passes (full workflow runs)
- [ ] T100.03 passes (cold start <5s)
- [ ] T106.01 passes (exit 0 for all safe)
- [ ] T106.02 passes (exit 1 for suspicious)
- [ ] T106.03 passes (exit 2 for high-risk)
- [ ] T106.04 passes (exit code in [0-5] proptest)
- [ ] INV100 enforced (always produces valid output)
- [ ] INV101 enforced (exit code matches status)
- [ ] INV108 enforced (exit codes in range)

### Estimated Effort
- Optimistic: 3 hours
- Likely: 6 hours
- Pessimistic: 12 hours
- **Planned**: 6 hours

### Post-Conditions
- action/action.yml exists
- action/src/index.ts exists
- action/src/exit.ts exists
```

### W8.2-W8.6: Remaining Action Modules

| Task | Module | Key Tests | Invariants |
|:-----|:-------|:----------|:-----------|
| W8.2 | action/files.ts | T101.01-T101.05 | INV102 |
| W8.3 | action/extract.ts | T102.01-T102.05 | INV103 |
| W8.4 | action/validate.ts | T103.01-T103.03 | INV104 |
| W8.5 | action/comment.ts | T104.01-T104.05 | INV105, INV106 |
| W8.6 | action/sarif.ts | T105.01-T105.03 | INV107 |

### Exit Criteria (Week 8)
- [ ] All W8.* tasks complete
- [ ] T100-T106 tests passing (116 tests total)
- [ ] Action builds successfully (npm run build)
- [ ] Action works in test repository
- [ ] Cold start <5s, 50 packages <30s
- [ ] SARIF output validates against schema
- [ ] Hostile review on action: GO

---

## Phase 9: VS Code Extension (Week 9)

### Goals
- Build complete VS Code extension
- Real-time validation with diagnostics
- Hover tooltips and code actions
- Secure subprocess integration

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W9.1 | S120 | Extension activation | 6 | PENDING |
| W9.2 | S121 | Diagnostic provider | 6 | PENDING |
| W9.3 | S122 | Hover provider | 4 | PENDING |
| W9.4 | S123 | Code action provider | 4 | PENDING |
| W9.5 | S124, S125 | Status bar + configuration | 4 | PENDING |
| W9.6 | S126 | Core integration (subprocess) | 6 | PENDING |
| W9.7 | - | Extension integration tests | 8 | PENDING |
| **Buffer** | - | Contingency (20%) | 10 | - |
| **Total** | - | Week 9 | **48** | - |

### W9.6: Core Integration (Security Critical)

```markdown
## TASK: W9.6 — Core Integration

### Traces
- SPEC: S126
- INVARIANTS: INV127, INV128
- TESTS: T126.01-T126.04

### Definition
Implement secure subprocess integration with phantom-guard CLI.

### SECURITY REQUIREMENTS (P0-SEC-001)
- NEVER use shell string interpolation for commands
- ALWAYS use execFile() with array arguments (no shell)
- Validate package names before subprocess: /^[@a-z0-9][a-z0-9._-]*$/i
- Reject packages with shell metacharacters: ; | & $ ` \ " '
- Use child_process.spawn with shell: false (default)

### Acceptance Criteria
- [ ] T126.01 passes (spawn error handled gracefully)
- [ ] T126.02 passes (shell injection prevented - SECURITY)
- [ ] T126.03 passes (package name validated - SECURITY)
- [ ] T126.04 passes (first call <500ms bench)
- [ ] INV127 enforced (graceful spawn error handling)
- [ ] INV128 enforced (no shell injection)
- [ ] Uses execFile, not exec
- [ ] Package name regex validation

### Estimated Effort
- Optimistic: 3 hours
- Likely: 6 hours
- Pessimistic: 12 hours
- **Planned**: 6 hours

### Post-Conditions
- vscode/src/core.ts exists
- Security tests pass
```

### Exit Criteria (Week 9)
- [ ] All W9.* tasks complete
- [ ] T120-T126 tests passing (89 tests total)
- [ ] Extension builds successfully
- [ ] Extension activates <500ms
- [ ] Validation <200ms for cached packages
- [ ] Security tests pass (shell injection prevented)
- [ ] Hostile review on extension: GO

---

## Phase 10: Polish & Release (Week 10)

### Goals
- Full integration testing across all components
- Final hostile review
- Documentation updates
- Release preparation

### Tasks

| Task | SPEC | Description | Hours | Status |
|:-----|:-----|:------------|:------|:-------|
| W10.1 | - | Full system integration tests | 8 | PENDING |
| W10.2 | - | Performance regression tests | 4 | PENDING |
| W10.3 | - | Documentation updates (README, CHANGELOG) | 6 | PENDING |
| W10.4 | - | Final hostile review | 6 | PENDING |
| W10.5 | - | Release: PyPI (0.2.0), GitHub Action, VS Code Marketplace | 8 | PENDING |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 10 | **40** | - |

### Release Checklist

| Component | Target | Verification |
|:----------|:-------|:-------------|
| phantom-guard PyPI | v0.2.0 | pip install phantom-guard==0.2.0 |
| phantom-guard-action | v1.0.0 | GitHub Marketplace listing |
| phantom-guard-vscode | v0.1.0 | VS Code Marketplace listing |

### Exit Criteria (Week 10)
- [ ] All W10.* tasks complete
- [ ] All 473 tests passing (204 v0.1.x + 269 v0.2.0)
- [ ] Coverage ≥85% across all modules
- [ ] Performance budgets met
- [ ] False positive rate <0.5% (tested against top 1000 packages)
- [ ] Hostile review: GO
- [ ] All three components published

---

## Task Registry (v0.2.0 Trace Matrix)

| Task ID | SPEC_IDs | INV_IDs | TEST_IDs | Hours |
|:--------|:---------|:--------|:---------|:------|
| W6.1 | S058 | INV058, INV058a | T058.01-T058.05 | 6 |
| W6.2 | S059 | INV059, INV059a | T059.01-T059.06 | 4 |
| W6.3 | S060 | INV060, INV061, INV062 | T060.01-T060.06 | 8 |
| W6.4 | S065 | INV065, INV066, INV067 | T065.01-T065.06 | 8 |
| W6.5 | S058-S065 | - | Integration tests | 6 |
| W7.1 | S070 | INV070, INV071, INV072 | T070.01-T070.05 | 6 |
| W7.2 | S075 | INV075, INV076, INV077 | T075.01-T075.07 | 8 |
| W7.3 | S080 | INV060-INV077 | T080.01-T080.11 | 8 |
| W7.4 | S060-S080 | - | Full signal integration | 6 |
| W7.5 | S060-S080 | - | Performance benchmarks | 4 |
| W8.1 | S100, S106 | INV100, INV101, INV108 | T100.*, T106.* | 6 |
| W8.2 | S101 | INV102 | T101.01-T101.05 | 4 |
| W8.3 | S102 | INV103 | T102.01-T102.05 | 6 |
| W8.4 | S103 | INV104 | T103.01-T103.03 | 6 |
| W8.5 | S104 | INV105, INV106 | T104.01-T104.05 | 6 |
| W8.6 | S105 | INV107 | T105.01-T105.03 | 4 |
| W8.7 | S100-S106 | - | Action integration | 6 |
| W9.1 | S120 | INV120, INV121 | T120.01-T120.04 | 6 |
| W9.2 | S121 | INV122 | T121.01-T121.05 | 6 |
| W9.3 | S122 | INV123 | T122.01-T122.03 | 4 |
| W9.4 | S123 | INV124 | T123.01-T123.02 | 4 |
| W9.5 | S124, S125 | INV125, INV126 | T124.*, T125.* | 4 |
| W9.6 | S126 | INV127, INV128 | T126.01-T126.04 | 6 |
| W9.7 | S120-S126 | - | Extension integration | 8 |
| W10.1 | All | All | System integration | 8 |
| W10.2 | All | - | Performance regression | 4 |
| W10.3 | - | - | Documentation | 6 |
| W10.4 | All | All | Hostile review | 6 |
| W10.5 | - | - | Release | 8 |

**Total Tasks**: 28
**Total Hours (with buffer)**: 232

---

## Dependency Graph

```
                          W6.1 (Pattern Manager)
                                 │
                                 ▼
                          W6.2 (Pattern Validation)
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       │
    W6.3 (Namespace)       W6.4 (Downloads)              │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                          W6.5 (Signal Integration)
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       │
    W7.1 (Ownership)       W7.2 (Version Spike)          │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                          W7.3 (Signal Combination)
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
              W7.4 (Int)   W7.5 (Bench)   ─────┘
                    │            │
                    └────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                                   │
         ▼                                   ▼
    GitHub Action                    VS Code Extension
    ┌─────────────────┐              ┌─────────────────┐
    │ W8.1 (Entry)    │              │ W9.1 (Activate) │
    │       ▼         │              │       ▼         │
    │ W8.2 (Files)    │              │ W9.2 (Diag)     │
    │       ▼         │              │       ▼         │
    │ W8.3 (Extract)  │              │ W9.3 (Hover)    │
    │       ▼         │              │       ▼         │
    │ W8.4 (Validate) │              │ W9.4 (Actions)  │
    │       ▼         │              │       ▼         │
    │ W8.5 (Comment)  │              │ W9.5 (Status)   │
    │       ▼         │              │       ▼         │
    │ W8.6 (SARIF)    │              │ W9.6 (Core)     │
    │       ▼         │              │       ▼         │
    │ W8.7 (Int)      │              │ W9.7 (Int)      │
    └─────────────────┘              └─────────────────┘
                    │                        │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    W10.1 (System Integration)
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            W10.2 (Perf)  W10.3 (Docs)  W10.4 (Review)
                    │            │            │
                    └────────────┼────────────┘
                                 │
                                 ▼
                          W10.5 (Release)
```

### Critical Path
```
W6.1 → W6.2 → W6.3 → W7.3 → W8.1 → W8.4 → W8.7 → W10.1 → W10.4 → W10.5
```

**Total Critical Path**: ~70 hours (without buffer)

---

## Risk Assessment

| Task | Risk | Factor | Mitigation |
|:-----|:-----|:-------|:-----------|
| W6.3 | HIGH | npm org API rate limiting | Cache org lookups, graceful fallback |
| W6.4 | HIGH | libraries.io availability | Make optional, use native APIs where possible |
| W7.3 | MEDIUM | Scoring formula precision | Property tests for boundary conditions |
| W8.4 | HIGH | Subprocess timeout in CI | 60s circuit breaker, AbortController |
| W8.5 | MEDIUM | GitHub API rate limiting | Exponential backoff, token auth |
| W9.6 | HIGH (Security) | Shell injection | execFile only, strict regex validation |
| W10.1 | MEDIUM | Integration complexity | Incremental testing, mock fallbacks |

### Contingency Plans

**If npm Org API Rate Limited:**
1. Cache all org lookups with 24h TTL
2. Maintain static list of verified orgs
3. Skip signal on API failure (INV062)

**If libraries.io Unavailable:**
1. Use native crates.io reverse_dependencies
2. Use npm search API for dependents
3. Skip download inflation for PyPI

**If Extension Performance Budget Exceeded:**
1. Batch package validation
2. Increase debounce timeout
3. Cache results in globalState

**If False Positive Rate Exceeds 0.5%:**
1. Reduce signal weights
2. Expand verified namespace list
3. Add user allowlist configuration

---

## Performance Budgets (v0.2.0)

### New Detection Signals

| Operation | Budget | Constraint |
|:----------|:-------|:-----------|
| Namespace squatting | <100ms | P99 |
| Download inflation | <200ms | P99 |
| Ownership transfer | <50ms | P99 |
| Version spike | <10ms | P99 |
| All 4 signals (parallel) | <300ms | P99 |

### GitHub Action

| Operation | Budget | Constraint |
|:----------|:-------|:-----------|
| Cold start | <5s | P99 |
| File discovery | <1s | P99 |
| 50 packages | <30s | Total |
| SARIF generation | <100ms | P99 |

### VS Code Extension

| Operation | Budget | Constraint |
|:----------|:-------|:-----------|
| Activation | <500ms | P99 |
| Document validation | <200ms | Per file (cached) |
| First validation | <500ms | Per file (uncached) |
| Hover tooltip | <50ms | P99 |

---

## Progress Tracking

### Week 6
- [ ] W6.1 Complete (Pattern Manager)
- [ ] W6.2 Complete (Pattern Validation)
- [ ] W6.3 Complete (Namespace Signal)
- [ ] W6.4 Complete (Download Signal)
- [ ] W6.5 Complete (Signal Integration)
- [ ] Week 6 hostile review

### Week 7
- [ ] W7.1 Complete (Ownership Signal)
- [ ] W7.2 Complete (Version Signal)
- [ ] W7.3 Complete (Signal Combination)
- [ ] W7.4 Complete (Full Integration)
- [ ] W7.5 Complete (Performance Bench)
- [ ] Week 7 hostile review

### Week 8
- [ ] W8.1 Complete (Action Entry)
- [ ] W8.2 Complete (File Discovery)
- [ ] W8.3 Complete (Package Extraction)
- [ ] W8.4 Complete (Validation)
- [ ] W8.5 Complete (PR Comment)
- [ ] W8.6 Complete (SARIF)
- [ ] W8.7 Complete (Integration)
- [ ] Week 8 hostile review

### Week 9
- [ ] W9.1 Complete (Extension Activation)
- [ ] W9.2 Complete (Diagnostics)
- [ ] W9.3 Complete (Hover)
- [ ] W9.4 Complete (Actions)
- [ ] W9.5 Complete (Status/Config)
- [ ] W9.6 Complete (Core Integration)
- [ ] W9.7 Complete (Integration)
- [ ] Week 9 hostile review

### Week 10
- [ ] W10.1 Complete (System Integration)
- [ ] W10.2 Complete (Performance)
- [ ] W10.3 Complete (Documentation)
- [ ] W10.4 Complete (Final Hostile Review)
- [ ] W10.5 Complete (Release)
- [ ] v0.2.0 Released

---

## Quick Start

```bash
# Begin TDD implementation with first task
/implement W6.1

# For each task:
# 1. Remove @pytest.mark.skip from relevant tests
# 2. Run tests → MUST FAIL (Red)
# 3. Write minimal code to pass
# 4. Run tests → MUST PASS (Green)
# 5. Commit with IMPLEMENTS: SPEC_ID
```

---

**Gate 4 Status**: PENDING HOSTILE REVIEW

**Next Step**: Run `/hostile-review planning` for approval

**Document Version**: 1.0.0
