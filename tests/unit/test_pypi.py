# SPEC: S020-S026 - PyPI Registry Client
# Gate 3: Test Design - Implementation
"""
Unit tests for the PyPI registry client.

SPEC_IDs: S020-S026
TEST_IDs: T020.*
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
from phantom_guard.registry.pypi import PyPIClient


class TestPyPIClient:
    """Tests for PyPI registry client.

    SPEC: S020-S026 - PyPI client
    Total tests: 16 (10 unit, 5 integration, 1 bench)
    """

    # =========================================================================
    # SUCCESSFUL RESPONSE TESTS
    # =========================================================================

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_exists_returns_metadata(self):
        """
        TEST_ID: T020.01
        SPEC: S020
        INV: INV013
        EC: EC020

        Given: Package "flask" exists on PyPI
        When: get_package is called
        Then: Returns PackageMetadata with exists=True
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {
                        "name": "flask",
                        "version": "3.0.0",
                        "summary": "A micro web framework",
                        "author": "Armin Ronacher",
                    },
                    "releases": {"3.0.0": [], "2.0.0": []},
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("flask")

        assert metadata.exists is True
        assert metadata.name == "flask"

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_not_found_returns_not_exists(self):
        """
        TEST_ID: T020.02
        SPEC: S020
        INV: INV013
        EC: EC021

        Given: Package does not exist on PyPI
        When: get_package is called
        Then: Returns PackageMetadata with exists=False
        """
        respx.get("https://pypi.org/pypi/nonexistent-phantom-package/json").mock(
            return_value=httpx.Response(404)
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("nonexistent-phantom-package")

        assert metadata.exists is False
        assert metadata.name == "nonexistent-phantom-package"

    @pytest.mark.asyncio
    @respx.mock
    async def test_package_metadata_fields(self):
        """
        TEST_ID: T020.03
        SPEC: S020

        Given: Package exists with full metadata
        When: get_package is called
        Then: Metadata contains name, version, author, repo, etc.
        """
        respx.get("https://pypi.org/pypi/requests/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {
                        "name": "requests",
                        "version": "2.31.0",
                        "summary": "Python HTTP for Humans",
                        "author": "Kenneth Reitz",
                        "project_urls": {
                            "Source": "https://github.com/psf/requests",
                        },
                    },
                    "releases": {
                        "2.31.0": [{"upload_time": "2023-05-22T10:00:00"}],
                        "2.30.0": [{"upload_time": "2023-05-01T10:00:00"}],
                        "2.29.0": [{"upload_time": "2023-04-01T10:00:00"}],
                    },
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("requests")

        assert metadata.exists is True
        assert metadata.name == "requests"
        assert metadata.latest_version == "2.31.0"
        assert metadata.description == "Python HTTP for Humans"
        assert metadata.repository_url == "https://github.com/psf/requests"
        assert metadata.release_count == 3
        assert metadata.maintainer_count == 1

    # =========================================================================
    # ERROR HANDLING TESTS
    # =========================================================================

    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_raises_error(self):
        """
        TEST_ID: T020.04
        SPEC: S020
        INV: INV014
        EC: EC022

        Given: PyPI API does not respond within timeout
        When: get_package is called
        Then: Raises RegistryTimeoutError
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            side_effect=httpx.TimeoutException("timeout")
        )

        async with PyPIClient(timeout=1.0) as client:
            with pytest.raises(RegistryTimeoutError) as exc_info:
                await client.get_package_metadata("flask")

            assert exc_info.value.registry == "pypi"
            assert exc_info.value.timeout == 1.0

    @pytest.mark.asyncio
    @respx.mock
    async def test_server_error_raises_unavailable(self):
        """
        TEST_ID: T020.05
        SPEC: S020
        EC: EC023

        Given: PyPI returns 500 error
        When: get_package is called
        Then: Raises RegistryUnavailableError
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(return_value=httpx.Response(500))

        async with PyPIClient() as client:
            with pytest.raises(RegistryUnavailableError) as exc_info:
                await client.get_package_metadata("flask")

            assert exc_info.value.registry == "pypi"
            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    @respx.mock
    async def test_gateway_error_raises_unavailable(self):
        """
        TEST_ID: T020.06
        SPEC: S020
        EC: EC024

        Given: PyPI returns 502/503/504 error
        When: get_package is called
        Then: Raises RegistryUnavailableError
        """
        for status_code in [502, 503, 504]:
            respx.get("https://pypi.org/pypi/flask/json").mock(
                return_value=httpx.Response(status_code)
            )

            async with PyPIClient() as client:
                with pytest.raises(RegistryUnavailableError) as exc_info:
                    await client.get_package_metadata("flask")

                assert exc_info.value.status_code == status_code

            respx.clear()

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_raises_error(self):
        """
        TEST_ID: T020.07
        SPEC: S020
        EC: EC025

        Given: PyPI returns 429 error
        When: get_package is called
        Then: Raises RegistryRateLimitError with retry_after
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "60"})
        )

        async with PyPIClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("flask")

            assert exc_info.value.registry == "pypi"
            assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    @respx.mock
    async def test_invalid_json_raises_parse_error(self):
        """
        TEST_ID: T020.08
        SPEC: S020
        EC: EC026

        Given: PyPI returns invalid JSON
        When: get_package is called
        Then: Raises RegistryParseError
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            return_value=httpx.Response(200, content=b"not valid json{{{")
        )

        async with PyPIClient() as client:
            with pytest.raises(RegistryParseError) as exc_info:
                await client.get_package_metadata("flask")

            assert exc_info.value.registry == "pypi"

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_fields_graceful_default(self):
        """
        TEST_ID: T020.09
        SPEC: S020
        EC: EC027

        Given: PyPI returns partial JSON
        When: get_package is called
        Then: Uses graceful defaults for missing fields
        """
        respx.get("https://pypi.org/pypi/minimal-package/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {"name": "minimal-package"},
                    "releases": {},
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("minimal-package")

        assert metadata.exists is True
        assert metadata.name == "minimal-package"
        assert metadata.latest_version is None
        assert metadata.description is None
        assert metadata.repository_url is None
        assert metadata.release_count == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response_handled(self):
        """
        TEST_ID: T020.10
        SPEC: S020
        EC: EC028

        Given: PyPI returns empty JSON {}
        When: get_package is called
        Then: Handles gracefully
        """
        respx.get("https://pypi.org/pypi/empty-package/json").mock(
            return_value=httpx.Response(200, json={})
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("empty-package")

        assert metadata.exists is True
        assert metadata.name == "empty-package"

    # =========================================================================
    # PYPISTATS TESTS (P1-PERF-001)
    # =========================================================================

    @pytest.mark.asyncio
    @respx.mock
    async def test_pypistats_success_returns_downloads(self):
        """
        TEST_ID: T020.11
        SPEC: S023
        EC: EC034

        Given: pypistats.org available
        When: get_downloads is called
        Then: Returns download count
        """
        respx.get("https://pypistats.org/api/packages/flask/recent").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"last_month": 15000000}},
            )
        )

        async with PyPIClient() as client:
            downloads = await client.get_downloads("flask")

        assert downloads == 15000000

    @pytest.mark.asyncio
    @respx.mock
    async def test_pypistats_unavailable_returns_none(self):
        """
        TEST_ID: T020.12
        SPEC: S023
        EC: EC034

        Given: pypistats.org returns 5xx
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://pypistats.org/api/packages/flask/recent").mock(
            return_value=httpx.Response(500)
        )

        async with PyPIClient() as client:
            downloads = await client.get_downloads("flask")

        assert downloads is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_pypistats_timeout_returns_none(self):
        """
        TEST_ID: T020.13
        SPEC: S023
        EC: EC034

        Given: pypistats.org times out (>2s)
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://pypistats.org/api/packages/flask/recent").mock(
            side_effect=httpx.TimeoutException("timeout")
        )

        async with PyPIClient() as client:
            downloads = await client.get_downloads("flask")

        assert downloads is None


