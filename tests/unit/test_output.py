# SPEC: S011 - Output Formatting
# Gate 3: Test Design
"""
Unit tests for the CLI output formatting module.

SPEC_IDs: S011
TEST_IDs: T010.05, T010.06
"""

from __future__ import annotations

from io import StringIO

import pytest
from rich.console import Console

from phantom_guard.cli.output import (
    COLORS,
    ICONS,
    STYLES,
    OutputFormatter,
    create_scanner_progress,
    show_danger_panel,
    show_result_with_signals,
    show_summary,
    show_warning_panel,
)
from phantom_guard.core.types import PackageRisk, Recommendation, Signal, SignalType

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def string_console() -> Console:
    """Create a console that captures output to a string buffer."""
    return Console(file=StringIO(), force_terminal=True, width=120)


@pytest.fixture
def safe_package_risk() -> PackageRisk:
    """Create a sample SAFE package risk for testing."""
    return PackageRisk(
        name="flask",
        registry="pypi",
        exists=True,
        risk_score=0.1,
        signals=(),
        recommendation=Recommendation.SAFE,
        latency_ms=50.0,
    )


@pytest.fixture
def suspicious_package_risk() -> PackageRisk:
    """Create a sample SUSPICIOUS package risk for testing."""
    return PackageRisk(
        name="flaskk",
        registry="pypi",
        exists=True,
        risk_score=0.45,
        signals=(
            Signal(
                type=SignalType.TYPOSQUAT,
                weight=0.4,
                message="Similar to popular package 'flask'",
            ),
        ),
        recommendation=Recommendation.SUSPICIOUS,
        latency_ms=100.0,
    )


@pytest.fixture
def high_risk_package_risk() -> PackageRisk:
    """Create a sample HIGH_RISK package risk for testing."""
    return PackageRisk(
        name="malicious-pkg",
        registry="pypi",
        exists=True,
        risk_score=0.85,
        signals=(
            Signal(
                type=SignalType.KNOWN_MALICIOUS,
                weight=0.8,
                message="Package on malicious list",
            ),
            Signal(
                type=SignalType.RECENTLY_CREATED,
                weight=0.3,
                message="Created less than 7 days ago",
            ),
        ),
        recommendation=Recommendation.HIGH_RISK,
        latency_ms=150.0,
    )


@pytest.fixture
def not_found_package_risk() -> PackageRisk:
    """Create a sample NOT_FOUND package risk for testing."""
    return PackageRisk(
        name="nonexistent-pkg-12345",
        registry="pypi",
        exists=False,
        risk_score=0.0,
        signals=(
            Signal(
                type=SignalType.NOT_FOUND,
                weight=0.0,
                message="Package does not exist",
            ),
        ),
        recommendation=Recommendation.NOT_FOUND,
        latency_ms=75.0,
    )


# =============================================================================
# COLORS AND ICONS TESTS
# =============================================================================


