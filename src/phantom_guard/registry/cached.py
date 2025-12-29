"""
IMPLEMENTS: S040-S049
INVARIANTS: INV003, INV016, INV017
Cached registry client wrapper.

Provides caching layer for registry clients to reduce API calls
and improve performance. Implements two-tier caching strategy.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from phantom_guard.cache import Cache
from phantom_guard.core.types import PackageMetadata

if TYPE_CHECKING:
    from types import TracebackType


@runtime_checkable
class RegistryClientProtocol(Protocol):
    """
    Protocol defining the interface for registry clients.

    All registry clients (PyPIClient, NpmClient, CratesClient) implement this.
    """

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """Fetch package metadata from registry."""
        ...  # pragma: no cover


def _metadata_to_dict(metadata: PackageMetadata) -> dict[str, Any]:
    """
    Convert PackageMetadata to dict for cache storage.

    Handles datetime serialization.
    """
    data = asdict(metadata)
    # Serialize datetime to ISO format
    if data.get("created_at") is not None:
        data["created_at"] = data["created_at"].isoformat()
    return data


def _dict_to_metadata(data: dict[str, Any]) -> PackageMetadata | None:
    """
    Convert cached dict back to PackageMetadata.

    Handles datetime deserialization. Returns None if data is invalid,
    which allows the caller to treat it as a cache miss.

    Args:
        data: Cached dictionary data

    Returns:
        PackageMetadata if valid, None if data is corrupted/invalid
    """
    try:
        # Deserialize datetime from ISO format
        if data.get("created_at") is not None:
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return PackageMetadata(
            name=data["name"],
            exists=data["exists"],
            registry=data.get("registry", "pypi"),
            created_at=data.get("created_at"),
            downloads_last_month=data.get("downloads_last_month"),
            repository_url=data.get("repository_url"),
            maintainer_count=data.get("maintainer_count"),
            release_count=data.get("release_count"),
            latest_version=data.get("latest_version"),
            description=data.get("description"),
        )
    except (KeyError, TypeError, ValueError):
        # Invalid data - return None to treat as cache miss
        return None


class CachedRegistryClient:
    """
    IMPLEMENTS: S040, S041, S042
    INV: INV003, INV016, INV017

    Caching wrapper for registry clients.

    Checks cache before making network requests. Stores results
    in both memory (fast) and SQLite (persistent) tiers.

    Usage:
        cache = Cache(sqlite_path="cache.db")
        client = PyPIClient()

        async with cache:
            async with CachedRegistryClient(client, cache, "pypi") as cached:
                metadata = await cached.get_package_metadata("flask")

    Attributes:
        client: Underlying registry client
        cache: Two-tier cache instance
        registry: Registry name for cache keys ("pypi", "npm", "crates")
    """

    def __init__(
        self,
        client: RegistryClientProtocol,
        cache: Cache,
        registry: str,
    ) -> None:
        """
        Initialize cached registry client.

        Args:
            client: Underlying registry client (PyPIClient, NpmClient, etc.)
            cache: Cache instance (should already be initialized via context manager)
            registry: Registry name for cache keys
        """
        self.client = client
        self.cache = cache
        self.registry = registry

    async def __aenter__(self) -> CachedRegistryClient:
        """Enter context - delegates to underlying client."""
        if hasattr(self.client, "__aenter__"):
            await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context - delegates to underlying client."""
        if hasattr(self.client, "__aexit__"):
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S041
        INV: INV003
        TEST: T040.11, T040.12

        Get package metadata with caching.

        Flow:
            1. Check cache (memory first, then SQLite)
            2. If hit, return cached data
            3. If miss, fetch from registry
            4. Store in cache
            5. Return data

        Args:
            name: Package name

        Returns:
            PackageMetadata from cache or registry

        Note:
            INV003 guarantees cached results identical to uncached.
        """
        # Check cache first
        cached_data = await self.cache.get(self.registry, name)
        if cached_data is not None:
            metadata = _dict_to_metadata(cached_data)
            if metadata is not None:
                return metadata
            # Invalid cache data - treat as miss and re-fetch

        # Cache miss - fetch from registry
        metadata = await self.client.get_package_metadata(name)

        # Store in cache
        await self.cache.set(
            self.registry,
            name,
            _metadata_to_dict(metadata),
        )

        return metadata

    async def get_package_metadata_uncached(self, name: str) -> PackageMetadata:
        """
        Get package metadata directly from registry, bypassing cache.

        Useful for testing INV003 (cached = uncached results).

        Args:
            name: Package name

        Returns:
            PackageMetadata from registry (not cached)
        """
        return await self.client.get_package_metadata(name)

    async def invalidate(self, name: str) -> bool:
        """
        Remove package from cache.

        Args:
            name: Package name

        Returns:
            True if entry was found and removed
        """
        return await self.cache.invalidate(self.registry, name)

    async def is_cached(self, name: str) -> bool:
        """
        Check if package is in cache.

        Args:
            name: Package name

        Returns:
            True if entry exists in cache (memory or SQLite)
        """
        cached = await self.cache.get(self.registry, name)
        return cached is not None
