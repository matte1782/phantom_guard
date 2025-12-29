"""
Package manifest parsers for CLI batch scanning.

IMPLEMENTS: S013, S014, S015
TESTS: T010.13, T010.14, T010.15, T010.16, T010.17
EDGE_CASES: EC084, EC087, EC088
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore  # pragma: no cover


@dataclass
class ParsedPackage:
    """
    Represents a parsed package from a manifest file.

    Attributes:
        name: Package name (may include scope for npm)
        version_spec: Version specification (e.g., ">=1.0,<2.0", "^1.2.3", None)
        registry: Registry type ("pypi", "npm", "crates")
    """

    name: str
    version_spec: str | None
    registry: str


class ParserError(Exception):
    """Raised when a manifest file cannot be parsed."""

    pass


def parse_requirements_txt(content: str) -> list[ParsedPackage]:
    """
    Parse Python requirements.txt format.

    IMPLEMENTS: S013
    TESTS: T010.13, T010.14
    EDGE_CASES: EC084, EC087, EC088

    Supports:
        - Simple names: flask
        - Versioned: flask==2.0.0
        - Ranges: flask>=2.0,<3.0
        - Extras: flask[async]
        - Comments: # comment
        - Inline comments: flask  # web framework

    Skips:
        - URLs: https://...
        - Editable installs: -e
        - Options: --index-url, -r, etc.

    Args:
        content: Contents of requirements.txt file

    Returns:
        List of ParsedPackage instances

    Example:
        >>> parse_requirements_txt("flask==2.0.0\\nrequests>=2.28")
        [ParsedPackage(name='flask', version_spec='==2.0.0', registry='pypi'),
         ParsedPackage(name='requests', version_spec='>=2.28', registry='pypi')]
    """
    packages: list[ParsedPackage] = []

    # Pattern to match package specifications
    # Matches: name, name[extra], name==version, name>=version,<version, etc.
    # Captures: package name, extras (optional), version spec (optional)
    pattern = re.compile(
        r"^([a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?)"  # Package name
        r"(\[[^\]]+\])?"  # Optional extras [extra1,extra2]
        r"([!<>=~][^#\s]*)?"  # Optional version specifier
    )

    for line in content.splitlines():
        # Strip whitespace
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip comments
        if line.startswith("#"):
            continue

        # Skip options
        if line.startswith("-") or line.startswith("--"):
            continue

        # Skip URLs (including git+ URLs)
        if line.startswith(("http://", "https://", "git+")):
            continue

        # Remove inline comments
        if "#" in line:
            line = line.split("#")[0].strip()

        # Match package specification
        match = pattern.match(line)
        if match:
            name = match.group(1)
            # extras = match.group(3)  # Not used currently
            version_spec = match.group(4)

            packages.append(ParsedPackage(name=name, version_spec=version_spec, registry="pypi"))

    return packages


def parse_package_json(content: str) -> list[ParsedPackage]:
    """
    Parse npm package.json format.

    IMPLEMENTS: S014
    TESTS: T010.15
    EDGE_CASES: EC084

    Supports:
        - dependencies and devDependencies sections
        - Scoped packages: @types/node
        - Standard version specs: ^1.2.3, ~1.2.3, >=1.0.0

    Args:
        content: Contents of package.json file

    Returns:
        List of ParsedPackage instances

    Raises:
        ParserError: If JSON is invalid

    Example:
        >>> parse_package_json('{"dependencies": {"express": "^4.18.0"}}')
        [ParsedPackage(name='express', version_spec='^4.18.0', registry='npm')]
    """
    packages: list[ParsedPackage] = []

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ParserError(f"Failed to parse package.json: {e}") from e

    # Parse dependencies
    for section in ["dependencies", "devDependencies"]:
        deps = data.get(section, {})
        if not isinstance(deps, dict):
            continue

        for name, version_spec in deps.items():
            packages.append(
                ParsedPackage(
                    name=name, version_spec=version_spec if version_spec else None, registry="npm"
                )
            )

    return packages


def parse_cargo_toml(content: str) -> list[ParsedPackage]:
    """
    Parse Rust Cargo.toml format.

    IMPLEMENTS: S015
    TESTS: T010.16
    EDGE_CASES: EC084

    Supports:
        - dependencies and dev-dependencies sections
        - Simple version specs: "1.0"
        - Complex specs: { version = "1.0", features = [...] }

    Args:
        content: Contents of Cargo.toml file

    Returns:
        List of ParsedPackage instances

    Raises:
        ParserError: If TOML is invalid

    Example:
        >>> parse_cargo_toml('[dependencies]\\nserde = "1.0"')
        [ParsedPackage(name='serde', version_spec='1.0', registry='crates')]
    """
    packages: list[ParsedPackage] = []

    try:
        data = tomllib.loads(content)
    except Exception as e:
        raise ParserError(f"Failed to parse Cargo.toml: {e}") from e

    # Parse dependencies
    for section in ["dependencies", "dev-dependencies"]:
        deps = data.get(section, {})
        if not isinstance(deps, dict):
            continue

        for name, spec in deps.items():
            # Handle simple string version: serde = "1.0"
            if isinstance(spec, str):
                version_spec: str | None = spec
            # Handle complex table: serde = { version = "1.0", features = [...] }
            elif isinstance(spec, dict):
                version_spec = spec.get("version")
            else:
                version_spec = None

            packages.append(ParsedPackage(name=name, version_spec=version_spec, registry="crates"))

    return packages


def detect_and_parse(file_path: Path) -> list[ParsedPackage]:
    """
    Auto-detect file format and parse accordingly.

    IMPLEMENTS: S013, S014, S015
    TESTS: T010.17

    Detection strategy:
        1. Check filename (requirements.txt, package.json, Cargo.toml)
        2. If ambiguous, inspect content

    Args:
        file_path: Path to manifest file

    Returns:
        List of ParsedPackage instances

    Raises:
        ParserError: If file format cannot be detected or parsing fails
        FileNotFoundError: If file does not exist

    Example:
        >>> detect_and_parse(Path("requirements.txt"))
        [ParsedPackage(name='flask', version_spec='==2.0.0', registry='pypi')]
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    filename = file_path.name.lower()

    # Detect by filename
    if filename in ("requirements.txt", "requirements-dev.txt", "requirements-test.txt"):
        return parse_requirements_txt(content)
    elif filename == "package.json":
        return parse_package_json(content)
    elif filename == "cargo.toml":
        return parse_cargo_toml(content)

    # Try to detect by content if filename is ambiguous
    # Try JSON first (most strict)
    try:
        return parse_package_json(content)
    except (ParserError, json.JSONDecodeError):
        pass

    # Try TOML
    try:
        return parse_cargo_toml(content)
    except ParserError:
        pass

    # Fall back to requirements.txt (most lenient)
    try:
        return parse_requirements_txt(content)
    except Exception as e:  # pragma: no cover
        raise ParserError(  # pragma: no cover
            f"Could not detect file format for {file_path.name}. "
            f"Expected requirements.txt, package.json, or Cargo.toml"
        ) from e
