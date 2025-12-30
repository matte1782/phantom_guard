# SPEC: S020 - Retry Logic
"""
Unit tests for retry module.

SPEC_IDs: S020
Tests retry logic with exponential backoff.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from phantom_guard.registry.exceptions import (
    RegistryParseError,
    RegistryRateLimitError,
    RegistryTimeoutError,
    RegistryUnavailableError,
)
from phantom_guard.registry.retry import (
    DEFAULT_BASE_DELAY,
    RetryConfig,
    calculate_backoff,
    retry_async,
    with_retry,
)


class TestCalculateBackoff:
    """Tests for backoff calculation."""

    def test_exponential_growth(self) -> None:
        """Backoff grows exponentially."""
        # With no jitter, should be: 1, 2, 4, 8
        delays = [calculate_backoff(i, jitter=0) for i in range(4)]
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0
        assert delays[3] == 8.0

    def test_max_delay_cap(self) -> None:
        """Backoff is capped at max_delay."""
        delay = calculate_backoff(10, base_delay=1.0, max_delay=10.0, jitter=0)
        assert delay == 10.0

    def test_jitter_adds_randomness(self) -> None:
        """Jitter adds randomness to delay."""
        # Run multiple times and check for variation
        delays = [calculate_backoff(1, jitter=0.5) for _ in range(100)]

        # All should be around 2.0 ± 1.0 (50% jitter)
        assert all(1.0 <= d <= 3.0 for d in delays)

        # Should have some variation (not all the same)
        unique_delays = {round(d, 2) for d in delays}
        assert len(unique_delays) > 1

    def test_custom_base_delay(self) -> None:
        """Custom base delay is respected."""
        delay = calculate_backoff(0, base_delay=5.0, jitter=0)
        assert delay == 5.0


class TestWithRetryDecorator:
    """Tests for @with_retry decorator."""

    @pytest.mark.asyncio
    async def test_success_no_retry(self) -> None:
        """Successful call doesn't retry."""
        call_count = 0

        @with_retry(max_retries=3)
        async def success() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await success()

        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retries_on_timeout(self) -> None:
        """
        EC: EC022

        Retries on timeout errors.
        """
        call_count = 0

        @with_retry(max_retries=3, base_delay=0.01)
        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RegistryTimeoutError("pypi", 5.0)
            return "ok"

        result = await flaky()

        assert result == "ok"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retries_on_unavailable(self) -> None:
        """
        EC: EC023, EC024

        Retries on server unavailable errors.
        """
        call_count = 0

        @with_retry(max_retries=3, base_delay=0.01)
        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RegistryUnavailableError("pypi", 503)
            return "ok"

        result = await flaky()

        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_rate_limit_respects_retry_after(self) -> None:
        """
        EC: EC025

        Rate limit errors respect Retry-After header.
        """
        call_count = 0
        sleep_times: list[float] = []

        @with_retry(max_retries=3, base_delay=1.0)
        async def rate_limited() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RegistryRateLimitError("pypi", retry_after=2)
            return "ok"

        # Patch asyncio.sleep to capture delay
        original_sleep = asyncio.sleep

        async def mock_sleep(delay: float) -> None:
            sleep_times.append(delay)
            await original_sleep(0.001)  # Actually sleep tiny amount

        with patch("phantom_guard.registry.retry.asyncio.sleep", mock_sleep):
            result = await rate_limited()

        assert result == "ok"
        assert call_count == 2
        # Should use retry_after value (2), not exponential backoff
        assert sleep_times[0] == 2.0

    @pytest.mark.asyncio
    async def test_no_retry_on_parse_error(self) -> None:
        """
        EC: EC026

        Parse errors are not retried (indicates API change).
        """
        call_count = 0

        @with_retry(max_retries=3, base_delay=0.01)
        async def parse_fails() -> str:
            nonlocal call_count
            call_count += 1
            raise RegistryParseError("pypi", "invalid JSON")

        with pytest.raises(RegistryParseError):
            await parse_fails()

        # Should not retry - only 1 call
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_exhausted_retries_raises(self) -> None:
        """After max retries, original exception is raised."""

        @with_retry(max_retries=2, base_delay=0.01)
        async def always_fails() -> str:
            raise RegistryTimeoutError("pypi", 5.0)

        with pytest.raises(RegistryTimeoutError):
            await always_fails()

    @pytest.mark.asyncio
    async def test_preserves_function_metadata(self) -> None:
        """Decorator preserves function name and docstring."""

        @with_retry()
        async def my_function() -> str:
            """My docstring."""
            return "ok"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."


