# Week 3 - Day 1: CLI Validate Command + Branding

> **Date**: Day 1 (Week 3)
> **Focus**: CLI `validate` command with ASCII branding and Rich output
> **Tasks**: W3.1
> **Hours**: 6-8 hours
> **SPEC_IDs**: S010-S012
> **TEST_IDs**: T010.01-T010.12
> **EC_IDs**: EC080-EC083

---

## Overview

Build the CLI foundation with the iconic Phantom Guard branding. The `validate` command is the core user interaction point - it must be beautiful, fast, and informative.

### Deliverables
- [ ] CLI entry point with typer
- [ ] ASCII art logo (phantom ghost)
- [ ] `validate` command implementation
- [ ] Rich terminal output with colors
- [ ] Proper exit codes (0-5)

---

## Morning Session (3h)

### Objective
Set up CLI infrastructure with typer and implement the ASCII branding.

### Step 1: Create CLI Module Structure (30min)

```bash
# Create CLI module
mkdir -p src/phantom_guard/cli
touch src/phantom_guard/cli/__init__.py
touch src/phantom_guard/cli/main.py
touch src/phantom_guard/cli/branding.py
touch src/phantom_guard/cli/output.py
```

### Step 2: Implement Branding Module (45min)

```python
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
```

### Step 3: Enable CLI Test Stubs (15min)

```python
# tests/unit/test_cli.py
# Remove @pytest.mark.skip from:
# - test_validate_safe_package_exit_0 (T010.01)
# - test_validate_suspicious_package_exit_1 (T010.02)
# - test_validate_high_risk_package_exit_2 (T010.03)
# - test_validate_not_found_package_exit_3 (T010.04)
```

**Run tests - must FAIL:**
```bash
pytest tests/unit/test_cli.py -v -k "validate"
# Expected: ImportError (module doesn't exist yet)
```

### Step 4: Implement CLI Entry Point (1h)

```python
# src/phantom_guard/cli/main.py
"""
IMPLEMENTS: S010-S012
Phantom Guard CLI entry point.
"""

from __future__ import annotations

import asyncio
from typing import Annotated

import typer
from rich.console import Console

from phantom_guard.cli.branding import print_banner
from phantom_guard.cli.output import OutputFormatter
from phantom_guard.core.detector import Detector
from phantom_guard.core.types import Recommendation

# CLI app
app = typer.Typer(
    name="phantom-guard",
    help="Detect AI-hallucinated malicious packages",
    add_completion=False,
)

console = Console()


# Exit codes (from SPECIFICATION.md Section 6.4)
EXIT_SAFE = 0
EXIT_SUSPICIOUS = 1
EXIT_HIGH_RISK = 2
EXIT_NOT_FOUND = 3
EXIT_INPUT_ERROR = 4
EXIT_RUNTIME_ERROR = 5


@app.command()
def validate(
    package: Annotated[str, typer.Argument(help="Package name to validate")],
    registry: Annotated[str, typer.Option("-r", "--registry", help="Registry: pypi, npm, crates")] = "pypi",
    verbose: Annotated[bool, typer.Option("-v", "--verbose", help="Show detailed signals")] = False,
    quiet: Annotated[bool, typer.Option("-q", "--quiet", help="Only show result")] = False,
    no_banner: Annotated[bool, typer.Option("--no-banner", help="Hide banner")] = False,
) -> None:
    """
    IMPLEMENTS: S010, S011
    TEST: T010.01-T010.06
    EC: EC080-EC083

    Validate a single package for supply chain risks.
    """
    if not quiet and not no_banner:
        print_banner(console)

    # Run async validation
    result = asyncio.run(_validate_package(package, registry, verbose, quiet))

    # Exit with appropriate code
    raise typer.Exit(code=result)


async def _validate_package(
    package: str,
    registry: str,
    verbose: bool,
    quiet: bool,
) -> int:
    """Run the actual validation logic."""
    detector = Detector()
    formatter = OutputFormatter(console, verbose=verbose, quiet=quiet)

    try:
        risk = await detector.validate(package, registry=registry)
        formatter.print_result(risk)

        # Return exit code based on recommendation
        match risk.recommendation:
            case Recommendation.SAFE:
                return EXIT_SAFE
            case Recommendation.SUSPICIOUS:
                return EXIT_SUSPICIOUS
            case Recommendation.HIGH_RISK:
                return EXIT_HIGH_RISK
            case Recommendation.NOT_FOUND:
                return EXIT_NOT_FOUND
    except Exception as e:
        formatter.print_error(str(e))
        return EXIT_RUNTIME_ERROR
```

### Step 5: Run CLI Tests (30min)

```bash
pytest tests/unit/test_cli.py::TestValidateCommand -v --tb=short
# Expected: T010.01-T010.04 pass
```

