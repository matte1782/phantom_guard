# SPEC: S027-S032 - npm Live API Integration Tests
# Gate 3: Test Design - Stubs
"""
Integration tests for npm registry client against live API.

SPEC_IDs: S027-S032
TEST_IDs: T027.I*
Requires network access.
"""

from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.network
class TestNpmLiveAPI:
    """Live tests against npm API.

    SPEC: S027-S032
    Requires: Network access to registry.npmjs.org
    """

    @pytest.mark.skip(reason="Stub - implement with S027")
    async def test_known_package_exists(self):
        """
        TEST_ID: T027.I01
        SPEC: S027
        EC: EC020

        Given: Package "express" (known to exist)
        When: Query live npm API
        Then: Returns package metadata with exists=True
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S027")
    async def test_known_package_metadata_complete(self):
        """
        TEST_ID: T027.I02
        SPEC: S027

        Given: Package "lodash"
        When: Query live npm API
        Then: Metadata includes version, author, repository
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S027")
    async def test_scoped_package_exists(self):
        """
        TEST_ID: T027.I03
        SPEC: S027

        Given: Scoped package "@types/node"
        When: Query live npm API
        Then: Returns package metadata correctly
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S027")
    async def test_nonexistent_package_not_found(self):
        """
        TEST_ID: T027.I04
        SPEC: S027
        EC: EC021

        Given: Package "definitely-not-a-real-package-xyz123abc"
        When: Query live npm API
        Then: Returns exists=False
        """
        pass
