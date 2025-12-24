# Week 2 - Day 4: Two-Tier Cache

> **Date**: Day 4 (Week 2)
> **Focus**: Memory LRU + SQLite persistent cache (async)
> **Tasks**: W2.4
> **Hours**: 6-8 hours
> **SPEC_IDs**: S040-S049
> **INV_IDs**: INV016, INV017
> **TEST_IDs**: T040.01-T040.17

---

## Architecture Overview

```
+---------------------------------------------------------------------+
|                     CACHE SYSTEM (S040)                             |
+---------------------------------------------------------------------+
|                                                                     |
|   +-------------------+    miss    +---------------------------+    |
|   |   Memory LRU      | ---------> |   SQLite Store (async)    |    |
|   |   (Tier 1)        |            |      (Tier 2)             |    |
|   |                   |  <-------- |                           |    |
|   | - Max 1000        |   promote  | - Max 100,000             |    |
|   | - TTL: 1 hour     |            | - TTL: 24 hours           |    |
|   | - ~200KB          |            | - ~10MB                   |    |
|   | - Sync (fast)     |            | - Async (aiosqlite)       |    |
|   +-------------------+            +---------------------------+    |
|                                                                     |
+---------------------------------------------------------------------+
```

**CRITICAL**: Per ADR-003 in ARCHITECTURE.md:
> "Standard sqlite3 is blocking and incompatible with async-first architecture.
> **Solution**: Use `aiosqlite` package for async SQLite access."

---

## Morning Session (4h)

### Objective
Implement two-tier caching with memory LRU (sync) and SQLite (async via aiosqlite).

### Step 1: Enable Cache Tests (15min)

```python
# tests/unit/test_cache.py
# Remove @pytest.mark.skip from:
# - test_cache_hit_returns_cached_value (T040.01)
# - test_cache_miss_returns_none (T040.02)
# - test_cache_set_stores_value (T040.03)
# - test_cache_ttl_honored (T040.04)
# - test_cache_ttl_not_expired (T040.05)
```

### Step 2: Implement Cache Entry Type (30min)

```python
# src/phantom_guard/cache/types.py
"""
IMPLEMENTS: S040
Cache data structures.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from typing import Any


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """
    IMPLEMENTS: S040
    INV: INV016

    Cache entry with TTL support.
    """
    key: str
    value: Any
    created_at: datetime
    ttl_seconds: int

    @property
    def expires_at(self) -> datetime:
        """Calculate expiration time."""
        return self.created_at + timedelta(seconds=self.ttl_seconds)

    def is_expired(self, now: datetime | None = None) -> bool:
        """
        INV: INV016 - TTL honored, stale data not returned.
        """
        if now is None:
            now = datetime.now(UTC)
        return now >= self.expires_at


def make_cache_key(registry: str, package_name: str) -> str:
    """
    IMPLEMENTS: S040
    TEST: T040.09, T040.10

    Create normalized cache key.
    """
    # Normalize: lowercase, replace _ with -
    normalized_name = package_name.lower().replace("_", "-")
    return f"{registry}:{normalized_name}"
```

### Step 3: Implement Memory LRU Cache (1h)

