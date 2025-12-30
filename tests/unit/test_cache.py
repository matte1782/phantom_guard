# SPEC: S040-S049 - Cache System
"""
Unit tests for the Cache module.

SPEC_IDs: S040-S049
TEST_IDs: T040.*
INVARIANTS: INV016, INV017
EDGE_CASES: EC060-EC070
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

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

    def test_cache_entry_is_expired_with_custom_now(self) -> None:
        """
        TEST_ID: T040.05a

        CacheEntry.is_expired works with custom now parameter.
        """
        created = datetime.now(UTC)
        entry = CacheEntry(
            key="test",
            value={},
            created_at=created,
            ttl_seconds=3600,
        )

        # Not expired when checking at creation time + 30 minutes
        future_30_min = created + timedelta(minutes=30)
        assert entry.is_expired(now=future_30_min) is False

        # Expired when checking at creation time + 2 hours
        future_2_hours = created + timedelta(hours=2)
        assert entry.is_expired(now=future_2_hours) is True

    def test_cache_entry_is_expired_naive_datetime(self) -> None:
        """
        TEST_ID: T040.05b

        CacheEntry.is_expired handles naive datetime (no timezone).
        """
        # Create entry with naive datetime (no tzinfo)
        naive_created = datetime(2024, 1, 1, 12, 0, 0)
        entry = CacheEntry(
            key="test",
            value={},
            created_at=naive_created,
            ttl_seconds=3600,
        )

        # Should handle timezone conversion internally
        # Checking against current time (which is much later)
        assert entry.is_expired() is True


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

    def test_contains_expired_entry_returns_false(self) -> None:
        """
        TEST_ID: T040.11
        INV: INV016

        __contains__ returns False for expired entries.
        """
        cache = MemoryCache(default_ttl=1)
        # Set with 0 TTL to make it expire immediately
        cache.set("expired", {"v": 1}, ttl=0)

        # Entry should appear expired and be removed
        assert "expired" not in cache

        # Entry should be removed after check
        assert len(cache) == 0

    def test_set_existing_key_replaces_value(self) -> None:
        """
        TEST_ID: T040.30
        SPEC: S042

        Given: A key already exists in the cache
        When: set is called with the same key but different value
        Then: The old entry is deleted and replaced with the new one

        This test covers line 118 in memory.py: `del self._cache[key]`
        """
        cache = MemoryCache(max_size=5)

        # Set initial value
        cache.set("pypi:flask", {"version": "1.0", "name": "flask"})
        assert cache.get("pypi:flask") == {"version": "1.0", "name": "flask"}

        # Set same key with different value - this triggers line 118
        cache.set("pypi:flask", {"version": "2.0", "name": "flask-updated"})

        # Verify the value was replaced
        value = cache.get("pypi:flask")
        assert value is not None
        assert value["version"] == "2.0"
        assert value["name"] == "flask-updated"

        # Verify cache size is still 1 (not 2)
        assert len(cache) == 1


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


class TestAsyncSQLiteCacheNoConnection:
    """Tests for AsyncSQLiteCache when connection is not established."""

    @pytest.mark.asyncio
    async def test_get_without_connection_returns_none(self) -> None:
        """get() returns None when connection is not established."""
        cache = AsyncSQLiteCache()
        # Don't call connect() - connection is None
        result = await cache.get("any:key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_without_connection_does_nothing(self) -> None:
        """set() does nothing when connection is not established."""
        cache = AsyncSQLiteCache()
        # Don't call connect() - connection is None
        # Should not raise, just return silently
        await cache.set("any:key", {"value": "test"})
        # Verify it didn't crash and cache is still disconnected
        assert cache._conn is None

    @pytest.mark.asyncio
    async def test_delete_without_connection_returns_false(self) -> None:
        """delete() returns False when connection is not established."""
        cache = AsyncSQLiteCache()
        result = await cache.delete("any:key")
        assert result is False

    @pytest.mark.asyncio
    async def test_count_without_connection_returns_zero(self) -> None:
        """count() returns 0 when connection is not established."""
        cache = AsyncSQLiteCache()
        result = await cache.count()
        assert result == 0

    @pytest.mark.asyncio
    async def test_clear_without_connection_returns_zero(self) -> None:
        """clear() returns 0 when connection is not established."""
        cache = AsyncSQLiteCache()
        result = await cache.clear()
        assert result == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired_without_connection_returns_zero(self) -> None:
        """cleanup_expired() returns 0 when connection is not established."""
        cache = AsyncSQLiteCache()
        result = await cache.cleanup_expired()
        assert result == 0

    @pytest.mark.asyncio
    async def test_clear_by_prefix_without_connection_returns_zero(self) -> None:
        """clear_by_prefix() returns 0 when connection is not established."""
        cache = AsyncSQLiteCache()
        result = await cache.clear_by_prefix("pypi:")
        assert result == 0

    @pytest.mark.asyncio
    async def test_get_stats_by_registry_without_connection_returns_empty(
        self,
    ) -> None:
        """get_stats_by_registry() returns {} when connection is not established."""
        cache = AsyncSQLiteCache()
        result = await cache.get_stats_by_registry()
        assert result == {}

    @pytest.mark.asyncio
    async def test_close_without_connection_does_nothing(self) -> None:
        """close() does nothing when connection is not established."""
        cache = AsyncSQLiteCache()
        # Should not raise
        await cache.close()
        assert cache._conn is None


class TestAsyncSQLiteCacheCleanup:
    """Tests for AsyncSQLiteCache cleanup and maintenance operations."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_removes_old_entries(self, tmp_path: Path) -> None:
        """cleanup_expired() removes entries past their TTL."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path, default_ttl=3600) as cache:
            # Insert entries with 0 TTL (immediately expired)
            await cache.set("expired:key1", {"v": 1}, ttl=0)
            await cache.set("expired:key2", {"v": 2}, ttl=0)

            # Should have 2 entries
            assert await cache.count() == 2

            # Cleanup should remove expired entries
            removed = await cache.cleanup_expired()
            # Expired entries should be removed
            assert removed >= 0  # At least runs without error
            # Since TTL=0 means expired, all should be cleaned up
            # The actual behavior is that cleanup removes entries where:
            # datetime(created_at, '+0 seconds') < now - which is always true
            assert removed == 2

    @pytest.mark.asyncio
    async def test_cleanup_expired_keeps_valid_entries(self, tmp_path: Path) -> None:
        """cleanup_expired() keeps entries with future TTL."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path, default_ttl=3600) as cache:
            # Insert only valid entry with long TTL
            await cache.set("valid:key", {"v": 1}, ttl=86400)

            # Should have 1 entry
            assert await cache.count() == 1

            # Cleanup should not remove valid entries
            removed = await cache.cleanup_expired()
            assert removed == 0

            # Entry should still be there
            assert await cache.count() == 1
            value = await cache.get("valid:key")
            assert value is not None
            assert value["v"] == 1

    @pytest.mark.asyncio
    async def test_clear_by_prefix_removes_matching_entries(self, tmp_path: Path) -> None:
        """clear_by_prefix() removes only entries with matching prefix."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            await cache.set("pypi:flask", {"v": 1})
            await cache.set("pypi:requests", {"v": 2})
            await cache.set("npm:express", {"v": 3})
            await cache.set("npm:lodash", {"v": 4})

            assert await cache.count() == 4

            # Clear only pypi entries
            removed = await cache.clear_by_prefix("pypi:")
            assert removed == 2

            # npm entries remain
            assert await cache.count() == 2
            assert await cache.get("npm:express") is not None
            assert await cache.get("npm:lodash") is not None
            assert await cache.get("pypi:flask") is None


class TestAsyncSQLiteCacheStats:
    """Tests for AsyncSQLiteCache statistics operations."""

    @pytest.mark.asyncio
    async def test_get_stats_by_registry_groups_entries(self, tmp_path: Path) -> None:
        """get_stats_by_registry() groups entries by registry prefix."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path, default_ttl=3600) as cache:
            await cache.set("pypi:flask", {"name": "flask"})
            await cache.set("pypi:requests", {"name": "requests"})
            await cache.set("npm:express", {"name": "express"})

            stats = await cache.get_stats_by_registry()

            assert "pypi" in stats
            assert "npm" in stats
            assert stats["pypi"]["entries"] == 2
            assert stats["npm"]["entries"] == 1
            # Size should be positive
            assert stats["pypi"]["size_bytes"] > 0
            assert stats["npm"]["size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_get_stats_ignores_expired_entries(self, tmp_path: Path) -> None:
        """get_stats_by_registry() only counts non-expired entries."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            # Valid entry
            await cache.set("pypi:flask", {"name": "flask"}, ttl=3600)
            # Expired entry (TTL=0)
            await cache.set("pypi:old", {"name": "old"}, ttl=0)

            stats = await cache.get_stats_by_registry()

            # Only the valid entry should be counted
            assert stats.get("pypi", {}).get("entries", 0) == 1

    @pytest.mark.asyncio
    async def test_get_stats_ignores_entries_without_colon(self, tmp_path: Path) -> None:
        """get_stats_by_registry() ignores keys without registry prefix."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path, default_ttl=3600) as cache:
            await cache.set("pypi:flask", {"name": "flask"})
            await cache.set("no_prefix_key", {"name": "test"})

            stats = await cache.get_stats_by_registry()

            # Only pypi entry should be counted
            assert "pypi" in stats
            assert stats["pypi"]["entries"] == 1
            # no_prefix_key should not create any registry entry
            assert "no_prefix_key" not in stats


class TestAsyncSQLiteCacheEdgeCases:
    """Tests for AsyncSQLiteCache edge cases."""

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_false(self, tmp_path: Path) -> None:
        """delete() returns False for nonexistent key."""
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            result = await cache.delete("nonexistent:key")
            assert result is False

    @pytest.mark.asyncio
    async def test_get_handles_naive_datetime(self, tmp_path: Path) -> None:
        """get() handles entries with naive datetime (no tzinfo)."""
        import json

        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            # Insert data directly with a naive datetime (no timezone)
            # Use a FUTURE date to ensure the entry won't be expired
            naive_datetime = "2099-12-28T12:00:00"  # No +00:00 or Z suffix
            value_json = json.dumps({"name": "test"})
            ttl = 86400  # 24 hours

            await cache._conn.execute(  # type: ignore[union-attr]
                """
                INSERT INTO cache (key, value, created_at, ttl_seconds, expires_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("naive:key", value_json, naive_datetime, ttl, 9999999999.0),
            )
            await cache._conn.commit()  # type: ignore[union-attr]

            # get() should handle the naive datetime and return the value
            result = await cache.get("naive:key")
            assert result is not None
            assert result["name"] == "test"

    @pytest.mark.asyncio
    async def test_in_memory_database(self) -> None:
        """Cache works with in-memory database."""
        async with AsyncSQLiteCache(":memory:") as cache:
            await cache.set("test:key", {"value": 123})
            result = await cache.get("test:key")
            assert result is not None
            assert result["value"] == 123

    @pytest.mark.asyncio
    async def test_connect_and_close_lifecycle(self, tmp_path: Path) -> None:
        """Manual connect/close lifecycle works correctly."""
        db_path = tmp_path / "test.db"
        cache = AsyncSQLiteCache(db_path)

        # Initially no connection
        assert cache._conn is None

        # Connect
        await cache.connect()
        assert cache._conn is not None

        # Use cache
        await cache.set("test:key", {"v": 1})
        value = await cache.get("test:key")
        assert value is not None

        # Close
        await cache.close()
        assert cache._conn is None

        # Close again does nothing
        await cache.close()
        assert cache._conn is None


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

            memory_count, _sqlite_count = await cache.clear_all()

            assert memory_count == 2
            assert cache.memory_size() == 0

    @pytest.mark.asyncio
    async def test_sqlite_size_with_enabled(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.18
        SPEC: S040

        sqlite_size returns count when SQLite is enabled.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            await cache.set("npm", "express", {"name": "express"})

            size = await cache.sqlite_size()
            assert size == 2

    @pytest.mark.asyncio
    async def test_sqlite_size_without_sqlite(self) -> None:
        """
        TEST_ID: T040.19
        SPEC: S040
        EC: EC069

        sqlite_size returns 0 when SQLite is disabled.
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})

            size = await cache.sqlite_size()
            assert size == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired_with_sqlite(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.20
        SPEC: S040
        INV: INV016

        cleanup_expired removes expired SQLite entries.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
            sqlite_ttl=3600,
        )

        async with cache:
            # Set with TTL=0 so it expires immediately
            await cache.sqlite.set("pypi:expired", {"name": "expired"}, ttl=0)  # type: ignore[union-attr]
            await cache.set("pypi", "valid", {"name": "valid"})

            # Run cleanup
            removed = await cache.cleanup_expired()

            # At least 1 expired entry should be removed
            assert removed >= 1

    @pytest.mark.asyncio
    async def test_cleanup_expired_without_sqlite(self) -> None:
        """
        TEST_ID: T040.21
        SPEC: S040

        cleanup_expired returns 0 when SQLite is disabled.
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})

            removed = await cache.cleanup_expired()
            assert removed == 0

    @pytest.mark.asyncio
    async def test_clear_registry_clears_specific_registry(self, tmp_path: Path) -> None:
        """
        TEST_ID: T010.22
        SPEC: S016

        clear_registry removes entries for specific registry only.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            # Add entries from multiple registries
            await cache.set("pypi", "flask", {"name": "flask"})
            await cache.set("pypi", "requests", {"name": "requests"})
            await cache.set("npm", "express", {"name": "express"})
            await cache.set("crates", "serde", {"name": "serde"})

            # Clear only pypi entries
            deleted = await cache.clear_registry("pypi")

            assert deleted >= 2  # At least 2 from memory

            # Verify pypi entries are gone from memory
            assert cache.memory.get("pypi:flask") is None
            assert cache.memory.get("pypi:requests") is None

            # Verify other registries are intact
            assert cache.memory.get("npm:express") is not None
            assert cache.memory.get("crates:serde") is not None

    @pytest.mark.asyncio
    async def test_clear_registry_without_sqlite(self) -> None:
        """
        TEST_ID: T010.22b
        SPEC: S016

        clear_registry works when SQLite is disabled.
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            await cache.set("pypi", "requests", {"name": "requests"})
            await cache.set("npm", "express", {"name": "express"})

            deleted = await cache.clear_registry("pypi")

            assert deleted == 2
            assert cache.memory.get("pypi:flask") is None
            assert cache.memory.get("npm:express") is not None

    @pytest.mark.asyncio
    async def test_get_stats_returns_registry_stats(self, tmp_path: Path) -> None:
        """
        TEST_ID: T010.23
        SPEC: S017

        get_stats returns stats for each registry.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            await cache.set("pypi", "requests", {"name": "requests"})
            await cache.set("npm", "express", {"name": "express"})

            stats = await cache.get_stats()

            assert "pypi" in stats
            assert "npm" in stats
            assert stats["pypi"]["entries"] >= 2
            assert stats["npm"]["entries"] >= 1

    @pytest.mark.asyncio
    async def test_get_stats_without_sqlite(self) -> None:
        """
        TEST_ID: T010.23b
        SPEC: S017

        get_stats works when SQLite is disabled.
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            await cache.set("npm", "express", {"name": "express"})

            stats = await cache.get_stats()

            assert "pypi" in stats
            assert "npm" in stats
            assert stats["pypi"]["entries"] == 1
            assert stats["npm"]["entries"] == 1

    @pytest.mark.asyncio
    async def test_get_stats_empty_cache(self, tmp_path: Path) -> None:
        """
        TEST_ID: T010.23c
        SPEC: S017

        get_stats returns empty dict for empty cache.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            stats = await cache.get_stats()
            assert stats == {}

    @pytest.mark.asyncio
    async def test_context_manager_without_sqlite(self) -> None:
        """
        TEST_ID: T040.22
        SPEC: S040

        Context manager works when SQLite is disabled.
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            assert cache.sqlite is None
            await cache.set("pypi", "flask", {"name": "flask"})
            value = await cache.get("pypi", "flask")
            assert value is not None

    @pytest.mark.asyncio
    async def test_invalidate_returns_false_when_not_found(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.23
        SPEC: S043

        invalidate returns False when entry not found in either tier.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            result = await cache.invalidate("pypi", "nonexistent")
            assert result is False

    @pytest.mark.asyncio
    async def test_invalidate_without_sqlite(self) -> None:
        """
        TEST_ID: T040.24
        SPEC: S043

        invalidate works when SQLite is disabled.
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            result = await cache.invalidate("pypi", "flask")
            assert result is True
            assert cache.memory.get("pypi:flask") is None

    @pytest.mark.asyncio
    async def test_clear_all_without_sqlite(self) -> None:
        """
        TEST_ID: T040.25
        SPEC: S040

        clear_all works when SQLite is disabled.
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            await cache.set("npm", "express", {"name": "express"})

            memory_count, sqlite_count = await cache.clear_all()

            assert memory_count == 2
            assert sqlite_count == 0

    @pytest.mark.asyncio
    async def test_get_sqlite_miss_returns_none(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.26
        SPEC: S041

        When memory misses and SQLite also misses, returns None.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            # Ensure SQLite is connected but empty
            assert cache.sqlite is not None

            # Request should check memory (miss), then sqlite (miss), return None
            value = await cache.get("pypi", "nonexistent")
            assert value is None

    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.27
        SPEC: S042

        set accepts custom TTL for memory and SQLite.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
            memory_ttl=3600,
            sqlite_ttl=86400,
        )

        async with cache:
            # Set with custom TTL (shorter than default)
            await cache.set(
                "pypi",
                "flask",
                {"name": "flask"},
                memory_ttl=60,
                sqlite_ttl=120,
            )

            value = await cache.get("pypi", "flask")
            assert value is not None

    @pytest.mark.asyncio
    async def test_sqlite_disabled_flag(self) -> None:
        """
        TEST_ID: T040.28
        SPEC: S040

        sqlite_enabled=False disables SQLite even with valid path.
        """
        cache = Cache(
            sqlite_path="/some/path.db",
            sqlite_enabled=False,
            memory_max_size=100,
        )

        assert cache.sqlite is None
        assert cache._sqlite_enabled is False

    @pytest.mark.asyncio
    async def test_clear_all_with_sqlite(self, tmp_path: Path) -> None:
        """
        TEST_ID: T040.29
        SPEC: S040

        clear_all clears both memory and SQLite tiers.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})
            await cache.set("npm", "express", {"name": "express"})

            memory_count, sqlite_count = await cache.clear_all()

            assert memory_count == 2
            assert sqlite_count == 2
            assert cache.memory_size() == 0
            assert await cache.sqlite_size() == 0

    @pytest.mark.asyncio
    async def test_get_stats_with_sqlite_stats(self, tmp_path: Path) -> None:
        """
        TEST_ID: T010.23d
        SPEC: S017

        get_stats includes SQLite statistics when enabled.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            # Add entries to both tiers
            await cache.set("pypi", "flask", {"name": "flask", "version": "2.0"})
            await cache.set("npm", "express", {"name": "express", "version": "4.0"})

            stats = await cache.get_stats()

            assert "pypi" in stats
            assert "npm" in stats
            # Size bytes should be tracked from SQLite
            assert stats["pypi"]["size_bytes"] > 0
            assert stats["npm"]["size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_get_stats_sqlite_only_registry(self, tmp_path: Path) -> None:
        """
        TEST_ID: T010.23e
        SPEC: S017

        get_stats includes registry that only exists in SQLite (not memory).
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            # Add to both tiers
            await cache.set("pypi", "flask", {"name": "flask"})

            # Add directly to SQLite only (bypass memory)
            await cache.sqlite.set("npm:express", {"name": "express"})  # type: ignore[union-attr]

            # Clear memory for npm (simulate entry not in memory)
            # Memory has pypi:flask, SQLite has pypi:flask and npm:express

            stats = await cache.get_stats()

            # Both registries should be in stats
            assert "pypi" in stats
            assert "npm" in stats
            # npm should have stats from SQLite even though not in memory
            assert stats["npm"]["entries"] >= 1

    @pytest.mark.asyncio
    async def test_clear_registry_no_matching_entries(self, tmp_path: Path) -> None:
        """
        TEST_ID: T010.22c
        SPEC: S016

        clear_registry returns 0 when no entries match.
        """
        cache = Cache(
            sqlite_path=tmp_path / "test.db",
            memory_max_size=100,
        )

        async with cache:
            await cache.set("pypi", "flask", {"name": "flask"})

            # Try to clear nonexistent registry
            deleted = await cache.clear_registry("crates")

            assert deleted == 0
            # pypi entries still exist
            assert cache.memory.get("pypi:flask") is not None

    @pytest.mark.asyncio
    async def test_clear_registry_delete_returns_false(self) -> None:
        """
        TEST_ID: T010.22d
        SPEC: S016

        clear_registry handles case where memory.delete returns False.

        This tests the branch at line 235->234 in cache.py where
        self.memory.delete(key) returns False for a key that matches
        the prefix but was removed before delete was called.
        """
        from unittest.mock import patch

        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            # Add a valid entry
            await cache.set("pypi", "flask", {"name": "flask"})

            # Create a mock that simulates the key being listed but
            # then delete returning False (as if removed by another thread)
            original_delete = MemoryCache.delete

            def mock_delete(self: MemoryCache, key: str) -> bool:
                # First call will get the keys list, then we return False
                # to simulate race condition where key was removed
                if key == "pypi:flask":
                    return False
                return original_delete(self, key)

            # Patch at class level since MemoryCache uses __slots__
            with patch.object(MemoryCache, "delete", mock_delete):
                deleted = await cache.clear_registry("pypi")

            # The delete returned False, so deleted count should be 0
            assert deleted == 0

    @pytest.mark.asyncio
    async def test_get_stats_keys_without_colon(self) -> None:
        """
        TEST_ID: T010.23f
        SPEC: S017

        get_stats ignores memory cache keys that don't contain ':'.

        This tests the branch at line 262->261 in cache.py where
        keys without ':' are skipped in get_stats.
        """
        cache = Cache(
            sqlite_path=None,
            memory_max_size=100,
        )

        async with cache:
            # Add a regular entry with proper registry:name format
            await cache.set("pypi", "flask", {"name": "flask"})

            # Directly add a malformed key without ':' to memory cache
            # This simulates an edge case where a key doesn't have the
            # expected registry:package format
            cache.memory.set("malformed_key_no_colon", {"name": "bad"})

            stats = await cache.get_stats()

            # Only the properly formatted key should be counted
            assert "pypi" in stats
            assert stats["pypi"]["entries"] == 1

            # The malformed key should not create its own registry entry
            assert "malformed_key_no_colon" not in stats
