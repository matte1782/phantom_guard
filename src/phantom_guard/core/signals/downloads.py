"""
IMPLEMENTS: S065
INVARIANTS: INV065, INV066, INV067
Download Inflation Detection for Phantom Guard.

Detects artificially inflated download counts by:
- Comparing downloads vs dependents (age-adjusted)
- Using libraries.io as fallback for dependent counts
- Graceful degradation on API failures

INV065: Uses age-adjusted threshold (not absolute)
INV066: Handles API failures gracefully (return None)
INV067: libraries.io fallback is optional (failure = skip)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class DownloadInflationSignal:
    """
    IMPLEMENTS: S065

    Signal indicating potential download inflation.
    """

    downloads: int
    dependents_count: int
    age_days: int
    downloads_per_day: float
    confidence: float  # Weight: 0.30 per spec
    reason: str


# =============================================================================
# CONSTANTS
# =============================================================================

# Weight for download inflation signal
DOWNLOAD_INFLATION_WEIGHT: float = 0.30

# Minimum age to consider for inflation detection (days)
MIN_AGE_DAYS: int = 30

# Minimum downloads per day to trigger check
MIN_DOWNLOADS_PER_DAY: float = 1000.0

# Ratio thresholds: downloads-to-dependents ratio
# If ratio > threshold, suspicious
# Higher threshold for newer packages
SUSPICIOUS_RATIO_BASE: float = 10000.0  # 10K downloads per dependent

# Minimum dependents to be considered legitimate
MIN_DEPENDENTS_LEGITIMATE: int = 10


# =============================================================================
# THRESHOLD CALCULATION
# =============================================================================


def calculate_age_adjusted_threshold(age_days: int) -> float:
    """
    IMPLEMENTS: S065
    INVARIANT: INV065 - Age-adjusted threshold

    Calculate age-adjusted threshold for download inflation.
    Newer packages get more lenient thresholds.

    Args:
        age_days: Package age in days.

    Returns:
        Downloads-per-dependent threshold.
    """
    if age_days < MIN_AGE_DAYS:
        # Too new to reliably detect inflation
        return float("inf")

    # Older packages should have more dependents for their download count
    # Formula: base * (365 / age_days)^0.5
    # This makes threshold more strict as package ages
    age_factor: float = min(age_days, 365) / 365.0
    threshold: float = SUSPICIOUS_RATIO_BASE / (age_factor**0.5)

    return threshold


# =============================================================================
# DETECTION FUNCTION
# =============================================================================


def detect_download_inflation(
    package_name: str,
    metadata: dict[str, Any],
    registry: str,
) -> DownloadInflationSignal | None:
    """
    IMPLEMENTS: S065
    INVARIANTS: INV065, INV066, INV067
    TESTS: T065.01-T065.06

    Detect download inflation for a package.

    Args:
        package_name: The package name to check.
        metadata: Package metadata with downloads, dependents_count, age_days.
        registry: The registry type (npm, pypi, crates).

    Returns:
        DownloadInflationSignal if inflation detected, None otherwise.
        Returns None on any error (INV066).
    """
    try:
        # Extract required data from metadata
        downloads = metadata.get("downloads", 0)
        dependents_count = metadata.get("dependents_count")
        age_days = metadata.get("age_days", 0)

        # INV066: Missing data = skip signal
        if downloads is None or downloads == 0:
            logger.debug("No download data for %s, skipping inflation check", package_name)
            return None

        if age_days < MIN_AGE_DAYS:
            logger.debug("Package %s too new (%d days), skipping", package_name, age_days)
            return None

        # Calculate downloads per day
        downloads_per_day = downloads / max(age_days, 1)

        # If downloads per day is low, not worth checking
        if downloads_per_day < MIN_DOWNLOADS_PER_DAY:
            return None

        # INV067: dependents_count might be None (libraries.io unavailable)
        if dependents_count is None:
            logger.debug("No dependents data for %s, skipping", package_name)
            return None

        # If package has enough dependents, it's legitimate
        if dependents_count >= MIN_DEPENDENTS_LEGITIMATE:
            # Check the ratio
            ratio = downloads / max(dependents_count, 1)
            threshold = calculate_age_adjusted_threshold(age_days)

            if ratio <= threshold:
                # Legitimate: downloads proportional to dependents
                return None

        # Suspicious: high downloads but low/no dependents
        reason = (
            f"High downloads ({downloads:,}) with only {dependents_count} dependents "
            f"({downloads_per_day:.0f}/day over {age_days} days)"
        )

        return DownloadInflationSignal(
            downloads=downloads,
            dependents_count=dependents_count,
            age_days=age_days,
            downloads_per_day=downloads_per_day,
            confidence=DOWNLOAD_INFLATION_WEIGHT,
            reason=reason,
        )

    except Exception as e:
        # INV066: Return None on any error, not exception
        logger.warning(
            "Download inflation check failed for %s: %s",
            package_name,
            e,
        )
        return None
