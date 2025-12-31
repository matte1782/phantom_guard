# src/phantom_guard/cli/branding.py
"""
Phantom Guard CLI Branding - Tiered Banner System.

IMPLEMENTS: S010, BRANDING_GUIDE.md Section 2
Provides context-aware banner display with Phantom Mocha theme.
"""

from __future__ import annotations

import sys
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Version constant
VERSION = "0.1.2"

# Phantom Mocha color constants
MAUVE = "#CBA6F7"
DIM = "#A6ADC8"
OVERLAY = "#6C7086"


def _can_use_unicode() -> bool:
    """Check if the console can handle Unicode output."""
    encoding = getattr(sys.stdout, "encoding", "") or ""
    return encoding.lower() in ("utf-8", "utf8", "utf-16", "utf-16-le", "utf-16-be")


class BannerType(Enum):
    """
    Banner display levels based on context.

    IMPLEMENTS: S010
    TEST: T010.10

    Attributes:
        LARGE: Full block-letter banner for --version
        COMPACT: Single line with ghost for daily commands (validate/check)
        MEDIUM: Ghost panel for --help screens
        NONE: No banner for --no-banner, CI mode, or JSON output
    """

    LARGE = "large"
    COMPACT = "compact"
    MEDIUM = "medium"
    NONE = "none"


# Large block-letter banner for --version (ASCII-safe version)
LARGE_BANNER_ASCII = r"""
 ____  _   _    _    _   _ _____ ___  __  __
|  _ \| | | |  / \  | \ | |_   _/ _ \|  \/  |
| |_) | |_| | / _ \ |  \| | | || | | | |\/| |
|  __/|  _  |/ ___ \| |\  | | || |_| | |  | |
|_|   |_| |_/_/   \_\_| \_| |_| \___/|_|  |_|

      ____ _   _    _    ____  ____
     / ___| | | |  / \  |  _ \|  _ \
    | |  _| | | | / _ \ | |_) | | | |
    | |_| | |_| |/ ___ \|  _ <| |_| |
     \____|\___//_/   \_\_| \_\____/
"""

# Large block-letter banner for --version (Unicode version)
LARGE_BANNER_UNICODE = r"""
    ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
    ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
    ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
    ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
    ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
                     ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗
                    ██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗
                    ██║  ███╗██║   ██║███████║██████╔╝██║  ██║
                    ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║
                    ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
                     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
"""

# Compact banner for daily use (validate/check commands)
COMPACT_BANNER_ASCII = "PHANTOM GUARD"
COMPACT_BANNER_UNICODE = "\U0001f47b PHANTOM GUARD"  # 👻 PHANTOM GUARD

# Medium ghost panel for --help screens
MEDIUM_GHOST_ASCII = r"""
    .-----.      PHANTOM
   ( o   o )      GUARD
    \  ^  /
     '---'
"""

MEDIUM_GHOST_UNICODE = r"""
     ▄▀▀▀▀▀▄      PHANTOM
    █  ◉ ◉  █      GUARD
    █   ▽   █
     ▀█▀▀▀█▀
"""


def _get_large_banner() -> str:
    """Get large banner based on terminal capabilities."""
    return LARGE_BANNER_UNICODE if _can_use_unicode() else LARGE_BANNER_ASCII


def _get_compact_banner() -> str:
    """Get compact banner based on terminal capabilities."""
    return COMPACT_BANNER_UNICODE if _can_use_unicode() else COMPACT_BANNER_ASCII


def _get_medium_ghost() -> str:
    """Get medium ghost based on terminal capabilities."""
    return MEDIUM_GHOST_UNICODE if _can_use_unicode() else MEDIUM_GHOST_ASCII


def _get_line_char() -> str:
    """Get line character based on terminal capabilities."""
    return "\u2500" if _can_use_unicode() else "-"


def _get_ghost_emoji() -> str:
    """Get ghost emoji or empty string based on terminal capabilities."""
    return "\U0001f47b " if _can_use_unicode() else ""


