"""
SPEC: S070 - Ownership Transfer Detection
TEST_IDs: T070.01-T070.05
INVARIANTS: INV070, INV071, INV072

Tests for ownership transfer signal detection.
"""

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from phantom_guard.core.signals.ownership import (
    OWNERSHIP_MAX_WEIGHT,
    OwnershipSignal,
    detect_ownership_transfer,
)


class TestOwnershipTransferDetection:
    """Unit tests for ownership transfer detection (S070)."""

    # =========================================================================
    # T070.01: Missing data defaults to safe
    # =========================================================================
    def test_missing_data_defaults_safe(self):
        """
        SPEC: S070
        TEST_ID: T070.01
        INV_ID: INV070
        EC_ID: EC443

        Given: Package with no maintainer info (field missing)
        When: detect_ownership_transfer is called
        Then: Returns None (defaults to safe)
        """
        # Arrange - metadata with no maintainer_count field
        package = "some-package"
        registry = "pypi"
        metadata: dict[str, Any] = {
            "name": package,
            "version": "1.0.0",
            # No maintainer_count field
        }

        # Act
        result = detect_ownership_transfer(package, metadata, registry)

        # Assert - INV070: defaults to safe
        assert result is None

    # =========================================================================
    # T070.02: Single maintainer max weight 0.15
    # =========================================================================
    def test_single_maintainer_max_weight(self):
        """
        SPEC: S070
        TEST_ID: T070.02
        INV_ID: INV071
        EC_ID: EC441

        Given: Package with 1 maintainer, 1 package (new maintainer)
        When: detect_ownership_transfer is called
        Then: Returns signal with weight <= 0.15 (never HIGH_RISK alone)
        """
        # Arrange - all risk factors present
        package = "suspicious-package"
        registry = "npm"
        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 1,  # Single maintainer
            "maintainer_packages": 1,  # Only 1 package
            "maintainer_age_days": 7,  # New account (7 days)
        }

        # Act
        result = detect_ownership_transfer(package, metadata, registry)

        # Assert - INV071: max weight is 0.15
        assert result is not None
        assert isinstance(result, OwnershipSignal)
        assert result.confidence <= OWNERSHIP_MAX_WEIGHT
        assert result.confidence == 0.15  # All 3 factors = 0.15 (capped)

    # =========================================================================
    # T070.03: Partial data handled
    # =========================================================================
    def test_partial_data_handled(self):
        """
        SPEC: S070
        TEST_ID: T070.03
        INV_ID: INV072
        EC_ID: EC452

        Given: Package with only maintainer count (no age data)
        When: detect_ownership_transfer is called
        Then: Uses available data, doesn't crash
        """
        # Arrange - only maintainer_count available
        package = "partial-data-package"
        registry = "pypi"
        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 1,  # Single maintainer
            # No maintainer_packages or maintainer_age_days
        }

        # Act - should not raise exception
        result = detect_ownership_transfer(package, metadata, registry)

        # Assert - uses partial data, returns signal with reduced weight
        assert result is not None
        assert isinstance(result, OwnershipSignal)
        assert result.confidence == 0.05  # Only single maintainer factor
        assert result.maintainer_packages is None
        assert result.maintainer_age_days is None

    # =========================================================================
    # T070.04: Cross-reference check
    # =========================================================================
    def test_cross_reference_check(self):
        """
        SPEC: S070
        TEST_ID: T070.04
        EC_ID: EC446

        Given: Maintainer with only 1 package in entire registry
        When: detect_ownership_transfer is called
        Then: Flags as suspicious (cross-reference fails)
        """
        # Arrange - maintainer with single package
        package = "only-package"
        registry = "npm"
        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 1,
            "maintainer_packages": 1,  # Only 1 package in registry
            "maintainer_age_days": 365,  # Established account (doesn't trigger age)
        }

        # Act
        result = detect_ownership_transfer(package, metadata, registry)

        # Assert - cross-reference flagged
        assert result is not None
        assert "only 1 packages" in result.reason
        assert result.confidence == 0.10  # Single + low packages

    # =========================================================================
    # T070.05: Weight never exceeds 0.15 property
    # =========================================================================
    @pytest.mark.property
    @given(
        maintainer_count=st.integers(min_value=0, max_value=10),
        maintainer_packages=st.one_of(st.none(), st.integers(min_value=0, max_value=100)),
        maintainer_age_days=st.one_of(st.none(), st.integers(min_value=0, max_value=3650)),
    )
    def test_weight_never_exceeds_limit(
        self,
        maintainer_count: int,
        maintainer_packages: int | None,
        maintainer_age_days: int | None,
    ) -> None:
        """
        SPEC: S070
        TEST_ID: T070.05
        INV_ID: INV071

        Property: For any input, ownership transfer weight <= 0.15
        (reduced per P0-DESIGN-001)
        """
        # Arrange
        package = "test-package"
        registry = "pypi"
        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": maintainer_count,
        }
        if maintainer_packages is not None:
            metadata["maintainer_packages"] = maintainer_packages
        if maintainer_age_days is not None:
            metadata["maintainer_age_days"] = maintainer_age_days

        # Act
        result = detect_ownership_transfer(package, metadata, registry)

        # Assert - INV071: weight never exceeds max
        if result is not None:
            assert result.confidence <= OWNERSHIP_MAX_WEIGHT


