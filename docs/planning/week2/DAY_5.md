# Week 2 - Day 5: Error Handling and Integration

> **Date**: Day 5 (Week 2)
> **Focus**: Error handling, retries, and Week 2 integration
> **Tasks**: W2.5, Week 2 Review
> **Hours**: 6-8 hours
> **SPEC_IDs**: S020+
> **INV_IDs**: INV013, INV014

---

## Morning Session (3h)

### Objective
Implement retry logic with exponential backoff and integrate all Week 2 components.

### Step 1: Implement Retry Decorator (45min)

```python
# src/phantom_guard/registry/retry.py
"""
IMPLEMENTS: S020 (error handling)
Retry logic with exponential backoff.
"""

from __future__ import annotations

import asyncio
import functools
from typing import TypeVar, Callable, Any

from phantom_guard.registry.exceptions import (
    RegistryTimeoutError,
    RegistryRateLimitError,
    RegistryUnavailableError,
)

T = TypeVar("T")

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0  # seconds
DEFAULT_MAX_DELAY = 30.0  # seconds


class RetryConfig:
    """Retry configuration."""

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay


def calculate_delay(
    attempt: int,
    base: float,
    max_delay: float,
    rate_limit_delay: int | None = None,
) -> float:
    """
    Calculate delay for next retry.

    Uses exponential backoff: base * 2^attempt
    Respects rate limit Retry-After if present.
    """
    if rate_limit_delay is not None:
        return float(rate_limit_delay)

    delay = base * (2 ** attempt)
    return min(delay, max_delay)


def with_retry(config: RetryConfig | None = None):
    """
    Decorator for retry logic on registry operations.

    Retries on:
        - RegistryTimeoutError
        - RegistryUnavailableError
        - RegistryRateLimitError (respects retry_after)

    Does NOT retry on:
        - RegistryParseError (no point, same response)
        - Other exceptions
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except RegistryRateLimitError as e:
                    last_exception = e
                    delay = calculate_delay(
                        attempt,
                        config.base_delay,
                        config.max_delay,
                        e.retry_after,
                    )

                except (RegistryTimeoutError, RegistryUnavailableError) as e:
                    last_exception = e
                    delay = calculate_delay(
                        attempt,
                        config.base_delay,
                        config.max_delay,
                    )

                except Exception:
                    # Don't retry other exceptions
                    raise

                # Wait before retry (unless last attempt)
                if attempt < config.max_retries:
                    await asyncio.sleep(delay)

            # All retries exhausted
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic error")

        return wrapper
    return decorator
```

### Step 2: Create Cached Registry Client (1h)

```python
# src/phantom_guard/registry/cached.py
"""
IMPLEMENTS: S020-S039, S040-S049
Registry client with caching layer.
"""

from __future__ import annotations

from phantom_guard.core.types import PackageMetadata, Registry
from phantom_guard.cache.cache import Cache
from phantom_guard.registry.pypi import PyPIClient
from phantom_guard.registry.npm import NpmClient
from phantom_guard.registry.crates import CratesClient
from phantom_guard.registry.retry import with_retry, RetryConfig


class CachedRegistryClient:
    """
    IMPLEMENTS: S020-S039, S040-S049

    Registry client with caching and retry logic.
    This is the primary client for production use.
    """

    def __init__(
        self,
        cache: Cache,
        retry_config: RetryConfig | None = None,
    ):
        self.cache = cache
        self.retry_config = retry_config or RetryConfig()

        self._pypi: PyPIClient | None = None
        self._npm: NpmClient | None = None
        self._crates: CratesClient | None = None

    async def __aenter__(self) -> "CachedRegistryClient":
        self._pypi = PyPIClient()
        self._npm = NpmClient()
        self._crates = CratesClient()

        await self._pypi.__aenter__()
        await self._npm.__aenter__()
        await self._crates.__aenter__()

        return self

    async def __aexit__(self, *args) -> None:
        if self._pypi:
            await self._pypi.__aexit__(*args)
        if self._npm:
            await self._npm.__aexit__(*args)
        if self._crates:
            await self._crates.__aexit__(*args)

    async def get_package_metadata(
        self,
        name: str,
        registry: Registry = "pypi",
    ) -> PackageMetadata:
        """
        Get package metadata with cache.

        Flow:
            1. Check cache
            2. If miss, fetch from registry (with retry)
            3. Cache result
            4. Return metadata
        """
        # Check cache first
        cached = self.cache.get(registry, name)
        if cached is not None:
            return self._dict_to_metadata(cached, name, registry)

        # Fetch from registry
        metadata = await self._fetch_with_retry(name, registry)

        # Cache the result
        self.cache.set(registry, name, self._metadata_to_dict(metadata))

        return metadata

    @with_retry()
    async def _fetch_with_retry(
        self,
        name: str,
        registry: Registry,
    ) -> PackageMetadata:
        """Fetch with retry logic."""
        if registry == "pypi":
            return await self._pypi.get_package_metadata(name)
        elif registry == "npm":
            return await self._npm.get_package_metadata(name)
        else:  # crates
            return await self._crates.get_package_metadata(name)

    def _metadata_to_dict(self, metadata: PackageMetadata) -> dict:
        """Convert metadata to cacheable dict."""
        return {
            "name": metadata.name,
            "exists": metadata.exists,
            "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
            "downloads_last_month": metadata.downloads_last_month,
            "repository_url": metadata.repository_url,
            "maintainer_count": metadata.maintainer_count,
            "release_count": metadata.release_count,
            "latest_version": metadata.latest_version,
            "description": metadata.description,
        }

    def _dict_to_metadata(
        self,
        data: dict,
        name: str,
        registry: Registry,
    ) -> PackageMetadata:
        """Convert cached dict back to metadata."""
        from datetime import datetime

        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])

        return PackageMetadata(
            name=data.get("name", name),
            exists=data.get("exists", True),
            created_at=created_at,
            downloads_last_month=data.get("downloads_last_month"),
            repository_url=data.get("repository_url"),
            maintainer_count=data.get("maintainer_count"),
            release_count=data.get("release_count"),
            latest_version=data.get("latest_version"),
            description=data.get("description"),
        )
```

