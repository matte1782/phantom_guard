"""Abstract base class for registry clients.

All registry clients (PyPI, npm, crates.io) implement this interface.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import ClassVar

import httpx

from phantom_guard.core.types import PackageMetadata, Registry

# Package name validation pattern
# Allows alphanumeric, dots, underscores, hyphens
# Must start and end with alphanumeric
PACKAGE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$")
MAX_PACKAGE_NAME_LENGTH = 100


class RegistryError(Exception):
    """Error communicating with package registry.

    Attributes:
        package: Package name that caused the error.
        registry: Registry that was being accessed.
        message: Error description.
    """

    def __init__(
        self,
        message: str,
        package: str | None = None,
        registry: str | None = None,
    ) -> None:
        self.package = package
        self.registry = registry
        self.message = message
        super().__init__(message)


class RegistryClient(ABC):
    """Abstract base class for registry clients.

    Provides async context manager support and input validation.
    Subclasses must implement fetch_metadata and package_exists.

    Usage:
        async with PyPIClient() as client:
            metadata = await client.fetch_metadata("flask")
    """

    registry: ClassVar[Registry]
    base_url: ClassVar[str]
    timeout: float = 10.0

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        """Initialize registry client.

        Args:
            client: Optional httpx client to use. If not provided,
                   a new client will be created and managed.
        """
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> RegistryClient:
        """Enter async context, creating client if needed."""
        if self._owns_client:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit async context, closing client if we own it."""
        if self._owns_client and self._client:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def fetch_metadata(self, package_name: str) -> PackageMetadata:
        """Fetch package metadata from registry.

        Args:
            package_name: Name of the package to look up.

        Returns:
            PackageMetadata with exists=False if package not found.

        Raises:
            RegistryError: On network/API errors.
            ValueError: If package name is invalid.
        """
        ...

    @abstractmethod
    async def package_exists(self, package_name: str) -> bool:
        """Check if package exists in registry.

        This is a faster check than fetch_metadata when you only
        need to know if the package exists.

        Args:
            package_name: Name of the package to check.

        Returns:
            True if package exists, False otherwise.
        """
        ...

    def validate_package_name(self, name: str) -> str:
        """Validate and normalize package name.

        Args:
            name: Package name to validate.

        Returns:
            Normalized package name (lowercase).

        Raises:
            ValueError: If package name is invalid.
        """
        if not name:
            raise ValueError("Package name cannot be empty")

        if len(name) > MAX_PACKAGE_NAME_LENGTH:
            raise ValueError(f"Package name exceeds maximum length of {MAX_PACKAGE_NAME_LENGTH}")

        if not PACKAGE_NAME_PATTERN.match(name):
            raise ValueError(
                f"Invalid package name: {name!r}. "
                "Must contain only alphanumeric characters, dots, underscores, "
                "and hyphens, and must start and end with alphanumeric."
            )

        # Check for path traversal attempts
        if ".." in name or "/" in name or "\\" in name:
            raise ValueError(f"Invalid package name: {name!r}")

        return name.lower()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not in context."""
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client
