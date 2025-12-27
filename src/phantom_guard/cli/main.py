"""
IMPLEMENTS: S010-S012
Command-line interface for Phantom Guard.
"""

from __future__ import annotations

import asyncio
from typing import Annotated

import typer
from rich.console import Console

from phantom_guard.cache import Cache
from phantom_guard.cli.branding import print_banner
from phantom_guard.cli.output import OutputFormatter
from phantom_guard.core import detector
from phantom_guard.core.types import (
    InvalidPackageNameError,
    InvalidRegistryError,
    Recommendation,
    validate_registry,
)
from phantom_guard.registry import CachedRegistryClient, CratesClient, NpmClient, PyPIClient
from phantom_guard.registry.exceptions import RegistryError

# CLI app
app = typer.Typer(
    name="phantom-guard",
    help="Detect AI-hallucinated package attacks (slopsquatting)",
    add_completion=False,
)

console = Console()

# Exit codes (from SPECIFICATION.md Section 6.4)
EXIT_SAFE = 0
EXIT_SUSPICIOUS = 1
EXIT_HIGH_RISK = 2
EXIT_NOT_FOUND = 3
EXIT_INPUT_ERROR = 4
EXIT_RUNTIME_ERROR = 5


@app.command()
def validate(
    package: Annotated[str, typer.Argument(help="Package name to validate")],
    registry: Annotated[
        str, typer.Option("-r", "--registry", help="Registry: pypi, npm, crates")
    ] = "pypi",
    verbose: Annotated[bool, typer.Option("-v", "--verbose", help="Show detailed signals")] = False,
    quiet: Annotated[bool, typer.Option("-q", "--quiet", help="Only show result")] = False,
    no_banner: Annotated[bool, typer.Option("--no-banner", help="Hide banner")] = False,
) -> None:
    """
    IMPLEMENTS: S010, S011
    TEST: T010.01-T010.06
    EC: EC080-EC083

    Validate a single package for supply chain risks.
    """
    if not quiet and not no_banner:
        print_banner(console)

    # Run async validation
    result = asyncio.run(_validate_package(package, registry, verbose, quiet))

    # Exit with appropriate code
    raise typer.Exit(code=result)


async def _validate_package(
    package: str,
    registry: str,
    verbose: bool,
    quiet: bool,
) -> int:
    """
    Run the actual validation logic.

    Args:
        package: Package name to validate
        registry: Registry name (pypi, npm, crates)
        verbose: Show detailed signal information
        quiet: Show minimal output

    Returns:
        Exit code based on validation result
    """
    formatter = OutputFormatter(console, verbose=verbose, quiet=quiet)

    try:
        # Validate registry
        validated_registry = validate_registry(registry)

        # Create registry client based on registry type
        # Use memory-only cache (no SQLite for CLI validation)
        cache = Cache(sqlite_enabled=False)

        if validated_registry == "pypi":
            base_client = PyPIClient()
        elif validated_registry == "npm":
            base_client = NpmClient()
        else:  # crates
            base_client = CratesClient()

        # Wrap with caching
        async with cache, CachedRegistryClient(base_client, cache, validated_registry) as client:
            # Run validation
            risk = await detector.validate_package(package, validated_registry, client)

            # Display result
            formatter.print_result(risk)

            # Return exit code based on recommendation
            match risk.recommendation:
                case Recommendation.SAFE:
                    return EXIT_SAFE
                case Recommendation.SUSPICIOUS:
                    return EXIT_SUSPICIOUS
                case Recommendation.HIGH_RISK:
                    return EXIT_HIGH_RISK
                case Recommendation.NOT_FOUND:
                    return EXIT_NOT_FOUND

            # Default return if no match (shouldn't happen)
            return EXIT_RUNTIME_ERROR

    except InvalidPackageNameError as e:
        formatter.print_error(f"Invalid package name: {e.reason}")
        return EXIT_INPUT_ERROR
    except InvalidRegistryError as e:
        formatter.print_error(str(e))
        return EXIT_INPUT_ERROR
    except RegistryError as e:
        formatter.print_error(f"Registry error: {e}")
        return EXIT_RUNTIME_ERROR
    except Exception as e:
        formatter.print_error(f"Unexpected error: {e}")
        return EXIT_RUNTIME_ERROR


@app.command()
def check(
    file: str = typer.Argument(..., help="Requirements file to check"),
) -> None:
    """Check all packages in a requirements file."""
    # Stub - will be implemented in W3.2
    typer.echo(f"Checking packages in {file}...")


if __name__ == "__main__":
    app()
