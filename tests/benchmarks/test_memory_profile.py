# SPEC: S040, S001, S002 - Memory Profiling Tests
# Gate 3: Test Design
"""
Memory profiling tests for Phantom Guard components.

SPEC_IDs: S040 (Cache), S001 (Detector), S002 (Batch)
IMPLEMENTS: Memory usage validation for key components

These tests use tracemalloc to measure memory usage and fail if
memory consumption exceeds expected bounds.
"""

from __future__ import annotations

import asyncio
import gc
import tracemalloc
from typing import TYPE_CHECKING

import pytest

from phantom_guard.cache.memory import MemoryCache
from phantom_guard.cache.types import make_cache_key
from phantom_guard.core.detector import validate_package_sync
from phantom_guard.data import POPULAR_BY_REGISTRY as POPULAR_PACKAGES

if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# MEMORY MEASUREMENT UTILITIES
# =============================================================================


def get_memory_usage_bytes() -> int:
    """
    Get current memory usage in bytes using tracemalloc.

    Returns:
        Current memory usage in bytes
    """
    current, _ = tracemalloc.get_traced_memory()
    return current


def bytes_to_mb(bytes_val: int) -> float:
    """Convert bytes to megabytes."""
    return bytes_val / (1024 * 1024)


def bytes_to_kb(bytes_val: int) -> float:
    """Convert bytes to kilobytes."""
    return bytes_val / 1024


@pytest.fixture(autouse=False)
def memory_tracker() -> Generator[None, None, None]:
    """
    Fixture to start/stop tracemalloc for memory tests.

    Automatically starts tracemalloc before test and stops after.
    """
    gc.collect()  # Clean up before test
    tracemalloc.start()
    yield
    tracemalloc.stop()


# =============================================================================
# MEMORY CACHE TESTS
# =============================================================================


