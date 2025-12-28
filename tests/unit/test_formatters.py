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