class TestPyPIURL:
    """Tests for PyPI URL construction."""

    @pytest.mark.asyncio
    async def test_api_url_format(self):
        """
        TEST_ID: T020.14
        SPEC: S020

        Given: Package name "flask"
        When: Constructing API URL
        Then: Returns "https://pypi.org/pypi/flask/json"
        """
        async with PyPIClient() as client:
            url = client._get_api_url("flask")

        assert url == "https://pypi.org/pypi/flask/json"

    @pytest.mark.asyncio
    async def test_api_url_normalized(self):
        """
        TEST_ID: T020.15
        SPEC: S020

        Given: Package name "Flask_Redis"
        When: Constructing API URL
        Then: Returns normalized URL
        """
        async with PyPIClient() as client:
            url = client._get_api_url("Flask_Redis")

        # PEP 503: lowercase, _ -> -
        assert url == "https://pypi.org/pypi/flask-redis/json"


class TestPyPIClientErrors:
    """Additional error handling tests for full coverage."""

    @pytest.mark.asyncio
    async def test_client_not_initialized_raises_runtime_error(self):
        """
        TEST_ID: T020.16
        SPEC: S020

        Given: PyPIClient created but not entered via context manager
        When: get_package_metadata is called
        Then: Raises RuntimeError with helpful message
        """
        client = PyPIClient()
        # Don't use context manager

        with pytest.raises(RuntimeError) as exc_info:
            await client.get_package_metadata("flask")

        assert "context" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @respx.mock
    async def test_network_error_raises_unavailable(self):
        """
        TEST_ID: T020.17
        SPEC: S020
        EC: EC023

        Given: Network connection fails (not timeout)
        When: get_package_metadata is called
        Then: Raises RegistryUnavailableError
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with PyPIClient() as client:
            with pytest.raises(RegistryUnavailableError) as exc_info:
                await client.get_package_metadata("flask")

            assert exc_info.value.registry == "pypi"
            assert exc_info.value.status_code is None

    @pytest.mark.asyncio
    async def test_get_downloads_without_context_returns_none(self):
        """
        TEST_ID: T020.18
        SPEC: S023

        Given: PyPIClient not initialized
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        client = PyPIClient()
        # Don't use context manager

        result = await client.get_downloads("flask")
        assert result is None


