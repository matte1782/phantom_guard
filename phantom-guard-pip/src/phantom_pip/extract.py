"""
Package name extraction from pip arguments.

IMPLEMENTS: S202
INVARIANTS: INV204 (validate before subprocess)
TESTS: T202.*
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from phantom_pip.parser import ParsedArgs

# SECURITY: Package name validation
# Note: @ and / allowed for scoped packages (npm-style @scope/package)
PACKAGE_NAME_REGEX = re.compile(r"^[@a-z0-9][a-z0-9._/-]*$", re.IGNORECASE)
# Note: <> NOT included because they're valid version operators
# SECURITY: Include newlines (\n\r) to prevent line injection attacks
SHELL_METACHARACTERS = re.compile(r"[;|&$`\\\"'()\n\r\x00]")
VERSION_OPERATORS = re.compile(r"[<>=!~\[]")
# SECURITY: Max length for version specifiers to prevent ReDoS
MAX_VERSION_SPEC_LENGTH = 500
# SECURITY: Max file size for requirements files to prevent DoS
MAX_REQUIREMENTS_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@dataclass
class ExtractedPackage:
    """A package extracted from pip arguments."""

    name: str  # Base name without version (e.g., 'flask')
    full_spec: str  # Full specification (e.g., 'flask>=2.0[async]')
    extras: list[str]  # Extras (e.g., ['async', 'dotenv'])
    version_spec: Optional[str]  # Version specifier (e.g., '>=2.0')


def validate_package_name(name: str) -> bool:
    """
    Validate package name for safety.

    INV204: Must be called before any subprocess operation.
    INV205: Prevents shell injection via metacharacters.

    Args:
        name: Package name or spec to validate

    Returns:
        True if safe, False if potentially dangerous
    """
    if not name:
        return False

    # SECURITY: Reject shell metacharacters
    if SHELL_METACHARACTERS.search(name):
        return False

    # Extract base name (strip version specifier and extras)
    base_name = _extract_base_name(name)

    if not base_name:
        return False

    return bool(PACKAGE_NAME_REGEX.match(base_name))


def _extract_base_name(spec: str) -> str:
    """Extract base package name from a full specification."""
    # Remove extras [async,dotenv]
    name = re.split(r"\[", spec)[0]
    # Remove version specifier
    name = re.split(r"[<>=!~]", name)[0]
    return name.strip()


def _extract_extras(spec: str) -> list[str]:
    """Extract extras from package specification."""
    match = re.search(r"\[([^\]]+)\]", spec)
    if match:
        return [e.strip() for e in match.group(1).split(",")]
    return []


def _extract_version_spec(spec: str) -> Optional[str]:
    """Extract version specifier from package specification."""
    # SECURITY: Reject overly long specs to prevent ReDoS
    if len(spec) > MAX_VERSION_SPEC_LENGTH:
        return None
    # Remove extras first
    no_extras = re.sub(r"\[[^\]]+\]", "", spec)
    # SECURITY: Use bounded regex to prevent catastrophic backtracking
    # Match: operator(s) followed by version string (limited length)
    match = re.search(r"([<>=!~]+[0-9a-zA-Z.,*_-]{0,200})$", no_extras)
    if match:
        return match.group(1)
    return None


def _is_url_or_path(arg: str) -> bool:
    """Check if argument is a URL or local path (not a package name)."""
    # URL patterns
    if arg.startswith(("http://", "https://", "git+", "svn+", "hg+", "bzr+")):
        return True

    # Absolute or relative paths
    if arg.startswith(("/", "./", "../", "~")):
        return True

    # Windows absolute paths (C:/ or C:\)
    if len(arg) > 2 and arg[1] == ":" and arg[2] in ("/", "\\"):
        return True

    # SECURITY: Windows UNC paths (//server/share or \\server\share)
    if arg.startswith(("//", "\\\\")):
        return True

    # File extensions
    if arg.endswith((".whl", ".tar.gz", ".zip", ".egg")):
        return True

    return False


def is_validatable_package(package: str) -> bool:
    """
    Check if a package string should be validated against registries.

    Returns False for:
    - URLs (git+https://, http://, etc.)
    - Local paths (., .., /, ~, C:)
    - Local files (.whl, .tar.gz)

    Returns True for:
    - Package names: flask, requests
    - With version: flask>=2.0
    - With extras: flask[async]
    """
    return not _is_url_or_path(package)


def extract_package(spec: str) -> Optional[ExtractedPackage]:
    """
    Extract and validate a single package specification.

    Args:
        spec: Package specification (e.g., 'flask>=2.0[async]')

    Returns:
        ExtractedPackage if valid, None if invalid/not validatable
    """
    # Skip non-validatable specs (URLs, paths)
    if not is_validatable_package(spec):
        return None

    # Validate for security
    if not validate_package_name(spec):
        return None

    return ExtractedPackage(
        name=_extract_base_name(spec),
        full_spec=spec,
        extras=_extract_extras(spec),
        version_spec=_extract_version_spec(spec),
    )


def extract_packages(parsed: "ParsedArgs") -> list[ExtractedPackage]:
    """
    Extract all packages from parsed pip arguments.

    Also extracts packages from requirements files.

    INV204: All packages validated before return.

    Args:
        parsed: Parsed pip arguments

    Returns:
        List of validated ExtractedPackage objects
    """
    packages: list[ExtractedPackage] = []

    # Extract from direct package arguments
    for spec in parsed.packages:
        pkg = extract_package(spec)
        if pkg is not None:
            packages.append(pkg)

    # Extract from requirements files
    for req_file in parsed.requirements_files:
        file_packages = extract_from_requirements_file(req_file)
        packages.extend(file_packages)

    return packages


def extract_from_requirements_file(filepath: str) -> list[ExtractedPackage]:
    """
    Extract packages from a requirements.txt file.

    Args:
        filepath: Path to requirements file

    Returns:
        List of ExtractedPackage objects
    """
    packages: list[ExtractedPackage] = []
    path = Path(filepath)

    if not path.exists():
        return packages

    try:
        # SECURITY: Check file size to prevent DoS via large files
        file_size = path.stat().st_size
        if file_size > MAX_REQUIREMENTS_FILE_SIZE:
            return packages

        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return packages

    for line in content.splitlines():
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Skip -r, -e, -c, -i, --index-url, etc.
        if line.startswith("-"):
            continue

        # Skip URLs
        if line.startswith(("http://", "https://", "git+", "svn+")):
            continue

        # Handle inline comments
        if " #" in line:
            line = line.split(" #")[0].strip()

        # Handle environment markers (e.g., "requests; python_version >= '3.6'")
        if ";" in line:
            line = line.split(";")[0].strip()

        pkg = extract_package(line)
        if pkg is not None:
            packages.append(pkg)

    return packages


def get_package_names(packages: list[ExtractedPackage]) -> list[str]:
    """
    Get just the base package names for validation.

    Args:
        packages: List of ExtractedPackage objects

    Returns:
        List of base package names (e.g., ['flask', 'requests'])
    """
    return [pkg.name for pkg in packages]
