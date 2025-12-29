# SPEC: S027-S032 - npm Registry Client
# Gate 3: Test Design - Implementation
"""
Unit tests for the npm registry client.

SPEC_IDs: S027-S032
TEST_IDs: T027.*
INVARIANTS: INV013, INV014
EDGE_CASES: EC020-EC034
"""

from __future__ import annotations

import httpx
import pytest
import respx

from phantom_guard.registry.exceptions import (
    RegistryParseError,
    RegistryRateLimitError,
    RegistryTimeoutError,
    RegistryUnavailableError,
)
from phantom_guard.registry.npm import NpmClient


class TestNpmClient:
    """Tests for npm registry client.

    SPEC: S027-S032 - npm client
    Total tests: 13 (8 unit, 4 integration, 1 bench)
    """

    # =========================================================================
    # SUCCESSFUL RESPONSE TESTS
    # =========================================================================

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_exists_returns_metadata(self) -> None:
        """
        TEST_ID: T027.01
        SPEC: S027
        INV: INV013
        EC: EC020

        Given: Package "express" exists on npm
        When: get_package is called
        Then: Returns PackageMetadata with exists=True
        """
        respx.get("https://registry.npmjs.org/express").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "express",
                    "dist-tags": {"latest": "4.18.2"},
                    "time": {"created": "2010-12-29T19:38:25.450Z"},
                    "versions": {"4.18.2": {}},
                    "maintainers": [{"name": "dougwilson"}],
                    "description": "Fast web framework",
                },
            )
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("express")

        assert metadata.exists is True
        assert metadata.name == "express"

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_not_found_returns_not_exists(self) -> None:
        """
        TEST_ID: T027.02
        SPEC: S027
        INV: INV013
        EC: EC021

        Given: Package does not exist on npm
        When: get_package is called
        Then: Returns PackageMetadata with exists=False
        """
        respx.get("https://registry.npmjs.org/nonexistent-package-xyz123").mock(
            return_value=httpx.Response(404)
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("nonexistent-package-xyz123")

        assert metadata.exists is False
        assert metadata.name == "nonexistent-package-xyz123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_scoped_package_handled(self) -> None:
        """
        TEST_ID: T027.03
        SPEC: S027

        Given: Scoped package "@types/node"
        When: get_package is called
        Then: Returns correct metadata
        """
        respx.get("https://registry.npmjs.org/@types%2Fnode").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "@types/node",
                    "dist-tags": {"latest": "20.10.0"},
                    "time": {"created": "2016-07-31T12:00:00Z"},
                    "versions": {"20.10.0": {}},
                    "maintainers": [{"name": "types"}],
                },
            )
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("@types/node")

        assert metadata.exists is True
        assert metadata.name == "@types/node"

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_metadata_fields(self) -> None:
        """
        TEST_ID: T027.04
        SPEC: S027

        Given: Package exists with full metadata
        When: get_package is called
        Then: Metadata contains name, version, author, repo, etc.
        """
        respx.get("https://registry.npmjs.org/lodash").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "lodash",
                    "description": "Lodash modular utilities.",
                    "dist-tags": {"latest": "4.17.21"},
                    "time": {"created": "2012-04-23T16:13:12.054Z"},
                    "versions": {"4.17.21": {}, "4.17.20": {}, "4.17.19": {}},
                    "maintainers": [
                        {"name": "jdalton"},
                        {"name": "mathias"},
                    ],
                    "repository": {
                        "type": "git",
                        "url": "git+https://github.com/lodash/lodash.git",
                    },
                },
            )
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("lodash")

        assert metadata.name == "lodash"
        assert metadata.exists is True
        assert metadata.latest_version == "4.17.21"
        assert metadata.release_count == 3
        assert metadata.maintainer_count == 2
        assert metadata.description == "Lodash modular utilities."
        assert metadata.repository_url == "https://github.com/lodash/lodash"
        assert metadata.created_at is not None

    # =========================================================================
    # ERROR HANDLING TESTS
    # =========================================================================

    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_raises_error(self) -> None:
        """
        TEST_ID: T027.05
        SPEC: S027
        INV: INV014
        EC: EC022

        Given: npm API does not respond within timeout
        When: get_package is called
        Then: Raises RegistryTimeoutError
        """
        respx.get("https://registry.npmjs.org/express").mock(
            side_effect=httpx.TimeoutException("Connection timed out")
        )

        async with NpmClient() as client:
            with pytest.raises(RegistryTimeoutError) as exc_info:
                await client.get_package_metadata("express")

        assert exc_info.value.registry == "npm"

    @pytest.mark.asyncio
    @respx.mock
    async def test_server_error_raises_unavailable(self) -> None:
        """
        TEST_ID: T027.06
        SPEC: S027
        EC: EC023

        Given: npm returns 500 error
        When: get_package is called
        Then: Raises RegistryUnavailableError
        """
        respx.get("https://registry.npmjs.org/express").mock(return_value=httpx.Response(500))

        async with NpmClient() as client:
            with pytest.raises(RegistryUnavailableError) as exc_info:
                await client.get_package_metadata("express")

        assert exc_info.value.registry == "npm"
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_raises_error(self) -> None:
        """
        TEST_ID: T027.07
        SPEC: S027
        EC: EC025

        Given: npm returns 429 error
        When: get_package is called
        Then: Raises RegistryRateLimitError
        """
        respx.get("https://registry.npmjs.org/express").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "60"})
        )

        async with NpmClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("express")

        assert exc_info.value.registry == "npm"
        assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    @respx.mock
    async def test_invalid_json_raises_parse_error(self) -> None:
        """
        TEST_ID: T027.08
        SPEC: S027
        EC: EC026

        Given: npm returns invalid JSON
        When: get_package is called
        Then: Raises RegistryParseError
        """
        respx.get("https://registry.npmjs.org/express").mock(
            return_value=httpx.Response(200, content=b"not valid json")
        )

        async with NpmClient() as client:
            with pytest.raises(RegistryParseError) as exc_info:
                await client.get_package_metadata("express")

        assert exc_info.value.registry == "npm"


