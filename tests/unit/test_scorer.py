# SPEC: S007-S009 - Risk Scoring
# Gate 3: Test Design - Implementation
"""
Unit tests for the Scorer module.

SPEC_IDs: S007, S008, S009
TEST_IDs: T007.*, T008.*, T009.*
INVARIANTS: INV001, INV010, INV011, INV012
EDGE_CASES: EC040-EC055
"""

from __future__ import annotations

import pytest

from phantom_guard.core.scorer import (
    THRESHOLD_SAFE,
    THRESHOLD_SUSPICIOUS,
    ThresholdConfig,
    aggregate_results,
    build_package_risk,
    calculate_raw_score,
    calculate_risk_score,
    determine_recommendation,
)
from phantom_guard.core.types import (
    PackageRisk,
    Recommendation,
    Signal,
    SignalType,
)


class TestRiskCalculation:
    """Tests for calculate_risk_score function.

    SPEC: S007 - Risk calculation
    """

    # =========================================================================
    # SCORE BOUNDS TESTS (INV001)
    # =========================================================================

    @pytest.mark.unit
    def test_score_minimum_with_negative_signals(self) -> None:
        """
        TEST_ID: T007.01
        SPEC: S007
        INV: INV001
        EC: EC040

        Given: All safe signals (negative weights)
        When: calculate_risk_score is called
        Then: Returns score close to 0.0
        """
        # Maximum negative weight = -1.0
        signals = (
            Signal(SignalType.POPULAR_PACKAGE, -0.5, "Very popular"),
            Signal(SignalType.LONG_HISTORY, -0.3, "Long history"),
        )
        score = calculate_risk_score(signals)
        assert score < 0.3  # Should be low

    @pytest.mark.unit
    def test_score_maximum_with_high_risk(self) -> None:
        """
        TEST_ID: T007.02
        SPEC: S007
        INV: INV001
        EC: EC041

        Given: All high risk signals
        When: calculate_risk_score is called
        Then: Returns score = 1.0 (clamped)
        """
        signals = (
            Signal(SignalType.NOT_FOUND, 0.9, "Package not found"),
            Signal(SignalType.TYPOSQUAT, 0.95, "Typosquat detected"),
            Signal(SignalType.HALLUCINATION_PATTERN, 0.8, "AI pattern"),
        )
        score = calculate_risk_score(signals)
        assert score == 1.0  # Clamped to max

    @pytest.mark.unit
    def test_score_clamped_low(self) -> None:
        """
        TEST_ID: T007.03
        SPEC: S007
        INV: INV001
        EC: EC054

        Given: Extremely safe package (strong negative weights)
        When: calculate_risk_score is called
        Then: Returns score = 0.0 (clamped)
        """
        # Create signals that would push raw score below -100
        signals = tuple(Signal(SignalType.POPULAR_PACKAGE, -1.0, f"Popular {i}") for i in range(3))
        score = calculate_risk_score(signals)
        assert score == 0.0

    @pytest.mark.unit
    def test_score_clamped_high(self) -> None:
        """
        TEST_ID: T007.04
        SPEC: S007
        INV: INV001
        EC: EC055

        Given: Extremely risky package (many high-weight signals)
        When: calculate_risk_score is called
        Then: Returns score = 1.0 (clamped)
        """
        signals = tuple(Signal(SignalType.TYPOSQUAT, 1.0, f"Risk {i}") for i in range(5))
        score = calculate_risk_score(signals)
        assert score == 1.0

    # =========================================================================
    # SIGNAL COMBINATION TESTS
    # =========================================================================

    @pytest.mark.unit
    def test_mixed_signals_middle_score(self) -> None:
        """
        TEST_ID: T007.05
        SPEC: S007
        EC: EC042

        Given: Mixed signals (some safe, some risky)
        When: calculate_risk_score is called
        Then: Returns 0.3 < score < 0.7
        """
        signals = (
            Signal(SignalType.LOW_DOWNLOADS, 0.3, "Low downloads"),
            Signal(SignalType.POPULAR_PACKAGE, -0.3, "Known package"),
        )
        score = calculate_risk_score(signals)
        assert 0.3 < score < 0.7

    @pytest.mark.unit
    def test_popular_package_low_score(self) -> None:
        """
        TEST_ID: T007.06
        SPEC: S007
        EC: EC043

        Given: Popular package signal only
        When: calculate_risk_score is called
        Then: Returns score < 0.3
        """
        signals = (Signal(SignalType.POPULAR_PACKAGE, -0.5, "Popular"),)
        score = calculate_risk_score(signals)
        assert score < 0.3

    @pytest.mark.unit
    def test_typosquat_high_score(self) -> None:
        """
        TEST_ID: T007.08
        SPEC: S007
        EC: EC046

        Given: Typosquat signal
        When: calculate_risk_score is called
        Then: Returns score > 0.5
        """
        signals = (Signal(SignalType.TYPOSQUAT, 0.9, "Typosquat of requests"),)
        score = calculate_risk_score(signals)
        assert score > 0.5

    @pytest.mark.unit
    def test_hallucination_pattern_elevated_score(self) -> None:
        """
        TEST_ID: T007.09
        SPEC: S007
        EC: EC047

        Given: Package with hallucination pattern
        When: calculate_risk_score is called
        Then: Returns score > 0.5
        """
        signals = (Signal(SignalType.HALLUCINATION_PATTERN, 0.7, "AI pattern"),)
        score = calculate_risk_score(signals)
        assert score > 0.5

    @pytest.mark.unit
    def test_no_signals_neutral_score(self) -> None:
        """
        TEST_ID: T007.10
        SPEC: S007
        EC: EC048

        Given: No signals at all (empty tuple)
        When: calculate_risk_score is called
        Then: Returns score ≈ 0.38 (neutral)
        """
        score = calculate_risk_score(())
        # (0 + 100) / 260 ≈ 0.385
        assert 0.38 <= score <= 0.39

    @pytest.mark.unit
    def test_single_weak_signal_moderate_score(self) -> None:
        """
        TEST_ID: T007.11
        SPEC: S007
        EC: EC049

        Given: Single weak signal
        When: calculate_risk_score is called
        Then: Returns moderate score
        """
        signals = (Signal(SignalType.NO_REPOSITORY, 0.2, "No repo"),)
        score = calculate_risk_score(signals)
        assert 0.4 < score < 0.5

    @pytest.mark.unit
    def test_single_strong_signal_high_score(self) -> None:
        """
        TEST_ID: T007.12
        SPEC: S007
        EC: EC050

        Given: Single strong signal (TYPOSQUAT)
        When: calculate_risk_score is called
        Then: Returns score > 0.6
        """
        signals = (Signal(SignalType.TYPOSQUAT, 0.95, "Typosquat"),)
        score = calculate_risk_score(signals)
        assert score > 0.6

    # =========================================================================
    # NORMALIZATION TESTS
    # =========================================================================

    @pytest.mark.unit
    def test_normalization_formula(self) -> None:
        """
        TEST_ID: T007.13
        SPEC: S007

        Given: Known raw score
        When: Normalizing
        Then: Uses formula (raw + 100) / 260
        """
        # With weight 0.5, raw = 50
        signals = (Signal(SignalType.LOW_DOWNLOADS, 0.5, "Test"),)
        raw = calculate_raw_score(signals)
        expected = (raw + 100) / 260
        actual = calculate_risk_score(signals)
        assert abs(expected - actual) < 0.001

    @pytest.mark.unit
    def test_signal_weights_applied(self) -> None:
        """
        TEST_ID: T007.14
        SPEC: S007

        Given: Signals with known weights
        When: calculate_risk_score is called
        Then: Weights are correctly summed
        """
        signals = (
            Signal(SignalType.LOW_DOWNLOADS, 0.3, "Low"),
            Signal(SignalType.RECENTLY_CREATED, 0.4, "New"),
        )
        raw = calculate_raw_score(signals)
        assert raw == 70  # (0.3 + 0.4) * 100