class TestPyPIMetadataWithDownloads:
    """Tests for combined metadata + downloads method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_downloads_success(self):
        """
        TEST_ID: T020.19
        SPEC: S020, S023

        Given: Package exists and pypistats available
        When: get_package_metadata_with_downloads is called
        Then: Returns metadata with download count
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {"name": "flask", "version": "3.0.0"},
                    "releases": {"3.0.0": []},
                },
            )
        )
        respx.get("https://pypistats.org/api/packages/flask/recent").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"last_month": 5000000}},
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata_with_downloads("flask")

        assert metadata.exists is True
        assert metadata.name == "flask"
        assert metadata.downloads_last_month == 5000000

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_downloads_not_found(self):
        """
        TEST_ID: T020.20
        SPEC: S020, S023

        Given: Package does not exist
        When: get_package_metadata_with_downloads is called
        Then: Returns metadata with exists=False, no downloads fetch
        """
        respx.get("https://pypi.org/pypi/nonexistent/json").mock(return_value=httpx.Response(404))
        # pypistats should NOT be called

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata_with_downloads("nonexistent")

        assert metadata.exists is False
        assert metadata.downloads_last_month is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_metadata_with_downloads_stats_unavailable(self):
        """
        TEST_ID: T020.21
        SPEC: S020, S023

        Given: Package exists but pypistats unavailable
        When: get_package_metadata_with_downloads is called
        Then: Returns metadata with downloads=None
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {"name": "flask", "version": "3.0.0"},
                    "releases": {"3.0.0": []},
                },
            )
        )
        respx.get("https://pypistats.org/api/packages/flask/recent").mock(
            return_value=httpx.Response(500)
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata_with_downloads("flask")

        assert metadata.exists is True
        assert metadata.downloads_last_month is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_downloads_invalid_json(self):
        """
        TEST_ID: T020.22
        SPEC: S023

        Given: pypistats returns invalid JSON
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://pypistats.org/api/packages/flask/recent").mock(
            return_value=httpx.Response(200, content=b"not json{{{")
        )

        async with PyPIClient() as client:
            downloads = await client.get_downloads("flask")

        assert downloads is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_downloads_non_integer_value(self):
        """
        TEST_ID: T020.23
        SPEC: S023

        Given: pypistats returns non-integer download count
        When: get_downloads is called
        Then: Returns None
        """
        respx.get("https://pypistats.org/api/packages/flask/recent").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"last_month": "not a number"}},
            )
        )

        async with PyPIClient() as client:
            downloads = await client.get_downloads("flask")

        assert downloads is None


