"""
Registry clients for package metadata retrieval.

IMPLEMENTS: S020-S039
"""

from __future__ import annotations

from phantom_guard.registry.exceptions import (
    RegistryError,
    RegistryParseError,
    RegistryRateLimitError,
    RegistryTimeoutError,
    RegistryUnavailableError,
)
from phantom_guard.registry.pypi import PyPIClient

__all__ = [
    # Clients
    "PyPIClient",
    # Exceptions (alphabetical)
    "RegistryError",
    "RegistryParseError",
    "RegistryRateLimitError",
    "RegistryTimeoutError",
    "RegistryUnavailableError",
]