---

## Afternoon Session (3h)

### Objective
Implement Rich output formatting with colors, icons, and progress indicators.

### Step 6: Implement Output Formatter (1.5h)

```python
# src/phantom_guard/cli/output.py
"""
IMPLEMENTS: S011
CLI output formatting with Rich.
"""

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from phantom_guard.core.types import PackageRisk, Recommendation, Signal

# Color scheme
COLORS = {
    Recommendation.SAFE: "green",
    Recommendation.SUSPICIOUS: "yellow",
    Recommendation.HIGH_RISK: "red",
    Recommendation.NOT_FOUND: "dim",
}

ICONS = {
    Recommendation.SAFE: "✓",
    Recommendation.SUSPICIOUS: "⚠",
    Recommendation.HIGH_RISK: "✗",
    Recommendation.NOT_FOUND: "?",
}


class OutputFormatter:
    """
    IMPLEMENTS: S011
    TEST: T010.05, T010.06

    Format and display validation results.
    """

    def __init__(
        self,
        console: Console,
        verbose: bool = False,
        quiet: bool = False,
    ):
        self.console = console
        self.verbose = verbose
        self.quiet = quiet

    def print_result(self, risk: PackageRisk) -> None:
        """Print single package result."""
        color = COLORS[risk.recommendation]
        icon = ICONS[risk.recommendation]

        # Quiet mode: just the essentials
        if self.quiet:
            self.console.print(f"{risk.name}: {risk.recommendation.value}")
            return

        # Standard output
        text = Text()
        text.append(f"  {icon} ", style=color)
        text.append(f"{risk.name:<20}", style="bold")
        text.append(f"{risk.recommendation.value:<12}", style=color)
        text.append(f"[{risk.risk_score:.2f}]", style="dim")

        self.console.print(text)

        # Verbose: show signals
        if self.verbose and risk.signals:
            for signal in risk.signals:
                self.console.print(f"      └─ {signal.signal_type.value}", style="dim")

    def print_scanning(self, package: str) -> Progress:
        """Show scanning progress."""
        return Progress(
            SpinnerColumn(),
            TextColumn(f"[cyan]Scanning {package}..."),
            console=self.console,
        )

    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[red]Error:[/red] {message}")
```

### Step 7: Add CLI Tests for Output Formatting (45min)

```python
# tests/unit/test_cli.py

def test_verbose_shows_signals():
    """
    TEST_ID: T010.05
    SPEC: S011
    EC: EC091
    """
    result = runner.invoke(app, ["validate", "flask", "-v"])
    # Check that signals are shown
    assert "signals" in result.output.lower() or "└─" in result.output


def test_quiet_minimal_output():
    """
    TEST_ID: T010.06
    SPEC: S011
    EC: EC092
    """
    result = runner.invoke(app, ["validate", "flask", "-q"])
    # Quiet mode has minimal output
    assert len(result.output.strip().split("\n")) <= 2
```

### Step 8: Add Entry Point to pyproject.toml (15min)

```toml
# pyproject.toml
[project.scripts]
phantom-guard = "phantom_guard.cli.main:app"
```

### Step 9: Manual Testing (30min)

```bash
# Install in dev mode
pip install -e .

# Test commands
phantom-guard --help
phantom-guard validate flask
phantom-guard validate flask -v
phantom-guard validate flask -q
phantom-guard validate reqeusts  # Typosquat test
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/cli/` - No lint errors
- [ ] `ruff format src/phantom_guard/cli/` - Code formatted
- [ ] `mypy src/phantom_guard/cli/ --strict` - No type errors
- [ ] All T010.01-T010.06 tests passing

### Documentation
- [ ] All modules have IMPLEMENTS tags
- [ ] CLI commands have comprehensive help text
- [ ] All public functions have type hints

### Git Commit

```bash
git add src/phantom_guard/cli/ tests/unit/test_cli.py pyproject.toml
git commit -m "feat(cli): Implement validate command with Rich branding

IMPLEMENTS: S010-S012
TESTS: T010.01-T010.06
EC: EC080-EC083

- Add CLI entry point with typer
- Add ASCII art phantom ghost branding
- Implement validate command with exit codes
- Add Rich output formatting (colors, icons)
- Support verbose and quiet modes

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Day 1 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W3.1 | |
| Tests Passing | 6 (T010.01-T010.06) | |
| Type Coverage | 100% | |
| Lint Errors | 0 | |
| CLI Works | `phantom-guard validate flask` | |

---

## Tomorrow Preview

**Day 2 Focus**: CLI `check` command (W3.2)
- Parse requirements.txt
- Parse package.json
- Parse Cargo.toml
- Batch file validation
- Progress bar for multiple packages
