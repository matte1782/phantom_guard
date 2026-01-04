"""
IMPLEMENTS: S004, S060, S065, S070, S075
Phantom Guard Detection Signals.

This package provides detection signals for supply chain attacks:
- Legacy signals (S004): extract_signals, merge_signals
- Namespace squatting (S060)
- Download inflation (S065)
- Ownership transfer (S070)
- Version spike (S075)
"""

from __future__ import annotations

# Re-export legacy signals for backward compatibility
from phantom_guard.core.signals.legacy import (
    AGE_THRESHOLD_NEW_DAYS,
    DESCRIPTION_THRESHOLD_SHORT,
    # Constants - thresholds
    DOWNLOAD_THRESHOLD_LOW,
    DOWNLOAD_THRESHOLD_POPULAR,
    RELEASE_THRESHOLD_FEW,
    WEIGHT_FEW_RELEASES,
    WEIGHT_LONG_HISTORY,
    WEIGHT_LOW_DOWNLOADS,
    WEIGHT_NO_MAINTAINER,
    WEIGHT_NO_REPOSITORY,
    # Constants - weights
    WEIGHT_NOT_FOUND,
    WEIGHT_POPULAR_PACKAGE,
    WEIGHT_RECENTLY_CREATED,
    WEIGHT_SHORT_DESCRIPTION,
    calculate_total_weight,
    # Functions
    extract_signals,
    get_signal_by_type,
    has_signal_type,
    merge_signals,
)

__all__ = [
    "AGE_THRESHOLD_NEW_DAYS",
    "DESCRIPTION_THRESHOLD_SHORT",
    # Legacy constants - thresholds
    "DOWNLOAD_THRESHOLD_LOW",
    "DOWNLOAD_THRESHOLD_POPULAR",
    "RELEASE_THRESHOLD_FEW",
    "WEIGHT_FEW_RELEASES",
    "WEIGHT_LONG_HISTORY",
    "WEIGHT_LOW_DOWNLOADS",
    # Legacy constants - weights
    "WEIGHT_NOT_FOUND",
    "WEIGHT_NO_MAINTAINER",
    "WEIGHT_NO_REPOSITORY",
    "WEIGHT_POPULAR_PACKAGE",
    "WEIGHT_RECENTLY_CREATED",
    "WEIGHT_SHORT_DESCRIPTION",
    "calculate_total_weight",
    # Legacy functions
    "extract_signals",
    "get_signal_by_type",
    "has_signal_type",
    "merge_signals",
]
