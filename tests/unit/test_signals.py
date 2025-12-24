# SPEC: S004 - Signal Extraction Tests
# Gate 3: Test Design - W1.2 Implementation Tests
"""
Unit tests for signal extraction module.

SPEC_IDs: S004
TEST_IDs: T004.*
INVARIANTS: INV007 (weight bounds), INV008 (purity)
EDGE_CASES: EC040-EC055
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from phantom_guard.core import (
    AGE_THRESHOLD_NEW_DAYS,
    DOWNLOAD_THRESHOLD_LOW,
    DOWNLOAD_THRESHOLD_POPULAR,
    RELEASE_THRESHOLD_FEW,
    PackageMetadata,
    Signal,
    SignalType,
    calculate_total_weight,
    extract_signals,
    get_signal_by_type,
    has_signal_type,
    merge_signals,
)

# =============================================================================
# TEST FIXTURES
# =============================================================================


def make_metadata(
    name: str = "test-package",
    exists: bool = True,
    age_days: int | None = 100,
    downloads: int | None = 50000,
    has_repo: bool = True,
    maintainers: int | None = 2,
    releases: int | None = 10,
    description: str | None = "A test package for testing purposes",
) -> PackageMetadata:
    """Helper to create PackageMetadata with sensible defaults."""
    created_at = None
    if age_days is not None:
        created_at = datetime.now(tz=UTC) - timedelta(days=age_days)

    return PackageMetadata(
        name=name,
        exists=exists,
        registry="pypi",
        created_at=created_at,
        downloads_last_month=downloads,
        repository_url="https://github.com/test/test" if has_repo else None,
        maintainer_count=maintainers,
        release_count=releases,
        description=description,
    )


# =============================================================================
# PURITY TESTS (INV008)
# =============================================================================


class TestSignalExtractionPurity:
    """Tests for extract_signals purity (INV008)."""

    @pytest.mark.unit
    def test_extract_signals_is_deterministic(self) -> None:
        """
        TEST_ID: T004.01
        SPEC: S004
        INV: INV008

        Given: Same metadata input
        When: extract_signals is called multiple times
        Then: Returns identical results
        """
        metadata = make_metadata()
        result1 = extract_signals(metadata)
        result2 = extract_signals(metadata)
        result3 = extract_signals(metadata)

        assert result1 == result2 == result3

    @pytest.mark.unit
    def test_extract_signals_no_side_effects(self) -> None:
        """
        TEST_ID: T004.02
        SPEC: S004
        INV: INV008

        Given: Metadata object
        When: extract_signals is called
        Then: Original metadata is unchanged (frozen dataclass)
        """
        metadata = make_metadata(downloads=500)
        original_downloads = metadata.downloads_last_month

        _ = extract_signals(metadata)

        # Metadata is frozen, so this should be unchanged
        assert metadata.downloads_last_month == original_downloads

    @pytest.mark.unit
    def test_extract_signals_returns_tuple(self) -> None:
        """
        TEST_ID: T004.03
        SPEC: S004
        INV: INV008

        extract_signals returns an immutable tuple, not a list.
        """
        metadata = make_metadata()
        result = extract_signals(metadata)

        assert isinstance(result, tuple)


# =============================================================================
# SIGNAL DETECTION TESTS
# =============================================================================


class TestSignalDetection:
    """Tests for individual signal detection."""

    @pytest.mark.unit
    def test_popular_package_positive_signal(self) -> None:
        """
        TEST_ID: T004.04
        SPEC: S004
        EC: EC043

        Given: Metadata for popular package (>1M downloads)
        When: extract_signals is called
        Then: Returns POPULAR_PACKAGE signal with negative weight
        """
        metadata = make_metadata(downloads=2_000_000)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.POPULAR_PACKAGE)
        popular_signal = get_signal_by_type(signals, SignalType.POPULAR_PACKAGE)
        assert popular_signal is not None
        assert popular_signal.weight < 0  # Negative = reduces risk

    @pytest.mark.unit
    def test_recently_created_signal(self) -> None:
        """
        TEST_ID: T004.05
        SPEC: S004

        Given: Metadata with age < 30 days
        When: extract_signals is called
        Then: Returns signal containing RECENTLY_CREATED
        """
        metadata = make_metadata(age_days=15)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.RECENTLY_CREATED)
        signal = get_signal_by_type(signals, SignalType.RECENTLY_CREATED)
        assert signal is not None
        assert signal.metadata.get("age_days") == 15

    @pytest.mark.unit
    def test_low_downloads_signal(self) -> None:
        """
        TEST_ID: T004.06
        SPEC: S004
        EC: EC025

        Given: Metadata with downloads < 1000
        When: extract_signals is called
        Then: Returns signal containing LOW_DOWNLOADS
        """
        metadata = make_metadata(downloads=500)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.LOW_DOWNLOADS)
        signal = get_signal_by_type(signals, SignalType.LOW_DOWNLOADS)
        assert signal is not None
        assert signal.metadata.get("downloads") == 500

    @pytest.mark.unit
    def test_no_repository_signal(self) -> None:
        """
        TEST_ID: T004.07
        SPEC: S004

        Given: Metadata with no repository URL
        When: extract_signals is called
        Then: Returns signal containing NO_REPOSITORY
        """
        metadata = make_metadata(has_repo=False)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.NO_REPOSITORY)

    @pytest.mark.unit
    def test_no_maintainer_signal(self) -> None:
        """
        TEST_ID: T004.08
        SPEC: S004

        Given: Metadata with no maintainers
        When: extract_signals is called
        Then: Returns signal containing NO_MAINTAINER
        """
        metadata = make_metadata(maintainers=0)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.NO_MAINTAINER)

    @pytest.mark.unit
    def test_few_releases_signal(self) -> None:
        """
        TEST_ID: T004.09
        SPEC: S004

        Given: Metadata with releases < 3
        When: extract_signals is called
        Then: Returns signal containing FEW_RELEASES
        """
        metadata = make_metadata(releases=2)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.FEW_RELEASES)
        signal = get_signal_by_type(signals, SignalType.FEW_RELEASES)
        assert signal is not None
        assert signal.metadata.get("release_count") == 2

    @pytest.mark.unit
    def test_short_description_signal(self) -> None:
        """
        TEST_ID: T004.10
        SPEC: S004

        Given: Metadata with description < 10 chars
        When: extract_signals is called
        Then: Returns signal containing SHORT_DESCRIPTION
        """
        metadata = make_metadata(description="Hi")
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.SHORT_DESCRIPTION)

    @pytest.mark.unit
    def test_long_history_signal(self) -> None:
        """
        TEST_ID: T004.11
        SPEC: S004

        Given: Package older than 1 year
        When: extract_signals is called
        Then: Returns LONG_HISTORY signal with negative weight
        """
        metadata = make_metadata(age_days=400)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.LONG_HISTORY)
        signal = get_signal_by_type(signals, SignalType.LONG_HISTORY)
        assert signal is not None
        assert signal.weight < 0  # Negative = reduces risk

    @pytest.mark.unit
    def test_not_found_signal(self) -> None:
        """
        TEST_ID: T004.12
        SPEC: S004

        Given: Package that doesn't exist
        When: extract_signals is called
        Then: Returns only NOT_FOUND signal
        """
        metadata = make_metadata(exists=False)
        signals = extract_signals(metadata)

        assert len(signals) == 1
        assert signals[0].type == SignalType.NOT_FOUND


# =============================================================================
# COMPOSITE SIGNAL TESTS
# =============================================================================


class TestCompositeSignals:
    """Tests for multiple signals working together."""

    @pytest.mark.unit
    def test_all_safe_signals(self) -> None:
        """
        TEST_ID: T004.13
        SPEC: S004
        EC: EC040

        Given: Metadata with all safe indicators
        When: extract_signals is called
        Then: Returns signals with net negative or zero weight
        """
        metadata = make_metadata(
            age_days=500,  # Old package
            downloads=2_000_000,  # Very popular
            has_repo=True,
            maintainers=5,
            releases=50,
            description="A comprehensive and well-documented package",
        )
        signals = extract_signals(metadata)
        total_weight = calculate_total_weight(signals)

        # Safe packages should have negative or near-zero total weight
        assert total_weight <= 0

    @pytest.mark.unit
    def test_all_risk_signals(self) -> None:
        """
        TEST_ID: T004.14
        SPEC: S004
        EC: EC041

        Given: Metadata with all risk indicators
        When: extract_signals is called
        Then: Returns multiple risk signals with high total weight
        """
        metadata = make_metadata(
            age_days=5,  # Very new
            downloads=50,  # Very low
            has_repo=False,  # No repo
            maintainers=0,  # No maintainers
            releases=1,  # Few releases
            description="",  # Empty description
        )
        signals = extract_signals(metadata)
        total_weight = calculate_total_weight(signals)

        # Risky packages should have high positive total weight
        assert total_weight > 1.0
        assert len(signals) >= 5  # Multiple risk indicators

    @pytest.mark.unit
    def test_new_but_legitimate_package(self) -> None:
        """
        TEST_ID: T004.15
        SPEC: S004
        EC: EC045

        Given: New package (age=7d) with 10k downloads and repo
        When: extract_signals is called
        Then: Only RECENTLY_CREATED signal, not LOW_DOWNLOADS
        """
        metadata = make_metadata(
            age_days=7,  # New
            downloads=10000,  # Not low
            has_repo=True,
            maintainers=1,
            releases=3,  # Not few
            description="A legitimate new package with good documentation",
        )
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.RECENTLY_CREATED)
        assert not has_signal_type(signals, SignalType.LOW_DOWNLOADS)
        assert not has_signal_type(signals, SignalType.NO_REPOSITORY)


# =============================================================================
# BOUNDARY CONDITION TESTS
# =============================================================================


class TestBoundaryConditions:
    """Tests for threshold boundary conditions."""

    @pytest.mark.unit
    def test_exactly_30_days_not_new(self) -> None:
        """
        TEST_ID: T004.16
        SPEC: S004
        EC: EC051

        Given: Metadata with age = exactly 30 days
        When: extract_signals is called
        Then: Does NOT return RECENTLY_CREATED signal
        """
        metadata = make_metadata(age_days=AGE_THRESHOLD_NEW_DAYS)
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.RECENTLY_CREATED)

    @pytest.mark.unit
    def test_29_days_is_new(self) -> None:
        """
        TEST_ID: T004.17
        SPEC: S004
        EC: EC051

        Given: Metadata with age = 29 days
        When: extract_signals is called
        Then: Returns RECENTLY_CREATED signal
        """
        metadata = make_metadata(age_days=AGE_THRESHOLD_NEW_DAYS - 1)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.RECENTLY_CREATED)

    @pytest.mark.unit
    def test_exactly_1000_downloads_not_low(self) -> None:
        """
        TEST_ID: T004.18
        SPEC: S004
        EC: EC052

        Given: Metadata with downloads = 1000
        When: extract_signals is called
        Then: Does NOT return LOW_DOWNLOADS signal
        """
        metadata = make_metadata(downloads=DOWNLOAD_THRESHOLD_LOW)
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.LOW_DOWNLOADS)

    @pytest.mark.unit
    def test_999_downloads_is_low(self) -> None:
        """
        TEST_ID: T004.19
        SPEC: S004
        EC: EC052

        Given: Metadata with downloads = 999
        When: extract_signals is called
        Then: Returns LOW_DOWNLOADS signal
        """
        metadata = make_metadata(downloads=DOWNLOAD_THRESHOLD_LOW - 1)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.LOW_DOWNLOADS)

    @pytest.mark.unit
    def test_exactly_3_releases_not_few(self) -> None:
        """
        TEST_ID: T004.20
        SPEC: S004
        EC: EC053

        Given: Metadata with releases = 3
        When: extract_signals is called
        Then: Does NOT return FEW_RELEASES signal
        """
        metadata = make_metadata(releases=RELEASE_THRESHOLD_FEW)
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.FEW_RELEASES)

    @pytest.mark.unit
    def test_2_releases_is_few(self) -> None:
        """
        TEST_ID: T004.21
        SPEC: S004
        EC: EC053

        Given: Metadata with releases = 2
        When: extract_signals is called
        Then: Returns FEW_RELEASES signal
        """
        metadata = make_metadata(releases=RELEASE_THRESHOLD_FEW - 1)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.FEW_RELEASES)

    @pytest.mark.unit
    def test_exactly_10_char_description_not_short(self) -> None:
        """
        TEST_ID: T004.22
        SPEC: S004

        Given: Description of exactly 10 characters
        When: extract_signals is called
        Then: Does NOT return SHORT_DESCRIPTION signal
        """
        metadata = make_metadata(description="1234567890")  # Exactly 10 chars
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.SHORT_DESCRIPTION)

    @pytest.mark.unit
    def test_9_char_description_is_short(self) -> None:
        """
        TEST_ID: T004.23
        SPEC: S004

        Given: Description of 9 characters
        When: extract_signals is called
        Then: Returns SHORT_DESCRIPTION signal
        """
        metadata = make_metadata(description="123456789")  # 9 chars
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.SHORT_DESCRIPTION)

    @pytest.mark.unit
    def test_exactly_1m_downloads_is_popular(self) -> None:
        """
        TEST_ID: T004.24
        SPEC: S004

        Given: Downloads = exactly 1,000,000
        When: extract_signals is called
        Then: Returns POPULAR_PACKAGE signal
        """
        metadata = make_metadata(downloads=DOWNLOAD_THRESHOLD_POPULAR)
        signals = extract_signals(metadata)

        assert has_signal_type(signals, SignalType.POPULAR_PACKAGE)


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestHelperFunctions:
    """Tests for signal helper functions."""

    @pytest.mark.unit
    def test_merge_signals_removes_duplicates(self) -> None:
        """merge_signals keeps only first occurrence of each type."""
        signal1 = Signal(
            type=SignalType.LOW_DOWNLOADS,
            weight=0.3,
            message="First",
        )
        signal2 = Signal(
            type=SignalType.LOW_DOWNLOADS,
            weight=0.5,
            message="Second (should be ignored)",
        )
        signal3 = Signal(
            type=SignalType.NO_REPOSITORY,
            weight=0.2,
            message="Different type",
        )

        merged = merge_signals((signal1,), (signal2, signal3))

        assert len(merged) == 2
        assert merged[0].message == "First"  # First LOW_DOWNLOADS kept
        assert merged[1].type == SignalType.NO_REPOSITORY

    @pytest.mark.unit
    def test_merge_signals_empty_groups(self) -> None:
        """merge_signals handles empty groups."""
        signal = Signal(type=SignalType.LOW_DOWNLOADS, weight=0.3, message="Test")

        merged = merge_signals((), (signal,), ())

        assert len(merged) == 1
        assert merged[0] == signal

    @pytest.mark.unit
    def test_has_signal_type_true(self) -> None:
        """has_signal_type returns True when signal present."""
        signals = (Signal(type=SignalType.LOW_DOWNLOADS, weight=0.3, message="Test"),)

        assert has_signal_type(signals, SignalType.LOW_DOWNLOADS) is True

    @pytest.mark.unit
    def test_has_signal_type_false(self) -> None:
        """has_signal_type returns False when signal absent."""
        signals = (Signal(type=SignalType.LOW_DOWNLOADS, weight=0.3, message="Test"),)

        assert has_signal_type(signals, SignalType.NO_REPOSITORY) is False

    @pytest.mark.unit
    def test_get_signal_by_type_found(self) -> None:
        """get_signal_by_type returns signal when present."""
        signal = Signal(type=SignalType.LOW_DOWNLOADS, weight=0.3, message="Test")
        signals = (signal,)

        result = get_signal_by_type(signals, SignalType.LOW_DOWNLOADS)

        assert result == signal

    @pytest.mark.unit
    def test_get_signal_by_type_not_found(self) -> None:
        """get_signal_by_type returns None when absent."""
        signals = (Signal(type=SignalType.LOW_DOWNLOADS, weight=0.3, message="Test"),)

        result = get_signal_by_type(signals, SignalType.NO_REPOSITORY)

        assert result is None

    @pytest.mark.unit
    def test_calculate_total_weight(self) -> None:
        """calculate_total_weight sums all weights."""
        signals = (
            Signal(type=SignalType.LOW_DOWNLOADS, weight=0.3, message="Test1"),
            Signal(type=SignalType.NO_REPOSITORY, weight=0.2, message="Test2"),
            Signal(type=SignalType.POPULAR_PACKAGE, weight=-0.5, message="Test3"),
        )

        total = calculate_total_weight(signals)

        assert total == pytest.approx(0.0)  # 0.3 + 0.2 - 0.5 = 0.0


# =============================================================================
# NONE VALUE HANDLING TESTS
# =============================================================================


class TestNoneValueHandling:
    """Tests for handling None/missing metadata values."""

    @pytest.mark.unit
    def test_none_downloads_no_signal(self) -> None:
        """When downloads is None, no download-related signal is generated."""
        metadata = make_metadata(downloads=None)
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.LOW_DOWNLOADS)
        assert not has_signal_type(signals, SignalType.POPULAR_PACKAGE)

    @pytest.mark.unit
    def test_none_age_no_signal(self) -> None:
        """When created_at is None, no age-related signal is generated."""
        metadata = make_metadata(age_days=None)
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.RECENTLY_CREATED)
        assert not has_signal_type(signals, SignalType.LONG_HISTORY)

    @pytest.mark.unit
    def test_none_maintainers_no_signal(self) -> None:
        """When maintainer_count is None, no maintainer signal is generated."""
        metadata = make_metadata(maintainers=None)
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.NO_MAINTAINER)

    @pytest.mark.unit
    def test_none_releases_no_signal(self) -> None:
        """When release_count is None, no release signal is generated."""
        metadata = make_metadata(releases=None)
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.FEW_RELEASES)

    @pytest.mark.unit
    def test_none_description_no_signal(self) -> None:
        """When description is None, no description signal is generated."""
        metadata = make_metadata(description=None)
        signals = extract_signals(metadata)

        assert not has_signal_type(signals, SignalType.SHORT_DESCRIPTION)
