# Phantom Guard — Test Matrix

> **Version**: 0.1.0
> **Date**: 2025-12-24
> **Gate**: 3 of 6 - Test Design
> **Status**: STUBS CREATED

---

## 1. Test Inventory Summary

| Category | Count | Status |
|:---------|:------|:-------|
| Unit Tests | 145 | STUBS |
| Property Tests | 15 | STUBS |
| Fuzz Tests | 5 | STUBS |
| Integration Tests | 29 | STUBS |
| Benchmarks | 10 | STUBS |
| **TOTAL** | **204** | STUBS |

---

## 2. SPEC_ID to Test Matrix

| SPEC_ID | Description | Unit | Property | Fuzz | Integration | Bench | Total | Status |
|:--------|:------------|:-----|:---------|:-----|:------------|:------|:------|:-------|
| S001 | Package validation | 20 | 8 | 2 | 2 | 2 | 34 | STUBS |
| S002 | Batch validation | 8 | 1 | 0 | 2 | 2 | 13 | STUBS |
| S003 | Detection orchestrator | 5 | 0 | 0 | 0 | 0 | 5 | STUBS |
| S004 | Signal extraction | 20 | 0 | 0 | 0 | 0 | 20 | STUBS |
| S005 | Pattern matching | 17 | 0 | 0 | 0 | 2 | 19 | STUBS |
| S006 | Typosquat detection | 19 | 7 | 1 | 0 | 1 | 28 | STUBS |
| S007 | Risk calculation | 17 | 6 | 0 | 0 | 2 | 25 | STUBS |
| S008 | Threshold evaluation | 6 | 1 | 0 | 0 | 0 | 7 | STUBS |
| S009 | Result aggregation | 5 | 2 | 0 | 0 | 0 | 7 | STUBS |
| S010-S019 | CLI commands | 24 | 0 | 0 | 8 | 0 | 32 | STUBS |
| S020-S026 | PyPI client | 15 | 0 | 0 | 7 | 1 | 23 | STUBS |
| S027-S032 | npm client | 12 | 0 | 0 | 4 | 1 | 17 | STUBS |
| S033-S039 | crates.io client | 13 | 0 | 0 | 4 | 1 | 18 | STUBS |
| S040-S049 | Cache system | 17 | 0 | 0 | 4 | 5 | 26 | STUBS |
| S050-S059 | Pattern database | 3 | 0 | 0 | 0 | 0 | 3 | STUBS |

---

## 3. Invariant to Test Matrix

| INV_ID | Statement | Test Type | Test File | Status |
|:-------|:----------|:----------|:----------|:-------|
| INV001 | risk_score in [0.0, 1.0] | proptest | test_detector_props.py | STUB |
| INV002 | signals never None | unit + mypy | test_detector.py | STUB |
| INV003 | cached = uncached | integration | test_cache_integration.py | STUB |
| INV004 | batch contains all | unit | test_detector.py | STUB |
| INV005 | fail_fast stops | unit | test_detector.py | STUB |
| INV006 | returns PackageRisk | mypy | test_detector.py | STUB |
| INV007 | pure function | unit | test_analyzer.py | STUB |
| INV008 | valid PatternMatch | unit | test_patterns.py | STUB |
| INV009 | threshold in (0,1) | proptest | test_typosquat_props.py | STUB |
| INV010 | monotonicity | proptest | test_scorer_props.py | STUB |
| INV011 | thresholds ordered | unit | test_scorer.py | STUB |
| INV012 | aggregate preserves | proptest | test_scorer_props.py | STUB |
| INV013 | valid metadata or raises | unit | test_pypi.py, test_npm.py, test_crates.py | STUB |
| INV014 | timeout honored | integration | test_*_live.py | STUB |
| INV015 | User-Agent header | integration | test_crates_live.py | STUB |
| INV016 | TTL honored | unit | test_cache.py | STUB |
| INV017 | size limit enforced | unit | test_cache.py | STUB |
| INV018 | immutable during match | review | test_patterns.py | STUB |
| INV019 | valid chars | unit + fuzz | test_detector.py | STUB |
| INV020 | length 1-214 | unit | test_detector.py | STUB |
| INV021 | known registry | unit | test_detector.py | STUB |
| INV022 | config thresholds valid | unit | test_scorer.py | STUB |

---

## 4. Edge Case to Test Matrix

| EC_ID Range | Category | Count | Test File | Status |
|:------------|:---------|:------|:----------|:-------|
| EC001-EC015 | Package name input | 15 | test_detector.py | STUB |
| EC020-EC035 | Registry responses | 16 | test_pypi.py, test_npm.py, test_crates.py | STUB |
| EC040-EC055 | Risk scoring | 16 | test_scorer.py, test_analyzer.py | STUB |
| EC060-EC070 | Cache behavior | 11 | test_cache.py | STUB |
| EC080-EC095 | CLI behavior | 16 | test_cli.py | STUB |
| EC100-EC110 | Pattern matching | 11 | test_patterns.py | STUB |

---

## 5. Test File Registry

### Unit Tests

