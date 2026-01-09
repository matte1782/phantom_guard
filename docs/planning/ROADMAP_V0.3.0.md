# Phantom Guard v0.3.0 Roadmap

> **Version**: 0.3.0
> **Created**: 2026-01-09
> **Last Updated**: 2026-01-09
> **Status**: PLANNING
> **Gate**: 4 of 6 - Planning
> **Base**: Extends v0.2.0 (PyPI, VS Code Marketplace, GitHub Action released)

---

## Overview

### v0.3.0 Theme: Invisible Protection

Building on v0.2.0's detection engine and integrations, v0.3.0 focuses on **shifting security left to installation time** - intercepting dangerous packages before they're installed, not after.

**Philosophy**: The most effective security tools are those developers never have to think about. v0.3.0 makes Phantom Guard invisible by integrating directly into `pip` and `npm` workflows.

### Research-Backed Priorities

This roadmap is informed by comprehensive user research (January 2026):

| Research Source | Key Finding | v0.3.0 Response |
|-----------------|-------------|-----------------|
| HN User Feedback | False positive concerns | Publish FP benchmark, feedback system |
| Competitor Analysis | 0.08% FP rate is 30x better than alternatives | Lead marketing message |
| Workflow Research | 86% of devs skip manual security steps | Automatic pip/npm wrappers |
| Enterprise Research | SSO/Audit logs are non-negotiable | Defer to v0.4.0, focus on adoption first |

### Success Criteria

| Criterion | v0.2.0 Baseline | v0.3.0 Target |
|-----------|-----------------|---------------|
| GitHub stars | 3 | 500 |
| PyPI weekly downloads | ~100 | 2,000 |
| pip wrapper installs | 0 | 500 |
| npm wrapper installs | 0 | 200 |
| Pre-commit hook repos | 0 | 100 |
| False positive rate | 0.08% | <0.1% |

### Total Effort

| Phase | Weeks | Hours (with 20% buffer) |
|-------|-------|-------------------------|
| pip Install Wrapper | 11 | 72 |
| npm Install Wrapper | 12 | 48 |
| Pre-commit Hook | 13 | 24 |
| MCP Server | 14 | 48 |
| Telemetry & Polish | 15 | 40 |
| **Total** | **5 weeks** | **232 hours** |

---

## Phase 11: pip Install Wrapper (Week 11)

### Goals

- Create `phantom-pip` command that wraps pip with security validation
- Intercept package installation at the moment of danger
- Zero workflow change required (alias pip to phantom-pip)
- Interactive confirmation for HIGH_RISK packages

### User Story

```bash
# Before v0.3.0 (dangerous)
$ pip install flask-gpt-helper
# Malware installed silently

# After v0.3.0 (protected)
$ pip install flask-gpt-helper
# OR: phantom-pip install flask-gpt-helper

Phantom Guard v0.3.0

Validating packages...

  Package: flask-gpt-helper
  Registry: pypi
  Status: HIGH RISK

  Signals:
    - Package not found on PyPI (weight: 0.90)
    - Matches hallucination pattern (weight: 0.85)

  Risk Score: 0.92
  Recommendation: DO NOT INSTALL

Proceed anyway? [y/N] n
Installation cancelled.
```

### Tasks

| Task | SPEC | Description | Hours | Status |
|------|------|-------------|-------|--------|
| W11.1 | S200 | Package structure (phantom-guard-pip) | 4 | PENDING |
| W11.2 | S201 | pip argument parser | 8 | PENDING |
| W11.3 | S202 | Package extraction from pip args | 8 | PENDING |
| W11.4 | S203 | Interactive confirmation flow | 6 | PENDING |
| W11.5 | S204 | Configuration system (~/.phantom-guard/pip.yaml) | 6 | PENDING |
| W11.6 | S205 | Allowlist/blocklist support | 4 | PENDING |
| W11.7 | S206 | pip subprocess delegation | 6 | PENDING |
| W11.8 | - | Unit tests (90% coverage target) | 8 | PENDING |
| W11.9 | - | Integration tests (mock pip) | 6 | PENDING |
| W11.10 | - | Documentation | 4 | PENDING |
| **Buffer** | - | Contingency (20%) | 12 | - |
| **Total** | - | Week 11 | **72** | - |

### W11.1: Package Structure