class TestOwnershipTransferEdgeCases:
    """Edge case tests for ownership transfer (EC440-EC455)."""

    def test_single_maintainer_many_packages(self):
        """
        EC_ID: EC440
        Given: 1 maintainer with 50 packages
        When: detect_ownership_transfer is called
        Then: Returns signal with reduced weight (established maintainer)
        """
        # Arrange
        package = "established-package"
        registry = "npm"
        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 1,
            "maintainer_packages": 50,  # Many packages = established
            "maintainer_age_days": 1000,  # Old account
        }

        # Act
        result = detect_ownership_transfer(package, metadata, registry)

        # Assert - single maintainer still triggers, but no other factors
        assert result is not None
        assert result.confidence == 0.05  # Only single maintainer factor

    def test_multiple_maintainers_no_signal(self):
        """
        EC_ID: EC442
        Given: Package with 3 maintainers
        When: detect_ownership_transfer is called
        Then: Returns None
        """
        # Arrange
        package = "team-package"
        registry = "npm"
        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 3,  # Multiple maintainers = safe
        }

        # Act
        result = detect_ownership_transfer(package, metadata, registry)

        # Assert - multiple maintainers = no signal
        assert result is None

    def test_none_metadata_safe(self):
        """
        EC_ID: EC443 (variant)
        Given: None metadata
        When: detect_ownership_transfer is called
        Then: Returns None (safe)
        """
        # Act
        result = detect_ownership_transfer("some-pkg", None, "pypi")

        # Assert
        assert result is None

    @pytest.mark.skip(reason="Stub - implement with S070 integration")
    @pytest.mark.integration
    def test_cross_reference_pass_many_packages(self):
        """
        EC_ID: EC447
        Given: User with 50 packages in registry
        When: detect_ownership_transfer is called
        Then: Returns None (established presence)
        """
        pass

    @pytest.mark.skip(reason="Stub - PyPI-specific implementation")
    def test_pypi_no_user_api(self):
        """
        EC_ID: EC448
        Given: PyPI package (no user metadata API)
        When: detect_ownership_transfer is called
        Then: Skips maintainer age check, uses other signals
        """
        pass

    @pytest.mark.skip(reason="Stub - crates.io-specific implementation")
    def test_crates_io_team_ownership(self):
        """
        EC_ID: EC449
        Given: crates.io package with team ownership
        When: detect_ownership_transfer is called
        Then: Returns None (org ownership is safer)
        """
        pass

    def test_combined_signals_full_weight(self):
        """
        EC_ID: EC450
        Given: Single maintainer + new user + 1 package
        When: detect_ownership_transfer is called
        Then: Full 0.15 weight applied
        """
        # Arrange
        package = "high-risk-package"
        registry = "npm"
        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 1,
            "maintainer_packages": 1,
            "maintainer_age_days": 7,
        }

        # Act
        result = detect_ownership_transfer(package, metadata, registry)

        # Assert
        assert result is not None
        assert result.confidence == 0.15  # Full weight (capped)

    @pytest.mark.skip(reason="Stub - rate limiting integration test")
    @pytest.mark.integration
    def test_api_rate_limit_skip(self):
        """
        EC_ID: EC455
        Given: npm user API returns 429
        When: detect_ownership_transfer is called
        Then: Returns None (skip check)
        """
        pass
