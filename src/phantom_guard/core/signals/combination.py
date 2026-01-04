"""
IMPLEMENTS: S080
Signal Combination for Phantom Guard.

Combines multiple detection signals into a unified risk score:
- Namespace squatting (S060): 0.35
- Download inflation (S065): 0.30
- Ownership transfer (S070): 0.15
- Version spike (S075): 0.45

Total v0.2.0 signal weight: 1.25
Combined with legacy signals for full risk assessment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from phantom_guard.core.signals.downloads import (
    DOWNLOAD_INFLATION_WEIGHT,
    DownloadInflationSignal,
    detect_download_inflation,
)
from phantom_guard.core.signals.namespace import (
    NAMESPACE_SQUAT_WEIGHT,
    NamespaceSignal,
    detect_namespace_squatting,
)
from phantom_guard.core.signals.ownership import (
    OWNERSHIP_MAX_WEIGHT,
    OwnershipSignal,
    detect_ownership_transfer,
)
from phantom_guard.core.signals.versions import (
    WEIGHT_7D_SPIKE,
    WEIGHT_24H_SPIKE,
    VersionSpikeSignal,
    detect_version_spike,
)

logger = logging.getLogger(__name__)


# =============================================================================
# TYPES
# =============================================================================


@dataclass
class CombinedSignals:
    """
    IMPLEMENTS: S080

    Container for all v0.2.0 signals.
    """

    namespace: NamespaceSignal | None = None
    download: DownloadInflationSignal | None = None
    ownership: OwnershipSignal | None = None
    version: VersionSpikeSignal | None = None
    signals_collected: list[str] = field(default_factory=list)
    total_weight: float = 0.0

    def add_signal(self, name: str, weight: float) -> None:
        """Add a signal to the collected list."""
        self.signals_collected.append(name)
        self.total_weight += weight


# =============================================================================
# CONSTANTS
# =============================================================================

# Signal weights (from individual modules)
SIGNAL_WEIGHTS: dict[str, float] = {
    "NAMESPACE_SQUATTING": NAMESPACE_SQUAT_WEIGHT,  # 0.35
    "DOWNLOAD_INFLATION": DOWNLOAD_INFLATION_WEIGHT,  # 0.30
    "OWNERSHIP_TRANSFER": OWNERSHIP_MAX_WEIGHT,  # 0.15
    "VERSION_SPIKE_24H": WEIGHT_24H_SPIKE,  # 0.45
    "VERSION_SPIKE_7D": WEIGHT_7D_SPIKE,  # 0.30
}

# Maximum combined weight from v0.2.0 signals
MAX_V02_WEIGHT: float = 1.25  # 0.35 + 0.30 + 0.15 + 0.45


# =============================================================================
# SIGNAL COMBINATION
# =============================================================================


def gather_all_signals(
    package_name: str,
    metadata: dict[str, Any] | None,
    registry: str,
) -> CombinedSignals:
    """
    IMPLEMENTS: S080
    TESTS: T080.01-T080.11

    Gather all v0.2.0 signals for a package.

    Args:
        package_name: The package name to check.
        metadata: Package metadata.
        registry: The registry type (npm, pypi, crates).

    Returns:
        CombinedSignals with all detected signals.
    """
    combined = CombinedSignals()

    if metadata is None:
        return combined

    # Detect namespace squatting
    namespace_signal = detect_namespace_squatting(package_name, metadata, registry)
    if namespace_signal is not None:
        combined.namespace = namespace_signal
        combined.add_signal("NAMESPACE_SQUATTING", namespace_signal.confidence)

    # Detect download inflation
    download_signal = detect_download_inflation(package_name, metadata, registry)
    if download_signal is not None:
        combined.download = download_signal
        combined.add_signal("DOWNLOAD_INFLATION", download_signal.confidence)

    # Detect ownership transfer
    ownership_signal = detect_ownership_transfer(package_name, metadata, registry)
    if ownership_signal is not None:
        combined.ownership = ownership_signal
        combined.add_signal("OWNERSHIP_TRANSFER", ownership_signal.confidence)

    # Detect version spike
    version_signal = detect_version_spike(package_name, metadata, registry)
    if version_signal is not None:
        combined.version = version_signal
        # Use the specific weight from the signal
        combined.add_signal("VERSION_SPIKE", version_signal.confidence)

    return combined


def calculate_combined_weight(signals: list[str]) -> float:
    """
    IMPLEMENTS: S080
    TESTS: T080.01-T080.03

    Calculate combined weight from signal names.

    Args:
        signals: List of signal names.

    Returns:
        Combined weight.
    """
    total: float = 0.0
    for signal in signals:
        if signal == "VERSION_SPIKE":
            # Default to 24h weight for generic VERSION_SPIKE
            total += SIGNAL_WEIGHTS.get("VERSION_SPIKE_24H", 0.0)
        else:
            total += SIGNAL_WEIGHTS.get(signal, 0.0)
    return total


def combine_signals(
    signals: list[tuple[str, float | None]],
) -> tuple[list[str], float]:
    """
    IMPLEMENTS: S080
    TESTS: T080.08

    Combine signals, skipping None values.

    Args:
        signals: List of (name, weight) tuples where weight can be None.

    Returns:
        Tuple of (active signal names, combined weight).
    """
    active: list[str] = []
    total: float = 0.0

    for name, weight in signals:
        if weight is not None:
            active.append(name)
            total += weight

    return active, total


def order_signals(signals: list[str]) -> list[str]:
    """
    IMPLEMENTS: S080
    TESTS: T080.11

    Order signals consistently (alphabetical).

    Args:
        signals: List of signal names.

    Returns:
        Alphabetically sorted signal names.
    """
    return sorted(signals)


def calculate_normalized_score(
    raw_score: float,
    max_score: float = 285.0,
) -> float:
    """
    IMPLEMENTS: S080
    TESTS: T080.09

    Normalize raw score to [0.0, 1.0] range.

    Args:
        raw_score: The raw combined score.
        max_score: Maximum expected raw score.

    Returns:
        Normalized score clamped to [0.0, 1.0].
    """
    if raw_score <= 0:
        return 0.0
    if raw_score >= max_score:
        return 1.0
    return raw_score / max_score