class TestThresholdEvaluation:
    """Tests for determine_recommendation function.

    SPEC: S008 - Threshold evaluation
    """

    @pytest.mark.unit
    def test_thresholds_ordered(self) -> None:
        """
        TEST_ID: T008.01
        SPEC: S008
        INV: INV011

        Given: Default thresholds
        When: Comparing values
        Then: safe < suspicious
        """
        assert THRESHOLD_SAFE < THRESHOLD_SUSPICIOUS

    @pytest.mark.unit
    def test_score_below_safe_is_safe(self) -> None:
        """
        TEST_ID: T008.02
        SPEC: S008

        Given: Score below safe threshold
        When: determine_recommendation is called
        Then: Returns SAFE recommendation
        """
        rec = determine_recommendation(0.1, exists=True)
        assert rec == Recommendation.SAFE

    @pytest.mark.unit
    def test_score_between_safe_and_suspicious(self) -> None:
        """
        TEST_ID: T008.03
        SPEC: S008

        Given: Score between safe and suspicious threshold
        When: determine_recommendation is called
        Then: Returns SUSPICIOUS recommendation
        """
        rec = determine_recommendation(0.45, exists=True)
        assert rec == Recommendation.SUSPICIOUS

    @pytest.mark.unit
    def test_score_above_suspicious_is_high_risk(self) -> None:
        """
        TEST_ID: T008.04
        SPEC: S008

        Given: Score above suspicious threshold
        When: determine_recommendation is called
        Then: Returns HIGH_RISK recommendation
        """
        rec = determine_recommendation(0.8, exists=True)
        assert rec == Recommendation.HIGH_RISK

    @pytest.mark.unit
    def test_not_exists_returns_not_found(self) -> None:
        """
        TEST_ID: T008.05
        SPEC: S008

        Given: Package does not exist
        When: determine_recommendation is called
        Then: Returns NOT_FOUND
        """
        rec = determine_recommendation(0.5, exists=False)
        assert rec == Recommendation.NOT_FOUND

    @pytest.mark.unit
    def test_custom_thresholds_applied(self) -> None:
        """
        TEST_ID: T008.06
        SPEC: S008

        Given: Custom threshold values
        When: determine_recommendation is called
        Then: Uses custom thresholds
        """
        custom = ThresholdConfig(safe=0.5, suspicious=0.8)
        # With custom, 0.4 should be SAFE (below 0.5)
        rec = determine_recommendation(0.4, exists=True, thresholds=custom)
        assert rec == Recommendation.SAFE

    @pytest.mark.unit
    def test_invalid_threshold_order_rejected(self) -> None:
        """
        TEST_ID: T008.07
        SPEC: S008
        INV: INV011

        Given: Thresholds where safe >= suspicious
        When: Creating config
        Then: Raises ValueError
        """
        with pytest.raises(ValueError, match="ordered"):
            ThresholdConfig(safe=0.7, suspicious=0.3)

    @pytest.mark.unit
    def test_threshold_at_boundary_safe(self) -> None:
        """Score exactly at safe threshold is SAFE."""
        rec = determine_recommendation(THRESHOLD_SAFE, exists=True)
        assert rec == Recommendation.SAFE

    @pytest.mark.unit
    def test_threshold_at_boundary_suspicious(self) -> None:
        """Score exactly at suspicious threshold is SUSPICIOUS."""
        rec = determine_recommendation(THRESHOLD_SUSPICIOUS, exists=True)
        assert rec == Recommendation.SUSPICIOUS


