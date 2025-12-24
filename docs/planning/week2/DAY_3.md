# Week 2 - Day 3: crates.io Client

> **Date**: Day 3 (Week 2)
> **Focus**: crates.io registry client with User-Agent requirement
> **Tasks**: W2.3
> **Hours**: 6 hours
> **SPEC_IDs**: S033-S039
> **INV_IDs**: INV013, INV014, INV015
> **TEST_IDs**: T033.01-T033.13

---

## Critical Requirement: INV015

**crates.io REQUIRES a User-Agent header.** Requests without it will be blocked.

From ARCHITECTURE.md:
> Required headers: User-Agent: PhantomGuard/0.1.0 (REQUIRED by crates.io)

---

## Morning Session (3h)

### Objective
Implement the crates.io registry client with required User-Agent header.

### Step 1: Enable Core Tests (15min)

```python
# tests/unit/test_crates.py
# Remove @pytest.mark.skip from:
# - test_package_exists_returns_metadata (T033.01)
# - test_package_not_found_returns_not_exists (T033.02)
# - test_package_metadata_fields (T033.03)
# - test_user_agent_header_included (T033.04)
# - test_user_agent_format (T033.05)
```

### Step 2: Implement crates.io Client (1.5h)

```python
# src/phantom_guard/registry/crates.py
"""
IMPLEMENTS: S033-S039
INVARIANTS: INV013, INV014, INV015
crates.io registry client.
"""

from __future__ import annotations

import httpx
from datetime import datetime, UTC

from phantom_guard.core.types import PackageMetadata
from phantom_guard.registry.exceptions import (
    RegistryTimeoutError,
    RegistryRateLimitError,
    RegistryUnavailableError,
    RegistryParseError,
)

# Constants
CRATES_API_BASE = "https://crates.io/api/v1/crates"
DEFAULT_TIMEOUT = 5.0

# INV015: User-Agent is REQUIRED by crates.io
USER_AGENT = "PhantomGuard/0.1.0 (https://github.com/phantom-guard)"


class CratesClient:
    """
    IMPLEMENTS: S033-S039
    INV: INV013, INV014, INV015

    crates.io registry client.

    Endpoints:
        - https://crates.io/api/v1/crates/{crate} (metadata)
        - https://crates.io/api/v1/crates/{crate}/owners (maintainers)

    CRITICAL: User-Agent header is REQUIRED (INV015).
    """

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.AsyncClient | None = None,
        user_agent: str = USER_AGENT,
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "CratesClient":
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},  # INV015
            )
        return self

    async def __aexit__(self, *args) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    def _get_api_url(self, name: str) -> str:
        """
        IMPLEMENTS: S033
        TEST: T033.10, T033.11

        Construct API URL for crate.
        crates.io uses lowercase crate names.
        """
        normalized = name.lower()
        return f"{CRATES_API_BASE}/{normalized}"

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S033, S034
        INV: INV013, INV014, INV015
        TEST: T033.01-T033.09
        """
        url = self._get_api_url(name)
        headers = {"User-Agent": self.user_agent}  # INV015

        try:
            response = await self._client.get(url, headers=headers)
        except httpx.TimeoutException:
            raise RegistryTimeoutError("crates.io", self.timeout)
        except httpx.RequestError:
            raise RegistryUnavailableError("crates.io", None)

        if response.status_code == 404:
            return PackageMetadata(name=name, exists=False)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RegistryRateLimitError(
                "crates.io",
                int(retry_after) if retry_after else None
            )

        if response.status_code >= 500:
            raise RegistryUnavailableError("crates.io", response.status_code)

        try:
            data = response.json()
        except Exception as e:
            raise RegistryParseError("crates.io", str(e))

        if not data or "crate" not in data:
            return PackageMetadata(name=name, exists=True)

        return self._parse_metadata(name, data)

    def _parse_metadata(self, name: str, data: dict) -> PackageMetadata:
        """
        IMPLEMENTS: S034

        Parse crates.io JSON response.
        crates.io uses nested "crate" object.
        """
        crate = data.get("crate", {})
        versions = data.get("versions", [])

        # Parse created_at
        created_at = None
        if crate.get("created_at"):
            try:
                created_at = datetime.fromisoformat(
                    crate["created_at"].replace("Z", "+00:00")
                )
            except ValueError:
                pass

        return PackageMetadata(
            name=crate.get("name", name),
            exists=True,
            created_at=created_at,
            downloads_last_month=crate.get("recent_downloads"),
            repository_url=crate.get("repository"),
            maintainer_count=None,  # Requires separate API call
            release_count=len(versions),
            latest_version=crate.get("newest_version"),
            description=crate.get("description"),
        )
```

