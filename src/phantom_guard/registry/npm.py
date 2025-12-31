"""
IMPLEMENTS: S027-S032
INVARIANTS: INV013, INV014
npm registry client.
"""

from __future__ import annotations

import contextlib
from datetime import datetime
from typing import Any
from urllib.parse import quote

import httpx

from phantom_guard.core.types import PackageMetadata
from phantom_guard.registry.exceptions import (
    RegistryParseError,
    RegistryRateLimitError,
    RegistryTimeoutError,
    RegistryUnavailableError,
)

# Constants
NPM_REGISTRY_BASE = "https://registry.npmjs.org"
NPM_DOWNLOADS_BASE = "https://api.npmjs.org/downloads/point/last-week"
DEFAULT_TIMEOUT = 10.0
DOWNLOADS_TIMEOUT = 2.0  # Shorter timeout for optional downloads


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
    ) -> None:
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> NpmClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
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

    def _get_downloads_url(self, name: str) -> str:
        """
        IMPLEMENTS: S029

        Construct downloads API URL for package.
        Handles scoped packages.
        """
        if name.startswith("@"):
            encoded = quote(name, safe="@")
            return f"{NPM_DOWNLOADS_BASE}/{encoded}"
        return f"{NPM_DOWNLOADS_BASE}/{name}"

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S027, S028
        INV: INV013, INV014
        TEST: T027.01-T027.08

        Fetch package metadata from npm registry.
        """
        if self._client is None:
            msg = "Client not initialized. Use 'async with NpmClient()' context."
            raise RuntimeError(msg)

        url = self._get_api_url(name)

        try:
            response = await self._client.get(url)
        except httpx.TimeoutException as err:
            raise RegistryTimeoutError("npm", self.timeout) from err
        except httpx.RequestError as err:
            raise RegistryUnavailableError("npm", None) from err

        # Handle status codes
        if response.status_code == 404:
            return PackageMetadata(name=name, exists=False, registry="npm")

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = None
            if retry_after:
                with contextlib.suppress(ValueError):
                    retry_seconds = int(retry_after)
            raise RegistryRateLimitError("npm", retry_seconds)

        if response.status_code >= 500:
            raise RegistryUnavailableError("npm", response.status_code)

        # Parse JSON
        try:
            data = response.json()
        except Exception as e:
            raise RegistryParseError("npm", str(e)) from e

        return self._parse_metadata(name, data)

    def _parse_metadata(self, name: str, data: dict[str, Any]) -> PackageMetadata:
        """
        IMPLEMENTS: S028

        Parse npm registry JSON response.
        npm response format is different from PyPI.
        """
        if not data:
            return PackageMetadata(name=name, exists=True, registry="npm")

        # npm uses "time" object for timestamps
        time_data: dict[str, Any] = data.get("time", {})
        created_at = None
        if "created" in time_data:
            with contextlib.suppress(ValueError):
                created_at = datetime.fromisoformat(time_data["created"].replace("Z", "+00:00"))

        # Get latest version
        dist_tags: dict[str, Any] = data.get("dist-tags", {})
        latest_version = dist_tags.get("latest")

        # Get repository URL
        repository = data.get("repository")
        repository_url = None
        if isinstance(repository, dict):
            raw_url = repository.get("url", "")
            # Clean git+ prefix and .git suffix
            repository_url = raw_url.replace("git+", "").rstrip(".git")
            if repository_url.endswith("."):  # pragma: no cover - defensive, rstrip removes dots
                repository_url = repository_url[:-1]
        elif isinstance(repository, str):
            repository_url = repository

        # Count maintainers and versions
        maintainers: list[dict[str, Any]] = data.get("maintainers", [])
        versions: dict[str, Any] = data.get("versions", {})

        return PackageMetadata(
            name=data.get("name", name),
            exists=True,
            registry="npm",
            created_at=created_at,
            downloads_last_month=None,  # Fetched separately via downloads API
            repository_url=repository_url,
            maintainer_count=len(maintainers),
            release_count=len(versions),
            latest_version=latest_version,
            description=data.get("description"),
        )

    async def get_downloads(self, name: str) -> int | None:
        """
        IMPLEMENTS: S029
        TEST: T027.11-T027.13

        Fetch download count from npm downloads API.
        Returns None if unavailable (graceful degradation).

        Note: npm reports weekly downloads, so multiply by 4 for monthly estimate.
        """
        if self._client is None:
            return None

        url = self._get_downloads_url(name)

        try:
            response = await self._client.get(url, timeout=DOWNLOADS_TIMEOUT)
        except (httpx.TimeoutException, httpx.RequestError):
            return None

        if response.status_code != 200:
            return None

        try:
            data = response.json()
            # npm downloads API returns {"downloads": 12345, "package": "..."}
            downloads = data.get("downloads")
            if isinstance(downloads, int):
                # Multiply by 4 to estimate monthly downloads
                return downloads * 4
            return None
        except Exception:
            return None

    async def get_package_metadata_with_downloads(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S027, S029

        Fetch package metadata including download count.
        Combines npm metadata with downloads data.
        """
        metadata = await self.get_package_metadata(name)

        if not metadata.exists:
            return metadata

        downloads = await self.get_downloads(name)

        # Create new metadata with downloads (frozen dataclass)
        return PackageMetadata(
            name=metadata.name,
            exists=metadata.exists,
            registry="npm",
            created_at=metadata.created_at,
            downloads_last_month=downloads,
            repository_url=metadata.repository_url,
            maintainer_count=metadata.maintainer_count,
            release_count=metadata.release_count,
            latest_version=metadata.latest_version,
            description=metadata.description,
        )