class TestResultAggregation:
    """Tests for aggregate_results function.

    SPEC: S009 - Result aggregation
    """

    @pytest.mark.unit
    def test_aggregate_preserves_all_inputs(self) -> None:
        """
        TEST_ID: T009.01
        SPEC: S009
        INV: INV012

        Given: List of 3 PackageRisk results
        When: aggregate_results is called
        Then: Result contains all 3 packages
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("pkg3", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]
        agg = aggregate_results(results)
        assert agg.total_count == 3
        assert len(agg.packages) == 3

    @pytest.mark.unit
    def test_aggregate_empty_list(self) -> None:
        """
        TEST_ID: T009.02
        SPEC: S009
        INV: INV012

        Given: Empty list
        When: aggregate_results is called
        Then: Returns empty aggregate with SAFE overall
        """
        agg = aggregate_results([])
        assert agg.total_count == 0
        assert agg.overall_risk == Recommendation.SAFE

    @pytest.mark.unit
    def test_aggregate_counts_categories(self) -> None:
        """
        TEST_ID: T009.03
        SPEC: S009

        Given: List with mixed recommendations
        When: aggregate_results is called
        Then: Correctly counts each category
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg3", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("pkg4", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
            PackageRisk("pkg5", "pypi", False, 0.0, (), Recommendation.NOT_FOUND),
        ]
        agg = aggregate_results(results)
        assert agg.safe_count == 2
        assert agg.suspicious_count == 1
        assert agg.high_risk_count == 1
        assert agg.not_found_count == 1

    @pytest.mark.unit
    def test_aggregate_highest_risk(self) -> None:
        """
        TEST_ID: T009.04
        SPEC: S009

        Given: List with mixed risks
        When: aggregate_results is called
        Then: overall_risk reflects highest individual risk
        """
        # Only SUSPICIOUS
        results_sus = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
        ]
        agg = aggregate_results(results_sus)
        assert agg.overall_risk == Recommendation.SUSPICIOUS

        # With HIGH_RISK
        results_high = [
            *results_sus,
            PackageRisk("pkg3", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]
        agg = aggregate_results(results_high)
        assert agg.overall_risk == Recommendation.HIGH_RISK

    @pytest.mark.unit
    def test_aggregate_only_not_found(self) -> None:
        """
        TEST_ID: T009.06
        SPEC: S009

        Given: List with only NOT_FOUND packages
        When: aggregate_results is called
        Then: overall_risk is NOT_FOUND
        """
        results = [
            PackageRisk("pkg1", "pypi", False, 1.0, (), Recommendation.NOT_FOUND),
            PackageRisk("pkg2", "pypi", False, 1.0, (), Recommendation.NOT_FOUND),
        ]
        agg = aggregate_results(results)
        assert agg.overall_risk == Recommendation.NOT_FOUND
        assert agg.not_found_count == 2

    @pytest.mark.unit
    def test_aggregate_not_found_with_safe(self) -> None:
        """
        TEST_ID: T009.07
        SPEC: S009

        Given: List with NOT_FOUND and SAFE packages
        When: aggregate_results is called
        Then: overall_risk is NOT_FOUND (higher priority than SAFE)

        This test covers the NOT_FOUND branch at line 282->274 in scorer.py.
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", False, 1.0, (), Recommendation.NOT_FOUND),
        ]
        agg = aggregate_results(results)
        assert agg.safe_count == 1
        assert agg.not_found_count == 1
        assert agg.overall_risk == Recommendation.NOT_FOUND

    @pytest.mark.unit
    def test_aggregate_not_found_first_then_continue(self) -> None:
        """
        TEST_ID: T009.08
        SPEC: S009

        Given: List with NOT_FOUND package followed by another package
        When: aggregate_results is called
        Then: Loop continues from NOT_FOUND case to next iteration

        This test specifically ensures the loop continuation branch
        from NOT_FOUND case (line 282->274) is exercised.
        """
        results = [
            PackageRisk("pkg1", "pypi", False, 1.0, (), Recommendation.NOT_FOUND),
            PackageRisk("pkg2", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("pkg3", "pypi", True, 0.1, (), Recommendation.SAFE),
        ]
        agg = aggregate_results(results)
        assert agg.not_found_count == 1
        assert agg.suspicious_count == 1
        assert agg.safe_count == 1
        assert agg.overall_risk == Recommendation.SUSPICIOUS

    @pytest.mark.unit
    def test_aggregate_to_dict(self) -> None:
        """
        TEST_ID: T009.05
        SPEC: S009

        Given: Aggregate result
        When: Converting to dict
        Then: Contains summary with counts
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
        ]
        agg = aggregate_results(results)
        d = agg.to_dict()
        assert d["total"] == 1
        assert d["safe"] == 1
        assert d["overall_risk"] == "safe"


