"""
SPEC: S060, S065, S070, S075, S080
Performance benchmarks for v0.2.0 signal detection.

Performance Budget:
- All 4 signals combined: < 300ms
- Individual signal: < 100ms each
- gather_all_signals: < 300ms

IMPLEMENTS: Performance validation for new signal detection system
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from phantom_guard.core.signals.combination import gather_all_signals
from phantom_guard.core.signals.downloads import detect_download_inflation
from phantom_guard.core.signals.namespace import detect_namespace_squatting
from phantom_guard.core.signals.ownership import detect_ownership_transfer
from phantom_guard.core.signals.versions import detect_version_spike


@pytest.fixture
def npm_suspicious_metadata() -> dict[str, Any]:
    """Fixture for suspicious npm package metadata."""
    now = datetime.now(UTC)
    return {
        "name": "@fake-corp/suspicious-package",
        "maintainer_count": 1,
        "maintainer_packages": 1,
        "maintainer_age_days": 7,
        "downloads": 100_000,
        "dependents_count": 0,
        "age_days": 30,
        "time": {
            "created": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "modified": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            **{
                f"1.0.{i}": (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
                for i in range(10)
            },
        },
    }


@pytest.fixture
def pypi_suspicious_metadata() -> dict[str, Any]:
    """Fixture for suspicious PyPI package metadata."""
    now = datetime.now(UTC)
    return {
        "name": "netflix-fake-helper",
        "maintainer_count": 1,
        "maintainer_packages": 1,
        "maintainer_age_days": 14,
        "downloads": 50_000,
        "dependents_count": 0,
        "age_days": 45,
        "releases": {
            f"0.0.{i}": [{"upload_time": (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%S")}]
            for i in range(8)
        },
    }


@pytest.fixture
def legitimate_metadata() -> dict[str, Any]:
    """Fixture for legitimate package metadata (no signals should fire)."""
    now = datetime.now(UTC)
    return {
        "name": "normal-package",
        "maintainer_count": 5,
        "maintainer_packages": 100,
        "maintainer_age_days": 2000,
        "downloads": 1_000_000,
        "dependents_count": 500,
        "age_days": 1500,
        "time": {
            f"1.{i}.0": (now - timedelta(weeks=i * 4)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for i in range(10)
        },
    }


@pytest.mark.benchmark
class TestSignalBenchmarks:
    """Performance benchmarks for individual signals.

    Performance Budget:
    - Individual signal: < 100ms each
    """

    def test_namespace_signal_latency(self, benchmark, npm_suspicious_metadata):
        """
        TEST_ID: T060.B01
        SPEC: S060
        BUDGET: < 100ms

        Measures: Namespace squatting detection latency
        """

        def detect_namespace():
            return detect_namespace_squatting(
                "@fake-corp/suspicious-package",
                npm_suspicious_metadata,
                "npm",
            )

        result = benchmark(detect_namespace)

        # Verify detection worked
        assert result is not None
        assert result.namespace == "fake-corp"

        # Budget: < 100ms mean
        assert benchmark.stats.stats.mean < 0.1, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 100ms budget"
        )

    def test_download_signal_latency(self, benchmark, npm_suspicious_metadata):
        """
        TEST_ID: T065.B01
        SPEC: S065
        BUDGET: < 100ms

        Measures: Download inflation detection latency
        """

        def detect_downloads():
            return detect_download_inflation(
                "suspicious-package",
                npm_suspicious_metadata,
                "npm",
            )

        result = benchmark(detect_downloads)

        # Verify detection worked
        assert result is not None
        assert result.downloads > 0

        # Budget: < 100ms mean
        assert benchmark.stats.stats.mean < 0.1, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 100ms budget"
        )

    def test_ownership_signal_latency(self, benchmark, npm_suspicious_metadata):
        """
        TEST_ID: T070.B01
        SPEC: S070
        BUDGET: < 100ms

        Measures: Ownership transfer detection latency
        """

        def detect_ownership():
            return detect_ownership_transfer(
                "suspicious-package",
                npm_suspicious_metadata,
                "npm",
            )

        result = benchmark(detect_ownership)

        # Verify detection worked
        assert result is not None
        assert result.maintainer_count == 1

        # Budget: < 100ms mean
        assert benchmark.stats.stats.mean < 0.1, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 100ms budget"
        )

    def test_version_signal_latency(self, benchmark, npm_suspicious_metadata):
        """
        TEST_ID: T075.B01
        SPEC: S075
        BUDGET: < 100ms

        Measures: Version spike detection latency
        """

        def detect_version():
            return detect_version_spike(
                "suspicious-package",
                npm_suspicious_metadata,
                "npm",
            )

        result = benchmark(detect_version)

        # Verify detection worked
        assert result is not None
        assert result.versions_24h >= 5

        # Budget: < 100ms mean
        assert benchmark.stats.stats.mean < 0.1, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 100ms budget"
        )


@pytest.mark.benchmark
class TestCombinedSignalBenchmarks:
    """Performance benchmarks for combined signal detection.

    Performance Budget:
    - All 4 signals combined: < 300ms
    """

    def test_gather_all_signals_latency(self, benchmark, npm_suspicious_metadata):
        """
        TEST_ID: T080.B01
        SPEC: S080
        BUDGET: < 300ms for all 4 signals

        Measures: Combined signal gathering latency
        """

        def gather_signals():
            return gather_all_signals(
                "@fake-corp/suspicious-package",
                npm_suspicious_metadata,
                "npm",
            )

        result = benchmark(gather_signals)

        # Verify at least some signals fired
        assert result is not None
        assert len(result.signals_collected) > 0
        assert result.total_weight > 0

        # Budget: < 300ms mean for all 4 signals
        assert benchmark.stats.stats.mean < 0.3, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 300ms budget"
        )

    def test_gather_all_signals_pypi(self, benchmark, pypi_suspicious_metadata):
        """
        TEST_ID: T080.B02
        SPEC: S080
        BUDGET: < 300ms for all 4 signals (PyPI format)

        Measures: Combined signal gathering with PyPI metadata format
        """

        def gather_signals_pypi():
            return gather_all_signals(
                "netflix-fake-helper",
                pypi_suspicious_metadata,
                "pypi",
            )

        result = benchmark(gather_signals_pypi)

        # Verify detection worked
        assert result is not None
        assert len(result.signals_collected) >= 2  # At least namespace + version

        # Budget: < 300ms mean
        assert benchmark.stats.stats.mean < 0.3, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 300ms budget"
        )

    def test_gather_signals_legitimate_package(self, benchmark, legitimate_metadata):
        """
        TEST_ID: T080.B03
        SPEC: S080
        BUDGET: < 300ms even for legitimate packages

        Measures: Signal gathering latency for legitimate packages (no signals fire)
        """

        def gather_signals_legitimate():
            return gather_all_signals(
                "normal-package",
                legitimate_metadata,
                "npm",
            )

        result = benchmark(gather_signals_legitimate)

        # Verify no signals fired
        assert result is not None
        assert len(result.signals_collected) == 0
        assert result.total_weight == 0.0

        # Budget: < 300ms mean even when checking all signals
        assert benchmark.stats.stats.mean < 0.3, (
            f"Mean latency {benchmark.stats.stats.mean * 1000:.2f}ms exceeds 300ms budget"
        )

    def test_gather_signals_batch(self, benchmark, npm_suspicious_metadata):
        """
        TEST_ID: T080.B04
        SPEC: S080
        BUDGET: 10 packages in < 3s

        Measures: Batch signal gathering throughput
        """
        packages = [
            ("@fake-corp/pkg1", npm_suspicious_metadata),
            ("@fake-corp/pkg2", npm_suspicious_metadata),
            ("@fake-corp/pkg3", npm_suspicious_metadata),
            ("@fake-corp/pkg4", npm_suspicious_metadata),
            ("@fake-corp/pkg5", npm_suspicious_metadata),
            ("@fake-corp/pkg6", npm_suspicious_metadata),
            ("@fake-corp/pkg7", npm_suspicious_metadata),
            ("@fake-corp/pkg8", npm_suspicious_metadata),
            ("@fake-corp/pkg9", npm_suspicious_metadata),
            ("@fake-corp/pkg10", npm_suspicious_metadata),
        ]

        def gather_batch():
            results = []
            for pkg_name, metadata in packages:
                results.append(gather_all_signals(pkg_name, metadata, "npm"))
            return results

        results = benchmark(gather_batch)

        # Verify all processed
        assert len(results) == 10
        assert all(r is not None for r in results)

        # Budget: < 3s for 10 packages (300ms each)
        assert benchmark.stats.stats.mean < 3.0, (
            f"Mean latency {benchmark.stats.stats.mean:.2f}s exceeds 3s budget for 10 packages"
        )


@pytest.mark.benchmark
class TestSignalMemoryBenchmarks:
    """Memory usage benchmarks for signals."""

    def test_signal_dataclass_size(self, benchmark, npm_suspicious_metadata):
        """
        TEST_ID: T080.B05
        SPEC: S080

        Measures: Memory footprint of signal objects
        """
        import sys

        def create_signals():
            # Create all signal types
            signals = []
            ns = detect_namespace_squatting("@fake-corp/pkg", npm_suspicious_metadata, "npm")
            if ns:
                signals.append(ns)
            dl = detect_download_inflation("pkg", npm_suspicious_metadata, "npm")
            if dl:
                signals.append(dl)
            ow = detect_ownership_transfer("pkg", npm_suspicious_metadata, "npm")
            if ow:
                signals.append(ow)
            vs = detect_version_spike("pkg", npm_suspicious_metadata, "npm")
            if vs:
                signals.append(vs)
            return signals

        results = benchmark(create_signals)

        # Verify signals created
        assert len(results) > 0

        # Check approximate size (frozen dataclasses with slots are compact)
        for signal in results:
            size = sys.getsizeof(signal)
            # Signal objects should be small (< 500 bytes each)
            assert size < 500, f"Signal {type(signal).__name__} is {size} bytes"
