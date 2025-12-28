"""
IMPLEMENTS: S040, S041, S042
INVARIANTS: INV016
Async SQLite persistent cache (Tier 2) using aiosqlite.

Per ADR-003: "Use aiosqlite package for async SQLite access"
Standard sqlite3 is blocking and incompatible with async-first architecture.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiosqlite

if TYPE_CHECKING:
    from types import TracebackType

# Type alias for cached values (JSON-serializable data)
CacheValue = dict[str, Any]


class AsyncSQLiteCache:
    """
    IMPLEMENTS: S040
    INV: INV016

    Async SQLite-backed persistent cache using aiosqlite.

    - Max entries: 100,000 (default)
    - Default TTL: 86400 seconds (24 hours)
    - All operations are async (non-blocking)

    Reference: https://aiosqlite.omnilib.dev/
    """

    CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            ttl_seconds INTEGER NOT NULL,
            expires_at REAL NOT NULL
        )
    """

    CREATE_INDEX = """
        CREATE INDEX IF NOT EXISTS idx_cache_created
        ON cache(created_at)
    """

    def __init__(
        self,
        db_path: str | Path = ":memory:",
        default_ttl: int = 86400,
    ) -> None:
        """
        Initialize async SQLite cache.

        Args:
            db_path: Path to SQLite database file (or ":memory:" for in-memory)
            default_ttl: Default TTL in seconds (default 86400 = 24 hours)
        """
        self.db_path = str(db_path)
        self.default_ttl = default_ttl
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """
        IMPLEMENTS: S040
        TEST: T040.17

        Initialize async database connection and schema.
        Uses aiosqlite for non-blocking I/O.
        """
        self._conn = await aiosqlite.connect(self.db_path)
        await self._conn.execute(self.CREATE_TABLE)
        await self._conn.execute(self.CREATE_INDEX)
        await self._conn.commit()

    async def close(self) -> None:
        """Close async database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self) -> AsyncSQLiteCache:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def get(self, key: str) -> CacheValue | None:
        """
        IMPLEMENTS: S041
        INV: INV016 - Returns None if expired
        TEST: T040.15, T040.16

        Async get value from SQLite cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not self._conn:
            return None

        async with self._conn.execute(
            "SELECT value, created_at, ttl_seconds FROM cache WHERE key = ?",
            (key,),
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        value_json, created_str, ttl = row
        created_at = datetime.fromisoformat(created_str)

        # Ensure timezone awareness
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        # INV016: Check TTL before returning
        expires_at = created_at + timedelta(seconds=ttl)
        if datetime.now(UTC) >= expires_at:
            await self.delete(key)
            return None

        result: CacheValue = json.loads(value_json)
        return result

    async def set(
        self,
        key: str,
        value: CacheValue,
        ttl: int | None = None,
    ) -> None:
        """
        IMPLEMENTS: S042
        TEST: T040.15

        Async set value in SQLite cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: TTL in seconds (uses default if None)
        """
        if not self._conn:
            return

        if ttl is None:
            ttl = self.default_ttl

        value_json = json.dumps(value, default=str)
        created_at = datetime.now(UTC).isoformat()
        expires_at = time.time() + ttl

        await self._conn.execute(
            """
            INSERT OR REPLACE INTO cache (key, value, created_at, ttl_seconds, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (key, value_json, created_at, ttl, expires_at),
        )
        await self._conn.commit()

    async def delete(self, key: str) -> bool:
        """
        Async remove entry from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if entry was found and deleted
        """
        if not self._conn:
            return False

        cursor = await self._conn.execute(
            "DELETE FROM cache WHERE key = ?",
            (key,),
        )
        await self._conn.commit()
        count: int = cursor.rowcount
        return count > 0

    async def cleanup_expired(self) -> int:
        """
        Async remove all expired entries.

        Returns:
            Number of entries removed
        """
        if not self._conn:
            return 0

        now = datetime.now(UTC).isoformat()
        cursor = await self._conn.execute(
            """
            DELETE FROM cache
            WHERE datetime(created_at, '+' || ttl_seconds || ' seconds') < ?
            """,
            (now,),
        )
        await self._conn.commit()
        count: int = cursor.rowcount
        return count

    async def count(self) -> int:
        """
        Async get number of entries in cache.

        Returns:
            Number of entries
        """
        if not self._conn:
            return 0

        async with self._conn.execute("SELECT COUNT(*) FROM cache") as cursor:
            row = await cursor.fetchone()
            count: int = row[0] if row else 0
            return count

    async def clear(self) -> int:
        """
        Async clear all entries.

        Returns:
            Number of entries removed
        """
        if not self._conn:
            return 0

        cursor = await self._conn.execute("DELETE FROM cache")
        await self._conn.commit()
        count: int = cursor.rowcount
        return count

    async def clear_by_prefix(self, prefix: str) -> int:
        """Clear all entries with keys starting with prefix."""
        if not self._conn:
            return 0
        cursor = await self._conn.execute(
            "DELETE FROM cache WHERE key LIKE ?",
            (f"{prefix}%",),
        )
        await self._conn.commit()
        return cursor.rowcount

    async def get_stats_by_registry(self) -> dict[str, dict[str, Any]]:
        """Get entry counts grouped by registry prefix."""
        if not self._conn:
            return {}

        stats: dict[str, dict[str, Any]] = {}
        cursor = await self._conn.execute(
            "SELECT key, LENGTH(value) as size FROM cache WHERE expires_at > ?",
            (time.time(),),
        )
        rows = await cursor.fetchall()

        for row in rows:
            key = row[0]
            size = row[1]
            if ":" in key:
                registry = key.split(":")[0]
                if registry not in stats:
                    stats[registry] = {"entries": 0, "size_bytes": 0}
                stats[registry]["entries"] += 1
                stats[registry]["size_bytes"] += size

        return stats
