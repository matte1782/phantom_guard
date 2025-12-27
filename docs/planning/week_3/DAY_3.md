# Week 3 - Day 3: Cache Management + Output Formats

> **Date**: Day 3 (Week 3)
> **Focus**: CLI cache commands and JSON/text output formatting
> **Tasks**: W3.3, W3.5
> **Hours**: 6-8 hours
> **SPEC_IDs**: S016-S019
> **TEST_IDs**: T010.22-T010.24, T010.02-T010.03
> **EC_IDs**: EC089, EC094

---

## Overview

Implement cache management CLI commands and structured output formats. These features improve developer experience and CI/CD integration.

### Deliverables
- [ ] `cache clear` command
- [ ] `cache stats` command
- [ ] `cache path` command
- [ ] JSON output format (`--output json`)
- [ ] Text output formatter (enhanced)
- [ ] Machine-readable output for CI/CD

---

## Morning Session (3h)

### Objective
Implement cache management subcommands.

### Step 1: Create Cache Command Group (30min)

```python
# src/phantom_guard/cli/main.py (add cache subcommand)

# Cache subcommand group
cache_app = typer.Typer(help="Manage the local cache")
app.add_typer(cache_app, name="cache")


@cache_app.command("clear")
def cache_clear(
    registry: Annotated[str | None, typer.Option("-r", "--registry", help="Only clear specific registry")] = None,
    force: Annotated[bool, typer.Option("-f", "--force", help="Skip confirmation")] = False,
) -> None:
    """
    IMPLEMENTS: S016
    TEST: T010.22
    EC: EC094

    Clear the local cache.
    """
    from phantom_guard.cache import Cache, get_default_cache_path

    cache_path = get_default_cache_path()

    if not cache_path.exists():
        console.print("[dim]No cache found[/dim]")
        raise typer.Exit(code=0)

    # Confirmation
    if not force:
        if registry:
            msg = f"Clear cache for {registry}?"
        else:
            msg = "Clear entire cache?"
        if not typer.confirm(msg):
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(code=0)

    # Clear cache
    asyncio.run(_clear_cache(cache_path, registry))
    console.print("[green]Cache cleared successfully[/green]")


async def _clear_cache(cache_path: Path, registry: str | None) -> None:
    """Clear cache entries."""
    from phantom_guard.cache import Cache

    cache = Cache(sqlite_path=cache_path)
    async with cache:
        if registry:
            await cache.clear_registry(registry)
        else:
            await cache.clear_all()


@cache_app.command("stats")
def cache_stats() -> None:
    """
    IMPLEMENTS: S017
    TEST: T010.23

    Show cache statistics.
    """
    from phantom_guard.cache import Cache, get_default_cache_path

    cache_path = get_default_cache_path()

    if not cache_path.exists():
        console.print("[dim]No cache found[/dim]")
        raise typer.Exit(code=0)

    stats = asyncio.run(_get_cache_stats(cache_path))

    # Display stats
    from rich.table import Table

    table = Table(title="Cache Statistics")
    table.add_column("Registry", style="cyan")
    table.add_column("Entries", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("Hit Rate", justify="right")

    for reg, data in stats.items():
        table.add_row(
            reg,
            str(data["entries"]),
            _format_size(data["size_bytes"]),
            f"{data['hit_rate']:.1%}" if data["hit_rate"] else "N/A",
        )

    console.print(table)


async def _get_cache_stats(cache_path: Path) -> dict:
    """Get cache statistics."""
    from phantom_guard.cache import Cache

    cache = Cache(sqlite_path=cache_path)
    async with cache:
        return await cache.get_stats()


@cache_app.command("path")
def cache_path() -> None:
    """
    Show cache file location.
    """
    from phantom_guard.cache import get_default_cache_path

    path = get_default_cache_path()
    console.print(f"Cache path: [cyan]{path}[/cyan]")
    if path.exists():
        size = path.stat().st_size
        console.print(f"Size: [dim]{_format_size(size)}[/dim]")
    else:
        console.print("[dim]Cache does not exist yet[/dim]")


def _format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
```

