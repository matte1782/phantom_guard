"""
SPEC: S060, S065, S070, S075, S080
TEST_IDs: Integration tests for all v0.2.0 signals

Full signal integration tests verifying:
- All 4 signals work together correctly
- Signals with realistic package metadata
- End-to-end gather_all_signals flow
- Weight combination verification
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from phantom_guard.core.signals.combination import (
    CombinedSignals,
    calculate_combined_weight,
    calculate_normalized_score,
    gather_all_signals,
)
from phantom_guard.core.signals.downloads import (
    DOWNLOAD_INFLATION_WEIGHT,
    detect_download_inflation,
)
from phantom_guard.core.signals.namespace import (
    NAMESPACE_SQUAT_WEIGHT,
    detect_namespace_squatting,
)
from phantom_guard.core.signals.ownership import (
    OWNERSHIP_MAX_WEIGHT,
    detect_ownership_transfer,
)
from phantom_guard.core.signals.versions import (
    WEIGHT_24H_SPIKE,
    detect_version_spike,
)


class TestSignalIntegrationScenarios:
    """Integration tests for realistic signal scenarios."""

    def test_legitimate_popular_package_no_signals(self):
        """
        SCENARIO: Popular, well-maintained package

        Given: Package like 'requests' with:
          - Multiple maintainers
          - High downloads with many dependents
          - No namespace issues
          - Normal release cadence
        When: All signals are checked
        Then: No signals fire (legitimate package)
        """
        # Arrange - simulate a legitimate popular package
        package = "requests"
        registry = "pypi"
        now = datetime.now(UTC)

        metadata: dict[str, Any] = {
            "name": package,
            # Ownership: multiple maintainers (safe)
            "maintainer_count": 5,
            "maintainer_packages": 50,
            "maintainer_age_days": 3650,  # 10 years
            # Downloads: high but proportional to dependents
            "downloads": 10_000_000,
            "dependents_count": 50000,
            "age_days": 4000,
            # Versions: normal release cadence
            "releases": {
                f"2.{i}.0": [
                    {"upload_time": (now - timedelta(weeks=i * 4)).strftime("%Y-%m-%dT%H:%M:%S")}
                ]
                for i in range(10)
            },
        }

        # Act
        result = gather_all_signals(package, metadata, registry)

        # Assert - no signals should fire
        assert result.namespace is None
        assert result.download is None
        assert result.ownership is None
        assert result.version is None
        assert result.total_weight == 0.0
        assert result.signals_collected == []

    def test_highly_suspicious_package_all_signals(self):
        """
        SCENARIO: Highly suspicious package

        Given: Package with:
          - Fake namespace (e.g., @google-fake/package)
          - Inflated downloads (100K with 0 dependents)
          - Single new maintainer
          - 10 versions in 24 hours
        When: All signals are checked
        Then: All 4 signals fire with maximum weight
        """
        # Arrange - simulate a highly suspicious package
        package = "@microsoft-fake/util"  # Fake namespace
        registry = "npm"
        now = datetime.now(UTC)

        metadata: dict[str, Any] = {
            "name": package,
            # Ownership: single new maintainer with only this package
            "maintainer_count": 1,
            "maintainer_packages": 1,
            "maintainer_age_days": 7,  # 1 week old account
            # Downloads: high but zero dependents (inflated)
            "downloads": 100_000,
            "dependents_count": 0,
            "age_days": 60,
            # Versions: 10 versions in last 24 hours (spike)
            "time": {
                f"1.0.{i}": (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(10)
            },
        }

        # Act - check all signals individually
        namespace_signal = detect_namespace_squatting(package, metadata, registry)
        download_signal = detect_download_inflation(package, metadata, registry)
        ownership_signal = detect_ownership_transfer(package, metadata, registry)
        version_signal = detect_version_spike(package, metadata, registry)

        # Assert - all signals should fire
        assert namespace_signal is not None, "Namespace signal should fire"
        assert download_signal is not None, "Download signal should fire"
        assert ownership_signal is not None, "Ownership signal should fire"
        assert version_signal is not None, "Version signal should fire"

        # Verify weights
        assert namespace_signal.confidence == NAMESPACE_SQUAT_WEIGHT
        assert download_signal.confidence == DOWNLOAD_INFLATION_WEIGHT
        assert ownership_signal.confidence <= OWNERSHIP_MAX_WEIGHT
        assert version_signal.confidence == WEIGHT_24H_SPIKE

    def test_gather_all_signals_integration(self):
        """
        SCENARIO: Use gather_all_signals for full detection

        Given: Package with multiple suspicious signals
        When: gather_all_signals is called
        Then: All signals are collected and weights summed
        """
        # Arrange
        package = "@facebook-fake/analytics"
        registry = "npm"
        now = datetime.now(UTC)

        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 1,
            "maintainer_packages": 2,
            "maintainer_age_days": 30,
            "downloads": 50_000,
            "dependents_count": 0,
            "age_days": 45,
            "time": {
                f"1.0.{i}": (now - timedelta(hours=i * 2)).strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(8)
            },
        }

        # Act
        result = gather_all_signals(package, metadata, registry)

        # Assert - multiple signals should be collected
        assert isinstance(result, CombinedSignals)
        assert len(result.signals_collected) >= 2  # At least namespace + version
        assert result.total_weight > 0.5  # Significant risk

    def test_partial_data_graceful_degradation(self):
        """
        SCENARIO: Package with incomplete metadata

        Given: Package with only some metadata fields
        When: All signals are checked
        Then: Available signals work, missing data is handled gracefully
        """
        # Arrange - minimal metadata
        package = "some-package"
        registry = "pypi"

        metadata: dict[str, Any] = {
            "name": package,
            # Only version data available
            "releases": {
                "1.0.0": [{"upload_time": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")}],
            },
            # No maintainer data
            # No download data
        }

        # Act
        result = gather_all_signals(package, metadata, registry)

        # Assert - should not crash, handle missing data
        assert isinstance(result, CombinedSignals)
        # Some signals may be None due to missing data, that's OK

    def test_pypi_package_realistic_metadata(self):
        """
        SCENARIO: PyPI package with realistic metadata structure

        Given: Package with PyPI-style metadata
        When: All signals are checked
        Then: Signals correctly parse PyPI format
        """
        # Arrange - realistic PyPI metadata
        # Note: Using netflix- prefix (not in legitimate list)
        package = "netflix-fake-sdk"
        registry = "pypi"
        now = datetime.now(UTC)

        metadata: dict[str, Any] = {
            "name": package,
            "info": {
                "author": "unknown",
                "maintainer": "unknown",
            },
            "maintainer_count": 1,
            "maintainer_packages": 1,
            "maintainer_age_days": 14,
            "downloads": 1000,
            "dependents_count": 0,
            "age_days": 14,
            "releases": {
                "0.0.1": [
                    {"upload_time": (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")}
                ],
                "0.0.2": [
                    {"upload_time": (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")}
                ],
                "0.0.3": [
                    {"upload_time": (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")}
                ],
                "0.0.4": [
                    {"upload_time": (now - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%S")}
                ],
                "0.0.5": [
                    {"upload_time": (now - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S")}
                ],
            },
        }

        # Act
        namespace_signal = detect_namespace_squatting(package, metadata, registry)
        ownership_signal = detect_ownership_transfer(package, metadata, registry)
        version_signal = detect_version_spike(package, metadata, registry)

        # Assert
        assert namespace_signal is not None  # netflix- prefix detected
        assert ownership_signal is not None  # Single new maintainer
        assert version_signal is not None  # 5 versions in 5 hours

    def test_npm_package_realistic_metadata(self):
        """
        SCENARIO: npm package with realistic metadata structure

        Given: Package with npm-style metadata
        When: All signals are checked
        Then: Signals correctly parse npm format
        """
        # Arrange - realistic npm metadata
        package = "@stripe-fake/payments"  # Suspicious scope
        registry = "npm"
        now = datetime.now(UTC)

        metadata: dict[str, Any] = {
            "name": package,
            "maintainers": [{"name": "attacker"}],
            "maintainer_count": 1,
            "maintainer_packages": 1,
            "maintainer_age_days": 3,
            "downloads": 50000,
            "dependents_count": 0,
            "age_days": 30,
            "time": {
                "created": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "modified": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "1.0.0": (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "1.0.1": (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "1.0.2": (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "1.0.3": (now - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "1.0.4": (now - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "1.0.5": (now - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }

        # Act
        result = gather_all_signals(package, metadata, registry)

        # Assert - multiple signals should fire
        assert result.namespace is not None  # @stripe-fake scope
        assert result.version is not None  # 6 versions in 6 hours
        assert result.ownership is not None  # Single 3-day-old maintainer

    def test_crates_package_realistic_metadata(self):
        """
        SCENARIO: crates.io package with realistic metadata structure

        Given: Package with crates.io-style metadata
        When: All signals are checked
        Then: Signals correctly parse crates.io format
        """
        # Arrange - realistic crates.io metadata
        # Note: Using netflix- prefix (not in legitimate list)
        package = "netflix-fake-crate"  # Suspicious prefix
        registry = "crates"
        now = datetime.now(UTC)

        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 1,
            "maintainer_packages": 1,
            "maintainer_age_days": 7,
            "downloads": 10000,
            "dependents_count": 0,
            "age_days": 14,
            "versions": [
                {
                    "num": "0.1.0",
                    "created_at": (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                {
                    "num": "0.1.1",
                    "created_at": (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                {
                    "num": "0.1.2",
                    "created_at": (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                {
                    "num": "0.1.3",
                    "created_at": (now - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                {
                    "num": "0.1.4",
                    "created_at": (now - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            ],
        }

        # Act
        namespace_signal = detect_namespace_squatting(package, metadata, registry)
        ownership_signal = detect_ownership_transfer(package, metadata, registry)
        version_signal = detect_version_spike(package, metadata, registry)

        # Assert
        assert namespace_signal is not None  # netflix- prefix detected
        assert ownership_signal is not None  # Single maintainer
        assert version_signal is not None  # 5 versions in 5 hours


class TestSignalWeightIntegration:
    """Integration tests for signal weight calculations."""

    def test_combined_weight_calculation(self):
        """Verify combined weight calculation matches individual signals."""
        # Arrange
        signals = [
            "NAMESPACE_SQUATTING",  # 0.35
            "DOWNLOAD_INFLATION",  # 0.30
            "OWNERSHIP_TRANSFER",  # 0.15
            "VERSION_SPIKE",  # 0.45
        ]

        # Act
        total = calculate_combined_weight(signals)

        # Assert - should be 1.25
        expected = (
            NAMESPACE_SQUAT_WEIGHT
            + DOWNLOAD_INFLATION_WEIGHT
            + OWNERSHIP_MAX_WEIGHT
            + WEIGHT_24H_SPIKE
        )
        assert total == pytest.approx(expected)
        assert total == pytest.approx(1.25)

    def test_normalized_score_integration(self):
        """Verify normalized score calculation with real signal weights."""
        # Arrange - all v0.2.0 signals fire (weight 1.25)
        # Plus some v0.1.x signals (say 50 points)
        v02_weight = 1.25
        v01_points = 50
        raw_score = (v02_weight * 100) + v01_points  # 175 points

        # Act
        normalized = calculate_normalized_score(raw_score, max_score=285.0)

        # Assert
        assert 0.0 <= normalized <= 1.0
        assert normalized == pytest.approx(175.0 / 285.0)

    def test_weight_ordering_by_severity(self):
        """Verify signal weights are ordered by severity."""
        # Assert weights are in expected order
        assert WEIGHT_24H_SPIKE > NAMESPACE_SQUAT_WEIGHT  # 0.45 > 0.35
        assert NAMESPACE_SQUAT_WEIGHT > DOWNLOAD_INFLATION_WEIGHT  # 0.35 > 0.30
        assert DOWNLOAD_INFLATION_WEIGHT > OWNERSHIP_MAX_WEIGHT  # 0.30 > 0.15


class TestSignalEdgeCaseIntegration:
    """Integration tests for edge cases across signals."""

    def test_ci_package_exemption_cascade(self):
        """
        SCENARIO: CI package with many releases

        Given: @types/node (known CI package) with 100 versions
        When: Version spike is checked
        Then: No signal fires (CI exemption)
        """
        # Arrange
        package = "@types/node"
        registry = "npm"
        now = datetime.now(UTC)

        metadata: dict[str, Any] = {
            "name": package,
            "time": {
                f"18.0.{i}": (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(20)  # Many versions
            },
        }

        # Act
        version_signal = detect_version_spike(package, metadata, registry)

        # Assert - CI package exempted
        assert version_signal is None

    def test_legitimate_org_namespace_exemption(self):
        """
        SCENARIO: Legitimate organization package

        Given: @babel/core (known legitimate org)
        When: Namespace squatting is checked
        Then: No signal fires (legitimate org)
        """
        # Arrange
        package = "@babel/core"
        registry = "npm"
        metadata: dict[str, Any] = {"name": package}

        # Act
        namespace_signal = detect_namespace_squatting(package, metadata, registry)

        # Assert - legitimate org exempted
        assert namespace_signal is None

    def test_established_maintainer_reduced_weight(self):
        """
        SCENARIO: Single but established maintainer

        Given: Package with 1 maintainer who has 100 packages
        When: Ownership signal is checked
        Then: Reduced weight (established maintainer)
        """
        # Arrange
        package = "some-package"
        registry = "npm"
        metadata: dict[str, Any] = {
            "name": package,
            "maintainer_count": 1,
            "maintainer_packages": 100,  # Very established
            "maintainer_age_days": 3650,  # 10 years
        }

        # Act
        ownership_signal = detect_ownership_transfer(package, metadata, registry)

        # Assert - single maintainer triggers but with low weight
        assert ownership_signal is not None
        assert ownership_signal.confidence == 0.05  # Only base factor

    def test_viral_package_not_flagged(self):
        """
        SCENARIO: Legitimately viral package

        Given: Package with 1M downloads but also 1000 dependents
        When: Download inflation is checked
        Then: No signal fires (legitimate viral)
        """
        # Arrange
        package = "lodash-clone"  # Hypothetical popular utility
        registry = "npm"
        metadata: dict[str, Any] = {
            "name": package,
            "downloads": 1_000_000,
            "dependents_count": 1000,  # Many real dependents
            "age_days": 365,
        }

        # Act
        download_signal = detect_download_inflation(package, metadata, registry)

        # Assert - legitimate viral, no inflation
        assert download_signal is None
