"""
IMPLEMENTS: S011
CLI output formatting with Rich.
Full UI/UX features from BRANDING_GUIDE.md - Phantom Mocha theme.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.text import Text

from phantom_guard.core.types import PackageRisk, Recommendation

if TYPE_CHECKING:
    from collections.abc import Sequence

# =============================================================================
# COLOR SCHEME - Phantom Mocha Theme (WCAG AAA Compliant)
# =============================================================================

COLORS = {
    Recommendation.SAFE: "#A6E3A1",  # Phantom Green
    Recommendation.SUSPICIOUS: "#F9E2AF",  # Spectral Amber
    Recommendation.HIGH_RISK: "#F38BA8",  # Danger Rose
    Recommendation.NOT_FOUND: "#89B4FA",  # Mist Blue
}

# =============================================================================
# ICONS (Unicode with ASCII fallback for Windows legacy console)
# =============================================================================

# Unicode icons for modern terminals
UNICODE_ICONS = {
    Recommendation.SAFE: "\u2713",  # ✓ checkmark
    Recommendation.SUSPICIOUS: "\u26a0",  # ⚠ warning
    Recommendation.HIGH_RISK: "\u2717",  # ✗ x mark
    Recommendation.NOT_FOUND: "\u2753",  # ❓ question mark
}

# ASCII fallback icons for Windows legacy console (cp1252)
ASCII_ICONS = {
    Recommendation.SAFE: "+",
    Recommendation.SUSPICIOUS: "!",
    Recommendation.HIGH_RISK: "X",
    Recommendation.NOT_FOUND: "?",
}


def _can_use_unicode() -> bool:
    """Check if the console can handle Unicode output."""
    import sys

    # Check if stdout encoding supports Unicode
    encoding = getattr(sys.stdout, "encoding", "") or ""
    return encoding.lower() in ("utf-8", "utf8", "utf-16", "utf-16-le", "utf-16-be")


def get_icons() -> dict[Recommendation, str]:
    """Get appropriate icons based on terminal capabilities."""
    if _can_use_unicode():
        return UNICODE_ICONS
    return ASCII_ICONS


# Default icons (computed at import time)
ICONS = get_icons()

# Tree formatting characters
TREE_LAST = "\u2514\u2500" if _can_use_unicode() else "`-"  # └─ or `-
TREE_MID = "\u251c\u2500" if _can_use_unicode() else "|-"  # ├─ or |-
BULLET = "\u2022" if _can_use_unicode() else "*"  # • or *
LINE_CHAR = "\u2500" if _can_use_unicode() else "-"  # ─ or -
GHOST = "\U0001f47b " if _can_use_unicode() else ""  # 👻 or empty

# =============================================================================
# THEME STYLES - Rich Theme Integration
# =============================================================================

STYLES = {
    Recommendation.SAFE: "status.safe",
    Recommendation.SUSPICIOUS: "status.suspicious",
    Recommendation.HIGH_RISK: "status.high_risk",
    Recommendation.NOT_FOUND: "status.not_found",
}


# =============================================================================
# PANEL DISPLAY FUNCTIONS
# =============================================================================


def show_warning_panel(
    console: Console,
    package: str,
    signals: Sequence[str],
) -> None:
    """
    Display a warning panel for suspicious packages.

    Args:
        console: Rich console for output
        package: Package name that triggered the warning
        signals: List of signal descriptions to display
    """
    content = Text()
    content.append("Package ", style="#CDD6F4")  # phantom.text
    content.append(f"'{package}'", style="bold #F9E2AF")
    content.append(" requires review\n\n", style="#CDD6F4")

    content.append("Signals detected:\n", style="#A6ADC8")  # phantom.dim
    for signal in signals:
        content.append(f"  {BULLET} {signal}\n", style="#F9E2AF")

    console.print(
        Panel(
            content,
            title="[bold #F9E2AF]\u26a0 WARNING[/]",
            border_style="#F9E2AF",
            padding=(1, 2),
        )
    )


def show_danger_panel(
    console: Console,
    package: str,
    signals: Sequence[str],
) -> None:
    """
    Display a danger panel for high-risk packages.

    Args:
        console: Rich console for output
        package: Package name that triggered the alert
        signals: List of critical signal descriptions
    """
    content = Text()
    content.append("Package ", style="#CDD6F4")  # phantom.text
    content.append(f"'{package}'", style="bold #F38BA8")
    content.append(" is HIGH RISK\n\n", style="#CDD6F4")

    content.append("Critical signals:\n", style="#A6ADC8")  # phantom.dim
    for signal in signals:
        content.append(f"  {BULLET} {signal}\n", style="#F38BA8")

    content.append("\n")
    content.append("Recommendation: ", style="#CDD6F4")
    content.append("DO NOT INSTALL", style="bold #F38BA8")

    console.print(
        Panel(
            content,
            title="[bold #F38BA8]\u2717 HIGH RISK[/]",
            border_style="#F38BA8",
            padding=(1, 2),
        )
    )


# =============================================================================
# PROGRESS DISPLAY
# =============================================================================


def create_scanner_progress(console: Console) -> Progress:
    """
    Create a themed progress bar with ghost spinner.

    Args:
        console: Rich console for progress display

    Returns:
        Configured Progress object with Phantom theme styling
    """
    ghost_prefix = f"[#CBA6F7]{GHOST}[/#CBA6F7]" if GHOST else ""
    return Progress(
        SpinnerColumn(spinner_name="dots", style="#CBA6F7"),
        TextColumn(f"{ghost_prefix} {{task.description}}"),
        BarColumn(
            complete_style="#CBA6F7",
            finished_style="#A6E3A1",
            pulse_style="#B4BEFE",
        ),
        console=console,
    )


# =============================================================================
# RESULT DISPLAY WITH SIGNALS
# =============================================================================


def show_result_with_signals(
    console: Console,
    result: PackageRisk,
    verbose: bool = False,
) -> None:
    """
    Display a package result with icon, colors, and optional signal tree.

    Args:
        console: Rich console for output
        result: Package risk assessment to display
        verbose: Show detailed signal information even for safe packages
    """
    color = COLORS[result.recommendation]
    icon = ICONS[result.recommendation]

    # Main result line
    text = Text()
    text.append(f"  {icon} ", style=color)
    text.append(f"{result.name:<30} ", style=f"bold {color}")
    text.append(f"{result.recommendation.value:<12}", style=color)
    text.append(f"[{result.risk_score:.2f}]", style="#A6ADC8")  # phantom.dim

    console.print(text)

    # Show signals for verbose mode or risky packages
    should_show_signals = verbose or result.recommendation in (
        Recommendation.HIGH_RISK,
        Recommendation.SUSPICIOUS,
    )

    if should_show_signals and result.signals:
        signals_list = list(result.signals)
        for i, signal in enumerate(signals_list):
            is_last = i == len(signals_list) - 1
            prefix = TREE_LAST if is_last else TREE_MID
            console.print(
                f"      {prefix} {signal.type.value}: {signal.message}",
                style="#A6ADC8",
            )


# =============================================================================
# SUMMARY DISPLAY
# =============================================================================


def show_summary(
    console: Console,
    results: Sequence[PackageRisk],
    elapsed_ms: float,
) -> None:
    """
    Display scan summary with colored counts.

    Args:
        console: Rich console for output
        results: List of package risk assessments
        elapsed_ms: Total elapsed time in milliseconds
    """
    # Count results by recommendation
    safe_count = sum(1 for r in results if r.recommendation == Recommendation.SAFE)
    suspicious_count = sum(1 for r in results if r.recommendation == Recommendation.SUSPICIOUS)
    high_risk_count = sum(1 for r in results if r.recommendation == Recommendation.HIGH_RISK)
    total = len(results)

    # Build summary line
    summary = Text()
    summary.append(f"  {LINE_CHAR}" * 30 + "\n", style="#6C7086")  # phantom.overlay
    summary.append(
        f"  {GHOST}Complete in {elapsed_ms:.0f}ms | ",
        style="#A6ADC8",
    )  # ghost emoji + phantom.dim
    summary.append(f"{total} packages", style="#CDD6F4")  # phantom.text
    summary.append(" | ", style="#A6ADC8")
    summary.append(f"{safe_count} safe", style="bold #A6E3A1")  # status.safe
    summary.append(" | ", style="#A6ADC8")
    summary.append(
        f"{suspicious_count} suspicious",
        style="bold #F9E2AF",
    )  # status.suspicious
    summary.append(" | ", style="#A6ADC8")
    summary.append(
        f"{high_risk_count} high-risk",
        style="bold #F38BA8",
    )  # status.high_risk

    console.print(summary)


# =============================================================================
# OUTPUT FORMATTER CLASS
# =============================================================================


class OutputFormatter:
    """
    IMPLEMENTS: S011
    TEST: T010.05, T010.06

    Format and display validation results.
    """

    def __init__(
        self,
        console: Console,
        verbose: bool = False,
        quiet: bool = False,
    ) -> None:
        """
        Initialize the output formatter.

        Args:
            console: Rich console for output
            verbose: Show detailed signal information
            quiet: Show minimal output
        """
        self.console = console
        self.verbose = verbose
        self.quiet = quiet

    def print_result(self, risk: PackageRisk) -> None:
        """
        Print single package result.

        Args:
            risk: Package risk assessment to display
        """
        color = COLORS[risk.recommendation]
        icon = ICONS[risk.recommendation]

        # Quiet mode: just the essentials
        if self.quiet:
            self.console.print(f"{risk.name}: {risk.recommendation.value}")
            return

        # Standard output with themed colors
        text = Text()
        text.append(f"  {icon} ", style=color)
        text.append(f"{risk.name:<30} ", style=f"bold {color}")
        text.append(f"{risk.recommendation.value:<12}", style=color)
        text.append(f"[{risk.risk_score:.2f}]", style="#A6ADC8")

        self.console.print(text)

        # Verbose: show signals with tree formatting
        if self.verbose and risk.signals:
            signals_list = list(risk.signals)
            for i, signal in enumerate(signals_list):
                is_last = i == len(signals_list) - 1
                prefix = TREE_LAST if is_last else TREE_MID
                self.console.print(
                    f"      {prefix} {signal.type.value}",
                    style="#A6ADC8",
                )

    def print_scanning(self, package: str) -> Progress:
        """
        Show scanning progress with ghost spinner.

        Args:
            package: Package name being scanned

        Returns:
            Progress object for context manager usage
        """
        ghost_text = f"{GHOST}Scanning {package}..." if GHOST else f"Scanning {package}..."
        return Progress(
            SpinnerColumn(spinner_name="dots", style="#CBA6F7"),
            TextColumn(f"[#CBA6F7]{ghost_text}[/#CBA6F7]"),
            console=self.console,
        )

    def print_error(self, message: str) -> None:
        """
        Print error message.

        Args:
            message: Error message to display
        """
        self.console.print(f"[#F38BA8]Error:[/#F38BA8] {message}")

    def print_result_with_signals(self, risk: PackageRisk) -> None:
        """
        Print result with signal tree for risky packages.

        Args:
            risk: Package risk assessment to display
        """
        show_result_with_signals(self.console, risk, self.verbose)

    def print_summary(
        self,
        results: Sequence[PackageRisk],
        elapsed_ms: float,
    ) -> None:
        """
        Print summary of scan results.

        Args:
            results: List of package risk assessments
            elapsed_ms: Total elapsed time in milliseconds
        """
        show_summary(self.console, results, elapsed_ms)
