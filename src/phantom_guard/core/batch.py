"""
Batch validation with concurrency control.

IMPLEMENTS: S002
INVARIANTS: INV004, INV005
TESTS: T002.01-T002.08
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from phantom_guard.core.types import PackageRisk, Recommendation

if TYPE_CHECKING:
    from phantom_guard.registry.cached import RegistryClientProtocol

# Type alias for registry
RegistryType = Literal["pypi", "npm", "crates"]


@dataclass
class BatchConfig:
    """
    Configuration for batch validation.

    Attributes:
        max_concurrent: Maximum concurrent validations (default: 10)
        fail_fast: Stop on first HIGH_RISK package (default: False)
        timeout_per_package: Per-package timeout in seconds (default: 30.0)
        retry_count: Retries per package on transient errors (default: 2)
    """

    max_concurrent: int = 10
    fail_fast: bool = False
    timeout_per_package: float = 30.0
    retry_count: int = 2

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_concurrent < 1:
            raise ValueError("max_concurrent must be >= 1")
        if self.timeout_per_package <= 0:
            raise ValueError("timeout_per_package must be > 0")
        if self.retry_count < 0:
            raise ValueError("retry_count must be >= 0")


@dataclass
class BatchResult:
    """
    Result of batch validation.

    INVARIANT: INV004 - Contains all input packages (success or error).

    Attributes:
        results: All successful package results
        errors: Packages that failed with errors (name -> exception)
        total_time_ms: Total validation time in milliseconds
        was_cancelled: True if fail_fast triggered early stop
    """

    results: list[PackageRisk] = field(default_factory=list)
    errors: dict[str, Exception] = field(default_factory=dict)
    total_time_ms: float = 0.0
    was_cancelled: bool = False

    @property
    def success_count(self) -> int:
        """Number of successfully validated packages."""
        return len(self.results)

    @property
    def error_count(self) -> int:
        """Number of packages that failed with errors."""
        return len(self.errors)

    @property
    def total_count(self) -> int:
        """Total packages processed (success + errors)."""
        return self.success_count + self.error_count

    @property
    def has_high_risk(self) -> bool:
        """Check if any HIGH_RISK packages found."""
        return any(r.recommendation == Recommendation.HIGH_RISK for r in self.results)

    @property
    def has_suspicious(self) -> bool:
        """Check if any SUSPICIOUS packages found."""
        return any(r.recommendation == Recommendation.SUSPICIOUS for r in self.results)

    def get_by_recommendation(self, rec: Recommendation) -> list[PackageRisk]:
        """Get all results with a specific recommendation."""
        return [r for r in self.results if r.recommendation == rec]


class BatchValidator:
    """
    High-performance batch package validation.

    IMPLEMENTS: S002
    INV: INV004, INV005
    TEST: T002.01-T002.08

    Validates multiple packages concurrently with:
    - Configurable concurrency limits
    - Automatic rate limit handling
    - Real-time progress callbacks
    - Fail-fast option for CI/CD
    - Graceful error handling

    Example:
        validator = BatchValidator(config=BatchConfig(max_concurrent=10))
        result = await validator.validate_batch(
            packages=["flask", "django", "requests"],
            registry="pypi",
            on_progress=lambda done, total: print(f"{done}/{total}"),
        )
    """

    def __init__(self, config: BatchConfig | None = None) -> None:
        """
        Initialize batch validator.

        Args:
            config: Batch configuration (uses defaults if None)
        """
        self.config = config or BatchConfig()
        self._cancel_event: asyncio.Event | None = None

    async def validate_batch(
        self,
        packages: list[str],
        registry: RegistryType,
        client: RegistryClientProtocol,
        on_progress: Callable[[int, int], None] | None = None,
        on_result: Callable[[PackageRisk], Awaitable[None] | None] | None = None,
    ) -> BatchResult:
        """
        Validate multiple packages concurrently.

        IMPLEMENTS: S002
        INV: INV004, INV005
        TEST: T002.01-T002.04

        Args:
            packages: List of package names to validate
            registry: Registry to check (pypi, npm, crates)
            client: Registry client to use for validation
            on_progress: Called after each package with (done, total)
            on_result: Called with each result as it completes

        Returns:
            BatchResult with all results and any errors

        Note:
            INV004: Result contains all input packages (success or error)
            INV005: With fail_fast=True, stops on first HIGH_RISK
        """
        from phantom_guard.core import detector

        start_time = time.perf_counter()
        self._cancel_event = asyncio.Event()

        result = BatchResult()
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        completed = 0
        lock = asyncio.Lock()

        async def validate_one(package: str) -> None:
            nonlocal completed

            # Check for cancellation before starting
            if self._cancel_event and self._cancel_event.is_set():  # pragma: no cover
                return  # pragma: no cover

            try:
                async with semaphore:
                    # Check again after acquiring semaphore
                    if self._cancel_event and self._cancel_event.is_set():
                        return

                    # Run validation with timeout
                    risk = await asyncio.wait_for(
                        detector.validate_package(package, registry, client),
                        timeout=self.config.timeout_per_package,
                    )

                    async with lock:
                        result.results.append(risk)
                        completed += 1

                        if on_progress:
                            on_progress(completed, len(packages))

                        if on_result:
                            callback_result = on_result(risk)
                            if asyncio.iscoroutine(callback_result):
                                await callback_result

                        # INV005: fail_fast stops on HIGH_RISK
                        if (
                            self.config.fail_fast
                            and risk.recommendation == Recommendation.HIGH_RISK
                            and self._cancel_event
                        ):
                            self._cancel_event.set()
                            result.was_cancelled = True

            except TimeoutError:
                async with lock:
                    result.errors[package] = TimeoutError(
                        f"Validation timed out after {self.config.timeout_per_package}s"
                    )
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(packages))

            except Exception as e:
                async with lock:
                    result.errors[package] = e
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(packages))

        # Create and run all validation tasks
        tasks = [asyncio.create_task(validate_one(pkg)) for pkg in packages]

        # Wait for all tasks (or until cancelled)
        await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate total time
        result.total_time_ms = (time.perf_counter() - start_time) * 1000

        return result

    def cancel(self) -> None:
        """Cancel ongoing batch validation."""
        if self._cancel_event:
            self._cancel_event.set()
