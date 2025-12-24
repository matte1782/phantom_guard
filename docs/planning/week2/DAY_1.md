# Week 2 - Day 1: PyPI Client

> **Date**: Day 1 (Week 2)
> **Focus**: PyPI registry client + pypistats integration
> **Tasks**: W2.1
> **Hours**: 6-8 hours
> **SPEC_IDs**: S020-S026
> **INV_IDs**: INV013, INV014
> **TEST_IDs**: T020.01-T020.15

---

## Morning Session (3h)

### Objective
Implement the PyPI registry client with proper error handling and pypistats download count integration.

### Step 1: Create Registry Base Classes (45min)

Before implementing PyPI-specific logic, create the shared exception types and base client.

```python
# src/phantom_guard/registry/exceptions.py
"""
IMPLEMENTS: S020
Registry client exceptions.
"""

from __future__ import annotations


class RegistryError(Exception):
    """Base class for registry errors."""
    pass


class RegistryTimeoutError(RegistryError):
    """
    IMPLEMENTS: S020
    INV: INV014

    Registry request timed out.
    """
    def __init__(self, registry: str, timeout: float):
        self.registry = registry
        self.timeout = timeout
        super().__init__(f"{registry} request timed out after {timeout}s")


class RegistryRateLimitError(RegistryError):
    """
    IMPLEMENTS: S020
    EC: EC025

    Registry rate limit exceeded (429 response).
    """
    def __init__(self, registry: str, retry_after: int | None = None):
        self.registry = registry
        self.retry_after = retry_after
        msg = f"{registry} rate limit exceeded"
        if retry_after:
            msg += f", retry after {retry_after}s"
        super().__init__(msg)


class RegistryUnavailableError(RegistryError):
    """
    IMPLEMENTS: S020
    EC: EC023, EC024

    Registry returned 5xx or is unreachable.
    """
    def __init__(self, registry: str, status_code: int | None = None):
        self.registry = registry
        self.status_code = status_code
        super().__init__(f"{registry} unavailable (status: {status_code})")


class RegistryParseError(RegistryError):
    """
    IMPLEMENTS: S020
    EC: EC026

    Registry response could not be parsed.
    """
    def __init__(self, registry: str, reason: str):
        self.registry = registry
        self.reason = reason
        super().__init__(f"Failed to parse {registry} response: {reason}")
```

### Step 2: Enable PyPI Test Stubs (15min)

```python
# tests/unit/test_pypi.py
# Remove @pytest.mark.skip from:
# - test_package_exists_returns_metadata (T020.01)
# - test_package_not_found_returns_not_exists (T020.02)
# - test_package_metadata_fields (T020.03)
```

**Run tests - must FAIL:**
```bash
pytest tests/unit/test_pypi.py::TestPyPIClient::test_package_exists_returns_metadata -v
# Expected: ImportError or NameError (module doesn't exist)
```

### Step 3: Implement PyPI Client Core (1.5h)

```python
# src/phantom_guard/registry/pypi.py
"""
IMPLEMENTS: S020-S026
INVARIANTS: INV013, INV014
PyPI registry client.
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
PYPI_API_BASE = "https://pypi.org/pypi"
PYPISTATS_API_BASE = "https://pypistats.org/api/packages"
DEFAULT_TIMEOUT = 5.0
PYPISTATS_TIMEOUT = 2.0  # Shorter timeout for optional stats


class PyPIClient:
    """
    IMPLEMENTS: S020-S026
    INV: INV013, INV014

    PyPI registry client.

    Endpoints:
        - https://pypi.org/pypi/{package}/json (metadata)
        - https://pypistats.org/api/packages/{package}/recent (downloads)
    """

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.AsyncClient | None = None,
    ):
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "PyPIClient":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *args) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    def _get_api_url(self, name: str) -> str:
        """
        IMPLEMENTS: S020
        TEST: T020.14, T020.15

        Construct API URL for package.
        Normalizes name per PEP 503.
        """
        # PEP 503: lowercase, replace _ with -
        normalized = name.lower().replace("_", "-")
        return f"{PYPI_API_BASE}/{normalized}/json"

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S020, S022
        INV: INV013, INV014
        TEST: T020.01-T020.10

        Fetch package metadata from PyPI.
        """
        url = self._get_api_url(name)

        try:
            response = await self._client.get(url)
        except httpx.TimeoutException:
            raise RegistryTimeoutError("pypi", self.timeout)
        except httpx.RequestError:
            raise RegistryUnavailableError("pypi", None)

        # Handle status codes
        if response.status_code == 404:
            return PackageMetadata(name=name, exists=False)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RegistryRateLimitError(
                "pypi",
                int(retry_after) if retry_after else None
            )

        if response.status_code >= 500:
            raise RegistryUnavailableError("pypi", response.status_code)

        # Parse JSON
        try:
            data = response.json()
        except Exception as e:
            raise RegistryParseError("pypi", str(e))

        return self._parse_metadata(name, data)
```

