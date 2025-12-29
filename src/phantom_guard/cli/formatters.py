"""
IMPLEMENTS: S018-S019
Output formatters for different formats.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from rich.console import Console
from rich.text import Text

if TYPE_CHECKING:
    from phantom_guard.core.types import PackageRisk


class OutputFormatter(ABC):
    """
    Base output formatter.

    All formatters must implement format_results and print_results methods.
    """

    @abstractmethod
    def format_results(self, results: list[PackageRisk]) -> str:
        """Format results for output."""
        ...  # pragma: no cover

    @abstractmethod
    def print_results(self, results: list[PackageRisk], console: Console) -> None:
        """Print results to console."""
        ...  # pragma: no cover


class TextFormatter(OutputFormatter):
    """
    IMPLEMENTS: S018
    TEST: T010.02

    Human-readable text output with colors and icons.
    """

    COLORS: ClassVar[dict[str, str]] = {
        "SAFE": "green",
        "SUSPICIOUS": "yellow",
        "HIGH_RISK": "red",
        "NOT_FOUND": "dim",
    }

    # Use ASCII-compatible icons for cross-platform support
    ICONS: ClassVar[dict[str, str]] = {
        "SAFE": "+",
        "SUSPICIOUS": "!",
        "HIGH_RISK": "x",
        "NOT_FOUND": "?",
    }

    def __init__(self, verbose: bool = False, quiet: bool = False) -> None:
        """
        Initialize text formatter.

        Args:
            verbose: Show detailed signal information
            quiet: Show minimal output
        """
        self.verbose = verbose
        self.quiet = quiet

    def format_results(self, results: list[PackageRisk]) -> str:
        """Format as text lines."""
        lines = []
        for risk in results:
            rec = risk.recommendation.value
            icon = self.ICONS.get(rec, " ")
            line = f"  {icon} {risk.name:<30} {rec:<12} [{risk.risk_score:.2f}]"
            lines.append(line)
        return "\n".join(lines)

    def print_results(self, results: list[PackageRisk], console: Console) -> None:
        """Print formatted results with Rich styling."""
        for risk in results:
            rec = risk.recommendation.value
            color = self.COLORS.get(rec, "white")
            icon = self.ICONS.get(rec, " ")

            text = Text()
            text.append(f"  {icon} ", style=color)
            text.append(f"{risk.name:<30} ", style="bold")
            text.append(f"{rec:<12}", style=color)
            text.append(f"[{risk.risk_score:.2f}]", style="dim")

            console.print(text)

            if self.verbose and risk.signals:
                for signal in risk.signals:
                    console.print(f"      `-- {signal.type.value}", style="dim")


class JSONFormatter(OutputFormatter):
    """
    IMPLEMENTS: S019
    TEST: T010.03
    EC: EC089

    Machine-readable JSON output.
    """

    def __init__(self, indent: int = 2) -> None:
        """
        Initialize JSON formatter.

        Args:
            indent: JSON indentation level
        """
        self.indent = indent

    def format_results(self, results: list[PackageRisk]) -> str:
        """Format as JSON string."""
        output = {
            "results": [self._serialize_risk(r) for r in results],
            "summary": self._create_summary(results),
        }
        return json.dumps(output, indent=self.indent)

    def print_results(self, results: list[PackageRisk], console: Console) -> None:
        """Print JSON output."""
        console.print(self.format_results(results))

    def _serialize_risk(self, risk: PackageRisk) -> dict[str, Any]:
        """Convert PackageRisk to JSON-serializable dict."""
        return {
            "name": risk.name,
            "recommendation": risk.recommendation.value.lower(),
            "risk_score": round(risk.risk_score, 4),
            "signals": [
                {
                    "type": s.type.value,
                    "weight": s.weight,
                    "metadata": s.metadata if s.metadata else {},
                }
                for s in risk.signals
            ],
        }

    def _create_summary(self, results: list[PackageRisk]) -> dict[str, int]:
        """Create summary statistics."""
        from collections import Counter

        counts = Counter(r.recommendation.value.lower() for r in results)
        return {
            "total": len(results),
            "safe": counts.get("safe", 0),
            "suspicious": counts.get("suspicious", 0),
            "high_risk": counts.get("high_risk", 0),
            "not_found": counts.get("not_found", 0),
        }


def get_formatter(output_format: str, **kwargs: bool | int) -> OutputFormatter:
    """
    Factory function to get appropriate formatter.

    Args:
        output_format: "text" or "json"
        **kwargs: Formatter-specific options (verbose, quiet, indent)

    Returns:
        Appropriate OutputFormatter instance

    Raises:
        ValueError: If output_format is unknown
    """
    formatters: dict[str, type[OutputFormatter]] = {
        "text": TextFormatter,
        "json": JSONFormatter,
    }

    formatter_cls = formatters.get(output_format.lower())
    if not formatter_cls:
        raise ValueError(f"Unknown output format: {output_format}")

    # Filter kwargs based on formatter class
    if formatter_cls == TextFormatter:
        valid_kwargs = {k: v for k, v in kwargs.items() if k in ("verbose", "quiet")}
    elif formatter_cls == JSONFormatter:
        valid_kwargs = {k: v for k, v in kwargs.items() if k in ("indent",)}
    else:  # pragma: no cover
        valid_kwargs = {}

    return formatter_cls(**valid_kwargs)
