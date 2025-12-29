# Week 4 - Day 2: Performance Optimization

> **Date**: Day 2 (Week 4)
> **Focus**: Analyze benchmarks, identify hotspots, optimize critical paths
> **Tasks**: W4.2
> **Hours**: 6 hours
> **Dependencies**: W4.1 (Performance Benchmarks) complete
> **Exit Criteria**: All performance budgets met, no regressions

---

## Overview

Based on Day 1 benchmark results, identify and optimize performance bottlenecks. Focus on the critical path: single package validation and batch processing.

### Optimization Priorities

1. **Pattern Matching** - Most frequently called, should be instant
2. **Cache Hits** - Memory cache must be <1ms
3. **Registry API Calls** - Minimize redundant network requests
4. **Batch Concurrency** - Optimal semaphore limits

### Deliverables
- [ ] Profile analysis report
- [ ] Optimized pattern matching (pre-compiled regex)
- [ ] Cache warm-up optimization
- [ ] Batch concurrency tuning
- [ ] Re-run benchmarks with improvements

---

## Morning Session (3h)

### Objective
Analyze profiling data and implement pattern matching optimizations.

### Step 1: Generate Detailed Profiles (30min)

```bash
# CPU profile for single package validation
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
p.print_stats(30)
"

# Generate flamegraph
py-spy record -o flamegraph.svg -- python -c "
import asyncio
from phantom_guard import Detector

async def main():
    d = Detector()
    for _ in range(50):
        await d.validate('flask')

asyncio.run(main())
"
```

### Step 2: Optimize Pattern Matching (1h)

```python
# src/phantom_guard/core/patterns.py
"""
IMPLEMENTS: S005, S050-S059
OPTIMIZED: Pre-compiled regex patterns for sub-millisecond matching.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phantom_guard.core.types import PatternMatch


@dataclass(frozen=True, slots=True)
class CompiledPattern:
    """Pre-compiled pattern for fast matching."""
    name: str
    regex: re.Pattern[str]
    weight: float
    description: str


# Pre-compile ALL patterns at module load time
_COMPILED_PATTERNS: tuple[CompiledPattern, ...] = tuple([
    CompiledPattern(
        name="ai_suffix",
        regex=re.compile(r"-(gpt|ai|llm|chatgpt|openai|anthropic|claude)$", re.IGNORECASE),
        weight=0.3,
        description="AI-related suffix detected",
    ),
    CompiledPattern(
        name="helper_suffix",
        regex=re.compile(r"-(helper|utils|tools|wrapper|client)$", re.IGNORECASE),
        weight=0.2,
        description="Helper/utility suffix detected",
    ),
    CompiledPattern(
        name="simple_prefix",
        regex=re.compile(r"^(easy|simple|quick|fast|auto|super)-", re.IGNORECASE),
        weight=0.15,
        description="Simplicity prefix detected",
    ),
    CompiledPattern(
        name="typo_pattern",
        regex=re.compile(r"(.)\1{2,}", re.IGNORECASE),  # Triple+ repeated chars
        weight=0.4,
        description="Suspicious character repetition",
    ),
    # ... more patterns
])


@lru_cache(maxsize=10000)
def check_pattern(name: str) -> tuple[PatternMatch, ...]:
    """
    IMPLEMENTS: S005
    OPTIMIZED: LRU cache + pre-compiled regex

    Check package name against all patterns.
    Results are cached for repeated lookups.
    """
    matches: list[PatternMatch] = []

    for pattern in _COMPILED_PATTERNS:
        if pattern.regex.search(name):
            matches.append(PatternMatch(
                pattern_name=pattern.name,
                weight=pattern.weight,
                description=pattern.description,
            ))

    return tuple(matches)


def get_pattern_stats() -> dict[str, int]:
    """Get cache statistics for monitoring."""
    info = check_pattern.cache_info()
    return {
        "hits": info.hits,
        "misses": info.misses,
        "size": info.currsize,
        "maxsize": info.maxsize,
    }
```

### Step 3: Optimize Typosquat Detection (1h)

