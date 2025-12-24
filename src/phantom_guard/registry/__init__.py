"""
Registry clients for package metadata retrieval.

IMPLEMENTS: S020-S039
"""

from __future__ import annotations

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

__all__ = [
    # Clients (alphabetical)
    "CratesClient",
    "NpmClient",
    "PyPIClient",
    # Exceptions (alphabetical)
    "RegistryError",
    "RegistryParseError",
    "RegistryRateLimitError",
    "RegistryTimeoutError",
    "RegistryUnavailableError",
]