@pytest.mark.benchmark
class TestMemoryCacheFootprint:
    """
    TEST_ID: T040.M01-T040.M04
    SPEC: S040

    Memory footprint tests for MemoryCache component.
    Validates memory usage stays within expected bounds.
    """

    def test_memory_cache_footprint_100_entries(self, memory_tracker: None) -> None:
        """
        TEST_ID: T040.M01
        SPEC: S040

        Validate memory footprint with 100 cache entries.

        Expected: < 1 MB for 100 entries
        Rationale: Each entry ~1KB typical, overhead ~50%
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        cache = MemoryCache(max_size=100)

        # Fill cache with realistic data
        for i in range(100):
            key = make_cache_key("pypi", f"test-package-{i}")
            value = {
                "name": f"test-package-{i}",
                "version": "1.0.0",
                "description": "A test package " * 10,  # ~150 chars
                "author": "Test Author",
                "exists": True,
                "downloads": 1000000,
            }
            cache.set(key, value)

        gc.collect()
        after_fill = get_memory_usage_bytes()
        memory_used = after_fill - baseline

        # Assert: 100 entries should use less than 1 MB
        max_expected_bytes = 1 * 1024 * 1024  # 1 MB
        assert memory_used < max_expected_bytes, (
            f"Memory usage for 100 entries ({bytes_to_kb(memory_used):.2f} KB) "
            f"exceeds limit ({bytes_to_kb(max_expected_bytes):.2f} KB)"
        )

        # Verify all entries are present
        assert len(cache) == 100

    def test_memory_cache_footprint_1000_entries(self, memory_tracker: None) -> None:
        """
        TEST_ID: T040.M02
        SPEC: S040

        Validate memory footprint with 1000 cache entries.

        Expected: < 10 MB for 1000 entries
        Rationale: Linear scaling from 100 entries test
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        cache = MemoryCache(max_size=1000)

        # Fill cache with realistic data
        for i in range(1000):
            key = make_cache_key("pypi", f"test-package-{i}")
            value = {
                "name": f"test-package-{i}",
                "version": "1.0.0",
                "description": "A test package " * 10,
                "author": "Test Author",
                "exists": True,
                "downloads": 1000000,
            }
            cache.set(key, value)

        gc.collect()
        after_fill = get_memory_usage_bytes()
        memory_used = after_fill - baseline

        # Assert: 1000 entries should use less than 10 MB
        max_expected_bytes = 10 * 1024 * 1024  # 10 MB
        assert memory_used < max_expected_bytes, (
            f"Memory usage for 1000 entries ({bytes_to_mb(memory_used):.2f} MB) "
            f"exceeds limit ({bytes_to_mb(max_expected_bytes):.2f} MB)"
        )

        # Verify all entries are present
        assert len(cache) == 1000

    def test_memory_cache_footprint_10000_entries(self, memory_tracker: None) -> None:
        """
        TEST_ID: T040.M03
        SPEC: S040

        Validate memory footprint with 10000 cache entries.

        Expected: < 100 MB for 10000 entries
        Rationale: Linear scaling, validates no exponential growth
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        cache = MemoryCache(max_size=10000)

        # Fill cache with realistic data
        for i in range(10000):
            key = make_cache_key("pypi", f"test-package-{i}")
            value = {
                "name": f"test-package-{i}",
                "version": "1.0.0",
                "description": "A test package " * 10,
                "author": "Test Author",
                "exists": True,
                "downloads": 1000000,
            }
            cache.set(key, value)

        gc.collect()
        after_fill = get_memory_usage_bytes()
        memory_used = after_fill - baseline

        # Assert: 10000 entries should use less than 100 MB
        max_expected_bytes = 100 * 1024 * 1024  # 100 MB
        assert memory_used < max_expected_bytes, (
            f"Memory usage for 10000 entries ({bytes_to_mb(memory_used):.2f} MB) "
            f"exceeds limit ({bytes_to_mb(max_expected_bytes):.2f} MB)"
        )

        # Verify all entries are present
        assert len(cache) == 10000

    def test_memory_cache_per_entry_overhead(self, memory_tracker: None) -> None:
        """
        TEST_ID: T040.M04
        SPEC: S040

        Validate per-entry memory overhead is reasonable.

        Expected: Average entry size < 10 KB
        Rationale: Entry data ~1KB, overhead should be < 10x
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        cache = MemoryCache(max_size=500)

        for i in range(500):
            key = make_cache_key("pypi", f"package-{i}")
            value = {
                "name": f"package-{i}",
                "version": "1.0.0",
                "description": "Description",
                "exists": True,
            }
            cache.set(key, value)

        gc.collect()
        after_fill = get_memory_usage_bytes()
        memory_used = after_fill - baseline

        avg_entry_bytes = memory_used / 500
        max_avg_bytes = 10 * 1024  # 10 KB per entry max

        assert avg_entry_bytes < max_avg_bytes, (
            f"Average entry size ({bytes_to_kb(avg_entry_bytes):.2f} KB) "
            f"exceeds limit ({bytes_to_kb(max_avg_bytes):.2f} KB)"
        )


# =============================================================================
# DETECTOR MEMORY TESTS
# =============================================================================


