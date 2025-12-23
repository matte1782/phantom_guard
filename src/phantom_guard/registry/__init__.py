"""Registry client implementations."""

from phantom_guard.registry.base import RegistryClient, RegistryError
from phantom_guard.registry.crates import CratesClient
from phantom_guard.registry.npm import NpmClient
from phantom_guard.registry.pypi import PyPIClient

__all__ = [
    "CratesClient",
    "NpmClient",
    "PyPIClient",
    "RegistryClient",
    "RegistryError",
]
