# SPEC: S040-S049 - Cache System
"""
Unit tests for the Cache module.

SPEC_IDs: S040-S049
TEST_IDs: T040.*
INVARIANTS: INV016, INV017
EDGE_CASES: EC060-EC070
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from phantom_guard.cache.cache import Cache
from phantom_guard.cache.memory import MemoryCache
from phantom_guard.cache.sqlite import AsyncSQLiteCache
from phantom_guard.cache.types import CacheEntry, make_cache_key


class TestCacheEntry:
    """Tests for CacheEntry data structure."""

    def test_cache_entry_creation(self) -> None:
        """CacheEntry can be created with valid data."""
        entry = CacheEntry(
            key="pypi:flask",
            value={"name": "flask", "exists": True},
            created_at=datetime.now(UTC),
            ttl_seconds=3600,
        )
        assert entry.key == "pypi:flask"
        assert entry.value["name"] == "flask"
        assert entry.ttl_seconds == 3600

    def test_cache_entry_expires_at(self) -> None:
        """CacheEntry calculates expiration time correctly."""
        created = datetime.now(UTC)
        entry = CacheEntry(
            key="test",
            value={},
            created_at=created,
            ttl_seconds=3600,
        )
        expected_expires = created + timedelta(seconds=3600)
        assert entry.expires_at == expected_expires

    def test_cache_entry_is_expired_true(self) -> None:
        """
        TEST_ID: T040.04
        INV: INV016

        CacheEntry.is_expired returns True for expired entries.
        """
        past = datetime.now(UTC) - timedelta(hours=2)
        entry = CacheEntry(
            key="test",
            value={},
            created_at=past,
            ttl_seconds=3600,
        )
        assert entry.is_expired() is True

    def test_cache_entry_is_expired_false(self) -> None:
        """
        TEST_ID: T040.05

        CacheEntry.is_expired returns False for valid entries.
        """
        entry = CacheEntry(
            key="test",
            value={},
            created_at=datetime.now(UTC),
            ttl_seconds=3600,
        )
        assert entry.is_expired() is False


class TestMakeCacheKey:
    """Tests for make_cache_key utility."""

    def test_cache_key_format(self) -> None:
        """Cache key has correct format."""
        key = make_cache_key("pypi", "flask")
        assert key == "pypi:flask"

    def test_cache_key_normalized(self) -> None:
        """
        TEST_ID: T040.10

        Cache key is normalized (lowercase).
        """
        key = make_cache_key("PyPI", "Flask")
        assert key == "pypi:flask"

    def test_cache_key_underscores_replaced(self) -> None:
        """Underscores replaced with hyphens."""
        key = make_cache_key("pypi", "my_package")
        assert key == "pypi:my-package"

    def test_cache_key_different_registries(self) -> None:
        """
        TEST_ID: T040.09
        EC: EC066

        Same package name, different registries = different keys.
        """
        pypi_key = make_cache_key("pypi", "requests")
        npm_key = make_cache_key("npm", "requests")
        assert pypi_key != npm_key
        assert pypi_key == "pypi:requests"
        assert npm_key == "npm:requests"


class TestMemoryCacheBasics:
    """Tests for basic MemoryCache operations.

    SPEC: S040-S049 - Cache system
    """

    def test_cache_hit_returns_cached_value(self) -> None:
        """
        TEST_ID: T040.01
        SPEC: S040
        INV: INV016
        EC: EC060

        Given: Entry exists in cache and not expired
        When: get is called
        Then: Returns cached value
        """
        cache = MemoryCache()
        cache.set("pypi:flask", {"name": "flask", "exists": True})

        value = cache.get("pypi:flask")

        assert value is not None
        assert value["name"] == "flask"

    def test_cache_miss_returns_none(self) -> None:
        """
        TEST_ID: T040.02
        SPEC: S040
        EC: EC061

        Given: Entry does not exist in cache
        When: get is called
        Then: Returns None
        """
        cache = MemoryCache()

        value = cache.get("pypi:nonexistent")

        assert value is None

    def test_cache_set_stores_value(self) -> None:
        """
        TEST_ID: T040.03
        SPEC: S040

        Given: A value to cache
        When: set is called then get is called
        Then: Returns the stored value
        """
        cache = MemoryCache()

        cache.set("pypi:requests", {"name": "requests", "exists": True})
        value = cache.get("pypi:requests")

        assert value is not None
        assert value["name"] == "requests"


class TestMemoryCacheTTL:
    """Tests for MemoryCache TTL behavior (INV016)."""

    def test_cache_ttl_honored(self) -> None:
        """
        TEST_ID: T040.04
        SPEC: S040
        INV: INV016
        EC: EC062

        Given: Entry with TTL expired
        When: get is called
        Then: Returns None (stale data not returned)
        """
        cache = MemoryCache(default_ttl=1)
        cache.set("pypi:flask", {"name": "flask"}, ttl=0)

        # Entry should be expired immediately with TTL=0
        value = cache.get("pypi:flask")

        assert value is None

    def test_cache_ttl_not_expired(self) -> None:
        """
        TEST_ID: T040.05
        SPEC: S040
        INV: INV016

        Given: Entry with TTL not expired
        When: get is called
        Then: Returns cached value
        """
        cache = MemoryCache(default_ttl=3600)
        cache.set("pypi:flask", {"name": "flask"})

        value = cache.get("pypi:flask")

        assert value is not None
        assert value["name"] == "flask"

    def test_cache_ttl_default_value(self) -> None:
        """
        TEST_ID: T040.06
        SPEC: S040

        Given: Cache initialized with default TTL
        When: Checking TTL config
        Then: TTL is 1 hour (3600 seconds)
        """
        cache = MemoryCache()
        assert cache.default_ttl == 3600


class TestMemoryCacheLRU:
    """Tests for MemoryCache LRU eviction (INV017)."""

    def test_cache_lru_eviction(self) -> None:
        """
        TEST_ID: T040.07
        SPEC: S040
        INV: INV017
        EC: EC063

        Given: Cache at max capacity
        When: New entry is added
        Then: Least recently used entry is evicted
        """
        cache = MemoryCache(max_size=3)

        cache.set("key1", {"n": 1})
        cache.set("key2", {"n": 2})
        cache.set("key3", {"n": 3})

        # Access key1 to make it recently used
        cache.get("key1")

        # Add key4 - should evict key2 (LRU)
        cache.set("key4", {"n": 4})

        assert cache.get("key1") is not None  # Still there (accessed)
        assert cache.get("key2") is None  # Evicted (LRU)
        assert cache.get("key3") is not None  # Still there
        assert cache.get("key4") is not None  # Newly added

    def test_cache_size_limit_enforced(self) -> None:
        """
        TEST_ID: T040.08
        SPEC: S040
        INV: INV017

        Given: Cache with size limit
        When: Adding beyond limit
        Then: Size never exceeds limit
        """
        cache = MemoryCache(max_size=5)

        for i in range(10):
            cache.set(f"key{i}", {"n": i})

        assert len(cache) == 5


class TestMemoryCacheOperations:
    """Tests for additional MemoryCache operations."""

    def test_delete_existing_key(self) -> None:
        """Delete returns True for existing key."""
        cache = MemoryCache()
        cache.set("test", {"v": 1})

        result = cache.delete("test")

        assert result is True
        assert cache.get("test") is None

    def test_delete_nonexistent_key(self) -> None:
        """Delete returns False for nonexistent key."""
        cache = MemoryCache()

        result = cache.delete("nonexistent")

        assert result is False

    def test_clear_removes_all(self) -> None:
        """Clear removes all entries and returns count."""
        cache = MemoryCache()
        cache.set("key1", {"v": 1})
        cache.set("key2", {"v": 2})

        count = cache.clear()

        assert count == 2
        assert len(cache) == 0

    def test_contains_check(self) -> None:
        """__contains__ checks key existence."""
        cache = MemoryCache()
        cache.set("exists", {"v": 1})

        assert "exists" in cache
        assert "notexists" not in cache


class TestAsyncSQLiteCache:
    """Tests for AsyncSQLiteCache."""

    @pytest.mark.asyncio
    async def test_sqlite_async_connect(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.17
        SPEC: S040

        SQLite connects and creates schema asynchronously.
        """
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            assert cache._conn is not None
            count = await cache.count()
            assert count == 0

    @pytest.mark.asyncio
    async def test_sqlite_async_set_get(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.15
        SPEC: S041, S042

        Async set and get operations work.
        """
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            await cache.set("test:key", {"name": "test", "exists": True})

            value = await cache.get("test:key")
            assert value is not None
            assert value["name"] == "test"

    @pytest.mark.asyncio
    async def test_sqlite_async_ttl_honored(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.16
        SPEC: S041
        INV: INV016

        Expired entries return None.
        """
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path, default_ttl=1) as cache:
            await cache.set("test:key", {"name": "test"}, ttl=0)

            # Should be expired immediately
            value = await cache.get("test:key")
            assert value is None

    @pytest.mark.asyncio
    async def test_sqlite_miss_returns_none(self, tmp_path: Path) -> None:
        """Cache miss returns None."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            value = await cache.get("nonexistent")
            assert value is None

    @pytest.mark.asyncio
    async def test_sqlite_delete(self, tmp_path: Path) -> None:
        """Delete removes entry from SQLite."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            await cache.set("test:key", {"name": "test"})
            assert await cache.get("test:key") is not None

            deleted = await cache.delete("test:key")
            assert deleted is True
            assert await cache.get("test:key") is None

    @pytest.mark.asyncio
    async def test_sqlite_clear(self, tmp_path: Path) -> None:
        """Clear removes all entries."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            await cache.set("key1", {"v": 1})
            await cache.set("key2", {"v": 2})
            assert await cache.count() == 2

            count = await cache.clear()
            assert count == 2
            assert await cache.count() == 0

    @pytest.mark.asyncio
    async def test_sqlite_persistence(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.15
        SPEC: S040

        Entries persist across sessions.
        """
        db_path = tmp_path / "test.db"

        # First session: write data
        async with AsyncSQLiteCache(db_path) as cache:
            await cache.set("pypi:flask", {"name": "flask"})

        # Second session: read data
        async with AsyncSQLiteCache(db_path) as cache:
            value = await cache.get("pypi:flask")
            assert value is not None
            assert value["name"] == "flask"


