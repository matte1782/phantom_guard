"""
Phantom Guard Rich Theme - Catppuccin Mocha inspired.

IMPLEMENTS: BRANDING_GUIDE.md Section 5
"""

from rich.theme import Theme

__all__ = ["PHANTOM_THEME"]

# Phantom Mocha Color Palette
PHANTOM_THEME = Theme(
    {
        # Core brand colors
        "phantom.mauve": "#CBA6F7",
        "phantom.lavender": "#B4BEFE",
        "phantom.text": "#CDD6F4",
        "phantom.dim": "#A6ADC8",
        "phantom.overlay": "#6C7086",
        # Status colors (WCAG AAA compliant)
        "status.safe": "bold #A6E3A1",
        "status.suspicious": "bold #F9E2AF",
        "status.high_risk": "bold #F38BA8",
        "status.not_found": "#89B4FA",
        "status.info": "#89DCEB",
        # Semantic colors
        "success": "#A6E3A1",
        "warning": "#F9E2AF",
        "error": "#F38BA8",
        "info": "#89DCEB",
        # UI elements
        "border": "#6C7086",
        "panel.border": "#CBA6F7",
        "progress.complete": "#CBA6F7",
        "progress.remaining": "#45475A",
        # Extended accents
        "peach": "#FAB387",
        "teal": "#94E2D5",
        "sapphire": "#74C7EC",
        "flamingo": "#F2CDCD",
    }
)
