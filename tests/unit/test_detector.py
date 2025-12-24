# SPEC: S001-S003 - Package Validation and Detection
# Gate 3: Test Implementation
"""
Unit tests for the Detector module.

SPEC_IDs: S001, S002, S003
TEST_IDs: T001.*, T002.*, T003.*
INVARIANTS: INV001, INV002, INV004, INV005, INV006, INV019, INV020, INV021
EDGE_CASES: EC001-EC015, EC020-EC021, EC035
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from phantom_guard.core.detector import (
    normalize_package_name,
    validate_batch,
    validate_batch_sync,
    validate_package,
    validate_package_sync,
)
from phantom_guard.core.types import (
    InvalidPackageNameError,
    PackageMetadata,
    PackageRisk,
    Recommendation,
    SignalType,
)

# =============================================================================
# MOCK REGISTRY CLIENT
# =============================================================================


class MockRegistryClient:
    """Mock registry client for testing."""

    def __init__(
        self,
        exists: bool = True,
        downloads: int = 1000,
        description: str = "A test package",
        releases: int = 5,
    ) -> None:
        self.exists = exists
        self.downloads = downloads
        self.description = description
        self.releases = releases
        self.call_count = 0
        self.requested_names: list[str] = []

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """Return mock metadata."""
        self.call_count += 1
        self.requested_names.append(name)

        if not self.exists:
            return PackageMetadata(
                name=name,
                exists=False,
            )

        now = datetime.now(UTC)
        return PackageMetadata(
            name=name,
            exists=True,
            downloads_last_month=self.downloads,
            description=self.description,
            release_count=self.releases,
            created_at=now,
            repository_url="https://github.com/test/package",
        )


class TestValidatePackage:
    """Tests for validate_package function.

    SPEC: S001 - Package validation
    """

    # =========================================================================
    # INPUT VALIDATION TESTS (INV019, INV020)
    # =========================================================================

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_empty_package_name_rejected(self) -> None:
        """
        TEST_ID: T001.01
        SPEC: S001
        INV: INV019
        EC: EC001

        Given: An empty package name ""
        When: validate_package is called
        Then: Raises InvalidPackageNameError
        """
        with pytest.raises(InvalidPackageNameError):
            await validate_package("")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_whitespace_package_name_rejected(self) -> None:
        """
        TEST_ID: T001.02
        SPEC: S001
        INV: INV019
        EC: EC002

        Given: A whitespace-only package name "   "
        When: validate_package is called
        Then: Raises InvalidPackageNameError
        """
        with pytest.raises(InvalidPackageNameError):
            await validate_package("   ")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_unicode_package_name_rejected(self) -> None:
        """
        TEST_ID: T001.03
        SPEC: S001
        INV: INV019
        EC: EC005

        Given: A Unicode package name
        When: validate_package is called
        Then: Raises InvalidPackageNameError
        """
        with pytest.raises(InvalidPackageNameError):
            await validate_package("pàckage")  # Unicode character

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_oversized_package_name_rejected(self) -> None:
        """
        TEST_ID: T001.04
        SPEC: S001
        INV: INV020
        EC: EC003

        Given: A package name > 214 characters
        When: validate_package is called
        Then: Raises InvalidPackageNameError
        """
        long_name = "a" * 215
        with pytest.raises(InvalidPackageNameError):
            await validate_package(long_name)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_max_length_package_name_accepted(self) -> None:
        """
        TEST_ID: T001.05
        SPEC: S001
        INV: INV020
        EC: EC004

        Given: A package name of exactly 214 characters
        When: validate_package is called
        Then: Returns PackageRisk (no exception)
        """
        max_name = "a" * 214
        result = await validate_package(max_name)
        assert isinstance(result, PackageRisk)
        assert result.name == max_name

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_valid_simple_name_accepted(self) -> None:
        """
        TEST_ID: T001.06
        SPEC: S001
        INV: INV019
        EC: EC007

        Given: A valid simple name "flask"
        When: validate_package is called
        Then: Returns PackageRisk with name="flask"
        """
        result = await validate_package("flask")
        assert isinstance(result, PackageRisk)
        assert result.name == "flask"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_valid_hyphenated_name_accepted(self) -> None:
        """
        TEST_ID: T001.07
        SPEC: S001
        INV: INV019
        EC: EC008

        Given: A valid hyphenated name "flask-redis-helper"
        When: validate_package is called
        Then: Returns PackageRisk
        """
        result = await validate_package("flask-redis-helper")
        assert isinstance(result, PackageRisk)
        assert result.name == "flask-redis-helper"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_valid_underscored_name_normalized(self) -> None:
        """
        TEST_ID: T001.08
        SPEC: S001
        INV: INV019
        EC: EC009

        Given: A valid underscored name "flask_redis"
        When: validate_package is called
        Then: Returns PackageRisk with normalized name
        """
        result = await validate_package("flask_redis")
        assert isinstance(result, PackageRisk)
        # Underscores normalized to hyphens per PEP 503
        assert result.name == "flask-redis"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_valid_numeric_name_accepted(self) -> None:
        """
        TEST_ID: T001.09
        SPEC: S001
        INV: INV019
        EC: EC010

        Given: A valid name with numbers "py3-redis"
        When: validate_package is called
        Then: Returns PackageRisk
        """
        result = await validate_package("py3-redis")
        assert isinstance(result, PackageRisk)
        assert result.name == "py3-redis"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_leading_hyphen_rejected(self) -> None:
        """
        TEST_ID: T001.10
        SPEC: S001
        INV: INV019
        EC: EC011

        Given: A name starting with hyphen "-flask"
        When: validate_package is called
        Then: Raises InvalidPackageNameError
        """
        with pytest.raises(InvalidPackageNameError):
            await validate_package("-flask")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_trailing_hyphen_rejected(self) -> None:
        """
        TEST_ID: T001.11
        SPEC: S001
        INV: INV019
        EC: EC012

        Given: A name ending with hyphen "flask-"
        When: validate_package is called
        Then: Raises InvalidPackageNameError
        """
        with pytest.raises(InvalidPackageNameError):
            await validate_package("flask-")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_double_hyphen_rejected(self) -> None:
        """
        TEST_ID: T001.12
        SPEC: S001
        INV: INV019
        EC: EC013

        Given: A name with double hyphen "flask--redis"
        When: validate_package is called
        Then: Raises InvalidPackageNameError
        """
        with pytest.raises(InvalidPackageNameError):
            await validate_package("flask--redis")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_special_characters_rejected(self) -> None:
        """
        TEST_ID: T001.13
        SPEC: S001
        INV: INV019
        EC: EC006

        Given: A name with special characters "flask@redis"
        When: validate_package is called
        Then: Raises InvalidPackageNameError
        """
        with pytest.raises(InvalidPackageNameError):
            await validate_package("flask@redis")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_case_normalization(self) -> None:
        """
        TEST_ID: T001.14
        SPEC: S001
        EC: EC015

        Given: A mixed-case name "Flask"
        When: validate_package is called
        Then: Returns PackageRisk with normalized name "flask"
        """
        result = await validate_package("Flask")
        assert result.name == "flask"

    # =========================================================================
    # RESULT STRUCTURE TESTS (INV002, INV006)
    # =========================================================================

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_signals_never_none(self) -> None:
        """
        TEST_ID: T001.15
        SPEC: S001
        INV: INV002

        Given: Any valid package name
        When: validate_package is called
        Then: Result.signals is a tuple (never None)
        """
        result = await validate_package("testpackage")
        assert result.signals is not None
        assert isinstance(result.signals, tuple)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_returns_package_risk_type(self) -> None:
        """
        TEST_ID: T001.16
        SPEC: S001
        INV: INV006

        Given: Any valid package name
        When: validate_package is called
        Then: Returns instance of PackageRisk
        """
        result = await validate_package("testpackage")
        assert isinstance(result, PackageRisk)

    # =========================================================================
    # REGISTRY SELECTION TESTS (INV021)
    # =========================================================================

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_pypi_registry_accepted(self) -> None:
        """
        TEST_ID: T001.18
        SPEC: S001
        INV: INV021

        Given: Registry "pypi"
        When: validate_package is called
        Then: Uses PyPI registry
        """
        result = await validate_package("flask", registry="pypi")
        assert result.registry == "pypi"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_npm_registry_accepted(self) -> None:
        """
        TEST_ID: T001.19
        SPEC: S001
        INV: INV021

        Given: Registry "npm"
        When: validate_package is called
        Then: Uses npm registry
        """
        result = await validate_package("express", registry="npm")
        assert result.registry == "npm"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_crates_registry_accepted(self) -> None:
        """
        TEST_ID: T001.20
        SPEC: S001
        INV: INV021

        Given: Registry "crates"
        When: validate_package is called
        Then: Uses crates.io registry
        """
        result = await validate_package("serde", registry="crates")
        assert result.registry == "crates"

    # =========================================================================
    # CLIENT TESTS
    # =========================================================================

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_with_mock_client(self) -> None:
        """
        TEST_ID: T001.21
        SPEC: S001

        Given: A mock registry client
        When: validate_package is called
        Then: Client is called and result reflects metadata
        """
        client = MockRegistryClient(exists=True, downloads=50000)
        result = await validate_package("some-package", client=client)

        assert client.call_count == 1
        assert "some-package" in client.requested_names
        assert result.exists is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_package_not_found(self) -> None:
        """
        TEST_ID: T001.22
        SPEC: S001

        Given: A non-existent package
        When: validate_package is called with client
        Then: Returns NOT_FOUND recommendation
        """
        client = MockRegistryClient(exists=False)
        result = await validate_package("nonexistent-pkg", client=client)

        assert result.exists is False
        assert result.recommendation == Recommendation.NOT_FOUND

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_offline_mode_without_client(self) -> None:
        """
        TEST_ID: T001.23
        SPEC: S001

        Given: No client provided
        When: validate_package is called
        Then: Assumes package exists (offline mode)
        """
        result = await validate_package("some-random-package")
        assert result.exists is True

    # =========================================================================
    # SIGNAL COMBINATION TESTS
    # =========================================================================

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_popular_package_reduces_risk(self) -> None:
        """
        TEST_ID: T001.24
        SPEC: S003

        Given: A popular package name
        When: validate_package is called
        Then: POPULAR_PACKAGE signal reduces risk
        """
        result = await validate_package("requests")
        signal_types = [s.type for s in result.signals]
        assert SignalType.POPULAR_PACKAGE in signal_types

        popular_signal = next(s for s in result.signals if s.type == SignalType.POPULAR_PACKAGE)
        assert popular_signal.weight < 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_suspicious_pattern_increases_risk(self) -> None:
        """
        TEST_ID: T001.25
        SPEC: S003

        Given: A suspicious pattern in package name
        When: validate_package is called
        Then: HALLUCINATION_PATTERN signal increases risk
        """
        result = await validate_package("flask-gpt-helper")
        assert result.risk_score > 0.5
        signal_types = [s.type for s in result.signals]
        assert SignalType.HALLUCINATION_PATTERN in signal_types

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_typosquat_detection(self) -> None:
        """
        TEST_ID: T001.26
        SPEC: S003

        Given: A typosquat of a popular package
        When: validate_package is called
        Then: TYPOSQUAT signal is present
        """
        result = await validate_package("reqeusts")  # typo of requests
        signal_types = [s.type for s in result.signals]
        assert SignalType.TYPOSQUAT in signal_types

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_latency_measured(self) -> None:
        """
        TEST_ID: T001.27
        SPEC: S001

        Given: Any valid package
        When: validate_package is called
        Then: Latency is measured and positive
        """
        result = await validate_package("flask")
        assert result.latency_ms > 0


class TestBatchValidation:
    """Tests for batch_validate function.

    SPEC: S002 - Batch validation
    """

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_contains_all_inputs(self) -> None:
        """
        TEST_ID: T002.01
        SPEC: S002
        INV: INV004

        Given: A list of 5 package names
        When: batch_validate is called
        Then: Result contains exactly 5 PackageRisk objects
        """
        names = ["flask", "django", "requests", "numpy", "pandas"]
        results = await validate_batch(names)
        assert len(results) == 5

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_empty_list_returns_empty(self) -> None:
        """
        TEST_ID: T002.02
        SPEC: S002
        INV: INV004

        Given: An empty list
        When: batch_validate is called
        Then: Returns empty list
        """
        results = await validate_batch([])
        assert results == []

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_single_package(self) -> None:
        """
        TEST_ID: T002.03
        SPEC: S002
        INV: INV004

        Given: A list with one package
        When: batch_validate is called
        Then: Returns list with one PackageRisk
        """
        results = await validate_batch(["flask"])
        assert len(results) == 1
        assert results[0].name == "flask"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_preserves_order(self) -> None:
        """
        TEST_ID: T002.07
        SPEC: S002

        Given: A list of packages in specific order
        When: batch_validate is called
        Then: Results are in same order as input
        """
        names = ["flask", "django", "requests"]
        results = await validate_batch(names)

        assert len(results) == 3
        assert results[0].name == "flask"
        assert results[1].name == "django"
        assert results[2].name == "requests"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_handles_mixed_validity(self) -> None:
        """
        TEST_ID: T002.08
        SPEC: S002

        Given: A list with valid and invalid package names
        When: batch_validate is called
        Then: Invalid names return HIGH_RISK (not exceptions)
        """
        names = ["flask", "", "django"]  # empty string is invalid
        results = await validate_batch(names)

        assert len(results) == 3
        assert results[0].name == "flask"
        assert results[1].recommendation == Recommendation.HIGH_RISK
        assert results[1].risk_score == 1.0
        assert results[2].name == "django"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_with_client(self) -> None:
        """
        TEST_ID: T002.09
        SPEC: S002

        Given: A mock registry client
        When: batch_validate is called
        Then: Client is called for each package
        """
        client = MockRegistryClient(downloads=100000)
        names = ["pkg1", "pkg2"]
        results = await validate_batch(names, client=client)

        assert client.call_count == 2
        assert all(r.exists for r in results)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_registry_propagates(self) -> None:
        """
        TEST_ID: T002.10
        SPEC: S002

        Given: A specific registry
        When: batch_validate is called
        Then: Registry applies to all packages
        """
        names = ["express", "lodash"]
        results = await validate_batch(names, registry="npm")

        assert all(r.registry == "npm" for r in results)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_batch_concurrency_limit(self) -> None:
        """
        TEST_ID: T002.11
        SPEC: S002

        Given: A large batch
        When: batch_validate is called with concurrency limit
        Then: Completes without error
        """
        names = [f"package-{i}" for i in range(20)]
        results = await validate_batch(names, concurrency=5)

        assert len(results) == 20


class TestNormalizePackageName:
    """Tests for normalize_package_name function.

    SPEC: S001
    """

    @pytest.mark.unit
    def test_lowercase(self) -> None:
        """Package names are lowercased."""
        assert normalize_package_name("Flask") == "flask"
        assert normalize_package_name("REQUESTS") == "requests"
        assert normalize_package_name("NumPy") == "numpy"

    @pytest.mark.unit
    def test_underscore_to_hyphen(self) -> None:
        """Underscores converted to hyphens per PEP 503."""
        assert normalize_package_name("my_package") == "my-package"
        assert normalize_package_name("foo_bar_baz") == "foo-bar-baz"

    @pytest.mark.unit
    def test_strip_whitespace(self) -> None:
        """Leading/trailing whitespace is stripped."""
        assert normalize_package_name("  flask  ") == "flask"
        assert normalize_package_name("\tpackage\n") == "package"

    @pytest.mark.unit
    def test_combined_normalization(self) -> None:
        """All normalizations apply together."""
        assert normalize_package_name("  My_Package  ") == "my-package"
        assert normalize_package_name("\tFoo_Bar_BAZ\n") == "foo-bar-baz"

    @pytest.mark.unit
    def test_already_normalized(self) -> None:
        """Already normalized names pass through unchanged."""
        assert normalize_package_name("flask") == "flask"
        assert normalize_package_name("my-package") == "my-package"


class TestSyncWrappers:
    """Tests for synchronous wrapper functions.

    SPEC: S001, S002
    """

    @pytest.mark.unit
    def test_validate_package_sync(self) -> None:
        """
        TEST_ID: T004.01
        SPEC: S001

        Sync wrapper calls async function.
        """
        result = validate_package_sync("requests")

        assert isinstance(result, PackageRisk)
        assert result.name == "requests"

    @pytest.mark.unit
    def test_validate_package_sync_invalid(self) -> None:
        """
        TEST_ID: T004.02
        SPEC: S001

        Sync wrapper propagates exceptions.
        """
        with pytest.raises(InvalidPackageNameError):
            validate_package_sync("")

    @pytest.mark.unit
    def test_validate_batch_sync(self) -> None:
        """
        TEST_ID: T004.03
        SPEC: S002

        Batch sync wrapper works.
        """
        results = validate_batch_sync(["flask", "django"])

        assert len(results) == 2
        assert results[0].name == "flask"
        assert results[1].name == "django"

    @pytest.mark.unit
    def test_validate_batch_sync_empty(self) -> None:
        """
        TEST_ID: T004.04
        SPEC: S002

        Batch sync handles empty list.
        """
        results = validate_batch_sync([])
        assert results == []

    @pytest.mark.unit
    def test_validate_batch_sync_with_client(self) -> None:
        """
        TEST_ID: T004.05
        SPEC: S002

        Batch sync wrapper accepts client.
        """
        client = MockRegistryClient()
        results = validate_batch_sync(["pkg1"], client=client)

        assert len(results) == 1
        assert client.call_count == 1


class TestSignalCombination:
    """Tests for signal combination in detection.

    SPEC: S003
    """

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_multiple_signal_sources(self) -> None:
        """
        TEST_ID: T005.01
        SPEC: S003

        Signals from multiple sources are combined.
        Note: merge_signals deduplicates by type, keeping the highest-priority
        signal of each type. This test verifies typosquat AND pattern detection.
        """
        # Test a typosquat - combines typosquat detection with popular check
        result = await validate_package("reqeusts")

        signal_types = [s.type for s in result.signals]

        # Should have typosquat signal
        assert SignalType.TYPOSQUAT in signal_types

        # Now test a suspicious pattern name
        result2 = await validate_package("flask-gpt-helper")
        signal_types2 = [s.type for s in result2.signals]

        # Should have hallucination pattern signal
        assert SignalType.HALLUCINATION_PATTERN in signal_types2

        # Risk should be higher than base
        assert result2.risk_score > 0.4

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_popular_reduces_overall_risk(self) -> None:
        """
        TEST_ID: T005.02
        SPEC: S003

        Popular packages have lower risk than suspicious ones.
        """
        popular_result = await validate_package("requests")
        suspicious_result = await validate_package("flask-gpt-helper")

        assert popular_result.risk_score < suspicious_result.risk_score

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_metadata_signals_included(self) -> None:
        """
        TEST_ID: T005.03
        SPEC: S003

        Metadata signals are included when client provided.
        """
        client = MockRegistryClient(downloads=10, releases=1)
        result = await validate_package("test-pkg", client=client)

        signal_types = [s.type for s in result.signals]

        # Should have metadata-based signals
        assert SignalType.LOW_DOWNLOADS in signal_types


class TestEdgeCases:
    """Edge case tests for detector."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_single_character_package(self) -> None:
        """Single character names are valid (e.g., 'q' package)."""
        result = await validate_package("q")
        assert result.name == "q"
        assert isinstance(result, PackageRisk)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_very_long_valid_package_name(self) -> None:
        """Long package names within limit are handled."""
        long_name = "a" * 100
        result = await validate_package(long_name)
        assert result.name == long_name

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_package_with_numbers(self) -> None:
        """Package names with numbers are valid."""
        result = await validate_package("package123")
        assert result.name == "package123"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_package_with_hyphens(self) -> None:
        """Package names with hyphens are valid."""
        result = await validate_package("my-cool-package")
        assert result.name == "my-cool-package"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_large_batch(self) -> None:
        """Large batches are handled."""
        names = [f"package-{i}" for i in range(100)]
        results = await validate_batch(names, concurrency=20)
        assert len(results) == 100

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_duplicate_names_in_batch(self) -> None:
        """Duplicate names are processed separately."""
        names = ["flask", "flask", "flask"]
        results = await validate_batch(names)

        assert len(results) == 3
        assert all(r.name == "flask" for r in results)


class TestIntegrationScenarios:
    """Integration-style tests for realistic scenarios."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_requirements_file_simulation(self) -> None:
        """Simulate validating a requirements.txt."""
        packages = ["flask", "requests", "django", "numpy", "pandas"]
        results = await validate_batch(packages)

        assert len(results) == 5
        # All popular packages should have low risk
        for result in results:
            assert result.risk_score < 0.5

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_mixed_safe_suspicious(self) -> None:
        """Mix of safe and suspicious packages."""
        packages = [
            "requests",  # Safe (popular)
            "flask-gpt-helper",  # Suspicious (pattern match)
            "reqeusts",  # Suspicious (typosquat)
        ]
        results = await validate_batch(packages)

        assert len(results) == 3
        assert results[0].risk_score < results[1].risk_score
        assert results[0].risk_score < results[2].risk_score

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_all_invalid_packages(self) -> None:
        """Batch of all invalid packages."""
        packages = ["", "-invalid", "!bad!"]
        results = await validate_batch(packages)

        assert len(results) == 3
        assert all(r.recommendation == Recommendation.HIGH_RISK for r in results)
