# Week 2 - Day 2: npm Client

> **Date**: Day 2 (Week 2)
> **Focus**: npm registry client with scoped package support
> **Tasks**: W2.2
> **Hours**: 6 hours
> **SPEC_IDs**: S027-S032
> **INV_IDs**: INV013, INV014
> **TEST_IDs**: T027.01-T027.12

---

## Morning Session (3h)

### Objective
Implement the npm registry client with support for scoped packages and npm-specific API handling.

### Step 1: Enable Core npm Tests (15min)

```python
# tests/unit/test_npm.py
# Remove @pytest.mark.skip from:
# - test_package_exists_returns_metadata (T027.01)
# - test_package_not_found_returns_not_exists (T027.02)
# - test_scoped_package_handled (T027.03)
# - test_package_metadata_fields (T027.04)
```

**Run tests - must FAIL:**
```bash
pytest tests/unit/test_npm.py::TestNpmClient -v
# Expected: ImportError (NpmClient doesn't exist)
```

### Step 2: Implement npm Client Core (1.5h)

```python
# src/phantom_guard/registry/npm.py
"""
IMPLEMENTS: S027-S032
INVARIANTS: INV013, INV014
npm registry client.
"""

from __future__ import annotations

import httpx
from datetime import datetime, UTC
from urllib.parse import quote

from phantom_guard.core.types import PackageMetadata
from phantom_guard.registry.exceptions import (
    RegistryTimeoutError,
    RegistryRateLimitError,
    RegistryUnavailableError,
    RegistryParseError,
)

# Constants
NPM_REGISTRY_BASE = "https://registry.npmjs.org"
NPM_DOWNLOADS_BASE = "https://api.npmjs.org/downloads/point/last-week"
DEFAULT_TIMEOUT = 5.0


class NpmClient:
    """
    IMPLEMENTS: S027-S032
    INV: INV013, INV014

    npm registry client.

    Endpoints:
        - https://registry.npmjs.org/{package} (metadata)
        - https://api.npmjs.org/downloads/point/last-week/{package} (downloads)

    Scoped packages:
        - @scope/name -> /@scope%2Fname
    """

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.AsyncClient | None = None,
    ):
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "NpmClient":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *args) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    def _get_api_url(self, name: str) -> str:
        """
        IMPLEMENTS: S027
        TEST: T027.09, T027.10

        Construct API URL for package.
        Handles scoped packages (@scope/name).
        """
        if name.startswith("@"):
            # Scoped package: @scope/name -> /@scope%2Fname
            encoded = quote(name, safe="@")
            return f"{NPM_REGISTRY_BASE}/{encoded}"
        return f"{NPM_REGISTRY_BASE}/{name}"

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S027, S028
        INV: INV013, INV014
        TEST: T027.01-T027.08
        """
        url = self._get_api_url(name)

        try:
            response = await self._client.get(url)
        except httpx.TimeoutException:
            raise RegistryTimeoutError("npm", self.timeout)
        except httpx.RequestError:
            raise RegistryUnavailableError("npm", None)

        if response.status_code == 404:
            return PackageMetadata(name=name, exists=False)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RegistryRateLimitError(
                "npm",
                int(retry_after) if retry_after else None
            )

        if response.status_code >= 500:
            raise RegistryUnavailableError("npm", response.status_code)

        try:
            data = response.json()
        except Exception as e:
            raise RegistryParseError("npm", str(e))

        return self._parse_metadata(name, data)

    def _parse_metadata(self, name: str, data: dict) -> PackageMetadata:
        """
        IMPLEMENTS: S028

        Parse npm registry JSON response.
        npm response format is different from PyPI.
        """
        # npm uses "time" object for timestamps
        time_data = data.get("time", {})
        created_at = None
        if "created" in time_data:
            try:
                created_at = datetime.fromisoformat(
                    time_data["created"].replace("Z", "+00:00")
                )
            except ValueError:
                pass

        # Get latest version
        dist_tags = data.get("dist-tags", {})
        latest_version = dist_tags.get("latest")

        # Get repository URL
        repository = data.get("repository")
        repository_url = None
        if isinstance(repository, dict):
            repository_url = repository.get("url", "").replace("git+", "").rstrip(".git")
        elif isinstance(repository, str):
            repository_url = repository

        # Count maintainers and versions
        maintainers = data.get("maintainers", [])
        versions = data.get("versions", {})

        return PackageMetadata(
            name=data.get("name", name),
            exists=True,
            created_at=created_at,
            repository_url=repository_url,
            maintainer_count=len(maintainers),
            release_count=len(versions),
            latest_version=latest_version,
            description=data.get("description"),
        )
```

