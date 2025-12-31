"""
Phantom Guard - Detect AI-Hallucinated Package Attacks

IMPLEMENTS: S001-S019
"""

from __future__ import annotations

from phantom_guard.core import (
    PackageRisk,
    Recommendation,
    Registry,
    Signal,
    SignalType,
    detect_typosquat,
    normalize_package_name,
    validate_batch,
    validate_batch_sync,
    validate_package,
    validate_package_sync,
)

__version__ = "0.1.2"
__all__ = [
    "PackageRisk",
    "Recommendation",
    "Registry",
    "Signal",
    "SignalType",
    "__version__",
    "detect_typosquat",
    "normalize_package_name",
    "validate_batch",
    "validate_batch_sync",
    "validate_package",
    "validate_package_sync",
]