class TestNpmURL:
    """Tests for npm URL construction."""

    def test_api_url_format(self) -> None:
        """
        TEST_ID: T027.09
        SPEC: S027

        Given: Package name "express"
        When: Constructing API URL
        Then: Returns "https://registry.npmjs.org/express"
        """
        client = NpmClient()
        url = client._get_api_url("express")
        assert url == "https://registry.npmjs.org/express"

    def test_scoped_package_url(self) -> None:
        """
        TEST_ID: T027.10
        SPEC: S027

        Given: Scoped package "@types/node"
        When: Constructing API URL
        Then: Returns URL with encoded scope
        """
        client = NpmClient()
        url = client._get_api_url("@types/node")
        assert url == "https://registry.npmjs.org/@types%2Fnode"


class TestNpmNameValidation:
    """Tests for npm-specific name validation."""

    def test_leading_number_valid_for_npm(self) -> None:
        """
        TEST_ID: T027.11
        SPEC: S027
        EC: EC014

        Given: Package name starting with number "3flask"
        When: Validating for npm
        Then: URL is constructed correctly (npm allows leading numbers)
        """
        client = NpmClient()
        url = client._get_api_url("3flask")
        assert url == "https://registry.npmjs.org/3flask"

    def test_scoped_package_format_valid(self) -> None:
        """
        TEST_ID: T027.12
        SPEC: S027

        Given: Scoped package "@org/pkg"
        When: Validating for npm
        Then: URL is constructed with proper encoding
        """
        client = NpmClient()
        url = client._get_api_url("@org/pkg")
        assert url == "https://registry.npmjs.org/@org%2Fpkg"