@pytest.mark.benchmark
class TestDetectorMemory:
    """
    TEST_ID: T001.M01-T001.M02
    SPEC: S001

    Memory stability tests for Detector component.
    Validates memory doesn't grow unboundedly during validation.
    """

    def test_detector_memory_stable(self, memory_tracker: None) -> None:
        """
        TEST_ID: T001.M01
        SPEC: S001

        Validate memory doesn't grow unboundedly during repeated validations.

        Runs validation 100 times and checks memory growth is bounded.
        Expected: Memory growth < 5 MB for 100 validations
        Rationale: Internal LRU caches have limits, growth should plateau
        """
        gc.collect()

        # Warm up - run a few validations to populate internal caches
        for _ in range(5):
            validate_package_sync("flask")

        gc.collect()
        baseline = get_memory_usage_bytes()

        # Run many validations with unique names (worst case for caching)
        for i in range(100):
            name = f"test-pkg-{i}"  # Unique names each time
            validate_package_sync(name)

        gc.collect()
        after_validations = get_memory_usage_bytes()
        memory_growth = after_validations - baseline

        # Allow up to 5 MB growth for 100 unique validations
        # This accounts for internal LRU caches (levenshtein, etc.)
        max_growth = 5 * 1024 * 1024  # 5 MB absolute limit

        assert memory_growth < max_growth, (
            f"Memory grew by {bytes_to_mb(memory_growth):.2f} MB during 100 validations, "
            f"exceeds {bytes_to_mb(max_growth):.2f} MB limit"
        )

    def test_detector_single_validation_memory(self, memory_tracker: None) -> None:
        """
        TEST_ID: T001.M02
        SPEC: S001

        Validate single validation memory usage is bounded.

        Expected: Single validation < 1 MB additional memory
        Rationale: No large allocations for single package check
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        # Single validation
        result = validate_package_sync("requests")

        gc.collect()
        after_validation = get_memory_usage_bytes()
        memory_used = after_validation - baseline

        # Single validation should use less than 1 MB
        max_expected_bytes = 1 * 1024 * 1024  # 1 MB
        assert memory_used < max_expected_bytes, (
            f"Single validation used {bytes_to_kb(memory_used):.2f} KB, "
            f"exceeds limit ({bytes_to_kb(max_expected_bytes):.2f} KB)"
        )

        # Sanity check result
        assert result is not None
        assert result.name == "requests"


# =============================================================================
# BATCH VALIDATION MEMORY TESTS
# =============================================================================


@pytest.mark.benchmark
class TestBatchValidationMemory:
    """
    TEST_ID: T002.M01-T002.M02
    SPEC: S002

    Memory tests for batch validation.
    Validates memory stays bounded during batch processing.
    """

    def test_batch_validation_memory_50_packages(self, memory_tracker: None) -> None:
        """
        TEST_ID: T002.M01
        SPEC: S002

        Validate memory usage during batch validation of 50 packages.

        Expected: < 50 MB total memory for 50 packages
        Rationale: ~1 MB per package worst case
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        # Generate 50 package names
        packages = [f"test-package-{i}" for i in range(50)]

        # Run batch validation
        from phantom_guard.core.detector import validate_batch

        results = asyncio.run(validate_batch(packages, "pypi", concurrency=10))

        gc.collect()
        after_batch = get_memory_usage_bytes()
        memory_used = after_batch - baseline

        # 50 packages should use less than 50 MB
        max_expected_bytes = 50 * 1024 * 1024  # 50 MB
        assert memory_used < max_expected_bytes, (
            f"Batch validation of 50 packages used {bytes_to_mb(memory_used):.2f} MB, "
            f"exceeds limit ({bytes_to_mb(max_expected_bytes):.2f} MB)"
        )

        # Verify we got all results
        assert len(results) == 50

    def test_batch_validation_memory_per_package(self, memory_tracker: None) -> None:
        """
        TEST_ID: T002.M02
        SPEC: S002

        Validate per-package memory overhead in batch is reasonable.

        Expected: Average < 500 KB per package in batch
        Rationale: Batch should be efficient, not duplicate data
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        packages = [f"pkg-batch-{i}" for i in range(100)]

        from phantom_guard.core.detector import validate_batch

        results = asyncio.run(validate_batch(packages, "pypi", concurrency=10))

        gc.collect()
        after_batch = get_memory_usage_bytes()
        memory_used = after_batch - baseline

        avg_per_package = memory_used / 100
        max_avg_bytes = 500 * 1024  # 500 KB per package

        assert avg_per_package < max_avg_bytes, (
            f"Average per-package memory ({bytes_to_kb(avg_per_package):.2f} KB) "
            f"exceeds limit ({bytes_to_kb(max_avg_bytes):.2f} KB)"
        )

        assert len(results) == 100


# =============================================================================
# CACHE EVICTION MEMORY TESTS
# =============================================================================


@pytest.mark.benchmark
class TestCacheEvictionMemory:
    """
    TEST_ID: T040.M05-T040.M06
    SPEC: S040

    Memory tests for cache eviction.
    Validates LRU eviction actually frees memory.
    """

    def test_cache_eviction_frees_memory(self, memory_tracker: None) -> None:
        """
        TEST_ID: T040.M05
        SPEC: S040

        Validate LRU eviction actually frees memory.

        Fill cache to max, then add more entries and verify
        memory stays bounded as old entries are evicted.

        Expected: Memory doesn't exceed 2x the max cache size footprint
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        max_size = 100
        cache = MemoryCache(max_size=max_size)

        # Fill cache to max
        for i in range(max_size):
            key = make_cache_key("pypi", f"initial-{i}")
            value = {
                "name": f"initial-{i}",
                "data": "x" * 1000,  # ~1KB data
            }
            cache.set(key, value)

        gc.collect()
        after_initial_fill = get_memory_usage_bytes()
        initial_memory = after_initial_fill - baseline

        # Add 500 more entries (should evict old ones)
        for i in range(500):
            key = make_cache_key("pypi", f"additional-{i}")
            value = {
                "name": f"additional-{i}",
                "data": "y" * 1000,
            }
            cache.set(key, value)

        gc.collect()
        after_additional = get_memory_usage_bytes()
        final_memory = after_additional - baseline

        # Memory should not be more than 2x initial (eviction working)
        max_allowed = initial_memory * 2 if initial_memory > 0 else 10 * 1024 * 1024

        assert final_memory < max_allowed, (
            f"Memory after evictions ({bytes_to_kb(final_memory):.2f} KB) "
            f"exceeds 2x initial ({bytes_to_kb(max_allowed):.2f} KB). "
            "LRU eviction may not be freeing memory properly."
        )

        # Verify cache size is still at max
        assert len(cache) == max_size

    def test_cache_clear_frees_memory(self, memory_tracker: None) -> None:
        """
        TEST_ID: T040.M06
        SPEC: S040

        Validate cache.clear() releases memory.

        Expected: After clear(), memory usage drops significantly
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        cache = MemoryCache(max_size=1000)

        # Fill cache
        for i in range(1000):
            key = make_cache_key("pypi", f"clear-test-{i}")
            value = {
                "name": f"clear-test-{i}",
                "data": "z" * 500,
            }
            cache.set(key, value)

        gc.collect()
        after_fill = get_memory_usage_bytes()
        filled_memory = after_fill - baseline

        # Clear the cache
        cleared_count = cache.clear()

        # Force garbage collection
        gc.collect()
        gc.collect()  # Second pass for cyclic refs

        after_clear = get_memory_usage_bytes()
        cleared_memory = after_clear - baseline

        # Memory after clear should be significantly less (< 50% of filled)
        max_after_clear = filled_memory * 0.5

        assert cleared_memory < max_after_clear, (
            f"Memory after clear ({bytes_to_kb(cleared_memory):.2f} KB) "
            f"should be < 50% of filled ({bytes_to_kb(max_after_clear):.2f} KB)"
        )

        assert cleared_count == 1000
        assert len(cache) == 0


# =============================================================================
# POPULAR PACKAGES DATA TESTS
# =============================================================================


@pytest.mark.benchmark
class TestPopularPackagesMemory:
    """
    TEST_ID: T006.M01
    SPEC: S006

    Memory footprint tests for popular packages data.
    Validates the in-memory popular packages database is efficient.
    """

    def test_popular_packages_footprint(self, memory_tracker: None) -> None:
        """
        TEST_ID: T006.M01
        SPEC: S006

        Validate memory footprint of ~300 popular package names.

        Expected: < 1 MB for all popular packages data
        Rationale: ~300 names * ~20 bytes avg = ~6KB, plus overhead
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        # Access all popular packages to ensure they're loaded
        all_packages: set[str] = set()
        for _registry, packages in POPULAR_PACKAGES.items():
            all_packages.update(packages)

        # Force materialization
        package_list = list(all_packages)
        total_count = len(package_list)

        gc.collect()
        after_load = get_memory_usage_bytes()
        memory_used = after_load - baseline

        # All popular packages should use less than 1 MB
        max_expected_bytes = 1 * 1024 * 1024  # 1 MB
        assert memory_used < max_expected_bytes, (
            f"Popular packages ({total_count} names) use {bytes_to_kb(memory_used):.2f} KB, "
            f"exceeds limit ({bytes_to_kb(max_expected_bytes):.2f} KB)"
        )

    def test_popular_packages_3000_simulated(self, memory_tracker: None) -> None:
        """
        TEST_ID: T006.M02
        SPEC: S006

        Validate memory footprint if we had 3000 popular package names.

        Simulates scaling to 3000 packages to validate memory scaling.
        Expected: < 5 MB for 3000 package names
        Rationale: Linear scaling from current ~300 names
        """
        gc.collect()
        baseline = get_memory_usage_bytes()

        # Simulate 3000 package names (10x current)
        simulated_packages: frozenset[str] = frozenset(
            f"simulated-popular-package-{i}" for i in range(3000)
        )

        # Force materialization and access
        package_count = len(simulated_packages)
        _ = list(simulated_packages)  # Materialize

        gc.collect()
        after_load = get_memory_usage_bytes()
        memory_used = after_load - baseline

        # 3000 package names should use less than 5 MB
        max_expected_bytes = 5 * 1024 * 1024  # 5 MB
        assert memory_used < max_expected_bytes, (
            f"Simulated 3000 packages use {bytes_to_mb(memory_used):.2f} MB, "
            f"exceeds limit ({bytes_to_mb(max_expected_bytes):.2f} MB)"
        )

        assert package_count == 3000


