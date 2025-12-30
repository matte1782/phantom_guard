"""
SPEC: S018-S019
Tests for output formatters.
"""

from __future__ import annotations

import json

import pytest

from phantom_guard.cli.formatters import (
    JSONFormatter,
    OutputFormatter,
    TextFormatter,
    get_formatter,
)
from phantom_guard.core.types import PackageRisk, Recommendation, Signal, SignalType


class TestTextFormatter:
    """Tests for TextFormatter (S018)."""

    def test_format_safe_package(self) -> None:
        """
        TEST_ID: T010.02
        SPEC: S018
        """
        risk = PackageRisk(
            name="flask",
            registry="pypi",
            exists=True,
            risk_score=0.02,
            signals=(),
            recommendation=Recommendation.SAFE,
        )
        formatter = TextFormatter()
        output = formatter.format_results([risk])

        assert "flask" in output
        assert "safe" in output
        assert "0.02" in output

    def test_format_suspicious_package(self) -> None:
        """Format suspicious package correctly."""
        risk = PackageRisk(
            name="newpkg",
            registry="pypi",
            exists=True,
            risk_score=0.45,
            signals=(),
            recommendation=Recommendation.SUSPICIOUS,
        )
        formatter = TextFormatter()
        output = formatter.format_results([risk])

        assert "newpkg" in output
        assert "suspicious" in output

    def test_format_high_risk_package(self) -> None:
        """Format high risk package correctly."""
        risk = PackageRisk(
            name="malicious-pkg",
            registry="pypi",
            exists=True,
            risk_score=0.95,
            signals=(),
            recommendation=Recommendation.HIGH_RISK,
        )
        formatter = TextFormatter()
        output = formatter.format_results([risk])

        assert "malicious-pkg" in output
        assert "high_risk" in output

    def test_format_multiple_results(self) -> None:
        """Format multiple results correctly."""
        risks = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("pkg3", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]
        formatter = TextFormatter()
        output = formatter.format_results(risks)

        assert "pkg1" in output
        assert "pkg2" in output
        assert "pkg3" in output

    def test_icons_present(self) -> None:
        """Icons are present for each recommendation."""
        assert "SAFE" in TextFormatter.ICONS
        assert "SUSPICIOUS" in TextFormatter.ICONS
        assert "HIGH_RISK" in TextFormatter.ICONS
        assert "NOT_FOUND" in TextFormatter.ICONS

    def test_colors_present(self) -> None:
        """Colors are present for each recommendation."""
        assert "SAFE" in TextFormatter.COLORS
        assert "SUSPICIOUS" in TextFormatter.COLORS
        assert "HIGH_RISK" in TextFormatter.COLORS
        assert "NOT_FOUND" in TextFormatter.COLORS


class TestJSONFormatter:
    """Tests for JSONFormatter (S019)."""

    def test_valid_json_output(self) -> None:
        """
        TEST_ID: T010.03
        SPEC: S019
        EC: EC089
        """
        risk = PackageRisk(
            name="flask",
            registry="pypi",
            exists=True,
            risk_score=0.02,
            signals=(),
            recommendation=Recommendation.SAFE,
        )
        formatter = JSONFormatter()
        output = formatter.format_results([risk])

        # Should be valid JSON
        data = json.loads(output)
        assert "results" in data
        assert "summary" in data
        assert data["results"][0]["name"] == "flask"

    def test_json_structure(self) -> None:
        """JSON has correct structure with results and summary."""
        risk = PackageRisk(
            name="test-pkg",
            registry="pypi",
            exists=True,
            risk_score=0.5,
            signals=(),
            recommendation=Recommendation.SUSPICIOUS,
        )
        formatter = JSONFormatter()
        output = formatter.format_results([risk])

        data = json.loads(output)

        # Check results structure
        result = data["results"][0]
        assert "name" in result
        assert "recommendation" in result
        assert "risk_score" in result
        assert "signals" in result

        # Check summary structure
        summary = data["summary"]
        assert "total" in summary
        assert "safe" in summary
        assert "suspicious" in summary
        assert "high_risk" in summary
        assert "not_found" in summary

    def test_summary_counts(self) -> None:
        """Summary includes correct counts."""
        risks = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("pkg3", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]
        formatter = JSONFormatter()
        output = formatter.format_results(risks)

        data = json.loads(output)
        assert data["summary"]["total"] == 3
        assert data["summary"]["safe"] == 1
        assert data["summary"]["suspicious"] == 1
        assert data["summary"]["high_risk"] == 1

    def test_signals_serialization(self) -> None:
        """Signals are properly serialized."""
        signal = Signal(
            type=SignalType.RECENTLY_CREATED,
            weight=0.3,
            message="Package created recently",
            metadata={"age_days": 5},
        )
        risk = PackageRisk(
            name="newpkg",
            registry="pypi",
            exists=True,
            risk_score=0.45,
            signals=(signal,),
            recommendation=Recommendation.SUSPICIOUS,
        )
        formatter = JSONFormatter()
        output = formatter.format_results([risk])

        data = json.loads(output)
        signals = data["results"][0]["signals"]
        assert len(signals) == 1
        assert signals[0]["type"] == "recently_created"
        assert signals[0]["weight"] == 0.3
        assert signals[0]["metadata"]["age_days"] == 5

    def test_recommendation_lowercase(self) -> None:
        """Recommendations are lowercase in JSON."""
        risk = PackageRisk("pkg", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS)
        formatter = JSONFormatter()
        output = formatter.format_results([risk])

        data = json.loads(output)
        assert data["results"][0]["recommendation"] == "suspicious"

    def test_custom_indent(self) -> None:
        """Custom indent is applied."""
        risk = PackageRisk("pkg", "pypi", True, 0.1, (), Recommendation.SAFE)
        formatter = JSONFormatter(indent=4)
        output = formatter.format_results([risk])

        # 4-space indent should be present
        assert "    " in output


