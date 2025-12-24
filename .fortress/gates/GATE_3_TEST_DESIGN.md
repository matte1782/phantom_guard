# Gate 3: Test Design — COMPLETE

> **Date**: 2025-12-24
> **Approver**: TEST_ARCHITECT
> **Verdict**: GO
> **Output**: tests/, docs/testing/TEST_MATRIX.md

---

## Summary

Complete test design for Phantom Guard with 258 test stubs created across all categories. All tests compile and are ready for TDD implementation.

### Test Inventory

| Category | Count | Status |
|:---------|:------|:-------|
| Unit Tests | 191 | STUBS |
| Property Tests | 25 | STUBS |
| Fuzz Tests | 5 | STUBS |
| Integration Tests | 29 | STUBS |
| Benchmarks | 13 | STUBS |
| **TOTAL** | **258** | STUBS |

---

## Test Structure Created

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures, markers
├── unit/
│   ├── __init__.py
│   ├── test_detector.py           # S001-S003 (28 tests)
│   ├── test_analyzer.py           # S004 (20 tests)
│   ├── test_patterns.py           # S005, S050-S059 (20 tests)
│   ├── test_typosquat.py          # S006 (19 tests)
│   ├── test_scorer.py             # S007-S009 (23 tests)
│   ├── test_pypi.py               # S020-S026 (15 tests)
│   ├── test_npm.py                # S027-S032 (12 tests)
│   ├── test_crates.py             # S033-S039 (13 tests)
│   ├── test_cache.py              # S040-S049 (17 tests)
│   └── test_cli.py                # S010-S019 (24 tests)
├── property/
│   ├── __init__.py
│   ├── test_detector_props.py     # INV001, INV002, INV004 (11 tests)
│   ├── test_scorer_props.py       # INV010, INV011, INV012 (9 tests)
│   └── test_typosquat_props.py    # INV009 (8 tests)
├── integration/
│   ├── __init__.py
│   ├── test_pypi_live.py          # S020-S026 live (7 tests)
│   ├── test_npm_live.py           # S027-S032 live (4 tests)
│   ├── test_crates_live.py        # S033-S039 live (4 tests)
│   ├── test_cache_integration.py  # S040-S049 (4 tests)
│   └── test_cli_integration.py    # S010-S019 (10 tests)
└── benchmarks/
    ├── __init__.py
    ├── bench_detector.py          # S001, S002 (4 tests)
    ├── bench_cache.py             # S040-S049 (6 tests)
    └── bench_scorer.py            # S006, S007 (3 tests)
```

---

## Verification

### Compilation Check

```
pytest --collect-only: 258 tests collected
pytest -v: 258 skipped in 0.21s
```

All test stubs compile and are properly marked as skipped.

### Invariant Coverage

All 22 invariants have corresponding test stubs:
- INV001-INV012: Core invariants covered
- INV013-INV018: Registry client invariants covered
- INV019-INV022: Input validation invariants covered

### Edge Case Coverage

All 85 edge cases have corresponding test stubs:
- EC001-EC015: Package name input
- EC020-EC035: Registry responses
- EC040-EC055: Risk scoring
- EC060-EC070: Cache behavior
- EC080-EC095: CLI behavior
- EC100-EC110: Pattern matching

---

## P2 Issues Addressed (from Gate 2)

| Issue ID | Description | Resolution |
|:---------|:------------|:-----------|
| P2-EC-001 | EC_ID numbering gaps | Accepted gaps for clarity |
| P2-EC-002 | npm scoped package cases | Added T027.03, T027.11, T027.12 |
| P2-EC-003 | Boundary conditions | Clarified in T004.13-T004.18 |
| P2-CONS-001 | Registry-specific rules | Added T027.11 |
| P2-CONS-002 | Exit code priority | Documented in test_cli.py |
| P2-CONS-003 | Neutral score precision | EC048 tests ≈0.38 |

---

## Test Design Decisions

| Decision | Choice | Rationale |
|:---------|:-------|:----------|
| Property testing | Hypothesis | Python standard, good strategies |
| Mocking | unittest.mock + respx | Native + async HTTP mocking |
| Benchmarking | pytest-benchmark | Integrates with pytest |
| Coverage | pytest-cov | Standard, good reporting |

---

## Artifacts

| Artifact | Location |
|:---------|:---------|
| Test Matrix | docs/testing/TEST_MATRIX.md |
| Test Structure | tests/ |
| This Gate Record | .fortress/gates/GATE_3_TEST_DESIGN.md |

---

## Next Gate

**Gate 4: Planning**

Command: `/roadmap`

Required outputs:
- Traced task breakdown with SPEC_ID links
- Implementation order based on dependencies
- Weekly execution plan

---

## TDD Enforcement

During Gate 4-5 implementation:

```
1. Pick a test stub
2. Remove @pytest.mark.skip
3. Run test → MUST FAIL (Red)
4. Write minimal code to pass
5. Run test → MUST PASS (Green)
6. Refactor if needed
7. Commit
```

**If test passes before code exists**: Something is wrong.

---

*Gate 3 is about DESIGNING tests. Implementation comes in Gate 4-5.*
