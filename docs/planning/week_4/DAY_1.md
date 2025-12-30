# Week 4 - Day 1: Performance Benchmarks (OPTIMIZED)

> **Date**: Day 1 (Week 4)
> **Focus**: Implement existing benchmark stubs + add pattern matching benchmarks
> **Tasks**: W4.1
> **Hours**: 6 hours
> **Status**: OPTIMIZED based on hostile review findings

---

## Pre-Existing State Analysis

### What Already Exists (396 lines of benchmark code)

| File | Tests | Status |
|:-----|:------|:-------|
| `test_cli_performance.py` | 5 tests | ✅ PASSING |
| `bench_detector.py` | 4 tests | ⚠️ STUBS (skipped) |
| `bench_scorer.py` | 3 tests | ⚠️ STUBS (skipped) |
| `bench_cache.py` | 10 tests | ⚠️ STUBS (skipped) |

**Total**: 5 passing + 17 stubs to implement

### What's Missing

1. **Pattern matching benchmark** - No file exists, budget <1ms not tested
2. **Memory profiling tests** - Not implemented
3. **pytest-benchmark integration** - Stubs don't use benchmark library
4. **CI performance workflow** - Not created
5. **Baseline measurements document** - Not created

---

## Revised Task Breakdown

### Morning Session (3h) - Implement Core Benchmark Stubs

#### Step 1: Implement bench_detector.py Stubs (1.5h)

Convert 4 skipped stubs to real benchmarks:

```python
# tests/benchmarks/bench_detector.py - IMPLEMENT these stubs

@pytest.mark.benchmark
class TestDetectorBenchmarks:
    """
    IMPLEMENTS: W4.1
    Convert existing stubs to real pytest-benchmark tests.
    """

    def test_validate_package_uncached_latency(self, benchmark):
        """
        TEST_ID: T001.B01
        BUDGET: <200ms P99

        CURRENT: @pytest.mark.skip - STUB
        ACTION: Implement with benchmark.pedantic()
        """
        detector = Detector()

        result = benchmark.pedantic(
            detector.validate_sync,
            args=("flask",),
            kwargs={"registry": "pypi"},
            iterations=5,
            rounds=3,
        )

        assert benchmark.stats.stats.max < 0.200  # 200ms

    def test_validate_package_cached_latency(self, benchmark, warm_cache):
        """
        TEST_ID: T001.B02
        BUDGET: <10ms P99

        CURRENT: @pytest.mark.skip - STUB
        ACTION: Implement with pre-warmed cache
        """
        detector = Detector(cache=warm_cache)

        result = benchmark(detector.validate_sync, "flask", registry="pypi")

        assert benchmark.stats.stats.max < 0.010  # 10ms

    def test_batch_validate_50_packages(self, benchmark):
        """
        TEST_ID: T002.B01
        BUDGET: <5s P99

        CURRENT: @pytest.mark.skip - STUB
        ACTION: Implement with 50 package batch
        """
        detector = Detector()
        packages = ["flask", "django", "requests", "numpy", "pandas"] * 10

        result = benchmark.pedantic(
            detector.validate_batch_sync,
            args=(packages,),
            iterations=1,
            rounds=3,
        )

        assert benchmark.stats.stats.max < 5.0  # 5 seconds

    def test_batch_validate_concurrent_speedup(self, benchmark):
        """
        TEST_ID: T002.B02
        Concurrent should be faster than sequential.

        CURRENT: @pytest.mark.skip - STUB
        ACTION: Compare concurrent vs sequential timing
        """
        # Implementation...
```

#### Step 2: Implement bench_scorer.py Stubs (45min)

Convert 3 skipped stubs:

