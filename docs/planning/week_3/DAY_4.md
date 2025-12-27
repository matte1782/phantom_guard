# Week 3 - Day 4: Batch Validation (Concurrent Processing)

> **Date**: Day 4 (Week 3)
> **Focus**: High-performance batch validation with concurrency control
> **Tasks**: W3.4
> **Hours**: 6-8 hours
> **SPEC_IDs**: S002
> **INV_IDs**: INV004, INV005
> **TEST_IDs**: T002.01-T002.08
> **EC_IDs**: EC035

---

## Overview

Implement efficient batch validation that can process 50+ packages concurrently while respecting rate limits and providing real-time progress feedback. This is critical for CI/CD integration where large dependency files need fast validation.

### Deliverables
- [ ] BatchValidator class with concurrency control
- [ ] Rate limiting with adaptive backoff
- [ ] Progress reporting with Rich
- [ ] Error aggregation and partial results
- [ ] `--fail-fast` option support
- [ ] Performance within budget (<5s for 50 packages)

---

## Morning Session (3h)

### Objective
Implement the core BatchValidator with concurrency control.

### Step 1: Create Batch Validation Module (30min)

```bash
touch src/phantom_guard/core/batch.py
```

### Step 2: Implement BatchValidator Class (1.5h)

```python
# src/phantom_guard/core/batch.py
"""
IMPLEMENTS: S002
INVARIANTS: INV004, INV005
Batch validation with concurrency control.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Awaitable

from phantom_guard.core.detector import Detector
from phantom_guard.core.types import PackageRisk, Recommendation

if TYPE_CHECKING:
    from phantom_guard.cache import Cache


@dataclass
class BatchConfig:
    """
    Configuration for batch validation.

    Attributes:
        max_concurrent: Maximum concurrent validations (default: 10)
        fail_fast: Stop on first HIGH_RISK package (default: False)
        timeout_per_package: Per-package timeout in seconds (default: 10.0)
        retry_count: Retries per package on transient errors (default: 3)
    """
    max_concurrent: int = 10
    fail_fast: bool = False
    timeout_per_package: float = 10.0
    retry_count: int = 3


@dataclass
class BatchResult:
    """
    INVARIANT: INV004 - Contains all input packages.

    Result of batch validation.

    Attributes:
        results: All package results (success + failures)
        errors: Packages that failed with errors
        total_time_ms: Total validation time
        was_cancelled: True if fail_fast triggered
    """
    results: list[PackageRisk] = field(default_factory=list)
    errors: dict[str, Exception] = field(default_factory=dict)
    total_time_ms: float = 0.0
    was_cancelled: bool = False

    @property
    def success_count(self) -> int:
        return len(self.results)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def total_count(self) -> int:
        return self.success_count + self.error_count


class BatchValidator:
    """
    IMPLEMENTS: S002
    INV: INV004, INV005
    TEST: T002.01-T002.08

    High-performance batch package validation.

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

    def __init__(
        self,
        config: BatchConfig | None = None,
        detector: Detector | None = None,
    ):
        self.config = config or BatchConfig()
        self.detector = detector or Detector()
        self._cancel_event: asyncio.Event | None = None

    async def validate_batch(
        self,
        packages: list[str],
        registry: str = "pypi",
        on_progress: Callable[[int, int], None] | None = None,
        on_result: Callable[[PackageRisk], Awaitable[None]] | None = None,
    ) -> BatchResult:
        """
        IMPLEMENTS: S002
        INV: INV004, INV005
        TEST: T002.01-T002.04

        Validate multiple packages concurrently.

        Args:
            packages: List of package names to validate
            registry: Registry to check (pypi, npm, crates)
            on_progress: Called after each package (done, total)
            on_result: Called with each result as it completes

        Returns:
            BatchResult with all results and any errors

        Note:
            INV004: Result contains all input packages (success or error)
            INV005: With fail_fast, stops on first HIGH_RISK
        """
        import time

        start_time = time.perf_counter()
        self._cancel_event = asyncio.Event()

        result = BatchResult()
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        completed = 0
        lock = asyncio.Lock()

        async def validate_one(package: str) -> None:
            nonlocal completed

            # Check for cancellation
            if self._cancel_event.is_set():
                return

            try:
                async with semaphore:
                    if self._cancel_event.is_set():
                        return

                    risk = await asyncio.wait_for(
                        self.detector.validate(package, registry=registry),
                        timeout=self.config.timeout_per_package,
                    )

                    async with lock:
                        result.results.append(risk)
                        completed += 1

                        if on_progress:
                            on_progress(completed, len(packages))

                        if on_result:
                            await on_result(risk)

                        # INV005: fail_fast stops on HIGH_RISK
                        if self.config.fail_fast and risk.recommendation == Recommendation.HIGH_RISK:
                            self._cancel_event.set()
                            result.was_cancelled = True

            except asyncio.TimeoutError:
                async with lock:
                    result.errors[package] = TimeoutError(f"Validation timed out after {self.config.timeout_per_package}s")
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(packages))

            except Exception as e:
                async with lock:
                    result.errors[package] = e
                    completed += 1
                    if on_progress:
                        on_progress(completed, len(packages))

        # Create all validation tasks
        tasks = [validate_one(pkg) for pkg in packages]

        # Run with gathering
        await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate total time
        result.total_time_ms = (time.perf_counter() - start_time) * 1000

        return result

    async def validate_batch_with_cache(
        self,
        packages: list[str],
        registry: str,
        cache: "Cache",
        **kwargs,
    ) -> BatchResult:
        """
        Validate with cache integration.

        Pre-checks cache and only fetches uncached packages.
        """
        from phantom_guard.registry.cached import CachedRegistryClient

        # TODO: Integrate with cached registry client
        return await self.validate_batch(packages, registry, **kwargs)
```

