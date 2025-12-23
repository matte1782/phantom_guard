# Phantom Guard Development Roadmap

> **Target**: MVP Release v0.1.0
> **Deadline**: 90 days from start (adjust date when development begins)
> **Philosophy**: Ship fast, iterate based on feedback

---

## Overview

```
Week 1-2:   Foundation + Core Detection
Week 3-4:   CLI + Basic Integration
Week 5-6:   Caching + Performance
Week 7-8:   GitHub Action + Hooks
Week 9-10:  Testing + Hardening
Week 11-12: Release Prep + Launch
```

---

## Phase 0: Project Setup (Days 1-3)

### Objective
Project infrastructure ready for development.

### Deliverables

- [x] **P0.1**: Repository initialized
  - Git repo with proper .gitignore
  - README.md with project description
  - LICENSE (MIT)
  - pyproject.toml with dependencies
  - Pre-commit hooks configured

- [x] **P0.2**: Development environment
  - Python 3.11+ required
  - uv/pip for dependency management
  - pytest configured
  - mypy configured
  - ruff configured

- [ ] **P0.3**: CI/CD foundation
  - GitHub Actions workflow (tests, types, lint)
  - Branch protection on main
  - Dependabot configured

### Exit Criteria
- [x] `pytest` runs (even with no tests)
- [x] `mypy src/` passes
- [x] `ruff check src/` passes
- [ ] GitHub Actions green

---

## Phase 1: Core Detection Engine (Days 4-21)

### Objective
Can detect if a package exists and score its risk.

### Deliverables

- [ ] **P1.1**: Package metadata fetching
  - PyPI client (`src/phantom_guard/registry/pypi.py`)
  - npm client (`src/phantom_guard/registry/npm.py`)
  - crates.io client (`src/phantom_guard/registry/crates.py`)
  - Common interface (`src/phantom_guard/registry/base.py`)
  - Tests for each client

- [ ] **P1.2**: Risk scoring engine
  - Signal detection (`src/phantom_guard/core/signals.py`)
  - Score calculation (`src/phantom_guard/core/scorer.py`)
  - Risk thresholds configuration
  - Tests with known good/bad packages

- [ ] **P1.3**: Hallucination pattern matching
  - Pattern database (initial 50 patterns)
  - Pattern matching engine
  - Pattern file format (.yaml)
  - Tests for pattern matching

- [ ] **P1.4**: Data models
  - PackageMetadata
  - RiskSignal
  - PackageRisk
  - ValidationResult
  - Pydantic models with validation

### Exit Criteria
- [ ] Can fetch metadata from PyPI, npm, crates.io
- [ ] Can score "flask" as SAFE (score > 0.8)
- [ ] Can score non-existent package as BLOCKED
- [ ] Pattern matching identifies "flask-gpt-helper" as suspicious
- [ ] All tests pass
- [ ] **HOSTILE REVIEW PASSED**

---

## Phase 2: CLI Tool (Days 22-35)

### Objective
Users can run `phantom-guard check requirements.txt` from command line.

### Deliverables

- [ ] **P2.1**: CLI framework
  - Typer-based CLI (`src/phantom_guard/cli/main.py`)
  - `phantom-guard check <file>` command
  - `phantom-guard check-package <name>` command
  - Pretty terminal output (colors, tables)
  - JSON output option

- [ ] **P2.2**: File parsing
  - requirements.txt parser
  - package.json parser
  - pyproject.toml parser (dependencies)
  - Cargo.toml parser

- [ ] **P2.3**: Configuration
  - Config file support (~/.phantom-guard.yaml)
  - CLI flags for overrides
  - Threshold configuration
  - Registry selection

### Exit Criteria
- [ ] `phantom-guard check requirements.txt` works
- [ ] `phantom-guard check package.json` works
- [ ] Output is clear and actionable
- [ ] `--json` flag produces valid JSON
- [ ] Configuration file is respected
- [ ] **HOSTILE REVIEW PASSED**

---

## Phase 3: Caching & Performance (Days 36-49)

### Objective
Fast enough for real-time use (50 packages < 5s).

### Deliverables

- [ ] **P3.1**: In-memory cache
  - TTL-based caching
  - LRU eviction
  - Cache statistics

- [ ] **P3.2**: Persistent cache
  - SQLite storage
  - Cache warming option
  - Cache invalidation

- [ ] **P3.3**: Concurrent fetching
  - Async/await for API calls
  - Configurable concurrency limit
  - Timeout handling

- [ ] **P3.4**: Performance optimization
  - Batch API calls where possible
  - Connection pooling
  - Benchmark suite

### Exit Criteria
- [ ] Single package (cached): <10ms
- [ ] Single package (uncached): <200ms
- [ ] 50 packages concurrent: <5s
- [ ] Graceful degradation when offline
- [ ] **HOSTILE REVIEW PASSED**

---

## Phase 4: GitHub Action (Days 50-63)

### Objective
`uses: phantom-guard/action@v1` works in any workflow.

### Deliverables

- [ ] **P4.1**: GitHub Action
  - action.yml definition
  - Docker-based action
  - Input parameters (file, threshold, fail-on)
  - Output (results, summary)

- [ ] **P4.2**: PR Integration
  - Comment on PR with results
  - Status check (pass/fail)
  - Annotations on changed files

- [ ] **P4.3**: Documentation
  - Action README
  - Usage examples
  - Troubleshooting guide

### Exit Criteria
- [ ] Action runs in test repo
- [ ] Fails PR when suspicious package added
- [ ] Passes PR when packages are safe
- [ ] Clear documentation
- [ ] **HOSTILE REVIEW PASSED**

