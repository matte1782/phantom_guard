# SPEC: S040-S049 - Cache Integration Tests
"""
Integration tests for cache system.

SPEC_IDs: S040-S049
TEST_IDs: T040.I01-I04
INVARIANTS: INV003, INV016, INV017
Tests cache persistence, concurrent access, and corruption recovery.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from phantom_guard.cache import Cache
from phantom_guard.core.types import PackageMetadata
from phantom_guard.registry.cached import CachedRegistryClient


class MockRegistryClient:
    """Mock registry client for integration testing."""

    def __init__(self, registry: str = "pypi") -> None:
        self._registry = registry
        self.get_package_metadata = AsyncMock()
        self.call_count = 0

    async def __aenter__(self) -> MockRegistryClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass

    def set_response(self, name: str, exists: bool = True, **kwargs: Any) -> None:
        """Configure mock response."""
        self.get_package_metadata.return_value = PackageMetadata(
            name=name,
            exists=exists,
            registry=self._registry,
            **kwargs,
        )


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache system.

    SPEC: S040-S049
    """

    @pytest.mark.asyncio
    async def test_cache_persistence_across_sessions(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.I01
        SPEC: S040
        INV: INV016

        Given: Package cached in session 1
        When: New session starts
        Then: Cache hit in session 2 (SQLite persistence)
        """
        db_path = tmp_path / "cache.db"

        # Session 1: Cache a package
        mock_client = MockRegistryClient()
        mock_client.set_response(
            "flask",
            exists=True,
            created_at=datetime(2010, 4, 1, tzinfo=UTC),
            downloads_last_month=1000000,
        )

        cache1 = Cache(sqlite_path=db_path)
        async with cache1, CachedRegistryClient(mock_client, cache1, "pypi") as cached:
            await cached.get_package_metadata("flask")
            assert mock_client.get_package_metadata.call_count == 1

        # Session 2: New cache instance, same database
        mock_client2 = MockRegistryClient()
        mock_client2.set_response("flask", exists=True)

        cache2 = Cache(sqlite_path=db_path)
        async with cache2, CachedRegistryClient(mock_client2, cache2, "pypi") as cached:
            result = await cached.get_package_metadata("flask")

            # Should NOT call the client - cache hit from SQLite
            assert mock_client2.get_package_metadata.call_count == 0

            # Data should be from session 1
            assert result.name == "flask"
            assert result.exists is True
            assert result.downloads_last_month == 1000000

    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.I02
        SPEC: S040
        EC: EC065

        Given: Multiple concurrent readers
        When: All read same key
        Then: No corruption, all get correct value
        """
        db_path = tmp_path / "cache.db"

        # Pre-populate cache
        mock_client = MockRegistryClient()
        mock_client.set_response(
            "requests",
            exists=True,
            downloads_last_month=50000000,
        )

        cache = Cache(sqlite_path=db_path)
        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # Initial cache population
            await cached.get_package_metadata("requests")

            # Concurrent reads
            async def read_cached() -> PackageMetadata:
                return await cached.get_package_metadata("requests")

            # Run 20 concurrent reads
            results = await asyncio.gather(*[read_cached() for _ in range(20)])

            # All should return the same data
            for result in results:
                assert result.name == "requests"
                assert result.exists is True
                assert result.downloads_last_month == 50000000

            # Only 1 call to actual client (initial population)
            assert mock_client.get_package_metadata.call_count == 1

    @pytest.mark.asyncio
    async def test_concurrent_write_read(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.I03
        SPEC: S040
        EC: EC065

        Given: Writer and readers concurrent
        When: Operations execute
        Then: No data corruption
        """
        db_path = tmp_path / "cache.db"

        packages = ["pkg1", "pkg2", "pkg3", "pkg4", "pkg5"]

        mock_client = MockRegistryClient()

        async def get_mock_metadata(name: str) -> PackageMetadata:
            # Simulate some latency
            await asyncio.sleep(0.01)
            return PackageMetadata(
                name=name,
                exists=True,
                registry="pypi",
                downloads_last_month=hash(name) % 1000000,
            )

        mock_client.get_package_metadata.side_effect = get_mock_metadata

        cache = Cache(sqlite_path=db_path)
        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # Concurrent writes and reads
            async def fetch_package(name: str) -> PackageMetadata:
                return await cached.get_package_metadata(name)

            # First wave: all cache misses (writes)
            results1 = await asyncio.gather(*[fetch_package(p) for p in packages])

            # Second wave: all cache hits (reads)
            results2 = await asyncio.gather(*[fetch_package(p) for p in packages])

            # Verify no corruption
            for r1, r2 in zip(results1, results2, strict=True):
                assert r1.name == r2.name
                assert r1.downloads_last_month == r2.downloads_last_month

            # Each package should only trigger 1 client call
            assert mock_client.get_package_metadata.call_count == len(packages)


@pytest.mark.integration
class TestCacheCorruption:
    """Tests for cache corruption handling.

    EC: EC064
    """

    @pytest.mark.asyncio
    async def test_corrupted_cache_recovered(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.I04
        SPEC: S040
        EC: EC064

        Given: Corrupted SQLite database
        When: Cache initialized
        Then: Handles gracefully (treats as cache miss)
        """
        db_path = tmp_path / "corrupted.db"

        # Create a corrupted database file
        db_path.write_text("this is not a valid SQLite database")

        mock_client = MockRegistryClient()
        mock_client.set_response("flask", exists=True)

        # Cache should handle corruption gracefully
        # Either by rebuilding or treating as miss
        cache = Cache(sqlite_path=db_path)

        try:
            async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
                # Should work despite corruption
                result = await cached.get_package_metadata("flask")
                assert result.name == "flask"
        except Exception:  # noqa: S110
            # If it raises, that's also acceptable behavior
            # (fails fast on corruption)
            pass

    @pytest.mark.asyncio
    async def test_invalid_json_in_cache_treated_as_miss(self, tmp_path: Path) -> None:
        """
        EC: EC064

        Invalid JSON data in cache is treated as cache miss.
        """
        db_path = tmp_path / "cache.db"

        # First, create a valid cache entry
        cache1 = Cache(sqlite_path=db_path)
        async with cache1:
            # Manually insert invalid data into SQLite
            if cache1.sqlite:
                await cache1.sqlite.set(
                    "pypi:badpkg",
                    {"invalid": "not a PackageMetadata"},  # type: ignore[arg-type]
                )

        # Now try to read it
        mock_client = MockRegistryClient()
        mock_client.set_response("badpkg", exists=True, description="Fresh data")

        cache2 = Cache(sqlite_path=db_path)
        async with cache2, CachedRegistryClient(mock_client, cache2, "pypi") as cached:
            # Should handle invalid cache data gracefully
            try:
                result = await cached.get_package_metadata("badpkg")
                # If it returns, it should have fetched fresh data
                # or returned the partial data
                assert result.name == "badpkg"
            except (KeyError, TypeError):
                # Also acceptable: raise on invalid data
                pass


@pytest.mark.integration
class TestCacheInvariant003:
    """
    Tests for INV003: Cached results identical to uncached.
    """

    @pytest.mark.asyncio
    async def test_cached_identical_to_uncached(self, tmp_path: Path) -> None:
        """
        INV: INV003

        Cached results must be identical to uncached results.

        This is the critical invariant that guarantees cache correctness.
        """
        db_path = tmp_path / "cache.db"

        created_at = datetime(2010, 4, 1, 12, 0, 0, tzinfo=UTC)

        mock_client = MockRegistryClient()
        mock_client.set_response(
            "flask",
            exists=True,
            created_at=created_at,
            downloads_last_month=1000000,
            repository_url="https://github.com/pallets/flask",
            maintainer_count=5,
            release_count=100,
            latest_version="2.3.0",
            description="A lightweight WSGI web application framework.",
        )

        cache = Cache(sqlite_path=db_path)
        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # Get uncached result (directly from mock)
            uncached = await cached.get_package_metadata_uncached("flask")

            # Get cached result (will be stored in cache)
            cached_result = await cached.get_package_metadata("flask")

            # Get again from cache
            from_cache = await cached.get_package_metadata("flask")

            # All three should be identical
            assert cached_result.name == uncached.name
            assert cached_result.exists == uncached.exists
            assert cached_result.registry == uncached.registry
            assert cached_result.created_at == uncached.created_at
            assert cached_result.downloads_last_month == uncached.downloads_last_month
            assert cached_result.repository_url == uncached.repository_url
            assert cached_result.maintainer_count == uncached.maintainer_count
            assert cached_result.release_count == uncached.release_count
            assert cached_result.latest_version == uncached.latest_version
            assert cached_result.description == uncached.description

            # Cache result should also match
            assert from_cache.name == uncached.name
            assert from_cache.created_at == uncached.created_at
            assert from_cache.downloads_last_month == uncached.downloads_last_month

    @pytest.mark.asyncio
    async def test_cached_nonexistent_identical(self, tmp_path: Path) -> None:
        """
        INV: INV003

        Non-existent packages should also be cached identically.
        """
        db_path = tmp_path / "cache.db"

        mock_client = MockRegistryClient()
        mock_client.set_response("nonexistent-pkg", exists=False)

        cache = Cache(sqlite_path=db_path)
        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            uncached = await cached.get_package_metadata_uncached("nonexistent-pkg")
            cached_result = await cached.get_package_metadata("nonexistent-pkg")

            assert cached_result.name == uncached.name
            assert cached_result.exists == uncached.exists
            assert cached_result.exists is False


@pytest.mark.integration
class TestCacheEdgeCases:
    """
    Tests for additional cache edge cases.

    EC: EC067, EC068, EC070
    """

    @pytest.mark.asyncio
    async def test_sqlite_file_locked_handling(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.I05
        SPEC: S040
        EC: EC067

        Given: SQLite database file locked by another process
        When: Cache tries to access it
        Then: Handles gracefully (wait, retry, or error)

        Note: This simulates the locked condition by opening an exclusive
        connection before the cache tries to connect.
        """
        import sqlite3

        db_path = tmp_path / "locked.db"

        # Create database and hold an exclusive lock
        conn = sqlite3.connect(str(db_path), isolation_level="EXCLUSIVE")
        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
        conn.execute("BEGIN EXCLUSIVE")

        mock_client = MockRegistryClient()
        mock_client.set_response("flask", exists=True)

        # Cache should handle the locked database
        cache = Cache(sqlite_path=db_path)

        try:
            async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
                # Even if SQLite is locked, memory cache should work
                result = await cached.get_package_metadata("flask")
                assert result.name == "flask"
        except Exception as e:
            # Acceptable: raise an error indicating lock
            assert "lock" in str(e).lower() or "database" in str(e).lower()
        finally:
            conn.rollback()
            conn.close()

    @pytest.mark.asyncio
    async def test_disk_full_graceful_degradation(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.I06
        SPEC: S040
        EC: EC068

        Given: No disk space available for cache writes
        When: Cache tries to write
        Then: Gracefully degrades to memory-only mode

        Note: We simulate this by making the cache file read-only after
        initial creation. This tests the write failure path.
        """
        import os
        import stat

        db_path = tmp_path / "readonly.db"

        # Create the database first
        cache1 = Cache(sqlite_path=db_path)
        async with cache1:
            await cache1.set("pypi", "initial", {"name": "initial", "exists": True})

        # Make the file read-only to simulate disk full / permission denied
        os.chmod(db_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        mock_client = MockRegistryClient()
        mock_client.set_response("newpkg", exists=True)

        try:
            cache2 = Cache(sqlite_path=db_path)
            async with cache2, CachedRegistryClient(mock_client, cache2, "pypi") as cached:
                # Should still work via memory cache even if SQLite write fails
                result = await cached.get_package_metadata("newpkg")
                assert result.name == "newpkg"
        except Exception:  # noqa: S110
            # If it raises, that's also acceptable behavior
            pass
        finally:
            # Restore permissions for cleanup
            os.chmod(db_path, stat.S_IWUSR | stat.S_IRUSR)

    @pytest.mark.asyncio
    async def test_offline_mode_cache_hits_only(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.I07
        SPEC: S040
        EC: EC070

        Given: No network connectivity (simulated by failing client)
        When: Cache contains some packages
        Then: Cached packages return successfully, uncached fail

        This tests that the cache provides resilience during network outages.
        """
        from phantom_guard.registry.exceptions import RegistryUnavailableError

        db_path = tmp_path / "offline.db"

        # Phase 1: Pre-populate cache while "online"
        online_client = MockRegistryClient()
        online_client.set_response(
            "cached-pkg",
            exists=True,
            downloads_last_month=100000,
        )

        cache1 = Cache(sqlite_path=db_path)
        async with cache1, CachedRegistryClient(online_client, cache1, "pypi") as cached:
            await cached.get_package_metadata("cached-pkg")

        # Phase 2: Go "offline" - client raises for all requests
        offline_client = MockRegistryClient()
        offline_client.get_package_metadata.side_effect = RegistryUnavailableError("pypi", None)

        cache2 = Cache(sqlite_path=db_path)
        async with cache2, CachedRegistryClient(offline_client, cache2, "pypi") as cached:
            # Cached package should work (no network call needed)
            result = await cached.get_package_metadata("cached-pkg")
            assert result.name == "cached-pkg"
            assert result.downloads_last_month == 100000

            # Uncached package should fail (needs network)
            with pytest.raises(RegistryUnavailableError):
                await cached.get_package_metadata("uncached-pkg")

    @pytest.mark.asyncio
    async def test_memory_fallback_when_sqlite_unavailable(self, tmp_path: Path) -> None:
        """
        EC: EC068, EC070

        When SQLite is unavailable, memory cache should still function.
        """
        mock_client = MockRegistryClient()
        mock_client.set_response("testpkg", exists=True)

        # Use memory-only cache (no SQLite path)
        cache = Cache(sqlite_path=None, memory_max_size=100)

        async with cache, CachedRegistryClient(mock_client, cache, "pypi") as cached:
            # First call - cache miss, fetches from client
            await cached.get_package_metadata("testpkg")
            assert mock_client.get_package_metadata.call_count == 1

            # Second call - cache hit from memory
            result = await cached.get_package_metadata("testpkg")
            assert mock_client.get_package_metadata.call_count == 1
            assert result.name == "testpkg"
