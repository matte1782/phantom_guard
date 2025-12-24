---
name: test
description: Testing workflow for quality assurance. Use after implementation to run tests, check coverage, and validate critical paths.
---

# GATE 3: TEST DESIGN — TEST_ARCHITECT PROTOCOL

> **Agent**: TEST_ARCHITECT
> **Gate**: 3 of 6
> **Prerequisite**: Gate 2 (Specification) COMPLETE
> **Output**: Test stubs in tests/, TEST_MATRIX.md

---

## GATE 3 ENTRY CHECKLIST

Before proceeding, verify:

- [ ] .fortress/gates/GATE_2_SPECIFICATION.md exists
- [ ] docs/specification/SPECIFICATION.md is approved
- [ ] All TEST_IDs from Gate 2 are listed
- [ ] Coverage targets defined in specification

**If any checkbox fails**: STOP. Complete Gate 2 first.

---

## TEST_ARCHITECT PROTOCOL

### Core Principle: TESTS BEFORE CODE

```
❌ FORBIDDEN: Write implementation, then tests
✅ REQUIRED: Write test stubs, then implementation

The test stub IS the contract.
If you can't write the test, you don't understand the requirement.
```

---

### Step 1: Create Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_detector.py     # S001-S005
│   ├── test_analyzer.py     # S006-S009
│   ├── test_cli.py          # S010-S015
│   ├── test_cache.py        # S020-S025
│   ├── test_pypi.py         # S030-S035
│   ├── test_npm.py          # S040-S045
│   └── test_crates.py       # S050-S055
├── property/
│   ├── __init__.py
│   ├── test_detector_props.py
│   └── test_analyzer_props.py
├── integration/
│   ├── __init__.py
│   ├── test_pypi_live.py
│   ├── test_npm_live.py
│   └── test_crates_live.py
└── benchmarks/
    ├── __init__.py
    ├── bench_detector.py
    └── bench_cache.py
```

### Step 2: Write Test Stubs

For each TEST_ID in the specification, create a stub:

```python
# tests/unit/test_detector.py
"""
SPEC: S001 - Package Validation
TEST_IDs: T001.1-T001.10
"""

import pytest
from phantom_guard.core.detector import validate_package


class TestValidatePackage:
    """Tests for validate_package function."""

    # T001.1: Valid package name
    @pytest.mark.skip(reason="Stub - implement with S001")
    def test_valid_package_name_passes(self):
        """
        SPEC: S001
        TEST_ID: T001.1
        Given: A valid package name "flask-redis-helper"
        When: validate_package is called
        Then: Returns PackageRisk with valid structure
        """
        # Arrange
        package_name = "flask-redis-helper"

        # Act
        result = validate_package(package_name)

        # Assert
        assert result is not None
        assert result.name == package_name
        assert 0.0 <= result.risk_score <= 1.0

    # T001.2: Empty package name
    @pytest.mark.skip(reason="Stub - implement with S001")
    def test_empty_package_name_raises(self):
        """
        SPEC: S001
        TEST_ID: T001.2
        EDGE_CASE: EC001
        Given: An empty package name ""
        When: validate_package is called
        Then: Raises ValidationError
        """
        with pytest.raises(ValidationError):
            validate_package("")

    # T001.3: Risk score bounds (property test marker)
    @pytest.mark.skip(reason="Stub - implement with S001")
    @pytest.mark.property
    def test_risk_score_always_in_bounds(self):
        """
        SPEC: S001
        TEST_ID: T001.3
        INVARIANT: INV001
        Property: For all valid inputs, risk_score in [0.0, 1.0]
        """
        # Will use hypothesis for property testing
        pass
```

### Step 3: Create Property Test Stubs

```python
# tests/property/test_detector_props.py
"""
SPEC: S001, S002
Property Tests for Detector Module
"""

import pytest
from hypothesis import given, strategies as st


