"""
IMPLEMENTS: S007, S008, S009
INVARIANTS: INV001, INV010, INV011, INV012
Risk scoring algorithm.

This module provides functions to calculate risk scores from signals
and determine recommendations based on configurable thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from phantom_guard.core.types import (
    PackageRisk,
    Recommendation,
    Signal,
)

# =============================================================================
# TYPE ALIASES
# =============================================================================

Registry = Literal["pypi", "npm", "crates"]

# =============================================================================
# CONSTANTS
# =============================================================================

# Thresholds for recommendation
# IMPLEMENTS: S008
# INV011: safe < suspicious (0.30 < 0.60)
THRESHOLD_SAFE: float = 0.30
THRESHOLD_SUSPICIOUS: float = 0.60
# Above SUSPICIOUS = HIGH_RISK

# Normalization constants for the scoring formula
# Formula: score = clamp((raw + OFFSET) / DIVISOR, 0.0, 1.0)
SCORE_OFFSET: float = 100.0
SCORE_DIVISOR: float = 260.0


# =============================================================================
# THRESHOLD CONFIG
# =============================================================================


@dataclass(frozen=True, slots=True)
class ThresholdConfig:
    """
    IMPLEMENTS: S008
    INVARIANT: INV011 - safe < suspicious

    Configurable thresholds for recommendations.
    """

    safe: float = THRESHOLD_SAFE
    suspicious: float = THRESHOLD_SUSPICIOUS

    def __post_init__(self) -> None:
        """Validate threshold ordering (INV011)."""
        if self.safe >= self.suspicious:
            raise ValueError(
                f"Thresholds must be ordered: safe ({self.safe}) < suspicious ({self.suspicious})"
            )
        if not (0.0 <= self.safe <= 1.0):
            raise ValueError(f"Safe threshold must be in [0.0, 1.0], got {self.safe}")
        if not (0.0 <= self.suspicious <= 1.0):
            raise ValueError(f"Suspicious threshold must be in [0.0, 1.0], got {self.suspicious}")


# Default threshold configuration
DEFAULT_THRESHOLDS = ThresholdConfig()


# =============================================================================
# RISK SCORING
# =============================================================================


def calculate_risk_score(signals: tuple[Signal, ...]) -> float:
    """
    IMPLEMENTS: S007
    INVARIANTS: INV001, INV010

    Calculate risk score from signals.

    Formula: clamp((raw + 100) / 260, 0.0, 1.0)

    This formula:
    - Maps no signals to ~0.38 (neutral)
    - Maps max positive (160) to 1.0
    - Maps max negative (-100) to 0.0
    - Allows negative signals to reduce risk

    INV010: Adding a positive-weight signal increases or maintains score.
            Adding a negative-weight signal decreases or maintains score.

    Args:
        signals: Tuple of detected signals

    Returns:
        Risk score in [0.0, 1.0] (INV001)
    """
    # Sum weighted signals (weights are in [-1.0, 1.0])
    # Empty signals = 0.0 raw score (neutral baseline)
    raw_score = sum(signal.weight * 100 for signal in signals)

    # Apply formula with clamping
    # INV001: Result always in [0.0, 1.0]
    score = (raw_score + SCORE_OFFSET) / SCORE_DIVISOR
    return max(0.0, min(1.0, score))


def calculate_raw_score(signals: tuple[Signal, ...]) -> float:
    """
    Calculate raw score before normalization.

    This is useful for debugging and testing.

    Args:
        signals: Tuple of detected signals

    Returns:
        Raw score (sum of weights * 100)
    """
    return sum(signal.weight * 100 for signal in signals)


# =============================================================================
# RECOMMENDATION
# =============================================================================


def determine_recommendation(
    score: float,
    exists: bool,
    thresholds: ThresholdConfig | None = None,
) -> Recommendation:
    """
    IMPLEMENTS: S008
    INVARIANT: INV011 - Monotonic with score

    Determine recommendation based on score and existence.

    Default thresholds:
    - SAFE: score <= 0.30
    - SUSPICIOUS: 0.30 < score <= 0.60
    - HIGH_RISK: score > 0.60

    Args:
        score: Risk score in [0.0, 1.0]
        exists: Whether package exists on registry
        thresholds: Optional custom thresholds

    Returns:
        Recommendation enum value
    """
    if not exists:
        return Recommendation.NOT_FOUND

    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if score <= thresholds.safe:
        return Recommendation.SAFE
    elif score <= thresholds.suspicious:
        return Recommendation.SUSPICIOUS
    else:
        return Recommendation.HIGH_RISK


# =============================================================================
# PACKAGE RISK BUILDER
# =============================================================================


def build_package_risk(
    name: str,
    registry: Registry,
    exists: bool,
    signals: tuple[Signal, ...],
    latency_ms: float = 0.0,
    thresholds: ThresholdConfig | None = None,
) -> PackageRisk:
    """
    IMPLEMENTS: S001, S007, S008
    INVARIANT: INV012 - Signal count matches PackageRisk.signals

    Build complete PackageRisk from components.

    Args:
        name: Package name
        registry: Package registry
        exists: Whether package exists
        signals: Detected signals
        latency_ms: Detection latency
        thresholds: Optional custom thresholds

    Returns:
        Complete PackageRisk object
    """
    score = calculate_risk_score(signals)
    recommendation = determine_recommendation(score, exists, thresholds)

    return PackageRisk(
        name=name,
        registry=registry,
        exists=exists,
        risk_score=score,
        signals=signals,
        recommendation=recommendation,
        latency_ms=latency_ms,
    )


# =============================================================================
# AGGREGATION
# =============================================================================


@dataclass(frozen=True, slots=True)
class AggregateResult:
    """
    IMPLEMENTS: S009
    INVARIANT: INV012 - preserves all inputs

    Aggregated results from multiple package validations.
    """

    packages: tuple[PackageRisk, ...]
    safe_count: int
    suspicious_count: int
    high_risk_count: int
    not_found_count: int
    overall_risk: Recommendation

    @property
    def total_count(self) -> int:
        """Total number of packages."""
        return len(self.packages)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total": self.total_count,
            "safe": self.safe_count,
            "suspicious": self.suspicious_count,
            "high_risk": self.high_risk_count,
            "not_found": self.not_found_count,
            "overall_risk": self.overall_risk.value,
        }


def aggregate_results(results: list[PackageRisk]) -> AggregateResult:
    """
    IMPLEMENTS: S009
    INVARIANT: INV012 - preserves all inputs

    Aggregate multiple package results into a summary.

    Args:
        results: List of PackageRisk objects

    Returns:
        AggregateResult with counts and overall risk
    """
    safe_count = 0
    suspicious_count = 0
    high_risk_count = 0
    not_found_count = 0

    for result in results:
        match result.recommendation:
            case Recommendation.SAFE:
                safe_count += 1
            case Recommendation.SUSPICIOUS:
                suspicious_count += 1
            case Recommendation.HIGH_RISK:
                high_risk_count += 1
            case Recommendation.NOT_FOUND:  # pragma: no branch
                not_found_count += 1

    # Overall risk is the highest individual risk
    if high_risk_count > 0:
        overall_risk = Recommendation.HIGH_RISK
    elif suspicious_count > 0:
        overall_risk = Recommendation.SUSPICIOUS
    elif not_found_count > 0:
        overall_risk = Recommendation.NOT_FOUND
    else:
        overall_risk = Recommendation.SAFE

    return AggregateResult(
        packages=tuple(results),
        safe_count=safe_count,
        suspicious_count=suspicious_count,
        high_risk_count=high_risk_count,
        not_found_count=not_found_count,
        overall_risk=overall_risk,
    )