class TestRetryAsync:
    """Tests for retry_async function."""

    @pytest.mark.asyncio
    async def test_success_no_retry(self) -> None:
        """Successful call doesn't retry."""
        mock = AsyncMock(return_value="ok")

        result = await retry_async(mock)

        assert result == "ok"
        assert mock.call_count == 1

    @pytest.mark.asyncio
    async def test_retries_on_failure(self) -> None:
        """Retries on transient failures."""
        call_count = 0

        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RegistryTimeoutError("npm", 5.0)
            return "ok"

        result = await retry_async(flaky, max_retries=3, base_delay=0.01)

        assert result == "ok"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_rate_limit_with_retry_after(self) -> None:
        """Rate limit with Retry-After is respected in retry_async."""
        call_count = 0

        async def rate_limited() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RegistryRateLimitError("pypi", retry_after=1)
            return "ok"

        # Patch sleep to avoid actual waiting
        with patch("phantom_guard.registry.retry.asyncio.sleep", AsyncMock()):
            result = await retry_async(rate_limited, max_retries=3, base_delay=0.01)

        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_rate_limit_without_retry_after(self) -> None:
        """Rate limit without Retry-After uses exponential backoff."""
        call_count = 0

        async def rate_limited() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RegistryRateLimitError("pypi", retry_after=None)
            return "ok"

        with patch("phantom_guard.registry.retry.asyncio.sleep", AsyncMock()):
            result = await retry_async(rate_limited, max_retries=3, base_delay=0.01)

        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_exhausted_retries_raises(self) -> None:
        """After exhausted retries, exception is raised."""

        async def always_fails() -> str:
            raise RegistryUnavailableError("pypi", 503)

        with (
            patch("phantom_guard.registry.retry.asyncio.sleep", AsyncMock()),
            pytest.raises(RegistryUnavailableError),
        ):
            await retry_async(always_fails, max_retries=2, base_delay=0.01)

    @pytest.mark.asyncio
    async def test_exhausted_rate_limit_raises(self) -> None:
        """After exhausted rate limit retries, exception is raised."""

        async def always_rate_limited() -> str:
            raise RegistryRateLimitError("pypi", retry_after=1)

        with (
            patch("phantom_guard.registry.retry.asyncio.sleep", AsyncMock()),
            pytest.raises(RegistryRateLimitError),
        ):
            await retry_async(always_rate_limited, max_retries=2, base_delay=0.01)


class TestRetryConfig:
    """Tests for RetryConfig class."""

    def test_default_config(self) -> None:
        """Default config has expected values."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == DEFAULT_BASE_DELAY
        assert config.enabled is True

    def test_custom_config(self) -> None:
        """Custom config is respected."""
        config = RetryConfig(max_retries=5, base_delay=2.0, enabled=False)
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.enabled is False

    @pytest.mark.asyncio
    async def test_disabled_config_no_retry(self) -> None:
        """Disabled config doesn't add retry logic."""
        config = RetryConfig(enabled=False)
        decorator = config.decorator()

        call_count = 0

        @decorator
        async def should_not_retry() -> str:
            nonlocal call_count
            call_count += 1
            raise RegistryTimeoutError("pypi", 5.0)

        with pytest.raises(RegistryTimeoutError):
            await should_not_retry()

        # Should not retry when disabled
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_enabled_config_with_retry(self) -> None:
        """Enabled config adds retry logic."""
        config = RetryConfig(max_retries=2, base_delay=0.01)
        decorator = config.decorator()

        call_count = 0

        @decorator
        async def should_retry() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RegistryTimeoutError("pypi", 5.0)
            return "ok"

        result = await should_retry()

        assert result == "ok"
        assert call_count == 2


class TestExponentialBackoffTiming:
    """Tests for exponential backoff timing behavior."""

    @pytest.mark.asyncio
    async def test_backoff_delays_increase(self) -> None:
        """Verify delays actually increase with each retry."""
        sleep_times: list[float] = []

        @with_retry(max_retries=4, base_delay=0.1, jitter=0)
        async def always_fails() -> str:
            raise RegistryTimeoutError("pypi", 5.0)

        async def mock_sleep(delay: float) -> None:
            sleep_times.append(delay)

        with (
            patch("phantom_guard.registry.retry.asyncio.sleep", mock_sleep),
            pytest.raises(RegistryTimeoutError),
        ):
            await always_fails()

        # Should have 4 sleep calls (before retries 1, 2, 3, 4)
        assert len(sleep_times) == 4

        # Delays should increase: 0.1, 0.2, 0.4, 0.8
        assert sleep_times[0] == pytest.approx(0.1)
        assert sleep_times[1] == pytest.approx(0.2)
        assert sleep_times[2] == pytest.approx(0.4)
        assert sleep_times[3] == pytest.approx(0.8)
