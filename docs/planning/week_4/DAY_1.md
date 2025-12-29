# Week 4 - Day 1: Performance Benchmarks & Baseline

> **Date**: Day 1 (Week 4)
> **Focus**: Comprehensive performance benchmarking and baseline establishment
> **Tasks**: W4.1
> **Hours**: 6 hours
> **Dependencies**: Weeks 1-3 complete
> **Exit Criteria**: All performance budgets documented with baseline measurements

---

## Overview

Establish comprehensive performance benchmarks to validate the performance budget requirements. This ensures we have measurable baselines before optimization and release.

### Performance Budgets (from FORTRESS.md)

| Operation | Budget | Constraint |
|:----------|:-------|:-----------|
| Single package (cached) | <10ms | P99 |
| Single package (uncached) | <200ms | P99 |
| 50 packages (concurrent) | <5s | P99 |
| Pattern matching | <1ms | P99 |

### Deliverables
- [ ] Benchmark test suite with pytest-benchmark
- [ ] Performance baseline measurements document
- [ ] P99 latency validation tests
- [ ] Memory usage profiling
- [ ] CI/CD performance regression tests

---

## Morning Session (3h)

### Objective
Set up comprehensive benchmarking infrastructure and measure baseline performance.

### Step 1: Install Benchmark Dependencies (15min)

```bash
# Add to dev dependencies
pip install pytest-benchmark memory-profiler

# Update pyproject.toml
[project.optional-dependencies]
dev = [
    # ... existing deps
    "pytest-benchmark>=4.0.0",
    "memory-profiler>=0.61.0",
]
```

### Step 2: Create Benchmark Test Suite (1h)

```python
# tests/benchmarks/test_performance_benchmarks.py
"""
Performance benchmarks for Phantom Guard.

These tests validate the performance budget requirements:
- Single package (cached): <10ms P99
- Single package (uncached): <200ms P99
- Batch 50 packages: <5s P99
- Pattern matching: <1ms P99
"""

import pytest
from phantom_guard.core.detector import Detector
from phantom_guard.core.patterns import check_pattern
from phantom_guard.cache import Cache


@pytest.fixture
def detector():
    """Create detector with fresh cache."""
    return Detector()


@pytest.fixture
def warm_cache(detector, tmp_path):
    """Pre-populate cache with test packages."""
    cache = Cache(sqlite_path=tmp_path / "cache.db")
    # Warm cache with known packages
    packages = ["flask", "requests", "django", "numpy", "pandas"]
    # ... warm cache logic
    return cache


class TestSinglePackagePerformance:
    """Benchmark single package validation."""

    @pytest.mark.benchmark(group="single-package")
    def test_cached_package_under_10ms(self, benchmark, warm_cache):
        """
        PERF_ID: PERF001
        BUDGET: <10ms P99

        Cached package lookup should be nearly instant.
        """
        detector = Detector(cache=warm_cache)

        result = benchmark(
            detector.validate_sync,
            "flask",
            registry="pypi"
        )

        # Validate budget
        assert benchmark.stats.stats.max < 0.010  # 10ms

    @pytest.mark.benchmark(group="single-package")
    @pytest.mark.network
    def test_uncached_package_under_200ms(self, benchmark, detector):
        """
        PERF_ID: PERF002
        BUDGET: <200ms P99

        Uncached package should complete within 200ms.
        """
        result = benchmark.pedantic(
            detector.validate_sync,
            args=("flask",),
            kwargs={"registry": "pypi"},
            iterations=5,
            rounds=3,
        )

        # Validate budget (allowing some network variance)
        assert benchmark.stats.stats.max < 0.200  # 200ms


class TestBatchPerformance:
    """Benchmark batch validation."""

    @pytest.mark.benchmark(group="batch")
    @pytest.mark.network
    def test_batch_50_packages_under_5s(self, benchmark, detector):
        """
        PERF_ID: PERF003
        BUDGET: <5s P99

        50 packages should complete within 5 seconds.
        """
        packages = [
            "flask", "requests", "django", "numpy", "pandas",
            "scipy", "matplotlib", "pytest", "click", "typer",
            # ... 40 more packages
        ] * 5  # 50 total

        result = benchmark.pedantic(
            detector.validate_batch_sync,
            args=(packages,),
            iterations=1,
            rounds=3,
        )

        assert benchmark.stats.stats.max < 5.0  # 5 seconds


class TestPatternMatchingPerformance:
    """Benchmark pattern matching speed."""

    @pytest.mark.benchmark(group="patterns")
    def test_pattern_match_under_1ms(self, benchmark):
        """
        PERF_ID: PERF004
        BUDGET: <1ms P99

        Pattern matching should be sub-millisecond.
        """
        test_names = [
            "flask-gpt-helper",
            "requests-ai-wrapper",
            "django-chatgpt-utils",
            "simple-numpy",
            "auto-pandas",
        ]

        def match_all():
            for name in test_names:
                check_pattern(name)

        benchmark(match_all)

        # Each pattern match should be under 1ms
        assert benchmark.stats.stats.max / len(test_names) < 0.001


class TestCachePerformance:
    """Benchmark cache operations."""

    @pytest.mark.benchmark(group="cache")
    def test_memory_cache_hit_under_1ms(self, benchmark, warm_cache):
        """
        PERF_ID: PERF005
        BUDGET: <1ms

        Memory cache hit should be nearly instant.
        """
        result = benchmark(
            warm_cache.get,
            "pypi",
            "flask"
        )

        assert benchmark.stats.stats.max < 0.001  # 1ms

    @pytest.mark.benchmark(group="cache")
    def test_sqlite_cache_hit_under_5ms(self, benchmark, warm_cache):
        """
        PERF_ID: PERF006
        BUDGET: <5ms

        SQLite cache hit should be fast.
        """
        result = benchmark(
            warm_cache.get_sqlite,
            "pypi",
            "flask"
        )

        assert benchmark.stats.stats.max < 0.005  # 5ms
```

