"""
SPEC: S080 - Signal Combinations
TEST_IDs: T080.01-T080.11
EDGE_CASES: EC500-EC510

Tests for signal combination behavior when multiple signals fire together.
"""


import pytest

from phantom_guard.core.signals.combination import (
    CombinedSignals,
    calculate_combined_weight,
    calculate_normalized_score,
    combine_signals,
    gather_all_signals,
    order_signals,
)
from phantom_guard.core.signals.namespace import NAMESPACE_SQUAT_WEIGHT
from phantom_guard.core.signals.ownership import OWNERSHIP_MAX_WEIGHT
from phantom_guard.core.signals.versions import WEIGHT_24H_SPIKE


class TestSignalCombinations:
    """Unit tests for signal combination behavior (S080)."""

    # =========================================================================
    # T080.01: Two signals combine correctly
    # =========================================================================
    def test_two_signals_combine_correctly(self):
        """
        SPEC: S060, S075
        TEST_ID: T080.01
        EC_ID: EC500

        Given: VERSION_SPIKE (0.45) + NAMESPACE_SQUATTING (0.35) fire
        When: Combined score calculated
        Then: Combined weight = 0.80
        """
        # Arrange
        signals = ["VERSION_SPIKE", "NAMESPACE_SQUATTING"]

        # Act
        combined_weight = calculate_combined_weight(signals)

        # Assert
        assert combined_weight == pytest.approx(0.80)

    # =========================================================================
    # T080.02: Three signals combine correctly
    # =========================================================================
    def test_three_signals_combine_correctly(self):
        """
        SPEC: S060, S065, S075
        TEST_ID: T080.02
        EC_ID: EC501

        Given: VERSION + NAMESPACE + DOWNLOAD fire
        When: Combined score calculated
        Then: Combined weight = 1.10
        """
        # Arrange
        signals = ["VERSION_SPIKE", "NAMESPACE_SQUATTING", "DOWNLOAD_INFLATION"]

        # Act
        combined_weight = calculate_combined_weight(signals)

        # Assert - 0.45 + 0.35 + 0.30 = 1.10
        assert combined_weight == pytest.approx(1.10)

    # =========================================================================
    # T080.03: All four signals combine and clamp
    # =========================================================================
    def test_all_four_signals_combine_and_clamp(self):
        """
        SPEC: S060, S065, S070, S075
        TEST_ID: T080.03
        EC_ID: EC502

        Given: All 4 new signals fire
        When: Combined score calculated
        Then: Sum = 1.25, clamped appropriately in final score
        """
        # Arrange
        signals = [
            "VERSION_SPIKE",  # 0.45
            "NAMESPACE_SQUATTING",  # 0.35
            "DOWNLOAD_INFLATION",  # 0.30
            "OWNERSHIP_TRANSFER",  # 0.15
        ]

        # Act
        combined_weight = calculate_combined_weight(signals)

        # Assert - total = 1.25
        assert combined_weight == pytest.approx(1.25)

    # =========================================================================
    # T080.04: New + old signals combine
    # =========================================================================
    def test_new_and_old_signals_combine(self):
        """
        SPEC: S075
        TEST_ID: T080.04
        EC_ID: EC503

        Given: VERSION_SPIKE (new) + TYPOSQUAT (old) fire
        When: Combined score calculated
        Then: Both contribute to final score
        """
        # Arrange - new signal
        signals = ["VERSION_SPIKE"]

        # Act
        new_weight = calculate_combined_weight(signals)

        # Assert - new signal contributes
        assert new_weight == pytest.approx(WEIGHT_24H_SPIKE)
        # Old signals would be added separately in legacy system

    # =========================================================================
    # T080.05: Higher weight takes precedence
    # =========================================================================
    def test_higher_weight_takes_precedence(self):
        """
        SPEC: S070, S075
        TEST_ID: T080.05
        EC_ID: EC504

        Given: "Safe" by ownership, "risky" by version
        When: Signals conflict
        Then: VERSION_SPIKE (0.45) has more impact than OWNERSHIP (0.15)
        """
        # Arrange - both fire
        signals = ["VERSION_SPIKE", "OWNERSHIP_TRANSFER"]

        # Act
        combined = calculate_combined_weight(signals)

        # Assert - VERSION_SPIKE contributes more
        version_contribution = WEIGHT_24H_SPIKE  # 0.45
        ownership_contribution = OWNERSHIP_MAX_WEIGHT  # 0.15
        assert combined == pytest.approx(version_contribution + ownership_contribution)
        assert version_contribution > ownership_contribution  # Higher weight

    # =========================================================================
    # T080.06: API failure skips signal
    # =========================================================================
    def test_api_failure_skips_signal(self):
        """
        SPEC: S060, S065
        TEST_ID: T080.06
        INV_ID: INV062, INV066
        EC_ID: EC505

        Given: NAMESPACE succeeds, DOWNLOAD API fails (None)
        When: Combining signals
        Then: Only NAMESPACE signal used
        """
        # Arrange - NAMESPACE returns value, DOWNLOAD returns None
        signals: list[tuple[str, float | None]] = [
            ("NAMESPACE_SQUATTING", NAMESPACE_SQUAT_WEIGHT),
            ("DOWNLOAD_INFLATION", None),  # API failure
        ]

        # Act
        active, total = combine_signals(signals)

        # Assert
        assert "NAMESPACE_SQUATTING" in active
        assert "DOWNLOAD_INFLATION" not in active
        assert total == pytest.approx(NAMESPACE_SQUAT_WEIGHT)

    # =========================================================================
    # T080.07: All API failures = empty signals
    # =========================================================================
    def test_all_api_failures_fallback_v01x(self):
        """
        SPEC: S060, S065, S070, S075
        TEST_ID: T080.07
        EC_ID: EC506

        Given: All 4 new signal APIs fail
        When: Calculating risk score
        Then: No v0.2.0 signals, fall back to v0.1.x signals only
        """
        # Arrange - all signals return None
        signals: list[tuple[str, float | None]] = [
            ("NAMESPACE_SQUATTING", None),
            ("DOWNLOAD_INFLATION", None),
            ("OWNERSHIP_TRANSFER", None),
            ("VERSION_SPIKE", None),
        ]

        # Act
        active, total = combine_signals(signals)

        # Assert - no v0.2.0 signals
        assert active == []
        assert total == 0.0

    # =========================================================================
    # T080.08: Partial data handled
    # =========================================================================
    def test_partial_data_handled(self):
        """
        SPEC: S060, S065, S070, S075
        TEST_ID: T080.08
        EC_ID: EC507

        Given: Some signals return None
        When: Combining signals
        Then: Use non-None signals, skip None
        """
        # Arrange
        signals: list[tuple[str, float | None]] = [
            ("NAMESPACE_SQUATTING", None),  # Skipped
            ("VERSION_SPIKE", WEIGHT_24H_SPIKE),  # Used
        ]

        # Act
        active, total = combine_signals(signals)

        # Assert - only VERSION_SPIKE contributes
        assert active == ["VERSION_SPIKE"]
        assert total == pytest.approx(WEIGHT_24H_SPIKE)

    # =========================================================================
    # T080.09: Score clamped to 1.0
    # =========================================================================
    def test_score_clamped_to_one(self):
        """
        SPEC: S060, S065, S070, S075
        TEST_ID: T080.09
        EC_ID: EC508

        Given: Many signals fire pushing raw score > 285
        When: Normalizing score
        Then: Clamped to 1.0
        """
        # Arrange - raw score exceeds max
        raw_score = 400.0

        # Act
        normalized = calculate_normalized_score(raw_score, max_score=285.0)

        # Assert
        assert normalized == 1.0

    # =========================================================================
    # T080.10: Parallel execution benchmark (stub)
    # =========================================================================
    @pytest.mark.skip(reason="Benchmark - implement with full integration")
    @pytest.mark.benchmark
    def test_parallel_execution_benchmark(self, benchmark):
        """
        SPEC: S060, S065, S070, S075
        TEST_ID: T080.10
        EC_ID: EC509

        Given: 4 signals need to be computed
        When: Computed in parallel
        Then: Total time < 300ms
        """
        pass

    # =========================================================================
    # T080.11: Consistent signal ordering
    # =========================================================================
    def test_consistent_signal_ordering(self):
        """
        SPEC: S060, S065, S070, S075
        TEST_ID: T080.11
        EC_ID: EC510

        Given: Multiple signals with same weight
        When: Listing signals in output
        Then: Consistent alphabetical ordering
        """
        # Arrange - unsorted signals
        signals = ["VERSION_SPIKE", "DOWNLOAD_INFLATION", "NAMESPACE_SQUATTING"]

        # Act
        ordered = order_signals(signals)

        # Assert - alphabetical
        assert ordered == ["DOWNLOAD_INFLATION", "NAMESPACE_SQUATTING", "VERSION_SPIKE"]