class TestDetectorProperties:
    """Property-based tests for invariant enforcement."""

    # INV001: Risk score bounds
    @pytest.mark.skip(reason="Stub - implement with S001")
    @given(package_name=st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N', 'Pd'))))
    def test_risk_score_always_bounded(self, package_name):
        """
        INVARIANT: INV001
        For ANY valid package name, risk_score is in [0.0, 1.0]
        """
        result = validate_package(package_name)
        assert 0.0 <= result.risk_score <= 1.0

    # INV002: Signals never None
    @pytest.mark.skip(reason="Stub - implement with S001")
    @given(package_name=st.text(min_size=1, max_size=100))
    def test_signals_never_none(self, package_name):
        """
        INVARIANT: INV002
        For ANY input, signals is a list (possibly empty), never None
        """
        try:
            result = validate_package(package_name)
            assert result.signals is not None
            assert isinstance(result.signals, list)
        except ValidationError:
            pass  # Invalid input is allowed to raise
```

### Step 4: Create Integration Test Stubs

```python
# tests/integration/test_pypi_live.py
"""
SPEC: S030-S035
Integration Tests for PyPI Client (LIVE API)
"""

import pytest


@pytest.mark.integration
@pytest.mark.network
class TestPyPILive:
    """Live tests against PyPI API."""

    @pytest.mark.skip(reason="Stub - implement with S030")
    def test_known_package_exists(self):
        """
        SPEC: S030
        TEST_ID: T030.1
        Given: Package "flask" (known to exist)
        When: Query PyPI API
        Then: Returns package metadata
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S030")
    def test_nonexistent_package_not_found(self):
        """
        SPEC: S030
        TEST_ID: T030.2
        EDGE_CASE: EC012
        Given: Package "definitely-not-a-real-package-xyz123"
        When: Query PyPI API
        Then: Returns not found status
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S030")
    def test_api_response_time_within_budget(self):
        """
        SPEC: S030
        TEST_ID: T030.3
        PERFORMANCE: <500ms per request
        Given: Package "requests"
        When: Query PyPI API
        Then: Response time < 500ms
        """
        pass
```

### Step 5: Create Benchmark Stubs

```python
# tests/benchmarks/bench_detector.py
"""
SPEC: S001
Performance Benchmarks for Detector
"""

import pytest


@pytest.mark.benchmark
class TestDetectorBenchmarks:
    """Performance benchmarks for detector operations."""

    @pytest.mark.skip(reason="Stub - implement with S001")
    def test_validate_package_latency(self, benchmark):
        """
        SPEC: S001
        BUDGET: <200ms uncached, <10ms cached
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S001")
    def test_batch_validate_latency(self, benchmark):
        """
        SPEC: S001
        BUDGET: 50 packages in <5s
        """
        pass
```

### Step 6: Create Test Matrix Document

```markdown
# docs/testing/TEST_MATRIX.md

## Test Matrix

| SPEC_ID | Unit | Property | Fuzz | Integration | Bench | Total | Status |
|:--------|:-----|:---------|:-----|:------------|:------|:------|:-------|
| S001 | 5 | 2 | 1 | 1 | 1 | 10 | STUBS |
| S002 | 10 | 3 | 1 | 0 | 1 | 15 | STUBS |
| S010 | 5 | 0 | 0 | 3 | 0 | 8 | STUBS |
| S020 | 6 | 1 | 0 | 2 | 1 | 10 | STUBS |
| S030 | 4 | 0 | 0 | 3 | 1 | 8 | STUBS |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Test Status Legend

- STUBS: Test stubs created, marked skip
- IN_PROGRESS: Some tests passing
- COMPLETE: All tests passing
- VERIFIED: Passing + coverage met

## Coverage Targets

| Metric | Target | Current | Status |
|:-------|:-------|:--------|:-------|
| Line coverage | 90% | 0% | N/A |
| Branch coverage | 85% | 0% | N/A |
| SPEC coverage | 100% | 100% | STUBS ONLY |

## Test Commands

```bash
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
```
```

---

## GATE 3 EXIT CHECKLIST

Before Gate 3 is complete:

- [ ] Test structure created (tests/ directory)
- [ ] Every TEST_ID from spec has a stub
- [ ] Every stub has SPEC/TEST_ID/description
- [ ] Stubs are marked `@pytest.mark.skip`
- [ ] Property tests stubbed for all invariants
- [ ] Integration tests stubbed for all external APIs
- [ ] Benchmark tests stubbed for performance budgets
- [ ] TEST_MATRIX.md created
- [ ] All stubs compile (`pytest --collect-only`)
- [ ] TEST_ARCHITECT review requested

**If any checkbox fails**: DO NOT PROCEED TO GATE 4.

---

## VERIFICATION: STUBS COMPILE

Run this to verify all stubs are valid:

```bash
# Should collect all tests without error
pytest --collect-only

# Should show all skipped tests
pytest -v 2>&1 | grep -c "SKIPPED"
```

Expected: Number of skipped tests = Number of TEST_IDs in spec

---

## RECORDING GATE COMPLETION

```markdown
# .fortress/gates/GATE_3_TEST_DESIGN.md

## Gate 3: Test Design — COMPLETE

**Date**: YYYY-MM-DD
**Approver**: TEST_ARCHITECT
**Output**: tests/, TEST_MATRIX.md

### Summary
- X test stubs created
- Y property tests stubbed
- Z integration tests stubbed

### Test Inventory
| Category | Count |
|:---------|:------|
| Unit | X |
| Property | Y |
| Integration | Z |
| Benchmark | W |
| **Total** | **N** |

### Next Gate
Gate 4: Planning
```

---

## TDD ENFORCEMENT

During Gate 4-5 (implementation), tests drive development:

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

## PROTOCOL VIOLATIONS

| Violation | Response |
|:----------|:---------|
| TEST_ID without stub | Create stub |
| Stub without SPEC reference | Add SPEC |
| Stub doesn't compile | Fix syntax |
| Skipped TEST_ARCHITECT review | Run review |
| Writing code before test stub | STOP, write stub first |

---

*Gate 3 is about DESIGNING tests. Implementation comes in Gate 4-5.*
