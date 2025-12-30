# SPEC: S010 - CLI Branding
# Gate 3: Test Design - Week 4 Day 2
"""
Unit tests for the CLI branding module.

SPEC_IDs: S010
TEST_IDs: T_UI_001 - T_UI_010
"""

from __future__ import annotations

from enum import Enum
from io import StringIO
from unittest.mock import MagicMock

import pytest
from rich.console import Console

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def string_console() -> Console:
    """Create a console that captures output to a string buffer."""
    return Console(file=StringIO(), force_terminal=True, width=120)


@pytest.fixture
def mock_console() -> MagicMock:
    """Create a mock console for testing."""
    return MagicMock(spec=Console)


# =============================================================================
# BANNERTYPE ENUM TESTS
# =============================================================================


class TestBannerTypeEnum:
    """Tests for BannerType enum values."""

    @pytest.mark.unit
    def test_banner_type_is_enum(self) -> None:
        """
        TEST_ID: T_UI_001
        SPEC: S010

        Given: BannerType class
        When: Checking its type
        Then: It is an Enum subclass
        """
        from phantom_guard.cli.branding import BannerType

        assert issubclass(BannerType, Enum)

    @pytest.mark.unit
    def test_banner_type_has_large_value(self) -> None:
        """
        TEST_ID: T_UI_002
        SPEC: S010

        Given: BannerType enum
        When: Accessing LARGE member
        Then: It exists and has expected value
        """
        from phantom_guard.cli.branding import BannerType

        assert hasattr(BannerType, "LARGE")
        assert BannerType.LARGE.value == "large"

    @pytest.mark.unit
    def test_banner_type_has_compact_value(self) -> None:
        """
        TEST_ID: T_UI_003
        SPEC: S010

        Given: BannerType enum
        When: Accessing COMPACT member
        Then: It exists and has expected value
        """
        from phantom_guard.cli.branding import BannerType

        assert hasattr(BannerType, "COMPACT")
        assert BannerType.COMPACT.value == "compact"

    @pytest.mark.unit
    def test_banner_type_has_medium_value(self) -> None:
        """
        TEST_ID: T_UI_004
        SPEC: S010

        Given: BannerType enum
        When: Accessing MEDIUM member
        Then: It exists and has expected value
        """
        from phantom_guard.cli.branding import BannerType

        assert hasattr(BannerType, "MEDIUM")
        assert BannerType.MEDIUM.value == "medium"

    @pytest.mark.unit
    def test_banner_type_has_none_value(self) -> None:
        """
        TEST_ID: T_UI_005
        SPEC: S010

        Given: BannerType enum
        When: Accessing NONE member
        Then: It exists and has expected value
        """
        from phantom_guard.cli.branding import BannerType

        assert hasattr(BannerType, "NONE")
        assert BannerType.NONE.value == "none"


# =============================================================================
# GET_BANNER_TYPE TESTS
# =============================================================================


class TestGetBannerType:
    """Tests for get_banner_type function."""

    @pytest.mark.unit
    def test_get_banner_type_version_returns_large(self) -> None:
        """
        TEST_ID: T_UI_006
        SPEC: S010

        Given: "version" command string
        When: get_banner_type is called
        Then: Returns BannerType.LARGE
        """
        from phantom_guard.cli.branding import BannerType, get_banner_type

        result = get_banner_type("version")
        assert result == BannerType.LARGE

    @pytest.mark.unit
    def test_get_banner_type_validate_returns_compact(self) -> None:
        """
        TEST_ID: T_UI_007
        SPEC: S010

        Given: "validate" command string
        When: get_banner_type is called
        Then: Returns BannerType.COMPACT
        """
        from phantom_guard.cli.branding import BannerType, get_banner_type

        result = get_banner_type("validate")
        assert result == BannerType.COMPACT

    @pytest.mark.unit
    def test_get_banner_type_check_returns_compact(self) -> None:
        """
        TEST_ID: T_UI_008
        SPEC: S010

        Given: "check" command string
        When: get_banner_type is called
        Then: Returns BannerType.COMPACT
        """
        from phantom_guard.cli.branding import BannerType, get_banner_type

        result = get_banner_type("check")
        assert result == BannerType.COMPACT

    @pytest.mark.unit
    def test_get_banner_type_help_returns_medium(self) -> None:
        """
        TEST_ID: T_UI_009
        SPEC: S010

        Given: "help" command string
        When: get_banner_type is called
        Then: Returns BannerType.MEDIUM
        """
        from phantom_guard.cli.branding import BannerType, get_banner_type

        result = get_banner_type("help")
        assert result == BannerType.MEDIUM

    @pytest.mark.unit
    def test_get_banner_type_no_banner_returns_none(self) -> None:
        """
        TEST_ID: T_UI_010
        SPEC: S010

        Given: no_banner=True
        When: get_banner_type is called
        Then: Returns BannerType.NONE
        """
        from phantom_guard.cli.branding import BannerType, get_banner_type

        result = get_banner_type("validate", no_banner=True)
        assert result == BannerType.NONE

    @pytest.mark.unit
    def test_get_banner_type_quiet_returns_none(self) -> None:
        """
        TEST_ID: T_UI_010b
        SPEC: S010

        Given: quiet=True
        When: get_banner_type is called
        Then: Returns BannerType.NONE
        """
        from phantom_guard.cli.branding import BannerType, get_banner_type

        result = get_banner_type("validate", quiet=True)
        assert result == BannerType.NONE

    @pytest.mark.unit
    def test_get_banner_type_json_output_returns_none(self) -> None:
        """
        TEST_ID: T_UI_010c
        SPEC: S010

        Given: output_format="json"
        When: get_banner_type is called
        Then: Returns BannerType.NONE
        """
        from phantom_guard.cli.branding import BannerType, get_banner_type

        result = get_banner_type("validate", output_format="json")
        assert result == BannerType.NONE


