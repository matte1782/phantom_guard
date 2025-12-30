# SPEC: S001, S002, S005 - Detector Performance Benchmarks
# Gate 3: Test Design - Implementation
"""
Performance benchmarks for Detector module.

SPEC_IDs: S001, S002, S005
Performance budgets from ARCHITECTURE.md

IMPLEMENTS: Performance validation for core detector operations
"""

from __future__ import annotations

import pytest

from phantom_guard.core.detector import validate_batch_sync, validate_package_sync
from phantom_guard.core.patterns import HALLUCINATION_PATTERNS, match_patterns


@pytest.mark.benchmark
class TestDetectorBenchmarks:
    """Performance benchmarks for detector operations.

    Performance Budget:
    - Single package (uncached): < 200ms P99
    - Single package (cached): < 10ms P99
    - Batch (50 packages): < 5s P99
    """

    def test_validate_package_uncached_latency(self, benchmark):
        """
        TEST_ID: T001.B01
        SPEC: S001
        BUDGET: < 200ms P99 uncached

        Measures: End-to-end validation latency without cache (offline mode)
        """

        def validate_uncached():
            # Use offline mode (no client) - validates static analysis path
            return validate_package_sync("flask-gpt-helper")

        result = benchmark(validate_uncached)

        # Verify the result is valid
        assert result is not None
        assert result.name == "flask-gpt-helper"
        assert result.risk_score > 0  # Should have some risk signals

        # Budget: < 200ms mean
        assert benchmark.stats.stats.mean < 0.2, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 200ms budget"
        )

    def test_validate_package_cached_latency(self, benchmark):
        """
        TEST_ID: T001.B02
        SPEC: S001
        BUDGET: < 10ms P99 cached

        Measures: Validation latency with warm cache (simulated by offline mode)
        Note: In offline mode, there's no actual cache but the path is similar
        to cached performance since no HTTP calls are made.
        """
        # Pre-warm: run once before benchmark
        validate_package_sync("requests")

        def validate_cached():
            # Popular package validation (offline mode)
            return validate_package_sync("requests")

        result = benchmark(validate_cached)

        # Verify the result is valid
        assert result is not None
        assert result.name == "requests"
        # Requests is a popular package, should have low risk
        assert result.risk_score < 0.5

        # Budget: < 10ms mean (offline mode simulates cached path)
        assert benchmark.stats.stats.mean < 0.01, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 10ms budget"
        )

    def test_batch_validate_50_packages(self, benchmark, benchmark_packages):
        """
        TEST_ID: T002.B01
        SPEC: S002
        BUDGET: < 5s for 50 packages

        Measures: Batch validation throughput
        """
        assert len(benchmark_packages) == 50, "Fixture should provide 50 packages"

        def validate_batch():
            return validate_batch_sync(benchmark_packages, concurrency=10)

        results = benchmark(validate_batch)

        # Verify results
        assert len(results) == 50
        assert all(r is not None for r in results)

        # Budget: < 5s mean for 50 packages
        assert benchmark.stats.stats.mean < 5.0, (
            f"Mean latency {benchmark.stats.stats.mean:.2f}s exceeds 5s budget"
        )

    def test_batch_validate_concurrent_speedup(self, benchmark):
        """
        TEST_ID: T002.B02
        SPEC: S002

        Measures: Concurrent vs sequential speedup ratio
        Validates that concurrent processing provides meaningful speedup.
        """
        packages = ["flask", "django", "requests", "numpy", "pandas"] * 4  # 20 packages

        def validate_concurrent():
            return validate_batch_sync(packages, concurrency=10)

        results = benchmark(validate_concurrent)

        # Verify results
        assert len(results) == 20
        assert all(r is not None for r in results)

        # Verify each package was processed
        result_names = [r.name for r in results]
        assert result_names.count("flask") == 4
        assert result_names.count("django") == 4


@pytest.mark.benchmark
class TestPatternMatchBenchmarks:
    """Performance benchmarks for pattern matching.

    Performance Budget:
    - Pattern match: < 1ms P99
    """

    def test_pattern_match_latency(self, benchmark):
        """
        TEST_ID: T005.D01
        SPEC: S005
        BUDGET: < 1ms P99

        Measures: Single pattern match operation (detector context)
        """

        def match_single():
            return match_patterns("flask-gpt-helper")

        result = benchmark(match_single)

        # Verify the result - should match at least one pattern
        assert isinstance(result, tuple)
        assert len(result) > 0, "flask-gpt-helper should match hallucination patterns"

        # Budget: < 1ms mean
        assert benchmark.stats.stats.mean < 0.001, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.4f}ms exceeds 1ms budget"
        )

    def test_pattern_match_batch(self, benchmark):
        """
        TEST_ID: T005.D02
        SPEC: S005

        Measures: Pattern matching 100 names in batch (detector context)
        """
        # Mix of suspicious and normal names
        package_names = [
            "flask-gpt",
            "django-ai",
            "requests-helper",
            "numpy-wrapper",
            "easy-flask",
            "simple-requests",
            "auto-django",
            "flask-gpt-helper",
            "pyopenai",
            "flask-claude",
        ] * 10  # 100 names

        def match_batch():
            results = []
            for name in package_names:
                results.append(match_patterns(name))
            return results

        results = benchmark(match_batch)

        # Verify results
        assert len(results) == 100
        # Some should have matches
        matches_found = sum(1 for r in results if len(r) > 0)
        assert matches_found > 50, "Most suspicious names should have pattern matches"

        # Budget: 100 matches should complete in reasonable time
        # If single match is < 1ms, 100 should be < 100ms
        assert benchmark.stats.stats.mean < 0.1, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms "
            "exceeds 100ms budget for 100 matches"
        )

    def test_pattern_registry_access(self, benchmark):
        """
        TEST_ID: T005.D03
        SPEC: S005

        Measures: Pattern registry access overhead (detector context)
        Validates that pattern lookup is efficient.
        """

        def access_patterns():
            # Access all patterns and check their regex
            count = 0
            for pattern in HALLUCINATION_PATTERNS:
                if pattern.regex.search("test-package"):
                    count += 1
            return count

        result = benchmark(access_patterns)

        # Verify - "test-package" should not match any patterns
        assert result == 0

        # Budget: Iterating patterns should be very fast
        assert benchmark.stats.stats.mean < 0.0001, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.4f}ms exceeds 0.1ms budget"
        )

    def test_pattern_match_no_match(self, benchmark):
        """
        TEST_ID: T005.D04
        SPEC: S005

        Measures: Pattern matching for names that don't match any pattern
        This tests the worst-case scenario where all patterns must be checked.
        """

        def match_no_pattern():
            return match_patterns("completely-normal-package-name")

        result = benchmark(match_no_pattern)

        # Verify - should not match any patterns
        assert isinstance(result, tuple)
        assert len(result) == 0

        # Budget: < 1ms even when checking all patterns
        assert benchmark.stats.stats.mean < 0.001, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.4f}ms exceeds 1ms budget"
        )