# Backward compatibility aliases
LARGE_BANNER = LARGE_BANNER_UNICODE
COMPACT_BANNER = COMPACT_BANNER_UNICODE
MEDIUM_GHOST = MEDIUM_GHOST_UNICODE


def get_banner_type(
    command: str,
    no_banner: bool = False,
    quiet: bool = False,
    output_format: str = "text",
) -> BannerType:
    """
    Determine appropriate banner based on context.

    IMPLEMENTS: S010
    TEST: T010.11

    Args:
        command: The CLI command being executed (e.g., "version", "help", "validate")
        no_banner: If True, disable banner display (CI/CD mode)
        quiet: If True, minimal output mode
        output_format: Output format ("text" or "json")

    Returns:
        BannerType indicating which banner style to display

    Examples:
        >>> get_banner_type("version")
        BannerType.LARGE

        >>> get_banner_type("validate")
        BannerType.COMPACT

        >>> get_banner_type("help")
        BannerType.MEDIUM

        >>> get_banner_type("validate", no_banner=True)
        BannerType.NONE

        >>> get_banner_type("validate", output_format="json")
        BannerType.NONE
    """
    # Suppress banner for CI/CD, quiet mode, or JSON output
    if no_banner or quiet or output_format == "json":
        return BannerType.NONE

    # Large banner for version display
    if command == "version":
        return BannerType.LARGE

    # Medium banner for help screens
    if command == "help":
        return BannerType.MEDIUM

    # Compact banner for all other commands (daily use)
    return BannerType.COMPACT


def show_banner(
    console: Console,
    banner_type: BannerType,
    version: str | None = None,
) -> None:
    """
    Display the appropriate banner based on type.

    IMPLEMENTS: S010
    TEST: T010.12

    Args:
        console: Rich Console instance for output
        banner_type: The type of banner to display
        version: Version string to display (defaults to VERSION constant)

    Returns:
        None

    Examples:
        >>> from rich.console import Console
        >>> console = Console()
        >>> show_banner(console, BannerType.COMPACT, "0.1.0")
        # Outputs: 👻 PHANTOM GUARD v0.1.0
        #          ────────────────────────────────────────
    """
    if banner_type == BannerType.NONE:
        return

    version = version or VERSION

    if banner_type == BannerType.LARGE:
        _show_large_banner(console, version)
    elif banner_type == BannerType.COMPACT:
        _show_compact_banner(console, version)
    elif banner_type == BannerType.MEDIUM:
        _show_medium_banner(console, version)


def _show_large_banner(console: Console, version: str) -> None:
    """
    Display the full block-letter ASCII art banner.

    Used for --version command to make a strong first impression.
    """
    console.print(_get_large_banner(), style=f"bold {MAUVE}")
    ghost = _get_ghost_emoji()
    console.print(
        f"                            {ghost} Supply Chain Security",
        style=DIM,
    )
    console.print(
        f"                                    v{version}\n",
        style=OVERLAY,
    )


def _show_compact_banner(console: Console, version: str) -> None:
    """
    Display the compact single-line banner.

    Used for daily commands (validate/check) to minimize visual noise.
    """
    console.print(f"{_get_compact_banner()} v{version}", style=f"bold {MAUVE}")
    console.print(_get_line_char() * 40, style=OVERLAY)


def _show_medium_banner(console: Console, version: str) -> None:
    """
    Display the medium ghost panel banner.

    Used for --help screens to provide friendly branding.
    """
    text = Text()
    for line in _get_medium_ghost().strip().split("\n"):
        text.append(line + "\n", style=f"bold {MAUVE}")
    text.append(f"v{version}", style=OVERLAY)

    console.print(
        Panel(
            text,
            border_style=MAUVE,
            padding=(1, 2),
        )
    )


# Legacy function for backward compatibility
def print_banner(console: Console) -> None:
    """
    Print the Phantom Guard banner with logo.

    IMPLEMENTS: S010
    TEST: T010.10

    Deprecated: Use show_banner() with BannerType instead.

    Args:
        console: Rich Console instance for output
    """
    show_banner(console, BannerType.MEDIUM, VERSION)