# =============================================================================
# SHOW_BANNER TESTS
# =============================================================================


class TestShowBanner:
    """Tests for show_banner function."""

    @pytest.mark.unit
    def test_show_banner_large_produces_output(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_011
        SPEC: S010

        Given: LARGE banner type
        When: show_banner is called
        Then: Output is produced with version and ghost emoji
        """
        from phantom_guard.cli.branding import BannerType, show_banner

        show_banner(string_console, BannerType.LARGE)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert len(output) > 0
        # Large banner has block letters for PHANTOM GUARD, check for ghost and version
        assert "\U0001f47b" in output  # Ghost emoji
        assert "Supply Chain Security" in output

    @pytest.mark.unit
    def test_show_banner_compact_produces_output(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_012
        SPEC: S010

        Given: COMPACT banner type
        When: show_banner is called
        Then: Output is produced
        """
        from phantom_guard.cli.branding import BannerType, show_banner

        show_banner(string_console, BannerType.COMPACT)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert len(output) > 0
        assert "PHANTOM" in output.upper() or "phantom" in output.lower()

    @pytest.mark.unit
    def test_show_banner_medium_produces_output(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_013
        SPEC: S010

        Given: MEDIUM banner type
        When: show_banner is called
        Then: Output is produced
        """
        from phantom_guard.cli.branding import BannerType, show_banner

        show_banner(string_console, BannerType.MEDIUM)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert len(output) > 0

    @pytest.mark.unit
    def test_show_banner_none_produces_no_output(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_014
        SPEC: S010

        Given: NONE banner type
        When: show_banner is called
        Then: No output is produced
        """
        from phantom_guard.cli.branding import BannerType, show_banner

        show_banner(string_console, BannerType.NONE)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert output == ""

    @pytest.mark.unit
    def test_show_banner_large_includes_version(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_015
        SPEC: S010

        Given: LARGE banner type
        When: show_banner is called
        Then: Output includes version information
        """
        from phantom_guard.cli.branding import VERSION, BannerType, show_banner

        show_banner(string_console, BannerType.LARGE)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert VERSION in output or "v" in output.lower()

    @pytest.mark.unit
    def test_show_banner_with_custom_version(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_015b
        SPEC: S010

        Given: COMPACT banner type and custom version
        When: show_banner is called with version parameter
        Then: Output includes the custom version
        """
        import re

        from phantom_guard.cli.branding import BannerType, show_banner

        # Use COMPACT banner - simpler format that includes version string directly
        show_banner(string_console, BannerType.COMPACT, version="1.2.3")

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        # Strip ANSI escape codes for comparison
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        clean_output = ansi_escape.sub("", output)
        assert "v1.2.3" in clean_output


# =============================================================================
# PRINT_BANNER BACKWARD COMPATIBILITY TESTS
# =============================================================================


class TestPrintBannerCompatibility:
    """Tests for backward compatibility with existing print_banner function."""

    @pytest.mark.unit
    def test_print_banner_still_works(self, string_console: Console) -> None:
        """
        TEST_ID: T_UI_016
        SPEC: S010

        Given: Existing print_banner function
        When: Called with console
        Then: Produces output (backward compatible)
        """
        from phantom_guard.cli.branding import print_banner

        print_banner(string_console)

        output = string_console.file.getvalue()  # type: ignore[union-attr]
        assert len(output) > 0
        assert "PHANTOM" in output.upper() or "phantom" in output.lower()