class TestNpmClientErrors:
    """Tests for npm client error handling edge cases."""

    @pytest.mark.asyncio
    async def test_client_not_initialized_raises_runtime_error(self) -> None:
        """
        TEST_ID: T027.13
        SPEC: S027

        Given: NpmClient not used as context manager
        When: get_package_metadata is called
        Then: Raises RuntimeError
        """
        client = NpmClient()
        with pytest.raises(RuntimeError) as exc_info:
            await client.get_package_metadata("express")
        assert "context" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @respx.mock
    async def test_network_error_raises_unavailable(self) -> None:
        """
        TEST_ID: T027.14
        SPEC: S027

        Given: Network connection error
        When: get_package_metadata is called
        Then: Raises RegistryUnavailableError
        """
        respx.get("https://registry.npmjs.org/express").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with NpmClient() as client:
            with pytest.raises(RegistryUnavailableError):
                await client.get_package_metadata("express")

    @pytest.mark.asyncio
    async def test_get_downloads_without_context_returns_none(self) -> None:
        """
        TEST_ID: T027.15
        SPEC: S029

        Given: NpmClient not used as context manager
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        client = NpmClient()
        result = await client.get_downloads("express")
        assert result is None


class TestNpmDownloads:
    """Tests for npm downloads API."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_downloads_success(self) -> None:
        """
        TEST_ID: T027.16
        SPEC: S029

        Given: npm downloads API returns valid data
        When: get_downloads is called
        Then: Returns monthly estimate (weekly * 4)
        """
        respx.get("https://api.npmjs.org/downloads/point/last-week/express").mock(
            return_value=httpx.Response(
                200,
                json={
                    "downloads": 1000000,
                    "package": "express",
                    "start": "2023-01-01",
                    "end": "2023-01-07",
                },
            )
        )

        async with NpmClient() as client:
            downloads = await client.get_downloads("express")

        # Weekly downloads * 4 = monthly estimate
        assert downloads == 4000000

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_downloads_scoped_package(self) -> None:
        """
        TEST_ID: T027.17
        SPEC: S029

        Given: Scoped package download request
        When: get_downloads is called
        Then: Returns downloads with proper URL encoding
        """
        respx.get("https://api.npmjs.org/downloads/point/last-week/@types%2Fnode").mock(
            return_value=httpx.Response(
                200,
                json={"downloads": 500000, "package": "@types/node"},
            )
        )

        async with NpmClient() as client:
            downloads = await client.get_downloads("@types/node")

        assert downloads == 2000000  # 500000 * 4

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_downloads_unavailable_returns_none(self) -> None:
        """
        TEST_ID: T027.18
        SPEC: S029

        Given: npm downloads API returns error
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://api.npmjs.org/downloads/point/last-week/express").mock(
            return_value=httpx.Response(500)
        )

        async with NpmClient() as client:
            downloads = await client.get_downloads("express")

        assert downloads is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_downloads_timeout_returns_none(self) -> None:
        """
        TEST_ID: T027.19
        SPEC: S029

        Given: npm downloads API times out
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://api.npmjs.org/downloads/point/last-week/express").mock(
            side_effect=httpx.TimeoutException("Timeout")
        )

        async with NpmClient() as client:
            downloads = await client.get_downloads("express")

        assert downloads is None