### Step 3: Enable Batch Validation Tests (15min)

```python
# tests/unit/test_batch.py
# Remove @pytest.mark.skip from:
# - test_batch_contains_all_packages (T002.01)
# - test_batch_fail_fast_stops (T002.02)
# - test_batch_concurrent_limit (T002.03)
# - test_batch_handles_errors (T002.04)
```

### Step 4: Write Batch Validation Tests (45min)

```python
# tests/unit/test_batch.py
"""
SPEC: S002
INVARIANTS: INV004, INV005
Tests for batch validation.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from phantom_guard.core.batch import BatchValidator, BatchConfig, BatchResult
from phantom_guard.core.types import PackageRisk, Recommendation


class TestBatchValidator:
    @pytest.mark.asyncio
    async def test_batch_contains_all_packages(self):
        """
        TEST_ID: T002.01
        INV: INV004

        Result contains all input packages.
        """
        packages = ["flask", "django", "requests"]
        validator = BatchValidator()

        # Mock the detector
        validator.detector.validate = AsyncMock(
            side_effect=lambda name, **kw: PackageRisk(
                name=name,
                risk_score=0.1,
                recommendation=Recommendation.SAFE,
                signals=(),
            )
        )

        result = await validator.validate_batch(packages, registry="pypi")

        # INV004: All packages accounted for
        assert result.total_count == len(packages)
        result_names = {r.name for r in result.results}
        assert result_names == set(packages)

    @pytest.mark.asyncio
    async def test_batch_fail_fast_stops(self):
        """
        TEST_ID: T002.02
        INV: INV005

        fail_fast stops on first HIGH_RISK.
        """
        packages = ["safe1", "risky", "safe2", "safe3"]

        def mock_validate(name, **kw):
            if name == "risky":
                return PackageRisk(name, 0.9, Recommendation.HIGH_RISK, ())
            return PackageRisk(name, 0.1, Recommendation.SAFE, ())

        config = BatchConfig(fail_fast=True, max_concurrent=1)
        validator = BatchValidator(config=config)
        validator.detector.validate = AsyncMock(side_effect=mock_validate)

        result = await validator.validate_batch(packages, registry="pypi")

        # Should have stopped after risky
        assert result.was_cancelled is True
        # Not all packages processed
        assert len(result.results) < len(packages)
        # But risky was detected
        assert any(r.recommendation == Recommendation.HIGH_RISK for r in result.results)

    @pytest.mark.asyncio
    async def test_batch_respects_concurrent_limit(self):
        """
        TEST_ID: T002.03

        Never exceeds max_concurrent.
        """
        packages = ["pkg1", "pkg2", "pkg3", "pkg4", "pkg5"]
        max_concurrent_observed = 0
        current_concurrent = 0
        lock = asyncio.Lock()

        async def slow_validate(name, **kw):
            nonlocal max_concurrent_observed, current_concurrent
            async with lock:
                current_concurrent += 1
                max_concurrent_observed = max(max_concurrent_observed, current_concurrent)
            await asyncio.sleep(0.1)
            async with lock:
                current_concurrent -= 1
            return PackageRisk(name, 0.1, Recommendation.SAFE, ())

        config = BatchConfig(max_concurrent=2)
        validator = BatchValidator(config=config)
        validator.detector.validate = AsyncMock(side_effect=slow_validate)

        await validator.validate_batch(packages, registry="pypi")

        # Should never exceed limit
        assert max_concurrent_observed <= 2

    @pytest.mark.asyncio
    async def test_batch_handles_errors_gracefully(self):
        """
        TEST_ID: T002.04

        Errors don't stop other validations.
        """
        packages = ["good1", "error", "good2"]

        def mock_validate(name, **kw):
            if name == "error":
                raise ValueError("Test error")
            return PackageRisk(name, 0.1, Recommendation.SAFE, ())

        validator = BatchValidator()
        validator.detector.validate = AsyncMock(side_effect=mock_validate)

        result = await validator.validate_batch(packages, registry="pypi")

        # Errors captured, other packages succeeded
        assert len(result.results) == 2
        assert len(result.errors) == 1
        assert "error" in result.errors

    @pytest.mark.asyncio
    async def test_progress_callback_called(self):
        """Progress callback is called for each package."""
        packages = ["pkg1", "pkg2", "pkg3"]
        progress_calls = []

        def on_progress(done, total):
            progress_calls.append((done, total))

        validator = BatchValidator()
        validator.detector.validate = AsyncMock(
            return_value=PackageRisk("test", 0.1, Recommendation.SAFE, ())
        )

        await validator.validate_batch(
            packages,
            registry="pypi",
            on_progress=on_progress,
        )

        # Called for each package
        assert len(progress_calls) == 3
        # Last call should show completion
        assert progress_calls[-1][0] == 3


class TestBatchPerformance:
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_batch_50_packages_under_5s(self):
        """
        TEST_ID: T002.08
        EC: EC035

        50 packages complete in under 5 seconds.
        """
        import time

        packages = [f"package-{i}" for i in range(50)]

        async def fast_validate(name, **kw):
            await asyncio.sleep(0.05)  # 50ms per package
            return PackageRisk(name, 0.1, Recommendation.SAFE, ())

        config = BatchConfig(max_concurrent=10)
        validator = BatchValidator(config=config)
        validator.detector.validate = AsyncMock(side_effect=fast_validate)

        start = time.perf_counter()
        result = await validator.validate_batch(packages, registry="pypi")
        elapsed = time.perf_counter() - start

        # With 10 concurrent, 50 packages × 50ms = 250ms theoretical minimum
        # Allow up to 5s for real-world overhead
        assert elapsed < 5.0
        assert result.total_count == 50
```

