"""
IMPLEMENTS: S001, S002, S003
INVARIANTS: INV001-INV006, INV019-INV021
Main detection orchestrator.

This module provides the main entry point for package validation,
wiring together all core components (patterns, typosquat, signals, scorer).
"""

from __future__ import annotations

import asyncio
import time
from typing import Protocol

from phantom_guard.core.patterns import match_patterns
from phantom_guard.core.scorer import build_package_risk
from phantom_guard.core.signals import extract_signals, merge_signals
from phantom_guard.core.types import (
    InvalidPackageNameError,
    PackageMetadata,
    PackageRisk,
    Recommendation,
    Registry,
    Signal,
    SignalType,
    validate_package_name,
)
from phantom_guard.core.typosquat import detect_typosquat, is_popular_package

# =============================================================================
# PROTOCOLS
# =============================================================================


class RegistryClient(Protocol):
    """
    Protocol for registry clients.
    Allows dependency injection for testing.
    """

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """Fetch package metadata from registry."""
        ...  # pragma: no cover


# =============================================================================
# PACKAGE NAME HELPERS
# =============================================================================


def normalize_package_name(name: str) -> str:
    """
    IMPLEMENTS: S001

    Normalize package name for comparison.
    - Lowercase
    - Replace underscores with hyphens (PEP 503)
    - Strip whitespace

    Args:
        name: Package name to normalize

    Returns:
        Normalized package name
    """
    return name.lower().strip().replace("_", "-")


# =============================================================================
# SINGLE PACKAGE VALIDATION
# =============================================================================


async def validate_package(
    name: str,
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
) -> PackageRisk:
    """
    IMPLEMENTS: S001, S002, S003
    INVARIANTS: INV001-INV006

    Validate a single package for slopsquatting risk.

    This is the main entry point for package validation. It:
    1. Validates the package name format
    2. Runs static analysis (patterns, typosquat detection)
    3. Fetches metadata from registry (if client provided)
    4. Combines all signals and calculates risk score

    Args:
        name: Package name to validate
        registry: Target registry (pypi, npm, crates)
        client: Optional registry client (for testing or real API calls)

    Returns:
        PackageRisk with complete assessment

    Raises:
        InvalidPackageNameError: If package name is invalid
    """
    start_time = time.perf_counter()

    # Step 1: Validate and normalize input
    # This raises InvalidPackageNameError if invalid
    validated_name = validate_package_name(name)
    normalized_name = normalize_package_name(validated_name)

    # Step 2: Gather signals from static analysis
    pattern_signals = match_patterns(normalized_name)
    typosquat_signals = detect_typosquat(normalized_name, registry)

    # Step 3: Add popular package signal if applicable
    popular_signals: tuple[Signal, ...] = ()
    if is_popular_package(normalized_name, registry):
        popular_signals = (
            Signal(
                type=SignalType.POPULAR_PACKAGE,
                weight=-0.5,
                message=f"'{normalized_name}' is a popular {registry} package",
                metadata={"registry": registry},
            ),
        )

    # Step 4: Fetch metadata and extract signals (if client provided)
    if client is not None:
        metadata = await client.get_package_metadata(normalized_name)
        metadata_signals = extract_signals(metadata)
        exists = metadata.exists
    else:
        # No client = offline mode, use only static analysis
        metadata_signals = ()
        exists = True  # Assume exists if we can't check

    # Step 5: Merge all signals
    all_signals = merge_signals(
        pattern_signals,
        typosquat_signals,
        popular_signals,
        metadata_signals,
    )

    # Step 6: Build final result
    latency_ms = (time.perf_counter() - start_time) * 1000

    return build_package_risk(
        name=normalized_name,
        registry=registry,
        exists=exists,
        signals=all_signals,
        latency_ms=latency_ms,
    )


# =============================================================================
# BATCH VALIDATION
# =============================================================================


async def validate_batch(
    names: list[str],
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
    concurrency: int = 10,
) -> list[PackageRisk]:
    """
    IMPLEMENTS: S002
    INVARIANTS: INV004, INV005

    Validate multiple packages concurrently.

    Results are returned in the same order as the input list.
    Invalid package names result in HIGH_RISK entries (not exceptions).

    Args:
        names: List of package names to validate
        registry: Target registry
        client: Optional registry client
        concurrency: Max concurrent validations (default: 10)

    Returns:
        List of PackageRisk in same order as input
    """
    if not names:
        return []

    semaphore = asyncio.Semaphore(concurrency)

    async def validate_with_semaphore(name: str) -> PackageRisk:
        async with semaphore:
            try:
                return await validate_package(name, registry, client)
            except (InvalidPackageNameError, ValueError) as e:
                # Return error as high-risk result instead of raising
                # Use placeholder for empty names since PackageRisk requires non-empty
                safe_name = name if name and name.strip() else "<invalid>"
                return PackageRisk(
                    name=safe_name,
                    registry=registry,
                    exists=False,
                    risk_score=1.0,
                    signals=(
                        Signal(
                            type=SignalType.NOT_FOUND,
                            weight=0.9,
                            message=f"Invalid package name: {e}",
                        ),
                    ),
                    recommendation=Recommendation.HIGH_RISK,
                    latency_ms=0.0,
                )

    tasks = [validate_with_semaphore(name) for name in names]
    return list(await asyncio.gather(*tasks))


# =============================================================================
# SYNCHRONOUS WRAPPERS
# =============================================================================


def validate_package_sync(
    name: str,
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
) -> PackageRisk:
    """
    IMPLEMENTS: S001

    Synchronous wrapper for validate_package.

    This is a convenience function for non-async code.

    Args:
        name: Package name to validate
        registry: Target registry
        client: Optional registry client

    Returns:
        PackageRisk with complete assessment

    Raises:
        InvalidPackageNameError: If package name is invalid
    """
    return asyncio.run(validate_package(name, registry, client))


def validate_batch_sync(
    names: list[str],
    registry: Registry = "pypi",
    client: RegistryClient | None = None,
    concurrency: int = 10,
) -> list[PackageRisk]:
    """
    IMPLEMENTS: S002

    Synchronous wrapper for validate_batch.

    Args:
        names: List of package names
        registry: Target registry
        client: Optional registry client
        concurrency: Max concurrent validations

    Returns:
        List of PackageRisk in same order as input
    """
    return asyncio.run(validate_batch(names, registry, client, concurrency))
