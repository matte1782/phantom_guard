"""
SPEC: S075 - Version Spike Detection
TEST_IDs: T075.01-T075.07
INVARIANTS: INV075, INV076, INV077

Tests for version spike signal detection.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from phantom_guard.core.signals.versions import (
    VERSIONS_7D_THRESHOLD,
    VERSIONS_24H_THRESHOLD,
    WEIGHT_7D_SPIKE,
    WEIGHT_24H_SPIKE,
    VersionSpikeSignal,
    detect_version_spike,
    extract_version_timestamps,
    is_ci_package,
    parse_timestamp,
)


class TestVersionSpikeDetection:
    """Unit tests for version spike detection (S075)."""

    # =========================================================================
    # T075.01: 5 versions in 24h detected
    # =========================================================================
    def test_five_versions_in_24h_detected(self):
        """
        SPEC: S075
        TEST_ID: T075.01
        INV_ID: INV075
        EC_ID: EC461

        Given: Package with 5 versions released in last 24 hours
        When: detect_version_spike is called
        Then: Returns VersionSpikeSignal with weight 0.45
        """
        # Arrange - create 5 versions in last 24 hours
        now = datetime.now(UTC)
        timestamps = [(now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ") for i in range(5)]
        metadata: dict[str, Any] = {
            "time": {f"1.0.{i}": ts for i, ts in enumerate(timestamps)},
        }

        # Act
        result = detect_version_spike("some-package", metadata, "npm")

        # Assert
        assert result is not None
        assert isinstance(result, VersionSpikeSignal)
        assert result.versions_24h >= VERSIONS_24H_THRESHOLD
        assert result.confidence == WEIGHT_24H_SPIKE

    # =========================================================================
    # T075.02: 20 versions in 7d detected
    # =========================================================================
    def test_twenty_versions_in_7d_detected(self):
        """
        SPEC: S075
        TEST_ID: T075.02
        INV_ID: INV075
        EC_ID: EC462

        Given: Package with 20 versions released in last 7 days
        When: detect_version_spike is called
        Then: Returns VersionSpikeSignal with weight 0.30
        """
        # Arrange - create 20 versions over 7 days (but not 5 in 24h)
        now = datetime.now(UTC)
        timestamps = [
            (now - timedelta(hours=12 + i * 8)).strftime("%Y-%m-%dT%H:%M:%SZ") for i in range(20)
        ]
        metadata: dict[str, Any] = {
            "time": {f"1.0.{i}": ts for i, ts in enumerate(timestamps)},
        }

        # Act
        result = detect_version_spike("some-package", metadata, "npm")

        # Assert
        assert result is not None
        assert result.versions_7d >= VERSIONS_7D_THRESHOLD
        assert result.confidence == WEIGHT_7D_SPIKE

    # =========================================================================
    # T075.03: CI package excluded
    # =========================================================================
    def test_ci_package_excluded(self):
        """
        SPEC: S075
        TEST_ID: T075.03
        INV_ID: INV076
        EC_ID: EC463

        Given: Package "@types/node" (known CI package)
        When: detect_version_spike is called
        Then: Returns None (excluded from check)
        """
        # Arrange
        package = "@types/node"
        registry = "npm"
        now = datetime.now(UTC)
        timestamps = [
            (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for i in range(10)  # Would normally trigger
        ]
        metadata: dict[str, Any] = {
            "time": {f"1.0.{i}": ts for i, ts in enumerate(timestamps)},
        }

        # Act
        result = detect_version_spike(package, metadata, registry)

        # Assert - INV076: CI packages excluded
        assert result is None

    # =========================================================================
    # T075.04: PyPI timestamp parsed correctly
    # =========================================================================
    def test_pypi_timestamp_parsed(self):
        """
        SPEC: S075
        TEST_ID: T075.04
        INV_ID: INV077
        EC_ID: EC470

        Given: PyPI package with releases[version].upload_time format
        When: Parsing version timestamps
        Then: Timestamps parsed correctly
        """
        # Arrange - PyPI metadata format
        now = datetime.now(UTC)
        metadata: dict[str, Any] = {
            "releases": {
                "1.0.0": [{"upload_time": now.strftime("%Y-%m-%dT%H:%M:%S")}],
                "1.0.1": [
                    {"upload_time": (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")}
                ],
                "1.0.2": [
                    {"upload_time": (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")}
                ],
            }
        }

        # Act
        timestamps = extract_version_timestamps(metadata, "pypi")

        # Assert
        assert len(timestamps) == 3
        for ts in timestamps:
            assert ts.tzinfo is not None  # UTC-aware

    # =========================================================================
    # T075.05: npm timestamp parsed correctly
    # =========================================================================
    def test_npm_timestamp_parsed(self):
        """
        SPEC: S075
        TEST_ID: T075.05
        INV_ID: INV077
        EC_ID: EC471

        Given: npm package with time[version] object
        When: Parsing version timestamps
        Then: Timestamps parsed correctly
        """
        # Arrange - npm metadata format
        metadata: dict[str, Any] = {
            "time": {
                "created": "2024-01-01T00:00:00.000Z",
                "modified": "2024-12-01T00:00:00.000Z",
                "1.0.0": "2024-01-01T00:00:00.000Z",
                "1.0.1": "2024-06-01T00:00:00.000Z",
                "1.0.2": "2024-12-01T00:00:00.000Z",
            }
        }

        # Act
        timestamps = extract_version_timestamps(metadata, "npm")

        # Assert
        assert len(timestamps) == 3  # Excludes 'created' and 'modified'
        for ts in timestamps:
            assert ts.tzinfo is not None  # UTC-aware

    # =========================================================================
    # T075.06: crates.io timestamp parsed correctly
    # =========================================================================
    def test_crates_io_timestamp_parsed(self):
        """
        SPEC: S075
        TEST_ID: T075.06
        INV_ID: INV077
        EC_ID: EC472

        Given: crates.io package with versions[].created_at format
        When: Parsing version timestamps
        Then: Timestamps parsed correctly
        """
        # Arrange - crates.io metadata format
        metadata: dict[str, Any] = {
            "versions": [
                {"num": "1.0.0", "created_at": "2024-01-01T00:00:00Z"},
                {"num": "1.0.1", "created_at": "2024-06-01T00:00:00+00:00"},
                {"num": "1.0.2", "created_at": "2024-12-01T00:00:00.123456Z"},
            ]
        }

        # Act
        timestamps = extract_version_timestamps(metadata, "crates")

        # Assert
        assert len(timestamps) == 3
        for ts in timestamps:
            assert ts.tzinfo is not None  # UTC-aware

    # =========================================================================
    # T075.07: UTC consistency property
    # =========================================================================
    @pytest.mark.property
    @given(
        hour_offset=st.integers(min_value=0, max_value=168),  # Up to 7 days in hours
    )
    def test_utc_consistency_property(self, hour_offset: int) -> None:
        """
        SPEC: S075
        TEST_ID: T075.07
        INV_ID: INV075

        Property: Version spike uses UTC timestamps consistently
        across all calculations.
        """
        # Arrange - create timestamp at various offsets
        now = datetime.now(UTC)
        past_time = now - timedelta(hours=hour_offset)
        ts_str = past_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Act
        parsed = parse_timestamp(ts_str)

        # Assert - INV075: UTC consistency
        assert parsed is not None
        assert parsed.tzinfo is not None
        assert parsed.tzinfo == UTC


class TestVersionSpikeEdgeCases:
    """Edge case tests for version spike (EC460-EC475)."""

    def test_normal_release_cadence_no_signal(self):
        """
        EC_ID: EC460
        Given: Package with 1 version/week
        When: detect_version_spike is called
        Then: Returns None
        """
        # Arrange - 4 versions, 1 per week (normal)
        now = datetime.now(UTC)
        metadata: dict[str, Any] = {
            "time": {
                f"1.{i}.0": (now - timedelta(weeks=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(4)
            },
        }

        # Act
        result = detect_version_spike("normal-package", metadata, "npm")

        # Assert
        assert result is None

    def test_single_version_no_signal(self):
        """
        EC_ID: EC467
        Given: Package with only 1 release ever
        When: detect_version_spike is called
        Then: Returns None
        """
        # Arrange
        metadata: dict[str, Any] = {
            "time": {
                "1.0.0": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }

        # Act
        result = detect_version_spike("single-version", metadata, "npm")

        # Assert
        assert result is None

    def test_old_versions_no_signal(self):
        """
        EC_ID: EC468
        Given: Package with no versions in recent time
        When: detect_version_spike is called
        Then: Returns None
        """
        # Arrange - all versions > 30 days old
        now = datetime.now(UTC)
        metadata: dict[str, Any] = {
            "time": {
                f"1.0.{i}": (now - timedelta(days=60 + i)).strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(10)
            },
        }

        # Act
        result = detect_version_spike("old-package", metadata, "npm")

        # Assert
        assert result is None

    def test_ci_prefix_excluded(self):
        """
        EC_ID: EC463 variant
        Given: Package with CI-related prefix
        When: detect_version_spike is called
        Then: Returns None
        """
        # Assert
        assert is_ci_package("@types/express", "npm") is True
        assert is_ci_package("my-package-nightly", "npm") is True
        assert is_ci_package("regular-package", "npm") is False

    def test_none_metadata_safe(self):
        """
        Given: None metadata
        When: detect_version_spike is called
        Then: Returns None
        """
        result = detect_version_spike("package", None, "npm")
        assert result is None

    @pytest.mark.skip(reason="Stub - implement with S075 integration")
    def test_meaningful_version_increments_no_signal(self):
        """
        EC_ID: EC464
        Given: Versions 1.0 -> 1.1 -> 2.0 (meaningful changes)
        When: detect_version_spike is called
        Then: Returns None
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S075 integration")
    def test_micro_bumps_suspicious(self):
        """
        EC_ID: EC465
        Given: Versions 1.0.0 -> 1.0.99 (99 micro bumps)
        When: detect_version_spike is called
        Then: Returns signal (suspicious pattern)
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S075 integration")
    def test_prerelease_spam_flagged(self):
        """
        EC_ID: EC466
        Given: 50 pre-release versions (1.0.0-alpha.1 through .50)
        When: detect_version_spike is called
        Then: Returns signal
        """
        pass