class TestNpmMetadataWithDownloads:
    """Tests for combined metadata + downloads."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_downloads_success(self) -> None:
        """
        TEST_ID: T027.20
        SPEC: S027, S029

        Given: Package exists with metadata and downloads available
        When: get_package_metadata_with_downloads is called
        Then: Returns metadata with downloads included
        """
        respx.get("https://registry.npmjs.org/express").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "express",
                    "dist-tags": {"latest": "4.18.2"},
                    "time": {"created": "2010-12-29T19:38:25.450Z"},
                    "versions": {"4.18.2": {}},
                    "maintainers": [{"name": "dougwilson"}],
                },
            )
        )
        respx.get("https://api.npmjs.org/downloads/point/last-week/express").mock(
            return_value=httpx.Response(200, json={"downloads": 1000000, "package": "express"})
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata_with_downloads("express")

        assert metadata.exists is True
        assert metadata.name == "express"
        assert metadata.downloads_last_month == 4000000

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_downloads_not_found(self) -> None:
        """
        TEST_ID: T027.21
        SPEC: S027, S029

        Given: Package does not exist
        When: get_package_metadata_with_downloads is called
        Then: Returns metadata with exists=False
        """
        respx.get("https://registry.npmjs.org/nonexistent-xyz").mock(
            return_value=httpx.Response(404)
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata_with_downloads("nonexistent-xyz")

        assert metadata.exists is False
        assert metadata.downloads_last_month is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_downloads_stats_unavailable(self) -> None:
        """
        TEST_ID: T027.22
        SPEC: S027, S029

        Given: Package exists but downloads API unavailable
        When: get_package_metadata_with_downloads is called
        Then: Returns metadata with downloads=None
        """
        respx.get("https://registry.npmjs.org/express").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "express",
                    "dist-tags": {"latest": "4.18.2"},
                    "versions": {"4.18.2": {}},
                },
            )
        )
        respx.get("https://api.npmjs.org/downloads/point/last-week/express").mock(
            return_value=httpx.Response(503)
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata_with_downloads("express")

        assert metadata.exists is True
        assert metadata.downloads_last_month is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response_handled(self) -> None:
        """
        TEST_ID: T027.23
        SPEC: S028

        Given: npm returns empty JSON object
        When: get_package_metadata is called
        Then: Returns metadata with exists=True and default values
        """
        respx.get("https://registry.npmjs.org/empty-pkg").mock(
            return_value=httpx.Response(200, json={})
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("empty-pkg")

        assert metadata.exists is True
        assert metadata.name == "empty-pkg"


class TestNpmContextManager:
    """Tests for context manager edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_client_provided_not_closed_on_exit(self) -> None:
        """
        TEST_ID: T027.26
        SPEC: S027

        Given: NpmClient initialized with external httpx client
        When: Context manager exits
        Then: External client is NOT closed (_owns_client=False)
        """
        external_client = httpx.AsyncClient(timeout=10.0)
        try:
            respx.get("https://registry.npmjs.org/express").mock(
                return_value=httpx.Response(200, json={"name": "express", "versions": {}})
            )

            async with NpmClient(client=external_client) as client:
                metadata = await client.get_package_metadata("express")
                assert metadata.exists is True

            # External client should still be usable (not closed)
            assert not external_client.is_closed
        finally:
            await external_client.aclose()

    @pytest.mark.asyncio
    @respx.mock
    async def test_client_provided_uses_existing_client(self) -> None:
        """
        TEST_ID: T027.27
        SPEC: S027

        Given: NpmClient initialized with external httpx client
        When: Entering context manager
        Then: Uses the provided client, doesn't create new one
        """
        external_client = httpx.AsyncClient(timeout=10.0)
        try:
            respx.get("https://registry.npmjs.org/lodash").mock(
                return_value=httpx.Response(200, json={"name": "lodash", "versions": {}})
            )

            npm_client = NpmClient(client=external_client)
            # Before entering, _client should be the external client
            assert npm_client._client is external_client
            assert npm_client._owns_client is False

            async with npm_client as client:
                # Inside context, _client should still be the external client
                assert client._client is external_client
                await client.get_package_metadata("lodash")
        finally:
            await external_client.aclose()


