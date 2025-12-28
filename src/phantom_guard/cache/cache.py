"""
IMPLEMENTS: S040-S049
INVARIANTS: INV016, INV017
Two-tier cache system: sync memory + async SQLite.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from phantom_guard.cache.memory import MemoryCache
from phantom_guard.cache.sqlite import AsyncSQLiteCache
from phantom_guard.cache.types import make_cache_key

if TYPE_CHECKING:
    from types import TracebackType

# Type alias for cached values (JSON-serializable data)
CacheValue = dict[str, Any]


class Cache:
    """
    IMPLEMENTS: S040
    INV: INV016, INV017

    Two-tier cache: Memory LRU (Tier 1, sync) + SQLite (Tier 2, async).

    Read flow:
        1. Check memory cache (sync - instant)
        2. If miss, check SQLite (async - non-blocking)
        3. If SQLite hit, promote to memory
        4. Return value or None

    Write flow:
        1. Write to memory (sync)
        2. Write to SQLite (async)

    Design rationale:
        - Memory is sync because it's pure in-memory (no I/O)
        - SQLite is async to avoid blocking event loop during disk I/O

    Attributes:
        memory: In-memory LRU cache (Tier 1)
        sqlite: SQLite persistent cache (Tier 2), None if disabled
    """

    def __init__(
        self,
        memory_max_size: int = 1000,
        memory_ttl: int = 3600,
        sqlite_path: str | Path | None = None,
        sqlite_ttl: int = 86400,
        sqlite_enabled: bool = True,
    ) -> None:
        """
        Initialize two-tier cache.

        Args:
            memory_max_size: Max entries in memory cache (default 1000)
            memory_ttl: Memory cache TTL in seconds (default 3600 = 1 hour)
            sqlite_path: Path to SQLite database file (None disables SQLite)
            sqlite_ttl: SQLite cache TTL in seconds (default 86400 = 24 hours)
            sqlite_enabled: Whether to enable SQLite tier (default True)
        """
        self.memory = MemoryCache(
            max_size=memory_max_size,
            default_ttl=memory_ttl,
        )

        self._sqlite_enabled = sqlite_enabled and sqlite_path is not None
        self.sqlite: AsyncSQLiteCache | None = None

        if self._sqlite_enabled and sqlite_path is not None:
            self.sqlite = AsyncSQLiteCache(
                db_path=sqlite_path,
                default_ttl=sqlite_ttl,
            )

    async def __aenter__(self) -> Cache:
        """Async context manager entry - connects SQLite."""
        if self.sqlite:
            await self.sqlite.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit - closes SQLite."""
        if self.sqlite:
            await self.sqlite.close()

    async def get(self, registry: str, package_name: str) -> CacheValue | None:
        """
        IMPLEMENTS: S041
        TEST: T040.01, T040.02, T040.11, T040.12

        Get cached metadata.
        Checks memory first (sync), then SQLite (async).

        Args:
            registry: Registry name (pypi, npm, crates)
            package_name: Package name

        Returns:
            Cached value or None if not found/expired
        """
        key = make_cache_key(registry, package_name)

        # Tier 1: Memory (sync - no await needed)
        value = self.memory.get(key)
        if value is not None:
            return value

        # Tier 2: SQLite (async)
        if self.sqlite:
            value = await self.sqlite.get(key)
            if value is not None:
                # Promote to memory (sync)
                self.memory.set(key, value)
                return value

        return None

    async def set(
        self,
        registry: str,
        package_name: str,
        value: CacheValue,
        memory_ttl: int | None = None,
        sqlite_ttl: int | None = None,
    ) -> None:
        """
        IMPLEMENTS: S042
        TEST: T040.03

        Cache metadata in both tiers.
        Memory write is sync, SQLite write is async.

        Args:
            registry: Registry name (pypi, npm, crates)
            package_name: Package name
            value: Value to cache
            memory_ttl: Memory cache TTL (uses default if None)
            sqlite_ttl: SQLite cache TTL (uses default if None)
        """
        key = make_cache_key(registry, package_name)

        # Write to memory (sync)
        self.memory.set(key, value, ttl=memory_ttl)

        # Write to SQLite (async)
        if self.sqlite:
            await self.sqlite.set(key, value, ttl=sqlite_ttl)

    async def invalidate(self, registry: str, package_name: str) -> bool:
        """
        IMPLEMENTS: S043

        Remove entry from both tiers.

        Args:
            registry: Registry name (pypi, npm, crates)
            package_name: Package name

        Returns:
            True if entry was found in either tier
        """
        key = make_cache_key(registry, package_name)

        memory_deleted = self.memory.delete(key)
        sqlite_deleted = await self.sqlite.delete(key) if self.sqlite else False

        return memory_deleted or sqlite_deleted

    async def clear_all(self) -> tuple[int, int]:
        """
        Clear both cache tiers.

        Returns:
            Tuple of (memory_count, sqlite_count) deleted
        """
        memory_count = self.memory.clear()
        sqlite_count = 0
        if self.sqlite:
            sqlite_count = await self.sqlite.clear()
        return memory_count, sqlite_count

    async def cleanup_expired(self) -> int:
        """
        Remove expired entries from SQLite tier.

        Memory entries are cleaned up lazily on access.

        Returns:
            Number of SQLite entries removed
        """
        if self.sqlite:
            return await self.sqlite.cleanup_expired()
        return 0

    def memory_size(self) -> int:
        """Return number of entries in memory cache."""
        return len(self.memory)

    async def sqlite_size(self) -> int:
        """Return number of entries in SQLite cache."""
        if self.sqlite:
            return await self.sqlite.count()
        return 0

    async def clear_registry(self, registry: str) -> int:
        """
        IMPLEMENTS: S016
        TEST: T010.22

        Clear all entries for a specific registry.

        Args:
            registry: Registry name (pypi, npm, crates)

        Returns:
            Number of entries deleted
        """
        prefix = f"{registry}:"
        deleted = 0

        # Clear from memory
        keys_to_delete = [k for k in self.memory._cache if k.startswith(prefix)]
        for key in keys_to_delete:
            if self.memory.delete(key):
                deleted += 1

        # Clear from SQLite
        if self.sqlite:
            deleted += await self.sqlite.clear_by_prefix(prefix)

        return deleted

    async def get_stats(self) -> dict[str, dict[str, Any]]:
        """
        IMPLEMENTS: S017
        TEST: T010.23

        Get cache statistics by registry.

        Returns:
            Dict mapping registry names to stats:
            {
                "pypi": {"entries": int, "size_bytes": int, "hit_rate": float | None},
                ...
            }
        """
        stats: dict[str, dict[str, Any]] = {}

        # Gather from memory cache
        for key in self.memory._cache:
            if ":" in key:
                registry = key.split(":")[0]
                if registry not in stats:
                    stats[registry] = {"entries": 0, "size_bytes": 0, "hit_rate": None}
                stats[registry]["entries"] += 1

        # Gather from SQLite (if enabled)
        if self.sqlite:
            sqlite_stats = await self.sqlite.get_stats_by_registry()
            for registry, data in sqlite_stats.items():
                if registry not in stats:
                    stats[registry] = {"entries": 0, "size_bytes": 0, "hit_rate": None}
                stats[registry]["entries"] += data.get("entries", 0)
                stats[registry]["size_bytes"] += data.get("size_bytes", 0)

        return stats
