"""
Phantom Guard: Detect AI-hallucinated package attacks.

Protect your software supply chain from slopsquatting attacks
where AI coding assistants hallucinate package names that
attackers register with malware.

Example:
    >>> import asyncio
    >>> from phantom_guard import Detector, Registry
    >>>
    >>> async def main():
    ...     detector = Detector()
    ...     result = await detector.check_package("flask")
    ...     print(f"{result.risk_level}: {result.recommendation}")
    ...
    >>> asyncio.run(main())
    RiskLevel.SAFE: Package appears legitimate.
"""

from __future__ import annotations

__version__ = "0.0.1"
__author__ = "Phantom Guard Team"
__license__ = "MIT"

# Core types
# Detection engine
from phantom_guard.core.detector import Detector
from phantom_guard.core.patterns import PatternMatcher
from phantom_guard.core.scorer import RiskScorer
from phantom_guard.core.types import (
    PackageMetadata,
    PackageRisk,
    Registry,
    RiskLevel,
    RiskSignal,
    SignalType,
    ValidationResult,
)

# Registry clients
from phantom_guard.registry.base import RegistryClient, RegistryError
from phantom_guard.registry.crates import CratesClient
from phantom_guard.registry.npm import NpmClient
from phantom_guard.registry.pypi import PyPIClient

__all__ = [
    # Registry clients
    "CratesClient",
    # Detection engine
    "Detector",
    "NpmClient",
    # Core types
    "PackageMetadata",
    "PackageRisk",
    "PatternMatcher",
    "PyPIClient",
    "Registry",
    "RegistryClient",
    "RegistryError",
    "RiskLevel",
    "RiskScorer",
    "RiskSignal",
    "SignalType",
    "ValidationResult",
    # Version info
    "__version__",
]