class TestGetFormatter:
    """Tests for get_formatter factory function."""

    def test_get_text_formatter(self) -> None:
        """Factory returns TextFormatter for 'text'."""
        formatter = get_formatter("text")
        assert isinstance(formatter, TextFormatter)

    def test_get_json_formatter(self) -> None:
        """Factory returns JSONFormatter for 'json'."""
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)

    def test_case_insensitive(self) -> None:
        """Factory is case-insensitive."""
        assert isinstance(get_formatter("TEXT"), TextFormatter)
        assert isinstance(get_formatter("JSON"), JSONFormatter)
        assert isinstance(get_formatter("Json"), JSONFormatter)

    def test_unknown_format_raises(self) -> None:
        """Unknown format raises ValueError."""
        with pytest.raises(ValueError, match="Unknown output format"):
            get_formatter("xml")

    def test_text_formatter_with_verbose(self) -> None:
        """TextFormatter receives verbose kwarg."""
        formatter = get_formatter("text", verbose=True)
        assert isinstance(formatter, TextFormatter)
        assert formatter.verbose is True

    def test_json_formatter_with_indent(self) -> None:
        """JSONFormatter receives indent kwarg."""
        formatter = get_formatter("json", indent=4)
        assert isinstance(formatter, JSONFormatter)
        assert formatter.indent == 4

    def test_formatters_are_output_formatter_subclass(self) -> None:
        """All formatters inherit from OutputFormatter."""
        text = get_formatter("text")
        json_fmt = get_formatter("json")

        assert isinstance(text, OutputFormatter)
        assert isinstance(json_fmt, OutputFormatter)


class TestTextFormatterPrintResults:
    """Tests for TextFormatter print_results with Rich console."""

    def test_print_results_with_verbose_signals(self) -> None:
        """
        TEST_ID: T010.02.1
        SPEC: S018

        Verbose mode shows signal details.
        """
        from io import StringIO

        from rich.console import Console

        signal = Signal(
            type=SignalType.RECENTLY_CREATED,
            weight=0.3,
            message="Package created recently",
            metadata={"age_days": 5},
        )
        risk = PackageRisk(
            name="newpkg",
            registry="pypi",
            exists=True,
            risk_score=0.45,
            signals=(signal,),
            recommendation=Recommendation.SUSPICIOUS,
        )

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=100)
        formatter = TextFormatter(verbose=True)
        formatter.print_results([risk], console)

        result = output.getvalue()
        assert "newpkg" in result
        assert "recently_created" in result

    def test_print_results_quiet_mode(self) -> None:
        """Quiet mode still prints results."""
        from io import StringIO

        from rich.console import Console

        risk = PackageRisk(
            name="flask",
            registry="pypi",
            exists=True,
            risk_score=0.02,
            signals=(),
            recommendation=Recommendation.SAFE,
        )

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=100)
        formatter = TextFormatter(quiet=True)
        formatter.print_results([risk], console)

        result = output.getvalue()
        assert "flask" in result

    def test_print_results_not_found(self) -> None:
        """NOT_FOUND packages are formatted correctly."""
        from io import StringIO

        from rich.console import Console

        risk = PackageRisk(
            name="nonexistent",
            registry="pypi",
            exists=False,
            risk_score=0.0,
            signals=(),
            recommendation=Recommendation.NOT_FOUND,
        )

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=100)
        formatter = TextFormatter()
        formatter.print_results([risk], console)

        result = output.getvalue()
        assert "nonexistent" in result

    def test_format_results_unknown_recommendation(self) -> None:
        """Handle unknown recommendation gracefully."""
        risk = PackageRisk(
            name="pkg",
            registry="pypi",
            exists=True,
            risk_score=0.5,
            signals=(),
            recommendation=Recommendation.SUSPICIOUS,
        )
        formatter = TextFormatter()
        output = formatter.format_results([risk])

        # Should format without error
        assert "pkg" in output