```
phantom-guard-pip/
├── pyproject.toml
├── README.md
├── src/
│   └── phantom_pip/
│       ├── __init__.py
│       ├── __main__.py      # Entry point
│       ├── cli.py           # phantom-pip command
│       ├── parser.py        # pip argument parsing
│       ├── extract.py       # Package name extraction
│       ├── confirm.py       # Interactive confirmation
│       ├── config.py        # Configuration loading
│       ├── delegate.py      # pip subprocess delegation
│       └── lists.py         # Allowlist/blocklist
└── tests/
    ├── test_parser.py
    ├── test_extract.py
    ├── test_confirm.py
    └── test_integration.py
```

### W11.3: Package Extraction Logic

Must handle all pip install variants:

```bash
# Simple
pip install flask

# Multiple packages
pip install flask requests django

# Version specifiers
pip install flask>=2.0 requests==2.28.0

# Requirements file
pip install -r requirements.txt

# Editable installs (skip validation)
pip install -e .

# URL installs
pip install git+https://github.com/user/repo.git

# Extras
pip install flask[async]
```

### W11.4: Interactive Confirmation

```python
# IMPLEMENTS: S203
# INVARIANTS: INV200, INV201

def confirm_installation(
    package: str,
    risk: PackageRisk,
    config: Config
) -> bool:
    """
    Show interactive confirmation for risky packages.

    INV200: Always returns bool (never raises for user input)
    INV201: Respects --yes flag for CI environments
    """
    if config.auto_approve:
        return True

    if risk.recommendation == Recommendation.SAFE:
        return True

    # Show risk details
    display_risk_assessment(risk)

    # Prompt user
    response = input("Proceed anyway? [y/N] ")
    return response.lower() in ("y", "yes")
```

### W11.5: Configuration System

```yaml
# ~/.phantom-guard/pip.yaml
enabled: true
mode: interactive  # interactive | warn | block | silent

# Auto-approve for CI environments
auto_approve: false

# Packages to always allow
allowlist:
  - my-internal-package
  - company-utils

# Packages to always block
blocklist:
  - known-malware-package

# Risk threshold (0.0 - 1.0)
threshold: 0.6

# Timeout for validation (seconds)
timeout: 30
```

### Exit Criteria (Week 11)

- [ ] All W11.* tasks complete
- [ ] `phantom-pip install flask` works end-to-end
- [ ] `phantom-pip install flask-gpt-helper` shows warning and prompts
- [ ] Configuration file is respected
- [ ] Allowlist/blocklist works
- [ ] Unit tests: 90% coverage
- [ ] Integration tests pass
- [ ] Documentation complete

---

## Phase 12: npm Install Wrapper (Week 12)

### Goals

- Create `@phantom-guard/npm` package
- Same protection for JavaScript ecosystem
- Support npm, yarn, pnpm workflows
- Integration via preinstall hook or wrapper script

### Tasks

| Task | SPEC | Description | Hours | Status |
|------|------|-------------|-------|--------|
| W12.1 | S210 | Package structure (@phantom-guard/npm) | 4 | PENDING |
| W12.2 | S211 | npm argument parser | 6 | PENDING |
| W12.3 | S212 | Package extraction | 6 | PENDING |
| W12.4 | S213 | Interactive confirmation (Node.js) | 6 | PENDING |
| W12.5 | S214 | preinstall hook integration | 6 | PENDING |
| W12.6 | S215 | Configuration (package.json or .phantomguardrc) | 4 | PENDING |
| W12.7 | - | Unit tests | 6 | PENDING |
| W12.8 | - | Integration tests | 4 | PENDING |
| W12.9 | - | Documentation | 4 | PENDING |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 12 | **54** | - |

### W12.5: preinstall Hook Integration

```json
// package.json
{
  "scripts": {
    "preinstall": "phantom-guard-npm check"
  }
}
```

Or global configuration:

```bash
npm config set phantom-guard:enabled true
```

### Exit Criteria (Week 12)

- [ ] All W12.* tasks complete
- [ ] `phantom-npm install lodash` works
- [ ] preinstall hook integration works
- [ ] Configuration via package.json works
- [ ] Unit tests: 90% coverage
- [ ] Published to npm registry

---

## Phase 13: Pre-commit Hook (Week 13)

### Goals

- Official pre-commit framework integration
- Validate dependency files on commit
- Block commits with HIGH_RISK packages
- Easy one-line setup for any repository

### Tasks

| Task | SPEC | Description | Hours | Status |
|------|------|-------------|-------|--------|
| W13.1 | S220 | .pre-commit-hooks.yaml definition | 2 | PENDING |
| W13.2 | S221 | Hook entry point script | 4 | PENDING |
| W13.3 | S222 | Dependency file detection | 4 | PENDING |
| W13.4 | S223 | Exit code compliance (pre-commit spec) | 2 | PENDING |
| W13.5 | S224 | Configuration via args | 4 | PENDING |
| W13.6 | - | Integration tests with pre-commit | 4 | PENDING |
| W13.7 | - | Documentation and examples | 4 | PENDING |
| **Buffer** | - | Contingency (20%) | 4 | - |
| **Total** | - | Week 13 | **28** | - |

