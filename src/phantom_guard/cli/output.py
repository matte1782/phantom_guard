"""
IMPLEMENTS: S011
CLI output formatting with Rich.
"""

from __future__ import annotations

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from phantom_guard.core.types import PackageRisk, Recommendation

# Color scheme
COLORS = {
    Recommendation.SAFE: "green",
    Recommendation.SUSPICIOUS: "yellow",
    Recommendation.HIGH_RISK: "red",
    Recommendation.NOT_FOUND: "dim",
}

ICONS = {
    Recommendation.SAFE: "✓",
    Recommendation.SUSPICIOUS: "⚠",
    Recommendation.HIGH_RISK: "✗",
    Recommendation.NOT_FOUND: "?",
}


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

        # Standard output
        text = Text()
        text.append(f"  {icon} ", style=color)
        text.append(f"{risk.name:<20}", style="bold")
        text.append(f"{risk.recommendation.value:<12}", style=color)
        text.append(f"[{risk.risk_score:.2f}]", style="dim")

        self.console.print(text)

        # Verbose: show signals
        if self.verbose and risk.signals:
            for signal in risk.signals:
                self.console.print(f"      └─ {signal.type.value}", style="dim")

    def print_scanning(self, package: str) -> Progress:
        """
        Show scanning progress.

        Args:
            package: Package name being scanned

        Returns:
            Progress object for context manager usage
        """
        return Progress(
            SpinnerColumn(),
            TextColumn(f"[cyan]Scanning {package}..."),
            console=self.console,
        )

    def print_error(self, message: str) -> None:
        """
        Print error message.

        Args:
            message: Error message to display
        """
        self.console.print(f"[red]Error:[/red] {message}")
