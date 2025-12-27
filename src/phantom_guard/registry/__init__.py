"""
Registry clients for package metadata retrieval.

IMPLEMENTS: S020-S049
"""

from __future__ import annotations

from phantom_guard.registry.cached import CachedRegistryClient
from phantom_guard.registry.crates import CratesClient
from phantom_guard.registry.exceptions import (
    RegistryError,
    RegistryParseError,
    RegistryRateLimitError,
    RegistryTimeoutError,
    RegistryUnavailableError,
)
from phantom_guard.registry.npm import NpmClient
from phantom_guard.registry.pypi import PyPIClient
from phantom_guard.registry.retry import RetryConfig, retry_async, with_retry

__all__ = [
    # Clients (alphabetical)
    "CachedRegistryClient",
    "CratesClient",
    "NpmClient",
    "PyPIClient",
    # Exceptions (alphabetical)
    "RegistryError",
    "RegistryParseError",
    "RegistryRateLimitError",
    "RegistryTimeoutError",
    "RegistryUnavailableError",
    # Retry utilities
    "RetryConfig",
    "retry_async",
    "with_retry",
]
