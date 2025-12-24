# Phantom Guard — Brand Identity Guide

> **Version**: 2.0.0 (Phantom Mocha Edition)
> **Created**: 2025-12-24
> **Updated**: 2025-12-24
> **Color System**: Catppuccin Mocha-inspired with WCAG AAA accessibility
> **Inspiration**: Claude Code, Phantom Wallet, Catppuccin, Dracula, Rich Library

---

## 1. Brand Essence

### Core Values
| Value | Expression |
|:------|:-----------|
| **Trustworthy** | Security you can rely on |
| **Approachable** | Friendly ghost, not scary |
| **Fast** | Speed is visible, speed is felt |
| **Developer-First** | Built by devs, for devs |

### Brand Personality
- **Friendly guardian** — Protects without being intimidating
- **Quietly confident** — Doesn't need to shout about security
- **Technically excellent** — Precision in every detail
- **Subtly playful** — Ghost mascot adds personality

---

## 2. Logo Concepts

### Primary Logo: ASCII Art (Terminal)

**Style**: Filled block characters (like Claude Code / Gemini CLI)

```
Option A: Minimal Ghost
╔═══════════════════════════════════════╗
║                                       ║
║     ▄▀▀▀▀▀▀▀▄      PHANTOM            ║
║    █  ●   ●  █      GUARD             ║
║    █    ▽    █                        ║
║    ▀▄▄█▄█▄▄▀       v0.1.0             ║
║                                       ║
╚═══════════════════════════════════════╝

Option B: Ghost with Shield
    ▄▄▄▄▄▄▄▄▄▄▄
   ██▀▀▀▀▀▀▀▀▀██
   ██  ◉   ◉  ██     ╔═══════════════════╗
   ██    ▽    ██     ║  PHANTOM GUARD    ║
   ██▄▄▄▄▄▄▄▄▄██     ║  ────────────────  ║
   ▀██▀▀█▀▀█▀▀██▀    ║  Supply Chain     ║
     ▀▀ ▀▀ ▀▀        ║  Security         ║
                     ╚═══════════════════╝

Option C: Compact Inline
┌──────────────────────────────────────────────┐
│  👻 PHANTOM GUARD                    v0.1.0  │
│  ══════════════════════════════════════════  │
│  Detecting AI-hallucinated packages...       │
└──────────────────────────────────────────────┘

Option D: Large Banner (Recommended)
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
                            👻  Supply Chain Security
```

### Ghost Character Variations

```
Neutral:     Happy:       Alert:       Scanning:
  ▄▀▀▀▄       ▄▀▀▀▄       ▄▀▀▀▄       ▄▀▀▀▄
 █ ● ● █     █ ^ ^ █     █ ◉ ◉ █     █ ◐ ◐ █
 █  ▽  █     █  ω  █     █  △  █     █  ○  █
  ▀█▀█▀       ▀█▀█▀       ▀█▀█▀       ▀█▀█▀
```

---

## 3. Color Palette