### Step 2: Add Cache Helper to Cache Module (30min)

```python
# src/phantom_guard/cache/__init__.py (add helper functions)

from pathlib import Path
import platformdirs


def get_default_cache_path() -> Path:
    """
    IMPLEMENTS: S016

    Get the default cache file path.

    Uses platformdirs for cross-platform cache directory:
    - Linux: ~/.cache/phantom-guard/cache.db
    - macOS: ~/Library/Caches/phantom-guard/cache.db
    - Windows: C:/Users/<user>/AppData/Local/phantom-guard/Cache/cache.db
    """
    cache_dir = Path(platformdirs.user_cache_dir("phantom-guard"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "cache.db"


# Add to Cache class:
async def clear_registry(self, registry: str) -> int:
    """Clear all entries for a specific registry."""
    # Implementation
    pass

async def clear_all(self) -> int:
    """Clear all cache entries."""
    # Implementation
    pass

async def get_stats(self) -> dict[str, dict]:
    """Get cache statistics by registry."""
    # Implementation
    pass
```

### Step 3: Enable Cache Command Tests (15min)

```python
# tests/unit/test_cli.py
# Remove @pytest.mark.skip from:
# - test_cache_clear (T010.22)
# - test_cache_stats (T010.23)
# - test_cache_path (T010.24)
```

### Step 4: Run Cache Command Tests (30min)

```bash
pytest tests/unit/test_cli.py -v -k "cache" --tb=short
```

### Step 5: Add platformdirs Dependency (15min)

Add `platformdirs` to project dependencies in `pyproject.toml`:

```toml
# pyproject.toml - add to dependencies section
dependencies = [
    # ... existing deps ...
    "platformdirs>=4.0.0",
]
```

Then install:
```bash
pip install -e .
```

---

## Afternoon Session (3h)

### Objective
Implement JSON and enhanced text output formats.

### Step 6: Create Output Formatters Module (1h)

