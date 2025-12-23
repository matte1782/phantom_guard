"""PyPI package registry client.

Fetches package metadata from https://pypi.org/pypi/{package}/json
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

import httpx

from phantom_guard.core.types import PackageMetadata, Registry
from phantom_guard.registry.base import RegistryClient, RegistryError

logger = logging.getLogger(__name__)


class PyPIClient(RegistryClient):
    """Client for PyPI package registry.

    Usage:
        async with PyPIClient() as client:
            metadata = await client.fetch_metadata("flask")
            if metadata.exists:
                print(f"Found {metadata.release_count} releases")
    """

    registry: ClassVar[Registry] = Registry.PYPI
    base_url: ClassVar[str] = "https://pypi.org/pypi"

    async def package_exists(self, package_name: str) -> bool:
        """Check if package exists on PyPI using HEAD request.

        Args:
            package_name: Name of the package to check.

        Returns:
            True if package exists, False otherwise.
        """
        name = self.validate_package_name(package_name)
        url = f"{self.base_url}/{name}/json"

        try:
            response = await self.client.head(url)
            return response.status_code == 200
        except httpx.HTTPError as e:
            logger.warning("Error checking %s: %s", name, e)
            return False

    async def fetch_metadata(self, package_name: str) -> PackageMetadata:
        """Fetch package metadata from PyPI.

        Args:
            package_name: Name of the package to fetch.

        Returns:
            PackageMetadata with exists=False if package not found.

        Raises:
            RegistryError: On network/API errors.
            ValueError: If package name is invalid.
        """
        name = self.validate_package_name(package_name)
        url = f"{self.base_url}/{name}/json"

        try:
            response = await self.client.get(url)
        except httpx.TimeoutException as e:
            logger.warning("Timeout fetching %s from PyPI", name)
            raise RegistryError(
                f"Timeout fetching package: {name}",
                package=name,
                registry="pypi",
            ) from e
        except httpx.HTTPError as e:
            logger.error("HTTP error fetching %s: %s", name, e)
            raise RegistryError(
                f"HTTP error fetching package: {name}",
                package=name,
                registry="pypi",
            ) from e

        if response.status_code == 404:
            logger.debug("Package %s not found on PyPI", name)
            return PackageMetadata(
                name=name,
                registry=Registry.PYPI,
                exists=False,
            )

        if response.status_code != 200:
            raise RegistryError(
                f"Unexpected status {response.status_code} for {name}",
                package=name,
                registry="pypi",
            )

        try:
            data = response.json()
        except ValueError as e:
            raise RegistryError(
                f"Invalid JSON response for {name}",
                package=name,
                registry="pypi",
            ) from e

        return self._parse_response(name, data)

    def _parse_response(self, name: str, data: dict[str, Any]) -> PackageMetadata:
        """Parse PyPI JSON response into PackageMetadata.

        Args:
            name: Package name.
            data: Parsed JSON response from PyPI.

        Returns:
            PackageMetadata populated from response.
        """
        info = data.get("info", {})
        releases = data.get("releases", {})

        # Extract repository URL from project_urls
        has_repo = self._has_repository_url(info)

        # Check for author information
        has_author = bool(
            info.get("author")
            or info.get("author_email")
            or info.get("maintainer")
            or info.get("maintainer_email")
        )

        # Check for meaningful description
        description = info.get("description") or info.get("summary") or ""
        has_description = len(description.strip()) > 20

        return PackageMetadata(
            name=name,
            registry=Registry.PYPI,
            exists=True,
            release_count=len(releases),
            has_repository=has_repo,
            has_author=has_author,
            has_description=has_description,
        )

    def _has_repository_url(self, info: dict[str, Any]) -> bool:
        """Check if package info contains a repository URL.

        Looks for GitHub, GitLab, Bitbucket, or similar URLs.

        Args:
            info: Package info dict from PyPI response.

        Returns:
            True if a repository URL is found.
        """
        # Check project_urls
        project_urls = info.get("project_urls") or {}
        for url in project_urls.values():
            if url and self._is_repo_url(url):
                return True

        # Check home_page as fallback
        home_page = info.get("home_page") or ""
        return bool(self._is_repo_url(home_page))

    def _is_repo_url(self, url: str) -> bool:
        """Check if URL appears to be a code repository.

        Args:
            url: URL to check.

        Returns:
            True if URL looks like a repository.
        """
        url_lower = url.lower()
        repo_hosts = (
            "github.com",
            "gitlab.com",
            "bitbucket.org",
            "codeberg.org",
            "sr.ht",
            "gitea.",
            "forgejo.",
        )
        return any(host in url_lower for host in repo_hosts)