### Step 3: Create Memory Profiling Tests (45min)

```python
# tests/benchmarks/test_memory_profile.py
"""Memory usage profiling for Phantom Guard."""

import pytest
from memory_profiler import memory_usage

from phantom_guard.core.detector import Detector
from phantom_guard.core.patterns import PATTERN_DATABASE


class TestMemoryUsage:
    """Validate memory constraints."""

    def test_detector_memory_footprint(self):
        """
        PERF_ID: MEM001

        Detector should not exceed 50MB memory.
        """
        def create_detector():
            detector = Detector()
            return detector

        mem_usage = memory_usage((create_detector,), max_iterations=1)
        max_mem = max(mem_usage)

        # Should be under 50MB
        assert max_mem < 50, f"Detector uses {max_mem}MB, expected <50MB"

    def test_pattern_database_memory(self):
        """
        PERF_ID: MEM002

        Pattern database should be lightweight.
        """
        import sys

        size_bytes = sys.getsizeof(PATTERN_DATABASE)
        size_kb = size_bytes / 1024

        # Pattern database should be under 100KB
        assert size_kb < 100, f"Pattern DB is {size_kb}KB, expected <100KB"

    def test_batch_validation_memory_stable(self):
        """
        PERF_ID: MEM003

        Batch validation should not leak memory.
        """
        detector = Detector()
        packages = ["flask"] * 100

        initial_mem = memory_usage()[0]

        # Run multiple batches
        for _ in range(5):
            results = detector.validate_batch_sync(packages)

        final_mem = memory_usage()[0]

        # Memory should not grow significantly
        mem_growth = final_mem - initial_mem
        assert mem_growth < 20, f"Memory grew by {mem_growth}MB"
```

### Step 4: Run Initial Benchmarks (1h)

```bash
# Run all benchmarks
pytest tests/benchmarks/ -v --benchmark-autosave --benchmark-compare

# Run specific benchmark groups
pytest tests/benchmarks/ -v -k "single-package" --benchmark-only

# Generate benchmark report
pytest tests/benchmarks/ --benchmark-json=benchmark_results.json
```

---

## Afternoon Session (3h)

### Objective
Document baseline measurements and create CI/CD performance regression tests.

### Step 5: Create Baseline Document (1h)

