"""
Error types for phantom-pip wrapper.

IMPLEMENTS: S200
INVARIANTS: INV207 (config parse errors handled gracefully)
"""


class PhantomPipError(Exception):
    """Base exception for phantom-pip."""

    def __init__(self, message: str, recoverable: bool = True) -> None:
        super().__init__(message)
        self.recoverable = recoverable


class ConfigError(PhantomPipError):
    """Configuration file error."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Configuration error: {message}", recoverable=True)


class ValidationError(PhantomPipError):
    """Package validation error."""

    def __init__(self, package: str, reason: str) -> None:
        super().__init__(f"Validation failed for '{package}': {reason}", recoverable=True)
        self.package = package
        self.reason = reason


class DelegationError(PhantomPipError):
    """pip subprocess delegation error."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(f"pip delegation failed: {message}", recoverable=False)
        self.exit_code = exit_code


class SecurityError(PhantomPipError):
    """Security violation detected."""

    def __init__(self, message: str) -> None:
        super().__init__(f"SECURITY: {message}", recoverable=False)
