# SPEC: S033-S039 - crates.io Live API Integration Tests
# Gate 3: Test Design - Stubs
"""
Integration tests for crates.io registry client against live API.

SPEC_IDs: S033-S039
TEST_IDs: T033.I*
Requires network access.
"""

from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.network
class TestCratesLiveAPI:
    """Live tests against crates.io API.

    SPEC: S033-S039
    Requires: Network access to crates.io
    """

    @pytest.mark.skip(reason="Stub - implement with S033")
    async def test_known_crate_exists(self):
        """
        TEST_ID: T033.I01
        SPEC: S033
        EC: EC020

        Given: Crate "serde" (known to exist)
        When: Query live crates.io API
        Then: Returns package metadata with exists=True
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S033")
    async def test_known_crate_metadata_complete(self):
        """
        TEST_ID: T033.I02
        SPEC: S033

        Given: Crate "tokio"
        When: Query live crates.io API
        Then: Metadata includes version, repository, downloads
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S033")
    async def test_nonexistent_crate_not_found(self):
        """
        TEST_ID: T033.I03
        SPEC: S033
        EC: EC021

        Given: Crate "definitely-not-a-real-crate-xyz123abc"
        When: Query live crates.io API
        Then: Returns exists=False
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S033")
    async def test_user_agent_sent(self):
        """
        TEST_ID: T033.I04
        SPEC: S033
        INV: INV015

        Given: Any crates.io request
        When: Request sent
        Then: User-Agent header is present (required by crates.io)
        """
        pass
