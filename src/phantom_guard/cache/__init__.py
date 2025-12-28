"""
IMPLEMENTS: S040-S049
Two-tier cache system for package metadata.

Provides:
    - Cache: Unified two-tier cache (memory + SQLite)
    - MemoryCache: In-memory LRU cache (Tier 1)
    - AsyncSQLiteCache: Async SQLite persistent cache (Tier 2)
    - CacheEntry: Cache entry data structure
    - make_cache_key: Cache key normalization utility
    - get_default_cache_path: Platform-specific default cache directory
"""

from __future__ import annotations

from pathlib import Path

import platformdirs

from phantom_guard.cache.cache import Cache
from phantom_guard.cache.memory import MemoryCache
from phantom_guard.cache.sqlite import AsyncSQLiteCache
from phantom_guard.cache.types import CacheEntry, make_cache_key


def get_default_cache_path() -> Path:
    """
    IMPLEMENTS: S016

    Get the default cache file path using platformdirs.

    Returns:
        - Linux: ~/.cache/phantom-guard/cache.db
        - macOS: ~/Library/Caches/phantom-guard/cache.db
        - Windows: C:/Users/<user>/AppData/Local/phantom-guard/Cache/cache.db
    """
    cache_dir = Path(platformdirs.user_cache_dir("phantom-guard"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "cache.db"


__all__ = [
    "AsyncSQLiteCache",
    "Cache",
    "CacheEntry",
    "MemoryCache",
    "get_default_cache_path",
    "make_cache_key",
]
