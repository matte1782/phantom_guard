# SPEC: S033-S039 - crates.io Registry Client
# Gate 3: Test Design - Implementation
"""
Unit tests for the crates.io registry client.

SPEC_IDs: S033-S039
TEST_IDs: T033.*
INVARIANTS: INV013, INV014, INV015
EDGE_CASES: EC020-EC034
"""

from __future__ import annotations

import httpx
import pytest
import respx

from phantom_guard.registry.crates import USER_AGENT, CratesClient
from phantom_guard.registry.exceptions import (
    RegistryParseError,
    RegistryRateLimitError,
    RegistryTimeoutError,
    RegistryUnavailableError,
)


class TestCratesClient:
    """Tests for crates.io registry client.

    SPEC: S033-S039 - crates.io client
    Total tests: 13 (8 unit, 4 integration, 1 bench)
    """

    # =========================================================================
    # SUCCESSFUL RESPONSE TESTS
    # =========================================================================

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_exists_returns_metadata(self) -> None:
        """
        TEST_ID: T033.01
        SPEC: S033
        INV: INV013
        EC: EC020

        Given: Crate "serde" exists on crates.io
        When: get_package is called
        Then: Returns PackageMetadata with exists=True
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(
                200,
                json={
                    "crate": {
                        "name": "serde",
                        "newest_version": "1.0.193",
                        "created_at": "2015-03-05T00:00:00Z",
                        "recent_downloads": 50000000,
                        "description": "A serialization framework",
                    },
                    "versions": [{"num": "1.0.193"}],
                },
            )
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("serde")

        assert metadata.exists is True
        assert metadata.name == "serde"

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_not_found_returns_not_exists(self) -> None:
        """
        TEST_ID: T033.02
        SPEC: S033
        INV: INV013
        EC: EC021

        Given: Crate does not exist on crates.io
        When: get_package is called
        Then: Returns PackageMetadata with exists=False
        """
        respx.get("https://crates.io/api/v1/crates/nonexistent-crate-xyz123").mock(
            return_value=httpx.Response(404)
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("nonexistent-crate-xyz123")

        assert metadata.exists is False
        assert metadata.name == "nonexistent-crate-xyz123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_metadata_fields(self) -> None:
        """
        TEST_ID: T033.03
        SPEC: S033

        Given: Crate exists with full metadata
        When: get_package is called
        Then: Metadata contains name, version, repository, downloads
        """
        respx.get("https://crates.io/api/v1/crates/tokio").mock(
            return_value=httpx.Response(
                200,
                json={
                    "crate": {
                        "name": "tokio",
                        "newest_version": "1.35.0",
                        "created_at": "2016-08-14T12:00:00Z",
                        "recent_downloads": 30000000,
                        "repository": "https://github.com/tokio-rs/tokio",
                        "description": "Async runtime for Rust",
                    },
                    "versions": [
                        {"num": "1.35.0"},
                        {"num": "1.34.0"},
                        {"num": "1.33.0"},
                    ],
                },
            )
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("tokio")

        assert metadata.name == "tokio"
        assert metadata.exists is True
        assert metadata.latest_version == "1.35.0"
        assert metadata.release_count == 3
        assert metadata.downloads_last_month == 30000000
        assert metadata.repository_url == "https://github.com/tokio-rs/tokio"
        assert metadata.description == "Async runtime for Rust"
        assert metadata.created_at is not None

    # =========================================================================
    # USER-AGENT HEADER TESTS (INV015)
    # =========================================================================

    @pytest.mark.asyncio
    @respx.mock
    async def test_user_agent_header_included(self) -> None:
        """
        TEST_ID: T033.04
        SPEC: S033
        INV: INV015

        Given: Any crates.io request
        When: Request is made
        Then: User-Agent header is present
        """
        route = respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(200, json={"crate": {"name": "serde"}, "versions": []})
        )

        async with CratesClient() as client:
            await client.get_package_metadata("serde")

        # Verify User-Agent was sent
        assert route.called
        request = route.calls[0].request
        assert "User-Agent" in request.headers
        assert "PhantomGuard" in request.headers["User-Agent"]

    def test_user_agent_format(self) -> None:
        """
        TEST_ID: T033.05
        SPEC: S033
        INV: INV015

        Given: User-Agent header
        When: Inspecting format
        Then: Contains project name and contact info
        """
        assert "PhantomGuard" in USER_AGENT
        assert "/" in USER_AGENT  # Has version
        assert "github" in USER_AGENT.lower()  # Has contact URL

    # =========================================================================
    # ERROR HANDLING TESTS
    # =========================================================================

    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_raises_error(self) -> None:
        """
        TEST_ID: T033.06
        SPEC: S033
        INV: INV014
        EC: EC022

        Given: crates.io API does not respond within timeout
        When: get_package is called
        Then: Raises RegistryTimeoutError
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            side_effect=httpx.TimeoutException("Connection timed out")
        )

        async with CratesClient() as client:
            with pytest.raises(RegistryTimeoutError) as exc_info:
                await client.get_package_metadata("serde")

        assert exc_info.value.registry == "crates.io"

    @pytest.mark.asyncio
    @respx.mock
    async def test_server_error_raises_unavailable(self) -> None:
        """
        TEST_ID: T033.07
        SPEC: S033
        EC: EC023

        Given: crates.io returns 500 error
        When: get_package is called
        Then: Raises RegistryUnavailableError
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(return_value=httpx.Response(500))

        async with CratesClient() as client:
            with pytest.raises(RegistryUnavailableError) as exc_info:
                await client.get_package_metadata("serde")

        assert exc_info.value.registry == "crates.io"
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_raises_error(self) -> None:
        """
        TEST_ID: T033.08
        SPEC: S033
        EC: EC025

        Given: crates.io returns 429 error
        When: get_package is called
        Then: Raises RegistryRateLimitError
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "120"})
        )

        async with CratesClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("serde")

        assert exc_info.value.registry == "crates.io"
        assert exc_info.value.retry_after == 120

    @pytest.mark.asyncio
    @respx.mock
    async def test_invalid_json_raises_parse_error(self) -> None:
        """
        TEST_ID: T033.09
        SPEC: S033
        EC: EC026

        Given: crates.io returns invalid JSON
        When: get_package is called
        Then: Raises RegistryParseError
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(200, content=b"not valid json")
        )

        async with CratesClient() as client:
            with pytest.raises(RegistryParseError) as exc_info:
                await client.get_package_metadata("serde")

        assert exc_info.value.registry == "crates.io"


class TestCratesURL:
    """Tests for crates.io URL construction."""

    def test_api_url_format(self) -> None:
        """
        TEST_ID: T033.10
        SPEC: S033

        Given: Crate name "serde"
        When: Constructing API URL
        Then: Returns "https://crates.io/api/v1/crates/serde"
        """
        client = CratesClient()
        url = client._get_api_url("serde")
        assert url == "https://crates.io/api/v1/crates/serde"

    def test_crate_name_normalization(self) -> None:
        """
        TEST_ID: T033.11
        SPEC: S033

        Given: Crate name with uppercase
        When: Constructing API URL
        Then: URL is lowercase normalized
        """
        client = CratesClient()
        url = client._get_api_url("Serde")
        assert url == "https://crates.io/api/v1/crates/serde"


class TestCratesDownloads:
    """Tests for crates.io download count parsing."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_downloads_from_response(self) -> None:
        """
        TEST_ID: T033.12
        SPEC: S033

        Given: Crate response with downloads field
        When: Parsing metadata
        Then: Downloads count is extracted
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(
                200,
                json={
                    "crate": {
                        "name": "serde",
                        "recent_downloads": 50000000,
                    },
                    "versions": [],
                },
            )
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("serde")

        assert metadata.downloads_last_month == 50000000

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_downloads_field(self) -> None:
        """
        TEST_ID: T033.13
        SPEC: S033

        Given: Crate response without downloads field
        When: Parsing metadata
        Then: Returns None for downloads
        """
        respx.get("https://crates.io/api/v1/crates/obscure-crate").mock(
            return_value=httpx.Response(
                200,
                json={
                    "crate": {
                        "name": "obscure-crate",
                    },
                    "versions": [],
                },
            )
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("obscure-crate")

        assert metadata.downloads_last_month is None


class TestCratesClientErrors:
    """Tests for crates.io client error handling edge cases."""

    @pytest.mark.asyncio
    async def test_client_not_initialized_raises_runtime_error(self) -> None:
        """
        TEST_ID: T033.14
        SPEC: S033

        Given: CratesClient not used as context manager
        When: get_package_metadata is called
        Then: Raises RuntimeError
        """
        client = CratesClient()
        with pytest.raises(RuntimeError) as exc_info:
            await client.get_package_metadata("serde")
        assert "context" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @respx.mock
    async def test_network_error_raises_unavailable(self) -> None:
        """
        TEST_ID: T033.15
        SPEC: S033

        Given: Network connection error
        When: get_package_metadata is called
        Then: Raises RegistryUnavailableError
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with CratesClient() as client:
            with pytest.raises(RegistryUnavailableError):
                await client.get_package_metadata("serde")

    @pytest.mark.asyncio
    async def test_get_owners_without_context_returns_none(self) -> None:
        """
        TEST_ID: T033.16
        SPEC: S035

        Given: CratesClient not used as context manager
        When: get_owners is called
        Then: Returns None (graceful degradation)
        """
        client = CratesClient()
        result = await client.get_owners("serde")
        assert result is None


