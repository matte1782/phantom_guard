# SPEC: S005, S050-S059 - Pattern Matching Performance Benchmarks
# Gate 3: Test Design
"""
Performance benchmarks for Pattern Matching module.

SPEC_IDs: S005, S050-S059
Performance budget: < 1ms per pattern match
"""

from __future__ import annotations

import pytest

from phantom_guard.core.patterns import (
    HALLUCINATION_PATTERNS,
    count_pattern_matches,
    get_highest_weight_pattern,
    match_patterns,
)

# =============================================================================
# TEST DATA
# =============================================================================

# Package names that should NOT match any patterns
NO_MATCH_PACKAGES = (
    "requests",
    "flask",
    "django",
    "numpy",
    "pandas",
    "scipy",
    "matplotlib",
    "pytest",
    "black",
    "mypy",
)

# Package names that should match single patterns
SINGLE_MATCH_PACKAGES = (
    "mypackage-helper",  # HELPER_SUFFIX
    "mypackage-ai",  # AI_GPT_SUFFIX
    "easy-requests",  # EASY_PREFIX
    "simple-flask",  # SIMPLE_PREFIX
    "auto-deploy",  # AUTO_PREFIX
    "pygpt",  # PY_PREFIX_AI
)

# Package names that should match multiple patterns
MULTI_MATCH_PACKAGES = (
    "flask-gpt-helper",  # POPULAR_AI_COMBO + AI_GPT_INFIX + HELPER_SUFFIX
    "django-ai-utils",  # POPULAR_AI_COMBO + AI_GPT_INFIX + HELPER_SUFFIX
    "fastapi-openai-client",  # POPULAR_AI_COMBO + AI_GPT_INFIX + HELPER_SUFFIX
    "requests-llm-wrapper",  # POPULAR_AI_COMBO + AI_GPT_INFIX + HELPER_SUFFIX
)

# Mixed batch for throughput testing (realistic distribution)
THROUGHPUT_BATCH = (
    NO_MATCH_PACKAGES * 50  # 500 legitimate packages
    + SINGLE_MATCH_PACKAGES * 50  # 300 single-match packages
    + MULTI_MATCH_PACKAGES * 50  # 200 multi-match packages
)


# =============================================================================
# BENCHMARKS
# =============================================================================


@pytest.mark.benchmark
class TestPatternMatchBenchmarks:
    """Performance benchmarks for pattern matching operations.

    Performance Budget:
    - Single pattern match: < 1ms P99
    - Throughput target: > 1000 packages/second
    """

    def test_match_patterns_latency(self, benchmark):
        """
        TEST_ID: T005.B01
        SPEC: S005
        BUDGET: < 1ms P99

        Measures: Single pattern match operation latency.
        Verifies that match_patterns() completes within budget.
        """
        # Use a package that matches a pattern (worst case)
        package_name = "flask-gpt-helper"

        result = benchmark(match_patterns, package_name)

        # Verify correctness
        assert len(result) > 0, "Expected at least one pattern match"

        # Verify performance budget (1ms = 0.001s)
        mean_time = benchmark.stats.stats.mean
        assert mean_time < 0.001, f"Mean latency {mean_time * 1000:.3f}ms exceeds 1ms budget"

    def test_match_patterns_no_match(self, benchmark):
        """
        TEST_ID: T005.B02
        SPEC: S005
        BUDGET: < 1ms P99

        Measures: Pattern matching when no patterns match.
        This is the common case for legitimate packages.
        """
        # Use a legitimate package that should not match
        package_name = "requests"

        result = benchmark(match_patterns, package_name)

        # Verify correctness - no matches expected
        assert len(result) == 0, f"Expected no matches for '{package_name}'"

        # Verify performance budget
        mean_time = benchmark.stats.stats.mean
        assert mean_time < 0.001, f"Mean latency {mean_time * 1000:.3f}ms exceeds 1ms budget"

    def test_match_patterns_multiple_matches(self, benchmark):
        """
        TEST_ID: T005.B03
        SPEC: S005
        BUDGET: < 1ms P99

        Measures: Pattern matching when multiple patterns match.
        This is the worst-case scenario for performance.
        """
        # Use a package name that matches multiple patterns
        package_name = "flask-gpt-helper"

        result = benchmark(match_patterns, package_name)

        # Verify correctness - multiple matches expected
        assert len(result) >= 2, f"Expected multiple matches, got {len(result)}"

        # Verify performance budget
        mean_time = benchmark.stats.stats.mean
        assert mean_time < 0.001, f"Mean latency {mean_time * 1000:.3f}ms exceeds 1ms budget"

    def test_all_patterns_compilation(self, benchmark):
        """
        TEST_ID: T005.B04
        SPEC: S050-S059
        BUDGET: Patterns should be pre-compiled (< 1ms access)

        Measures: Access time for pre-compiled regex patterns.
        Verifies that HALLUCINATION_PATTERNS is pre-compiled at module load.
        """

        def access_patterns():
            """Access all patterns and their regex objects."""
            patterns = []
            for pattern in HALLUCINATION_PATTERNS:
                # Access the compiled regex
                _ = pattern.regex.pattern
                patterns.append(pattern)
            return patterns

        result = benchmark(access_patterns)

        # Verify all 10 patterns exist
        assert len(result) == 10, f"Expected 10 patterns, got {len(result)}"

        # Verify access is fast (patterns are pre-compiled)
        mean_time = benchmark.stats.stats.mean
        assert mean_time < 0.001, "Pattern access should be < 1ms (pre-compiled)"

    def test_pattern_throughput(self, benchmark):
        """
        TEST_ID: T005.B05
        SPEC: S005
        TARGET: > 1000 packages/second

        Measures: Pattern matching throughput on batch of packages.
        Verifies that we can process 1000+ packages per second.
        """
        # Use 1000 packages for throughput measurement
        packages = list(THROUGHPUT_BATCH)[:1000]

        def match_batch():
            """Match patterns for all packages in batch."""
            results = []
            for pkg in packages:
                results.append(match_patterns(pkg))
            return results

        result = benchmark(match_batch)

        # Verify we processed all packages
        assert len(result) == 1000, f"Expected 1000 results, got {len(result)}"

        # Calculate throughput
        total_time = benchmark.stats.stats.mean
        throughput = 1000 / total_time if total_time > 0 else float("inf")

        # Verify throughput target (> 1000 packages/second)
        assert throughput > 1000, f"Throughput {throughput:.0f} pkg/s below 1000 pkg/s target"