class TestColorScheme:
    """Tests for output color and icon constants."""

    @pytest.mark.unit
    def test_colors_defined_for_all_recommendations(self) -> None:
        """
        TEST_ID: T011.01
        SPEC: S011

        Given: COLORS constant
        When: Checking all Recommendation values
        Then: Each has a defined color
        """
        for rec in Recommendation:
            assert rec in COLORS, f"Missing color for {rec}"
            assert isinstance(COLORS[rec], str)

    @pytest.mark.unit
    def test_icons_defined_for_all_recommendations(self) -> None:
        """
        TEST_ID: T011.02
        SPEC: S011

        Given: ICONS constant
        When: Checking all Recommendation values
        Then: Each has a defined icon
        """
        for rec in Recommendation:
            assert rec in ICONS, f"Missing icon for {rec}"
            assert isinstance(ICONS[rec], str)

    @pytest.mark.unit
    def test_safe_color_is_phantom_green(self) -> None:
        """
        TEST_ID: T011.03
        SPEC: S011

        Given: SAFE recommendation
        Then: Color is Phantom Green (#A6E3A1)
        """
        assert COLORS[Recommendation.SAFE] == "#A6E3A1"

    @pytest.mark.unit
    def test_suspicious_color_is_spectral_amber(self) -> None:
        """
        TEST_ID: T011.04
        SPEC: S011

        Given: SUSPICIOUS recommendation
        Then: Color is Spectral Amber (#F9E2AF)
        """
        assert COLORS[Recommendation.SUSPICIOUS] == "#F9E2AF"

    @pytest.mark.unit
    def test_high_risk_color_is_danger_rose(self) -> None:
        """
        TEST_ID: T011.05
        SPEC: S011

        Given: HIGH_RISK recommendation
        Then: Color is Danger Rose (#F38BA8)
        """
        assert COLORS[Recommendation.HIGH_RISK] == "#F38BA8"

    @pytest.mark.unit
    def test_not_found_color_is_mist_blue(self) -> None:
        """
        TEST_ID: T011.06
        SPEC: S011

        Given: NOT_FOUND recommendation
        Then: Color is Mist Blue (#89B4FA)
        """
        assert COLORS[Recommendation.NOT_FOUND] == "#89B4FA"

    @pytest.mark.unit
    def test_icons_are_unicode(self) -> None:
        """
        TEST_ID: T011.06b
        SPEC: S011

        Given: ICONS constant
        When: Checking icon values
        Then: Icons are Unicode symbols (not ASCII)
        """
        # Unicode icons from BRANDING_GUIDE.md
        assert ICONS[Recommendation.SAFE] == "\u2713"  # checkmark
        assert ICONS[Recommendation.SUSPICIOUS] == "\u26a0"  # warning
        assert ICONS[Recommendation.HIGH_RISK] == "\u2717"  # x mark
        assert ICONS[Recommendation.NOT_FOUND] == "\u2753"  # question mark

    @pytest.mark.unit
    def test_styles_defined_for_all_recommendations(self) -> None:
        """
        TEST_ID: T011.06c
        SPEC: S011

        Given: STYLES constant
        When: Checking all Recommendation values
        Then: Each has a defined theme style
        """
        for rec in Recommendation:
            assert rec in STYLES, f"Missing style for {rec}"
            assert isinstance(STYLES[rec], str)

        # Verify specific style mappings
        assert STYLES[Recommendation.SAFE] == "status.safe"
        assert STYLES[Recommendation.SUSPICIOUS] == "status.suspicious"
        assert STYLES[Recommendation.HIGH_RISK] == "status.high_risk"
        assert STYLES[Recommendation.NOT_FOUND] == "status.not_found"


# =============================================================================
# OUTPUTFORMATTER INITIALIZATION TESTS
# =============================================================================


class TestOutputFormatterInit:
    """Tests for OutputFormatter initialization."""

    @pytest.mark.unit
    def test_init_default_values(self, string_console: Console) -> None:
        """
        TEST_ID: T011.07
        SPEC: S011

        Given: OutputFormatter with only console
        When: Initialized with defaults
        Then: verbose=False, quiet=False
        """
        formatter = OutputFormatter(string_console)

        assert formatter.console is string_console
        assert formatter.verbose is False
        assert formatter.quiet is False

    @pytest.mark.unit
    def test_init_verbose_mode(self, string_console: Console) -> None:
        """
        TEST_ID: T011.08
        SPEC: S011

        Given: OutputFormatter with verbose=True
        Then: verbose flag is set
        """
        formatter = OutputFormatter(string_console, verbose=True)

        assert formatter.verbose is True
        assert formatter.quiet is False

    @pytest.mark.unit
    def test_init_quiet_mode(self, string_console: Console) -> None:
        """
        TEST_ID: T011.09
        SPEC: S011

        Given: OutputFormatter with quiet=True
        Then: quiet flag is set
        """
        formatter = OutputFormatter(string_console, quiet=True)

        assert formatter.verbose is False
        assert formatter.quiet is True

    @pytest.mark.unit
    def test_init_both_verbose_and_quiet(self, string_console: Console) -> None:
        """
        TEST_ID: T011.10
        SPEC: S011

        Given: OutputFormatter with both verbose=True and quiet=True
        Then: Both flags are set (caller responsibility to handle)
        """
        formatter = OutputFormatter(string_console, verbose=True, quiet=True)

        assert formatter.verbose is True
        assert formatter.quiet is True


# =============================================================================
# PRINT_RESULT TESTS - STANDARD MODE
# =============================================================================


