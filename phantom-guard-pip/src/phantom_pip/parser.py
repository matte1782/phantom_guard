"""
pip argument parser.

IMPLEMENTS: S201
INVARIANTS: INV200 (never modify pip arguments)
TESTS: T201.*
"""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class ParsedArgs:
    """Parsed pip install arguments."""

    command: str  # 'install', 'uninstall', etc.
    packages: list[str] = field(default_factory=list)  # Direct package names
    requirements_files: list[str] = field(default_factory=list)  # -r files
    constraints_files: list[str] = field(default_factory=list)  # -c files
    editable: list[str] = field(default_factory=list)  # -e paths
    options: list[str] = field(default_factory=list)  # Other pip options
    raw_args: list[str] = field(default_factory=list)  # Original args (INV200)


# pip options that take a value (next argument)
OPTIONS_WITH_VALUES = {
    "-r", "--requirement",
    "-c", "--constraint",
    "-e", "--editable",
    "-t", "--target",
    "-d", "--download",
    "--src",
    "--root",
    "--prefix",
    "-b", "--build",
    "--platform",
    "--python-version",
    "--implementation",
    "--abi",
    "--index-url", "-i",
    "--extra-index-url",
    "--find-links", "-f",
    "--trusted-host",
    "--cert",
    "--client-cert",
    "--proxy",
    "--retries",
    "--timeout",
    "--config-settings",
    "--global-option",
    "--install-option",
    "--progress-bar",
    "--root-user-action",
}

# pip boolean flags (no value)
BOOLEAN_FLAGS = {
    "-U", "--upgrade",
    "--force-reinstall",
    "-I", "--ignore-installed",
    "--no-deps",
    "--pre",
    "--user",
    "--system",
    "--compile", "--no-compile",
    "-q", "--quiet",
    "-v", "--verbose",
    "--no-cache-dir",
    "--disable-pip-version-check",
    "--no-color",
    "--no-python-version-warning",
    "--use-pep517", "--no-use-pep517",
    "--check-build-dependencies", "--no-check-build-dependencies",
    "--break-system-packages",
    "--no-warn-script-location",
    "--no-warn-conflicts",
    "--report",
    "--no-binary", "--only-binary",
    "--prefer-binary",
    "--require-hashes",
    "--no-build-isolation",
    "--use-feature",
    "--no-index",
    "--ignore-requires-python",
    "--exists-action",
    "-h", "--help",
    "-V", "--version",
    "-y", "--yes",
}


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


def _categorize_option(result: ParsedArgs, option: str, value: str) -> None:
    """Categorize an option with its value."""
    if option in ("-r", "--requirement"):
        result.requirements_files.append(value)
    elif option in ("-c", "--constraint"):
        result.constraints_files.append(value)
    elif option in ("-e", "--editable"):
        result.editable.append(value)
    else:
        result.options.extend([option, value])


def parse_pip_args(args: list[str]) -> ParsedArgs:
    """
    Parse pip command line arguments.

    Handles all pip install variants:
    - Simple: pip install flask
    - Multiple: pip install flask requests
    - Versioned: pip install flask>=2.0
    - Requirements: pip install -r requirements.txt
    - Editable: pip install -e .
    - Extras: pip install flask[async]
    - URL: pip install git+https://...
    - Local wheel: pip install ./package.whl

    INV200: Original args preserved in raw_args for passthrough.

    Args:
        args: Command line arguments (e.g., ['install', 'flask', '-r', 'req.txt'])

    Returns:
        ParsedArgs with categorized arguments
    """
    if not args:
        return ParsedArgs(command="", raw_args=[])

    result = ParsedArgs(
        command=args[0] if args else "",
        raw_args=list(args),  # INV200: Preserve original
    )

    # Skip command itself
    arg_iter: Iterator[str] = iter(args[1:])

    for arg in arg_iter:
        # Handle options with values
        if arg in OPTIONS_WITH_VALUES:
            try:
                value = next(arg_iter)
                _categorize_option(result, arg, value)
            except StopIteration:
                result.options.append(arg)
            continue

        # Handle --option=value format
        if "=" in arg:
            opt_part = arg.split("=")[0]
            if opt_part in OPTIONS_WITH_VALUES:
                opt, value = arg.split("=", 1)
                _categorize_option(result, opt, value)
                continue

        # Handle boolean flags
        if arg in BOOLEAN_FLAGS or arg.startswith("-"):
            result.options.append(arg)
            continue

        # Skip URLs and local paths (not validatable package names)
        if _is_url_or_path(arg):
            result.options.append(arg)
            continue

        # It's a package name (possibly with version specifier or extras)
        result.packages.append(arg)

    return result


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