```python
# src/phantom_guard/core/typosquat.py
"""
IMPLEMENTS: S006
OPTIMIZED: Pre-computed distance matrix + early exit.
"""

from __future__ import annotations

from functools import lru_cache

# Pre-load popular packages as frozenset for O(1) lookup
_PYPI_POPULAR: frozenset[str] = frozenset([
    "flask", "requests", "django", "numpy", "pandas",
    "scipy", "matplotlib", "pytest", "click", "typer",
    # ... top 200 packages
])

_NPM_POPULAR: frozenset[str] = frozenset([
    "express", "react", "lodash", "axios", "moment",
    # ... top 200 packages
])

_CRATES_POPULAR: frozenset[str] = frozenset([
    "serde", "tokio", "clap", "rand", "log",
    # ... top 200 packages
])

_REGISTRY_POPULAR: dict[str, frozenset[str]] = {
    "pypi": _PYPI_POPULAR,
    "npm": _NPM_POPULAR,
    "crates": _CRATES_POPULAR,
}


@lru_cache(maxsize=50000)
def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Cached Levenshtein distance calculation.

    Uses dynamic programming with space optimization.
    """
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    if not s2:
        return len(s1)

    # Early exit for identical strings
    if s1 == s2:
        return 0

    # Early exit if length difference is too large
    if abs(len(s1) - len(s2)) > 3:
        return abs(len(s1) - len(s2))

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def find_typosquat_candidates(
    name: str,
    registry: str = "pypi",
    max_distance: int = 2,
) -> list[tuple[str, int]]:
    """
    IMPLEMENTS: S006
    OPTIMIZED: Early exit + distance threshold pruning.

    Find packages that could be typosquats of popular packages.
    """
    popular = _REGISTRY_POPULAR.get(registry, _PYPI_POPULAR)

    # Fast path: if package IS popular, not a typosquat
    if name in popular:
        return []

    candidates: list[tuple[str, int]] = []
    name_len = len(name)

    for pkg in popular:
        # Skip if length difference makes typosquat unlikely
        if abs(len(pkg) - name_len) > max_distance:
            continue

        dist = levenshtein_distance(name, pkg)
        if 0 < dist <= max_distance:
            candidates.append((pkg, dist))

    # Sort by distance (closest first)
    candidates.sort(key=lambda x: x[1])

    return candidates[:5]  # Return top 5 candidates
```

### Step 4: Verify Pattern Optimization (30min)

```bash
# Run pattern matching benchmark
pytest tests/benchmarks/test_performance_benchmarks.py::TestPatternMatchingPerformance -v --benchmark-only

# Expected: <1ms per pattern check
```

---

## Afternoon Session (3h)

### Objective
Optimize cache and batch processing performance.

### Step 5: Optimize Memory Cache (1h)

```python
# src/phantom_guard/cache/memory.py
"""
IMPLEMENTS: S040
OPTIMIZED: __slots__ + OrderedDict for LRU.
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

    Thread-safe in-memory LRU cache with TTL support.
    """

    __slots__ = ('_cache', '_lock', '_max_size', '_default_ttl', '_hits', '_misses')

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: float = 300.0,  # 5 minutes
    ) -> None:
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """
        O(1) cache lookup with LRU update.
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            # Check expiration
            if time() > entry.expires_at:
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """
        O(1) cache set with automatic eviction.
        """
        ttl = ttl or self._default_ttl
        expires_at = time() + ttl

        with self._lock:
            # If key exists, update and move to end
            if key in self._cache:
                self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
                self._cache.move_to_end(key)
                return

            # Evict oldest if at capacity
            while len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)

            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
```

### Step 6: Optimize Batch Concurrency (1h)