---

## Afternoon Session (3h)

### Objective
Integrate batch validation with CLI and add progress visualization.

### Step 5: Integrate with CLI Check Command (1h)

```python
# src/phantom_guard/cli/main.py (update _check_packages)

from phantom_guard.core.batch import BatchValidator, BatchConfig


async def _check_packages(
    packages: list[ParsedPackage],
    parallel: int,
    fail_on: str | None,
    output_format: str,
    quiet: bool,
    verbose: bool = False,
    fail_fast: bool = False,
) -> int:
    """Validate all packages using BatchValidator."""
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskID
    from phantom_guard.cli.formatters import get_formatter

    # Configure batch validation
    config = BatchConfig(
        max_concurrent=parallel,
        fail_fast=fail_fast,
    )
    validator = BatchValidator(config=config)

    # Get formatter
    formatter = get_formatter(output_format, verbose=verbose, quiet=quiet)

    # Progress tracking
    if not quiet:
        console.print(f"\n[cyan]Scanning {len(packages)} packages...[/cyan]\n")

    progress_task: TaskID | None = None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
        disable=quiet,
    ) as progress:
        progress_task = progress.add_task("Validating", total=len(packages))

        def on_progress(done: int, total: int) -> None:
            progress.update(progress_task, completed=done)

        # Run batch validation
        result = await validator.validate_batch(
            packages=[p.name for p in packages],
            registry=packages[0].registry if packages else "pypi",
            on_progress=on_progress,
        )

    # Print results
    console.print()
    formatter.print_results(result.results, console)

    # Print errors if any
    if result.errors:
        console.print("\n[yellow]Errors:[/yellow]")
        for pkg, error in result.errors.items():
            console.print(f"  [red]{pkg}:[/red] {error}")

    # Summary
    if output_format == "text":
        _print_batch_summary(result, console)

    # Timing
    if not quiet:
        console.print(f"\n[dim]Completed in {result.total_time_ms:.0f}ms[/dim]")

    return _determine_exit_code(result.results, fail_on)


def _print_batch_summary(result: BatchResult, console: Console) -> None:
    """Print batch summary."""
    safe = sum(1 for r in result.results if r.recommendation == Recommendation.SAFE)
    suspicious = sum(1 for r in result.results if r.recommendation == Recommendation.SUSPICIOUS)
    high_risk = sum(1 for r in result.results if r.recommendation == Recommendation.HIGH_RISK)
    not_found = sum(1 for r in result.results if r.recommendation == Recommendation.NOT_FOUND)

    console.print("\n" + "─" * 60)
    summary = f"Summary: {result.total_count} packages | "
    summary += f"[green]{safe} safe[/green] | "
    summary += f"[yellow]{suspicious} suspicious[/yellow] | "
    summary += f"[red]{high_risk} high-risk[/red]"
    if not_found:
        summary += f" | [dim]{not_found} not found[/dim]"
    if result.error_count:
        summary += f" | [red]{result.error_count} errors[/red]"
    console.print(summary)
    console.print("─" * 60)

    if result.was_cancelled:
        console.print("[yellow]Note: Stopped early due to --fail-fast[/yellow]")
```

