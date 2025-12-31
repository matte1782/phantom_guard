"""
IMPLEMENTS: S020-S026
INVARIANTS: INV013, INV014
PyPI registry client.
"""

from __future__ import annotations

import contextlib
from datetime import datetime
from typing import Any

import httpx

from phantom_guard.core.types import PackageMetadata
from phantom_guard.registry.exceptions import (
    RegistryParseError,
    RegistryRateLimitError,
    RegistryTimeoutError,
    RegistryUnavailableError,
)

# Constants
PYPI_API_BASE = "https://pypi.org/pypi"
PYPISTATS_API_BASE = "https://pypistats.org/api/packages"
DEFAULT_TIMEOUT = 10.0
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
    ) -> None:
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> PyPIClient:
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
        IMPLEMENTS: S020
        TEST: T020.14, T020.15

        Construct API URL for package.
        Normalizes name per PEP 503.
        """
        # PEP 503: lowercase, replace _ with -
        normalized = name.lower().replace("_", "-")
        return f"{PYPI_API_BASE}/{normalized}/json"

    def _get_pypistats_url(self, name: str) -> str:
        """
        IMPLEMENTS: S023

        Construct pypistats API URL for package.
        """
        normalized = name.lower().replace("_", "-")
        return f"{PYPISTATS_API_BASE}/{normalized}/recent"

    def _find_earliest_upload(self, releases: dict[str, list[dict[str, Any]]]) -> datetime | None:
        """
        Find earliest upload timestamp from releases.

        Optimized: Uses generator expression with min() instead of
        nested loops, efficient for packages with many releases.
        """
        timestamps: list[datetime] = []
        for release_files in releases.values():
            for file_info in release_files:
                upload_time = file_info.get("upload_time")
                if upload_time:
                    with contextlib.suppress(ValueError):
                        parsed = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                        timestamps.append(parsed)
        return min(timestamps) if timestamps else None

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S020, S022
        INV: INV013, INV014
        TEST: T020.01-T020.10

        Fetch package metadata from PyPI.
        """
        if self._client is None:
            msg = "Client not initialized. Use 'async with PyPIClient()' context."
            raise RuntimeError(msg)

        url = self._get_api_url(name)

        try:
            response = await self._client.get(url)
        except httpx.TimeoutException as err:
            raise RegistryTimeoutError("pypi", self.timeout) from err
        except httpx.RequestError as err:
            raise RegistryUnavailableError("pypi", None) from err

        # Handle status codes
        if response.status_code == 404:
            return PackageMetadata(name=name, exists=False, registry="pypi")

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = None
            if retry_after:
                with contextlib.suppress(ValueError):
                    retry_seconds = int(retry_after)
            raise RegistryRateLimitError("pypi", retry_seconds)

        if response.status_code >= 500:
            raise RegistryUnavailableError("pypi", response.status_code)

        # Parse JSON
        try:
            data = response.json()
        except Exception as e:
            raise RegistryParseError("pypi", str(e)) from e

        return self._parse_metadata(name, data)

    def _parse_metadata(self, name: str, data: dict[str, Any]) -> PackageMetadata:
        """
        IMPLEMENTS: S022

        Parse PyPI JSON response.
        """
        if not data:
            return PackageMetadata(name=name, exists=True, registry="pypi")

        info: dict[str, Any] = data.get("info", {})
        releases: dict[str, list[dict[str, Any]]] = data.get("releases", {})

        # Parse created_at from earliest release (optimized with generator)
        created_at = self._find_earliest_upload(releases)

        # Get repository URL
        repository_url = info.get("project_url") or info.get("home_page")
        project_urls = info.get("project_urls") or {}
        if not repository_url:
            repository_url = (
                project_urls.get("Source")
                or project_urls.get("Repository")
                or project_urls.get("Homepage")
            )

        # Get maintainer info
        maintainer = info.get("maintainer") or info.get("author")
        maintainer_count = 1 if maintainer else None

        return PackageMetadata(
            name=info.get("name", name),
            exists=True,
            registry="pypi",
            created_at=created_at,
            downloads_last_month=None,  # Fetched separately via pypistats
            repository_url=repository_url,
            maintainer_count=maintainer_count,
            release_count=len(releases),
            latest_version=info.get("version"),
            description=info.get("summary"),
        )

    async def get_downloads(self, name: str) -> int | None:
        """
        IMPLEMENTS: S023
        TEST: T020.11-T020.13

        Fetch download count from pypistats.org.
        Returns None if unavailable (graceful degradation).
        """
        if self._client is None:
            return None

        url = self._get_pypistats_url(name)

        try:
            response = await self._client.get(url, timeout=PYPISTATS_TIMEOUT)
        except (httpx.TimeoutException, httpx.RequestError):
            return None

        if response.status_code != 200:
            return None

        try:
            data = response.json()
            # pypistats returns {"data": {"last_month": 12345}}
            inner_data = data.get("data", {})
            last_month = inner_data.get("last_month")
            if isinstance(last_month, int):
                return last_month
            return None
        except Exception:
            return None

    async def get_package_metadata_with_downloads(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S020, S023

        Fetch package metadata including download count.
        Combines PyPI metadata with pypistats data.
        """
        metadata = await self.get_package_metadata(name)

        if not metadata.exists:
            return metadata

        downloads = await self.get_downloads(name)

        # Create new metadata with downloads (frozen dataclass)
        return PackageMetadata(
            name=metadata.name,
            exists=metadata.exists,
            registry="pypi",
            created_at=metadata.created_at,
            downloads_last_month=downloads,
            repository_url=metadata.repository_url,
            maintainer_count=metadata.maintainer_count,
            release_count=metadata.release_count,
            latest_version=metadata.latest_version,
            description=metadata.description,
        )
