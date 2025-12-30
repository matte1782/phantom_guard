# SPEC: S006, S007 - Scorer Performance Benchmarks
# Gate 3: Test Design - Implemented Benchmarks
"""
Performance benchmarks for Scorer module.

SPEC_IDs: S006, S007
IMPLEMENTS: S006, S007

Performance budgets:
- Score calculation: < 0.1ms
- Typosquat check: < 10ms
"""

from __future__ import annotations

import pytest

from phantom_guard.core.scorer import calculate_risk_score, determine_recommendation
from phantom_guard.core.types import Recommendation, Signal, SignalType
from phantom_guard.core.typosquat import check_typosquat, levenshtein_distance


@pytest.mark.benchmark
class TestScorerBenchmarks:
    """Performance benchmarks for scoring operations.

    Performance Budget:
    - Score calculation: < 0.1ms (100 microseconds)
    """

    def test_score_calculation_latency(self, benchmark):
        """
        TEST_ID: T007.B01
        SPEC: S007
        IMPLEMENTS: S007

        Measures: Single score calculation time
        Expected: < 0.1ms (0.0001 seconds)
        """
        # Create a typical set of signals for realistic benchmark
        signals = (
            Signal(
                type=SignalType.RECENTLY_CREATED,
                weight=0.3,
                message="Package created recently",
            ),
            Signal(
                type=SignalType.LOW_DOWNLOADS,
                weight=0.2,
                message="Low download count",
            ),
        )

        def calculate_score():
            return calculate_risk_score(signals)

        result = benchmark(calculate_score)

        # Verify correct calculation
        assert 0.0 <= result <= 1.0
        # Performance assertion: mean should be < 0.1ms (100 microseconds)
        assert benchmark.stats.stats.mean < 0.0001, (
            f"Score calculation too slow: {benchmark.stats.stats.mean * 1000:.3f}ms > 0.1ms"
        )

    def test_score_with_all_signals(self, benchmark):
        """
        TEST_ID: T007.B02
        SPEC: S007
        IMPLEMENTS: S007

        Measures: Score calculation with maximum signals
        """
        # Create signals representing all risk signal types
        all_signals = (
            Signal(
                type=SignalType.NOT_FOUND,
                weight=0.8,
                message="Package not found",
            ),
            Signal(
                type=SignalType.RECENTLY_CREATED,
                weight=0.4,
                message="Package created recently",
            ),
            Signal(
                type=SignalType.LOW_DOWNLOADS,
                weight=0.3,
                message="Low download count",
            ),
            Signal(
                type=SignalType.NO_REPOSITORY,
                weight=0.25,
                message="No repository linked",
            ),
            Signal(
                type=SignalType.NO_MAINTAINER,
                weight=0.2,
                message="No maintainer info",
            ),
            Signal(
                type=SignalType.FEW_RELEASES,
                weight=0.15,
                message="Few releases",
            ),
            Signal(
                type=SignalType.SHORT_DESCRIPTION,
                weight=0.1,
                message="Short description",
            ),
            Signal(
                type=SignalType.HALLUCINATION_PATTERN,
                weight=0.6,
                message="Matches hallucination pattern",
            ),
            Signal(
                type=SignalType.TYPOSQUAT,
                weight=0.7,
                message="Possible typosquat",
            ),
            # Include a positive signal to test mixed scoring
            Signal(
                type=SignalType.POPULAR_PACKAGE,
                weight=-0.5,
                message="Popular package",
            ),
        )

        def calculate_with_all():
            score = calculate_risk_score(all_signals)
            recommendation = determine_recommendation(score, exists=True)
            return score, recommendation

        result = benchmark(calculate_with_all)

        # Verify correct result types
        score, recommendation = result
        assert 0.0 <= score <= 1.0
        assert isinstance(recommendation, Recommendation)
        # Performance: should still be fast even with many signals
        assert benchmark.stats.stats.mean < 0.0001, (
            f"Score with all signals too slow: {benchmark.stats.stats.mean * 1000:.3f}ms > 0.1ms"
        )

    def test_typosquat_check_latency(self, benchmark):
        """
        TEST_ID: T006.B01
        SPEC: S006
        IMPLEMENTS: S006

        Measures: Typosquat check against popular packages database
        Expected: < 10ms
        """
        # Use a realistic typosquat candidate
        typosquat_name = "reqeusts"  # Common typo of "requests"

        def check_typo():
            return check_typosquat(typosquat_name, registry="pypi")

        result = benchmark(check_typo)

        # Verify detection works correctly
        assert result is not None, "Expected to detect 'reqeusts' as typosquat of 'requests'"
        assert result.target == "requests"
        assert result.distance <= 2
        # Performance assertion: mean should be < 10ms
        assert benchmark.stats.stats.mean < 0.010, (
            f"Typosquat check too slow: {benchmark.stats.stats.mean * 1000:.3f}ms > 10ms"
        )


@pytest.mark.benchmark
class TestLevenshteinBenchmarks:
    """Performance benchmarks for Levenshtein distance calculation.

    These are sub-tests to verify the underlying algorithm performance.
    """

    def test_levenshtein_short_strings(self, benchmark):
        """
        TEST_ID: T006.B02
        SPEC: S006
        IMPLEMENTS: S006

        Measures: Edit distance calculation for short strings (typical package names)
        """
        s1 = "requests"
        s2 = "reqeusts"

        def calc_distance():
            return levenshtein_distance(s1, s2)

        result = benchmark(calc_distance)

        assert result == 2  # Two transpositions
        # Should be very fast for short strings
        assert benchmark.stats.stats.mean < 0.00001, (
            f"Levenshtein too slow: {benchmark.stats.stats.mean * 1000000:.3f}us > 10us"
        )

    def test_levenshtein_longer_strings(self, benchmark):
        """
        TEST_ID: T006.B03
        SPEC: S006
        IMPLEMENTS: S006

        Measures: Edit distance for longer package names
        """
        s1 = "typing-extensions"
        s2 = "typin-extentions"

        def calc_distance():
            return levenshtein_distance(s1, s2)

        result = benchmark(calc_distance)

        assert result >= 1  # At least one difference
        # Still should be fast
        assert benchmark.stats.stats.mean < 0.0001, (
            f"Levenshtein longer strings too slow: "
            f"{benchmark.stats.stats.mean * 1000:.3f}ms > 0.1ms"
        )
