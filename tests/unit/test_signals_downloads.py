"""
SPEC: S065 - Download Inflation Detection
TEST_IDs: T065.01-T065.06
INVARIANTS: INV065, INV066, INV067

Tests for download inflation signal detection.
"""

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from phantom_guard.core.signals.downloads import (
    DOWNLOAD_INFLATION_WEIGHT,
    DownloadInflationSignal,
    calculate_age_adjusted_threshold,
    detect_download_inflation,
)


class TestDownloadInflationDetection:
    """Unit tests for download inflation detection (S065)."""

    # =========================================================================
    # T065.01: Legitimate viral package
    # =========================================================================
    def test_legitimate_viral_package_no_signal(self):
        """
        SPEC: S065
        TEST_ID: T065.01
        INV_ID: INV065
        EC_ID: EC420

        Given: Package with 1M downloads AND 1000 dependents
        When: detect_download_inflation is called
        Then: Returns None (legitimate viral package)
        """
        # Arrange - high downloads with high dependents = legitimate
        package = "popular-package"
        registry = "pypi"
        metadata: dict[str, Any] = {
            "name": package,
            "downloads": 1_000_000,
            "dependents_count": 1000,
            "age_days": 365,  # 1 year old
        }

        # Act
        result = detect_download_inflation(package, metadata, registry)

        # Assert - legitimate viral package, no signal
        assert result is None

    # =========================================================================
    # T065.02: Inflated downloads detected
    # =========================================================================
    def test_inflated_downloads_detected(self):
        """
        SPEC: S065
        TEST_ID: T065.02
        INV_ID: INV065
        EC_ID: EC421

        Given: Package with 100K downloads AND 0 dependents
        When: detect_download_inflation is called
        Then: Returns DownloadInflationSignal with weight 0.30
        """
        # Arrange - high downloads with zero dependents = suspicious
        package = "suspicious-package"
        registry = "npm"
        metadata: dict[str, Any] = {
            "name": package,
            "downloads": 100_000,
            "dependents_count": 0,
            "age_days": 60,  # 2 months old
        }

        # Act
        result = detect_download_inflation(package, metadata, registry)

        # Assert - inflation detected
        assert result is not None
        assert isinstance(result, DownloadInflationSignal)
        assert result.dependents_count == 0
        assert result.confidence == DOWNLOAD_INFLATION_WEIGHT

    # =========================================================================
    # T065.03: API failure skips signal
    # =========================================================================
    def test_api_failure_skip_signal(self):
        """
        SPEC: S065
        TEST_ID: T065.03
        INV_ID: INV066
        EC_ID: EC425

        Given: Missing/invalid metadata (simulates API failure)
        When: detect_download_inflation is called
        Then: Returns None (graceful degradation)
        """
        # Arrange - invalid metadata to simulate API failure
        package = "some-package"
        registry = "npm"
        metadata: dict[str, Any] = None  # type: ignore[assignment]

        # Act - should not raise exception (INV066)
        result = detect_download_inflation(package, metadata, registry)

        # Assert - graceful degradation
        assert result is None

    # =========================================================================
    # T065.04: Missing dependents data handled
    # =========================================================================
    def test_missing_dependents_data_skips(self):
        """
        SPEC: S065
        TEST_ID: T065.04
        INV_ID: INV067
        EC_ID: EC426

        Given: Package with no dependents_count in metadata
        When: detect_download_inflation is called
        Then: Returns None (graceful skip)
        """
        # Arrange - missing dependents data
        package = "some-package"
        registry = "pypi"
        metadata: dict[str, Any] = {
            "name": package,
            "downloads": 50_000,
            # dependents_count is missing
            "age_days": 90,
        }

        # Act
        result = detect_download_inflation(package, metadata, registry)

        # Assert - skipped due to missing data
        assert result is None

    # =========================================================================
    # T065.05: Threshold boundary
    # =========================================================================
    def test_threshold_boundary_no_signal(self):
        """
        SPEC: S065
        TEST_ID: T065.05
        EC_ID: EC432

        Given: Package with legitimate downloads-to-dependents ratio
        When: detect_download_inflation is called
        Then: Returns None (within threshold)
        """
        # Arrange - downloads proportional to dependents
        package = "normal-package"
        registry = "pypi"
        metadata: dict[str, Any] = {
            "name": package,
            "downloads": 100_000,
            "dependents_count": 50,  # reasonable ratio
            "age_days": 365,
        }

        # Act
        result = detect_download_inflation(package, metadata, registry)

        # Assert - within threshold, no signal
        assert result is None

    # =========================================================================
    # T065.06: Age-adjusted calculation property
    # =========================================================================
    @pytest.mark.property
    @given(age_days=st.integers(min_value=1, max_value=3650))
    def test_age_adjusted_calculation_property(self, age_days: int) -> None:
        """
        SPEC: S065
        TEST_ID: T065.06
        INV_ID: INV065

        Property: Age-adjusted threshold is always positive and finite
        for packages >= MIN_AGE_DAYS.
        """
        # Act
        threshold = calculate_age_adjusted_threshold(age_days)

        # Assert - threshold is valid
        if age_days < 30:
            # Too new = infinite threshold
            assert threshold == float("inf")
        else:
            # Valid threshold
            assert threshold > 0
            assert threshold < float("inf")


class TestDownloadInflationEdgeCases:
    """Edge case tests for download inflation (EC420-EC435)."""

    @pytest.mark.skip(reason="Stub - implement with S065")
    def test_new_package_no_signal(self):
        """
        EC_ID: EC422
        Given: Package with 100 downloads, 7 days old
        When: detect_download_inflation is called
        Then: Returns None (too new for reliable signal)
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S065")
    def test_zero_dependents_with_high_downloads(self):
        """
        EC_ID: EC424
        Given: Package with 50K/day downloads, 0 dependents
        When: detect_download_inflation is called
        Then: Signal triggered
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S065")
    def test_libraries_io_unavailable_skip(self):
        """
        EC_ID: EC427
        Given: libraries.io API fails
        When: detect_download_inflation is called
        Then: Returns None (skip signal gracefully)
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S065")
    def test_very_old_package_no_signal(self):
        """
        EC_ID: EC429
        Given: Package 5 years old with low downloads
        When: detect_download_inflation is called
        Then: Returns None
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S065")
    def test_missing_download_data_skip(self):
        """
        EC_ID: EC433
        Given: No download stats available
        When: detect_download_inflation is called
        Then: Returns None (skip signal)
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S065")
    @pytest.mark.integration
    def test_crates_io_reverse_deps(self):
        """
        EC_ID: EC434
        Given: crates.io package
        When: detect_download_inflation is called
        Then: Uses native reverse_dependencies API
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S065")
    @pytest.mark.integration
    def test_npm_dependents_search(self):
        """
        EC_ID: EC435
        Given: npm package
        When: detect_download_inflation is called
        Then: Uses correct search API query
        """
        pass