class TestCratesOwners:
    """Tests for crates.io owners API."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_owners_success(self) -> None:
        """
        TEST_ID: T033.17
        SPEC: S035

        Given: Crate with owners endpoint
        When: get_owners is called
        Then: Returns owner count
        """
        respx.get("https://crates.io/api/v1/crates/serde/owners").mock(
            return_value=httpx.Response(
                200,
                json={
                    "users": [
                        {"id": 1, "login": "dtolnay"},
                        {"id": 2, "login": "erickt"},
                    ]
                },
            )
        )

        async with CratesClient() as client:
            owner_count = await client.get_owners("serde")

        assert owner_count == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_owners_unavailable_returns_none(self) -> None:
        """
        TEST_ID: T033.18
        SPEC: S035

        Given: Owners endpoint returns error
        When: get_owners is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://crates.io/api/v1/crates/serde/owners").mock(
            return_value=httpx.Response(500)
        )

        async with CratesClient() as client:
            owner_count = await client.get_owners("serde")

        assert owner_count is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_owners_timeout_returns_none(self) -> None:
        """
        TEST_ID: T033.19
        SPEC: S035

        Given: Owners endpoint times out
        When: get_owners is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://crates.io/api/v1/crates/serde/owners").mock(
            side_effect=httpx.TimeoutException("Timeout")
        )

        async with CratesClient() as client:
            owner_count = await client.get_owners("serde")

        assert owner_count is None


class TestCratesMetadataWithOwners:
    """Tests for combined metadata + owners."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_owners_success(self) -> None:
        """
        TEST_ID: T033.20
        SPEC: S033, S035

        Given: Crate exists with owners available
        When: get_package_metadata_with_owners is called
        Then: Returns metadata with maintainer_count included
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(
                200,
                json={
                    "crate": {
                        "name": "serde",
                        "newest_version": "1.0.193",
                        "recent_downloads": 50000000,
                    },
                    "versions": [{"num": "1.0.193"}],
                },
            )
        )
        respx.get("https://crates.io/api/v1/crates/serde/owners").mock(
            return_value=httpx.Response(
                200,
                json={
                    "users": [
                        {"id": 1, "login": "dtolnay"},
                        {"id": 2, "login": "erickt"},
                    ]
                },
            )
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata_with_owners("serde")

        assert metadata.exists is True
        assert metadata.name == "serde"
        assert metadata.maintainer_count == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_owners_not_found(self) -> None:
        """
        TEST_ID: T033.21
        SPEC: S033, S035

        Given: Crate does not exist
        When: get_package_metadata_with_owners is called
        Then: Returns metadata with exists=False
        """
        respx.get("https://crates.io/api/v1/crates/nonexistent-xyz").mock(
            return_value=httpx.Response(404)
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata_with_owners("nonexistent-xyz")

        assert metadata.exists is False
        assert metadata.maintainer_count is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_owners_unavailable(self) -> None:
        """
        TEST_ID: T033.22
        SPEC: S033, S035

        Given: Crate exists but owners API unavailable
        When: get_package_metadata_with_owners is called
        Then: Returns metadata with maintainer_count=None
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(
                200,
                json={
                    "crate": {"name": "serde"},
                    "versions": [],
                },
            )
        )
        respx.get("https://crates.io/api/v1/crates/serde/owners").mock(
            return_value=httpx.Response(503)
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata_with_owners("serde")

        assert metadata.exists is True
        assert metadata.maintainer_count is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response_handled(self) -> None:
        """
        TEST_ID: T033.23
        SPEC: S034

        Given: crates.io returns empty JSON object
        When: get_package_metadata is called
        Then: Returns metadata with exists=True and default values
        """
        respx.get("https://crates.io/api/v1/crates/empty-crate").mock(
            return_value=httpx.Response(200, json={})
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("empty-crate")

        assert metadata.exists is True
        assert metadata.name == "empty-crate"

    @pytest.mark.asyncio
    @respx.mock
    async def test_custom_user_agent(self) -> None:
        """
        TEST_ID: T033.24
        SPEC: S033
        INV: INV015

        Given: CratesClient with custom user agent
        When: Request is made
        Then: Custom User-Agent header is used
        """
        custom_ua = "CustomApp/1.0.0"
        route = respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(200, json={"crate": {"name": "serde"}, "versions": []})
        )

        async with CratesClient(user_agent=custom_ua) as client:
            await client.get_package_metadata("serde")

        request = route.calls[0].request
        assert request.headers["User-Agent"] == custom_ua


class TestCratesContextManager:
    """Tests for context manager edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_client_provided_not_closed_on_exit(self) -> None:
        """
        TEST_ID: T033.27
        SPEC: S033

        Given: CratesClient initialized with external httpx client
        When: Context manager exits
        Then: External client is NOT closed (_owns_client=False)
        """
        external_client = httpx.AsyncClient(timeout=10.0)
        try:
            respx.get("https://crates.io/api/v1/crates/serde").mock(
                return_value=httpx.Response(200, json={"crate": {"name": "serde"}, "versions": []})
            )

            async with CratesClient(client=external_client) as client:
                metadata = await client.get_package_metadata("serde")
                assert metadata.exists is True

            # External client should still be usable (not closed)
            assert not external_client.is_closed
        finally:
            await external_client.aclose()

    @pytest.mark.asyncio
    @respx.mock
    async def test_client_provided_uses_existing_client(self) -> None:
        """
        TEST_ID: T033.28
        SPEC: S033

        Given: CratesClient initialized with external httpx client
        When: Entering context manager
        Then: Uses the provided client, doesn't create new one
        """
        external_client = httpx.AsyncClient(timeout=10.0)
        try:
            respx.get("https://crates.io/api/v1/crates/tokio").mock(
                return_value=httpx.Response(200, json={"crate": {"name": "tokio"}, "versions": []})
            )

            crates_client = CratesClient(client=external_client)
            # Before entering, _client should be the external client
            assert crates_client._client is external_client
            assert crates_client._owns_client is False

            async with crates_client as client:
                # Inside context, _client should still be the external client
                assert client._client is external_client
                await client.get_package_metadata("tokio")
        finally:
            await external_client.aclose()


class TestCratesRateLimitEdgeCases:
    """Tests for rate limit header parsing edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_invalid_retry_after_header(self) -> None:
        """
        TEST_ID: T033.29
        SPEC: S033
        EC: EC025

        Given: crates.io returns 429 with invalid Retry-After header
        When: get_package_metadata is called
        Then: Raises RegistryRateLimitError with retry_after=None
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "not-a-number"})
        )

        async with CratesClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("serde")

        assert exc_info.value.registry == "crates.io"
        assert exc_info.value.retry_after is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_no_retry_after_header(self) -> None:
        """
        TEST_ID: T033.30
        SPEC: S033
        EC: EC025

        Given: crates.io returns 429 without Retry-After header
        When: get_package_metadata is called
        Then: Raises RegistryRateLimitError with retry_after=None
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(return_value=httpx.Response(429))

        async with CratesClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("serde")

        assert exc_info.value.registry == "crates.io"
        assert exc_info.value.retry_after is None


class TestCratesInvalidDataTypes:
    """Tests for invalid data type handling."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_downloads_non_integer_returns_none(self) -> None:
        """
        TEST_ID: T033.31
        SPEC: S034

        Given: crates.io returns non-integer recent_downloads field
        When: get_package_metadata is called
        Then: Returns metadata with downloads_last_month=None
        """
        respx.get("https://crates.io/api/v1/crates/bad-downloads").mock(
            return_value=httpx.Response(
                200,
                json={
                    "crate": {
                        "name": "bad-downloads",
                        "recent_downloads": "not-a-number",
                    },
                    "versions": [],
                },
            )
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("bad-downloads")

        assert metadata.exists is True
        assert metadata.downloads_last_month is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_owners_users_not_list_returns_none(self) -> None:
        """
        TEST_ID: T033.32
        SPEC: S035

        Given: Owners API returns users as non-list
        When: get_owners is called
        Then: Returns None
        """
        respx.get("https://crates.io/api/v1/crates/serde/owners").mock(
            return_value=httpx.Response(
                200,
                json={"users": "not-a-list"},
            )
        )

        async with CratesClient() as client:
            owner_count = await client.get_owners("serde")

        assert owner_count is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_owners_invalid_json_returns_none(self) -> None:
        """
        TEST_ID: T033.33
        SPEC: S035

        Given: Owners API returns invalid JSON
        When: get_owners is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://crates.io/api/v1/crates/serde/owners").mock(
            return_value=httpx.Response(200, content=b"not valid json")
        )

        async with CratesClient() as client:
            owner_count = await client.get_owners("serde")

        assert owner_count is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_owners_network_error_returns_none(self) -> None:
        """
        TEST_ID: T033.34
        SPEC: S035

        Given: Owners API has network error
        When: get_owners is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://crates.io/api/v1/crates/serde/owners").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with CratesClient() as client:
            owner_count = await client.get_owners("serde")

        assert owner_count is None


class TestCratesRegistryField:
    """Tests to verify registry field is correctly set."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_registry_field_set_on_exists(self) -> None:
        """
        TEST_ID: T033.25
        SPEC: S033

        Given: Crate exists on crates.io
        When: get_package_metadata is called
        Then: Returns metadata with registry="crates"
        """
        respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(200, json={"crate": {"name": "serde"}, "versions": []})
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("serde")

        assert metadata.registry == "crates"

    @pytest.mark.asyncio
    @respx.mock
    async def test_registry_field_set_on_not_found(self) -> None:
        """
        TEST_ID: T033.26
        SPEC: S033

        Given: Crate does not exist on crates.io
        When: get_package_metadata is called
        Then: Returns metadata with registry="crates"
        """
        respx.get("https://crates.io/api/v1/crates/nonexistent").mock(
            return_value=httpx.Response(404)
        )

        async with CratesClient() as client:
            metadata = await client.get_package_metadata("nonexistent")

        assert metadata.registry == "crates"