### Step 3: Run Core Tests (15min)

```bash
pytest tests/unit/test_npm.py::TestNpmClient::test_package_exists_returns_metadata -v
pytest tests/unit/test_npm.py::TestNpmClient::test_scoped_package_handled -v
# Expected: Pass
```

### Step 4: Add Scoped Package Test Fixtures (30min)

```python
@pytest.mark.asyncio
@respx.mock
async def test_scoped_package_handled(self):
    """
    TEST_ID: T027.03
    SPEC: S027
    """
    respx.get("https://registry.npmjs.org/@types%2Fnode").mock(
        return_value=httpx.Response(200, json={
            "name": "@types/node",
            "dist-tags": {"latest": "20.10.0"},
            "time": {"created": "2016-07-31T12:00:00Z"},
            "versions": {"20.10.0": {}},
            "maintainers": [{"name": "types"}],
        })
    )

    async with NpmClient() as client:
        metadata = await client.get_package_metadata("@types/node")

    assert metadata.exists is True
    assert metadata.name == "@types/node"
```

---

## Afternoon Session (3h)

### Objective
Complete error handling tests and npm-specific validation tests.

### Step 5: Enable Error Handling Tests (15min)

```python
# tests/unit/test_npm.py
# Remove @pytest.mark.skip from:
# - test_timeout_raises_error (T027.05)
# - test_server_error_raises_unavailable (T027.06)
# - test_rate_limit_raises_error (T027.07)
# - test_invalid_json_raises_parse_error (T027.08)
```

### Step 6: Enable URL and Validation Tests (15min)

```python
# tests/unit/test_npm.py
# Remove @pytest.mark.skip from TestNpmURL and TestNpmNameValidation:
# - test_api_url_format (T027.09)
# - test_scoped_package_url (T027.10)
# - test_leading_number_valid_for_npm (T027.11)
# - test_scoped_package_format_valid (T027.12)
```

### Step 7: Add Downloads Support (45min)

Add `get_downloads()` method that fetches from npm downloads API.

Note: npm reports weekly downloads, so multiply by 4 for monthly estimate.

### Step 8: Run All Tests (30min)

```bash
pytest tests/unit/test_npm.py -v --tb=short
# Expected: 12/12 tests pass
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/registry/npm.py` - No lint errors
- [ ] `mypy src/phantom_guard/registry/npm.py --strict` - No type errors
- [ ] All T027.* tests passing

### Git Commit

```bash
git add src/phantom_guard/registry/npm.py tests/unit/test_npm.py
git commit -m "feat(registry): Implement npm client with scoped package support

IMPLEMENTS: S027-S032
INVARIANTS: INV013, INV014

- Add NpmClient with async HTTP handling
- Support scoped packages (@scope/name)
- Add npm downloads API integration
- Handle npm-specific JSON response format

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Day 2 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W2.2 | |
| Tests Passing | 12 (T027.*) | |
| Type Coverage | 100% | |

---

## Tomorrow Preview

**Day 3 Focus**: crates.io client (W2.3)
- User-Agent header requirement (INV015)
- crates.io API differences
- Separate owners endpoint