class TestNpmRateLimitEdgeCases:
    """Tests for rate limit header parsing edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_invalid_retry_after_header(self) -> None:
        """
        TEST_ID: T027.28
        SPEC: S027
        EC: EC025

        Given: npm returns 429 with invalid Retry-After header
        When: get_package_metadata is called
        Then: Raises RegistryRateLimitError with retry_after=None
        """
        respx.get("https://registry.npmjs.org/express").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "not-a-number"})
        )

        async with NpmClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("express")

        assert exc_info.value.registry == "npm"
        assert exc_info.value.retry_after is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_no_retry_after_header(self) -> None:
        """
        TEST_ID: T027.29
        SPEC: S027
        EC: EC025

        Given: npm returns 429 without Retry-After header
        When: get_package_metadata is called
        Then: Raises RegistryRateLimitError with retry_after=None
        """
        respx.get("https://registry.npmjs.org/express").mock(return_value=httpx.Response(429))

        async with NpmClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("express")

        assert exc_info.value.registry == "npm"
        assert exc_info.value.retry_after is None


class TestNpmRepositoryUrlEdgeCases:
    """Tests for repository URL parsing edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_repository_url_ends_with_dot(self) -> None:
        """
        TEST_ID: T027.30
        SPEC: S028

        Given: npm returns repository URL ending with dot after git suffix removal
        When: get_package_metadata is called
        Then: Trailing dot is removed from repository URL
        """
        respx.get("https://registry.npmjs.org/pkg-with-dot").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "pkg-with-dot",
                    "versions": {"1.0.0": {}},
                    "repository": {
                        "type": "git",
                        "url": "git+https://github.com/user/repo.git.",
                    },
                },
            )
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("pkg-with-dot")

        # URL should have trailing dot removed
        assert metadata.repository_url == "https://github.com/user/repo"

    @pytest.mark.asyncio
    @respx.mock
    async def test_repository_url_ends_with_trailing_dot_after_strip(self) -> None:
        """
        TEST_ID: T027.35
        SPEC: S028

        Given: npm returns repository URL that ends with just "." after rstrip(".git")
        When: get_package_metadata is called
        Then: The trailing dot is removed
        """
        # After rstrip(".git"), URL like "https://example.com/." becomes "https://example.com/."
        # (since rstrip removes trailing .git chars, not just ".git" suffix)
        # We need a URL that after replace("git+", "").rstrip(".git") ends with "."
        respx.get("https://registry.npmjs.org/pkg-trailing-dot").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "pkg-trailing-dot",
                    "versions": {"1.0.0": {}},
                    "repository": {
                        "type": "git",
                        # After rstrip(".git"), this becomes "https://example.com/repo."
                        "url": "https://example.com/repo.git.",
                    },
                },
            )
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("pkg-trailing-dot")

        # URL should have trailing dot removed
        assert metadata.repository_url == "https://example.com/repo"

    @pytest.mark.asyncio
    @respx.mock
    async def test_repository_as_string(self) -> None:
        """
        TEST_ID: T027.31
        SPEC: S028

        Given: npm returns repository as string (not dict)
        When: get_package_metadata is called
        Then: Uses string as repository URL
        """
        respx.get("https://registry.npmjs.org/string-repo").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": "string-repo",
                    "versions": {"1.0.0": {}},
                    "repository": "https://github.com/user/repo",
                },
            )
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("string-repo")

        assert metadata.repository_url == "https://github.com/user/repo"


class TestNpmInvalidDataTypes:
    """Tests for invalid data type handling."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_downloads_non_integer_returns_none(self) -> None:
        """
        TEST_ID: T027.32
        SPEC: S029

        Given: npm downloads API returns non-integer downloads field
        When: get_downloads is called
        Then: Returns None
        """
        respx.get("https://api.npmjs.org/downloads/point/last-week/express").mock(
            return_value=httpx.Response(
                200,
                json={"downloads": "not-a-number", "package": "express"},
            )
        )

        async with NpmClient() as client:
            downloads = await client.get_downloads("express")

        assert downloads is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_downloads_invalid_json_returns_none(self) -> None:
        """
        TEST_ID: T027.33
        SPEC: S029

        Given: npm downloads API returns invalid JSON
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://api.npmjs.org/downloads/point/last-week/express").mock(
            return_value=httpx.Response(200, content=b"not valid json")
        )

        async with NpmClient() as client:
            downloads = await client.get_downloads("express")

        assert downloads is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_downloads_network_error_returns_none(self) -> None:
        """
        TEST_ID: T027.34
        SPEC: S029

        Given: npm downloads API has network error
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://api.npmjs.org/downloads/point/last-week/express").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with NpmClient() as client:
            downloads = await client.get_downloads("express")

        assert downloads is None


class TestNpmRegistryField:
    """Tests to verify registry field is correctly set."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_registry_field_set_on_exists(self) -> None:
        """
        TEST_ID: T027.24
        SPEC: S027

        Given: Package exists on npm
        When: get_package_metadata is called
        Then: Returns metadata with registry="npm"
        """
        respx.get("https://registry.npmjs.org/express").mock(
            return_value=httpx.Response(200, json={"name": "express", "versions": {}})
        )

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("express")

        assert metadata.registry == "npm"

    @pytest.mark.asyncio
    @respx.mock
    async def test_registry_field_set_on_not_found(self) -> None:
        """
        TEST_ID: T027.25
        SPEC: S027

        Given: Package does not exist on npm
        When: get_package_metadata is called
        Then: Returns metadata with registry="npm"
        """
        respx.get("https://registry.npmjs.org/nonexistent").mock(return_value=httpx.Response(404))

        async with NpmClient() as client:
            metadata = await client.get_package_metadata("nonexistent")

        assert metadata.registry == "npm"
