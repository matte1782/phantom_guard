"""
Phantom Guard pip Wrapper — Install-time slopsquatting protection.

IMPLEMENTS: S200
"""

__version__ = "0.3.0"

from phantom_pip.errors import (
    ConfigError,
    DelegationError,
    PhantomPipError,
    SecurityError,
    ValidationError,
)

__all__ = [
    "__version__",
    "PhantomPipError",
    "ConfigError",
    "ValidationError",
    "DelegationError",
    "SecurityError",
]