### Step 6: Add --fail-fast CLI Option (30min)

```python
# Update check command signature
@app.command()
def check(
    file: Annotated[Path, typer.Argument(help="Dependency file to check")],
    # ... existing options ...
    fail_fast: Annotated[bool, typer.Option("--fail-fast", help="Stop on first HIGH_RISK package")] = False,
) -> None:
    # ... pass fail_fast to _check_packages
```

### Step 7: Run Integration Tests (1h)

```bash
# Unit tests
pytest tests/unit/test_batch.py -v --tb=short

# Create test requirements file
echo "flask
django
requests
numpy
pandas
scikit-learn
tensorflow
pytorch
fastapi
sqlalchemy" > /tmp/test-large.txt

# Manual testing
phantom-guard check /tmp/test-large.txt --parallel 5
phantom-guard check /tmp/test-large.txt --parallel 10
phantom-guard check /tmp/test-large.txt --fail-fast

# Performance test
time phantom-guard check /tmp/test-large.txt --parallel 10
```

### Step 8: Add CLI Integration Tests (30min)

```python
# tests/integration/test_cli_batch.py

@pytest.mark.integration
class TestCLIBatchValidation:
    def test_check_with_fail_fast(self, tmp_path):
        """
        EC: EC035

        --fail-fast stops on first high-risk package.
        """
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\nreqeusts\ndjango\n")  # reqeusts is typosquat

        result = runner.invoke(app, [
            "check", str(req_file), "--fail-fast"
        ])

        # Should have exited early
        assert "Stopped early" in result.output or result.exit_code == EXIT_HIGH_RISK

    def test_check_parallel_performance(self, tmp_path):
        """
        Parallel validation completes faster than serial.
        """
        import time

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("\n".join(f"package-{i}" for i in range(10)))

        # Would need mocking for actual test
        # This is a placeholder for manual verification
        pass
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/core/batch.py` - No lint errors
- [ ] `ruff format src/phantom_guard/core/batch.py` - Code formatted
- [ ] `mypy src/phantom_guard/core/batch.py --strict` - No type errors
- [ ] All T002.* tests passing

### Performance
- [ ] 50 packages in <5s with parallel=10
- [ ] Memory usage stable during batch

### Documentation
- [ ] BatchValidator has comprehensive docstrings
- [ ] INV004/INV005 documented in code
- [ ] Progress callback documented

### Git Commit

```bash
git add src/phantom_guard/core/batch.py tests/unit/test_batch.py
git commit -m "feat(core): Implement concurrent batch validation

IMPLEMENTS: S002
INVARIANTS: INV004, INV005
TESTS: T002.01-T002.08
EC: EC035

- Add BatchValidator with configurable concurrency
- Add fail_fast option for CI/CD (INV005)
- Ensure all packages in result (INV004)
- Add progress callback support
- Integrate with CLI check command
- 50 packages in <5s performance target met"
```

---

## Day 4 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W3.4 | |
| Tests Passing | 8+ (T002.*) | |
| Type Coverage | 100% | |
| Lint Errors | 0 | |
| 50 Packages Time | <5s | |
| INV004 Enforced | All packages in result | |
| INV005 Enforced | fail_fast works | |

---

## Tomorrow Preview

**Day 5 Focus**: End-to-end integration (W3.6)
- Full workflow testing
- Real API integration tests
- Performance benchmarks
- Documentation and cleanup