### W13.1: Hook Definition

```yaml
# .pre-commit-hooks.yaml (in phantom-guard repo root)
- id: phantom-guard
  name: Phantom Guard
  description: Detect AI-hallucinated package attacks
  entry: phantom-guard check
  language: python
  files: (requirements.*\.txt|package\.json|Cargo\.toml|pyproject\.toml|poetry\.lock|package-lock\.json)$
  pass_filenames: true
  types: [text]
  stages: [commit]
```

### User Setup

```yaml
# .pre-commit-config.yaml (user's repo)
repos:
  - repo: https://github.com/matte1782/phantom_guard
    rev: v0.3.0
    hooks:
      - id: phantom-guard
        args: [--fail-on, suspicious]
```

### Exit Criteria (Week 13)

- [ ] All W13.* tasks complete
- [ ] `pre-commit run phantom-guard` works
- [ ] Blocks commits with HIGH_RISK packages
- [ ] Configuration via args works
- [ ] Documentation complete

---

## Phase 14: MCP Server (Week 14)

### Goals

- Model Context Protocol server for AI coding tools
- Real-time validation in Claude Code, Cursor, Copilot
- Position as THE "vibe coding security" solution
- First-mover advantage (no competitor has this)

### Why MCP Server?

> "A promising direction is to embed application security tooling directly into AI code assistants, catching hallucinated packages before they ever reach your project." — Mend.io Research

```
AI Coding Tool → Suggests "pip install flask-gpt-helper"
       ↓
MCP Server → Validates package in real-time
       ↓
Tool → Shows inline warning: "Package doesn't exist on PyPI"
```

### Tasks

| Task | SPEC | Description | Hours | Status |
|------|------|-------------|-------|--------|
| W14.1 | S230 | MCP server scaffold | 4 | PENDING |
| W14.2 | S231 | validate_package tool | 8 | PENDING |
| W14.3 | S232 | check_file tool | 6 | PENDING |
| W14.4 | S233 | get_risk_report tool | 4 | PENDING |
| W14.5 | S234 | Configuration and authentication | 4 | PENDING |
| W14.6 | - | Testing with Claude Code | 6 | PENDING |
| W14.7 | - | Testing with Cursor | 4 | PENDING |
| W14.8 | - | Documentation | 4 | PENDING |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 14 | **48** | - |

### W14.2: MCP Tools Definition

```python
# phantom_guard_mcp/server.py
from mcp import Server, Tool

server = Server("phantom-guard")

@server.tool()
async def validate_package(
    name: str,
    registry: str = "pypi"
) -> dict:
    """
    Validate a single package for slopsquatting risk.

    Args:
        name: Package name to validate
        registry: Target registry (pypi, npm, crates)

    Returns:
        Risk assessment with score, signals, and recommendation
    """
    risk = await phantom_guard.validate_package(name, registry)
    return {
        "name": risk.name,
        "exists": risk.exists,
        "risk_score": risk.risk_score,
        "recommendation": risk.recommendation.value,
        "signals": [
            {"type": s.type.value, "message": s.message}
            for s in risk.signals
        ]
    }

@server.tool()
async def check_file(path: str) -> dict:
    """
    Check all packages in a dependency file.

    Args:
        path: Path to requirements.txt, package.json, etc.

    Returns:
        Aggregate results for all packages
    """
    ...
```

### Exit Criteria (Week 14)

- [ ] All W14.* tasks complete
- [ ] MCP server starts and responds to tool calls
- [ ] Works with Claude Code CLI
- [ ] Works with Cursor
- [ ] Published as `phantom-guard-mcp` package

---

## Phase 15: Telemetry & Polish (Week 15)

### Goals

- Opt-in telemetry for phantom package discovery
- False positive feedback system
- Performance optimization
- Documentation updates
- Final hostile review and release

### Tasks