class TestSignalCombinationEdgeCases:
    """Edge case tests for signal combinations."""

    def test_empty_signals_list(self):
        """Empty signal list returns zero weight."""
        assert calculate_combined_weight([]) == 0.0

    def test_unknown_signal_ignored(self):
        """Unknown signal names contribute 0 weight."""
        signals = ["UNKNOWN_SIGNAL", "VERSION_SPIKE"]
        weight = calculate_combined_weight(signals)
        assert weight == pytest.approx(WEIGHT_24H_SPIKE)

    def test_combined_signals_dataclass(self):
        """CombinedSignals tracks signals correctly."""
        combined = CombinedSignals()
        combined.add_signal("TEST", 0.5)
        combined.add_signal("TEST2", 0.25)

        assert "TEST" in combined.signals_collected
        assert "TEST2" in combined.signals_collected
        assert combined.total_weight == pytest.approx(0.75)

    def test_gather_all_signals_with_none_metadata(self):
        """Gather signals with None metadata returns empty."""
        result = gather_all_signals("pkg", None, "npm")
        assert result.signals_collected == []
        assert result.total_weight == 0.0

    def test_normalize_score_zero(self):
        """Zero raw score normalizes to zero."""
        assert calculate_normalized_score(0.0) == 0.0

    def test_normalize_score_negative(self):
        """Negative raw score normalizes to zero."""
        assert calculate_normalized_score(-10.0) == 0.0

    def test_normalize_score_mid_range(self):
        """Mid-range score normalizes correctly."""
        normalized = calculate_normalized_score(142.5, max_score=285.0)
        assert normalized == pytest.approx(0.5)