```python
# src/phantom_guard/cli/formatters.py
"""
IMPLEMENTS: S018-S019
Output formatters for different formats.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from phantom_guard.core.types import PackageRisk, Recommendation


class OutputFormatter(ABC):
    """Base output formatter."""

    @abstractmethod
    def format_results(self, results: list["PackageRisk"]) -> str:
        """Format results for output."""
        pass

    @abstractmethod
    def print_results(self, results: list["PackageRisk"], console: Console) -> None:
        """Print results to console."""
        pass


class TextFormatter(OutputFormatter):
    """
    IMPLEMENTS: S018
    TEST: T010.02

    Human-readable text output.
    """

    COLORS = {
        "SAFE": "green",
        "SUSPICIOUS": "yellow",
        "HIGH_RISK": "red",
        "NOT_FOUND": "dim",
    }

    ICONS = {
        "SAFE": "✓",
        "SUSPICIOUS": "⚠",
        "HIGH_RISK": "✗",
        "NOT_FOUND": "?",
    }

    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.verbose = verbose
        self.quiet = quiet

    def format_results(self, results: list["PackageRisk"]) -> str:
        """Format as text lines."""
        lines = []
        for risk in results:
            rec = risk.recommendation.value
            color = self.COLORS.get(rec, "white")
            icon = self.ICONS.get(rec, " ")
            line = f"  {icon} {risk.name:<20} {rec:<12} [{risk.risk_score:.2f}]"
            lines.append(line)
        return "\n".join(lines)

    def print_results(self, results: list["PackageRisk"], console: Console) -> None:
        """Print formatted results."""
        for risk in results:
            rec = risk.recommendation.value
            color = self.COLORS.get(rec, "white")
            icon = self.ICONS.get(rec, " ")

            text = Text()
            text.append(f"  {icon} ", style=color)
            text.append(f"{risk.name:<20}", style="bold")
            text.append(f"{rec:<12}", style=color)
            text.append(f"[{risk.risk_score:.2f}]", style="dim")

            console.print(text)

            if self.verbose and risk.signals:
                for signal in risk.signals:
                    console.print(f"      └─ {signal.signal_type.value}", style="dim")


class JSONFormatter(OutputFormatter):
    """
    IMPLEMENTS: S019
    TEST: T010.03
    EC: EC089

    Machine-readable JSON output.
    """

    def __init__(self, indent: int = 2):
        self.indent = indent

    def format_results(self, results: list["PackageRisk"]) -> str:
        """Format as JSON string."""
        output = {
            "results": [self._serialize_risk(r) for r in results],
            "summary": self._create_summary(results),
        }
        return json.dumps(output, indent=self.indent)

    def print_results(self, results: list["PackageRisk"], console: Console) -> None:
        """Print JSON output."""
        console.print(self.format_results(results))

    def _serialize_risk(self, risk: "PackageRisk") -> dict:
        """Convert PackageRisk to JSON-serializable dict."""
        return {
            "name": risk.name,
            "recommendation": risk.recommendation.value.lower(),
            "risk_score": round(risk.risk_score, 4),
            "signals": [
                {
                    "type": s.signal_type.value,
                    "weight": s.weight,
                    "metadata": s.metadata,
                }
                for s in risk.signals
            ],
        }

    def _create_summary(self, results: list["PackageRisk"]) -> dict:
        """Create summary statistics."""
        from collections import Counter

        counts = Counter(r.recommendation.value.lower() for r in results)
        return {
            "total": len(results),
            "safe": counts.get("safe", 0),
            "suspicious": counts.get("suspicious", 0),
            "high_risk": counts.get("high_risk", 0),
            "not_found": counts.get("not_found", 0),
        }


def get_formatter(output_format: str, **kwargs) -> OutputFormatter:
    """
    Factory function to get appropriate formatter.

    Args:
        output_format: "text" or "json"
        **kwargs: Formatter-specific options

    Returns:
        Appropriate OutputFormatter instance
    """
    formatters = {
        "text": TextFormatter,
        "json": JSONFormatter,
    }

    formatter_cls = formatters.get(output_format.lower())
    if not formatter_cls:
        raise ValueError(f"Unknown output format: {output_format}")

    return formatter_cls(**kwargs)
```

### Step 7: Integrate Formatters with CLI (30min)

```python
# src/phantom_guard/cli/main.py (update check command)

from phantom_guard.cli.formatters import get_formatter, TextFormatter, JSONFormatter


# Update the check command to use formatters
async def _check_packages(
    packages: list[ParsedPackage],
    parallel: int,
    fail_on: str | None,
    output_format: str,
    quiet: bool,
    verbose: bool = False,
) -> int:
    """Validate all packages from file."""
    # ... existing validation code ...

    # Get appropriate formatter
    formatter = get_formatter(
        output_format,
        verbose=verbose,
        quiet=quiet,
    )

    # Print results
    console.print()
    formatter.print_results(results, console)

    # Summary (only for text format)
    if output_format == "text":
        _print_summary(results, console)

    return _determine_exit_code(results, fail_on)
```

### Step 8: Add Output Format Tests (1h)