@pytest.mark.benchmark
class TestPatternHelperBenchmarks:
    """Performance benchmarks for pattern helper functions."""

    def test_get_highest_weight_pattern_latency(self, benchmark):
        """
        TEST_ID: T005.B06
        SPEC: S005
        BUDGET: < 1ms P99

        Measures: Latency of get_highest_weight_pattern().
        """
        package_name = "flask-gpt-helper"

        result = benchmark(get_highest_weight_pattern, package_name)

        # Verify correctness
        assert result is not None, "Expected a matching pattern"
        assert result.weight > 0, "Expected positive weight"

        # Verify performance budget
        mean_time = benchmark.stats.stats.mean
        assert mean_time < 0.001, f"Mean latency {mean_time * 1000:.3f}ms exceeds 1ms budget"

    def test_get_highest_weight_pattern_no_match(self, benchmark):
        """
        TEST_ID: T005.B07
        SPEC: S005
        BUDGET: < 1ms P99

        Measures: get_highest_weight_pattern() when no patterns match.
        """
        package_name = "requests"

        result = benchmark(get_highest_weight_pattern, package_name)

        # Verify correctness - no match expected
        assert result is None, f"Expected no match for '{package_name}'"

        # Verify performance budget
        mean_time = benchmark.stats.stats.mean
        assert mean_time < 0.001, f"Mean latency {mean_time * 1000:.3f}ms exceeds 1ms budget"

    def test_count_pattern_matches_latency(self, benchmark):
        """
        TEST_ID: T005.B08
        SPEC: S005
        BUDGET: < 1ms P99

        Measures: Latency of count_pattern_matches().
        """
        package_name = "flask-gpt-helper"

        result = benchmark(count_pattern_matches, package_name)

        # Verify correctness
        assert result >= 2, f"Expected multiple matches, got {result}"

        # Verify performance budget
        mean_time = benchmark.stats.stats.mean
        assert mean_time < 0.001, f"Mean latency {mean_time * 1000:.3f}ms exceeds 1ms budget"

    def test_count_pattern_matches_no_match(self, benchmark):
        """
        TEST_ID: T005.B09
        SPEC: S005
        BUDGET: < 1ms P99

        Measures: count_pattern_matches() when no patterns match.
        """
        package_name = "requests"

        result = benchmark(count_pattern_matches, package_name)

        # Verify correctness
        assert result == 0, f"Expected 0 matches, got {result}"

        # Verify performance budget
        mean_time = benchmark.stats.stats.mean
        assert mean_time < 0.001, f"Mean latency {mean_time * 1000:.3f}ms exceeds 1ms budget"