Memory cache remains synchronous (it's in-memory, no I/O blocking):

```python
# src/phantom_guard/cache/memory.py
"""
IMPLEMENTS: S040, S041, S042
INVARIANTS: INV016, INV017
In-memory LRU cache (Tier 1).
"""

from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, UTC
from threading import Lock
from typing import Any

from phantom_guard.cache.types import CacheEntry


class MemoryCache:
    """
    IMPLEMENTS: S040
    INV: INV016, INV017

    Thread-safe LRU memory cache.

    - Max entries: 1000 (default)
    - Default TTL: 3600 seconds (1 hour)
    - Uses OrderedDict for O(1) LRU eviction
    - Synchronous (no I/O, pure memory operations)
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        """
        IMPLEMENTS: S041
        INV: INV016 - Returns None if expired
        TEST: T040.01, T040.02, T040.04, T040.05
        """
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # INV016: Check TTL before returning
            if entry.is_expired():
                del self._cache[key]
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """
        IMPLEMENTS: S042
        INV: INV017 - Enforces size limit
        TEST: T040.03, T040.07, T040.08
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
            if key in self._cache:
                del self._cache[key]

            # INV017: Enforce size limit with LRU eviction
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)

            self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """Remove entry from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> int:
        """Clear all entries. Returns count removed."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def __len__(self) -> int:
        """Return current cache size."""
        return len(self._cache)
```

### Step 4: Run Memory Cache Tests (15min)

```bash
pytest tests/unit/test_cache.py::TestCacheBasics -v --tb=short
# Expected: T040.01-T040.06 pass
```

### Step 5: Implement ASYNC SQLite Cache with aiosqlite (1.5h)

**CRITICAL**: This uses `aiosqlite` per ADR-003 architectural decision.

```python
# src/phantom_guard/cache/sqlite.py
"""
IMPLEMENTS: S040, S041, S042
INVARIANTS: INV016
Async SQLite persistent cache (Tier 2) using aiosqlite.

Per ADR-003: "Use aiosqlite package for async SQLite access"
"""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import aiosqlite


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
            ttl_seconds INTEGER NOT NULL
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
    ):
        self.db_path = str(db_path)
        self.default_ttl = default_ttl
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """
        IMPLEMENTS: S040
        TEST: T040.17

        Initialize async database connection and schema.
        Uses aiosqlite context manager internally.
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

    async def __aenter__(self) -> "AsyncSQLiteCache":
        await self.connect()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def get(self, key: str) -> Any | None:
        """
        IMPLEMENTS: S041
        INV: INV016 - Returns None if expired
        TEST: T040.15, T040.16

        Async get value from SQLite cache.
        """
        if not self._conn:
            return None

        async with self._conn.execute(
            "SELECT value, created_at, ttl_seconds FROM cache WHERE key = ?",
            (key,)
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        value_json, created_str, ttl = row
        created_at = datetime.fromisoformat(created_str)

        # INV016: Check TTL before returning
        expires_at = created_at.replace(tzinfo=UTC) + \
            __import__('datetime').timedelta(seconds=ttl)
        if datetime.now(UTC) >= expires_at:
            await self.delete(key)
            return None

        return json.loads(value_json)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """
        IMPLEMENTS: S042
        TEST: T040.15

        Async set value in SQLite cache.
        """
        if not self._conn:
            return

        if ttl is None:
            ttl = self.default_ttl

        value_json = json.dumps(value)
        created_at = datetime.now(UTC).isoformat()

        await self._conn.execute(
            """
            INSERT OR REPLACE INTO cache (key, value, created_at, ttl_seconds)
            VALUES (?, ?, ?, ?)
            """,
            (key, value_json, created_at, ttl)
        )
        await self._conn.commit()

    async def delete(self, key: str) -> bool:
        """Async remove entry from cache."""
        if not self._conn:
            return False

        cursor = await self._conn.execute(
            "DELETE FROM cache WHERE key = ?",
            (key,)
        )
        await self._conn.commit()
        return cursor.rowcount > 0

    async def cleanup_expired(self) -> int:
        """Async remove all expired entries. Returns count removed."""
        if not self._conn:
            return 0

        now = datetime.now(UTC).isoformat()
        cursor = await self._conn.execute(
            """
            DELETE FROM cache
            WHERE datetime(created_at, '+' || ttl_seconds || ' seconds') < ?
            """,
            (now,)
        )
        await self._conn.commit()
        return cursor.rowcount

    async def count(self) -> int:
        """Async get number of entries in cache."""
        if not self._conn:
            return 0

        async with self._conn.execute("SELECT COUNT(*) FROM cache") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
```

---

## Afternoon Session (2h)

### Objective
Implement unified Cache class combining sync memory + async SQLite.

### Step 6: Implement Unified Async Cache (1h)

```python
# src/phantom_guard/cache/cache.py
"""
IMPLEMENTS: S040-S049
INVARIANTS: INV016, INV017
Two-tier cache system: sync memory + async SQLite.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from phantom_guard.cache.memory import MemoryCache
from phantom_guard.cache.sqlite import AsyncSQLiteCache
from phantom_guard.cache.types import make_cache_key


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
    """

    def __init__(
        self,
        memory_max_size: int = 1000,
        memory_ttl: int = 3600,
        sqlite_path: str | Path | None = None,
        sqlite_ttl: int = 86400,
        sqlite_enabled: bool = True,
    ):
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

    async def __aenter__(self) -> "Cache":
        """Async context manager entry - connects SQLite."""
        if self.sqlite:
            await self.sqlite.connect()
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit - closes SQLite."""
        if self.sqlite:
            await self.sqlite.close()

    async def get(self, registry: str, package_name: str) -> Any | None:
        """
        IMPLEMENTS: S041
        TEST: T040.01, T040.02, T040.11, T040.12

        Get cached metadata.
        Checks memory first (sync), then SQLite (async).
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
        value: Any,
        memory_ttl: int | None = None,
        sqlite_ttl: int | None = None,
    ) -> None:
        """
        IMPLEMENTS: S042
        TEST: T040.03

        Cache metadata in both tiers.
        Memory write is sync, SQLite write is async.
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
        """
        key = make_cache_key(registry, package_name)

        memory_deleted = self.memory.delete(key)
        sqlite_deleted = await self.sqlite.delete(key) if self.sqlite else False

        return memory_deleted or sqlite_deleted

    async def clear_all(self) -> tuple[int, int]:
        """
        Clear both cache tiers.
        Returns (memory_count, sqlite_count) deleted.
        """
        memory_count = self.memory.clear()
        sqlite_count = 0
        if self.sqlite:
            # Delete all from SQLite
            sqlite_count = await self.sqlite.cleanup_expired()
        return memory_count, sqlite_count
```

### Step 7: Update Cache __init__.py (15min)

```python
# src/phantom_guard/cache/__init__.py
"""
IMPLEMENTS: S040-S049
Two-tier cache system.
"""

from phantom_guard.cache.cache import Cache
from phantom_guard.cache.memory import MemoryCache
from phantom_guard.cache.sqlite import AsyncSQLiteCache
from phantom_guard.cache.types import CacheEntry, make_cache_key

__all__ = [
    "Cache",
    "MemoryCache",
    "AsyncSQLiteCache",
    "CacheEntry",
    "make_cache_key",
]
```

### Step 8: Write Async Cache Tests (30min)

```python
# tests/unit/test_cache.py - Update for async

import pytest
from phantom_guard.cache.cache import Cache
from phantom_guard.cache.sqlite import AsyncSQLiteCache


class TestAsyncSQLiteCache:
    """Tests for async SQLite cache.

    TEST: T040.15-T040.17
    """

    @pytest.mark.asyncio
    async def test_sqlite_async_connect(self, tmp_path):
        """
        TEST_ID: T040.17
        SPEC: S040

        SQLite connects and creates schema asynchronously.
        """
        db_path = tmp_path / "test.db"

        async with AsyncSQLiteCache(db_path) as cache:
            # Should be connected
            assert cache._conn is not None

            # Schema should exist
            count = await cache.count()
            assert count == 0

    @pytest.mark.asyncio
    async def test_sqlite_async_set_get(self, tmp_path):
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
    async def test_sqlite_async_ttl_honored(self, tmp_path):
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


class TestTwoTierCache:
    """Tests for unified two-tier cache."""

    @pytest.mark.asyncio
    async def test_memory_hit_skips_sqlite(self, tmp_path):
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
            # Set only in memory
            cache.memory.set("pypi:flask", {"name": "flask"})

            # Get should hit memory
            value = await cache.get("pypi", "flask")
            assert value is not None
            assert value["name"] == "flask"

    @pytest.mark.asyncio
    async def test_sqlite_miss_promotes_to_memory(self, tmp_path):
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
            await cache.sqlite.set("pypi:requests", {"name": "requests"})

            # Memory should be empty
            assert cache.memory.get("pypi:requests") is None

            # Get should hit SQLite and promote
            value = await cache.get("pypi", "requests")
            assert value is not None

            # Now memory should have it
            assert cache.memory.get("pypi:requests") is not None
```

### Step 9: Run All Cache Tests (30min)

```bash
pytest tests/unit/test_cache.py -v --tb=short
# Expected: 17/17 tests pass
```

---

## Dependencies Update

Ensure `aiosqlite` is in pyproject.toml:

```toml
# pyproject.toml
dependencies = [
    "httpx>=0.25.0",
    "aiosqlite>=0.19.0",  # REQUIRED per ADR-003
    # ...
]
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/cache/` - No lint errors
- [ ] `mypy src/phantom_guard/cache/ --strict` - No type errors
- [ ] All T040.* tests passing
- [ ] INV016 verified (TTL honored in both tiers)
- [ ] INV017 verified (size limit enforced in memory)

### Architecture Compliance
- [ ] SQLite uses `aiosqlite` (ADR-003 compliance)
- [ ] All SQLite operations are `async`
- [ ] Memory cache remains sync (no I/O)
- [ ] Unified Cache uses `async with` context manager

### Git Commit

```bash
git add src/phantom_guard/cache/
git commit -m "feat(cache): Implement two-tier async cache with aiosqlite

IMPLEMENTS: S040-S049
INVARIANTS: INV016, INV017
ADR: ADR-003 (async SQLite)

- Add MemoryCache with thread-safe LRU eviction (sync)
- Add AsyncSQLiteCache using aiosqlite (non-blocking I/O)
- Add unified Cache with async context manager
- Enforce TTL in both tiers (INV016)
- Enforce size limits with eviction (INV017)
- All SQLite operations are async per ADR-003

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Day 4 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W2.4 | |
| Tests Passing | 17 (T040.*) | |
| INV016 Verified | Yes | |
| INV017 Verified | Yes | |
| ADR-003 Compliant | Yes (aiosqlite) | |

---

## Tomorrow Preview

**Day 5 Focus**: Error handling + retries (W2.5)
- Exponential backoff
- Retry logic with async/await
- Integration testing all components

---

## Sources

- [aiosqlite Official Documentation](https://aiosqlite.omnilib.dev/)
- [aiosqlite GitHub](https://github.com/omnilib/aiosqlite)
- [aiosqlite on PyPI](https://pypi.org/project/aiosqlite/)
