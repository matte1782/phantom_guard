"""Core data types for Phantom Guard.

This module defines all data structures used throughout the system.
All types are immutable (frozen dataclasses) for security and hashability.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Registry(str, Enum):
    """Supported package registries."""

    PYPI = "pypi"
    NPM = "npm"
    CRATES = "crates"


class RiskLevel(str, Enum):
    """Risk classification levels.

    - SAFE: Score >= 60, package appears legitimate
    - SUSPICIOUS: Score 30-59, manual review recommended
    - HIGH_RISK: Score < 30, likely malicious or abandoned
    - NOT_FOUND: Package doesn't exist in registry
    """

    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    HIGH_RISK = "high_risk"
    NOT_FOUND = "not_found"


class SignalType(str, Enum):
    """Types of risk signals detected during analysis."""

    NOT_FOUND = "not_found"
    FEW_RELEASES = "few_releases"
    NO_REPOSITORY = "no_repository"
    NO_AUTHOR = "no_author"
    NO_DESCRIPTION = "no_description"
    LOW_DOWNLOADS = "low_downloads"
    NEW_PACKAGE = "new_package"
    HALLUCINATION_PATTERN = "hallucination_pattern"


@dataclass(frozen=True)
class PackageMetadata:
    """Metadata fetched from a package registry.

    Attributes:
        name: Package name as registered.
        registry: Which registry this metadata came from.
        exists: Whether the package exists in the registry.
        release_count: Number of published versions.
        has_repository: Whether a source repository URL is provided.
        has_author: Whether author information is available.
        has_description: Whether the package has a meaningful description.
        downloads_last_month: Download count in last 30 days (if available).
        created_at: When the package was first published (if available).
    """

    name: str
    registry: Registry
    exists: bool
    release_count: int = 0
    has_repository: bool = False
    has_author: bool = False
    has_description: bool = False
    downloads_last_month: int | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class RiskSignal:
    """Individual risk signal detected during analysis.

    Attributes:
        signal_type: Category of the signal.
        weight: Score impact (negative values reduce score).
        details: Human-readable explanation.
    """

    signal_type: SignalType
    weight: int
    details: str


@dataclass(frozen=True)
class PackageRisk:
    """Complete risk assessment for a package.

    Attributes:
        package_name: Name of the analyzed package.
        registry: Which registry was checked.
        risk_level: Overall risk classification.
        risk_score: Numeric score from 0-100 (higher is safer).
        signals: All detected risk signals.
        recommendation: Human-readable action recommendation.
        metadata: Raw metadata from registry (if available).
    """

    package_name: str
    registry: Registry
    risk_level: RiskLevel
    risk_score: int
    signals: tuple[RiskSignal, ...]
    recommendation: str
    metadata: PackageMetadata | None = None


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating multiple packages.

    Attributes:
        safe: Package names that passed validation.
        suspicious: Packages flagged for manual review.
        blocked: Packages that should not be installed.
        errors: Packages that couldn't be checked (with error messages).
        validation_time_ms: Total time taken in milliseconds.
    """

    safe: tuple[str, ...]
    suspicious: tuple[PackageRisk, ...]
    blocked: tuple[PackageRisk, ...]
    errors: tuple[str, ...]
    validation_time_ms: int
