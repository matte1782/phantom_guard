"""
IMPLEMENTS: S040
INVARIANTS: INV016
Cache data structures and utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

# Type alias for cached values (JSON-serializable data)
# We use Any because cache stores arbitrary PackageMetadata dicts
CacheValue = dict[str, Any]


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """
    IMPLEMENTS: S040
    INV: INV016

    Cache entry with TTL support.

    Attributes:
        key: Cache key (registry:package_name format)
        value: Cached data (typically PackageMetadata as dict)
        created_at: When the entry was created
        ttl_seconds: Time-to-live in seconds
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

        Args:
            now: Current time (defaults to UTC now)

        Returns:
            True if entry has expired
        """
        if now is None:
            now = datetime.now(UTC)
        # Ensure created_at is timezone-aware
        created = self.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        expires = created + timedelta(seconds=self.ttl_seconds)
        return now >= expires


def make_cache_key(registry: str, package_name: str) -> str:
    """
    IMPLEMENTS: S040
    TEST: T040.09, T040.10

    Create normalized cache key.

    Format: "{registry}:{normalized_package_name}"

    Normalization:
        - Lowercase registry and package name
        - Replace underscores with hyphens (npm convention)

    Args:
        registry: Registry name (pypi, npm, crates)
        package_name: Package name to cache

    Returns:
        Normalized cache key

    Examples:
        >>> make_cache_key("pypi", "Flask")
        "pypi:flask"
        >>> make_cache_key("npm", "@types/node")
        "npm:@types/node"
        >>> make_cache_key("pypi", "my_package")
        "pypi:my-package"
    """
    normalized_name = package_name.lower().replace("_", "-")
    return f"{registry.lower()}:{normalized_name}"