---

## Phase 5: Package Hooks (Days 64-77)

### Objective
Intercept `pip install` and `npm install` with warnings.

### Deliverables

- [ ] **P5.1**: pip hook
  - pip pre-install hook mechanism
  - Warning prompt for suspicious packages
  - Skip flag (--no-phantom-guard)
  - Works with pip, pip-tools, poetry

- [ ] **P5.2**: npm hook (optional for MVP)
  - npm preinstall script
  - Warning mechanism
  - Skip configuration

- [ ] **P5.3**: Pre-commit hook
  - pre-commit hook definition
  - .pre-commit-hooks.yaml
  - Documentation

### Exit Criteria
- [ ] `pip install flask-suspicious` shows warning
- [ ] User can bypass with confirmation
- [ ] Pre-commit hook catches bad packages in requirements.txt
- [ ] **HOSTILE REVIEW PASSED**

---

## Phase 6: Testing & Hardening (Days 78-84)

### Objective
Production-ready quality.

### Deliverables

- [ ] **P6.1**: Test coverage
  - >80% code coverage
  - Edge case tests
  - Error handling tests
  - Integration tests

- [ ] **P6.2**: Security hardening
  - Input validation audit
  - No shell injection possible
  - No path traversal possible
  - Error messages don't leak info

- [ ] **P6.3**: Real-world validation
  - Test on 10+ open source projects
  - False positive rate < 5%
  - Performance on large projects

- [ ] **P6.4**: Documentation
  - README complete
  - API documentation
  - Contributing guide
  - Security policy

### Exit Criteria
- [ ] Coverage >80%
- [ ] Security audit passed
- [ ] False positive rate <5% on real projects
- [ ] **FULL HOSTILE REVIEW PASSED**

---

## Phase 7: Release v0.1.0 (Days 85-90)

### Objective
Public release on PyPI and GitHub.

### Deliverables

- [ ] **P7.1**: Release preparation
  - Version bump to 0.1.0
  - CHANGELOG.md complete
  - All docs updated
  - License headers

- [ ] **P7.2**: PyPI release
  - Package built
  - Uploaded to PyPI
  - Installation tested

- [ ] **P7.3**: GitHub release
  - Release notes written
  - Tag created
  - Assets attached

- [ ] **P7.4**: Launch
  - Hacker News post prepared
  - Reddit post prepared
  - Twitter thread prepared

### Exit Criteria
- [ ] `pip install phantom-guard` works
- [ ] GitHub Action available
- [ ] Launch posts ready
- [ ] **FINAL HOSTILE REVIEW PASSED**

---

## Post-MVP Backlog

### v0.2.0 - Enhanced Detection
- [ ] More hallucination patterns (500+)
- [ ] Typosquatting detection
- [ ] Dependency confusion detection
- [ ] Community pattern contributions

### v0.3.0 - Enterprise Features
- [ ] Team dashboard (web UI)
- [ ] Policy configuration
- [ ] Audit logging
- [ ] SSO integration

### v0.4.0 - Intelligence
- [ ] Telemetry (opt-in)
- [ ] New pattern discovery
- [ ] Threat feed integration
- [ ] API for third-party tools

---

## Progress Tracking

### Current Status

| Phase | Status | Progress | Blockers |
|-------|--------|----------|----------|
| P0: Setup | COMPLETE | 100% | - |
| P1: Core | IN_PROGRESS | 60% | Tests needed |
| P2: CLI | NOT_STARTED | 0% | - |
| P3: Cache | NOT_STARTED | 0% | - |
| P4: Action | NOT_STARTED | 0% | - |
| P5: Hooks | NOT_STARTED | 0% | - |
| P6: Harden | NOT_STARTED | 0% | - |
| P7: Release | NOT_STARTED | 0% | - |

### Milestone Dates

| Milestone | Target Date | Actual Date | Notes |
|-----------|-------------|-------------|-------|
| P0 Complete | Day 3 | Day 1 | Git, pre-commit, initial scaffold |
| P1 Complete | Day 21 | - | Core engine 60% done |
| P2 Complete | Day 35 | - | - |
| P3 Complete | Day 49 | - | - |
| P4 Complete | Day 63 | - | - |
| P5 Complete | Day 77 | - | - |
| P6 Complete | Day 84 | - | - |
| v0.1.0 Release | Day 90 | - | - |

---

## Risk Mitigation

### If Behind Schedule

| Days Behind | Action |
|-------------|--------|
| 1-7 days | Work longer hours, no scope cut |
| 8-14 days | Cut P5 (hooks) to post-MVP |
| 15-21 days | Cut P4 (GitHub Action) to v0.1.1 |
| 22+ days | Reassess MVP scope entirely |

### If Competition Emerges

| Threat Level | Action |
|--------------|--------|
| OSS tool gains traction | Accelerate, focus on differentiation |
| Big Tech announces feature | Evaluate pivot or niche down |
| VC-funded startup | Race to market or find acquisition path |

---

## Success Criteria for v0.1.0

### Must Have
- [ ] CLI works (`phantom-guard check requirements.txt`)
- [ ] PyPI/npm detection works
- [ ] False positive rate <5%
- [ ] Documentation complete
- [ ] Available on PyPI

### Should Have
- [ ] GitHub Action works
- [ ] Pre-commit hook works
- [ ] Caching for performance

### Nice to Have
- [ ] pip install hook
- [ ] npm install hook
- [ ] crates.io support
