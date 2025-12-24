# FORTRESS 2.0 Configuration

> **Project**: Phantom Guard - Slopsquatting Detection
> **Framework Version**: 2.0.0
> **Created**: 2025-12-23

---

## Quality Standards

| Standard | Target | Enforcement |
|:---------|:-------|:------------|
| Test Coverage | 90%+ | pytest --cov |
| Function Size | <50 lines | Custom lint |
| Type Hints | 100% public | mypy --strict |
| Unwrap/Panic | 0 in library | grep + fail |
| Review Latency | <24h | Process |
| Regression Tolerance | <5% | Benchmark diff |
| False Positive Rate | <5% | Real-world testing |

---

## Gate Status

| Gate | Status | Date | Approver |
|:-----|:-------|:-----|:---------|
| G0: Problem | **COMPLETE** | 2025-12-22 | Research Fortress v7 |
| G1: Architecture | **COMPLETE** | 2025-12-24 | HOSTILE_VALIDATOR |
| G2: Specification | **COMPLETE** | 2025-12-24 | HOSTILE_VALIDATOR |
| G3: Test Design | **COMPLETE** | 2025-12-24 | TEST_ARCHITECT |
| G4: Planning | **COMPLETE** | 2025-12-24 | PLANNER |
| G5: Validation | PENDING | | |
| G6: Release | BLOCKED | | |

---

## Trace System

Every artifact carries a TRACE ID linking to specification:

```
SPEC_ID: S001
  ├── TEST_ID: T001.1, T001.2
  ├── TASK_ID: W1.1.a
  ├── CODE_ID: src/phantom_guard/core/detector.py:validate_package (line 45-67)
  └── REVIEW_ID: R001-2025-01-15
```

### Enforcement Rules

- Every test file has `# SPEC: S001` header
- Every implementation function has `# IMPLEMENTS: S001` docstring
- Every task in plan has `TRACES: S001` link
- Build fails if orphan code exists (code without SPEC link)

---

## Agent Roster

| Agent | Role | Veto Power | Command |
|:------|:-----|:-----------|:--------|
| PROBLEM_ANALYST | Define problem, success criteria | NO | `/gate-0` |
| META_ARCHITECT | System design, invariants | NO | `/gate-1` |
| SPEC_ENGINEER | Invariant registry, edge cases | NO | `/gate-2` |
| TEST_ARCHITECT | Design tests BEFORE code | NO | `/gate-3` |
| PLANNER | Task breakdown with traces | NO | `/gate-4` |
| HOSTILE_VALIDATOR | Final validation | **YES** | `/gate-5` |
| RELEASE_GUARDIAN | Release readiness | **YES** | `/gate-6` |
| QUALITY_HOUND | Automated quality scan | NO | `/quality-scan` |
| REGRESSION_SENTINEL | Performance regression | NO | `/regression-check` |

---

## Project-Specific Standards

### Phantom Guard Detection Accuracy

| Metric | Target | Critical |
|:-------|:-------|:---------|
| True Positive Rate | >95% | YES |
| False Positive Rate | <5% | YES |
| Detection Latency | <200ms | NO |
| Batch (50 packages) | <5s | NO |

### Performance Budget

| Operation | Budget | Constraint |
|:----------|:-------|:-----------|
| Single package (cached) | <10ms | P99 |
| Single package (uncached) | <200ms | P99 |
| 50 packages (concurrent) | <5s | P99 |
| Pattern matching | <1ms | P99 |

---

## Source of Truth

### Core Documentation
- **PROJECT_FOUNDATION.md** - Original research, business case, problem definition
- **docs/PROBLEM_STATEMENT.md** - Refined problem statement (Gate 0 output)
- **docs/architecture/ARCHITECTURE.md** - System design (Gate 1 output)
- **docs/specification/SPECIFICATION.md** - Invariants, edge cases (Gate 2 output)
- **docs/testing/TEST_MATRIX.md** - Test stubs and coverage (Gate 3 output)
- **docs/planning/ROADMAP.md** - Development roadmap with traced tasks (Gate 4 output)

### Showcase Documentation
- **docs/showcase/SHOWCASE_ARCHITECTURE.md** - Landing page design and specs
- **docs/planning/week1/** - Day-by-day implementation guides

---

## Project Scope (Updated)

### Core MVP (Weeks 1-4)
- Core detection engine
- Registry clients (PyPI, npm, crates.io)
- CLI interface
- PyPI release

### Showcase Landing Page (Week 5)
- High-end interactive demo
- Animated terminal simulation
- Live validation playground
- Performance visualization
- Mobile responsive design

**Total Effort**: 5 weeks (~200 hours with buffer)

---

## Quick Reference

```
# Session start
/master           # Load context and principles

# Gate progression
/gate-0           # Problem analysis
/gate-1           # Architecture design
/gate-2           # Specification creation
/gate-3           # Test design
/gate-4           # Planning
/gate-5           # Validation (HOSTILE_VALIDATOR)
/gate-6           # Release preparation

# During implementation
/implement        # Guided implementation
/quality-scan     # Run quality checks
/regression-check # Check for regressions
```