| Task | SPEC | Description | Hours | Status |
|------|------|-------------|-------|--------|
| W15.1 | S240 | Telemetry opt-in consent flow | 4 | PENDING |
| W15.2 | S241 | Anonymous data model | 4 | PENDING |
| W15.3 | S242 | Telemetry backend (Cloudflare Workers) | 6 | PENDING |
| W15.4 | S243 | False positive feedback command | 4 | PENDING |
| W15.5 | - | Performance benchmarks | 4 | PENDING |
| W15.6 | - | Documentation updates | 6 | PENDING |
| W15.7 | - | Final hostile review | 4 | PENDING |
| W15.8 | - | Release preparation | 4 | PENDING |
| **Buffer** | - | Contingency (20%) | 8 | - |
| **Total** | - | Week 15 | **44** | - |

### W15.1: Telemetry Consent

```bash
$ phantom-guard config telemetry enable

Phantom Guard Telemetry

We'd like to collect anonymous usage data to improve
slopsquatting detection. This helps us:
  - Discover new phantom package patterns
  - Reduce false positives
  - Improve detection accuracy

What we collect:
  - Package names flagged as risky
  - Risk scores and signals triggered
  - Registry (pypi/npm/crates)

What we DON'T collect:
  - Your IP address
  - Personal information
  - Source code or file paths

You can disable this anytime with:
  phantom-guard config telemetry disable

Enable telemetry? [y/N] y
Telemetry enabled. Thank you for helping improve security!
```

### W15.4: False Positive Feedback

```bash
$ phantom-guard feedback flask-gpt-helper --not-malicious

Thank you! Your feedback helps improve detection accuracy.
Package: flask-gpt-helper
Reported as: False positive (not malicious)

This will be reviewed and may update our pattern database.
```

### Exit Criteria (Week 15)

- [ ] All W15.* tasks complete
- [ ] Telemetry system works (opt-in)
- [ ] False positive feedback works
- [ ] All performance budgets met
- [ ] Documentation updated
- [ ] Hostile review: GO
- [ ] v0.3.0 released to PyPI

---

## Specification Registry (v0.3.0)

| SPEC_ID | Description | Component |
|---------|-------------|-----------|
| S200 | pip wrapper package structure | pip Hook |
| S201 | pip argument parser | pip Hook |
| S202 | Package extraction from pip | pip Hook |
| S203 | Interactive confirmation | pip Hook |
| S204 | pip configuration system | pip Hook |
| S205 | Allowlist/blocklist | pip Hook |
| S206 | pip subprocess delegation | pip Hook |
| S210 | npm wrapper package structure | npm Hook |
| S211 | npm argument parser | npm Hook |
| S212 | npm package extraction | npm Hook |
| S213 | npm interactive confirmation | npm Hook |
| S214 | npm preinstall integration | npm Hook |
| S215 | npm configuration | npm Hook |
| S220 | Pre-commit hook definition | Pre-commit |
| S221 | Hook entry point | Pre-commit |
| S222 | Dependency file detection | Pre-commit |
| S223 | Exit code compliance | Pre-commit |
| S224 | Hook args configuration | Pre-commit |
| S230 | MCP server scaffold | MCP |
| S231 | validate_package MCP tool | MCP |
| S232 | check_file MCP tool | MCP |
| S233 | get_risk_report MCP tool | MCP |
| S234 | MCP authentication | MCP |
| S240 | Telemetry consent flow | Telemetry |
| S241 | Anonymous data model | Telemetry |
| S242 | Telemetry backend | Telemetry |
| S243 | False positive feedback | Telemetry |

---

## Invariant Registry (v0.3.0)

| INV_ID | Statement | Enforcement |
|--------|-----------|-------------|
| INV200 | pip wrapper never modifies pip arguments | Passthrough test |
| INV201 | Interactive prompt respects --yes flag | Flag handling test |
| INV202 | Allowlist packages always pass validation | Allowlist test |
| INV203 | Blocklist packages always fail validation | Blocklist test |
| INV210 | npm wrapper handles all install variants | Variant tests |
| INV211 | preinstall hook exits 0 on success | Exit code test |
| INV220 | Pre-commit hook produces valid exit codes | Exit code test |
| INV221 | Hook processes only dependency files | File filter test |
| INV230 | MCP server responds to all tool calls | Tool response test |
| INV231 | MCP tools return valid JSON schema | Schema validation |
| INV240 | Telemetry data never contains PII | Data schema test |
| INV241 | Telemetry is opt-in only | Default config test |

---

## Performance Budgets (v0.3.0)

### pip Wrapper

| Operation | Budget | Constraint |
|-----------|--------|------------|
| Wrapper startup | <100ms | P99 |
| Single package validation | <500ms | P99 |
| Batch validation (10 packages) | <3s | P99 |
| Interactive prompt display | <10ms | P99 |

### npm Wrapper

