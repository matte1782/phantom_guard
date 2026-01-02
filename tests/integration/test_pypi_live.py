# SPEC: S020-S026 - PyPI Live API Integration Tests
"""
Integration tests for PyPI registry client against live API.

SPEC_IDs: S020-S026
TEST_IDs: T020.I01-I07
Requires network access.

NOTE: These tests hit real APIs and should be run sparingly.
Use pytest -m "integration and network" to run them.
"""

from __future__ import annotations

import time

import pytest

from phantom_guard.registry import PyPIClient
from phantom_guard.registry.exceptions import RegistryTimeoutError


@pytest.mark.integration
@pytest.mark.network
class TestPyPILiveAPI:
    """Live tests against PyPI API.

    SPEC: S020-S026
    Requires: Network access to pypi.org
    """

    @pytest.mark.asyncio
    async def test_known_package_exists(self) -> None:
        """
        TEST_ID: T020.I01
        SPEC: S020
        EC: EC020

        Given: Package "flask" (known to exist)
        When: Query live PyPI API
        Then: Returns package metadata with exists=True
        """
        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("flask")

            assert metadata.exists is True
            assert metadata.name.lower() == "flask"
            assert metadata.registry == "pypi"

    @pytest.mark.asyncio
    async def test_known_package_metadata_complete(self) -> None:
        """
        TEST_ID: T020.I02
        SPEC: S020

        Given: Package "requests"
        When: Query live PyPI API
        Then: Metadata includes version, author, repository
        """
        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("requests")

            assert metadata.exists is True
            assert metadata.latest_version is not None
            assert metadata.release_count is not None
            assert metadata.release_count > 0
            # requests has a known repository URL
            assert metadata.repository_url is not None

    @pytest.mark.asyncio
    async def test_nonexistent_package_not_found(self) -> None:
        """
        TEST_ID: T020.I03
        SPEC: S020
        EC: EC021

        Given: Package "definitely-not-a-real-package-xyz123abc"
        When: Query live PyPI API
        Then: Returns exists=False
        """
        async with PyPIClient() as client:
            metadata = await client.get_package_metadata(
                "definitely-not-a-real-package-xyz123abc-phantom-guard-test"
            )

            assert metadata.exists is False
            assert metadata.registry == "pypi"

    @pytest.mark.asyncio
    async def test_response_time_within_budget(self) -> None:
        """
        TEST_ID: T020.I04
        SPEC: S020
        INV: INV014

        Given: Package "flask"
        When: Query live PyPI API
        Then: Response time < 5s (within timeout budget)
        """
        async with PyPIClient(timeout=5.0) as client:
            start = time.perf_counter()
            await client.get_package_metadata("flask")
            elapsed = time.perf_counter() - start

            # Should complete within 5 seconds
            assert elapsed < 5.0

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Flaky on CI - timeout behavior depends on network/caching conditions")
    async def test_timeout_handling(self) -> None:
        """
        TEST_ID: T020.I05
        SPEC: S020
        INV: INV014
        EC: EC022

        Given: Very short timeout (0.001s = 1ms)
        When: Query live PyPI API
        Then: Raises RegistryTimeoutError

        Note: Skipped on CI due to flakiness - fast networks or OS-level
        caching can cause the request to succeed within 1ms.
        """
        async with PyPIClient(timeout=0.001) as client:
            with pytest.raises(RegistryTimeoutError) as exc_info:
                await client.get_package_metadata("flask")

            assert exc_info.value.registry == "pypi"

    @pytest.mark.asyncio
    async def test_normalized_package_name(self) -> None:
        """
        TEST_ID: T020.I08
        SPEC: S020

        Given: Package name with underscores "typing_extensions"
        When: Query live PyPI API
        Then: Correctly normalizes and returns metadata
        """
        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("typing_extensions")

            assert metadata.exists is True
            # Name is normalized (may have hyphen or underscore)
            assert "typing" in metadata.name.lower()


@pytest.mark.integration
@pytest.mark.network
class TestPyPIStatsLive:
    """Live tests against pypistats.org API."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Flaky on CI - pypistats.org API can be unavailable or rate-limited")
    async def test_pypistats_available(self) -> None:
        """
        TEST_ID: T020.I06
        SPEC: S023

        Given: Package "requests"
        When: Query pypistats.org
        Then: Returns download count > 0

        Note: Skipped on CI due to pypistats.org API reliability issues.
        """
        async with PyPIClient() as client:
            downloads = await client.get_downloads("requests")

            # requests is one of the most downloaded packages
            assert downloads is not None
            assert downloads > 0

    @pytest.mark.asyncio
    async def test_pypistats_nonexistent_package(self) -> None:
        """
        TEST_ID: T020.I07
        SPEC: S023

        Given: Nonexistent package
        When: Query pypistats.org
        Then: Returns None gracefully
        """
        async with PyPIClient() as client:
            downloads = await client.get_downloads(
                "definitely-not-a-real-package-xyz123abc-phantom-guard-test"
            )

            # Should return None, not raise
            assert downloads is None

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Flaky on CI - pypistats.org API can be unavailable or rate-limited")
    async def test_metadata_with_downloads(self) -> None:
        """
        TEST_ID: T020.I09
        SPEC: S020, S023

        Given: Popular package "flask"
        When: Get metadata with downloads
        Then: Both metadata and downloads are returned

        Note: Skipped on CI due to pypistats.org API reliability issues.
        """
        async with PyPIClient() as client:
            metadata = await client.get_package_metadata_with_downloads("flask")

            assert metadata.exists is True
            assert metadata.name.lower() == "flask"
            # Flask should have downloads (it's very popular)
            assert metadata.downloads_last_month is not None
            assert metadata.downloads_last_month > 0
