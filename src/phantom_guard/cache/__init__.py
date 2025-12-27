"""
IMPLEMENTS: S040-S049
Two-tier cache system for package metadata.

Provides:
    - Cache: Unified two-tier cache (memory + SQLite)
    - MemoryCache: In-memory LRU cache (Tier 1)
    - AsyncSQLiteCache: Async SQLite persistent cache (Tier 2)
    - CacheEntry: Cache entry data structure
    - make_cache_key: Cache key normalization utility
"""

from __future__ import annotations

from phantom_guard.cache.cache import Cache
from phantom_guard.cache.memory import MemoryCache
from phantom_guard.cache.sqlite import AsyncSQLiteCache
from phantom_guard.cache.types import CacheEntry, make_cache_key

__all__ = [
    "AsyncSQLiteCache",
    "Cache",
    "CacheEntry",
    "MemoryCache",
    "make_cache_key",
]
