"""
IMPLEMENTS: S010-S012
Command-line interface for Phantom Guard.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from phantom_guard import __version__
from phantom_guard.cache import Cache, get_default_cache_path
from phantom_guard.cli.branding import BannerType, get_banner_type, show_banner
from phantom_guard.cli.output import OutputFormatter
from phantom_guard.cli.theme import PHANTOM_THEME
from phantom_guard.core import detector
from phantom_guard.core.types import (
    InvalidPackageNameError,
    InvalidRegistryError,
    PackageRisk,
    Recommendation,
    validate_registry,
)
from phantom_guard.registry import CachedRegistryClient, CratesClient, NpmClient, PyPIClient
from phantom_guard.registry.cached import RegistryClientProtocol
from phantom_guard.registry.exceptions import RegistryError, RegistryTimeoutError
from phantom_guard.registry.retry import retry_async

# Themed console - respects NO_COLOR environment variable
console = Console(theme=PHANTOM_THEME, no_color=bool(os.environ.get("NO_COLOR")))


def version_callback(value: bool) -> None:
    """
    Display version with full LARGE banner.

    IMPLEMENTS: S010
    """
    if value:
        # Show LARGE banner for version display
        show_banner(console, BannerType.LARGE, __version__)
        raise typer.Exit()


# CLI app
app = typer.Typer(
    name="phantom-guard",
    help="Detect AI-hallucinated package attacks (slopsquatting)",
    add_completion=False,
)


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = False,
) -> None:
    """
    Phantom Guard - Detect AI-hallucinated package attacks (slopsquatting).
    """
    pass


# Cache subcommand group
cache_app = typer.Typer(help="Manage the local cache")
app.add_typer(cache_app, name="cache")


def _format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


@cache_app.command("clear")
def cache_clear(
    registry: Annotated[
        str | None, typer.Option("-r", "--registry", help="Only clear specific registry")
    ] = None,
    force: Annotated[bool, typer.Option("-f", "--force", help="Skip confirmation")] = False,
) -> None:
    """
    IMPLEMENTS: S016
    TEST: T010.22
    EC: EC094

    Clear the local cache.
    """
    cache_path = get_default_cache_path()

    if not cache_path.exists():
        console.print("[dim]No cache found[/dim]")
        raise typer.Exit(code=0)

    # Confirmation
    if not force:
        msg = f"Clear cache for {registry}?" if registry else "Clear entire cache?"
        if not typer.confirm(msg):
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(code=0)

    # Clear cache
    deleted = asyncio.run(_clear_cache(cache_path, registry))
    console.print(f"[green]Cache cleared successfully ({deleted} entries)[/green]")


async def _clear_cache(cache_path: Path, registry: str | None) -> int:
    """Clear cache entries."""
    from phantom_guard.cache import Cache

    cache = Cache(sqlite_path=cache_path)
    async with cache:
        if registry:
            return await cache.clear_registry(registry)
        else:
            memory_count, sqlite_count = await cache.clear_all()
            return memory_count + sqlite_count


@cache_app.command("stats")
def cache_stats() -> None:
    """
    IMPLEMENTS: S017
    TEST: T010.23

    Show cache statistics.
    """
    cache_path = get_default_cache_path()

    if not cache_path.exists():
        console.print("[dim]No cache found[/dim]")
        raise typer.Exit(code=0)

    stats = asyncio.run(_get_cache_stats(cache_path))

    if not stats:
        console.print("[dim]Cache is empty[/dim]")
        raise typer.Exit(code=0)

    # Display stats
    table = Table(title="Cache Statistics")
    table.add_column("Registry", style="cyan")
    table.add_column("Entries", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("Hit Rate", justify="right")

    for reg, data in stats.items():
        table.add_row(
            reg,
            str(data["entries"]),
            _format_size(data["size_bytes"]),
            f"{data['hit_rate']:.1%}" if data.get("hit_rate") else "N/A",
        )

    console.print(table)


async def _get_cache_stats(cache_path: Path) -> dict[str, dict[str, Any]]:
    """Get cache statistics."""
    from phantom_guard.cache import Cache

    cache = Cache(sqlite_path=cache_path)
    async with cache:
        return await cache.get_stats()


@cache_app.command("path")
def cache_path_cmd() -> None:
    """
    IMPLEMENTS: S016
    TEST: T010.24

    Show cache file location.
    """
    path = get_default_cache_path()
    console.print(f"Cache path: [cyan]{path}[/cyan]")
    if path.exists():
        size = path.stat().st_size
        console.print(f"Size: [dim]{_format_size(size)}[/dim]")
    else:
        console.print("[dim]Cache does not exist yet[/dim]")


# Exit codes (from SPECIFICATION.md Section 6.4)
EXIT_SAFE = 0
EXIT_SUSPICIOUS = 1
EXIT_HIGH_RISK = 2
EXIT_NOT_FOUND = 3
EXIT_INPUT_ERROR = 4
EXIT_RUNTIME_ERROR = 5


@app.command()
def validate(
    packages: Annotated[list[str], typer.Argument(help="Package name(s) to validate")],
    registry: Annotated[
        str, typer.Option("-r", "--registry", help="Registry: pypi, npm, crates")
    ] = "pypi",
    verbose: Annotated[bool, typer.Option("-v", "--verbose", help="Show detailed signals")] = False,
    quiet: Annotated[bool, typer.Option("-q", "--quiet", help="Only show result")] = False,
    no_banner: Annotated[bool, typer.Option("--no-banner", help="Hide banner")] = False,
    plain: Annotated[
        bool, typer.Option("--plain", help="Disable colors (plain text output)")
    ] = False,
) -> None:
    """
    IMPLEMENTS: S010, S011
    TEST: T010.01-T010.06
    EC: EC080-EC083

    Validate one or more packages for supply chain risks.

    Examples:
        phantom-guard validate requests
        phantom-guard validate requests flask numpy
        phantom-guard validate lodash -r npm
    """
    # Create console based on plain flag
    cmd_console = Console(force_terminal=False) if plain else console

    # Determine and show appropriate banner
    banner_type = get_banner_type("validate", no_banner, quiet, "text")
    show_banner(cmd_console, banner_type, __version__)

    # Run async validation for all packages
    result = asyncio.run(_validate_packages(packages, registry, verbose, quiet, cmd_console))

    # Exit with appropriate code
    raise typer.Exit(code=result)


async def _validate_packages(
    packages: list[str],
    registry: str,
    verbose: bool,
    quiet: bool,
    cmd_console: Console | None = None,
) -> int:
    """
    Validate multiple packages and return worst exit code.

    Args:
        packages: List of package names to validate
        registry: Registry name (pypi, npm, crates)
        verbose: Show detailed signal information
        quiet: Show minimal output
        cmd_console: Console to use for output

    Returns:
        Worst exit code from all validations (highest risk)
    """
    output_console = cmd_console or console
    formatter = OutputFormatter(output_console, verbose=verbose, quiet=quiet)
    worst_exit = EXIT_SAFE

    try:
        # Validate registry
        validated_registry = validate_registry(registry)

        # Create registry client
        cache = Cache(sqlite_enabled=False)

        base_client: RegistryClientProtocol
        if validated_registry == "pypi":
            base_client = PyPIClient()
        elif validated_registry == "npm":
            base_client = NpmClient()
        else:  # crates
            base_client = CratesClient()

        # Wrap with caching
        async with cache, CachedRegistryClient(base_client, cache, validated_registry) as client:
            for package in packages:
                try:
                    # Run validation with retry (3 attempts with exponential backoff)
                    # Capture loop variable with default argument to avoid B023
                    async def _validate(pkg: str = package) -> PackageRisk:
                        return await detector.validate_package(pkg, validated_registry, client)

                    risk = await retry_async(_validate, max_retries=3)

                    # Display result
                    formatter.print_result(risk)

                    # Track worst exit code
                    exit_code = _get_exit_code(risk.recommendation)
                    if exit_code > worst_exit:
                        worst_exit = exit_code

                except InvalidPackageNameError as e:
                    formatter.print_error(f"Invalid package name '{package}': {e.reason}")
                    if worst_exit < EXIT_INPUT_ERROR:
                        worst_exit = EXIT_INPUT_ERROR
                except RegistryTimeoutError:
                    formatter.print_error(f"Timeout validating '{package}' (retries exhausted)")
                    if worst_exit < EXIT_RUNTIME_ERROR:
                        worst_exit = EXIT_RUNTIME_ERROR

        return worst_exit

    except InvalidRegistryError as e:
        formatter.print_error(str(e))
        return EXIT_INPUT_ERROR
    except RegistryError as e:
        formatter.print_error(f"Registry error: {e}")
        return EXIT_RUNTIME_ERROR
    except Exception as e:
        formatter.print_error(f"Unexpected error: {e}")
        return EXIT_RUNTIME_ERROR


def _get_exit_code(recommendation: Recommendation) -> int:
    """Map recommendation to exit code."""
    match recommendation:
        case Recommendation.SAFE:
            return EXIT_SAFE
        case Recommendation.SUSPICIOUS:
            return EXIT_SUSPICIOUS
        case Recommendation.HIGH_RISK:
            return EXIT_HIGH_RISK
        case Recommendation.NOT_FOUND:
            return EXIT_NOT_FOUND
    return EXIT_RUNTIME_ERROR  # pragma: no cover


async def _validate_package(
    package: str,
    registry: str,
    verbose: bool,
    quiet: bool,
    cmd_console: Console | None = None,
) -> int:
    """
    Run the actual validation logic for a single package.

    Args:
        package: Package name to validate
        registry: Registry name (pypi, npm, crates)
        verbose: Show detailed signal information
        quiet: Show minimal output
        cmd_console: Console to use for output (defaults to module-level console)

    Returns:
        Exit code based on validation result
    """
    return await _validate_packages([package], registry, verbose, quiet, cmd_console)


@app.command()
def check(
    file: Annotated[Path, typer.Argument(help="Dependency file to check")],
    registry: Annotated[
        str | None, typer.Option("-r", "--registry", help="Override registry detection")
    ] = None,
    fail_on: Annotated[
        str | None,
        typer.Option("--fail-on", help="Exit non-zero on: suspicious, high_risk"),
    ] = None,
    ignore: Annotated[
        str | None, typer.Option("--ignore", help="Comma-separated packages to skip")
    ] = None,
    parallel: Annotated[int, typer.Option("--parallel", help="Concurrent validations")] = 10,
    fail_fast: Annotated[
        bool, typer.Option("--fail-fast", help="Stop on first HIGH_RISK package")
    ] = False,
    output_format: Annotated[
        str, typer.Option("-o", "--output", help="Output format: text, json")
    ] = "text",
    quiet: Annotated[bool, typer.Option("-q", "--quiet", help="Minimal output")] = False,
    no_banner: Annotated[bool, typer.Option("--no-banner", help="Hide banner")] = False,
    plain: Annotated[
        bool, typer.Option("--plain", help="Disable colors (plain text output)")
    ] = False,
) -> None:
    """
    IMPLEMENTS: S013-S015
    TEST: T010.18
    EC: EC084-EC090

    Check a dependency file for risky packages.

    Supports:
    - requirements.txt (Python/PyPI)
    - package.json (JavaScript/npm)
    - Cargo.toml (Rust/crates.io)
    """
    from phantom_guard.cli.parsers import ParserError, detect_and_parse

    # Create console based on plain flag
    cmd_console = Console(force_terminal=False) if plain else console

    # Determine and show appropriate banner
    banner_type = get_banner_type("check", no_banner, quiet, output_format)
    show_banner(cmd_console, banner_type, __version__)

    # Validate file exists
    if not file.exists():
        cmd_console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)

    # Parse file
    try:
        packages = detect_and_parse(file)
    except ParserError as e:
        cmd_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=EXIT_INPUT_ERROR) from None

    if not packages:
        cmd_console.print("[dim]No packages found in file[/dim]")
        raise typer.Exit(code=EXIT_SAFE)

    # Filter ignored packages
    ignored_set = set(ignore.split(",")) if ignore else set()
    packages = [p for p in packages if p.name not in ignored_set]

    # Override registry if specified
    if registry:
        try:
            validated_registry = validate_registry(registry)
            for p in packages:
                p.registry = validated_registry
        except InvalidRegistryError as e:
            cmd_console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=EXIT_INPUT_ERROR) from None

    # Run validation
    exit_code = asyncio.run(
        _check_packages(packages, parallel, fail_on, output_format, quiet, fail_fast, cmd_console)
    )
    raise typer.Exit(code=exit_code)


async def _check_packages(
    packages: list[Any],
    parallel: int,
    fail_on: str | None,
    output_format: str,
    quiet: bool,
    fail_fast: bool = False,
    cmd_console: Console | None = None,
) -> int:
    """
    Validate all packages from file using BatchValidator.

    IMPLEMENTS: S002
    INV: INV004, INV005

    Args:
        packages: List of ParsedPackage instances
        parallel: Maximum concurrent validations
        fail_on: Fail threshold (suspicious or high_risk)
        output_format: Output format (text or json)
        quiet: Minimal output mode
        fail_fast: Stop on first HIGH_RISK package
        cmd_console: Console to use for output (defaults to module-level console)

    Returns:
        Exit code based on validation results
    """
    from typing import Literal, TypeAlias

    from rich.progress import BarColumn, Progress, SpinnerColumn, TaskID, TextColumn

    from phantom_guard.cli.formatters import get_formatter
    from phantom_guard.cli.parsers import ParsedPackage
    from phantom_guard.core.batch import BatchConfig, BatchValidator

    output_console = cmd_console or console
    RegistryLiteral: TypeAlias = Literal["pypi", "npm", "crates"]

    # Group packages by registry
    packages_by_registry: dict[RegistryLiteral, list[ParsedPackage]] = {}
    for pkg in packages:
        reg = validate_registry(pkg.registry)
        if reg not in packages_by_registry:
            packages_by_registry[reg] = []
        packages_by_registry[reg].append(pkg)

    # Create cache
    cache = Cache(sqlite_enabled=False)

    # Configure batch validation
    config = BatchConfig(
        max_concurrent=parallel,
        fail_fast=fail_fast,
    )
    validator = BatchValidator(config=config)

    all_results: list[PackageRisk] = []
    all_errors: dict[str, Exception] = {}
    was_cancelled = False
    total_time_ms = 0.0

    # Suppress progress output for JSON format
    suppress_progress = quiet or output_format == "json"

    if not suppress_progress:
        output_console.print(f"\n[cyan]Scanning {len(packages)} packages...[/cyan]\n")

    # Create progress bar
    progress_task: TaskID | None = None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=output_console,
        disable=suppress_progress,
    ) as progress:
        progress_task = progress.add_task("Validating", total=len(packages))

        def on_progress(done: int, total: int) -> None:
            if progress_task is not None:  # pragma: no cover
                progress.update(progress_task, completed=done)

        # Validate each registry group
        async with cache:
            for reg, reg_packages in packages_by_registry.items():
                if was_cancelled:  # pragma: no cover
                    break  # pragma: no cover

                # Get appropriate registry client
                base_client: RegistryClientProtocol
                if reg == "pypi":
                    base_client = PyPIClient()
                elif reg == "npm":
                    base_client = NpmClient()
                else:  # crates
                    base_client = CratesClient()

                # Wrap with caching
                async with CachedRegistryClient(base_client, cache, reg) as client:
                    result = await validator.validate_batch(
                        packages=[p.name for p in reg_packages],
                        registry=reg,
                        client=client,
                        on_progress=on_progress,
                    )

                    all_results.extend(result.results)
                    all_errors.update(result.errors)
                    total_time_ms += result.total_time_ms

                    if result.was_cancelled:
                        was_cancelled = True

    # Print results
    if not suppress_progress:
        output_console.print()
    formatter = get_formatter(output_format, verbose=False, quiet=quiet)
    formatter.print_results(all_results, output_console)

    # Print errors if any (not for JSON format)
    if all_errors and not quiet and output_format != "json":
        output_console.print("\n[yellow]Errors:[/yellow]")
        for pkg, error in all_errors.items():
            output_console.print(f"  [red]{pkg}:[/red] {error}")

    # Print summary (only for text format)
    if output_format == "text" and not quiet:
        _print_batch_summary(all_results, all_errors, was_cancelled, total_time_ms, output_console)

    # Determine exit code
    return _determine_exit_code(all_results, fail_on)


def _print_batch_summary(
    results: list[PackageRisk],
    errors: dict[str, Exception],
    was_cancelled: bool,
    total_time_ms: float,
    console: Console,
) -> None:
    """
    Print batch validation summary.

    Args:
        results: List of package risk assessments
        errors: Dictionary of package errors
        was_cancelled: Whether validation was cancelled (fail_fast)
        total_time_ms: Total validation time in milliseconds
        console: Rich console for output
    """
    safe = sum(1 for r in results if r.recommendation == Recommendation.SAFE)
    suspicious = sum(1 for r in results if r.recommendation == Recommendation.SUSPICIOUS)
    high_risk = sum(1 for r in results if r.recommendation == Recommendation.HIGH_RISK)
    not_found = sum(1 for r in results if r.recommendation == Recommendation.NOT_FOUND)
    error_count = len(errors)

    # Use ASCII-safe separator for Windows compatibility
    separator = "-" * 60
    console.print("\n" + separator)

    # Status line
    if was_cancelled:
        console.print("[yellow]Validation stopped early (fail-fast triggered)[/yellow]")

    # Summary counts
    total = len(results) + error_count
    summary = f"Summary: {total} packages | "
    summary += f"[green]{safe} safe[/green] | "
    summary += f"[yellow]{suspicious} suspicious[/yellow] | "
    summary += f"[red]{high_risk} high-risk[/red]"
    if not_found:
        summary += f" | [dim]{not_found} not found[/dim]"
    if error_count:
        summary += f" | [red]{error_count} errors[/red]"
    console.print(summary)

    # Timing
    time_sec = total_time_ms / 1000
    console.print(f"[dim]Completed in {time_sec:.2f}s[/dim]")
    console.print(separator + "\n")


def _print_summary(results: list[PackageRisk], console: Console) -> None:
    """
    Print summary line.

    Args:
        results: List of package risk assessments
        console: Rich console for output
    """
    safe = sum(1 for r in results if r.recommendation == Recommendation.SAFE)
    suspicious = sum(1 for r in results if r.recommendation == Recommendation.SUSPICIOUS)
    high_risk = sum(1 for r in results if r.recommendation == Recommendation.HIGH_RISK)
    not_found = sum(1 for r in results if r.recommendation == Recommendation.NOT_FOUND)

    # Use ASCII-safe separator for Windows compatibility
    separator = "-" * 60
    console.print("\n" + separator)
    summary = f"Summary: {len(results)} packages | "
    summary += f"[green]{safe} safe[/green] | "
    summary += f"[yellow]{suspicious} suspicious[/yellow] | "
    summary += f"[red]{high_risk} high-risk[/red]"
    if not_found:
        summary += f" | [dim]{not_found} not found[/dim]"
    console.print(summary)
    console.print(separator + "\n")


def _determine_exit_code(results: list[PackageRisk], fail_on: str | None) -> int:
    """
    Determine exit code based on results and fail_on setting.

    Args:
        results: List of package risk assessments
        fail_on: Fail threshold (suspicious or high_risk)

    Returns:
        Appropriate exit code
    """
    has_high_risk = any(r.recommendation == Recommendation.HIGH_RISK for r in results)
    has_suspicious = any(r.recommendation == Recommendation.SUSPICIOUS for r in results)
    has_not_found = any(r.recommendation == Recommendation.NOT_FOUND for r in results)

    # Always fail on high risk
    if has_high_risk:
        return EXIT_HIGH_RISK

    # Fail on suspicious if requested
    if fail_on == "suspicious" and has_suspicious:
        return EXIT_SUSPICIOUS

    # Default behavior: exit with suspicious code if suspicious packages found
    if has_suspicious:
        return EXIT_SUSPICIOUS

    # Not found packages
    if has_not_found:
        return EXIT_NOT_FOUND

    # All safe
    return EXIT_SAFE


if __name__ == "__main__":
    app()