class TestTwoTierCache:
    """Tests for unified two-tier Cache."""

    @pytest.mark.asyncio
    async def test_memory_hit_skips_sqlite(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.11
        SPEC: S041

        Memory hit returns immediately without SQLite query.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            # Set only in memory (using internal API)
            cache.memory.set("pypi:flask", {"name": "flask"})

            # Get should hit memory
            value = await cache.get("pypi", "flask")
            assert value is not None
            assert value["name"] == "flask"

    @pytest.mark.asyncio
    async def test_sqlite_hit_promotes_to_memory(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.12
        SPEC: S041

        SQLite hit promotes value to memory cache.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            # Set directly in SQLite (bypass memory)
            await cache.sqlite.set("pypi:requests", {"name": "requests"})  # type: ignore[union-attr]

            # Memory should be empty
            assert cache.memory.get("pypi:requests") is None

            # Get should hit SQLite and promote to memory
            value = await cache.get("pypi", "requests")
            assert value is not None
            assert value["name"] == "requests"

            # Now memory should have it
            assert cache.memory.get("pypi:requests") is not None

    @pytest.mark.asyncio
    async def test_set_writes_to_both_tiers(self, tmp_path: Path) -> None:
        """Set writes to both memory and SQLite."""
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})

            # Check memory
            assert cache.memory.get("pypi:flask") is not None

            # Check SQLite
            assert await cache.sqlite.get("pypi:flask") is not None  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_invalidate_removes_from_both_tiers(self, tmp_path: Path) -> None:
        """Invalidate removes from both memory and SQLite."""
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})

            result = await cache.invalidate("pypi", "flask")
            assert result is True

            # Removed from both
            assert cache.memory.get("pypi:flask") is None
            assert await cache.sqlite.get("pypi:flask") is None  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_memory_only_mode(self) -> None:
        """
        TEST_ID: T040.11
        EC: EC069

        Cache works with memory only (SQLite disabled).
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            value = await cache.get("pypi", "flask")

            assert value is not None
            assert value["name"] == "flask"
            assert cache.sqlite is None

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self, tmp_path: Path) -> None:
        """Cache miss from both tiers returns None."""
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            value = await cache.get("pypi", "nonexistent")
            assert value is None

    @pytest.mark.asyncio
    async def test_clear_all_clears_both_tiers(self, tmp_path: Path) -> None:
        """clear_all removes entries from both tiers."""
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            await cache.set("npm", "express", {"name": "express"})

            memory_count, sqlite_count = await cache.clear_all()

            assert memory_count == 2
            assert cache.memory_size() == 0