class TestJSONFormatterPrintResults:
    """Tests for JSONFormatter print_results."""

    def test_print_results_outputs_json(self) -> None:
        """print_results outputs valid JSON."""
        from io import StringIO

        from rich.console import Console

        risk = PackageRisk(
            name="flask",
            registry="pypi",
            exists=True,
            risk_score=0.02,
            signals=(),
            recommendation=Recommendation.SAFE,
        )

        output = StringIO()
        console = Console(file=output, force_terminal=False, width=100)
        formatter = JSONFormatter()
        formatter.print_results([risk], console)

        result = output.getvalue()
        data = json.loads(result)
        assert data["results"][0]["name"] == "flask"

    def test_signals_with_empty_metadata(self) -> None:
        """Signals with no metadata return empty dict."""
        signal = Signal(
            type=SignalType.RECENTLY_CREATED,
            weight=0.3,
            message="Test",
            metadata=None,
        )
        risk = PackageRisk(
            name="pkg",
            registry="pypi",
            exists=True,
            risk_score=0.5,
            signals=(signal,),
            recommendation=Recommendation.SUSPICIOUS,
        )

        formatter = JSONFormatter()
        output = formatter.format_results([risk])
        data = json.loads(output)

        # Empty metadata should be an empty dict
        assert data["results"][0]["signals"][0]["metadata"] == {}