| File | SPEC_IDs | Test Count | Status |
|:-----|:---------|:-----------|:-------|
| tests/unit/test_detector.py | S001-S003 | 28 | STUBS |
| tests/unit/test_analyzer.py | S004 | 20 | STUBS |
| tests/unit/test_patterns.py | S005, S050-S059 | 20 | STUBS |
| tests/unit/test_typosquat.py | S006 | 19 | STUBS |
| tests/unit/test_scorer.py | S007-S009 | 23 | STUBS |
| tests/unit/test_pypi.py | S020-S026 | 15 | STUBS |
| tests/unit/test_npm.py | S027-S032 | 12 | STUBS |
| tests/unit/test_crates.py | S033-S039 | 13 | STUBS |
| tests/unit/test_cache.py | S040-S049 | 17 | STUBS |
| tests/unit/test_cli.py | S010-S019 | 24 | STUBS |

### Property Tests

| File | INV_IDs | Test Count | Status |
|:-----|:--------|:-----------|:-------|
| tests/property/test_detector_props.py | INV001, INV002, INV004, INV019, INV020 | 10 | STUBS |
| tests/property/test_scorer_props.py | INV001, INV010, INV011, INV012 | 8 | STUBS |
| tests/property/test_typosquat_props.py | INV009 | 7 | STUBS |

### Integration Tests

| File | SPEC_IDs | Test Count | Status |
|:-----|:---------|:-----------|:-------|
| tests/integration/test_pypi_live.py | S020-S026 | 7 | STUBS |
| tests/integration/test_npm_live.py | S027-S032 | 4 | STUBS |
| tests/integration/test_crates_live.py | S033-S039 | 4 | STUBS |
| tests/integration/test_cache_integration.py | S040-S049 | 4 | STUBS |
| tests/integration/test_cli_integration.py | S010-S019 | 10 | STUBS |

### Benchmarks

| File | SPEC_IDs | Test Count | Status |
|:-----|:---------|:-----------|:-------|
| tests/benchmarks/bench_detector.py | S001, S002, S005 | 4 | STUBS |
| tests/benchmarks/bench_cache.py | S040-S049 | 6 | STUBS |
| tests/benchmarks/bench_scorer.py | S006, S007 | 3 | STUBS |

---

## 6. Test Status Legend

| Status | Description |
|:-------|:------------|
| STUBS | Test stubs created, marked @pytest.mark.skip |
| IN_PROGRESS | Some tests implemented and passing |
| COMPLETE | All tests implemented and passing |
| VERIFIED | Passing + coverage targets met |

---

## 7. Coverage Targets

| Metric | Target | Minimum | Current | Status |
|:-------|:-------|:--------|:--------|:-------|
| Line coverage | 90% | 85% | 0% | STUBS ONLY |
| Branch coverage | 85% | 80% | 0% | STUBS ONLY |
| SPEC coverage | 100% | 100% | 100% | STUBS ONLY |
| Property tests | 10,000 cases | 1,000 | 0 | STUBS ONLY |
| Fuzz duration | 1 hour | 10 min | 0 | STUBS ONLY |

---

## 8. Test Commands

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=phantom_guard --cov-report=html

# Run property tests
pytest -m property

# Run integration tests (requires network)
pytest -m integration

# Run benchmarks
pytest -m benchmark --benchmark-only

# Run fuzz tests
pytest -m fuzz

# Collect all tests (verify stubs compile)
pytest --collect-only

# Count skipped tests (should equal 204 initially)
pytest -v 2>&1 | grep -c "SKIPPED"
```

---

## 9. P2 Issues from Gate 2 (Addressed)

| Issue ID | Description | Resolution |
|:---------|:------------|:-----------|
| P2-EC-001 | EC_ID numbering gaps | Accepted - gaps maintained for clarity |
| P2-EC-002 | Missing npm scoped package cases | Added T027.03, T027.11, T027.12 |
| P2-EC-003 | Boundary condition precision | Clarified in T004.13-T004.18 |
| P2-CONS-001 | Registry-specific name rules | Added T027.11 (npm leading number) |
| P2-CONS-002 | Exit code priority | Documented in test_cli.py |
| P2-CONS-003 | Neutral score precision | EC048 tests for ≈0.38 |

---

## 10. TDD Workflow

During Gate 4-5 implementation:

```
1. Pick a test stub from this matrix
2. Remove @pytest.mark.skip
3. Run test → MUST FAIL (Red)
4. Write minimal code to pass
5. Run test → MUST PASS (Green)
6. Refactor if needed
7. Update this matrix (Status → COMPLETE)
8. Commit
```

---

## Appendix: Test Decision Log

### A. Framework Decisions

| Decision | Choice | Rationale |
|:---------|:-------|:----------|
| Property testing | Hypothesis | Standard for Python, good strategies |
| Mocking | unittest.mock + respx | Native + async HTTP mocking |
| Benchmarking | pytest-benchmark | Integrates with pytest |
| Coverage | pytest-cov | Standard, good reporting |

### B. Mock Strategy

| Component | Mock Strategy |
|:----------|:--------------|
| Registry APIs | respx (async HTTP mocking) |
| Time | freezegun |
| Cache | temp directories |
| Network | pytest-httpx or respx |

---

**Gate 3 Status**: STUBS COMPLETE

**Next Step**: Run `pytest --collect-only` to verify all stubs compile

**Next Gate**: Gate 4 (Planning) after TEST_ARCHITECT review
