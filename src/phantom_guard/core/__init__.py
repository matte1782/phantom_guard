"""
Core detection engine for Phantom Guard.

IMPLEMENTS: S001-S009
"""

from __future__ import annotations

from phantom_guard.core.types import (
    InvalidPackageNameError,
    InvalidRegistryError,
    PackageRisk,
    PhantomGuardError,
    Recommendation,
    Registry,
    Signal,
    SignalType,
    validate_package_name,
    validate_registry,
)

__all__ = [
    "InvalidPackageNameError",
    "InvalidRegistryError",
    "PackageRisk",
    "PhantomGuardError",
    "Recommendation",
    "Registry",
    "Signal",
    "SignalType",
    "validate_package_name",
    "validate_registry",
]