class TestPrintResultStandard:
    """Tests for print_result in standard (non-quiet, non-verbose) mode."""

    @pytest.mark.unit
    def test_print_safe_package(
        self, string_console: Console, safe_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.11
        SPEC: S011

        Given: SAFE package risk
        When: print_result is called in standard mode
        Then: Output contains package name and recommendation
        """
        formatter = OutputFormatter(string_console)
        formatter.print_result(safe_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "flask" in output
        assert "safe" in output.lower()

    @pytest.mark.unit
    def test_print_suspicious_package(
        self, string_console: Console, suspicious_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.12
        SPEC: S011

        Given: SUSPICIOUS package risk
        When: print_result is called
        Then: Output contains package name and suspicious status
        """
        formatter = OutputFormatter(string_console)
        formatter.print_result(suspicious_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "flaskk" in output
        assert "suspicious" in output.lower()

    @pytest.mark.unit
    def test_print_high_risk_package(
        self, string_console: Console, high_risk_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.13
        SPEC: S011

        Given: HIGH_RISK package risk
        When: print_result is called
        Then: Output contains package name and high_risk status
        """
        formatter = OutputFormatter(string_console)
        formatter.print_result(high_risk_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "malicious-pkg" in output
        assert "high_risk" in output.lower()

    @pytest.mark.unit
    def test_print_not_found_package(
        self, string_console: Console, not_found_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.14
        SPEC: S011

        Given: NOT_FOUND package risk
        When: print_result is called
        Then: Output contains package name and not_found status
        """
        formatter = OutputFormatter(string_console)
        formatter.print_result(not_found_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "nonexistent-pkg-12345" in output
        assert "not_found" in output.lower()

    @pytest.mark.unit
    def test_print_result_includes_risk_score(
        self, string_console: Console, safe_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.15
        SPEC: S011

        Given: Any package risk
        When: print_result is called in standard mode
        Then: Output includes the risk score
        """
        formatter = OutputFormatter(string_console)
        formatter.print_result(safe_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Score is formatted as [0.10]
        assert "0.10" in output

    @pytest.mark.unit
    def test_print_result_standard_no_signals(
        self, string_console: Console, suspicious_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.16
        SPEC: S011

        Given: Package with signals
        When: print_result is called in standard mode (not verbose)
        Then: Signals are NOT shown
        """
        formatter = OutputFormatter(string_console)
        formatter.print_result(suspicious_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Signal details should not appear in standard mode
        assert "typosquat" not in output.lower()


# =============================================================================
# PRINT_RESULT TESTS - QUIET MODE
# =============================================================================


class TestPrintResultQuiet:
    """Tests for print_result in quiet mode."""

    @pytest.mark.unit
    def test_quiet_mode_minimal_output(
        self, string_console: Console, safe_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.17
        SPEC: S011
        EC: EC092

        Given: Package risk
        When: print_result is called with quiet=True
        Then: Output is minimal (just name: status)
        """
        formatter = OutputFormatter(string_console, quiet=True)
        formatter.print_result(safe_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Quiet mode outputs: "name: recommendation"
        assert "flask: safe" in output.lower()

    @pytest.mark.unit
    def test_quiet_mode_no_score(
        self, string_console: Console, safe_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.18
        SPEC: S011
        EC: EC092

        Given: Package risk
        When: print_result is called with quiet=True
        Then: Risk score is NOT shown
        """
        formatter = OutputFormatter(string_console, quiet=True)
        formatter.print_result(safe_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Score should not appear in quiet mode
        assert "[0.10]" not in output

    @pytest.mark.unit
    def test_quiet_mode_no_icons(
        self, string_console: Console, high_risk_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.19
        SPEC: S011
        EC: EC092

        Given: HIGH_RISK package
        When: print_result is called with quiet=True
        Then: No decorative icons in output
        """
        formatter = OutputFormatter(string_console, quiet=True)
        formatter.print_result(high_risk_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Quiet mode should have minimal formatting
        # Check that output is compact
        lines = [line for line in output.strip().split("\n") if line.strip()]
        assert len(lines) == 1

    @pytest.mark.unit
    def test_quiet_mode_all_recommendations(self, string_console: Console) -> None:
        """
        TEST_ID: T011.20
        SPEC: S011

        Given: All recommendation types
        When: print_result is called with quiet=True
        Then: Each outputs name: recommendation format
        """
        risks = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("pkg3", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
            PackageRisk("pkg4", "pypi", False, 0.0, (), Recommendation.NOT_FOUND),
        ]

        formatter = OutputFormatter(string_console, quiet=True)
        for risk in risks:
            formatter.print_result(risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "pkg1: safe" in output.lower()
        assert "pkg2: suspicious" in output.lower()
        assert "pkg3: high_risk" in output.lower()
        assert "pkg4: not_found" in output.lower()


# =============================================================================
# PRINT_RESULT TESTS - VERBOSE MODE
# =============================================================================


class TestPrintResultVerbose:
    """Tests for print_result in verbose mode."""

    @pytest.mark.unit
    def test_verbose_mode_shows_signals(
        self, string_console: Console, suspicious_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.21
        SPEC: S011
        EC: EC091

        Given: Package with signals
        When: print_result is called with verbose=True
        Then: Signals are displayed
        """
        formatter = OutputFormatter(string_console, verbose=True)
        formatter.print_result(suspicious_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Verbose mode shows signal types
        assert "typosquat" in output.lower()

    @pytest.mark.unit
    def test_verbose_mode_shows_multiple_signals(
        self, string_console: Console, high_risk_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.22
        SPEC: S011
        EC: EC091

        Given: Package with multiple signals
        When: print_result is called with verbose=True
        Then: All signals are displayed
        """
        formatter = OutputFormatter(string_console, verbose=True)
        formatter.print_result(high_risk_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Should show both signals
        assert "known_malicious" in output.lower()
        assert "recently_created" in output.lower()

    @pytest.mark.unit
    def test_verbose_mode_no_signals_package(
        self, string_console: Console, safe_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.23
        SPEC: S011

        Given: Package with empty signals tuple
        When: print_result is called with verbose=True
        Then: No signal lines are printed (but no error)
        """
        formatter = OutputFormatter(string_console, verbose=True)
        formatter.print_result(safe_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Should still show the main result line
        assert "flask" in output
        # But no signal indentation markers for empty signals
        lines = output.strip().split("\n")
        # Only 1 line (the main result), no signal lines
        assert len([line for line in lines if line.strip()]) == 1

    @pytest.mark.unit
    def test_verbose_mode_includes_score(
        self, string_console: Console, suspicious_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T011.24
        SPEC: S011

        Given: Package risk
        When: print_result is called with verbose=True
        Then: Risk score is still shown
        """
        formatter = OutputFormatter(string_console, verbose=True)
        formatter.print_result(suspicious_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "0.45" in output


# =============================================================================
# PRINT_SCANNING TESTS
# =============================================================================


class TestPrintScanning:
    """Tests for the print_scanning progress indicator."""

    @pytest.mark.unit
    def test_print_scanning_returns_progress(self, string_console: Console) -> None:
        """
        TEST_ID: T011.25
        SPEC: S011

        Given: OutputFormatter
        When: print_scanning is called
        Then: Returns a Progress object
        """
        from rich.progress import Progress

        formatter = OutputFormatter(string_console)
        progress = formatter.print_scanning("flask")

        assert isinstance(progress, Progress)

    @pytest.mark.unit
    def test_print_scanning_different_packages(self, string_console: Console) -> None:
        """
        TEST_ID: T011.26
        SPEC: S011

        Given: OutputFormatter
        When: print_scanning is called with different package names
        Then: Returns Progress objects for each
        """
        from rich.progress import Progress

        formatter = OutputFormatter(string_console)

        progress1 = formatter.print_scanning("flask")
        progress2 = formatter.print_scanning("requests")

        assert isinstance(progress1, Progress)
        assert isinstance(progress2, Progress)


# =============================================================================
# PRINT_ERROR TESTS
# =============================================================================


class TestPrintError:
    """Tests for error message output."""

    @pytest.mark.unit
    def test_print_error_basic(self, string_console: Console) -> None:
        """
        TEST_ID: T011.27
        SPEC: S011

        Given: Error message
        When: print_error is called
        Then: Output contains "Error:" prefix and the message
        """
        formatter = OutputFormatter(string_console)
        formatter.print_error("Something went wrong")

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "Error:" in output
        assert "Something went wrong" in output

    @pytest.mark.unit
    def test_print_error_with_special_chars(self, string_console: Console) -> None:
        """
        TEST_ID: T011.28
        SPEC: S011

        Given: Error message with special characters
        When: print_error is called
        Then: Message is displayed correctly
        """
        formatter = OutputFormatter(string_console)
        formatter.print_error("Package 'test-pkg' not found!")

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Rich may add ANSI codes around quoted strings, so check parts
        assert "Package" in output
        assert "test-pkg" in output
        assert "not found!" in output

    @pytest.mark.unit
    def test_print_error_empty_message(self, string_console: Console) -> None:
        """
        TEST_ID: T011.29
        SPEC: S011

        Given: Empty error message
        When: print_error is called
        Then: Outputs "Error:" with empty message (no crash)
        """
        formatter = OutputFormatter(string_console)
        formatter.print_error("")

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "Error:" in output


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestOutputFormatterIntegration:
    """Integration tests for output formatting workflows."""

    @pytest.mark.unit
    def test_multiple_results_sequential(self, string_console: Console) -> None:
        """
        TEST_ID: T011.30
        SPEC: S011

        Given: Multiple package risks
        When: print_result is called for each
        Then: All results are printed in order
        """
        risks = [
            PackageRisk("flask", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("requests", "pypi", True, 0.15, (), Recommendation.SAFE),
            PackageRisk("django", "pypi", True, 0.12, (), Recommendation.SAFE),
        ]

        formatter = OutputFormatter(string_console)
        for risk in risks:
            formatter.print_result(risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # All package names should appear
        assert "flask" in output
        assert "requests" in output
        assert "django" in output

    @pytest.mark.unit
    def test_mixed_recommendation_results(self, string_console: Console) -> None:
        """
        TEST_ID: T011.31
        SPEC: S011

        Given: Packages with different recommendations
        When: print_result is called for each
        Then: Each is formatted with correct status
        """
        risks = [
            PackageRisk("safe-pkg", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("sus-pkg", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("bad-pkg", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]

        formatter = OutputFormatter(string_console)
        for risk in risks:
            formatter.print_result(risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        output_lower = output.lower()

        assert "safe-pkg" in output_lower
        assert "sus-pkg" in output_lower
        assert "bad-pkg" in output_lower
        assert "safe" in output_lower
        assert "suspicious" in output_lower
        assert "high_risk" in output_lower

    @pytest.mark.unit
    def test_formatter_with_npm_registry(self, string_console: Console) -> None:
        """
        TEST_ID: T011.32
        SPEC: S011

        Given: Package from npm registry
        When: print_result is called
        Then: Formats correctly (registry agnostic)
        """
        npm_risk = PackageRisk(
            name="express",
            registry="npm",
            exists=True,
            risk_score=0.05,
            signals=(),
            recommendation=Recommendation.SAFE,
        )

        formatter = OutputFormatter(string_console)
        formatter.print_result(npm_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "express" in output

    @pytest.mark.unit
    def test_formatter_with_crates_registry(self, string_console: Console) -> None:
        """
        TEST_ID: T011.33
        SPEC: S011

        Given: Package from crates registry
        When: print_result is called
        Then: Formats correctly
        """
        crates_risk = PackageRisk(
            name="serde",
            registry="crates",
            exists=True,
            risk_score=0.02,
            signals=(),
            recommendation=Recommendation.SAFE,
        )

        formatter = OutputFormatter(string_console)
        formatter.print_result(crates_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "serde" in output


# =============================================================================
# NEW FUNCTION TESTS - BRANDING_GUIDE.md UI/UX Features
# =============================================================================


class TestShowWarningPanel:
    """Tests for show_warning_panel function."""

    @pytest.mark.unit
    def test_warning_panel_displays_package_name(self, string_console: Console) -> None:
        """
        TEST_ID: T011.34
        SPEC: S011

        Given: Package name and signals
        When: show_warning_panel is called
        Then: Output contains package name
        """
        show_warning_panel(string_console, "flask-utils", ["Low download count"])

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "flask-utils" in output

    @pytest.mark.unit
    def test_warning_panel_displays_signals(self, string_console: Console) -> None:
        """
        TEST_ID: T011.35
        SPEC: S011

        Given: Package name and multiple signals
        When: show_warning_panel is called
        Then: All signals are displayed
        """
        signals = ["Low download count", "Recently created"]
        show_warning_panel(string_console, "test-pkg", signals)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "Low download count" in output
        assert "Recently created" in output

    @pytest.mark.unit
    def test_warning_panel_has_warning_title(self, string_console: Console) -> None:
        """
        TEST_ID: T011.36
        SPEC: S011

        Given: show_warning_panel call
        Then: Output contains WARNING title
        """
        show_warning_panel(string_console, "test-pkg", ["Signal"])

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "WARNING" in output


class TestShowDangerPanel:
    """Tests for show_danger_panel function."""

    @pytest.mark.unit
    def test_danger_panel_displays_package_name(self, string_console: Console) -> None:
        """
        TEST_ID: T011.37
        SPEC: S011

        Given: Package name and signals
        When: show_danger_panel is called
        Then: Output contains package name
        """
        show_danger_panel(string_console, "malicious-pkg", ["Critical signal"])

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "malicious-pkg" in output

    @pytest.mark.unit
    def test_danger_panel_shows_do_not_install(self, string_console: Console) -> None:
        """
        TEST_ID: T011.38
        SPEC: S011

        Given: show_danger_panel call
        Then: Output contains "DO NOT INSTALL" recommendation
        """
        show_danger_panel(string_console, "bad-pkg", ["Malicious"])

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "DO NOT INSTALL" in output

    @pytest.mark.unit
    def test_danger_panel_has_high_risk_title(self, string_console: Console) -> None:
        """
        TEST_ID: T011.39
        SPEC: S011

        Given: show_danger_panel call
        Then: Output contains HIGH RISK title
        """
        show_danger_panel(string_console, "test-pkg", ["Signal"])

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "HIGH RISK" in output


class TestCreateScannerProgress:
    """Tests for create_scanner_progress function."""

    @pytest.mark.unit
    def test_create_scanner_progress_returns_progress(self, string_console: Console) -> None:
        """
        TEST_ID: T011.40
        SPEC: S011

        Given: Console
        When: create_scanner_progress is called
        Then: Returns a Progress object
        """
        from rich.progress import Progress

        progress = create_scanner_progress(string_console)

        assert isinstance(progress, Progress)


class TestShowResultWithSignals:
    """Tests for show_result_with_signals function."""

    @pytest.mark.unit
    def test_show_result_with_signals_safe_no_verbose(
        self,
        string_console: Console,
        safe_package_risk: PackageRisk,
    ) -> None:
        """
        TEST_ID: T011.41
        SPEC: S011

        Given: SAFE package risk
        When: show_result_with_signals is called with verbose=False
        Then: Shows result without signal tree
        """
        show_result_with_signals(string_console, safe_package_risk, verbose=False)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "flask" in output

    @pytest.mark.unit
    def test_show_result_with_signals_high_risk_shows_signals(
        self,
        string_console: Console,
        high_risk_package_risk: PackageRisk,
    ) -> None:
        """
        TEST_ID: T011.42
        SPEC: S011

        Given: HIGH_RISK package risk with signals
        When: show_result_with_signals is called (even without verbose)
        Then: Shows signals for risky packages
        """
        show_result_with_signals(string_console, high_risk_package_risk, verbose=False)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "malicious-pkg" in output
        # Should show signals even without verbose for HIGH_RISK
        assert "known_malicious" in output.lower()

    @pytest.mark.unit
    def test_show_result_with_signals_verbose_safe(
        self,
        string_console: Console,
    ) -> None:
        """
        TEST_ID: T011.43
        SPEC: S011

        Given: SAFE package with signals
        When: show_result_with_signals is called with verbose=True
        Then: Shows signals even for safe packages
        """
        safe_with_signals = PackageRisk(
            name="popular-pkg",
            registry="pypi",
            exists=True,
            risk_score=0.05,
            signals=(
                Signal(
                    type=SignalType.POPULAR_PACKAGE,
                    weight=-0.3,
                    message="Package is popular",
                ),
            ),
            recommendation=Recommendation.SAFE,
        )
        show_result_with_signals(string_console, safe_with_signals, verbose=True)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "popular-pkg" in output
        assert "popular_package" in output.lower()

    @pytest.mark.unit
    def test_show_result_with_signals_tree_formatting(
        self,
        string_console: Console,
        high_risk_package_risk: PackageRisk,
    ) -> None:
        """
        TEST_ID: T011.44
        SPEC: S011

        Given: Package with multiple signals
        When: show_result_with_signals is called
        Then: Uses tree formatting with branch prefixes
        """
        show_result_with_signals(string_console, high_risk_package_risk, verbose=True)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Check for tree branch characters (unicode)
        # Using unicode escape sequences for portability
        assert "\u2514\u2500" in output or "\u251c\u2500" in output


class TestShowSummary:
    """Tests for show_summary function."""

    @pytest.mark.unit
    def test_show_summary_displays_counts(self, string_console: Console) -> None:
        """
        TEST_ID: T011.45
        SPEC: S011

        Given: List of package results
        When: show_summary is called
        Then: Shows correct counts for each status
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg3", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("pkg4", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]

        show_summary(string_console, results, elapsed_ms=100.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "4 packages" in output
        assert "2 safe" in output
        assert "1 suspicious" in output
        assert "1 high-risk" in output

    @pytest.mark.unit
    def test_show_summary_displays_elapsed_time(self, string_console: Console) -> None:
        """
        TEST_ID: T011.46
        SPEC: S011

        Given: Elapsed time
        When: show_summary is called
        Then: Shows elapsed time in milliseconds
        """
        results = [PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE)]

        show_summary(string_console, results, elapsed_ms=234.5)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "235ms" in output or "234ms" in output  # Rounded

    @pytest.mark.unit
    def test_show_summary_contains_ghost_emoji(self, string_console: Console) -> None:
        """
        TEST_ID: T011.47
        SPEC: S011

        Given: show_summary call
        Then: Output contains ghost emoji for branding
        """
        results = [PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE)]

        show_summary(string_console, results, elapsed_ms=100.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Ghost emoji unicode
        assert "\U0001f47b" in output

    @pytest.mark.unit
    def test_show_summary_empty_results(self, string_console: Console) -> None:
        """
        TEST_ID: T011.48
        SPEC: S011

        Given: Empty results list
        When: show_summary is called
        Then: Shows 0 packages, no crash
        """
        show_summary(string_console, [], elapsed_ms=50.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "0 packages" in output
        assert "0 safe" in output
        assert "0 suspicious" in output
        assert "0 high-risk" in output


class TestOutputFormatterNewMethods:
    """Tests for new methods added to OutputFormatter class."""

    @pytest.mark.unit
    def test_print_result_with_signals_method(
        self,
        string_console: Console,
        high_risk_package_risk: PackageRisk,
    ) -> None:
        """
        TEST_ID: T011.49
        SPEC: S011

        Given: OutputFormatter
        When: print_result_with_signals is called
        Then: Delegates to show_result_with_signals correctly
        """
        formatter = OutputFormatter(string_console, verbose=True)
        formatter.print_result_with_signals(high_risk_package_risk)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "malicious-pkg" in output

    @pytest.mark.unit
    def test_print_summary_method(self, string_console: Console) -> None:
        """
        TEST_ID: T011.50
        SPEC: S011

        Given: OutputFormatter
        When: print_summary is called
        Then: Delegates to show_summary correctly
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]

        formatter = OutputFormatter(string_console)
        formatter.print_summary(results, elapsed_ms=150.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "2 packages" in output
        assert "150ms" in output


# =============================================================================
# WEEK 4 DAY 2 - UI FEATURE TESTS (T_UI_* Pattern)
# =============================================================================


class TestUnicodeIconsW4D2:
    """Tests for Unicode icon constants - Week 4 Day 2."""

    @pytest.mark.unit
    def test_safe_icon_is_checkmark(self) -> None:
        """
        TEST_ID: T_UI_037
        SPEC: S011

        Given: ICONS constant
        When: Accessing SAFE icon
        Then: Returns Unicode checkmark
        """
        assert ICONS[Recommendation.SAFE] == "\u2713"

    @pytest.mark.unit
    def test_suspicious_icon_is_warning(self) -> None:
        """
        TEST_ID: T_UI_038
        SPEC: S011

        Given: ICONS constant
        When: Accessing SUSPICIOUS icon
        Then: Returns Unicode warning sign
        """
        assert ICONS[Recommendation.SUSPICIOUS] == "\u26a0"

    @pytest.mark.unit
    def test_high_risk_icon_is_x_mark(self) -> None:
        """
        TEST_ID: T_UI_039
        SPEC: S011

        Given: ICONS constant
        When: Accessing HIGH_RISK icon
        Then: Returns Unicode x mark
        """
        assert ICONS[Recommendation.HIGH_RISK] == "\u2717"

    @pytest.mark.unit
    def test_not_found_icon_is_question_mark(self) -> None:
        """
        TEST_ID: T_UI_040
        SPEC: S011

        Given: ICONS constant
        When: Accessing NOT_FOUND icon
        Then: Returns Unicode question mark
        """
        assert ICONS[Recommendation.NOT_FOUND] == "\u2753"


class TestShowWarningPanelW4D2:
    """Tests for show_warning_panel function - Week 4 Day 2."""

    @pytest.mark.unit
    def test_show_warning_panel_produces_panel_output(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_041
        SPEC: S011

        Given: Package name and signals
        When: show_warning_panel is called
        Then: Output is produced containing Panel content
        """
        show_warning_panel(
            string_console,
            "suspicious-pkg",
            ["Typosquat detected", "New package"],
        )

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert len(output) > 0
        assert "suspicious-pkg" in output
        # Panel border characters should be present
        assert any(c in output for c in ["\u2500", "\u2502", "\u250c", "\u2510"])

    @pytest.mark.unit
    def test_show_warning_panel_displays_all_signals(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_042
        SPEC: S011

        Given: Package with multiple signals
        When: show_warning_panel is called
        Then: All signals are displayed in the panel
        """
        signals = ["Typosquat: similar to 'requests'", "Low download count", "New maintainer"]
        show_warning_panel(string_console, "reqeusts", signals)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        for signal in signals:
            assert signal in output


class TestShowDangerPanelW4D2:
    """Tests for show_danger_panel function - Week 4 Day 2."""

    @pytest.mark.unit
    def test_show_danger_panel_produces_panel_output(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_043
        SPEC: S011

        Given: Package name and signals
        When: show_danger_panel is called
        Then: Output is produced containing Panel content
        """
        show_danger_panel(
            string_console,
            "malicious-pkg",
            ["Known malware", "Contains backdoor"],
        )

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert len(output) > 0
        assert "malicious-pkg" in output
        # Panel border characters should be present
        assert any(c in output for c in ["\u2500", "\u2502", "\u250c", "\u2510"])

    @pytest.mark.unit
    def test_show_danger_panel_displays_all_signals(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_044
        SPEC: S011

        Given: Package with multiple critical signals
        When: show_danger_panel is called
        Then: All signals are displayed in the panel
        """
        signals = [
            "Known malicious package",
            "Contains obfuscated code",
            "Suspicious network access",
        ]
        show_danger_panel(string_console, "evil-pkg", signals)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        for signal in signals:
            assert signal in output


class TestCreateScannerProgressW4D2:
    """Tests for create_scanner_progress function - Week 4 Day 2."""

    @pytest.mark.unit
    def test_create_scanner_progress_returns_progress_object(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_045
        SPEC: S011

        Given: Console
        When: create_scanner_progress is called
        Then: Returns a Progress object
        """
        from rich.progress import Progress

        progress = create_scanner_progress(string_console)
        assert isinstance(progress, Progress)

    @pytest.mark.unit
    def test_create_scanner_progress_has_spinner_column(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_046
        SPEC: S011

        Given: Console
        When: create_scanner_progress is called
        Then: Progress has spinner column
        """
        from rich.progress import SpinnerColumn

        progress = create_scanner_progress(string_console)

        has_spinner = any(isinstance(col, SpinnerColumn) for col in progress.columns)
        assert has_spinner

    @pytest.mark.unit
    def test_create_scanner_progress_has_bar_column(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_047
        SPEC: S011

        Given: Console
        When: create_scanner_progress is called
        Then: Progress has bar column
        """
        from rich.progress import BarColumn

        progress = create_scanner_progress(string_console)

        has_bar = any(isinstance(col, BarColumn) for col in progress.columns)
        assert has_bar


class TestShowResultWithSignalsW4D2:
    """Tests for show_result_with_signals function - Week 4 Day 2."""

    @pytest.mark.unit
    def test_show_result_with_signals_verbose_true_shows_signals(
        self, string_console: Console, suspicious_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T_UI_048
        SPEC: S011

        Given: Package with signals
        When: show_result_with_signals is called with verbose=True
        Then: Signals are displayed
        """
        show_result_with_signals(string_console, suspicious_package_risk, verbose=True)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "typosquat" in output.lower()
        # Signal message should also be shown
        assert "flask" in output.lower()

    @pytest.mark.unit
    def test_show_result_with_signals_risky_shows_without_verbose(
        self, string_console: Console, high_risk_package_risk: PackageRisk
    ) -> None:
        """
        TEST_ID: T_UI_049
        SPEC: S011

        Given: HIGH_RISK package
        When: show_result_with_signals is called with verbose=False
        Then: Signals are still shown for risky packages
        """
        show_result_with_signals(string_console, high_risk_package_risk, verbose=False)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Should show signals for high risk even without verbose
        assert "known_malicious" in output.lower()


class TestShowSummaryW4D2:
    """Tests for show_summary function - Week 4 Day 2."""

    @pytest.mark.unit
    def test_show_summary_shows_correct_safe_count(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_050
        SPEC: S011

        Given: List with multiple safe packages
        When: show_summary is called
        Then: Correct safe count is displayed
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg2", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("pkg3", "pypi", True, 0.1, (), Recommendation.SAFE),
        ]

        show_summary(string_console, results, elapsed_ms=50.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "3 safe" in output

    @pytest.mark.unit
    def test_show_summary_shows_correct_suspicious_count(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_051
        SPEC: S011

        Given: List with suspicious packages
        When: show_summary is called
        Then: Correct suspicious count is displayed
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("pkg2", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
        ]

        show_summary(string_console, results, elapsed_ms=75.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "2 suspicious" in output

    @pytest.mark.unit
    def test_show_summary_shows_correct_high_risk_count(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_052
        SPEC: S011

        Given: List with high risk packages
        When: show_summary is called
        Then: Correct high-risk count is displayed
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]

        show_summary(string_console, results, elapsed_ms=30.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "1 high-risk" in output

    @pytest.mark.unit
    def test_show_summary_shows_elapsed_time(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_053
        SPEC: S011

        Given: Results and elapsed time
        When: show_summary is called
        Then: Elapsed time in ms is displayed
        """
        results = [
            PackageRisk("pkg1", "pypi", True, 0.1, (), Recommendation.SAFE),
        ]

        show_summary(string_console, results, elapsed_ms=150.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "150ms" in output

    @pytest.mark.unit
    def test_show_summary_shows_total_packages(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_054
        SPEC: S011

        Given: Results list
        When: show_summary is called
        Then: Total package count is displayed
        """
        results = [
            PackageRisk("s1", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("s2", "pypi", True, 0.1, (), Recommendation.SAFE),
            PackageRisk("s3", "pypi", True, 0.5, (), Recommendation.SUSPICIOUS),
            PackageRisk("h1", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
            PackageRisk("h2", "pypi", True, 0.9, (), Recommendation.HIGH_RISK),
        ]

        show_summary(string_console, results, elapsed_ms=200.0)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert "5 packages" in output
