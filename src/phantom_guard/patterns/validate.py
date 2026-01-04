"""
IMPLEMENTS: S059
INVARIANTS: INV059, INV059a
Pattern Validation for Phantom Guard.

Validates patterns before loading to ensure:
- Confidence is in [0.0, 1.0] (INV059)
- Pattern types are valid
- Regex patterns compile
- Patterns don't match popular packages (INV059a - FP prevention)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# TYPES
# =============================================================================


@dataclass
class ValidationResult:
    """
    IMPLEMENTS: S059
    Result of pattern validation.
    """

    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# CONSTANTS
# =============================================================================

# Valid pattern types
VALID_PATTERN_TYPES = {"prefix", "suffix", "compound", "regex"}

# Popular packages that should never be flagged (INV059a - FP prevention)
POPULAR_PACKAGES = frozenset(
    [
        "requests",
        "flask",
        "django",
        "numpy",
        "pandas",
        "pytest",
        "pip",
        "setuptools",
        "wheel",
        "boto3",
        "urllib3",
        "certifi",
        "idna",
        "charset-normalizer",
        "typing-extensions",
        "pyyaml",
        "cryptography",
        "six",
        "python-dateutil",
        "pydantic",
        "httpx",
        "aiohttp",
        "sqlalchemy",
        "pillow",
        "matplotlib",
        "scipy",
        "scikit-learn",
        "tensorflow",
        "torch",
        "keras",
        "beautifulsoup4",
        "lxml",
        "jinja2",
        "click",
        "typer",
        "rich",
        "fastapi",
        "starlette",
        "uvicorn",
        "gunicorn",
        "celery",
        "redis",
        "psycopg2",
        "pymongo",
        "elasticsearch",
    ]
)


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_pattern(pattern: dict[str, Any]) -> ValidationResult:
    """
    IMPLEMENTS: S059
    INVARIANTS: INV059, INV059a
    TESTS: T059.01-T059.06

    Validate a pattern dictionary before loading.

    Args:
        pattern: Pattern dictionary with id, type, confidence, etc.

    Returns:
        ValidationResult with success status and any errors.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Validate required fields
    if "id" not in pattern:
        errors.append("Missing required field: id")

    # Validate confidence (INV059: must be in [0.0, 1.0])
    confidence = pattern.get("confidence")
    if confidence is not None:
        if not isinstance(confidence, (int, float)):
            errors.append(f"Confidence must be a number, got {type(confidence).__name__}")
        elif not 0.0 <= float(confidence) <= 1.0:
            errors.append(f"Confidence must be in [0.0, 1.0], got {confidence}")

    # Validate pattern type
    pattern_type = pattern.get("type")
    if pattern_type is not None and pattern_type not in VALID_PATTERN_TYPES:
        errors.append(
            f"Invalid pattern type: {pattern_type}. "
            f"Valid types: {', '.join(sorted(VALID_PATTERN_TYPES))}"
        )

    # Validate regex if type is regex
    if pattern_type == "regex":
        regex_pattern = pattern.get("pattern")
        if regex_pattern:
            try:
                compiled = re.compile(regex_pattern)
                # Check for false positive risk (INV059a)
                fp_errors = _check_false_positive_risk(compiled)
                errors.extend(fp_errors)
            except re.error as e:
                errors.append(f"Invalid regex pattern: {e}")

    return ValidationResult(
        success=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def _check_false_positive_risk(compiled_regex: re.Pattern[str]) -> list[str]:
    """
    IMPLEMENTS: S059
    INVARIANT: INV059a - Patterns must not match popular packages

    Check if a regex pattern would match any popular packages.

    Args:
        compiled_regex: The compiled regex pattern.

    Returns:
        List of errors if pattern matches popular packages.
    """
    errors: list[str] = []

    for package in POPULAR_PACKAGES:
        if compiled_regex.match(package):
            errors.append(
                f"Pattern matches popular package '{package}' - would cause false positive"
            )
            break  # One match is enough to reject

    return errors
