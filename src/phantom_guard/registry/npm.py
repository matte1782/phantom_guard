"""npm package registry client.

Fetches package metadata from https://registry.npmjs.org/{package}
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

import httpx

from phantom_guard.core.types import PackageMetadata, Registry
from phantom_guard.registry.base import RegistryClient, RegistryError

logger = logging.getLogger(__name__)


class NpmClient(RegistryClient):
    """Client for npm package registry.

    Usage:
        async with NpmClient() as client:
            metadata = await client.fetch_metadata("express")
            if metadata.exists:
                print(f"Found {metadata.release_count} versions")
    """

    registry: ClassVar[Registry] = Registry.NPM
    base_url: ClassVar[str] = "https://registry.npmjs.org"

    async def package_exists(self, package_name: str) -> bool:
        """Check if package exists on npm using HEAD request.

        Args:
            package_name: Name of the package to check.

        Returns:
            True if package exists, False otherwise.
        """
        name = self.validate_package_name(package_name)
        url = f"{self.base_url}/{name}"

        try:
            response = await self.client.head(url)
            return response.status_code == 200
        except httpx.HTTPError as e:
            logger.warning("Error checking %s: %s", name, e)
            return False

    async def fetch_metadata(self, package_name: str) -> PackageMetadata:
        """Fetch package metadata from npm.

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
            logger.warning("Timeout fetching %s from npm", name)
            raise RegistryError(
                f"Timeout fetching package: {name}",
                package=name,
                registry="npm",
            ) from e
        except httpx.HTTPError as e:
            logger.error("HTTP error fetching %s: %s", name, e)
            raise RegistryError(
                f"HTTP error fetching package: {name}",
                package=name,
                registry="npm",
            ) from e

        if response.status_code == 404:
            logger.debug("Package %s not found on npm", name)
            return PackageMetadata(
                name=name,
                registry=Registry.NPM,
                exists=False,
            )

        if response.status_code != 200:
            raise RegistryError(
                f"Unexpected status {response.status_code} for {name}",
                package=name,
                registry="npm",
            )

        try:
            data = response.json()
        except ValueError as e:
            raise RegistryError(
                f"Invalid JSON response for {name}",
                package=name,
                registry="npm",
            ) from e

        return self._parse_response(name, data)

    def _parse_response(self, name: str, data: dict[str, Any]) -> PackageMetadata:
        """Parse npm JSON response into PackageMetadata.

        Args:
            name: Package name.
            data: Parsed JSON response from npm.

        Returns:
            PackageMetadata populated from response.
        """
        versions = data.get("versions", {})

        # Check for repository URL
        repository = data.get("repository", {})
        has_repo = self._has_repository(repository)

        # Check for author/maintainers
        has_author = bool(data.get("author") or data.get("maintainers"))

        # Check for description
        description = data.get("description") or ""
        has_description = len(description.strip()) > 20

        return PackageMetadata(
            name=name,
            registry=Registry.NPM,
            exists=True,
            release_count=len(versions),
            has_repository=has_repo,
            has_author=has_author,
            has_description=has_description,
        )

    def _has_repository(self, repository: dict[str, Any] | str | None) -> bool:
        """Check if package has a valid repository.

        npm repository field can be a string URL or an object with url field.

        Args:
            repository: Repository field from npm response.

        Returns:
            True if a repository is specified.
        """
        if not repository:
            return False

        if isinstance(repository, str):
            return len(repository) > 0

        if isinstance(repository, dict):
            url = repository.get("url", "")
            return len(url) > 0

        return False
