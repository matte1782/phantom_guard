# SPEC: S010 - CLI Theme
# Gate 3: Test Design - Week 4 Day 2
"""
Unit tests for the CLI theme module.

SPEC_IDs: S010
TEST_IDs: T_UI_017 - T_UI_030
"""

from __future__ import annotations

import pytest
from rich.theme import Theme

# =============================================================================
# PHANTOM_THEME VALIDATION TESTS
# =============================================================================


class TestPhantomThemeValidity:
    """Tests for PHANTOM_THEME validity and structure."""

    @pytest.mark.unit
    def test_phantom_theme_is_valid_rich_theme(self) -> None:
        """
        TEST_ID: T_UI_017
        SPEC: S010

        Given: PHANTOM_THEME constant
        When: Checking its type
        Then: It is a valid Rich Theme instance
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert isinstance(PHANTOM_THEME, Theme)

    @pytest.mark.unit
    def test_phantom_theme_has_mauve_style(self) -> None:
        """
        TEST_ID: T_UI_018
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for phantom.mauve style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "phantom.mauve" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_phantom_theme_has_lavender_style(self) -> None:
        """
        TEST_ID: T_UI_019
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for phantom.lavender style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "phantom.lavender" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_phantom_theme_has_text_style(self) -> None:
        """
        TEST_ID: T_UI_020
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for phantom.text style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "phantom.text" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_phantom_theme_has_dim_style(self) -> None:
        """
        TEST_ID: T_UI_021
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for phantom.dim style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "phantom.dim" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_phantom_theme_has_overlay_style(self) -> None:
        """
        TEST_ID: T_UI_022
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for phantom.overlay style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "phantom.overlay" in PHANTOM_THEME.styles


# =============================================================================
# STATUS COLOR TESTS
# =============================================================================


class TestStatusColors:
    """Tests for status colors in PHANTOM_THEME."""

    @pytest.mark.unit
    def test_status_safe_is_defined(self) -> None:
        """
        TEST_ID: T_UI_023
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for status.safe style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "status.safe" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_status_suspicious_is_defined(self) -> None:
        """
        TEST_ID: T_UI_024
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for status.suspicious style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "status.suspicious" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_status_high_risk_is_defined(self) -> None:
        """
        TEST_ID: T_UI_025
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for status.high_risk style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "status.high_risk" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_status_not_found_is_defined(self) -> None:
        """
        TEST_ID: T_UI_026
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for status.not_found style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "status.not_found" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_status_info_is_defined(self) -> None:
        """
        TEST_ID: T_UI_027
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for status.info style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "status.info" in PHANTOM_THEME.styles


# =============================================================================
# SEMANTIC COLOR TESTS
# =============================================================================


class TestSemanticColors:
    """Tests for semantic colors in PHANTOM_THEME."""

    @pytest.mark.unit
    def test_success_color_is_defined(self) -> None:
        """
        TEST_ID: T_UI_028
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for success style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "success" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_warning_color_is_defined(self) -> None:
        """
        TEST_ID: T_UI_029
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for warning style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "warning" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_error_color_is_defined(self) -> None:
        """
        TEST_ID: T_UI_030
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for error style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "error" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_info_color_is_defined(self) -> None:
        """
        TEST_ID: T_UI_031
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for info style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "info" in PHANTOM_THEME.styles


# =============================================================================
# UI ELEMENT STYLE TESTS
# =============================================================================


class TestUIElementStyles:
    """Tests for UI element styles in PHANTOM_THEME."""

    @pytest.mark.unit
    def test_border_style_is_defined(self) -> None:
        """
        TEST_ID: T_UI_032
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for border style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "border" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_panel_border_style_is_defined(self) -> None:
        """
        TEST_ID: T_UI_033
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for panel.border style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "panel.border" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_progress_complete_style_is_defined(self) -> None:
        """
        TEST_ID: T_UI_034
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for progress.complete style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "progress.complete" in PHANTOM_THEME.styles

    @pytest.mark.unit
    def test_progress_remaining_style_is_defined(self) -> None:
        """
        TEST_ID: T_UI_035
        SPEC: S010

        Given: PHANTOM_THEME
        When: Checking for progress.remaining style
        Then: Style exists in theme
        """
        from phantom_guard.cli.theme import PHANTOM_THEME

        assert "progress.remaining" in PHANTOM_THEME.styles


# =============================================================================
# THEME EXPORTS TESTS
# =============================================================================


class TestThemeExports:
    """Tests for theme module exports."""

    @pytest.mark.unit
    def test_phantom_theme_in_all(self) -> None:
        """
        TEST_ID: T_UI_036
        SPEC: S010

        Given: phantom_guard.cli.theme module
        When: Checking __all__
        Then: PHANTOM_THEME is exported
        """
        from phantom_guard.cli import theme

        assert "PHANTOM_THEME" in theme.__all__