### Step 3: Write Retry Tests (30min)

```python
# tests/unit/test_retry.py
"""
Tests for retry logic.
"""

import pytest
from unittest.mock import AsyncMock

from phantom_guard.registry.retry import (
    with_retry,
    RetryConfig,
    calculate_delay,
)
from phantom_guard.registry.exceptions import (
    RegistryTimeoutError,
    RegistryRateLimitError,
)


class TestCalculateDelay:

    def test_exponential_backoff(self):
        """Delay doubles each attempt."""
        assert calculate_delay(0, 1.0, 30.0) == 1.0
        assert calculate_delay(1, 1.0, 30.0) == 2.0
        assert calculate_delay(2, 1.0, 30.0) == 4.0
        assert calculate_delay(3, 1.0, 30.0) == 8.0

    def test_max_delay_cap(self):
        """Delay capped at max."""
        assert calculate_delay(10, 1.0, 30.0) == 30.0

    def test_rate_limit_override(self):
        """Rate limit delay takes precedence."""
        assert calculate_delay(0, 1.0, 30.0, rate_limit_delay=60) == 60.0


class TestWithRetry:

    @pytest.mark.asyncio
    async def test_success_no_retry(self):
        """Successful call returns immediately."""
        mock_func = AsyncMock(return_value="success")

        @with_retry()
        async def call():
            return await mock_func()

        result = await call()
        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Timeout triggers retry."""
        mock_func = AsyncMock(
            side_effect=[
                RegistryTimeoutError("test", 5.0),
                "success",
            ]
        )

        config = RetryConfig(base_delay=0.01)  # Fast for testing

        @with_retry(config)
        async def call():
            return await mock_func()

        result = await call()
        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_max_retries_exhausted(self):
        """Raises after max retries."""
        mock_func = AsyncMock(
            side_effect=RegistryTimeoutError("test", 5.0)
        )

        config = RetryConfig(max_retries=2, base_delay=0.01)

        @with_retry(config)
        async def call():
            return await mock_func()

        with pytest.raises(RegistryTimeoutError):
            await call()

        assert mock_func.call_count == 3  # Initial + 2 retries
```

---

## Afternoon Session (3h)

### Objective
Integration testing and Week 2 review.

### Step 4: Create Integration Tests (1h)

```python
# tests/integration/test_registry_integration.py
"""
Integration tests for registry clients.
"""

import pytest
from unittest.mock import patch

from phantom_guard.core.types import PackageMetadata
from phantom_guard.cache.cache import Cache
from phantom_guard.registry.cached import CachedRegistryClient


class TestCachedRegistryClient:

    @pytest.fixture
    def cache(self, tmp_path):
        """Create cache with temp SQLite."""
        cache = Cache(
            sqlite_path=tmp_path / "cache.db",
            memory_max_size=100,
        )
        cache.__enter__()
        yield cache
        cache.__exit__(None, None, None)

    @pytest.mark.asyncio
    async def test_cache_hit_skips_network(self, cache):
        """Cache hit does not call registry."""
        # Pre-populate cache
        cache.set("pypi", "flask", {
            "name": "flask",
            "exists": True,
        })

        async with CachedRegistryClient(cache) as client:
            with patch.object(
                client._pypi,
                'get_package_metadata'
            ) as mock:
                metadata = await client.get_package_metadata("flask", "pypi")

                assert metadata.name == "flask"
                assert metadata.exists is True
                mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_miss_fetches_and_caches(self, cache):
        """Cache miss fetches from registry and caches result."""
        assert cache.get("pypi", "requests") is None

        async with CachedRegistryClient(cache) as client:
            with patch.object(
                client._pypi,
                'get_package_metadata',
                return_value=PackageMetadata(
                    name="requests",
                    exists=True,
                )
            ) as mock:
                metadata = await client.get_package_metadata("requests", "pypi")

                assert metadata.name == "requests"
                mock.assert_called_once()

        # Check it was cached
        assert cache.get("pypi", "requests") is not None
```

