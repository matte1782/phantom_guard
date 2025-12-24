# SPEC: S020-S026 - PyPI Live API Integration Tests
# Gate 3: Test Design - Stubs
"""
Integration tests for PyPI registry client against live API.

SPEC_IDs: S020-S026
TEST_IDs: T020.I*
Requires network access.
"""

from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.network
class TestPyPILiveAPI:
    """Live tests against PyPI API.

    SPEC: S020-S026
    Requires: Network access to pypi.org
    """

    @pytest.mark.skip(reason="Stub - implement with S020")
    async def test_known_package_exists(self):
        """
        TEST_ID: T020.I01
        SPEC: S020
        EC: EC020

        Given: Package "flask" (known to exist)
        When: Query live PyPI API
        Then: Returns package metadata with exists=True
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S020")
    async def test_known_package_metadata_complete(self):
        """
        TEST_ID: T020.I02
        SPEC: S020

        Given: Package "requests"
        When: Query live PyPI API
        Then: Metadata includes version, author, repository
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S020")
    async def test_nonexistent_package_not_found(self):
        """
        TEST_ID: T020.I03
        SPEC: S020
        EC: EC021

        Given: Package "definitely-not-a-real-package-xyz123abc"
        When: Query live PyPI API
        Then: Returns exists=False
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S020")
    async def test_response_time_within_budget(self):
        """
        TEST_ID: T020.I04
        SPEC: S020

        Given: Package "flask"
        When: Query live PyPI API
        Then: Response time < 500ms
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S020")
    async def test_timeout_handling(self):
        """
        TEST_ID: T020.I05
        SPEC: S020
        INV: INV014
        EC: EC022

        Given: Very short timeout (10ms)
        When: Query live PyPI API
        Then: Raises RegistryTimeoutError
        """
        pass


@pytest.mark.integration
@pytest.mark.network
class TestPyPIStatsLive:
    """Live tests against pypistats.org API."""

    @pytest.mark.skip(reason="Stub - implement with S023")
    async def test_pypistats_available(self):
        """
        TEST_ID: T020.I06
        SPEC: S023

        Given: Package "requests"
        When: Query pypistats.org
        Then: Returns download count > 0
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S023")
    async def test_pypistats_nonexistent_package(self):
        """
        TEST_ID: T020.I07
        SPEC: S023

        Given: Nonexistent package
        When: Query pypistats.org
        Then: Returns None gracefully
        """
        pass