class TestPyPIContextManager:
    """Tests for context manager edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_client_provided_not_closed_on_exit(self):
        """
        TEST_ID: T020.26
        SPEC: S020

        Given: PyPIClient initialized with external httpx client
        When: Context manager exits
        Then: External client is NOT closed (_owns_client=False)
        """
        external_client = httpx.AsyncClient(timeout=10.0)
        try:
            respx.get("https://pypi.org/pypi/flask/json").mock(
                return_value=httpx.Response(200, json={"info": {"name": "flask"}, "releases": {}})
            )

            async with PyPIClient(client=external_client) as client:
                metadata = await client.get_package_metadata("flask")
                assert metadata.exists is True

            # External client should still be usable (not closed)
            assert not external_client.is_closed
        finally:
            await external_client.aclose()

    @pytest.mark.asyncio
    @respx.mock
    async def test_client_provided_uses_existing_client(self):
        """
        TEST_ID: T020.27
        SPEC: S020

        Given: PyPIClient initialized with external httpx client
        When: Entering context manager
        Then: Uses the provided client, doesn't create new one
        """
        external_client = httpx.AsyncClient(timeout=10.0)
        try:
            respx.get("https://pypi.org/pypi/requests/json").mock(
                return_value=httpx.Response(
                    200, json={"info": {"name": "requests"}, "releases": {}}
                )
            )

            pypi_client = PyPIClient(client=external_client)
            # Before entering, _client should be the external client
            assert pypi_client._client is external_client
            assert pypi_client._owns_client is False

            async with pypi_client as client:
                # Inside context, _client should still be the external client
                assert client._client is external_client
                await client.get_package_metadata("requests")
        finally:
            await external_client.aclose()


class TestPyPIRateLimitEdgeCases:
    """Tests for rate limit header parsing edge cases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_invalid_retry_after_header(self):
        """
        TEST_ID: T020.28
        SPEC: S020
        EC: EC025

        Given: PyPI returns 429 with invalid Retry-After header
        When: get_package_metadata is called
        Then: Raises RegistryRateLimitError with retry_after=None
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "not-a-number"})
        )

        async with PyPIClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("flask")

        assert exc_info.value.registry == "pypi"
        assert exc_info.value.retry_after is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_no_retry_after_header(self):
        """
        TEST_ID: T020.29
        SPEC: S020
        EC: EC025

        Given: PyPI returns 429 without Retry-After header
        When: get_package_metadata is called
        Then: Raises RegistryRateLimitError with retry_after=None
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(return_value=httpx.Response(429))

        async with PyPIClient() as client:
            with pytest.raises(RegistryRateLimitError) as exc_info:
                await client.get_package_metadata("flask")

        assert exc_info.value.registry == "pypi"
        assert exc_info.value.retry_after is None


