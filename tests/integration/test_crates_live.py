# SPEC: S033-S039 - crates.io Live API Integration Tests
"""
Integration tests for crates.io registry client against live API.

SPEC_IDs: S033-S039
TEST_IDs: T033.I01-I06
Requires network access.

NOTE: These tests hit real APIs and should be run sparingly.
Use pytest -m "integration and network" to run them.
"""

from __future__ import annotations

import time

import pytest

from phantom_guard.registry import CratesClient
from phantom_guard.registry.exceptions import RegistryTimeoutError


@pytest.mark.integration
@pytest.mark.network
class TestCratesLiveAPI:
    """Live tests against crates.io API.

    SPEC: S033-S039
    Requires: Network access to crates.io
    """

    @pytest.mark.asyncio
    async def test_known_crate_exists(self) -> None:
        """
        TEST_ID: T033.I01
        SPEC: S033
        EC: EC020

        Given: Crate "serde" (known to exist)
        When: Query live crates.io API
        Then: Returns crate metadata with exists=True
        """
        async with CratesClient() as client:
            metadata = await client.get_package_metadata("serde")

            assert metadata.exists is True
            assert metadata.name == "serde"
            assert metadata.registry == "crates"

    @pytest.mark.asyncio
    async def test_known_crate_metadata_complete(self) -> None:
        """
        TEST_ID: T033.I02
        SPEC: S033

        Given: Crate "tokio"
        When: Query live crates.io API
        Then: Metadata includes version, downloads, repository
        """
        async with CratesClient() as client:
            metadata = await client.get_package_metadata("tokio")

            assert metadata.exists is True
            assert metadata.latest_version is not None
            assert metadata.release_count is not None
            assert metadata.release_count > 0
            # tokio has downloads in the API response
            assert metadata.downloads_last_month is not None
            # tokio has a repository URL
            assert metadata.repository_url is not None

    @pytest.mark.asyncio
    async def test_nonexistent_crate_not_found(self) -> None:
        """
        TEST_ID: T033.I03
        SPEC: S033
        EC: EC021

        Given: Crate "definitely-not-a-real-crate-xyz123abc"
        When: Query live crates.io API
        Then: Returns exists=False
        """
        async with CratesClient() as client:
            metadata = await client.get_package_metadata(
                "definitely-not-a-real-crate-xyz123abc-phantom-guard-test"
            )

            assert metadata.exists is False
            assert metadata.registry == "crates"

    @pytest.mark.asyncio
    async def test_response_time_within_budget(self) -> None:
        """
        TEST_ID: T033.I04
        SPEC: S033
        INV: INV014

        Given: Crate "serde"
        When: Query live crates.io API
        Then: Response time < 5s (within timeout budget)
        """
        async with CratesClient(timeout=5.0) as client:
            start = time.perf_counter()
            await client.get_package_metadata("serde")
            elapsed = time.perf_counter() - start

            # Should complete within 5 seconds
            assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_timeout_handling(self) -> None:
        """
        TEST_ID: T033.I05
        SPEC: S033
        INV: INV014
        EC: EC022

        Given: Very short timeout (0.001s = 1ms)
        When: Query live crates.io API
        Then: Raises RegistryTimeoutError
        """
        async with CratesClient(timeout=0.001) as client:
            with pytest.raises(RegistryTimeoutError) as exc_info:
                await client.get_package_metadata("serde")

            assert exc_info.value.registry == "crates.io"

    @pytest.mark.asyncio
    async def test_user_agent_header_included(self) -> None:
        """
        TEST_ID: T033.I06
        SPEC: S033
        INV: INV015

        Given: Custom user agent
        When: Query crates.io
        Then: Request succeeds (crates.io requires User-Agent)

        Note: crates.io requires User-Agent header. If missing,
        it returns 403 Forbidden.
        """
        async with CratesClient() as client:
            # If user agent is missing, this would fail with 403
            metadata = await client.get_package_metadata("rand")

            assert metadata.exists is True
            assert metadata.name == "rand"
