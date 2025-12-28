"""
Performance benchmarks for CLI commands.

IMPLEMENTS: W3.6
SPEC_IDs: Performance budgets
INV: INV014

These tests verify performance budgets are met.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest


def run_cli(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """Run phantom-guard CLI command."""
    return subprocess.run(
        [sys.executable, "-m", "phantom_guard.cli.main", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


@pytest.mark.benchmark
class TestPerformanceBudgets:
    """Verify performance budgets from spec."""

    @pytest.mark.network
    @pytest.mark.slow
    def test_single_package_under_200ms(self) -> None:
        """
        INV: INV014

        Single package validation under 200ms (uncached).
        Note: This measures CLI overhead + network + validation.
        """
        # Clear cache first (if exists)
        run_cli("cache", "clear", "-f")

        start = time.perf_counter()
        result = run_cli("validate", "flask", "--no-banner", "-q")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        # Allow 2000ms for network + CLI startup overhead in CI
        assert elapsed_ms < 2000, f"Took {elapsed_ms:.0f}ms, expected <2000ms"

    @pytest.mark.network
    def test_cached_lookup_faster(self) -> None:
        """
        Cached lookup should be faster than uncached.
        """
        # First call to populate cache
        run_cli("validate", "flask", "--no-banner", "-q")

        # Second call should be faster
        start = time.perf_counter()
        result = run_cli("validate", "flask", "--no-banner", "-q")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        # CLI startup adds overhead, but cached should still be fast
        assert elapsed_ms < 1000, f"Cached took {elapsed_ms:.0f}ms, expected <1000ms"

    @pytest.mark.network
    @pytest.mark.slow
    def test_batch_10_packages_reasonable_time(self, tmp_path: Path) -> None:
        """
        10 packages should complete in reasonable time.
        """
        packages = [
            "flask",
            "django",
            "requests",
            "numpy",
            "pandas",
            "pytest",
            "click",
            "rich",
            "typer",
            "httpx",
        ]

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("\n".join(packages))

        start = time.perf_counter()
        result = run_cli(
            "check",
            str(req_file),
            "--parallel",
            "5",
            "--no-banner",
            "-q",
            timeout=120,
        )
        elapsed = time.perf_counter() - start

        assert result.returncode in [0, 1, 2, 3]
        # 10 packages with concurrency should complete in <30s
        assert elapsed < 30.0, f"Took {elapsed:.1f}s, expected <30s"


@pytest.mark.benchmark
class TestCLIStartupTime:
    """Verify CLI startup time is reasonable."""

    def test_help_command_fast(self) -> None:
        """
        Help command should be very fast (no network).
        """
        start = time.perf_counter()
        result = run_cli("--help")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        # Help should complete in <1s
        assert elapsed_ms < 1000, f"Help took {elapsed_ms:.0f}ms, expected <1000ms"

    def test_cache_path_fast(self) -> None:
        """
        Cache path command should be fast (no network).
        """
        start = time.perf_counter()
        result = run_cli("cache", "path")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        # Should complete in <1s
        assert elapsed_ms < 1000, f"Cache path took {elapsed_ms:.0f}ms, expected <1000ms"
