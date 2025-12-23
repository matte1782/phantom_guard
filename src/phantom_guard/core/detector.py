"""Main detection engine for slopsquatting attacks.

Orchestrates the complete validation pipeline:
1. Validate package name
2. Check cache (future)
3. Fetch metadata from registry
4. Check for hallucination patterns
5. Calculate risk score
6. Return risk assessment
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Sequence
from typing import TYPE_CHECKING

from phantom_guard.core.patterns import PatternMatcher
from phantom_guard.core.scorer import RiskScorer
from phantom_guard.core.types import (
    PackageRisk,
    Registry,
    RiskLevel,
    RiskSignal,
    SignalType,
    ValidationResult,
)
from phantom_guard.registry.base import RegistryClient, RegistryError

if TYPE_CHECKING:
    from phantom_guard.core.patterns import HallucinationPattern

logger = logging.getLogger(__name__)

# Pattern match penalty
PATTERN_MATCH_PENALTY = 20


class Detector:
    """Main detection engine for slopsquatting attacks.

    Coordinates registry clients, pattern matching, and risk scoring
    to produce comprehensive package risk assessments.

    Usage:
        detector = Detector()

        # Check single package
        risk = await detector.check_package("flask")
        print(f"{risk.risk_level}: {risk.recommendation}")

        # Check multiple packages
        result = await detector.check_packages(["flask", "django", "fake-pkg"])
        print(f"Safe: {len(result.safe)}, Blocked: {len(result.blocked)}")
    """

    def __init__(
        self,
        scorer: RiskScorer | None = None,
        pattern_matcher: PatternMatcher | None = None,
    ) -> None:
        """Initialize detector.

        Args:
            scorer: Risk scorer instance. Defaults to RiskScorer().
            pattern_matcher: Pattern matcher instance. Defaults to PatternMatcher().
        """
        self.scorer = scorer or RiskScorer()
        self.pattern_matcher = pattern_matcher or PatternMatcher()

    async def check_package(
        self,
        package_name: str,
        registry: Registry = Registry.PYPI,
    ) -> PackageRisk:
        """Check a single package for slopsquatting risk.

        Args:
            package_name: Name of the package to check.
            registry: Which registry to check. Defaults to PyPI.

        Returns:
            Complete risk assessment.

        Raises:
            RegistryError: If registry API fails.
            ValueError: If package name is invalid.
        """
        client = self._get_client(registry)

        async with client:
            metadata = await client.fetch_metadata(package_name)

        # Score based on metadata
        result = self.scorer.score(metadata)

        # Check for hallucination pattern in name
        pattern = self.pattern_matcher.match(package_name)
        if pattern:
            result = self._add_pattern_signal(result, pattern)

        return result

    async def check_packages(
        self,
        packages: Sequence[str],
        registry: Registry = Registry.PYPI,
        concurrency: int = 10,
    ) -> ValidationResult:
        """Check multiple packages concurrently.

        Args:
            packages: Package names to check.
            registry: Which registry to check. Defaults to PyPI.
            concurrency: Maximum concurrent requests. Defaults to 10.

        Returns:
            Aggregated validation results.
        """
        if not packages:
            return ValidationResult(
                safe=(),
                suspicious=(),
                blocked=(),
                errors=(),
                validation_time_ms=0,
            )

        start_time = time.monotonic()

        safe: list[str] = []
        suspicious: list[PackageRisk] = []
        blocked: list[PackageRisk] = []
        errors: list[str] = []

        client = self._get_client(registry)

        # Use semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        async def check_with_limit(pkg: str) -> tuple[str, PackageRisk | Exception]:
            async with semaphore:
                try:
                    result = await self._check_one(client, pkg)
                    return (pkg, result)
                except Exception as e:
                    return (pkg, e)

        async with client:
            tasks = [check_with_limit(pkg) for pkg in packages]
            results = await asyncio.gather(*tasks)

        for pkg, result in results:
            if isinstance(result, Exception):
                errors.append(f"{pkg}: {result}")
                logger.warning("Error checking %s: %s", pkg, result)
            elif result.risk_level == RiskLevel.SAFE:
                safe.append(pkg)
            elif result.risk_level == RiskLevel.NOT_FOUND:
                blocked.append(result)
            else:
                suspicious.append(result)

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        logger.info(
            "Validated %d packages in %dms: %d safe, %d suspicious, %d blocked, %d errors",
            len(packages),
            elapsed_ms,
            len(safe),
            len(suspicious),
            len(blocked),
            len(errors),
        )

        return ValidationResult(
            safe=tuple(safe),
            suspicious=tuple(suspicious),
            blocked=tuple(blocked),
            errors=tuple(errors),
            validation_time_ms=elapsed_ms,
        )

    async def _check_one(
        self,
        client: RegistryClient,
        package_name: str,
    ) -> PackageRisk:
        """Check a single package with a shared client.

        Args:
            client: Shared registry client.
            package_name: Name of the package to check.

        Returns:
            Risk assessment.

        Raises:
            RegistryError: If registry API fails.
            ValueError: If package name is invalid.
        """
        try:
            metadata = await client.fetch_metadata(package_name)
            result = self.scorer.score(metadata)

            pattern = self.pattern_matcher.match(package_name)
            if pattern:
                result = self._add_pattern_signal(result, pattern)

            return result
        except RegistryError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise RegistryError(
                f"Unexpected error checking {package_name}: {e}",
                package=package_name,
            ) from e

    def _get_client(self, registry: Registry) -> RegistryClient:
        """Get registry client for the specified registry.

        Args:
            registry: Which registry to get client for.

        Returns:
            Registry client instance.

        Raises:
            ValueError: If registry is not supported.
        """
        # Import here to avoid circular imports
        from phantom_guard.registry.crates import CratesClient
        from phantom_guard.registry.npm import NpmClient
        from phantom_guard.registry.pypi import PyPIClient

        clients: dict[Registry, type[RegistryClient]] = {
            Registry.PYPI: PyPIClient,
            Registry.NPM: NpmClient,
            Registry.CRATES: CratesClient,
        }

        if registry not in clients:
            raise ValueError(f"Registry not supported: {registry}")

        return clients[registry]()

    def _add_pattern_signal(
        self,
        result: PackageRisk,
        pattern: HallucinationPattern,
    ) -> PackageRisk:
        """Add hallucination pattern signal to result.

        Pattern matches reduce the score and add a warning signal.

        Args:
            result: Original risk assessment.
            pattern: Matched hallucination pattern.

        Returns:
            Updated risk assessment with pattern signal.
        """
        new_signal = RiskSignal(
            signal_type=SignalType.HALLUCINATION_PATTERN,
            weight=-PATTERN_MATCH_PENALTY,
            details=f"Name matches pattern: {pattern.description}",
        )

        new_signals = (*result.signals, new_signal)

        # Recalculate score with penalty
        new_score = max(0, result.risk_score - PATTERN_MATCH_PENALTY)

        # Recalculate risk level
        if new_score >= 60:
            new_level = RiskLevel.SAFE
        elif new_score >= 30:
            new_level = RiskLevel.SUSPICIOUS
        else:
            new_level = RiskLevel.HIGH_RISK

        return PackageRisk(
            package_name=result.package_name,
            registry=result.registry,
            risk_level=new_level,
            risk_score=new_score,
            signals=new_signals,
            recommendation=result.recommendation,
            metadata=result.metadata,
        )