| Operation | Budget | Constraint |
|-----------|--------|------------|
| preinstall hook | <2s | P99 |
| Single package validation | <500ms | P99 |

### Pre-commit Hook

| Operation | Budget | Constraint |
|-----------|--------|------------|
| Hook cold start | <2s | P99 |
| Per-file validation | <500ms | P99 |
| Full repo scan (50 files) | <30s | P99 |

### MCP Server

| Operation | Budget | Constraint |
|-----------|--------|------------|
| Server startup | <1s | P99 |
| validate_package call | <500ms | P99 |
| check_file call | <5s | P99 (50 packages) |

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| pip has no official hook API | HIGH | MEDIUM | Wrapper script approach |
| npm package name conflicts | LOW | MEDIUM | Use scoped package |
| MCP spec changes | MEDIUM | MEDIUM | Pin to stable MCP version |
| Telemetry privacy concerns | MEDIUM | HIGH | Opt-in only, transparency |

### Market Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Socket.dev adds pip wrapper | MEDIUM | HIGH | Ship fast, focus on UX |
| pip adds native security | LOW | HIGH | Differentiate on slopsquatting |
| User resistance to wrappers | MEDIUM | MEDIUM | Make opt-in, provide value |

### Execution Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep to enterprise | MEDIUM | MEDIUM | Defer SSO/audit to v0.4.0 |
| MCP complexity | MEDIUM | MEDIUM | Start with simple tools |
| Cross-platform issues | MEDIUM | HIGH | CI matrix testing |

---

## Dependency Graph

```
                    W11: pip Wrapper
                           │
          +----------------+----------------+
          │                                 │
          v                                 v
    W12: npm Wrapper              W13: Pre-commit Hook
          │                                 │
          +----------------+----------------+
                           │
                           v
                    W14: MCP Server
                           │
                           v
                    W15: Telemetry & Polish
                           │
                           v
                       v0.3.0 Release
```

### Critical Path

```
W11.1 → W11.3 → W11.4 → W11.7 → W13.1 → W14.1 → W15.7 → Release
```

**Total Critical Path**: ~45 hours (without buffer)

---

## Competitive Differentiation (Post v0.3.0)

| Feature | Phantom Guard | SlopGuard | Socket | Snyk |
|---------|---------------|-----------|--------|------|
| pip install wrapper | **v0.3.0** | No | No | No |
| npm install wrapper | **v0.3.0** | No | Partial | No |
| Pre-commit hook | **v0.3.0** | No | No | No |
| MCP Server | **v0.3.0** | No | No | No |
| VS Code Extension | v0.2.0 | No | No | Yes |
| GitHub Action | v0.2.0 | No | No | Yes |
| False positive rate | 0.08% | 2.5% | Unknown | Unknown |
| Price | FREE | FREE | Paid | $35K+ |

**v0.3.0 Unique Value**: First tool with install-time protection AND AI coding tool integration.

---

## Progress Tracking

### Week 11 (pip Wrapper)
- [ ] W11.1 Complete (Package structure)
- [ ] W11.2 Complete (Argument parser)
- [ ] W11.3 Complete (Package extraction)
- [ ] W11.4 Complete (Interactive confirmation)
- [ ] W11.5 Complete (Configuration)
- [ ] W11.6 Complete (Allowlist/blocklist)
- [ ] W11.7 Complete (pip delegation)
- [ ] W11.8 Complete (Unit tests)
- [ ] W11.9 Complete (Integration tests)
- [ ] W11.10 Complete (Documentation)

### Week 12 (npm Wrapper)
- [ ] W12.1 - W12.9 Complete
- [ ] Published to npm

### Week 13 (Pre-commit Hook)
- [ ] W13.1 - W13.7 Complete
- [ ] Tested with pre-commit framework

### Week 14 (MCP Server)
- [ ] W14.1 - W14.8 Complete
- [ ] Works with Claude Code
- [ ] Works with Cursor

### Week 15 (Telemetry & Polish)
- [ ] W15.1 - W15.8 Complete
- [ ] Hostile review: GO
- [ ] v0.3.0 Released

---

## Quick Start (After Planning Approval)

```bash
# Begin TDD implementation with first task
/implement W11.1

# For each task:
# 1. Write test stubs first
# 2. Run tests → MUST FAIL (Red)
# 3. Write minimal code to pass
# 4. Run tests → MUST PASS (Green)
# 5. Commit with IMPLEMENTS: SPEC_ID
```

---

**Gate 4 Status**: PENDING HOSTILE REVIEW

**Next Step**: Run `/hostile-review planning` for approval

**Document Version**: 1.0.0