# =============================================================================
# MEMORY LEAK DETECTION TESTS
# =============================================================================


@pytest.mark.benchmark
class TestMemoryLeaks:
    """
    TEST_ID: T000.M01-T000.M02
    SPEC: S001, S040

    Memory leak detection tests.
    Validates no memory leaks in repeated operations.
    """

    def test_no_leak_repeated_cache_operations(self, memory_tracker: None) -> None:
        """
        TEST_ID: T000.M01
        SPEC: S040

        Validate no memory leak in repeated cache get/set cycles.

        Expected: Memory stable after 10 cycles of fill/clear
        """
        gc.collect()

        cache = MemoryCache(max_size=100)

        # Warm up
        for i in range(100):
            cache.set(f"warmup-{i}", {"data": i})
        cache.clear()
        gc.collect()

        baseline = get_memory_usage_bytes()

        # Run 10 cycles of fill/clear
        for cycle in range(10):
            for i in range(100):
                cache.set(f"cycle-{cycle}-{i}", {"data": "x" * 100})
            cache.clear()
            gc.collect()

        after_cycles = get_memory_usage_bytes()
        growth = after_cycles - baseline

        # Should have minimal growth (< 1 MB)
        max_growth = 1 * 1024 * 1024  # 1 MB
        assert growth < max_growth, (
            f"Memory grew by {bytes_to_kb(growth):.2f} KB after 10 cache cycles, "
            f"possible memory leak"
        )

    def test_no_leak_repeated_validations_different_names(self, memory_tracker: None) -> None:
        """
        TEST_ID: T000.M02
        SPEC: S001

        Validate no memory leak with many unique package names.

        Expected: Memory growth bounded even with unique names
        """
        gc.collect()

        # Warm up with some validations
        for i in range(10):
            validate_package_sync(f"warmup-{i}")

        gc.collect()
        baseline = get_memory_usage_bytes()

        # Validate many unique names
        for i in range(200):
            validate_package_sync(f"unique-package-name-{i}")

        gc.collect()
        after_validations = get_memory_usage_bytes()
        growth = after_validations - baseline

        # Growth should be bounded (internal LRU caches have limits)
        # Allow up to 20 MB for 200 validations with LRU caches
        max_growth = 20 * 1024 * 1024  # 20 MB
        assert growth < max_growth, (
            f"Memory grew by {bytes_to_mb(growth):.2f} MB validating 200 unique packages, "
            f"possible memory leak or unbounded cache"
        )