```python
# tests/benchmarks/bench_scorer.py - IMPLEMENT these stubs

def test_score_calculation_latency(self, benchmark):
    """TEST_ID: T007.B01 - Budget: <0.1ms"""
    # STUB exists - implement real benchmark

def test_score_with_all_signals(self, benchmark):
    """TEST_ID: T007.B02 - Max signals performance"""
    # STUB exists - implement real benchmark

def test_typosquat_check_latency(self, benchmark):
    """TEST_ID: T006.B01 - Budget: <10ms against 1000 packages"""
    # STUB exists - implement real benchmark
```

#### Step 3: Create Pattern Matching Benchmark (45min)

**NEW FILE - Does not exist yet:**

```python
# tests/benchmarks/bench_patterns.py - CREATE NEW

"""
Pattern matching performance benchmarks.

IMPLEMENTS: W4.1
BUDGET: <1ms P99 per pattern check
"""

import pytest
from phantom_guard.core.patterns import check_pattern, PATTERN_DATABASE


@pytest.mark.benchmark
class TestPatternMatchingBenchmarks:
    """Pattern matching must be sub-millisecond."""

    def test_pattern_match_single_under_1ms(self, benchmark):
        """
        PERF_ID: PERF004
        BUDGET: <1ms P99
        """
        result = benchmark(check_pattern, "flask-gpt-helper")
        assert benchmark.stats.stats.max < 0.001  # 1ms

    def test_pattern_match_batch_100_names(self, benchmark):
        """
        Batch 100 pattern checks should complete quickly.
        """
        names = [
            "flask-gpt-helper", "requests-ai-wrapper", "django-chatgpt",
            "simple-numpy", "auto-pandas", "easy-scipy",
        ] * 17  # ~100 names

        def match_all():
            for name in names:
                check_pattern(name)

        benchmark(match_all)
        assert benchmark.stats.stats.max < 0.100  # 100ms for 100 names

    def test_pattern_database_lookup_performance(self, benchmark):
        """Pattern database should be efficiently accessible."""
        def access_patterns():
            return len(PATTERN_DATABASE)

        benchmark(access_patterns)
```

---

### Afternoon Session (3h) - Cache Benchmarks + Infrastructure

#### Step 4: Implement bench_cache.py Stubs (1.5h)

Convert 10 skipped stubs for cache performance:

```python
# tests/benchmarks/bench_cache.py - IMPLEMENT these stubs

def test_memory_cache_get_latency(self, benchmark):
    """BUDGET: <1ms"""

def test_memory_cache_set_latency(self, benchmark):
    """BUDGET: <1ms"""

def test_sqlite_cache_get_latency(self, benchmark):
    """BUDGET: <5ms"""

def test_sqlite_cache_set_latency(self, benchmark):
    """BUDGET: <5ms"""

def test_lru_eviction_overhead(self, benchmark):
    """LRU eviction should not impact performance"""

def test_pypi_client_latency(self, benchmark):
    """Registry client performance"""

def test_npm_client_latency(self, benchmark):
    """Registry client performance"""

def test_crates_client_latency(self, benchmark):
    """Registry client performance"""
```

#### Step 5: Create Memory Profiling Tests (45min)

**NEW FILE:**

```python
# tests/benchmarks/test_memory_profile.py - CREATE NEW

"""Memory usage profiling for Phantom Guard."""

from memory_profiler import memory_usage
from phantom_guard.core.detector import Detector
from phantom_guard.core.patterns import PATTERN_DATABASE


class TestMemoryUsage:
    """Validate memory constraints."""

    def test_detector_memory_footprint(self):
        """Detector should not exceed 50MB."""
        def create_detector():
            return Detector()

        mem = memory_usage((create_detector,), max_iterations=1)
        assert max(mem) < 50  # 50MB

    def test_pattern_database_size(self):
        """Pattern database should be under 100KB."""
        import sys
        size_kb = sys.getsizeof(PATTERN_DATABASE) / 1024
        assert size_kb < 100

    def test_batch_memory_stability(self):
        """Batch operations should not leak memory."""
        detector = Detector()
        initial = memory_usage()[0]

        for _ in range(5):
            detector.validate_batch_sync(["flask"] * 100)

        final = memory_usage()[0]
        assert (final - initial) < 20  # Max 20MB growth
```

