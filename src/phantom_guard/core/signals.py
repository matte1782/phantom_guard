"""
IMPLEMENTS: S004
INVARIANTS: INV007, INV008
Signal extraction from package metadata.

This module provides functions to analyze package metadata and extract
risk signals that indicate potential slopsquatting or other supply chain attacks.
"""

from __future__ import annotations

from phantom_guard.core.types import (
    PackageMetadata,
    Signal,
    SignalType,
)

# =============================================================================
# THRESHOLDS (configurable constants)
# =============================================================================

# Download thresholds
DOWNLOAD_THRESHOLD_LOW: int = 1000
DOWNLOAD_THRESHOLD_POPULAR: int = 1_000_000

# Age threshold (days)
AGE_THRESHOLD_NEW_DAYS: int = 30

# Release threshold
RELEASE_THRESHOLD_FEW: int = 3

# Description threshold (characters)
DESCRIPTION_THRESHOLD_SHORT: int = 10

# =============================================================================
# SIGNAL WEIGHTS
# =============================================================================

# Weights are in range [-1.0, 1.0]
# Positive weights increase risk, negative weights decrease risk
WEIGHT_NOT_FOUND: float = 0.9
WEIGHT_RECENTLY_CREATED: float = 0.4
WEIGHT_LOW_DOWNLOADS: float = 0.3
WEIGHT_NO_REPOSITORY: float = 0.25
WEIGHT_NO_MAINTAINER: float = 0.3
WEIGHT_FEW_RELEASES: float = 0.2
WEIGHT_SHORT_DESCRIPTION: float = 0.15
WEIGHT_POPULAR_PACKAGE: float = -0.5  # Reduces risk
WEIGHT_LONG_HISTORY: float = -0.2  # Reduces risk (age > 1 year)


# =============================================================================
# SIGNAL EXTRACTION
# =============================================================================


def extract_signals(metadata: PackageMetadata) -> tuple[Signal, ...]:
    """
    IMPLEMENTS: S004
    INVARIANTS: INV007 (signal weights bounded), INV008 (pure function)

    Extract risk signals from package metadata.

    This function analyzes the provided metadata and generates signals
    indicating potential risk factors. It is a pure function with no
    side effects - calling it multiple times with the same input will
    always produce the same output.

    Args:
        metadata: Package metadata from registry

    Returns:
        Tuple of detected signals (may be empty for safe packages)
    """
    signals: list[Signal] = []

    # Check existence first - if package doesn't exist, no other checks needed
    if not metadata.exists:
        signals.append(
            Signal(
                type=SignalType.NOT_FOUND,
                weight=WEIGHT_NOT_FOUND,
                message=f"Package '{metadata.name}' not found on {metadata.registry}",
            )
        )
        return tuple(signals)

    # Check age (recently created)
    if metadata.age_days is not None:
        if metadata.age_days < AGE_THRESHOLD_NEW_DAYS:
            signals.append(
                Signal(
                    type=SignalType.RECENTLY_CREATED,
                    weight=WEIGHT_RECENTLY_CREATED,
                    message=f"Recently created: {metadata.age_days} days old",
                    metadata={"age_days": metadata.age_days},
                )
            )
        elif metadata.age_days > 365:
            # Package has been around for more than a year - positive signal
            signals.append(
                Signal(
                    type=SignalType.LONG_HISTORY,
                    weight=WEIGHT_LONG_HISTORY,
                    message=f"Established package: {metadata.age_days} days old",
                    metadata={"age_days": metadata.age_days},
                )
            )

    # Check downloads
    if metadata.downloads_last_month is not None:
        if metadata.downloads_last_month < DOWNLOAD_THRESHOLD_LOW:
            signals.append(
                Signal(
                    type=SignalType.LOW_DOWNLOADS,
                    weight=WEIGHT_LOW_DOWNLOADS,
                    message=f"Low downloads: {metadata.downloads_last_month:,}/month",
                    metadata={"downloads": metadata.downloads_last_month},
                )
            )
        elif metadata.downloads_last_month >= DOWNLOAD_THRESHOLD_POPULAR:
            signals.append(
                Signal(
                    type=SignalType.POPULAR_PACKAGE,
                    weight=WEIGHT_POPULAR_PACKAGE,
                    message=f"Popular package: {metadata.downloads_last_month:,}/month",
                    metadata={"downloads": metadata.downloads_last_month},
                )
            )

    # Check repository
    if metadata.repository_url is None:
        signals.append(
            Signal(
                type=SignalType.NO_REPOSITORY,
                weight=WEIGHT_NO_REPOSITORY,
                message="No repository URL linked",
            )
        )

    # Check maintainers
    if metadata.maintainer_count is not None and metadata.maintainer_count == 0:
        signals.append(
            Signal(
                type=SignalType.NO_MAINTAINER,
                weight=WEIGHT_NO_MAINTAINER,
                message="No maintainers listed",
            )
        )

    # Check releases
    if metadata.release_count is not None and metadata.release_count < RELEASE_THRESHOLD_FEW:
        signals.append(
            Signal(
                type=SignalType.FEW_RELEASES,
                weight=WEIGHT_FEW_RELEASES,
                message=f"Few releases: {metadata.release_count}",
                metadata={"release_count": metadata.release_count},
            )
        )

    # Check description
    if (
        metadata.description is not None
        and len(metadata.description.strip()) < DESCRIPTION_THRESHOLD_SHORT
    ):
        signals.append(
            Signal(
                type=SignalType.SHORT_DESCRIPTION,
                weight=WEIGHT_SHORT_DESCRIPTION,
                message="Short or missing description",
                metadata={"description_length": len(metadata.description.strip())},
            )
        )

    return tuple(signals)


def merge_signals(*signal_groups: tuple[Signal, ...]) -> tuple[Signal, ...]:
    """
    IMPLEMENTS: S004
    Merge multiple signal groups, removing duplicates by type.

    When signals with the same type appear in multiple groups,
    only the first occurrence is kept (preserves priority ordering).

    Args:
        *signal_groups: Variable number of signal tuples to merge

    Returns:
        Merged tuple with unique signal types
    """
    seen_types: set[SignalType] = set()
    merged: list[Signal] = []

    for group in signal_groups:
        for signal in group:
            if signal.type not in seen_types:
                seen_types.add(signal.type)
                merged.append(signal)

    return tuple(merged)


def has_signal_type(signals: tuple[Signal, ...], signal_type: SignalType) -> bool:
    """
    Check if a signal tuple contains a specific signal type.

    Args:
        signals: Tuple of signals to search
        signal_type: The signal type to look for

    Returns:
        True if the signal type is present, False otherwise
    """
    return any(s.type == signal_type for s in signals)


def get_signal_by_type(signals: tuple[Signal, ...], signal_type: SignalType) -> Signal | None:
    """
    Get a signal by its type from a signal tuple.

    Args:
        signals: Tuple of signals to search
        signal_type: The signal type to find

    Returns:
        The matching signal, or None if not found
    """
    for signal in signals:
        if signal.type == signal_type:
            return signal
    return None


def calculate_total_weight(signals: tuple[Signal, ...]) -> float:
    """
    Calculate the sum of all signal weights.

    Note: This is a simple sum, not a normalized risk score.
    The risk scoring module will handle proper normalization.

    Args:
        signals: Tuple of signals

    Returns:
        Sum of all signal weights
    """
    return sum(s.weight for s in signals)
