# Phantom Guard — FORTRESS 2.0 Protocol

> **Project**: phantom-guard
> **Purpose**: Detect AI-hallucinated package attacks (slopsquatting)
> **Framework**: FORTRESS 2.0 (Military-Grade Development Protocol)
> **Status**: Gate 0 Complete → Gate 1 (Architecture) Pending

---

## FORTRESS 2.0 — MANDATORY PROTOCOL

This project follows **FORTRESS 2.0**, a strict gate-based development protocol.
**Gates cannot be skipped. Hostile review has veto power. Tests come before code.**

### Gate System

```
Gate 0: Problem Definition    ✅ COMPLETE (PROJECT_FOUNDATION.md)
Gate 1: Architecture          🟡 PENDING
Gate 2: Specification         ⬜ BLOCKED
Gate 3: Test Design           ⬜ BLOCKED
Gate 4: Planning              ⬜ BLOCKED
Gate 5: Validation            ⬜ BLOCKED
Gate 6: Release               ⬜ BLOCKED
```

---

## Commands

### Session Start (ALWAYS RUN FIRST)

```
/master                       # Load FORTRESS 2.0 context and gate status
```

### Gate Commands (Sequential - Cannot Skip)

| Command | Gate | Purpose |
|---------|------|---------|
| `/architect` | 1 | Design system architecture |
| `/spec` | 2 | Create specification (invariants, edge cases) |
| `/test` | 3 | Design test stubs BEFORE code |
| `/roadmap` | 4 | Create traced task breakdown |
| `/hostile-review` | 5 | MANDATORY validation (VETO POWER) |
| `/release` | 6 | Release preparation |

### Implementation Commands

| Command | Purpose |
|---------|---------|
| `/implement` | TDD implementation workflow |
| `/competitive-watch` | Weekly competition scan |
| `/validate-technical` | Monthly API validation |

---

## Absolute Rules — NO EXCEPTIONS

### Rule 1: Gates Cannot Be Skipped

```
❌ FORBIDDEN: "Let's skip architecture and start coding"
❌ FORBIDDEN: "We'll add tests later"
❌ FORBIDDEN: "This is simple, no spec needed"

✅ REQUIRED: Complete Gate N before starting Gate N+1
```

### Rule 2: HOSTILE_VALIDATOR Has Veto Power

```
If HOSTILE_VALIDATOR says NO_GO:
  1. STOP all work
  2. Address every issue raised
  3. Re-run validation
  4. Only proceed after GO verdict

NO EXCEPTIONS. NO SHORTCUTS. NO "WE'LL FIX IT LATER."
```

### Rule 3: TDD Is Mandatory

```
Before writing ANY production code:
  1. Test stub MUST exist
  2. Test MUST fail when run (Red)
  3. Write ONLY enough code to pass (Green)
  4. Refactor if needed
  5. THEN commit
```

### Rule 4: Trace Everything

```
Every function: # IMPLEMENTS: S001
Every test: # SPEC: S001, TEST_ID: T001.1
Every task: TRACES: S001, INV001

Orphan code (no trace) = BUILD FAILURE
```

### Rule 5: Detection Accuracy Is Sacred

```
False positives kill adoption.
- Target: <5% false positive rate
- Test against top 1000 packages
- Every heuristic needs justification
```

---

## Project Structure

```
phantom-guard/
├── .fortress/                    # FORTRESS 2.0 config
│   ├── FORTRESS.md               # Framework status
│   └── gates/                    # Gate completion records
├── .claude/skills/               # Command definitions
│   ├── master/                   # Session start
│   ├── architect/                # Gate 1
│   ├── spec/                     # Gate 2
│   ├── test/                     # Gate 3
│   ├── roadmap/                  # Gate 4
│   ├── hostile-review/           # Gate 5
│   ├── release/                  # Gate 6
│   ├── implement/                # TDD workflow
│   ├── competitive-watch/        # Competition scan
│   └── validate-technical/       # API validation
├── docs/
│   ├── frameworks/               # FORTRESS 2.0 framework docs
│   └── research/                 # Technical research
└── PROJECT_FOUNDATION.md         # SOURCE OF TRUTH
```

---

## Key Files

| File | Purpose |
|------|---------|
| `PROJECT_FOUNDATION.md` | SOURCE OF TRUTH - Original research |
| `.fortress/FORTRESS.md` | Gate status and quality standards |
| `docs/frameworks/FORTRESS_2.0_FRAMEWORK.md` | Full framework documentation |
| `docs/research/TECHNICAL_VALIDATION.md` | API validation research |

---

## Performance Budget

| Operation | Budget | Constraint |
|-----------|--------|------------|
| Single package (cached) | <10ms | P99 |
| Single package (uncached) | <200ms | P99 |
| 50 packages (concurrent) | <5s | P99 |
| Pattern matching | <1ms | P99 |

**Violation = BLOCK MERGE**

---

## Code Standards (For Implementation)

### Required Trace Comments

```python
"""
IMPLEMENTS: S001, S002
INVARIANTS: INV001
TESTS: T001.1, T001.2
"""
def validate_package(name: str) -> PackageRisk:
    ...
```

### Type Hints (MANDATORY)

```python
# Required
def check_package(name: str, registry: str = "pypi") -> PackageRisk:
    ...

# Forbidden
def check_package(name, registry="pypi"):
    ...
```

---

## Current Focus

**Active Gate**: Gate 1 (Architecture)

**Next Action**: Run `/architect` to begin system design

**Blockers**: None

---

## Don't Forget

1. **Gates cannot be skipped** - Complete N before N+1
2. **HOSTILE_VALIDATOR has veto** - NO_GO = STOP
3. **Tests before code** - TDD is mandatory
4. **Trace everything** - No orphan code
5. **False positives kill adoption** - Accuracy is sacred
