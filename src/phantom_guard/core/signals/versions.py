"""
IMPLEMENTS: S075
INVARIANTS: INV075, INV076, INV077
Version Spike Detection for Phantom Guard.

Detects suspicious version release patterns:
- 5+ versions in 24 hours
- 20+ versions in 7 days
- Excludes known CI/automated packages

INV075: Uses UTC timestamps consistently
INV076: Excludes CI packages from detection
INV077: Handles all registry timestamp formats
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class VersionSpikeSignal:
    """
    IMPLEMENTS: S075

    Signal indicating suspicious version release patterns.
    """

    versions_24h: int
    versions_7d: int
    confidence: float
    reason: str


# =============================================================================
# CONSTANTS
# =============================================================================

# Thresholds for version spike detection
VERSIONS_24H_THRESHOLD: int = 5
VERSIONS_7D_THRESHOLD: int = 20

# Weights for version spike signals
WEIGHT_24H_SPIKE: float = 0.45
WEIGHT_7D_SPIKE: float = 0.30

# Known CI/automated packages that release frequently (INV076)
CI_PACKAGES: frozenset[str] = frozenset(
    [
        # npm @types packages (DefinitelyTyped)
        "@types/node",
        "@types/react",
        "@types/express",
        "@types/lodash",
        "@types/jest",
        "@types/webpack",
        "@types/mocha",
        "@types/chai",
        # npm automated packages
        "typescript-daily",
        "canary",
        "nightly",
        # PyPI automation
        "black-pre-commit",
        "mypy-daily",
    ]
)

# CI package prefixes
CI_PREFIXES: tuple[str, ...] = (
    "@types/",  # DefinitelyTyped
    "-nightly",
    "-canary",
    "-alpha",
    "-beta",
    "-rc",
)


# =============================================================================
# TIMESTAMP PARSING
# =============================================================================


def parse_timestamp(timestamp_str: str) -> datetime | None:
    """
    IMPLEMENTS: S075
    INVARIANT: INV077 - Handle all registry formats

    Parse timestamp string to datetime (UTC).

    Args:
        timestamp_str: Timestamp string in various formats.

    Returns:
        datetime in UTC or None if parsing fails.
    """
    # Common formats across registries
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with microseconds
        "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 without microseconds
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 with timezone
        "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 with microseconds and tz
        "%Y-%m-%d %H:%M:%S",  # Simple format
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            # Ensure UTC
            dt = dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)
            return dt
        except ValueError:
            continue

    # Fallback: try fromisoformat (Python 3.11+)
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.astimezone(UTC)
    except ValueError:
        pass

    logger.warning("Could not parse timestamp: %s", timestamp_str)
    return None


def extract_version_timestamps(metadata: dict[str, Any], registry: str) -> list[datetime]:
    """
    IMPLEMENTS: S075
    INVARIANT: INV077 - Handle all registry formats

    Extract version timestamps from metadata based on registry type.

    Args:
        metadata: Package metadata.
        registry: Registry type (npm, pypi, crates).

    Returns:
        List of datetime objects (UTC) for each version.
    """
    timestamps: list[datetime] = []

    try:
        if registry == "npm":
            # npm: time object with version keys
            time_obj = metadata.get("time", {})
            for version, ts_str in time_obj.items():
                if version in ("created", "modified"):
                    continue
                if isinstance(ts_str, str):
                    dt = parse_timestamp(ts_str)
                    if dt:
                        timestamps.append(dt)

        elif registry == "pypi":
            # PyPI: releases object with version keys containing upload_time
            releases = metadata.get("releases", {})
            for _version, release_list in releases.items():
                if isinstance(release_list, list) and len(release_list) > 0:
                    first_release = release_list[0]
                    upload_time = first_release.get("upload_time")
                    if upload_time:
                        dt = parse_timestamp(upload_time)
                        if dt:
                            timestamps.append(dt)

        elif registry == "crates":
            # crates.io: versions array with created_at
            versions = metadata.get("versions", [])
            for version_obj in versions:
                created_at = version_obj.get("created_at")
                if created_at:
                    dt = parse_timestamp(created_at)
                    if dt:
                        timestamps.append(dt)

        else:
            # Generic: try version_timestamps field
            version_timestamps = metadata.get("version_timestamps", [])
            for ts_str in version_timestamps:
                if isinstance(ts_str, str):
                    dt = parse_timestamp(ts_str)
                    if dt:
                        timestamps.append(dt)

    except Exception as e:
        logger.warning("Error extracting timestamps: %s", e)

    return timestamps


# =============================================================================
# CI PACKAGE DETECTION
# =============================================================================


def is_ci_package(package_name: str, registry: str) -> bool:
    """
    IMPLEMENTS: S075
    INVARIANT: INV076 - Exclude CI packages

    Check if package is a known CI/automated package.

    Args:
        package_name: Package name.
        registry: Registry type.

    Returns:
        True if CI package (should be excluded).
    """
    # Direct match
    if package_name.lower() in CI_PACKAGES:
        return True

    # Prefix match
    name_lower = package_name.lower()
    for prefix in CI_PREFIXES:
        if name_lower.startswith(prefix) or name_lower.endswith(prefix):
            return True

    return False


# =============================================================================
# DETECTION FUNCTION
# =============================================================================


def detect_version_spike(
    package_name: str,
    metadata: dict[str, Any] | None,
    registry: str,
) -> VersionSpikeSignal | None:
    """
    IMPLEMENTS: S075
    INVARIANTS: INV075, INV076, INV077
    TESTS: T075.01-T075.07

    Detect suspicious version release patterns.

    Args:
        package_name: The package name to check.
        metadata: Package metadata with version info.
        registry: The registry type (npm, pypi, crates).

    Returns:
        VersionSpikeSignal if suspicious pattern detected, None otherwise.
    """
    try:
        # INV076: Exclude CI packages
        if is_ci_package(package_name, registry):
            logger.debug("Package %s is CI package, skipping version check", package_name)
            return None

        if metadata is None:
            return None

        # Extract version timestamps
        timestamps = extract_version_timestamps(metadata, registry)

        if len(timestamps) < 2:
            return None

        # INV075: Use UTC consistently
        now = datetime.now(UTC)
        cutoff_24h = now - timedelta(hours=24)
        cutoff_7d = now - timedelta(days=7)

        # Count versions in time windows
        versions_24h = sum(1 for ts in timestamps if ts >= cutoff_24h)
        versions_7d = sum(1 for ts in timestamps if ts >= cutoff_7d)

        # Check thresholds
        if versions_24h >= VERSIONS_24H_THRESHOLD:
            reason = f"{versions_24h} versions in 24h (threshold: {VERSIONS_24H_THRESHOLD})"
            return VersionSpikeSignal(
                versions_24h=versions_24h,
                versions_7d=versions_7d,
                confidence=WEIGHT_24H_SPIKE,
                reason=reason,
            )

        if versions_7d >= VERSIONS_7D_THRESHOLD:
            reason = f"{versions_7d} versions in 7d (threshold: {VERSIONS_7D_THRESHOLD})"
            return VersionSpikeSignal(
                versions_24h=versions_24h,
                versions_7d=versions_7d,
                confidence=WEIGHT_7D_SPIKE,
                reason=reason,
            )

        return None

    except Exception as e:
        logger.warning("Version spike check failed for %s: %s", package_name, e)
        return None
