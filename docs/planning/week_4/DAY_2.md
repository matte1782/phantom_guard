# Week 4 - Day 2: Performance Optimization (OPTIMIZED)

> **Date**: Day 2 (Week 4)
> **Focus**: Optimize based on W4.1 benchmark results
> **Tasks**: W4.2
> **Hours**: 6 hours
> **Status**: OPTIMIZED based on hostile review findings
> **Dependencies**: W4.1 (Performance Benchmarks) complete

---

## Pre-Existing State Analysis

### What Already Exists (Optimized Code)

| Component | Status | Optimization Level |
|:----------|:-------|:-------------------|
| `patterns.py` | ✅ 273 lines | Pre-compiled regex, frozen dataclass |
| `typosquat.py` | ✅ 579 lines | LRU-cached Levenshtein |
| `memory.py` | ⚠️ Basic | Needs __slots__ + OrderedDict |
| `batch.py` | ✅ Implemented | Semaphore-based concurrency |

### Patterns Module (Already Optimized)
```python
# src/phantom_guard/core/patterns.py - ALREADY OPTIMIZED
# - Pre-compiled regex patterns (re.compile at module load)
# - Frozen dataclass with __slots__
# - 10 hallucination patterns defined
```

### Typosquat Module (Already Optimized)
```python
# src/phantom_guard/core/typosquat.py - ALREADY OPTIMIZED
# - LRU cache on levenshtein_distance (maxsize=10000)
# - Early exit for length differences
# - 172 popular packages (needs expansion in W4.3)
```

---

## Revised Task Breakdown

### Morning Session (3h) - Profile & Identify Remaining Hotspots

#### Step 1: Run W4.1 Benchmarks and Profile (1h)

```bash
# Run all benchmarks from Day 1
pytest tests/benchmarks/ -v --benchmark-only --benchmark-autosave

# Generate CPU profile for critical paths
python -m cProfile -o validate_profile.stats -c "
import asyncio
from phantom_guard.core.detector import Detector

async def main():
    detector = Detector()
    for _ in range(100):
        await detector.validate('flask')

asyncio.run(main())
"

# Analyze profile
python -c "
import pstats
p = pstats.Stats('validate_profile.stats')
p.strip_dirs()
p.sort_stats('cumulative')
p.print_stats(20)
"
```

#### Step 2: Optimize Memory Cache (1.5h)

The memory cache can be optimized with `__slots__` and `OrderedDict`:

```python
# src/phantom_guard/cache/memory.py - OPTIMIZE
"""
IMPLEMENTS: S040
OPTIMIZED: Add __slots__ + OrderedDict for O(1) LRU.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from threading import Lock
from time import time
from typing import Any


@dataclass(slots=True)
class CacheEntry:
    """Lightweight cache entry with slots for memory efficiency."""
    value: Any
    expires_at: float
    created_at: float = field(default_factory=time)


class MemoryCache:
    """
    IMPLEMENTS: S040
    OPTIMIZED: O(1) operations with OrderedDict LRU.
    """

    __slots__ = ('_cache', '_lock', '_max_size', '_default_ttl', '_hits', '_misses')

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: float = 300.0,
    ) -> None:
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """O(1) cache lookup with LRU update."""
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if time() > entry.expires_at:
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """O(1) cache set with automatic eviction."""
        ttl = ttl or self._default_ttl
        expires_at = time() + ttl

        with self._lock:
            if key in self._cache:
                self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
                self._cache.move_to_end(key)
                return

            while len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)

            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
```

#### Step 3: Verify Pattern Matching Performance (30min)

```bash
# Verify patterns are sub-millisecond
pytest tests/benchmarks/bench_patterns.py -v --benchmark-only

# Expected: <1ms per pattern check (already optimized)
```

---

### Afternoon Session (3h) - Batch & Cache Optimization

#### Step 4: Tune Batch Concurrency (1h)

Review and tune batch processing parameters:

```python
# src/phantom_guard/core/batch.py - REVIEW AND TUNE

# Current defaults (verify optimal):
# - max_concurrency: 10 (check API rate limits)
# - chunk_size: 20 (balance memory vs throughput)
# - timeout_per_package: 5.0 (adjust based on registry latency)

# Run batch benchmark
pytest tests/benchmarks/bench_detector.py::test_batch_validate_50_packages -v
```

#### Step 5: Optimize Registry Client Connection Pooling (1h)

```python
# src/phantom_guard/registry/base.py - VERIFY CONNECTION POOLING

# Ensure httpx client reuses connections:
# - limits=httpx.Limits(max_connections=20)
# - timeout=httpx.Timeout(10.0, connect=5.0)
```

#### Step 6: Re-run All Benchmarks (45min)

```bash
# Run full benchmark suite
pytest tests/benchmarks/ -v --benchmark-autosave

# Compare against baseline from Day 1
pytest tests/benchmarks/ --benchmark-compare=0001

# Verify all budgets met:
# - Pattern matching: <1ms ✓ (already optimized)
# - Cache hits: <1ms (after optimization)
# - Batch 50: <5s ✓ (verify)
```

#### Step 7: Update Baseline Document (15min)

Update `docs/performance/BASELINE_MEASUREMENTS.md` with:
- Post-optimization measurements
- Improvement percentages
- Any remaining hotspots

---

## End of Day Checklist

### Optimizations Applied
- [ ] Memory cache uses `__slots__` + `OrderedDict`
- [ ] Batch concurrency parameters tuned
- [ ] Connection pooling verified

### Performance Verified
- [ ] Pattern matching <1ms (pre-existing)
- [ ] Memory cache <1ms (after optimization)
- [ ] Batch 50 <5s (verified)
- [ ] No memory leaks

### Code Quality
- [ ] `ruff check src/phantom_guard/` - No lint errors
- [ ] `mypy src/phantom_guard/ --strict` - No type errors
- [ ] All tests passing

### Git Commit

```bash
git add src/phantom_guard/cache/ docs/performance/
git commit -m "perf: Optimize memory cache with __slots__ + OrderedDict

W4.2: Performance optimization COMPLETE

- Add __slots__ to CacheEntry for memory efficiency
- Use OrderedDict for O(1) LRU operations
- Verify batch concurrency parameters
- Validate connection pooling
- All performance budgets met

Pattern matching: Already optimized (pre-compiled regex)
Typosquat: Already optimized (LRU-cached Levenshtein)"
```

---

## Day 2 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.2 | |
| Performance Regressions | 0 | |
| Budget Violations | 0 | |
| Memory Cache Improvement | 2-3x | |

---

## Key Insight from Hostile Review

Most optimization is already done:
- **patterns.py**: Pre-compiled regex ✓
- **typosquat.py**: LRU-cached Levenshtein ✓

Focus on:
1. Memory cache `__slots__` optimization
2. Verifying existing optimizations meet budgets
3. Documenting baseline measurements

---

## Tomorrow Preview

**Day 3 Focus**: Popular Packages Database (W4.3)
- CRITICAL: Expand from 172 → 3000+ packages
- PyPI: 97 → 1000
- npm: 50 → 1000
- crates: 25 → 1000
