# src/phantom_guard/cli/branding.py
"""
IMPLEMENTS: S010
Phantom Guard CLI branding and ASCII art.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# ASCII art ghost logo
PHANTOM_LOGO = r"""
   ▄▀▀▀▀▀▄
  █  ◉ ◉  █
  █   ▽   █
   ▀█▀▀▀█▀
"""

VERSION = "0.1.0"

def print_banner(console: Console) -> None:
    """
    IMPLEMENTS: S010
    TEST: T010.10

    Print the Phantom Guard banner with logo.
    """
    title = Text()
    title.append("PHANTOM GUARD", style="bold cyan")
    title.append(" — Supply Chain Security", style="dim")

    panel = Panel(
        f"{PHANTOM_LOGO}\n{title}\nv{VERSION}",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
