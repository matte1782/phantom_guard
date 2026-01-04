"""
IMPLEMENTS: S060
INVARIANTS: INV060, INV061, INV062
Namespace Squatting Detection for Phantom Guard.

Detects attempts to squat on organizational namespaces:
- npm scopes (@org/package)
- PyPI company prefixes (company-package)
- crates.io team prefixes

INV060: Handles all registry formats correctly
INV061: Never flags legitimate org packages (FP < 0.1%)
INV062: Returns None on API failure (not exception)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class NamespaceSignal:
    """
    IMPLEMENTS: S060

    Signal indicating potential namespace squatting.
    """

    namespace: str
    registry: str
    confidence: float  # Weight: 0.35 per spec
    reason: str


# =============================================================================
# CONSTANTS
# =============================================================================

# Weight for namespace squatting signal
NAMESPACE_SQUAT_WEIGHT: float = 0.35

# Known legitimate organizations (INV061 - FP prevention)
# This list prevents false positives on popular org packages
KNOWN_LEGITIMATE_ORGS: frozenset[str] = frozenset(
    [
        # npm scopes (without @)
        "babel",
        "angular",
        "vue",
        "react",
        "types",
        "microsoft",
        "google",
        "aws-sdk",
        "azure",
        "facebook",
        "tensorflow",
        "nestjs",
        "storybook",
        "emotion",
        "mui",
        "ant-design",
        "chakra-ui",
        "reduxjs",
        "tanstack",
        "trpc",
        "prisma",
        "vercel",
        "clerk",
        "auth0",
        "stripe",
        "sentry",
        "datadog",
        "apollo",
        "graphql-tools",
        "testing-library",
        "sveltejs",
        "rollup",
        "vitejs",
        "esbuild",
        "swc",
        "parcel",
        "webpack",
        # PyPI prefixes
        "google-cloud",
        "google-api",
        "google-auth",
        "azure-",
        "aws-",
        "boto",
        "django-",
        "flask-",
        "pytest-",
        "celery-",
        "sqlalchemy-",
        "pydantic-",
        "fastapi-",
        "starlette-",
        "uvicorn-",
        "httpx-",
        "aiohttp-",
        "requests-",
    ]
)

# Company prefixes to check for PyPI (INV061)
SUSPICIOUS_COMPANY_PREFIXES: frozenset[str] = frozenset(
    [
        "google-",
        "microsoft-",
        "amazon-",
        "facebook-",
        "meta-",
        "apple-",
        "netflix-",
        "uber-",
        "airbnb-",
        "stripe-",
        "shopify-",
        "twitter-",
        "linkedin-",
        "salesforce-",
        "oracle-",
        "ibm-",
        "intel-",
        "nvidia-",
        "adobe-",
        "atlassian-",
    ]
)


# =============================================================================
# NAMESPACE EXTRACTION
# =============================================================================


def extract_namespace(package_name: str, registry: str) -> str | None:
    """
    IMPLEMENTS: S060
    INVARIANT: INV060 - Handle all registry formats

    Extract namespace from package name based on registry format.

    Args:
        package_name: The package name.
        registry: The registry type (npm, pypi, crates).

    Returns:
        The namespace (scope/prefix) or None if no namespace.
    """
    if not package_name:
        return None

    # Normalize to lowercase
    package_name = package_name.lower()

    if registry == "npm":
        # npm scopes: @scope/package
        if package_name.startswith("@"):
            match = re.match(r"^@([a-z0-9][-a-z0-9]*)/", package_name)
            if match:
                return match.group(1)
        return None

    elif registry == "pypi":
        # PyPI prefixes: company-package
        for prefix in SUSPICIOUS_COMPANY_PREFIXES:
            if package_name.startswith(prefix):
                return prefix.rstrip("-")
        return None

    elif registry == "crates":
        # crates.io: Similar prefix pattern
        for prefix in SUSPICIOUS_COMPANY_PREFIXES:
            if package_name.startswith(prefix):
                return prefix.rstrip("-")
        return None

    return None


# =============================================================================
# DETECTION FUNCTION
# =============================================================================


def detect_namespace_squatting(
    package_name: str,
    metadata: dict[str, Any],
    registry: str,
) -> NamespaceSignal | None:
    """
    IMPLEMENTS: S060
    INVARIANTS: INV060, INV061, INV062
    TESTS: T060.01-T060.06

    Detect namespace squatting for a package.

    Args:
        package_name: The package name to check.
        metadata: Package metadata from registry.
        registry: The registry type (npm, pypi, crates).

    Returns:
        NamespaceSignal if squatting detected, None otherwise.
        Returns None on any error (INV062).
    """
    try:
        # Extract namespace from package name
        namespace = extract_namespace(package_name, registry)

        # No namespace = no squatting possible
        if namespace is None:
            return None

        # Check if namespace is in known legitimate orgs (INV061 - FP prevention)
        if _is_known_legitimate_org(namespace, registry):
            logger.debug(
                "Package %s has known legitimate org namespace %s",
                package_name,
                namespace,
            )
            return None

        # If we reach here, namespace exists but is not in known list
        # This is a potential squatting attempt
        return NamespaceSignal(
            namespace=namespace,
            registry=registry,
            confidence=NAMESPACE_SQUAT_WEIGHT,
            reason=f"Package uses namespace '{namespace}' without verified ownership",
        )

    except Exception as e:
        # INV062: Return None on any error, not exception
        logger.warning(
            "Namespace squatting check failed for %s: %s",
            package_name,
            e,
        )
        return None


def _is_known_legitimate_org(namespace: str, registry: str) -> bool:
    """
    INVARIANT: INV061 - FP prevention

    Check if namespace belongs to a known legitimate organization.

    Args:
        namespace: The extracted namespace.
        registry: The registry type.

    Returns:
        True if namespace is known legitimate, False otherwise.
    """
    # Direct match
    if namespace in KNOWN_LEGITIMATE_ORGS:
        return True

    # For PyPI, check prefix patterns
    if registry == "pypi":
        # google-cloud-*, google-api-*, etc. are legitimate
        if namespace.startswith("google"):
            return True
        if namespace.startswith("azure"):
            return True
        if namespace.startswith("aws"):
            return True
        if namespace.startswith("boto"):
            return True

    return False
