"""
Interactive confirmation flow for risky packages.

IMPLEMENTS: S203
INVARIANTS: INV201 (respects --yes flag)
TESTS: T203.*
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

# Handle phantom_guard import gracefully
try:
    from phantom_guard import PackageRisk
    PHANTOM_GUARD_AVAILABLE = True
except ImportError:
    PHANTOM_GUARD_AVAILABLE = False

    # Define minimal PackageRisk for when phantom-guard not installed
    @dataclass
    class PackageRisk:  # type: ignore[no-redef]
        """Minimal PackageRisk when phantom-guard not available."""
        name: str = ""
        risk_level: str = "UNKNOWN"
        risk_score: float = 0.0
        signals: list[str] = field(default_factory=list)
        recommendation: Optional[str] = None


console = Console()


def get_risk_color(risk_level: str) -> str:
    """Get color for risk level."""
    colors = {
        "SAFE": "green",
        "SUSPICIOUS": "yellow",
        "HIGH_RISK": "red",
        "NOT_FOUND": "red",
        "ERROR": "dim",
        "UNKNOWN": "dim",
    }
    return colors.get(risk_level, "white")


def get_risk_icon(risk_level: str) -> str:
    """Get icon for risk level."""
    icons = {
        "SAFE": "[green]✓[/green]",
        "SUSPICIOUS": "[yellow]⚠[/yellow]",
        "HIGH_RISK": "[red]✗[/red]",
        "NOT_FOUND": "[red]?[/red]",
        "ERROR": "[dim]![/dim]",
        "UNKNOWN": "[dim]?[/dim]",
    }
    return icons.get(risk_level, " ")


def display_risk(package: str, risk: Any) -> None:
    """
    Display risk assessment to user.

    Shows formatted risk information with colors and signals.
    """
    risk_level = getattr(risk, "risk_level", "UNKNOWN")
    risk_score = getattr(risk, "risk_score", 0.0)
    signals = getattr(risk, "signals", [])
    recommendation = getattr(risk, "recommendation", None)

    color = get_risk_color(risk_level)
    icon = get_risk_icon(risk_level)

    # Create risk panel
    content = []
    content.append(f"[bold]Package:[/bold] {package}")
    content.append("[bold]Registry:[/bold] pypi")
    content.append(f"[bold]Status:[/bold] [{color}]{risk_level}[/{color}] {icon}")
    content.append("")
    content.append(f"[bold]Risk Score:[/bold] [{color}]{risk_score:.2f}[/{color}]")

    if signals:
        content.append("")
        content.append("[bold]Signals:[/bold]")
        for signal in signals:
            content.append(f"  • {signal}")

    if recommendation:
        rec_color = "red" if recommendation in ("BLOCK", "DO NOT INSTALL") else "yellow"
        content.append("")
        content.append(f"[bold]Recommendation:[/bold] [{rec_color}]{recommendation}[/{rec_color}]")

    panel = Panel(
        "\n".join(content),
        title="[bold]Phantom Guard Analysis[/bold]",
        border_style=color,
        box=box.ROUNDED,
    )
    console.print(panel)


def display_summary(results: dict[str, Any]) -> None:
    """
    Display summary table of all validation results.

    Args:
        results: Dict of package name to PackageRisk
    """
    table = Table(
        title="[bold]Validation Summary[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
    )
    table.add_column("Package", style="cyan")
    table.add_column("Risk Level", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Signals", justify="right")

    for name, risk in results.items():
        risk_level = getattr(risk, "risk_level", "UNKNOWN")
        risk_score = getattr(risk, "risk_score", 0.0)
        signals = getattr(risk, "signals", [])

        color = get_risk_color(risk_level)
        icon = get_risk_icon(risk_level)
        table.add_row(
            name,
            f"[{color}]{risk_level}[/{color}] {icon}",
            f"[{color}]{risk_score:.2f}[/{color}]",
            str(len(signals)),
        )

    console.print(table)


def confirm_installation(
    package: str,
    risk: Any,
    auto_approve: bool = False,
) -> bool:
    """
    Prompt user to confirm risky installation.

    INV201: If auto_approve is True, always returns True.

    Args:
        package: Package name
        risk: Risk assessment result
        auto_approve: Skip confirmation (--yes flag)

    Returns:
        True if user confirms, False otherwise
    """
    # INV201: Respect --yes flag
    if auto_approve:
        return True

    risk_level = getattr(risk, "risk_level", "UNKNOWN")

    # Safe packages don't need confirmation
    if risk_level == "SAFE":
        return True

    # Display risk information
    display_risk(package, risk)

    # Different prompts based on risk level
    if risk_level in ("HIGH_RISK", "NOT_FOUND"):
        console.print("\n[bold red]WARNING: This package appears to be dangerous![/bold red]")
        return Confirm.ask(
            "[bold]Proceed anyway?[/bold]",
            default=False,
            console=console,
        )
    else:  # SUSPICIOUS or other
        return Confirm.ask(
            "[bold]Proceed with installation?[/bold]",
            default=True,
            console=console,
        )


def confirm_batch_installation(
    results: dict[str, Any],
    auto_approve: bool = False,
) -> tuple[list[str], list[str]]:
    """
    Confirm installation of multiple packages.

    INV201: If auto_approve is True, approves all.

    Args:
        results: Dict of package name to PackageRisk
        auto_approve: Skip all confirmations

    Returns:
        Tuple of (approved packages, rejected packages)
    """
    # INV201: Auto-approve all
    if auto_approve:
        return list(results.keys()), []

    approved: list[str] = []
    rejected: list[str] = []

    # Categorize packages
    safe = {k: v for k, v in results.items() if getattr(v, "risk_level", "") == "SAFE"}
    risky = {k: v for k, v in results.items() if getattr(v, "risk_level", "") != "SAFE"}

    # Safe packages auto-approved
    approved.extend(safe.keys())

    if not risky:
        return approved, rejected

    # Show summary for risky packages
    console.print("\n[bold yellow]Risky packages detected:[/bold yellow]\n")
    display_summary(risky)

    # Ask for each risky package
    for name, risk in risky.items():
        console.print()  # Blank line
        if confirm_installation(name, risk, auto_approve=False):
            approved.append(name)
        else:
            rejected.append(name)

    return approved, rejected


def display_blocked_message(package: str, reason: str) -> None:
    """Display message for blocked package."""
    console.print(Panel(
        f"[bold red]BLOCKED[/bold red]: {package}\n\n"
        f"Reason: {reason}\n\n"
        "[dim]Use --skip-validation to bypass (not recommended)[/dim]",
        title="[bold red]Installation Blocked[/bold red]",
        border_style="red",
    ))


def display_skipped_message(packages: list[str]) -> None:
    """Display message for skipped packages."""
    if packages:
        console.print(f"\n[yellow]Skipped {len(packages)} package(s): {', '.join(packages)}[/yellow]")