class TestPyPIDatetimeParsingEdgeCases:
    """Tests for datetime parsing edge cases in releases."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_invalid_upload_time_format_ignored(self):
        """
        TEST_ID: T020.30
        SPEC: S022

        Given: PyPI returns release with invalid upload_time format
        When: get_package_metadata is called
        Then: Invalid datetime is ignored, created_at uses valid timestamps
        """
        respx.get("https://pypi.org/pypi/pkg-bad-time/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {"name": "pkg-bad-time", "version": "1.0.0"},
                    "releases": {
                        "1.0.0": [{"upload_time": "not-a-valid-datetime"}],
                        "0.9.0": [{"upload_time": "2023-01-01T00:00:00"}],
                    },
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("pkg-bad-time")

        assert metadata.exists is True
        # Should still get created_at from valid timestamp
        assert metadata.created_at is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_all_invalid_upload_times_returns_none(self):
        """
        TEST_ID: T020.31
        SPEC: S022

        Given: PyPI returns all releases with invalid upload_time formats
        When: get_package_metadata is called
        Then: created_at is None
        """
        respx.get("https://pypi.org/pypi/pkg-all-bad-time/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {"name": "pkg-all-bad-time", "version": "1.0.0"},
                    "releases": {
                        "1.0.0": [{"upload_time": "invalid1"}],
                        "0.9.0": [{"upload_time": "invalid2"}],
                    },
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("pkg-all-bad-time")

        assert metadata.exists is True
        assert metadata.created_at is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_upload_time_field_ignored(self):
        """
        TEST_ID: T020.33
        SPEC: S022

        Given: PyPI returns release files without upload_time field
        When: get_package_metadata is called
        Then: Files without upload_time are skipped gracefully
        """
        respx.get("https://pypi.org/pypi/pkg-no-time/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {"name": "pkg-no-time", "version": "1.0.0"},
                    "releases": {
                        "1.0.0": [{"filename": "pkg-1.0.0.tar.gz"}],  # No upload_time
                        "0.9.0": [{"upload_time": "2023-01-01T00:00:00"}],
                    },
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("pkg-no-time")

        assert metadata.exists is True
        # Should still get created_at from the valid timestamp
        assert metadata.created_at is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_upload_time_field_ignored(self):
        """
        TEST_ID: T020.34
        SPEC: S022

        Given: PyPI returns release files with empty upload_time
        When: get_package_metadata is called
        Then: Empty upload_time values are skipped
        """
        respx.get("https://pypi.org/pypi/pkg-empty-time/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {"name": "pkg-empty-time", "version": "1.0.0"},
                    "releases": {
                        "1.0.0": [{"upload_time": ""}],  # Empty string
                        "0.9.0": [{"upload_time": None}],  # None value
                    },
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("pkg-empty-time")

        assert metadata.exists is True
        assert metadata.created_at is None


class TestPyPIRepositoryUrlFallback:
    """Tests for repository URL resolution priority."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_project_url_takes_priority(self):
        """
        TEST_ID: T020.35
        SPEC: S022

        Given: PyPI returns project_url in info
        When: get_package_metadata is called
        Then: project_url is used, project_urls fallback not consulted
        """
        respx.get("https://pypi.org/pypi/pkg-project-url/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {
                        "name": "pkg-project-url",
                        "version": "1.0.0",
                        "project_url": "https://primary-url.example.com",
                        "project_urls": {
                            "Source": "https://fallback-url.example.com",
                        },
                    },
                    "releases": {},
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("pkg-project-url")

        assert metadata.repository_url == "https://primary-url.example.com"

    @pytest.mark.asyncio
    @respx.mock
    async def test_home_page_takes_priority(self):
        """
        TEST_ID: T020.36
        SPEC: S022

        Given: PyPI returns home_page in info (but no project_url)
        When: get_package_metadata is called
        Then: home_page is used, project_urls fallback not consulted
        """
        respx.get("https://pypi.org/pypi/pkg-home-page/json").mock(
            return_value=httpx.Response(
                200,
                json={
                    "info": {
                        "name": "pkg-home-page",
                        "version": "1.0.0",
                        "home_page": "https://home-page-url.example.com",
                        "project_urls": {
                            "Source": "https://fallback-url.example.com",
                        },
                    },
                    "releases": {},
                },
            )
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("pkg-home-page")

        assert metadata.repository_url == "https://home-page-url.example.com"


class TestPyPIInvalidDataTypes:
    """Tests for invalid data type handling."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_downloads_network_error_returns_none(self):
        """
        TEST_ID: T020.32
        SPEC: S023

        Given: pypistats API has network error
        When: get_downloads is called
        Then: Returns None (graceful degradation)
        """
        respx.get("https://pypistats.org/api/packages/flask/recent").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with PyPIClient() as client:
            downloads = await client.get_downloads("flask")

        assert downloads is None


class TestPyPIRegistryField:
    """Tests to verify registry field is correctly set."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_registry_field_set_on_exists(self):
        """
        TEST_ID: T020.24
        SPEC: S020

        Given: Package exists on PyPI
        When: get_package_metadata is called
        Then: Returns metadata with registry="pypi"
        """
        respx.get("https://pypi.org/pypi/flask/json").mock(
            return_value=httpx.Response(200, json={"info": {"name": "flask"}, "releases": {}})
        )

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("flask")

        assert metadata.registry == "pypi"

    @pytest.mark.asyncio
    @respx.mock
    async def test_registry_field_set_on_not_found(self):
        """
        TEST_ID: T020.25
        SPEC: S020

        Given: Package does not exist on PyPI
        When: get_package_metadata is called
        Then: Returns metadata with registry="pypi"
        """
        respx.get("https://pypi.org/pypi/nonexistent/json").mock(return_value=httpx.Response(404))

        async with PyPIClient() as client:
            metadata = await client.get_package_metadata("nonexistent")

        assert metadata.registry == "pypi"
