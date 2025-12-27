# SPEC: S027-S032 - npm Live API Integration Tests
"""
Integration tests for npm registry client against live API.

SPEC_IDs: S027-S032
TEST_IDs: T027.I01-I06
Requires network access.

NOTE: These tests hit real APIs and should be run sparingly.
Use pytest -m "integration and network" to run them.
"""

from __future__ import annotations

import time

import pytest

from phantom_guard.registry import NpmClient
from phantom_guard.registry.exceptions import RegistryTimeoutError


@pytest.mark.integration
@pytest.mark.network
class TestNpmLiveAPI:
    """Live tests against npm registry API.

    SPEC: S027-S032
    Requires: Network access to registry.npmjs.org
    """

    @pytest.mark.asyncio
    async def test_known_package_exists(self) -> None:
        """
        TEST_ID: T027.I01
        SPEC: S027
        EC: EC020

        Given: Package "express" (known to exist)
        When: Query live npm API
        Then: Returns package metadata with exists=True
        """
        async with NpmClient() as client:
            metadata = await client.get_package_metadata("express")

            assert metadata.exists is True
            assert metadata.name == "express"
            assert metadata.registry == "npm"

    @pytest.mark.asyncio
    async def test_scoped_package_exists(self) -> None:
        """
        TEST_ID: T027.I02
        SPEC: S027

        Given: Scoped package "@types/node"
        When: Query live npm API
        Then: Returns package metadata with exists=True
        """
        async with NpmClient() as client:
            metadata = await client.get_package_metadata("@types/node")

            assert metadata.exists is True
            assert "@types/node" in metadata.name
            assert metadata.registry == "npm"

    @pytest.mark.asyncio
    async def test_nonexistent_package_not_found(self) -> None:
        """
        TEST_ID: T027.I03
        SPEC: S027
        EC: EC021

        Given: Package "definitely-not-a-real-package-xyz123abc"
        When: Query live npm API
        Then: Returns exists=False
        """
        async with NpmClient() as client:
            metadata = await client.get_package_metadata(
                "definitely-not-a-real-package-xyz123abc-phantom-guard-test"
            )

            assert metadata.exists is False
            assert metadata.registry == "npm"

    @pytest.mark.asyncio
    async def test_response_time_within_budget(self) -> None:
        """
        TEST_ID: T027.I04
        SPEC: S027
        INV: INV014

        Given: Package "lodash"
        When: Query live npm API
        Then: Response time < 5s (within timeout budget)
        """
        async with NpmClient(timeout=5.0) as client:
            start = time.perf_counter()
            await client.get_package_metadata("lodash")
            elapsed = time.perf_counter() - start

            # Should complete within 5 seconds
            assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_timeout_handling(self) -> None:
        """
        TEST_ID: T027.I05
        SPEC: S027
        INV: INV014
        EC: EC022

        Given: Very short timeout (0.001s = 1ms)
        When: Query live npm API
        Then: Raises RegistryTimeoutError
        """
        async with NpmClient(timeout=0.001) as client:
            with pytest.raises(RegistryTimeoutError) as exc_info:
                await client.get_package_metadata("express")

            assert exc_info.value.registry == "npm"

    @pytest.mark.asyncio
    async def test_downloads_available(self) -> None:
        """
        TEST_ID: T027.I06
        SPEC: S029

        Given: Popular package "express"
        When: Query npm downloads API
        Then: Returns download count > 0
        """
        async with NpmClient() as client:
            downloads = await client.get_downloads("express")

            # express is very popular
            assert downloads is not None
            assert downloads > 0
