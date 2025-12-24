"""
Core detection engine for Phantom Guard.

IMPLEMENTS: S001-S009
"""

from __future__ import annotations

from phantom_guard.core.patterns import (
    HALLUCINATION_PATTERNS,
    HallucinationPattern,
    PatternCategory,
    count_pattern_matches,
    get_highest_weight_pattern,
    get_pattern_by_id,
    list_patterns,
    match_patterns,
)
from phantom_guard.core.signals import (
    AGE_THRESHOLD_NEW_DAYS,
    DESCRIPTION_THRESHOLD_SHORT,
    DOWNLOAD_THRESHOLD_LOW,
    DOWNLOAD_THRESHOLD_POPULAR,
    RELEASE_THRESHOLD_FEW,
    calculate_total_weight,
    extract_signals,
    get_signal_by_type,
    has_signal_type,
    merge_signals,
)
from phantom_guard.core.types import (
    InvalidPackageNameError,
    InvalidRegistryError,
    PackageMetadata,
    PackageRisk,
    PhantomGuardError,
    Recommendation,
    Registry,
    Signal,
    SignalType,
    ValidationError,
    validate_package_name,
    validate_registry,
)

__all__ = [
    "AGE_THRESHOLD_NEW_DAYS",
    "DESCRIPTION_THRESHOLD_SHORT",
    "DOWNLOAD_THRESHOLD_LOW",
    "DOWNLOAD_THRESHOLD_POPULAR",
    "HALLUCINATION_PATTERNS",
    "RELEASE_THRESHOLD_FEW",
    "HallucinationPattern",
    "InvalidPackageNameError",
    "InvalidRegistryError",
    "PackageMetadata",
    "PackageRisk",
    "PatternCategory",
    "PhantomGuardError",
    "Recommendation",
    "Registry",
    "Signal",
    "SignalType",
    "ValidationError",
    "calculate_total_weight",
    "count_pattern_matches",
    "extract_signals",
    "get_highest_weight_pattern",
    "get_pattern_by_id",
    "get_signal_by_type",
    "has_signal_type",
    "list_patterns",
    "match_patterns",
    "merge_signals",
    "validate_package_name",
    "validate_registry",
]
