"""
phantom-pip CLI entry point.

IMPLEMENTS: S200
INVARIANTS: INV200-INV208
TESTS: T200.*
"""

from typing import Literal, Optional, cast

import typer
from rich.console import Console

from phantom_pip import __version__
from phantom_pip.config import (
    create_default_config,
    get_config_path,
    load_config,
    merge_cli_options,
)
from phantom_pip.confirm import (
    confirm_batch_installation,
    display_blocked_message,
    display_skipped_message,
    display_summary,
)
from phantom_pip.delegate import delegate_to_pip
from phantom_pip.errors import PhantomPipError, SecurityError
from phantom_pip.extract import extract_packages, get_package_names
from phantom_pip.lists import filter_packages_by_lists
from phantom_pip.parser import parse_pip_args

# Import phantom-guard core
try:
    from phantom_guard import validate_package
    PHANTOM_GUARD_AVAILABLE = True
except ImportError:
    PHANTOM_GUARD_AVAILABLE = False
    validate_package = None  # type: ignore[assignment]

app = typer.Typer(
    name="phantom-pip",
    help="pip with slopsquatting protection - Phantom Guard v0.3.0",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"[bold green]phantom-pip[/bold green] {__version__}")
        console.print("[dim]Powered by Phantom Guard - Slopsquatting Detection[/dim]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", callback=version_callback, is_eager=True
    ),
) -> None:
    """phantom-pip: pip with slopsquatting protection."""
    pass


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def install(
    ctx: typer.Context,
    yes: bool = typer.Option(False, "-y", "--yes", help="Auto-approve risky packages"),
    skip_validation: bool = typer.Option(
        False, "--skip-validation", help="Skip phantom-guard validation"
    ),
    mode: Optional[str] = typer.Option(
        None, "--mode", help="Override mode: interactive|warn|block|silent"
    ),
    threshold: Optional[float] = typer.Option(
        None, "--threshold", help="Risk score threshold (0.0-1.0)"
    ),
) -> None:
    """
    Install packages with slopsquatting protection.

    All pip install arguments are supported and passed through.
    """
    # Collect all arguments
    args = ["install"] + ctx.args

    # Skip validation mode
    if skip_validation:
        exit_code = delegate_to_pip(args)
        raise typer.Exit(exit_code)

    # Load and merge configuration
    config = load_config()
    config = merge_cli_options(
        config,
        yes=yes,
        mode=mode,
        threshold=threshold,
    )

    # Check if validation is enabled
    if not config.enabled:
        exit_code = delegate_to_pip(args)
        raise typer.Exit(exit_code)

    # Check phantom-guard availability
    if not PHANTOM_GUARD_AVAILABLE:
        console.print("[yellow]phantom-guard not installed, skipping validation[/yellow]")
        exit_code = delegate_to_pip(args)
        raise typer.Exit(exit_code)

    try:
        # Parse arguments
        parsed = parse_pip_args(args)

        # Extract packages to validate
        extracted = extract_packages(parsed)
        package_names = get_package_names(extracted)

        if not package_names:
            # No packages to validate (e.g., -e . only)
            exit_code = delegate_to_pip(args)
            raise typer.Exit(exit_code)

        # Filter by allowlist/blocklist
        allowed, blocked, to_validate = filter_packages_by_lists(
            package_names,
            config.allowlist,
            config.blocklist,
        )

        # Handle blocked packages
        if blocked:
            for pkg in blocked:
                display_blocked_message(pkg, "Package is in blocklist")
            if config.mode == "block":
                console.print(f"\n[red]Blocked {len(blocked)} package(s). Aborting.[/red]")
                raise typer.Exit(1)

        # Validate remaining packages
        results: dict[str, object] = {}
        if to_validate and validate_package is not None:
            console.print("[dim]Validating packages...[/dim]")
            for pkg in to_validate:
                try:
                    registry_typed = cast(Literal["pypi", "npm", "crates"], config.registry)
                    risk = validate_package(pkg, registry=registry_typed)
                    if risk:
                        results[pkg] = risk
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not validate {pkg}: {e}[/yellow]")

        # Handle based on mode
        if config.mode == "silent":
            # Log only, proceed with installation
            pass
        elif config.mode == "warn":
            # Show warnings but don't block
            if results:
                display_summary(results)
        elif config.mode == "block":
            # Block any risky packages
            risky = {
                k: v for k, v in results.items()
                if getattr(v, "risk_score", 0.0) >= config.threshold
            }
            if risky:
                display_summary(risky)
                console.print(f"\n[red]Blocked {len(risky)} risky package(s). Aborting.[/red]")
                raise typer.Exit(1)
        else:  # interactive (default)
            # Prompt for confirmation
            if results:
                approved, rejected = confirm_batch_installation(
                    results,
                    auto_approve=config.auto_approve,
                )
                if rejected:
                    display_skipped_message(rejected)

        # Delegate to pip
        exit_code = delegate_to_pip(args)
        raise typer.Exit(exit_code)

    except SecurityError as e:
        console.print(f"[bold red]SECURITY ERROR:[/bold red] {e}")
        raise typer.Exit(2) from None
    except PhantomPipError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"[bold green]phantom-pip[/bold green] {__version__}")
    console.print("[dim]Powered by Phantom Guard - Slopsquatting Detection[/dim]")


@app.command(name="config")
def config_cmd(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    init: bool = typer.Option(False, "--init", help="Create default config file"),
) -> None:
    """Manage phantom-pip configuration."""
    if init:
        path = create_default_config()
        console.print(f"[green]Created config file:[/green] {path}")
    elif show:
        config = load_config()
        console.print("[bold]Configuration:[/bold]")
        console.print(f"  enabled: {config.enabled}")
        console.print(f"  mode: {config.mode}")
        console.print(f"  threshold: {config.threshold}")
        console.print(f"  allowlist: {config.allowlist}")
        console.print(f"  blocklist: {config.blocklist}")
        console.print(f"\n[dim]Config file: {get_config_path()}[/dim]")
    else:
        console.print("Use --show to view config or --init to create default")


# Passthrough commands - delegate directly to pip
@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def uninstall(ctx: typer.Context) -> None:
    """Uninstall packages (passthrough to pip)."""
    exit_code = delegate_to_pip(["uninstall"] + ctx.args)
    raise typer.Exit(exit_code)


@app.command(
    name="list",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def list_packages(ctx: typer.Context) -> None:
    """List installed packages (passthrough to pip)."""
    exit_code = delegate_to_pip(["list"] + ctx.args)
    raise typer.Exit(exit_code)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def show(ctx: typer.Context) -> None:
    """Show package information (passthrough to pip)."""
    exit_code = delegate_to_pip(["show"] + ctx.args)
    raise typer.Exit(exit_code)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def freeze(ctx: typer.Context) -> None:
    """Output installed packages (passthrough to pip)."""
    exit_code = delegate_to_pip(["freeze"] + ctx.args)
    raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()
