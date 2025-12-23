"""Core detection engine components."""

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

__all__ = [
    "Detector",
    "PackageMetadata",
    "PackageRisk",
    "PatternMatcher",
    "Registry",
    "RiskLevel",
    "RiskScorer",
    "RiskSignal",
    "SignalType",
    "ValidationResult",
]