```python
# tests/unit/test_formatters.py
"""
SPEC: S018-S019
Tests for output formatters.
"""

import json
import pytest
from phantom_guard.cli.formatters import TextFormatter, JSONFormatter, get_formatter
from phantom_guard.core.types import PackageRisk, Recommendation, Signal, SignalType


class TestTextFormatter:
    def test_format_safe_package(self):
        """
        TEST_ID: T010.02
        SPEC: S018
        """
        risk = PackageRisk(
            name="flask",
            risk_score=0.02,
            recommendation=Recommendation.SAFE,
            signals=(),
        )
        formatter = TextFormatter()
        output = formatter.format_results([risk])

        assert "flask" in output
        assert "SAFE" in output
        assert "0.02" in output

    def test_verbose_shows_signals(self):
        """Verbose mode shows signal details."""
        signal = Signal(signal_type=SignalType.NEW_PACKAGE, weight=0.3)
        risk = PackageRisk(
            name="newpkg",
            risk_score=0.45,
            recommendation=Recommendation.SUSPICIOUS,
            signals=(signal,),
        )
        formatter = TextFormatter(verbose=True)
        # Note: format_results doesn't include signals, print_results does
        # Test through integration


class TestJSONFormatter:
    def test_valid_json_output(self):
        """
        TEST_ID: T010.03
        SPEC: S019
        EC: EC089
        """
        risk = PackageRisk(
            name="flask",
            risk_score=0.02,
            recommendation=Recommendation.SAFE,
            signals=(),
        )
        formatter = JSONFormatter()
        output = formatter.format_results([risk])

        # Should be valid JSON
        data = json.loads(output)
        assert "results" in data
        assert "summary" in data
        assert data["results"][0]["name"] == "flask"

    def test_summary_counts(self):
        """Summary includes correct counts."""
        risks = [
            PackageRisk("pkg1", 0.1, Recommendation.SAFE, ()),
            PackageRisk("pkg2", 0.5, Recommendation.SUSPICIOUS, ()),
            PackageRisk("pkg3", 0.9, Recommendation.HIGH_RISK, ()),
        ]
        formatter = JSONFormatter()
        output = formatter.format_results(risks)

        data = json.loads(output)
        assert data["summary"]["total"] == 3
        assert data["summary"]["safe"] == 1
        assert data["summary"]["suspicious"] == 1
        assert data["summary"]["high_risk"] == 1


class TestGetFormatter:
    def test_get_text_formatter(self):
        """Factory returns TextFormatter for 'text'."""
        formatter = get_formatter("text")
        assert isinstance(formatter, TextFormatter)

    def test_get_json_formatter(self):
        """Factory returns JSONFormatter for 'json'."""
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)

    def test_unknown_format_raises(self):
        """Unknown format raises ValueError."""
        with pytest.raises(ValueError):
            get_formatter("xml")
```

### Step 9: Run All Tests (30min)

```bash
# Run all formatter tests
pytest tests/unit/test_formatters.py -v --tb=short

# Run CLI tests with JSON output
pytest tests/unit/test_cli.py -v -k "json" --tb=short

# Manual testing
phantom-guard validate flask --output json
phantom-guard check requirements.txt --output json
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/cli/` - No lint errors
- [ ] `ruff format src/phantom_guard/cli/` - Code formatted
- [ ] `mypy src/phantom_guard/cli/ --strict` - No type errors
- [ ] All T010.22-T010.24, T010.02-T010.03 tests passing

### Documentation
- [ ] All formatters have IMPLEMENTS tags
- [ ] Cache commands have comprehensive help
- [ ] JSON schema documented

### Git Commit

```bash
git add src/phantom_guard/cli/ tests/unit/
git commit -m "feat(cli): Add cache management and output formatters

IMPLEMENTS: S016-S019
TESTS: T010.02-T010.03, T010.22-T010.24
EC: EC089, EC094

- Add cache clear/stats/path commands
- Add platformdirs for cross-platform cache location
- Add TextFormatter with colors and icons
- Add JSONFormatter with summary stats
- Add formatter factory function"
```

---

## Day 3 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W3.3, W3.5 | |
| Tests Passing | 8+ | |
| Type Coverage | 100% | |
| Lint Errors | 0 | |
| Commands Work | `phantom-guard cache stats` | |
| JSON Output | Valid JSON | |

---

## Tomorrow Preview

**Day 4 Focus**: Batch validation (W3.4)
- Concurrent validation with semaphores
- Rate limiting
- Progress reporting
- Error aggregation
