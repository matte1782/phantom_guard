"""
IMPLEMENTS: S040, S041, S042
INVARIANTS: INV016, INV017
In-memory LRU cache (Tier 1).

This cache is synchronous as it performs no I/O operations.
Thread-safe via Lock for concurrent access.
"""

from __future__ import annotations

from collections import OrderedDict
from datetime import UTC, datetime
from threading import Lock
from typing import Any

from phantom_guard.cache.types import CacheEntry

# Type alias for cached values (JSON-serializable data)
CacheValue = dict[str, Any]


class MemoryCache:
    """
    IMPLEMENTS: S040
    INV: INV016, INV017
    OPTIMIZED: Add __slots__ + OrderedDict for O(1) LRU.

    Thread-safe LRU memory cache.

    - Max entries: 1000 (default)
    - Default TTL: 3600 seconds (1 hour)
    - Uses OrderedDict for O(1) LRU eviction
    - Synchronous (no I/O, pure memory operations)

    Attributes:
        max_size: Maximum number of entries before LRU eviction
        default_ttl: Default time-to-live in seconds
    """

    __slots__ = ("_cache", "_hits", "_lock", "_misses", "default_ttl", "max_size")

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
    ) -> None:
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of entries (default 1000)
            default_ttl: Default TTL in seconds (default 3600 = 1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> CacheValue | None:
        """
        IMPLEMENTS: S041
        INV: INV016 - Returns None if expired
        TEST: T040.01, T040.02, T040.04, T040.05
        OPTIMIZED: O(1) cache lookup with LRU update.

        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]

            # INV016: Check TTL before returning
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            result: CacheValue = entry.value
            return result

    def set(
        self,
        key: str,
        value: CacheValue,
        ttl: int | None = None,
    ) -> None:
        """
        IMPLEMENTS: S042
        INV: INV017 - Enforces size limit
        TEST: T040.03, T040.07, T040.08
        OPTIMIZED: O(1) cache set with automatic eviction.

        Store value in cache with LRU eviction.

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(UTC),
            ttl_seconds=ttl,
        )

        with self._lock:
            # Remove existing entry if present
            if key in self._cache:
                del self._cache[key]

            # INV017: Enforce size limit with LRU eviction
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)  # Remove oldest (LRU)

            self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """
        Remove entry from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if entry was found and deleted
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> int:
        """
        Clear all entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def __len__(self) -> int:
        """Return current cache size."""
        with self._lock:
            return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Check if key exists (does not update LRU order)."""
        with self._lock:
            if key not in self._cache:
                return False
            # Check expiration without updating LRU
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return False
            return True