class TestMonotonicity:
    """Tests for score monotonicity property.

    SPEC: S007
    INV: INV010
    """

    @pytest.mark.unit
    def test_adding_positive_signal_increases_score(self) -> None:
        """
        TEST_ID: T007.15
        SPEC: S007
        INV: INV010

        Given: Signal set S1
        When: Adding a positive-weight signal to get S2
        Then: score(S2) >= score(S1)
        """
        base = (Signal(SignalType.LOW_DOWNLOADS, 0.3, "Low"),)
        extended = (*base, Signal(SignalType.RECENTLY_CREATED, 0.4, "New"))

        base_score = calculate_risk_score(base)
        extended_score = calculate_risk_score(extended)

        assert extended_score >= base_score

    @pytest.mark.unit
    def test_adding_negative_signal_decreases_score(self) -> None:
        """
        TEST_ID: T007.16
        SPEC: S007
        INV: INV010

        Given: Signal set S1
        When: Adding a negative-weight signal to get S2
        Then: score(S2) <= score(S1)
        """
        base = (Signal(SignalType.LOW_DOWNLOADS, 0.3, "Low"),)
        extended = (*base, Signal(SignalType.POPULAR_PACKAGE, -0.5, "Popular"))

        base_score = calculate_risk_score(base)
        extended_score = calculate_risk_score(extended)

        assert extended_score <= base_score


