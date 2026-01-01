"""
Unit tests for batch validation.

SPEC: S002
INVARIANTS: INV004, INV005
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from phantom_guard.core.batch import BatchConfig, BatchResult, BatchValidator
from phantom_guard.core.types import PackageRisk, Recommendation


class TestBatchConfig:
    """Tests for BatchConfig dataclass."""

    def test_default_values(self) -> None:
        """Default configuration values are sensible."""
        config = BatchConfig()

        assert config.max_concurrent == 10
        assert config.fail_fast is False
        assert config.timeout_per_package == 30.0
        assert config.retry_count == 2

    def test_custom_values(self) -> None:
        """Custom configuration values are accepted."""
        config = BatchConfig(
            max_concurrent=5,
            fail_fast=True,
            timeout_per_package=60.0,
            retry_count=3,
        )

        assert config.max_concurrent == 5
        assert config.fail_fast is True
        assert config.timeout_per_package == 60.0
        assert config.retry_count == 3

    def test_invalid_max_concurrent_rejected(self) -> None:
        """max_concurrent < 1 is rejected."""
        with pytest.raises(ValueError, match="max_concurrent"):
            BatchConfig(max_concurrent=0)

    def test_invalid_timeout_rejected(self) -> None:
        """timeout_per_package <= 0 is rejected."""
        with pytest.raises(ValueError, match="timeout_per_package"):
            BatchConfig(timeout_per_package=0)

    def test_invalid_retry_count_rejected(self) -> None:
        """retry_count < 0 is rejected."""
        with pytest.raises(ValueError, match="retry_count"):
            BatchConfig(retry_count=-1)


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_empty_result(self) -> None:
        """Empty result has zero counts."""
        result = BatchResult()

        assert result.success_count == 0
        assert result.error_count == 0
        assert result.total_count == 0
        assert result.has_high_risk is False
        assert result.has_suspicious is False

    def test_success_count(self) -> None:
        """success_count returns number of results."""
        result = BatchResult(
            results=[
                PackageRisk(
                    name="pkg1",
                    registry="pypi",
                    exists=True,
                    risk_score=0.1,
                    signals=(),
                    recommendation=Recommendation.SAFE,
                ),
                PackageRisk(
                    name="pkg2",
                    registry="pypi",
                    exists=True,
                    risk_score=0.1,
                    signals=(),
                    recommendation=Recommendation.SAFE,
                ),
            ]
        )

        assert result.success_count == 2
        assert result.total_count == 2

    def test_error_count(self) -> None:
        """error_count returns number of errors."""
        result = BatchResult(
            errors={
                "pkg1": ValueError("test"),
                "pkg2": TimeoutError("timeout"),
            }
        )

        assert result.error_count == 2
        assert result.total_count == 2

    def test_mixed_count(self) -> None:
        """total_count sums success and errors."""
        result = BatchResult(
            results=[
                PackageRisk(
                    name="pkg1",
                    registry="pypi",
                    exists=True,
                    risk_score=0.1,
                    signals=(),
                    recommendation=Recommendation.SAFE,
                )
            ],
            errors={"pkg2": ValueError("test")},
        )

        assert result.success_count == 1
        assert result.error_count == 1
        assert result.total_count == 2

    def test_has_high_risk(self) -> None:
        """has_high_risk detects HIGH_RISK packages."""
        result = BatchResult(
            results=[
                PackageRisk(
                    name="safe",
                    registry="pypi",
                    exists=True,
                    risk_score=0.1,
                    signals=(),
                    recommendation=Recommendation.SAFE,
                ),
                PackageRisk(
                    name="risky",
                    registry="pypi",
                    exists=True,
                    risk_score=0.9,
                    signals=(),
                    recommendation=Recommendation.HIGH_RISK,
                ),
            ]
        )

        assert result.has_high_risk is True

    def test_has_suspicious(self) -> None:
        """has_suspicious detects SUSPICIOUS packages."""
        result = BatchResult(
            results=[
                PackageRisk(
                    name="safe",
                    registry="pypi",
                    exists=True,
                    risk_score=0.1,
                    signals=(),
                    recommendation=Recommendation.SAFE,
                ),
                PackageRisk(
                    name="sus",
                    registry="pypi",
                    exists=True,
                    risk_score=0.5,
                    signals=(),
                    recommendation=Recommendation.SUSPICIOUS,
                ),
            ]
        )

        assert result.has_suspicious is True

    def test_get_by_recommendation(self) -> None:
        """get_by_recommendation filters correctly."""
        result = BatchResult(
            results=[
                PackageRisk(
                    name="safe1",
                    registry="pypi",
                    exists=True,
                    risk_score=0.1,
                    signals=(),
                    recommendation=Recommendation.SAFE,
                ),
                PackageRisk(
                    name="risky",
                    registry="pypi",
                    exists=True,
                    risk_score=0.9,
                    signals=(),
                    recommendation=Recommendation.HIGH_RISK,
                ),
                PackageRisk(
                    name="safe2",
                    registry="pypi",
                    exists=True,
                    risk_score=0.1,
                    signals=(),
                    recommendation=Recommendation.SAFE,
                ),
            ]
        )

        safe_packages = result.get_by_recommendation(Recommendation.SAFE)
        assert len(safe_packages) == 2

        risky_packages = result.get_by_recommendation(Recommendation.HIGH_RISK)
        assert len(risky_packages) == 1


class TestBatchValidator:
    """Tests for BatchValidator class."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock registry client."""
        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        return client

    @pytest.mark.asyncio
    async def test_batch_contains_all_packages(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.01
        INV: INV004

        Result contains all input packages.
        """
        packages = ["flask", "django", "requests"]

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        # Monkeypatch the detector.validate_package function
        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        validator = BatchValidator()
        result = await validator.validate_batch(packages, "pypi", mock_client)

        # INV004: All packages accounted for
        assert result.total_count == len(packages)
        result_names = {r.name for r in result.results}
        assert result_names == set(packages)

    @pytest.mark.asyncio
    async def test_batch_fail_fast_stops(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.02
        INV: INV005

        fail_fast stops on first HIGH_RISK.
        """
        packages = ["safe1", "risky", "safe2", "safe3"]
        call_order: list[str] = []

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            call_order.append(name)
            await asyncio.sleep(0.01)  # Small delay to ensure ordering
            if name == "risky":
                return PackageRisk(
                    name=name,
                    registry="pypi",
                    exists=True,
                    risk_score=0.9,
                    signals=(),
                    recommendation=Recommendation.HIGH_RISK,
                )
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        config = BatchConfig(fail_fast=True, max_concurrent=1)  # Serial for predictable order
        validator = BatchValidator(config=config)
        result = await validator.validate_batch(packages, "pypi", mock_client)

        # Should have stopped after risky
        assert result.was_cancelled is True
        # Risky was detected
        assert any(r.recommendation == Recommendation.HIGH_RISK for r in result.results)

    @pytest.mark.asyncio
    async def test_batch_respects_concurrent_limit(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.03

        Never exceeds max_concurrent.
        """
        packages = ["pkg1", "pkg2", "pkg3", "pkg4", "pkg5"]
        max_concurrent_observed = 0
        current_concurrent = 0
        lock = asyncio.Lock()

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            nonlocal max_concurrent_observed, current_concurrent
            async with lock:
                current_concurrent += 1
                max_concurrent_observed = max(max_concurrent_observed, current_concurrent)
            await asyncio.sleep(0.05)
            async with lock:
                current_concurrent -= 1
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        config = BatchConfig(max_concurrent=2)
        validator = BatchValidator(config=config)
        await validator.validate_batch(packages, "pypi", mock_client)

        # Should never exceed limit
        assert max_concurrent_observed <= 2

    @pytest.mark.asyncio
    async def test_batch_handles_errors_gracefully(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.04

        Errors don't stop other validations.
        """
        packages = ["good1", "error_pkg", "good2"]

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            if name == "error_pkg":
                raise ValueError("Test error")
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        validator = BatchValidator()
        result = await validator.validate_batch(packages, "pypi", mock_client)

        # Errors captured, other packages succeeded
        assert len(result.results) == 2
        assert len(result.errors) == 1
        assert "error_pkg" in result.errors

    @pytest.mark.asyncio
    async def test_progress_callback_called(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.05

        Progress callback is called for each package.
        """
        packages = ["pkg1", "pkg2", "pkg3"]
        progress_calls: list[tuple[int, int]] = []

        def on_progress(done: int, total: int) -> None:
            progress_calls.append((done, total))

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        validator = BatchValidator()
        await validator.validate_batch(
            packages,
            "pypi",
            mock_client,
            on_progress=on_progress,
        )

        # Called for each package
        assert len(progress_calls) == 3
        # Last call should show completion
        totals = [t for _, t in progress_calls]
        assert all(t == 3 for t in totals)

    @pytest.mark.asyncio
    async def test_result_callback_called(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.06

        Result callback is called for each successful result.
        """
        packages = ["pkg1", "pkg2"]
        results_received: list[PackageRisk] = []

        async def on_result(risk: PackageRisk) -> None:
            results_received.append(risk)

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        validator = BatchValidator()
        await validator.validate_batch(
            packages,
            "pypi",
            mock_client,
            on_result=on_result,
        )

        assert len(results_received) == 2

    @pytest.mark.asyncio
    async def test_timeout_handled(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.07

        Timeout is handled gracefully.
        """
        packages = ["slow_pkg"]

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            await asyncio.sleep(10)  # Longer than timeout
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        config = BatchConfig(timeout_per_package=0.1)
        validator = BatchValidator(config=config)
        result = await validator.validate_batch(packages, "pypi", mock_client)

        # Timeout captured as error
        assert len(result.errors) == 1
        assert "slow_pkg" in result.errors
        assert isinstance(result.errors["slow_pkg"], TimeoutError)

    @pytest.mark.asyncio
    async def test_total_time_recorded(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Total time is recorded in result."""
        packages = ["pkg1"]

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            await asyncio.sleep(0.05)
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        validator = BatchValidator()
        result = await validator.validate_batch(packages, "pypi", mock_client)

        # Time should be at least ~50ms (allow some tolerance for CI timing)
        assert result.total_time_ms >= 45

    @pytest.mark.asyncio
    async def test_cancel_method(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Cancel method stops validation."""
        packages = ["pkg1", "pkg2", "pkg3", "pkg4", "pkg5"]

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            await asyncio.sleep(0.1)
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        config = BatchConfig(max_concurrent=1)
        validator = BatchValidator(config=config)

        async def cancel_after_delay() -> None:
            await asyncio.sleep(0.15)
            validator.cancel()

        # Start validation and cancel
        cancel_task = asyncio.create_task(cancel_after_delay())
        result = await validator.validate_batch(packages, "pypi", mock_client)
        await cancel_task

        # Not all packages should be processed
        assert result.total_count < len(packages)


class TestBatchPerformance:
    """Performance tests for batch validation."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock registry client."""
        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        return client

    @pytest.mark.asyncio
    async def test_batch_50_packages_performance(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.08
        EC: EC035

        50 packages complete in reasonable time with concurrency.
        """
        packages = [f"package-{i}" for i in range(50)]

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            await asyncio.sleep(0.02)  # 20ms per package
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        config = BatchConfig(max_concurrent=10)
        validator = BatchValidator(config=config)
        result = await validator.validate_batch(packages, "pypi", mock_client)

        # With 10 concurrent, 50 packages x 20ms = ~100ms theoretical minimum
        # Allow generous margin for test environment
        assert result.total_time_ms < 5000  # Under 5 seconds
        assert result.total_count == 50


class TestBatchValidatorEdgeCases:
    """Edge case tests for BatchValidator."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock registry client."""
        client = MagicMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        return client

    @pytest.mark.asyncio
    async def test_cancel_before_start(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.09

        Test cancellation before validation starts.
        """
        packages = ["pkg1", "pkg2", "pkg3"]

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            await asyncio.sleep(0.5)  # Long delay
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        config = BatchConfig(max_concurrent=1)
        validator = BatchValidator(config=config)

        # Cancel immediately after starting
        async def cancel_quickly() -> None:
            await asyncio.sleep(0.01)
            validator.cancel()

        cancel_task = asyncio.create_task(cancel_quickly())
        result = await validator.validate_batch(packages, "pypi", mock_client)
        await cancel_task

        # Some packages should be skipped due to early cancel
        assert result.total_count < len(packages)

    @pytest.mark.asyncio
    async def test_progress_callback_on_timeout(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.10

        Progress callback is called even when packages timeout.
        """
        packages = ["slow_pkg"]
        progress_calls: list[tuple[int, int]] = []

        def on_progress(done: int, total: int) -> None:
            progress_calls.append((done, total))

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            await asyncio.sleep(10)  # Longer than timeout
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        config = BatchConfig(timeout_per_package=0.1)
        validator = BatchValidator(config=config)
        result = await validator.validate_batch(
            packages,
            "pypi",
            mock_client,
            on_progress=on_progress,
        )

        # Progress should be called for timeout
        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 1)
        # Package should be in errors
        assert "slow_pkg" in result.errors

    @pytest.mark.asyncio
    async def test_progress_callback_on_error(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.11

        Progress callback is called even when packages error.
        """
        packages = ["error_pkg"]
        progress_calls: list[tuple[int, int]] = []

        def on_progress(done: int, total: int) -> None:
            progress_calls.append((done, total))

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            raise RuntimeError("Simulated error")

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        validator = BatchValidator()
        result = await validator.validate_batch(
            packages,
            "pypi",
            mock_client,
            on_progress=on_progress,
        )

        # Progress should be called for error
        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 1)
        # Package should be in errors
        assert "error_pkg" in result.errors

    @pytest.mark.asyncio
    async def test_sync_result_callback(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.12

        Sync result callback is handled correctly.
        """
        packages = ["pkg1"]
        results_received: list[PackageRisk] = []

        def on_result(risk: PackageRisk) -> None:
            results_received.append(risk)

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        validator = BatchValidator()
        await validator.validate_batch(
            packages,
            "pypi",
            mock_client,
            on_result=on_result,
        )

        assert len(results_received) == 1

    @pytest.mark.asyncio
    async def test_cancel_method_before_validation(
        self, mock_client: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        TEST_ID: T002.13

        Cancel method before validation starts does nothing.
        """
        validator = BatchValidator()

        # Cancel before any validation - should not raise
        validator.cancel()

        # Should still work after that
        packages = ["pkg1"]

        async def mock_validate(name: str, registry: str, client: MagicMock) -> PackageRisk:
            return PackageRisk(
                name=name,
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

        import phantom_guard.core.detector as detector_module

        monkeypatch.setattr(detector_module, "validate_package", mock_validate)

        result = await validator.validate_batch(packages, "pypi", mock_client)
        assert result.total_count == 1
