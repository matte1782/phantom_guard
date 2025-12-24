"""
IMPLEMENTS: S001
INVARIANTS: INV001, INV002, INV006, INV007, INV019, INV020
Core data structures for Phantom Guard.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

# =============================================================================
# CONSTANTS
# =============================================================================

# INV020: Maximum package name length (npm standard)
MAX_PACKAGE_NAME_LENGTH = 214

# Package name validation pattern (alphanumeric, hyphen, underscore)
# Must start with alphanumeric, no consecutive hyphens, no leading/trailing hyphens
PACKAGE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$|^[a-zA-Z0-9]$")


# =============================================================================
# EXCEPTIONS
# =============================================================================


class PhantomGuardError(Exception):
    """Base exception for all Phantom Guard errors."""


class InvalidPackageNameError(PhantomGuardError):
    """
    IMPLEMENTS: S001
    INV: INV019

    Raised when a package name fails validation.
    """

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason
        super().__init__(f"Invalid package name '{name}': {reason}")


class InvalidRegistryError(PhantomGuardError):
    """
    IMPLEMENTS: S001
    INV: INV021

    Raised when an unsupported registry is specified.
    """

    def __init__(self, registry: str) -> None:
        self.registry = registry
        super().__init__(f"Unknown registry '{registry}'. Supported: pypi, npm, crates")


# =============================================================================
# ENUMS
# =============================================================================


class Recommendation(Enum):
    """
    IMPLEMENTS: S001
    Package safety recommendation levels.
    """

    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    HIGH_RISK = "high_risk"
    NOT_FOUND = "not_found"


class SignalType(Enum):
    """
    IMPLEMENTS: S004
    Types of risk signals detected during package analysis.
    """

    # Existence signals
    NOT_FOUND = "not_found"
    RECENTLY_CREATED = "recently_created"
    LOW_DOWNLOADS = "low_downloads"
    NO_REPOSITORY = "no_repository"
    NO_MAINTAINER = "no_maintainer"
    FEW_RELEASES = "few_releases"
    SHORT_DESCRIPTION = "short_description"

    # Pattern signals
    HALLUCINATION_PATTERN = "hallucination_pattern"
    TYPOSQUAT = "typosquat"
    KNOWN_MALICIOUS = "known_malicious"

    # Positive signals (reduce risk)
    POPULAR_PACKAGE = "popular_package"
    VERIFIED_PUBLISHER = "verified_publisher"
    LONG_HISTORY = "long_history"


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass(frozen=True, slots=True)
class Signal:
    """
    IMPLEMENTS: S004
    INVARIANT: INV007 - Signals are immutable, weights bounded

    A detected risk signal with optional metadata.
    """

    type: SignalType
    weight: float  # Contribution to risk score, in [-1.0, 1.0]
    message: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate signal weight bounds."""
        # INV007: Validate weight bounds
        if not -1.0 <= self.weight <= 1.0:
            raise ValueError(f"Signal weight must be in [-1.0, 1.0], got {self.weight}")


@dataclass(frozen=True, slots=True)
class PackageRisk:
    """
    IMPLEMENTS: S001
    INVARIANTS: INV001, INV002, INV006

    Complete risk assessment for a package.
    """

    name: str
    registry: Literal["pypi", "npm", "crates"]
    exists: bool
    risk_score: float
    signals: tuple[Signal, ...]  # INV002: Never None, use empty tuple
    recommendation: Recommendation
    latency_ms: float = 0.0

    def __post_init__(self) -> None:
        """Validate invariants."""
        # INV001: Risk score must be in [0.0, 1.0]
        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError(f"risk_score must be in [0.0, 1.0], got {self.risk_score}")

        # INV002: Signals must not be None (runtime check for defensive programming)
        if self.signals is None:
            raise ValueError("signals cannot be None, use empty tuple")

        # INV019: Package name validation
        if not self.name or not self.name.strip():
            raise ValueError("Package name cannot be empty")


# =============================================================================
# TYPE ALIASES
# =============================================================================

Registry = Literal["pypi", "npm", "crates"]


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_package_name(name: str) -> str:
    """
    IMPLEMENTS: S001
    INVARIANTS: INV019, INV020

    Validate and normalize a package name.

    Args:
        name: The package name to validate

    Returns:
        Normalized (lowercase) package name

    Raises:
        InvalidPackageNameError: If name is invalid
    """
    # EC001, EC002: Empty or whitespace-only
    if not name or not name.strip():
        raise InvalidPackageNameError(name, "cannot be empty or whitespace-only")

    stripped = name.strip()

    # EC003, EC004: Length validation (INV020)
    if len(stripped) > MAX_PACKAGE_NAME_LENGTH:
        raise InvalidPackageNameError(
            name, f"exceeds maximum length of {MAX_PACKAGE_NAME_LENGTH} characters"
        )

    # EC005: Unicode validation (only ASCII alphanumeric, hyphen, underscore, dot)
    if not stripped.isascii():
        raise InvalidPackageNameError(name, "contains non-ASCII characters")

    # EC011, EC012: Leading/trailing hyphens
    if stripped.startswith("-") or stripped.startswith("_"):
        raise InvalidPackageNameError(name, "cannot start with hyphen or underscore")

    if stripped.endswith("-") or stripped.endswith("_"):
        raise InvalidPackageNameError(name, "cannot end with hyphen or underscore")

    # EC013: Double hyphens/underscores
    if "--" in stripped or "__" in stripped:
        raise InvalidPackageNameError(name, "cannot contain consecutive hyphens or underscores")

    # EC006: Special characters (only allow alphanumeric, hyphen, underscore, dot)
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$", stripped):
        raise InvalidPackageNameError(name, "contains invalid characters")

    # EC015: Case normalization
    return stripped.lower()


def validate_registry(registry: str) -> Registry:
    """
    IMPLEMENTS: S001
    INVARIANT: INV021

    Validate that the registry is supported.

    Args:
        registry: Registry name to validate

    Returns:
        Valid registry literal type

    Raises:
        InvalidRegistryError: If registry is not supported
    """
    valid_registries: set[str] = {"pypi", "npm", "crates"}
    normalized = registry.lower().strip()

    if normalized not in valid_registries:
        raise InvalidRegistryError(registry)

    # Type narrowing for Literal
    if normalized == "pypi":
        return "pypi"
    elif normalized == "npm":
        return "npm"
    else:
        return "crates"
