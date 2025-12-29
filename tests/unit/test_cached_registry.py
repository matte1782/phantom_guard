# SPEC: S040-S049 - Cached Registry Client
"""
Unit tests for CachedRegistryClient.

SPEC_IDs: S040-S049
TEST_IDs: T040.11, T040.12, T040.13, T040.14
INVARIANTS: INV003, INV016, INV017
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from phantom_guard.cache import Cache
from phantom_guard.core.types import PackageMetadata
from phantom_guard.registry.cached import (
    CachedRegistryClient,
    _dict_to_metadata,
    _metadata_to_dict,
)


class MockRegistryClient:
    """Mock registry client for testing."""

    def __init__(self) -> None:
        self.get_package_metadata = AsyncMock()
        self.call_count = 0

    async def __aenter__(self) -> MockRegistryClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass


class TestMetadataConversion:
    """Tests for metadata serialization/deserialization."""

    def test_metadata_to_dict_basic(self) -> None:
        """Basic metadata converts to dict."""
        metadata = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
        )

        result = _metadata_to_dict(metadata)

        assert result["name"] == "flask"
        assert result["exists"] is True
        assert result["registry"] == "pypi"

    def test_metadata_to_dict_with_datetime(self) -> None:
        """Datetime is serialized to ISO format."""
        created = datetime(2020, 1, 15, 12, 30, 0, tzinfo=UTC)
        metadata = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
            created_at=created,
        )

        result = _metadata_to_dict(metadata)

        assert result["created_at"] == "2020-01-15T12:30:00+00:00"

    def test_dict_to_metadata_basic(self) -> None:
        """Basic dict converts to metadata."""
        data = {
            "name": "flask",
            "exists": True,
            "registry": "pypi",
        }

        result = _dict_to_metadata(data)

        assert result is not None
        assert result.name == "flask"
        assert result.exists is True
        assert result.registry == "pypi"

    def test_dict_to_metadata_with_datetime(self) -> None:
        """ISO datetime string is deserialized to datetime."""
        data = {
            "name": "flask",
            "exists": True,
            "registry": "pypi",
            "created_at": "2020-01-15T12:30:00+00:00",
        }

        result = _dict_to_metadata(data)

        assert result is not None
        assert result.created_at is not None
        assert result.created_at.year == 2020
        assert result.created_at.month == 1
        assert result.created_at.day == 15

    def test_invalid_data_returns_none(self) -> None:
        """
        Invalid cache data returns None instead of crashing.

        This allows the caller to treat it as a cache miss.
        """
        # Missing required field 'name'
        invalid_data: dict[str, Any] = {"exists": True, "registry": "pypi"}
        result = _dict_to_metadata(invalid_data)
        assert result is None

    def test_invalid_datetime_returns_none(self) -> None:
        """Invalid datetime format returns None."""
        invalid_data = {
            "name": "flask",
            "exists": True,
            "registry": "pypi",
            "created_at": "not-a-valid-datetime",
        }
        result = _dict_to_metadata(invalid_data)
        assert result is None

    def test_roundtrip_conversion(self) -> None:
        """
        TEST_ID: T040.13
        INV: INV003

        Metadata survives roundtrip through dict conversion.
        """
        original = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
            created_at=datetime(2020, 1, 15, 12, 30, 0, tzinfo=UTC),
            downloads_last_month=1000000,
            repository_url="https://github.com/pallets/flask",
            maintainer_count=5,
            release_count=100,
            latest_version="2.3.0",
            description="A lightweight WSGI web application framework.",
        )

        # Convert to dict and back
        as_dict = _metadata_to_dict(original)
        restored = _dict_to_metadata(as_dict)

        assert restored is not None
        assert restored.name == original.name
        assert restored.exists == original.exists
        assert restored.registry == original.registry
        assert restored.created_at == original.created_at
        assert restored.downloads_last_month == original.downloads_last_month
        assert restored.repository_url == original.repository_url
        assert restored.maintainer_count == original.maintainer_count
        assert restored.release_count == original.release_count
        assert restored.latest_version == original.latest_version
        assert restored.description == original.description


class TestCachedRegistryClientBasics:
    """Basic tests for CachedRegistryClient."""

    @pytest.mark.asyncio
    async def test_cache_miss_fetches_from_client(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.11
        SPEC: S041
        EC: EC061

        Given: Package not in cache
        When: get_package_metadata called
        Then: Fetches from underlying client
        """
        mock_client = MockRegistryClient()
        mock_client.get_package_metadata.return_value = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            result = await cached.get_package_metadata("flask")

        assert result.name == "flask"
        assert result.exists is True
        mock_client.get_package_metadata.assert_called_once_with("flask")

    @pytest.mark.asyncio
    async def test_cache_hit_skips_client(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.12
        SPEC: S041
        EC: EC060

        Given: Package in cache
        When: get_package_metadata called
        Then: Returns cached data, doesn't call client
        """
        mock_client = MockRegistryClient()
        mock_client.get_package_metadata.return_value = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # First call - cache miss
            await cached.get_package_metadata("flask")
            assert mock_client.get_package_metadata.call_count == 1

            # Second call - cache hit
            result = await cached.get_package_metadata("flask")
            assert mock_client.get_package_metadata.call_count == 1  # No new call

        assert result.name == "flask"

    @pytest.mark.asyncio
    async def test_stores_in_cache_after_fetch(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.14
        SPEC: S042

        Given: Cache miss
        When: Fetch completes
        Then: Result is stored in cache
        """
        mock_client = MockRegistryClient()
        mock_client.get_package_metadata.return_value = PackageMetadata(
            name="requests",
            exists=True,
            registry="pypi",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            await cached.get_package_metadata("requests")

            # Verify it's cached
            assert await cached.is_cached("requests") is True


class TestCachedRegistryClientOperations:
    """Tests for CachedRegistryClient operations."""

    @pytest.mark.asyncio
    async def test_invalidate_removes_from_cache(self, tmp_path: Path) -> None:
        """Invalidate removes entry from cache."""
        mock_client = MockRegistryClient()
        mock_client.get_package_metadata.return_value = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # Cache the package
            await cached.get_package_metadata("flask")
            assert await cached.is_cached("flask") is True

            # Invalidate
            result = await cached.invalidate("flask")
            assert result is True
            assert await cached.is_cached("flask") is False

    @pytest.mark.asyncio
    async def test_uncached_bypasses_cache(self, tmp_path: Path) -> None:
        """get_package_metadata_uncached bypasses cache."""
        mock_client = MockRegistryClient()
        mock_client.get_package_metadata.return_value = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # First call via cached method
            await cached.get_package_metadata("flask")
            assert mock_client.get_package_metadata.call_count == 1

            # Second call via cached method - should hit cache
            await cached.get_package_metadata("flask")
            assert mock_client.get_package_metadata.call_count == 1

            # Third call via uncached method - should call client
            await cached.get_package_metadata_uncached("flask")
            assert mock_client.get_package_metadata.call_count == 2

    @pytest.mark.asyncio
    async def test_different_registries_separate_keys(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.09
        EC: EC066

        Same package name, different registries have separate cache entries.
        """
        pypi_client = MockRegistryClient()
        pypi_client.get_package_metadata.return_value = PackageMetadata(
            name="requests",
            exists=True,
            registry="pypi",
            description="PyPI version",
        )

        npm_client = MockRegistryClient()
        npm_client.get_package_metadata.return_value = PackageMetadata(
            name="requests",
            exists=True,
            registry="npm",
            description="npm version",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        async with cache:
            # Cache PyPI version
            async with CachedRegistryClient(pypi_client, cache, "pypi") as pypi_cached:
                pypi_result = await pypi_cached.get_package_metadata("requests")

            # Cache npm version
            async with CachedRegistryClient(npm_client, cache, "npm") as npm_cached:
                npm_result = await npm_cached.get_package_metadata("requests")

        # Both should have been fetched (different cache keys)
        assert pypi_client.get_package_metadata.call_count == 1
        assert npm_client.get_package_metadata.call_count == 1

        # Results should be different
        assert pypi_result.registry == "pypi"
        assert npm_result.registry == "npm"


class TestCachedRegistryClientNonExistent:
    """Tests for caching non-existent packages."""

    @pytest.mark.asyncio
    async def test_caches_nonexistent_packages(self, tmp_path: Path) -> None:
        """
        Non-existent packages are also cached (negative caching).

        This prevents repeated API calls for packages that don't exist.
        """
        mock_client = MockRegistryClient()
        mock_client.get_package_metadata.return_value = PackageMetadata(
            name="nonexistent-pkg-xyz",
            exists=False,
            registry="pypi",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # First call
            result1 = await cached.get_package_metadata("nonexistent-pkg-xyz")
            assert result1.exists is False
            assert mock_client.get_package_metadata.call_count == 1

            # Second call - should hit cache
            result2 = await cached.get_package_metadata("nonexistent-pkg-xyz")
            assert result2.exists is False
            assert mock_client.get_package_metadata.call_count == 1  # No new call


class TestCachedRegistryClientMemoryOnly:
    """Tests for memory-only cache mode."""

    @pytest.mark.asyncio
    async def test_works_with_memory_only_cache(self) -> None:
        """
        EC: EC069

        CachedRegistryClient works with memory-only cache.
        """
        mock_client = MockRegistryClient()
        mock_client.get_package_metadata.return_value = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
        )

        # Memory-only cache (no SQLite path)
        cache = Cache(sqlite_path=None)

        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # First call - cache miss
            await cached.get_package_metadata("flask")
            assert mock_client.get_package_metadata.call_count == 1

            # Second call - cache hit
            await cached.get_package_metadata("flask")
            assert mock_client.get_package_metadata.call_count == 1


class SimpleClient:
    """Client without context manager methods."""

    def __init__(self) -> None:
        self.get_package_metadata = AsyncMock()


class TestCachedRegistryClientWithSimpleClient:
    """Tests for CachedRegistryClient with clients lacking context manager."""

    @pytest.mark.asyncio
    async def test_works_with_client_without_context_manager(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.15

        CachedRegistryClient works with clients that don't have __aenter__/__aexit__.
        """
        simple_client = SimpleClient()
        simple_client.get_package_metadata.return_value = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        # Using CachedRegistryClient with simple client
        async with cache, CachedRegistryClient(simple_client, cache, "pypi") as cached:
            result = await cached.get_package_metadata("flask")

        assert result.name == "flask"
        simple_client.get_package_metadata.assert_called_once_with("flask")


class TestCachedRegistryClientInvalidCache:
    """Tests for CachedRegistryClient handling invalid cache data."""

    @pytest.mark.asyncio
    async def test_refetches_on_invalid_cache_data(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.16

        When cached data is corrupted/invalid, refetches from client.
        """
        mock_client = MockRegistryClient()
        mock_client.get_package_metadata.return_value = PackageMetadata(
            name="flask",
            exists=True,
            registry="pypi",
        )

        cache = Cache(sqlite_path=tmp_path / "test.db")

        async with cache:
            # Manually store invalid data in cache
            await cache.set("pypi", "flask", {"invalid": "data"})

            async with CachedRegistryClient(mock_client, cache, "pypi") as cached:
                # Should detect invalid cache and refetch
                result = await cached.get_package_metadata("flask")

        assert result.name == "flask"
        assert result.exists is True
        # Client should have been called since cached data was invalid
        mock_client.get_package_metadata.assert_called_once_with("flask")
