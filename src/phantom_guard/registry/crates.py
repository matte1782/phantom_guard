"""
IMPLEMENTS: S033-S039
INVARIANTS: INV013, INV014, INV015
crates.io registry client.
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
CRATES_API_BASE = "https://crates.io/api/v1/crates"
DEFAULT_TIMEOUT = 10.0

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
    ) -> None:
        self.timeout = timeout
        self.user_agent = user_agent
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> CratesClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},  # INV015
            )
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
        IMPLEMENTS: S033
        TEST: T033.10, T033.11

        Construct API URL for crate.
        crates.io uses lowercase crate names.
        """
        normalized = name.lower()
        return f"{CRATES_API_BASE}/{normalized}"

    def _get_owners_url(self, name: str) -> str:
        """
        IMPLEMENTS: S035

        Construct owners API URL for crate.
        """
        normalized = name.lower()
        return f"{CRATES_API_BASE}/{normalized}/owners"

    async def get_package_metadata(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S033, S034
        INV: INV013, INV014, INV015
        TEST: T033.01-T033.09

        Fetch crate metadata from crates.io.
        """
        if self._client is None:
            msg = "Client not initialized. Use 'async with CratesClient()' context."
            raise RuntimeError(msg)

        url = self._get_api_url(name)
        headers = {"User-Agent": self.user_agent}  # INV015

        try:
            response = await self._client.get(url, headers=headers)
        except httpx.TimeoutException as err:
            raise RegistryTimeoutError("crates.io", self.timeout) from err
        except httpx.RequestError as err:
            raise RegistryUnavailableError("crates.io", None) from err

        # Handle status codes
        if response.status_code == 404:
            return PackageMetadata(name=name, exists=False, registry="crates")

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = None
            if retry_after:
                with contextlib.suppress(ValueError):
                    retry_seconds = int(retry_after)
            raise RegistryRateLimitError("crates.io", retry_seconds)

        if response.status_code >= 500:
            raise RegistryUnavailableError("crates.io", response.status_code)

        # Parse JSON
        try:
            data = response.json()
        except Exception as e:
            raise RegistryParseError("crates.io", str(e)) from e

        if not data or "crate" not in data:
            return PackageMetadata(name=name, exists=True, registry="crates")

        return self._parse_metadata(name, data)

    def _parse_metadata(self, name: str, data: dict[str, Any]) -> PackageMetadata:
        """
        IMPLEMENTS: S034

        Parse crates.io JSON response.
        crates.io uses nested "crate" object.
        """
        crate: dict[str, Any] = data.get("crate", {})
        versions: list[dict[str, Any]] = data.get("versions", [])

        # Parse created_at
        created_at = None
        if crate.get("created_at"):
            with contextlib.suppress(ValueError):
                created_at = datetime.fromisoformat(crate["created_at"].replace("Z", "+00:00"))

        # Get downloads - crates.io provides recent_downloads directly
        downloads = crate.get("recent_downloads")
        if downloads is not None and not isinstance(downloads, int):
            downloads = None

        return PackageMetadata(
            name=crate.get("name", name),
            exists=True,
            registry="crates",
            created_at=created_at,
            downloads_last_month=downloads,
            repository_url=crate.get("repository"),
            maintainer_count=None,  # Requires separate API call
            release_count=len(versions),
            latest_version=crate.get("newest_version"),
            description=crate.get("description"),
        )

    async def get_owners(self, name: str) -> int | None:
        """
        IMPLEMENTS: S035
        TEST: T033.14-T033.15

        Fetch owner count from crates.io owners endpoint.
        Returns None if unavailable (graceful degradation).
        """
        if self._client is None:
            return None

        url = self._get_owners_url(name)
        headers = {"User-Agent": self.user_agent}  # INV015

        try:
            response = await self._client.get(url, headers=headers, timeout=2.0)
        except (httpx.TimeoutException, httpx.RequestError):
            return None

        if response.status_code != 200:
            return None

        try:
            data = response.json()
            users = data.get("users", [])
            if isinstance(users, list):
                return len(users)
            return None
        except Exception:
            return None

    async def get_package_metadata_with_owners(self, name: str) -> PackageMetadata:
        """
        IMPLEMENTS: S033, S035

        Fetch crate metadata including owner count.
        Combines crates.io metadata with owners data.
        """
        metadata = await self.get_package_metadata(name)

        if not metadata.exists:
            return metadata

        owner_count = await self.get_owners(name)

        # Create new metadata with owner count (frozen dataclass)
        return PackageMetadata(
            name=metadata.name,
            exists=metadata.exists,
            registry="crates",
            created_at=metadata.created_at,
            downloads_last_month=metadata.downloads_last_month,
            repository_url=metadata.repository_url,
            maintainer_count=owner_count,
            release_count=metadata.release_count,
            latest_version=metadata.latest_version,
            description=metadata.description,
        )
