"""
Allowlist and blocklist management.

IMPLEMENTS: S205
INVARIANTS: INV202 (allowlist always pass), INV203 (blocklist always fail)
TESTS: T205.*
"""

import fnmatch
import re
from typing import Optional


def normalize_package_name(name: str) -> str:
    """
    Normalize package name for comparison.

    PEP 503: Names are case-insensitive and -/_ are equivalent.
    """
    return re.sub(r"[-_.]+", "-", name.lower())


def _matches_pattern(package: str, pattern: str) -> bool:
    """
    Check if package matches a pattern.

    Supports:
    - Exact match: flask
    - Wildcard: flask-*
    - Prefix: flask-* (matches flask-login, flask-wtf)
    - Suffix: *-utils (matches django-utils, flask-utils)
    """
    normalized_pkg = normalize_package_name(package)
    normalized_pattern = normalize_package_name(pattern)

    # Exact match (most common)
    if normalized_pkg == normalized_pattern:
        return True

    # Wildcard/glob matching
    if "*" in pattern or "?" in pattern:
        return fnmatch.fnmatch(normalized_pkg, normalized_pattern)

    return False


def is_allowed(package: str, allowlist: list[str]) -> bool:
    """
    Check if package is in allowlist.

    INV202: Returns True if package matches ANY allowlist entry.

    Args:
        package: Package name to check
        allowlist: List of allowed packages/patterns

    Returns:
        True if allowed, False otherwise
    """
    if not allowlist:
        return False

    for pattern in allowlist:
        if _matches_pattern(package, pattern):
            return True

    return False


def is_blocked(package: str, blocklist: list[str]) -> bool:
    """
    Check if package is in blocklist.

    INV203: Returns True if package matches ANY blocklist entry.

    Args:
        package: Package name to check
        blocklist: List of blocked packages/patterns

    Returns:
        True if blocked, False otherwise
    """
    if not blocklist:
        return False

    for pattern in blocklist:
        if _matches_pattern(package, pattern):
            return True

    return False


def get_list_status(
    package: str,
    allowlist: list[str],
    blocklist: list[str],
) -> Optional[str]:
    """
    Get the list status of a package.

    Args:
        package: Package name to check
        allowlist: Allowlist entries
        blocklist: Blocklist entries

    Returns:
        "allowed" if in allowlist (takes precedence)
        "blocked" if in blocklist
        None if in neither list
    """
    # Allowlist takes precedence
    if is_allowed(package, allowlist):
        return "allowed"

    if is_blocked(package, blocklist):
        return "blocked"

    return None


def filter_packages_by_lists(
    packages: list[str],
    allowlist: list[str],
    blocklist: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """
    Filter packages by allowlist and blocklist.

    Args:
        packages: Packages to filter
        allowlist: Allowlist entries
        blocklist: Blocklist entries

    Returns:
        Tuple of (allowed, blocked, to_validate)
        - allowed: Packages in allowlist (skip validation)
        - blocked: Packages in blocklist (reject)
        - to_validate: Packages requiring validation
    """
    allowed: list[str] = []
    blocked: list[str] = []
    to_validate: list[str] = []

    for pkg in packages:
        status = get_list_status(pkg, allowlist, blocklist)
        if status == "allowed":
            allowed.append(pkg)
        elif status == "blocked":
            blocked.append(pkg)
        else:
            to_validate.append(pkg)

    return allowed, blocked, to_validate


def add_to_list(
    package: str,
    current_list: list[str],
) -> list[str]:
    """Add package to a list (immutable operation)."""
    normalized = normalize_package_name(package)
    if normalized not in [normalize_package_name(p) for p in current_list]:
        return current_list + [package]
    return current_list


def remove_from_list(
    package: str,
    current_list: list[str],
) -> list[str]:
    """Remove package from a list (immutable operation)."""
    normalized = normalize_package_name(package)
    return [p for p in current_list if normalize_package_name(p) != normalized]