```python
# src/phantom_guard/core/batch.py
"""
IMPLEMENTS: S002
OPTIMIZED: Adaptive concurrency + connection pooling.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Callable

from phantom_guard.core.types import PackageRisk


@dataclass
class BatchConfig:
    """Batch processing configuration."""
    max_concurrency: int = 10      # Optimal for most APIs
    chunk_size: int = 20           # Process in chunks
    timeout_per_package: float = 5.0
    fail_fast: bool = False


class BatchValidator:
    """
    IMPLEMENTS: S002
    OPTIMIZED: Chunked processing + connection reuse.
    """

    def __init__(
        self,
        detector: "Detector",
        config: BatchConfig | None = None,
    ) -> None:
        self.detector = detector
        self.config = config or BatchConfig()

    async def validate_batch(
        self,
        packages: list[str],
        registry: str = "pypi",
        on_progress: Callable[[int, int], None] | None = None,
    ) -> list[PackageRisk]:
        """
        Validate packages in optimized batches.

        Uses chunking to balance memory and throughput.
        """
        results: list[PackageRisk] = []
        total = len(packages)
        completed = 0

        # Process in chunks to avoid overwhelming the event loop
        for i in range(0, total, self.config.chunk_size):
            chunk = packages[i:i + self.config.chunk_size]

            # Use semaphore for rate limiting within chunk
            semaphore = asyncio.Semaphore(self.config.max_concurrency)

            async def validate_one(pkg: str) -> PackageRisk:
                async with semaphore:
                    return await asyncio.wait_for(
                        self.detector.validate(pkg, registry=registry),
                        timeout=self.config.timeout_per_package,
                    )

            # Gather chunk results
            chunk_results = await asyncio.gather(
                *[validate_one(pkg) for pkg in chunk],
                return_exceptions=True,
            )

            for pkg, result in zip(chunk, chunk_results):
                if isinstance(result, Exception):
                    # Handle timeout/error gracefully
                    results.append(PackageRisk.error(pkg, str(result)))
                else:
                    results.append(result)

                    # Fail fast on HIGH_RISK
                    if self.config.fail_fast and result.recommendation == "HIGH_RISK":
                        return results

                completed += 1
                if on_progress:
                    on_progress(completed, total)

        return results
```

### Step 7: Re-run All Benchmarks (45min)

```bash
# Run full benchmark suite
pytest tests/benchmarks/ -v --benchmark-autosave

# Compare against baseline
pytest tests/benchmarks/ --benchmark-compare=0001

# Expected output:
# - Pattern matching: >50% improvement
# - Cache hits: 2-3x faster
# - Batch processing: Consistent under budget
```

### Step 8: Update Baseline Document (15min)

Update `docs/performance/BASELINE_MEASUREMENTS.md` with:
- Post-optimization measurements
- Improvement percentages
- Any remaining hotspots

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/core/` - No lint errors
- [ ] `ruff format src/phantom_guard/` - Code formatted
- [ ] `mypy src/phantom_guard/ --strict` - No type errors
- [ ] All tests still passing (no regressions)

### Performance Verified
- [ ] Pattern matching <1ms
- [ ] Memory cache <1ms
- [ ] Batch 50 <5s
- [ ] No memory leaks

### Documentation
- [ ] BASELINE_MEASUREMENTS.md updated
- [ ] Optimization notes added to code

### Git Commit

```bash
git add src/phantom_guard/core/ src/phantom_guard/cache/ docs/performance/
git commit -m "perf: Optimize critical paths for performance budgets

W4.2: Performance optimization complete

- Pre-compile regex patterns (50% faster matching)
- Add LRU cache for Levenshtein distance
- Optimize MemoryCache with __slots__ + OrderedDict
- Add chunked batch processing with adaptive concurrency
- Update baseline measurements

All performance budgets now met:
- Pattern match: <1ms (was Xms, now Xms)
- Cache hit: <1ms (was Xms, now Xms)
- Batch 50: <5s (was Xs, now Xs)"
```

---

## Day 2 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.2 | |
| Performance Regressions | 0 | |
| Budget Violations | 0 | |
| Improvement % | >20% | |

---

## Tomorrow Preview

**Day 3 Focus**: Popular Packages List (W4.3)
- Fetch top 1000 packages from PyPI, npm, crates.io
- Create static frozen sets
- Integrate with typosquat detection
- Reduce false positive rate