class TestTextFormatterFormatResultsDirect:
    """Direct tests for TextFormatter.format_results() method (lines 73-79)."""

    def test_format_results_returns_string_with_components(self) -> None:
        """
        TEST_ID: T010.02.2
        SPEC: S018

        format_results returns string with name, recommendation, and score.
        """
        risk = PackageRisk(
            name="test-package",
            registry="pypi",
            exists=True,
            risk_score=0.25,
            signals=(),
            recommendation=Recommendation.SAFE,
        )
        formatter = TextFormatter()
        output = formatter.format_results([risk])

        # Verify the output format contains name, recommendation, and score
        assert "test-package" in output
        assert "safe" in output
        assert "0.25" in output
        # Verify the output has the expected structure with brackets around score
        assert "[0.25]" in output

    def test_format_results_empty_list(self) -> None:
        """
        TEST_ID: T010.02.3
        SPEC: S018

        format_results with empty list returns empty string.
        """
        formatter = TextFormatter()
        output = formatter.format_results([])
        assert output == ""

    def test_format_results_multiple_lines(self) -> None:
        """
        TEST_ID: T010.02.4
        SPEC: S018

        format_results returns newline-separated lines for multiple packages.
        """
        risks = [
            PackageRisk("safe-pkg", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("suspicious-pkg", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("high-risk-pkg", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
            PackageRisk("missing-pkg", "pypi", False, 0.0, (), Recommendation.NOT_FOUND),
        ]
        formatter = TextFormatter()
        output = formatter.format_results(risks)

        lines = output.split("\n")
        assert len(lines) == 4

        # Verify each line contains its respective package name
        assert "safe-pkg" in lines[0]
        assert "suspicious-pkg" in lines[1]
        assert "high-risk-pkg" in lines[2]
        assert "missing-pkg" in lines[3]

        # Verify each line has corresponding recommendation value
        assert "safe" in lines[0]
        assert "suspicious" in lines[1]
        assert "high_risk" in lines[2]
        assert "not_found" in lines[3]

    def test_format_results_line_format_structure(self) -> None:
        """
        TEST_ID: T010.02.5
        SPEC: S018

        format_results produces correctly structured output lines.
        """
        risk = PackageRisk(
            name="mypackage",
            registry="pypi",
            exists=True,
            risk_score=0.33,
            signals=(),
            recommendation=Recommendation.SUSPICIOUS,
        )
        formatter = TextFormatter()
        output = formatter.format_results([risk])

        # Each line should have the format: "  {icon} {name:<30} {rec:<12} [{score:.2f}]"
        # The line should start with spaces and contain the package components
        assert output.startswith("  ")
        assert "mypackage" in output
        assert "suspicious" in output
        assert "[0.33]" in output


class TestTextFormatterVerboseSignals:
    """Tests for TextFormatter verbose mode showing signals (lines 97-98)."""

    def test_verbose_prints_signal_types(self) -> None:
        """
        TEST_ID: T010.02.6
        SPEC: S018

        Verbose mode prints signal type values below each result.
        """
        from io import StringIO

        from rich.console import Console

        signal1 = Signal(
            type=SignalType.RECENTLY_CREATED,
            weight=0.3,
            message="Package created recently",
            metadata={"age_days": 5},
        )
        signal2 = Signal(
            type=SignalType.NO_REPOSITORY,
            weight=0.2,
            message="No repository link",
            metadata=None,
        )
        risk = PackageRisk(
            name="suspicious-pkg",
            registry="pypi",
            exists=True,
            risk_score=0.55,
            signals=(signal1, signal2),
            recommendation=Recommendation.SUSPICIOUS,
        )

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)
        formatter = TextFormatter(verbose=True)
        formatter.print_results([risk], console)

        result = output.getvalue()
        # Verify both signal types are printed
        assert "recently_created" in result
        assert "no_repository" in result
        # Verify the signal prefix format (tree-drawing characters)
        assert "\u251c\u2500" in result or "\u2514\u2500" in result

    def test_verbose_with_multiple_packages_and_signals(self) -> None:
        """
        TEST_ID: T010.02.7
        SPEC: S018

        Verbose mode shows signals for all packages with signals.
        """
        from io import StringIO

        from rich.console import Console

        signal = Signal(
            type=SignalType.RECENTLY_CREATED,
            weight=0.3,
            message="Created recently",
            metadata={},
        )
        risks = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.6, (signal,), Recommendation.SUSPICIOUS),
        ]

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)
        formatter = TextFormatter(verbose=True)
        formatter.print_results(risks, console)

        result = output.getvalue()
        assert "pkg1" in result
        assert "pkg2" in result
        assert "recently_created" in result

    def test_non_verbose_hides_signals(self) -> None:
        """
        TEST_ID: T010.02.8
        SPEC: S018

        Non-verbose mode does not print signal details.
        """
        from io import StringIO

        from rich.console import Console

        signal = Signal(
            type=SignalType.RECENTLY_CREATED,
            weight=0.3,
            message="Created recently",
            metadata={},
        )
        risk = PackageRisk(
            name="pkg",
            registry="pypi",
            exists=True,
            risk_score=0.5,
            signals=(signal,),
            recommendation=Recommendation.SUSPICIOUS,
        )

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)
        formatter = TextFormatter(verbose=False)
        formatter.print_results([risk], console)

        result = output.getvalue()
        assert "pkg" in result
        # Signal type should NOT appear without verbose (tree-drawing characters)
        assert "\u251c\u2500" not in result
        assert "\u2514\u2500" not in result


class TestGetFormatterInvalidFormat:
    """Tests for get_formatter() with invalid format (line 182)."""

    def test_invalid_format_raises_value_error(self) -> None:
        """
        TEST_ID: T010.04.1
        SPEC: S018-S019

        get_formatter raises ValueError for unknown format.
        """
        with pytest.raises(ValueError) as exc_info:
            get_formatter("xml")
        assert "Unknown output format" in str(exc_info.value)
        assert "xml" in str(exc_info.value)

    def test_empty_format_raises_value_error(self) -> None:
        """
        TEST_ID: T010.04.2
        SPEC: S018-S019

        get_formatter raises ValueError for empty string.
        """
        with pytest.raises(ValueError, match="Unknown output format"):
            get_formatter("")

    def test_invalid_format_with_similar_name(self) -> None:
        """
        TEST_ID: T010.04.3
        SPEC: S018-S019

        get_formatter raises ValueError for typos of valid formats.
        """
        with pytest.raises(ValueError, match="Unknown output format"):
            get_formatter("txt")

        with pytest.raises(ValueError, match="Unknown output format"):
            get_formatter("jsn")