### Step 4: Run Core Tests (15min)

```bash
pytest tests/unit/test_pypi.py::TestPyPIClient -v --tb=short
# Expected: T020.01, T020.02, T020.03 pass
```

---

## Afternoon Session (3h)

### Objective
Add pypistats integration, error handling tests, and URL construction tests.

### Step 5: Enable Error Handling Tests (15min)

```python
# tests/unit/test_pypi.py
# Remove @pytest.mark.skip from:
# - test_timeout_raises_error (T020.04)
# - test_server_error_raises_unavailable (T020.05)
# - test_gateway_error_raises_unavailable (T020.06)
# - test_rate_limit_raises_error (T020.07)
# - test_invalid_json_raises_parse_error (T020.08)
```

### Step 6: Write Test Fixtures with respx (30min)

```python
# tests/unit/test_pypi.py
import pytest
import respx
import httpx
from phantom_guard.registry.pypi import PyPIClient
from phantom_guard.registry.exceptions import (
    RegistryTimeoutError,
    RegistryRateLimitError,
    RegistryUnavailableError,
    RegistryParseError,
)


@pytest.mark.asyncio
@respx.mock
async def test_timeout_raises_error():
    """
    TEST_ID: T020.04
    SPEC: S020
    INV: INV014
    """
    respx.get("https://pypi.org/pypi/flask/json").mock(
        side_effect=httpx.TimeoutException("timeout")
    )

    async with PyPIClient(timeout=1.0) as client:
        with pytest.raises(RegistryTimeoutError) as exc_info:
            await client.get_package_metadata("flask")

        assert exc_info.value.registry == "pypi"
        assert exc_info.value.timeout == 1.0
```

### Step 7: Implement pypistats Integration (1h)

Add `get_downloads()` and `get_package_metadata_with_downloads()` methods to PyPIClient.

### Step 8: Enable URL Tests and Run All (30min)

```bash
# Run all PyPI tests
pytest tests/unit/test_pypi.py -v --tb=short
# Expected: 15/15 tests pass
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/registry/` - No lint errors
- [ ] `ruff format src/phantom_guard/registry/` - Code formatted
- [ ] `mypy src/phantom_guard/registry/ --strict` - No type errors
- [ ] All T020.* tests passing

### Documentation
- [ ] Exception classes have IMPLEMENTS tags
- [ ] PyPIClient has comprehensive docstrings
- [ ] All public methods have type hints

### Git Commit

```bash
git add src/phantom_guard/registry/
git commit -m "feat(registry): Implement PyPI client with pypistats integration

IMPLEMENTS: S020-S026
INVARIANTS: INV013, INV014

- Add RegistryError base class and subclasses
- Add PyPIClient with async HTTP handling
- Add pypistats.org download count integration
- Handle 404, 429, 5xx responses correctly

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Day 1 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W2.1 | |
| Tests Passing | 15 (T020.*) | |
| Type Coverage | 100% | |
| Lint Errors | 0 | |

---

## Tomorrow Preview

**Day 2 Focus**: npm client (W2.2)
- Similar pattern to PyPI
- Handle scoped packages (@scope/name)
- npm registry API differences
