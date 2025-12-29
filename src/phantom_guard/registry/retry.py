"""
IMPLEMENTS: S020 (Error Handling)
INVARIANTS: INV013, INV014
Retry logic with exponential backoff for registry clients.

Provides automatic retry for transient failures:
    - Network timeouts (RegistryTimeoutError)
    - Server errors (RegistryUnavailableError)
    - Rate limits (RegistryRateLimitError) with Retry-After

Does NOT retry:
    - Parse errors (RegistryParseError) - indicates API change
    - 404 responses - legitimate "not found"
"""

from __future__ import annotations

import asyncio
import functools
import random
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from phantom_guard.registry.exceptions import (
    RegistryRateLimitError,
    RegistryTimeoutError,
    RegistryUnavailableError,
)

# Type variables for generic decorator
P = ParamSpec("P")
T = TypeVar("T")

# Exceptions that should trigger retry
RETRYABLE_EXCEPTIONS = (
    RegistryTimeoutError,
    RegistryUnavailableError,
)

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0  # seconds
DEFAULT_MAX_DELAY = 30.0  # seconds
DEFAULT_JITTER = 0.1  # 10% jitter


def calculate_backoff(
    attempt: int,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    jitter: float = DEFAULT_JITTER,
) -> float:
    """
    Calculate exponential backoff delay with jitter.

    Formula: min(base_delay * 2^attempt + random_jitter, max_delay)

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap
        jitter: Jitter factor (0.1 = ±10%)

    Returns:
        Delay in seconds before next retry
    """
    # Exponential backoff: 1, 2, 4, 8, ...
    delay = base_delay * (2**attempt)

    # Add jitter to prevent thundering herd
    # Note: Using standard random is acceptable here - this is for load distribution,
    # not security purposes. Cryptographic randomness is not required.
    jitter_amount = delay * jitter * random.uniform(-1, 1)  # noqa: S311
    delay += jitter_amount

    # Cap at max delay
    return float(min(delay, max_delay))


async def _execute_with_retry(
    func: Callable[[], Awaitable[T]],
    max_retries: int,
    base_delay: float,
    max_delay: float,
    jitter: float,
) -> T:
    """
    Core retry logic - shared implementation.

    This is the single source of truth for retry behavior,
    used by both the decorator and the standalone function.

    Args:
        func: Zero-argument async callable to execute
        max_retries: Maximum retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay cap
        jitter: Jitter factor

    Returns:
        Result of func

    Raises:
        The last exception if all retries are exhausted
    """
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await func()

        except RegistryRateLimitError as e:
            # Respect Retry-After header if present
            if e.retry_after:
                delay = float(e.retry_after)
            else:
                delay = calculate_backoff(attempt, base_delay, max_delay, jitter)

            last_exception = e

            if attempt < max_retries:
                await asyncio.sleep(delay)
            else:
                raise

        except RETRYABLE_EXCEPTIONS as e:
            last_exception = e

            if attempt < max_retries:
                delay = calculate_backoff(attempt, base_delay, max_delay, jitter)
                await asyncio.sleep(delay)
            else:
                raise

    # Should not reach here, but for type checker  # pragma: no cover
    if last_exception:  # pragma: no cover
        raise last_exception  # pragma: no cover
    msg = "Unexpected retry loop exit"  # pragma: no cover
    raise RuntimeError(msg)  # pragma: no cover


def with_retry(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    jitter: float = DEFAULT_JITTER,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    IMPLEMENTS: S020
    INV: INV013

    Decorator for async functions with retry logic.

    Retries on transient failures with exponential backoff.
    Respects Retry-After header from rate limit responses.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries (seconds)
        max_delay: Maximum delay cap (seconds)
        jitter: Jitter factor for delay randomization

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_retries=3)
        async def fetch_data():
            ...
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Wrap the function call in a zero-argument callable
            async def call_func() -> T:
                return await func(*args, **kwargs)

            return await _execute_with_retry(
                call_func,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                jitter=jitter,
            )

        return wrapper

    return decorator


class RetryConfig:
    """
    Configuration for retry behavior.

    Attributes:
        max_retries: Maximum retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay cap
        jitter: Jitter factor
        enabled: Whether retries are enabled
    """

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        jitter: float = DEFAULT_JITTER,
        enabled: bool = True,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.enabled = enabled

    def decorator(self) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
        """Get retry decorator with this config."""
        if not self.enabled:
            # Return identity decorator if disabled
            def identity(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
                return func

            return identity

        return with_retry(
            max_retries=self.max_retries,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            jitter=self.jitter,
        )


async def retry_async(
    func: Callable[[], Awaitable[T]],
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    jitter: float = DEFAULT_JITTER,
) -> T:
    """
    Execute an async function with retry logic.

    Alternative to decorator for one-off use.

    Args:
        func: Async callable to execute (zero-argument)
        max_retries: Maximum retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay cap
        jitter: Jitter factor

    Returns:
        Result of func

    Example:
        result = await retry_async(
            lambda: client.get_package_metadata("flask"),
            max_retries=3
        )
    """
    return await _execute_with_retry(
        func,
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        jitter=jitter,
    )