#### Step 6: Create Benchmark Infrastructure (30min)

```python
# tests/benchmarks/conftest.py - CREATE/UPDATE

"""Benchmark configuration and fixtures."""

import pytest
from phantom_guard.cache import Cache


PERFORMANCE_BUDGETS = {
    "single-cached": 0.010,      # 10ms
    "single-uncached": 0.200,    # 200ms
    "batch-50": 5.0,             # 5s
    "pattern-match": 0.001,      # 1ms
    "memory-cache": 0.001,       # 1ms
    "sqlite-cache": 0.005,       # 5ms
}


@pytest.fixture
def warm_cache(tmp_path):
    """Pre-populated cache for cached benchmarks."""
    cache = Cache(sqlite_path=tmp_path / "bench_cache.db")
    # Pre-warm with known packages
    return cache


@pytest.fixture
def budget_enforcer():
    """Helper to enforce performance budgets."""
    class Enforcer:
        def check(self, metric: str, actual: float) -> bool:
            budget = PERFORMANCE_BUDGETS.get(metric)
            return actual <= budget if budget else True
    return Enforcer()
```

#### Step 7: Create Baseline Document (15min)

After running all benchmarks, create:

```markdown
# docs/performance/BASELINE_MEASUREMENTS.md

# Performance Baseline - v0.1.0

> **Date**: YYYY-MM-DD
> **Environment**: Python 3.11+
> **Test Count**: 22 benchmarks (5 existing + 17 converted from stubs)

## Summary

| Operation | Budget | Baseline | P99 | Status |
|:----------|:-------|:---------|:----|:-------|
| Single (cached) | <10ms | Xms | Xms | PASS |
| Single (uncached) | <200ms | Xms | Xms | PASS |
| Batch 50 | <5s | Xs | Xs | PASS |
| Pattern match | <1ms | Xms | Xms | PASS |

[Fill in after running benchmarks]
```

---

## Verification Commands

```bash
# Run all benchmarks (should be 22 tests now, not 5)
pytest tests/benchmarks/ -v --benchmark-only

# Run with statistics
pytest tests/benchmarks/ --benchmark-autosave

# Compare against baseline
pytest tests/benchmarks/ --benchmark-compare=0001

# Memory profiling
python -m memory_profiler tests/benchmarks/test_memory_profile.py
```

---

## End of Day Checklist

### Stubs Implemented
- [ ] bench_detector.py: 4 stubs → 4 real benchmarks
- [ ] bench_scorer.py: 3 stubs → 3 real benchmarks
- [ ] bench_cache.py: 10 stubs → 10 real benchmarks
- [ ] **Total**: 17 stubs converted

### New Files Created
- [ ] `tests/benchmarks/bench_patterns.py` (pattern matching)
- [ ] `tests/benchmarks/test_memory_profile.py` (memory profiling)
- [ ] `tests/benchmarks/conftest.py` (fixtures + budgets)
- [ ] `docs/performance/BASELINE_MEASUREMENTS.md`

### Tests Passing
- [ ] 22+ benchmark tests passing (5 existing + 17 converted)
- [ ] All P99 budgets met
- [ ] No memory leaks detected

### Git Commit

```bash
git commit -m "perf(benchmarks): Implement 17 benchmark stubs + add pattern matching

W4.1: Performance benchmarks COMPLETE

- Convert 17 skipped benchmark stubs to real tests
- Add pattern matching benchmarks (budget <1ms)
- Add memory profiling tests
- Create baseline measurements document
- All P99 budgets validated"
```

---

## Day 1 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Benchmark Tests | 22+ | |
| Stubs Converted | 17 | |
| New Benchmarks | 5+ | |
| P99 Violations | 0 | |
| Memory Leaks | 0 | |
