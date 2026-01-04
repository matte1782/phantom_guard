"""
IMPLEMENTS: S070
INVARIANTS: INV070, INV071, INV072
Ownership Transfer Detection for Phantom Guard.

Detects suspicious maintainer patterns:
- Single maintainer (reduced weight per P0-DESIGN-001)
- New maintainer accounts
- Low package count for maintainer (cross-reference)

INV070: Defaults to safe (None) on missing data
INV071: Single-maintainer alone is not HIGH_RISK (max 0.15)
INV072: Returns None when all data missing
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
class OwnershipSignal:
    """
    IMPLEMENTS: S070

    Signal indicating suspicious ownership patterns.
    """

    maintainer_count: int
    maintainer_packages: int | None
    maintainer_age_days: int | None
    confidence: float  # Max 0.15 per INV071
    reason: str


# =============================================================================
# CONSTANTS
# =============================================================================

# Maximum weight for ownership signal (reduced per P0-DESIGN-001)
OWNERSHIP_MAX_WEIGHT: float = 0.15

# Thresholds for suspicious patterns
MIN_MAINTAINER_PACKAGES: int = 5  # Established maintainer has >= 5 packages
MIN_MAINTAINER_AGE_DAYS: int = 90  # Established account is >= 90 days old
SAFE_MAINTAINER_COUNT: int = 2  # Multiple maintainers = safer


# =============================================================================
# DETECTION FUNCTION
# =============================================================================


def detect_ownership_transfer(
    package_name: str,
    metadata: dict[str, Any] | None,
    registry: str,
) -> OwnershipSignal | None:
    """
    IMPLEMENTS: S070
    INVARIANTS: INV070, INV071, INV072
    TESTS: T070.01-T070.05

    Detect suspicious ownership patterns for a package.

    Args:
        package_name: The package name to check.
        metadata: Package metadata with maintainer info.
        registry: The registry type (npm, pypi, crates).

    Returns:
        OwnershipSignal if suspicious pattern detected, None otherwise.
        Returns None on missing data (INV070, INV072).
    """
    try:
        # INV070, INV072: Missing data = safe
        if metadata is None:
            logger.debug("No metadata for %s, skipping ownership check", package_name)
            return None

        # Extract maintainer info
        maintainer_count = metadata.get("maintainer_count")
        maintainer_packages = metadata.get("maintainer_packages")
        maintainer_age_days = metadata.get("maintainer_age_days")

        # INV070: Missing maintainer_count = safe
        if maintainer_count is None:
            logger.debug("No maintainer count for %s, skipping ownership check", package_name)
            return None

        # Multiple maintainers = safer, no signal
        if maintainer_count >= SAFE_MAINTAINER_COUNT:
            return None

        # Calculate risk factors
        risk_score: float = 0.0
        risk_reasons: list[str] = []

        # Factor 1: Single maintainer (base risk)
        if maintainer_count == 1:
            risk_score += 0.05
            risk_reasons.append("single maintainer")

        # Factor 2: New maintainer account (if available)
        if maintainer_age_days is not None and maintainer_age_days < MIN_MAINTAINER_AGE_DAYS:
            risk_score += 0.05
            risk_reasons.append(f"new account ({maintainer_age_days} days)")

        # Factor 3: Low package count (cross-reference, if available)
        if maintainer_packages is not None and maintainer_packages < MIN_MAINTAINER_PACKAGES:
            risk_score += 0.05
            risk_reasons.append(f"only {maintainer_packages} packages")

        # INV071: Cap at maximum weight
        risk_score = min(risk_score, OWNERSHIP_MAX_WEIGHT)

        # No risk factors = no signal
        if risk_score == 0.0 or len(risk_reasons) == 0:
            return None

        reason = f"Ownership concerns: {', '.join(risk_reasons)}"

        return OwnershipSignal(
            maintainer_count=maintainer_count,
            maintainer_packages=maintainer_packages,
            maintainer_age_days=maintainer_age_days,
            confidence=risk_score,
            reason=reason,
        )

    except Exception as e:
        # INV070: Return None on any error
        logger.warning(
            "Ownership check failed for %s: %s",
            package_name,
            e,
        )
        return None