### Step 5: Run Full Test Suite (30min)

```bash
# Run all Week 2 tests
pytest tests/unit/test_pypi.py tests/unit/test_npm.py \
       tests/unit/test_crates.py tests/unit/test_cache.py \
       tests/unit/test_retry.py -v

# Run integration tests
pytest tests/integration/test_registry_integration.py -v

# Full coverage
pytest tests/ --cov=phantom_guard.registry --cov=phantom_guard.cache \
       --cov-report=term-missing
```

### Step 6: Week 2 Exit Checklist (30min)

```markdown
## Week 2 Exit Checklist

### Implementation
- [ ] W2.1 PyPI client - COMPLETE
- [ ] W2.2 npm client - COMPLETE
- [ ] W2.3 crates.io client - COMPLETE
- [ ] W2.4 Two-tier cache - COMPLETE
- [ ] W2.5 Error handling - COMPLETE

### Quality
- [ ] All unit tests passing (57+)
- [ ] Integration tests passing
- [ ] mypy --strict passes on registry/ and cache/
- [ ] ruff check passes
- [ ] Coverage >= 90% on registry/ and cache/

### Invariants Verified
- [ ] INV013: Registry returns valid metadata or raises
- [ ] INV014: Timeout honored in all clients
- [ ] INV015: User-Agent sent to crates.io
- [ ] INV016: Cache TTL honored (no stale returns)
- [ ] INV017: Cache size limit enforced
```

### Step 7: Final Code Quality Check (30min)

```bash
# Full quality check
ruff check src/phantom_guard/registry/ src/phantom_guard/cache/ && \
ruff format --check src/phantom_guard/registry/ src/phantom_guard/cache/ && \
mypy src/phantom_guard/registry/ src/phantom_guard/cache/ --strict && \
pytest tests/ --cov=phantom_guard.registry --cov=phantom_guard.cache \
       --cov-fail-under=90
```

---

## End of Day Checklist

### Week 2 Complete

```bash
git add src/phantom_guard/registry/ src/phantom_guard/cache/ tests/
git commit -m "feat(registry): Add retry logic and cached registry client

IMPLEMENTS: S020-S049
INVARIANTS: INV013-INV017

- Add RetryConfig and with_retry decorator
- Add CachedRegistryClient combining all components
- Add integration tests for full flow
- Week 2 complete: Registry clients + cache

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Git Tag

```bash
git tag -a v0.0.2-alpha.1 -m "Week 2 Complete: Registry Clients + Cache"
```

---

## Week 2 Final Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | 5/5 | |
| Unit Tests | 57+ | |
| Integration Tests | 5+ | |
| Coverage | 90%+ | |
| Type Errors | 0 | |
| Lint Errors | 0 | |

---

## Week 3 Preview

**Week 3 Focus**: CLI & Integration

| Day | Task | Description |
|:----|:-----|:------------|
| Day 1 | W3.1 | CLI: validate command + branding |
| Day 2 | W3.2 | CLI: check command (files) |
| Day 3 | W3.3 | CLI: cache management |
| Day 4 | W3.4 | Batch validation (concurrent) |
| Day 5 | W3.5-W3.6 | Output formats + E2E |

---

## Celebration Checkpoint

Week 2 complete! The registry layer is working:

```python
from phantom_guard.cache.cache import Cache
from phantom_guard.registry.cached import CachedRegistryClient

async def main():
    cache = Cache(sqlite_path="cache.db")

    with cache:
        async with CachedRegistryClient(cache) as client:
            # PyPI
            flask = await client.get_package_metadata("flask", "pypi")
            print(f"Flask: {flask.downloads_last_month:,} downloads/month")

            # npm
            express = await client.get_package_metadata("express", "npm")
            print(f"Express: {express.release_count} versions")

            # crates.io
            serde = await client.get_package_metadata("serde", "crates")
            print(f"Serde: {serde.description}")

import asyncio
asyncio.run(main())
```

All three registries are wired up with caching and retry logic!