```markdown
# docs/performance/BASELINE_MEASUREMENTS.md

# Performance Baseline - v0.1.0

> **Date**: YYYY-MM-DD
> **Environment**: Python 3.11, macOS/Windows/Linux
> **Commit**: [hash]

## Summary

| Metric | Budget | Baseline | Status |
|:-------|:-------|:---------|:-------|
| Single (cached) | <10ms | Xms | PASS/FAIL |
| Single (uncached) | <200ms | Xms | PASS/FAIL |
| Batch 50 | <5s | Xs | PASS/FAIL |
| Pattern match | <1ms | Xms | PASS/FAIL |

## Detailed Results

### Single Package (Cached)
- Min: X.XXms
- Max: X.XXms
- Mean: X.XXms
- P99: X.XXms

### Single Package (Uncached)
- Min: X.XXms
- Max: X.XXms
- Mean: X.XXms
- P99: X.XXms

### Batch 50 Packages
- Min: X.XXs
- Max: X.XXs
- Mean: X.XXs
- P99: X.XXs

## Memory Usage

| Component | Usage |
|:----------|:------|
| Detector init | XMB |
| Pattern DB | XKB |
| Cache (warm) | XMB |

## Recommendations

[Based on results, identify optimization opportunities]
```

### Step 6: Add CI Performance Tests (45min)

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run benchmarks
        run: |
          pytest tests/benchmarks/ \
            --benchmark-json=benchmark.json \
            --benchmark-compare-fail=min:10%

      - name: Store benchmark results
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: benchmark.json
          fail-on-alert: true
          alert-threshold: '150%'
```

### Step 7: Create Performance Budget Enforcement (45min)

```python
# tests/benchmarks/conftest.py
"""Benchmark configuration and budget enforcement."""

import pytest


# Performance budgets (in seconds)
PERFORMANCE_BUDGETS = {
    "single-cached": 0.010,      # 10ms
    "single-uncached": 0.200,   # 200ms
    "batch-50": 5.0,            # 5s
    "pattern-match": 0.001,     # 1ms
    "memory-cache": 0.001,      # 1ms
    "sqlite-cache": 0.005,      # 5ms
}


def pytest_benchmark_compare_machine_info(config, benchmarksession):
    """Record machine info for benchmark comparison."""
    return {
        "cpu": "benchmark-cpu",
        "memory": "benchmark-memory",
    }


@pytest.fixture
def budget_enforcer():
    """Helper to enforce performance budgets."""
    class BudgetEnforcer:
        def check(self, metric: str, actual: float) -> bool:
            budget = PERFORMANCE_BUDGETS.get(metric)
            if budget is None:
                return True
            return actual <= budget

    return BudgetEnforcer()
```

### Step 8: Document Profiling Commands (30min)

```markdown
# docs/performance/PROFILING_GUIDE.md

# Performance Profiling Guide

## Quick Commands

### Run All Benchmarks
```bash
pytest tests/benchmarks/ -v --benchmark-autosave
```

### Compare Against Baseline
```bash
pytest tests/benchmarks/ --benchmark-compare=0001
```

### Profile Memory
```bash
python -m memory_profiler tests/benchmarks/test_memory_profile.py
```

### Profile CPU
```bash
python -m cProfile -o profile.stats -m pytest tests/unit/test_detector.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

### Generate Flamegraph
```bash
pip install py-spy
py-spy record -o profile.svg -- python -c "from phantom_guard import Detector; Detector().validate_sync('flask')"
```
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check tests/benchmarks/` - No lint errors
- [ ] `ruff format tests/benchmarks/` - Code formatted
- [ ] All benchmark tests discoverable by pytest

### Benchmarks Complete
- [ ] Single package (cached) benchmark
- [ ] Single package (uncached) benchmark
- [ ] Batch 50 packages benchmark
- [ ] Pattern matching benchmark
- [ ] Memory profiling tests
- [ ] Cache performance tests

### Documentation
- [ ] BASELINE_MEASUREMENTS.md created
- [ ] PROFILING_GUIDE.md created
- [ ] CI performance workflow added

### Git Commit

```bash
git add tests/benchmarks/ docs/performance/ .github/workflows/performance.yml
git commit -m "perf: Add comprehensive performance benchmarks

W4.1: Performance benchmarks complete

- Add pytest-benchmark test suite
- Add memory profiling tests
- Create baseline measurements document
- Add CI performance regression tests
- Establish P99 budget enforcement

Performance budgets validated:
- Single (cached): <10ms
- Single (uncached): <200ms
- Batch 50: <5s
- Pattern match: <1ms"
```

---

## Day 1 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.1 | |
| Benchmark Tests | 6+ tests | |
| Budget Violations | 0 | |
| Baseline Document | Created | |
| CI Workflow | Added | |

---

## Tomorrow Preview

**Day 2 Focus**: Performance Optimization (W4.2)
- Analyze benchmark results
- Identify hotspots with profiling
- Optimize critical paths
- Re-run benchmarks to verify improvements