class TestBuildPackageRisk:
    """Tests for build_package_risk function."""

    @pytest.mark.unit
    def test_build_creates_valid_package_risk(self) -> None:
        """build_package_risk creates a valid PackageRisk."""
        signals = (Signal(SignalType.LOW_DOWNLOADS, 0.3, "Low"),)
        result = build_package_risk(
            name="test-pkg",
            registry="pypi",
            exists=True,
            signals=signals,
            latency_ms=50.0,
        )
        assert result.name == "test-pkg"
        assert result.registry == "pypi"
        assert result.exists is True
        assert 0.0 <= result.risk_score <= 1.0
        assert result.signals == signals
        assert result.latency_ms == 50.0

    @pytest.mark.unit
    def test_build_with_custom_thresholds(self) -> None:
        """build_package_risk uses custom thresholds."""
        custom = ThresholdConfig(safe=0.1, suspicious=0.2)
        # Score will be ~0.38 for no signals, which is HIGH_RISK with custom thresholds
        result = build_package_risk(
            name="test-pkg",
            registry="pypi",
            exists=True,
            signals=(),
            thresholds=custom,
        )
        assert result.recommendation == Recommendation.HIGH_RISK


class TestThresholdConfig:
    """Tests for ThresholdConfig dataclass."""

    @pytest.mark.unit
    def test_default_values(self) -> None:
        """Default values match constants."""
        config = ThresholdConfig()
        assert config.safe == THRESHOLD_SAFE
        assert config.suspicious == THRESHOLD_SUSPICIOUS

    @pytest.mark.unit
    def test_custom_valid_values(self) -> None:
        """Valid custom values are accepted."""
        config = ThresholdConfig(safe=0.2, suspicious=0.7)
        assert config.safe == 0.2
        assert config.suspicious == 0.7

    @pytest.mark.unit
    def test_safe_out_of_range_high(self) -> None:
        """Safe threshold > 1.0 is rejected (caught by ordering first)."""
        with pytest.raises(ValueError):
            ThresholdConfig(safe=1.5, suspicious=0.8)

    @pytest.mark.unit
    def test_safe_out_of_range_low(self) -> None:
        """Safe threshold < 0.0 is rejected."""
        with pytest.raises(ValueError, match="Safe threshold must be"):
            ThresholdConfig(safe=-0.1, suspicious=0.5)

    @pytest.mark.unit
    def test_suspicious_out_of_range_high(self) -> None:
        """Suspicious threshold > 1.0 is rejected."""
        with pytest.raises(ValueError, match="Suspicious threshold must be"):
            ThresholdConfig(safe=0.2, suspicious=1.5)

    @pytest.mark.unit
    def test_suspicious_out_of_range_low(self) -> None:
        """Suspicious threshold < 0.0 is rejected (caught by ordering)."""
        with pytest.raises(ValueError):
            ThresholdConfig(safe=0.2, suspicious=-0.1)

    @pytest.mark.unit
    def test_frozen(self) -> None:
        """ThresholdConfig is frozen."""
        config = ThresholdConfig()
        with pytest.raises(AttributeError):
            config.safe = 0.5  # type: ignore[misc]


class TestAggregateResult:
    """Tests for AggregateResult dataclass."""

    @pytest.mark.unit
    def test_total_count_property(self) -> None:
        """total_count property works correctly."""
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
        ]
        agg = aggregate_results(results)
        assert agg.total_count == 2

    @pytest.mark.unit
    def test_frozen(self) -> None:
        """AggregateResult is frozen."""
        agg = aggregate_results([])
        with pytest.raises(AttributeError):
            agg.safe_count = 10  # type: ignore[misc]
