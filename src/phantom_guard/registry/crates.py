"""crates.io package registry client.

Fetches package metadata from https://crates.io/api/v1/crates/{package}

Note: crates.io requires a User-Agent header.
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

import httpx

from phantom_guard.core.types import PackageMetadata, Registry
from phantom_guard.registry.base import RegistryClient, RegistryError

logger = logging.getLogger(__name__)

# crates.io requires User-Agent header
USER_AGENT = "PhantomGuard/0.1.0 (https://github.com/phantom-guard/phantom-guard)"


class CratesClient(RegistryClient):
    """Client for crates.io package registry.

    Note: crates.io requires a User-Agent header for all requests.

    Usage:
        async with CratesClient() as client:
            metadata = await client.fetch_metadata("serde")
            if metadata.exists:
                print(f"Found {metadata.release_count} versions")
    """

    registry: ClassVar[Registry] = Registry.CRATES
    base_url: ClassVar[str] = "https://crates.io/api/v1/crates"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        """Initialize crates.io client.

        Overridden to add required User-Agent header.

        Args:
            client: Optional httpx client to use.
        """
        super().__init__(client)
        # Will create client with User-Agent in __aenter__
        self._user_agent = USER_AGENT

    async def __aenter__(self) -> CratesClient:
        """Enter async context, creating client with User-Agent."""
        if self._owns_client:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": self._user_agent},
            )
        return self

    async def package_exists(self, package_name: str) -> bool:
        """Check if package exists on crates.io.

        Args:
            package_name: Name of the package to check.

        Returns:
            True if package exists, False otherwise.
        """
        name = self.validate_package_name(package_name)
        url = f"{self.base_url}/{name}"

        try:
            response = await self.client.get(url)
            return response.status_code == 200
        except httpx.HTTPError as e:
            logger.warning("Error checking %s: %s", name, e)
            return False

    async def fetch_metadata(self, package_name: str) -> PackageMetadata:
        """Fetch package metadata from crates.io.

        Args:
            package_name: Name of the package to fetch.

        Returns:
            PackageMetadata with exists=False if package not found.

        Raises:
            RegistryError: On network/API errors.
            ValueError: If package name is invalid.
        """
        name = self.validate_package_name(package_name)
        url = f"{self.base_url}/{name}"

        try:
            response = await self.client.get(url)
        except httpx.TimeoutException as e:
            logger.warning("Timeout fetching %s from crates.io", name)
            raise RegistryError(
                f"Timeout fetching package: {name}",
                package=name,
                registry="crates",
            ) from e
        except httpx.HTTPError as e:
            logger.error("HTTP error fetching %s: %s", name, e)
            raise RegistryError(
                f"HTTP error fetching package: {name}",
                package=name,
                registry="crates",
            ) from e

        if response.status_code == 404:
            logger.debug("Package %s not found on crates.io", name)
            return PackageMetadata(
                name=name,
                registry=Registry.CRATES,
                exists=False,
            )

        if response.status_code != 200:
            raise RegistryError(
                f"Unexpected status {response.status_code} for {name}",
                package=name,
                registry="crates",
            )

        try:
            data = response.json()
        except ValueError as e:
            raise RegistryError(
                f"Invalid JSON response for {name}",
                package=name,
                registry="crates",
            ) from e

        return self._parse_response(name, data)

    def _parse_response(self, name: str, data: dict[str, Any]) -> PackageMetadata:
        """Parse crates.io JSON response into PackageMetadata.

        Args:
            name: Package name.
            data: Parsed JSON response from crates.io.

        Returns:
            PackageMetadata populated from response.
        """
        crate = data.get("crate", {})
        versions = data.get("versions", [])

        # Check for repository URL
        repository = crate.get("repository") or ""
        has_repo = len(repository) > 0

        # crates.io doesn't have explicit author in main response
        # but we can check if there are any owners (would need separate API call)
        # For now, assume has author if package exists
        has_author = True

        # Check for description
        description = crate.get("description") or ""
        has_description = len(description.strip()) > 20

        return PackageMetadata(
            name=name,
            registry=Registry.CRATES,
            exists=True,
            release_count=len(versions),
            has_repository=has_repo,
            has_author=has_author,
            has_description=has_description,
        )
