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

    def __init__(self, registry: str, timeout: float) -> None:
        self.registry = registry
        self.timeout = timeout
        super().__init__(f"{registry} request timed out after {timeout}s")


class RegistryRateLimitError(RegistryError):
    """
    IMPLEMENTS: S020
    EC: EC025

    Registry rate limit exceeded (429 response).
    """

    def __init__(self, registry: str, retry_after: int | None = None) -> None:
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

    def __init__(self, registry: str, status_code: int | None = None) -> None:
        self.registry = registry
        self.status_code = status_code
        super().__init__(f"{registry} unavailable (status: {status_code})")


class RegistryParseError(RegistryError):
    """
    IMPLEMENTS: S020
    EC: EC026

    Registry response could not be parsed.
    """

    def __init__(self, registry: str, reason: str) -> None:
        self.registry = registry
        self.reason = reason
        super().__init__(f"Failed to parse {registry} response: {reason}")