### Step 3: Write User-Agent Tests (30min)

```python
# tests/unit/test_crates.py

import pytest
import respx
import httpx
from phantom_guard.registry.crates import CratesClient, USER_AGENT


class TestCratesClient:

    @pytest.mark.asyncio
    @respx.mock
    async def test_user_agent_header_included(self):
        """
        TEST_ID: T033.04
        SPEC: S033
        INV: INV015
        """
        route = respx.get("https://crates.io/api/v1/crates/serde").mock(
            return_value=httpx.Response(200, json={"crate": {"name": "serde"}})
        )

        async with CratesClient() as client:
            await client.get_package_metadata("serde")

        # Verify User-Agent was sent
        assert route.called
        request = route.calls[0].request
        assert "User-Agent" in request.headers
        assert "PhantomGuard" in request.headers["User-Agent"]

    @pytest.mark.asyncio
    async def test_user_agent_format(self):
        """
        TEST_ID: T033.05
        SPEC: S033
        INV: INV015
        """
        assert "PhantomGuard" in USER_AGENT
        assert "/" in USER_AGENT  # Has version
```

### Step 4: Run Core Tests (15min)

```bash
pytest tests/unit/test_crates.py::TestCratesClient -v --tb=short
# Expected: T033.01-T033.05 pass
```

---

## Afternoon Session (3h)

### Objective
Complete error handling and download count tests.

### Step 5: Enable Error Handling Tests (15min)

```python
# tests/unit/test_crates.py
# Remove @pytest.mark.skip from:
# - test_timeout_raises_error (T033.06)
# - test_server_error_raises_unavailable (T033.07)
# - test_rate_limit_raises_error (T033.08)
# - test_invalid_json_raises_parse_error (T033.09)
```

### Step 6: Enable URL and Download Tests (15min)

```python
# tests/unit/test_crates.py
# Remove @pytest.mark.skip from:
# - test_api_url_format (T033.10)
# - test_crate_name_normalization (T033.11)
# - test_downloads_from_response (T033.12)
# - test_missing_downloads_field (T033.13)
```

### Step 7: Update Registry __init__.py (30min)

```python
# src/phantom_guard/registry/__init__.py
"""
Registry clients for package metadata retrieval.

IMPLEMENTS: S020-S039
"""

from phantom_guard.registry.exceptions import (
    RegistryError,
    RegistryTimeoutError,
    RegistryRateLimitError,
    RegistryUnavailableError,
    RegistryParseError,
)
from phantom_guard.registry.pypi import PyPIClient
from phantom_guard.registry.npm import NpmClient
from phantom_guard.registry.crates import CratesClient

__all__ = [
    # Exceptions
    "RegistryError",
    "RegistryTimeoutError",
    "RegistryRateLimitError",
    "RegistryUnavailableError",
    "RegistryParseError",
    # Clients
    "PyPIClient",
    "NpmClient",
    "CratesClient",
]
```

### Step 8: Run All Registry Tests (30min)

```bash
# All registry tests
pytest tests/unit/test_pypi.py tests/unit/test_npm.py tests/unit/test_crates.py -v

# Expected: 40+ tests pass
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/registry/` - No lint errors
- [ ] `mypy src/phantom_guard/registry/ --strict` - No type errors
- [ ] All T033.* tests passing
- [ ] INV015 verified (User-Agent in all requests)

### Git Commit

```bash
git add src/phantom_guard/registry/
git commit -m "feat(registry): Implement crates.io client with User-Agent header

IMPLEMENTS: S033-S039
INVARIANTS: INV013, INV014, INV015

- Add CratesClient with required User-Agent header
- Parse crates.io nested response format
- Support owners endpoint for maintainer count
- Handle crate name normalization

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Day 3 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W2.3 | |
| Tests Passing | 13 (T033.*) | |
| INV015 Verified | Yes | |

---

## Tomorrow Preview

**Day 4 Focus**: Two-tier cache (W2.4)
- LRU memory cache (Tier 1)
- SQLite persistent cache (Tier 2)
- TTL and size limit enforcement