> **Design Philosophy**: Inspired by [Catppuccin](https://catppuccin.com/palette/) and [Dracula](https://draculatheme.com/spec) themes,
> optimized for [WCAG accessibility](https://webaim.org/articles/contrast/) with colorblind-safe status indicators.

### Theme Selection

Phantom Guard offers **two official themes**. Choose based on preference:

| Theme | Vibe | Best For |
|:------|:-----|:---------|
| **Phantom Mocha** (Default) | Warm, cozy, pastel | Modern terminals, long sessions |
| **Phantom Dracula** | Bold, saturated, classic | High contrast, hacker aesthetic |

---

### THEME 1: Phantom Mocha (Recommended)

*Warm pastels, cozy dark background, easy on the eyes*

#### Core Palette (Phantom Mocha)

| Token | Name | Hex | RGB | Contrast | Usage |
|:------|:-----|:----|:----|:---------|:------|
| `--phantom-mauve` | **Phantom Mauve** | `#CBA6F7` | 203, 166, 247 | 7.2:1 | Primary accent, logo, links |
| `--phantom-lavender` | **Spectral Lavender** | `#B4BEFE` | 180, 190, 254 | 8.1:1 | Secondary accent, highlights |
| `--phantom-base` | **Void Base** | `#1E1E2E` | 30, 30, 46 | — | Primary background |
| `--phantom-mantle` | **Deep Mantle** | `#181825` | 24, 24, 37 | — | Elevated surfaces, panels |
| `--phantom-crust` | **Abyss Crust** | `#11111B` | 17, 17, 27 | — | Deepest background, borders |
| `--phantom-text` | **Ghost Text** | `#CDD6F4` | 205, 214, 244 | 11.5:1 | Primary text |
| `--phantom-subtext` | **Spectral Gray** | `#A6ADC8` | 166, 173, 200 | 6.8:1 | Secondary text, dimmed |
| `--phantom-overlay` | **Mist Overlay** | `#6C7086` | 108, 112, 134 | 4.6:1 | Disabled, borders |

### Status Colors (Accessible + Colorblind-Safe)

> **Important**: Always pair colors with icons to ensure accessibility.
> [Never rely on color alone](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html).

| Status | Name | Hex | Icon | Contrast | WCAG |
|:-------|:-----|:----|:-----|:---------|:-----|
| **SAFE** | Phantom Green | `#A6E3A1` | ✓ | 10.2:1 | AAA |
| **SUSPICIOUS** | Spectral Amber | `#F9E2AF` | ⚠ | 12.1:1 | AAA |
| **HIGH_RISK** | Danger Rose | `#F38BA8` | ✗ | 7.3:1 | AAA |
| **NOT_FOUND** | Mist Blue | `#89B4FA` | ❓ | 6.8:1 | AA |
| **SCANNING** | Phantom Mauve | `#CBA6F7` | 👻 | 7.2:1 | AAA |
| **INFO** | Sky Cyan | `#89DCEB` | ℹ | 9.4:1 | AAA |

### Extended Accent Palette

| Name | Hex | Usage |
|:-----|:----|:------|
| **Peach Glow** | `#FAB387` | Highlights, links hover |
| **Teal Mint** | `#94E2D5` | Success secondary, badges |
| **Sapphire** | `#74C7EC` | Info, external links |
| **Flamingo** | `#F2CDCD` | Soft warnings, notes |
| **Rosewater** | `#F5E0DC` | Subtle accents |

### Semantic Color Mapping

```python
# Rich library color definitions
PHANTOM_COLORS = {
    # Core
    "phantom.purple": "#CBA6F7",
    "phantom.lavender": "#B4BEFE",
    "phantom.text": "#CDD6F4",
    "phantom.dim": "#A6ADC8",

    # Status (with icons for accessibility)
    "safe": "#A6E3A1",      # ✓ Always show with checkmark
    "suspicious": "#F9E2AF", # ⚠ Always show with warning
    "high_risk": "#F38BA8",  # ✗ Always show with X
    "not_found": "#89B4FA",  # ❓ Always show with question

    # Semantic
    "info": "#89DCEB",
    "success": "#A6E3A1",
    "warning": "#F9E2AF",
    "error": "#F38BA8",
}
```

### Gradient System

```css
/* Primary Phantom Gradient - Hero, Headers */
--gradient-phantom: linear-gradient(
  135deg,
  #CBA6F7 0%,      /* Mauve */
  #89B4FA 50%,     /* Blue */
  #B4BEFE 100%     /* Lavender */
);

/* Danger Gradient - Critical alerts */
--gradient-danger: linear-gradient(
  135deg,
  #F38BA8 0%,      /* Rose */
  #EBA0AC 100%     /* Maroon */
);

/* Success Gradient - Safe confirmations */
--gradient-success: linear-gradient(
  135deg,
  #A6E3A1 0%,      /* Green */
  #94E2D5 100%     /* Teal */
);

/* Ambient Glow Effects */
--glow-purple: 0 0 40px rgba(203, 166, 247, 0.25);
--glow-safe: 0 0 20px rgba(166, 227, 161, 0.2);
--glow-danger: 0 0 20px rgba(243, 139, 168, 0.2);
```

### Dark/Light Theme Tokens

```css
/* Dark Theme (Default) - Phantom Mocha */
:root[data-theme="dark"] {
  --bg-primary: #1E1E2E;
  --bg-secondary: #181825;
  --bg-tertiary: #11111B;
  --text-primary: #CDD6F4;
  --text-secondary: #A6ADC8;
  --accent-primary: #CBA6F7;
  --accent-secondary: #B4BEFE;
}

/* Light Theme - Phantom Latte */
:root[data-theme="light"] {
  --bg-primary: #EFF1F5;
  --bg-secondary: #E6E9EF;
  --bg-tertiary: #DCE0E8;
  --text-primary: #4C4F69;
  --text-secondary: #6C6F85;
  --accent-primary: #8839EF;
  --accent-secondary: #7287FD;
}
```

### Colorblind Accessibility Matrix

| Color Pair | Protanopia | Deuteranopia | Tritanopia | Contrast |
|:-----------|:-----------|:-------------|:-----------|:---------|
| Safe + High Risk | ✓ Distinguishable | ✓ Distinguishable | ✓ Distinguishable | 1.4:1 hue |
| Text + Background | ✓ | ✓ | ✓ | 11.5:1 |
| Purple + Background | ✓ | ✓ | ✓ | 7.2:1 |

> **Note**: All status colors are paired with distinct icons (✓ ⚠ ✗ ❓) as per
> [WCAG 1.4.1](https://accessibility.psu.edu/color/colorcoding/) to ensure
> information is never conveyed by color alone.

---

### THEME 2: Phantom Dracula (Alternative)

*Bold saturated colors, classic dark hacker aesthetic*

#### Core Palette (Phantom Dracula)

| Token | Name | Hex | RGB | Contrast | Usage |
|:------|:-----|:----|:----|:---------|:------|
| `--phantom-purple` | **Dracula Purple** | `#BD93F9` | 189, 147, 249 | 6.8:1 | Primary accent, logo |
| `--phantom-pink` | **Neon Pink** | `#FF79C6` | 255, 121, 198 | 6.2:1 | Secondary accent |
| `--phantom-base` | **Void Black** | `#282A36` | 40, 42, 54 | — | Primary background |
| `--phantom-mantle` | **Current Line** | `#44475A` | 68, 71, 90 | — | Elevated surfaces |
| `--phantom-crust` | **Deep Black** | `#21222C` | 33, 34, 44 | — | Deepest background |
| `--phantom-text` | **Foreground** | `#F8F8F2` | 248, 248, 242 | 13.1:1 | Primary text |
| `--phantom-subtext` | **Comment** | `#6272A4` | 98, 114, 164 | 4.2:1 | Secondary text |

#### Status Colors (Dracula)

| Status | Name | Hex | Icon | Contrast | WCAG |
|:-------|:-----|:----|:-----|:---------|:-----|
| **SAFE** | Dracula Green | `#50FA7B` | ✓ | 12.8:1 | AAA |
| **SUSPICIOUS** | Dracula Yellow | `#F1FA8C` | ⚠ | 14.2:1 | AAA |
| **HIGH_RISK** | Dracula Red | `#FF5555` | ✗ | 5.7:1 | AA |
| **NOT_FOUND** | Dracula Cyan | `#8BE9FD` | ❓ | 10.8:1 | AAA |
| **SCANNING** | Dracula Purple | `#BD93F9` | 👻 | 6.8:1 | AA |
| **INFO** | Dracula Cyan | `#8BE9FD` | ℹ | 10.8:1 | AAA |

#### Rich Theme (Dracula)

```python
PHANTOM_DRACULA_THEME = Theme({
    # Core brand colors
    "phantom.purple": "#BD93F9",
    "phantom.pink": "#FF79C6",
    "phantom.text": "#F8F8F2",
    "phantom.dim": "#6272A4",
    "phantom.overlay": "#44475A",

    # Status colors (WCAG AA+ compliant)
    "status.safe": "bold #50FA7B",
    "status.suspicious": "bold #F1FA8C",
    "status.high_risk": "bold #FF5555",
    "status.not_found": "#8BE9FD",
    "status.info": "#8BE9FD",

    # UI elements
    "border": "#6272A4",
    "panel.border": "#BD93F9",
    "progress.complete": "#BD93F9",
    "progress.remaining": "#44475A",
})
```

#### Theme Comparison

```
╔════════════════════════════════════════════════════════════════════════╗
║                     PHANTOM MOCHA vs DRACULA                           ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  MOCHA (Pastel)                    DRACULA (Saturated)                 ║
║  ────────────────                  ──────────────────                  ║
║                                                                        ║
║  ████  #CBA6F7  Mauve              ████  #BD93F9  Purple               ║
║  ████  #A6E3A1  Green              ████  #50FA7B  Green (brighter)     ║
║  ████  #F9E2AF  Amber              ████  #F1FA8C  Yellow               ║
║  ████  #F38BA8  Rose               ████  #FF5555  Red (more vibrant)   ║
║  ████  #1E1E2E  Background         ████  #282A36  Background           ║
║                                                                        ║
║  Best for: Modern, minimal         Best for: Classic, high contrast   ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## 4. Typography

### Terminal / CLI

| Element | Font | Fallback |
|:--------|:-----|:---------|
| Logo ASCII | System monospace | - |
| Commands | JetBrains Mono | Fira Code, Consolas |
| Output | JetBrains Mono | Fira Code, Consolas |

### Documentation / Web

| Element | Font | Weight | Size |
|:--------|:-----|:-------|:-----|
| Headlines | Inter | 700 | 2.5rem |
| Body | Inter | 400 | 1rem |
| Code | JetBrains Mono | 400 | 0.875rem |

---

## 5. CLI Output Design

### Custom Rich Theme (Python)

```python
"""
Phantom Guard CLI Theme - Rich Library Integration
IMPLEMENTS: CLI branding with Catppuccin-inspired Phantom Mocha palette
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich.theme import Theme
from rich.style import Style

# === PHANTOM MOCHA COLOR THEME ===
PHANTOM_THEME = Theme({
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
})

# Create themed console
console = Console(theme=PHANTOM_THEME)


# === BANNER DISPLAY ===
def show_banner(version: str = "0.1.0") -> None:
    """Display the Phantom Guard startup banner."""
    ghost = Text()
    ghost.append("     ▄▀▀▀▀▀▄    ", style="bold #CBA6F7")
    ghost.append("PHANTOM ", style="bold #CDD6F4")
    ghost.append("GUARD\n", style="bold #B4BEFE")
    ghost.append("    █  ◉ ◉  █   ", style="bold #CBA6F7")
    ghost.append("Supply Chain Security\n", style="#A6ADC8")
    ghost.append("    █   ▽   █   ", style="bold #CBA6F7")
    ghost.append(f"v{version}\n", style="#6C7086")
    ghost.append("     ▀█▀▀▀█▀", style="bold #CBA6F7")

    console.print(Panel(
        ghost,
        border_style="#CBA6F7",
        padding=(1, 2),
    ))


# === STATUS DISPLAY ===
STATUS_CONFIG = {
    "SAFE": {"icon": "✓", "style": "status.safe", "label": "SAFE"},
    "SUSPICIOUS": {"icon": "⚠", "style": "status.suspicious", "label": "SUSPICIOUS"},
    "HIGH_RISK": {"icon": "✗", "style": "status.high_risk", "label": "HIGH_RISK"},
    "NOT_FOUND": {"icon": "❓", "style": "status.not_found", "label": "NOT_FOUND"},
}

def show_result(name: str, status: str, score: float) -> None:
    """Display a package validation result with proper coloring."""
    config = STATUS_CONFIG.get(status, STATUS_CONFIG["NOT_FOUND"])

    result = Text()
    result.append(f"  {config['icon']} ", style=config["style"])
    result.append(f"{name:<20}", style=config["style"])
    result.append(f"{config['label']:<12}", style=config["style"])
    result.append(f"[{score:.2f}]", style="phantom.dim")

    console.print(result)


# === PROGRESS DISPLAY ===
def create_scanner_progress() -> Progress:
    """Create a themed progress bar with ghost spinner."""
    return Progress(
        SpinnerColumn(spinner_name="dots", style="#CBA6F7"),
        TextColumn("[#CBA6F7]👻[/#CBA6F7] {task.description}"),
        BarColumn(
            complete_style="#CBA6F7",
            finished_style="#A6E3A1",
            pulse_style="#B4BEFE",
        ),
        console=console,
    )


# === ALERT PANELS ===
def show_warning(package: str, signals: list[str]) -> None:
    """Display a warning panel for suspicious packages."""
    content = Text()
    content.append(f"Package ", style="phantom.text")
    content.append(f"'{package}'", style="bold #F9E2AF")
    content.append(" requires review\n\n", style="phantom.text")

    content.append("Signals detected:\n", style="phantom.dim")
    for signal in signals:
        content.append(f"  • {signal}\n", style="#F9E2AF")

    console.print(Panel(
        content,
        title="[bold #F9E2AF]⚠ WARNING[/]",
        border_style="#F9E2AF",
        padding=(1, 2),
    ))


def show_danger(package: str, signals: list[str]) -> None:
    """Display a danger panel for high-risk packages."""
    content = Text()
    content.append(f"Package ", style="phantom.text")
    content.append(f"'{package}'", style="bold #F38BA8")
    content.append(" is HIGH RISK\n\n", style="phantom.text")

    content.append("Critical signals:\n", style="phantom.dim")
    for signal in signals:
        content.append(f"  • {signal}\n", style="#F38BA8")

    content.append("\n")
    content.append("Recommendation: ", style="phantom.text")
    content.append("DO NOT INSTALL", style="bold #F38BA8")

    console.print(Panel(
        content,
        title="[bold #F38BA8]✗ HIGH RISK[/]",
        border_style="#F38BA8",
        padding=(1, 2),
    ))


# === SUMMARY TABLE ===
def show_summary(safe: int, suspicious: int, high_risk: int, time_ms: float) -> None:
    """Display scan summary with colored counts."""
    total = safe + suspicious + high_risk

    summary = Text()
    summary.append("  ─" * 30 + "\n", style="phantom.overlay")
    summary.append(f"  👻 Complete in {time_ms:.0f}ms | ", style="phantom.dim")
    summary.append(f"{total} packages", style="phantom.text")
    summary.append(" | ", style="phantom.dim")
    summary.append(f"{safe} safe", style="status.safe")
    summary.append(" | ", style="phantom.dim")
    summary.append(f"{suspicious} suspicious", style="status.suspicious")
    summary.append(" | ", style="phantom.dim")
    summary.append(f"{high_risk} high-risk", style="status.high_risk")

    console.print(summary)
```

### Output Examples

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│      ▄▀▀▀▀▀▄    PHANTOM GUARD          ← #CBA6F7 Mauve          │
│     █  ◉ ◉  █   Supply Chain Security  ← #A6ADC8 Subtext        │
│     █   ▽   █   v0.1.0                 ← #6C7086 Overlay        │
│      ▀█▀▀▀█▀                                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

  👻 Scanning requirements.txt...                ← #CBA6F7 Mauve

  ✓ flask              SAFE         [0.05]       ← #A6E3A1 Green
  ✓ requests           SAFE         [0.03]       ← #A6E3A1 Green
  ⚠ flask-utils        SUSPICIOUS   [0.42]       ← #F9E2AF Amber
  ✗ flask-gpt-helper   HIGH_RISK    [0.91]       ← #F38BA8 Rose
  ❓ nonexistent-pkg    NOT_FOUND    [0.00]       ← #89B4FA Blue

  ────────────────────────────────────────────── ← #6C7086 Overlay
  👻 Complete in 234ms | 5 packages | 2 safe | 1 suspicious | 1 high-risk
```

### Color Legend

```
╔══════════════════════════════════════════════════════════════════╗
║  PHANTOM MOCHA COLOR REFERENCE                                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ████████  #CBA6F7  Phantom Mauve     Primary accent, logo       ║
║  ████████  #B4BEFE  Spectral Lavender Secondary accent           ║
║  ████████  #CDD6F4  Ghost Text        Primary text               ║
║  ████████  #A6ADC8  Spectral Gray     Secondary text             ║
║  ████████  #6C7086  Mist Overlay      Borders, disabled          ║
║                                                                  ║
║  ████████  #A6E3A1  Phantom Green     ✓ SAFE status              ║
║  ████████  #F9E2AF  Spectral Amber    ⚠ SUSPICIOUS status        ║
║  ████████  #F38BA8  Danger Rose       ✗ HIGH_RISK status         ║
║  ████████  #89B4FA  Mist Blue         ❓ NOT_FOUND status         ║
║  ████████  #89DCEB  Sky Cyan          ℹ INFO status              ║
║                                                                  ║
║  ████████  #1E1E2E  Void Base         Background                 ║
║  ████████  #181825  Deep Mantle       Panels                     ║
║  ████████  #11111B  Abyss Crust       Deepest layer              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Alert Panels

```
┌──────────────────────────────────────────────────────────────────┐
│  ⚠ WARNING                                     Border: #F9E2AF   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Package 'flask-utils' requires review                           │
│                                                                  │
│  Signals detected:                                               │
│    • Similar to popular package 'flask'                          │
│    • Low download count (< 1000/month)                           │
│    • Created within last 30 days                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  ✗ HIGH RISK                                   Border: #F38BA8   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Package 'flask-gpt-helper' is HIGH RISK                         │
│                                                                  │
│  Critical signals:                                               │
│    • Package does not exist on PyPI                              │
│    • Matches AI hallucination pattern: {base}-{ai}-helper        │
│    • Name suggests LLM-generated package                         │
│                                                                  │
│  Recommendation: DO NOT INSTALL                                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 6. Animation Patterns

### Ghost Spinner Frames

```python
GHOST_SPINNER = [
    "👻  ",
    " 👻 ",
    "  👻",
    " 👻 ",
]

# Or ASCII version
GHOST_ASCII_SPINNER = [
    "▄▀▀▄ ",
    " ▄▀▀▄",
    "▀▄▄▀ ",
    " ▀▄▄▀",
]
```

### Progress Bar Styles

```
Standard:  [████████░░░░░░░░░░░░] 40%
Ghost:     [👻████████░░░░░░░░░░] 40%
Gradient:  [▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒] 40%
```

---

## 7. Iconography

### Status Icons

| Status | Unicode | Fallback |
|:-------|:--------|:---------|
| Safe | ✓ | [PASS] |
| Warning | ⚠ | [WARN] |
| Error | ✗ | [FAIL] |
| Info | ℹ | [INFO] |
| Scanning | 👻 | [...] |

### Signal Type Icons

| Signal | Icon | Color |
|:-------|:-----|:------|
| Typosquat | 🔤 | Yellow |
| Not Found | ❓ | Gray |
| Low Downloads | 📉 | Yellow |
| No Repository | 📦 | Yellow |
| Hallucination | 🤖 | Red |
| Popular | ⭐ | Green |

---

## 8. Voice & Tone

### CLI Messages

| Type | Style | Example |
|:-----|:------|:--------|
| Success | Brief, confident | "✓ All packages safe" |
| Warning | Clear, actionable | "⚠ 2 packages need review" |
| Error | Helpful, not scary | "Package 'xyz' not found. Did you mean 'xzy'?" |
| Progress | Friendly | "👻 Scanning packages..." |

### Documentation

- **Clear over clever** — Explain simply
- **Show, don't tell** — Use examples
- **Respect time** — Get to the point
- **Be human** — Occasional personality is okay

---

## 9. Comparison: Before & After

### Before (Generic CLI)
```
$ check-packages requirements.txt
checking packages...
flask: ok
requests: ok
reqeusts: WARNING - possible typosquat
flask-gpt-helper: WARNING - not found
done. 4 packages checked.
```

### After (Phantom Guard with Phantom Mocha Theme)
```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│      ▄▀▀▀▀▀▄    PHANTOM GUARD                               │
│     █  ◉ ◉  █   Supply Chain Security                       │
│     █   ▽   █   v0.1.0                                       │
│      ▀█▀▀▀█▀                                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘

  👻 Scanning requirements.txt...

  ✓ flask              SAFE         [0.05]
  ✓ requests           SAFE         [0.03]
  ✗ reqeusts           HIGH_RISK    [0.89]
    └─ Typosquat of 'requests' (distance: 1)
  ✗ flask-gpt-helper   HIGH_RISK    [0.91]
    └─ AI hallucination pattern detected

  ──────────────────────────────────────────────────────────────
  👻 Complete in 156ms | 4 packages | 2 safe | 0 suspicious | 2 high-risk
```

### Visual Impact Analysis

| Aspect | Before | After |
|:-------|:-------|:------|
| **Brand Recognition** | None | Instant with ghost logo |
| **Status Clarity** | Text only | Color + Icon + Text |
| **Scan Progress** | Hidden | Visible with spinner |
| **Risk Severity** | Unclear | Color-coded gradient |
| **Accessibility** | Low contrast | WCAG AAA compliant |
| **Developer Appeal** | Generic | Professional, memorable |

---

## 10. Implementation Checklist

### Phase 3 (CLI Week)

- [ ] Implement Rich console wrapper
- [ ] Create ASCII banner with ghost
- [ ] Add ghost spinner animation
- [ ] Implement colored status output
- [ ] Add panel-based warnings
- [ ] Create summary table
- [ ] Add `--no-banner` flag for CI
- [ ] Add `--plain` flag for no colors

### Phase 5 (Showcase Week)

- [ ] Animate ghost in hero section
- [ ] Apply color palette to components
- [ ] Use typography scale
- [ ] Add gradient accents
- [ ] Implement dark theme

---

## Sources & Inspiration

### Color Palettes
- [Catppuccin — Soothing Pastel Theme](https://catppuccin.com/palette/) — Primary color source
- [Dracula Theme Specification](https://draculatheme.com/spec) — Accent inspiration
- [Gogh Terminal Color Schemes](https://gogh-co.github.io/Gogh/) — Terminal theme collection
- [terminal.sexy](https://terminal.sexy/) — Color scheme designer

### Accessibility
- [WebAIM Contrast Checker](https://webaim.org/articles/contrast/) — WCAG guidelines
- [WCAG 1.4.1 Use of Color](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html) — Accessibility standard
- [Penn State Color Coding Guide](https://accessibility.psu.edu/color/colorcoding/) — Colorblind-safe design

### CLI Design
- [Rich Python Library](https://github.com/Textualize/rich) — Terminal formatting
- [Claude Code ASCII Style](https://dev.to/shinshin86/cli-renaissance-alert-meet-oh-my-logo-your-gemini-cli-and-claude-code-style-logo-generator-2gp1) — Logo inspiration
- [oh-my-logo CLI Generator](https://github.com/chrisberno/ascii-logo-generator) — ASCII art tools

### Brand Identity
- [Phantom Wallet Brand Identity](https://phantom.com/learn/blog/introducing-phantom-s-new-brand-identity) — Ghost mascot concept
- [Cybersecurity Logo Design](https://www.ebaqdesign.com/blog/cyber-security-logos) — Security branding

---

## Changelog

| Version | Date | Changes |
|:--------|:-----|:--------|
| 2.1.0 | 2025-12-24 | Added Phantom Dracula theme variant, theme comparison guide |
| 2.0.0 | 2025-12-24 | Complete color system overhaul with Catppuccin-inspired Phantom Mocha palette, WCAG AAA accessibility, colorblind-safe design |
| 1.0.0 | 2025-12-24 | Initial brand identity guide |

---

*The ghost that guards your supply chain.* 👻
