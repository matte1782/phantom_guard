# Week 4 - Day 2: UI/UX Implementation + Performance Optimization

> **Date**: Day 2 (Week 4)
> **Focus**: Full BRANDING_GUIDE.md implementation + Performance optimization
> **Tasks**: W4.2a (UI/UX), W4.2b (Performance)
> **Hours**: 10 hours total (6h UI + 4h Perf)
> **Status**: PENDING
> **Dependencies**: W4.1 (Performance Benchmarks) complete
> **Reference**: `docs/design/BRANDING_GUIDE.md`

---

## PART 1: UI/UX Implementation (W4.2a) — 6 hours

> **Reference**: `docs/design/BRANDING_GUIDE.md`
> **Theme**: Phantom Mocha (Catppuccin-inspired)

### Morning Session (3h) - Core Branding & Theme

#### Step 1: Implement Tiered Banner System (1.5h)

```python
# src/phantom_guard/cli/branding.py - REWRITE

"""
Phantom Guard CLI Branding - Tiered Banner System.

IMPLEMENTS: BRANDING_GUIDE.md Section 2
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

if TYPE_CHECKING:
    pass


class BannerType(Enum):
    """Banner display levels based on context."""
    LARGE = "large"      # --version: Full block-letter banner
    COMPACT = "compact"  # validate/check: Single line with ghost
    MEDIUM = "medium"    # --help: Ghost panel
    NONE = "none"        # --no-banner, CI mode, JSON output


# Large block-letter banner for --version
LARGE_BANNER = r'''
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
'''

# Compact banner for daily use
COMPACT_BANNER = "👻 PHANTOM GUARD"

# Medium ghost panel
MEDIUM_GHOST = r'''
     ▄▀▀▀▀▀▄    PHANTOM
    █  ◉ ◉  █    GUARD
    █   ▽   █
     ▀█▀▀▀█▀
'''


def get_banner_type(
    command: str,
    no_banner: bool = False,
    quiet: bool = False,
    output_format: str = "text",
) -> BannerType:
    """Determine appropriate banner based on context."""
    if no_banner or quiet or output_format == "json":
        return BannerType.NONE
    if command == "version":
        return BannerType.LARGE
    if command == "help":
        return BannerType.MEDIUM
    return BannerType.COMPACT


def show_banner(
    console: Console,
    banner_type: BannerType,
    version: str = "0.1.0",
) -> None:
    """Display the appropriate banner."""
    if banner_type == BannerType.NONE:
        return

    if banner_type == BannerType.LARGE:
        console.print(LARGE_BANNER, style="bold #CBA6F7")
        console.print(
            "                            👻  Supply Chain Security",
            style="#A6ADC8",
        )
        console.print(f"                                    v{version}\n", style="#6C7086")

    elif banner_type == BannerType.COMPACT:
        console.print(f"{COMPACT_BANNER} v{version}", style="bold #CBA6F7")
        console.print("─" * 40, style="#6C7086")

    elif banner_type == BannerType.MEDIUM:
        text = Text()
        for line in MEDIUM_GHOST.strip().split("\n"):
            text.append(line + "\n", style="bold #CBA6F7")
        text.append(f"v{version}", style="#6C7086")
        console.print(Panel(text, border_style="#CBA6F7", padding=(1, 2)))
```

#### Step 2: Implement PHANTOM_THEME (1h)

```python
# src/phantom_guard/cli/theme.py - NEW FILE

"""
Phantom Guard Rich Theme - Catppuccin Mocha inspired.

IMPLEMENTS: BRANDING_GUIDE.md Section 5
"""

from rich.theme import Theme

# Phantom Mocha Color Palette
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
```

#### Step 3: Update Output Formatting with Unicode Icons (30min)

```python
# src/phantom_guard/cli/output.py - UPDATE ICONS

# Replace ASCII with Unicode
ICONS = {
    Recommendation.SAFE: "✓",
    Recommendation.SUSPICIOUS: "⚠",
    Recommendation.HIGH_RISK: "✗",
    Recommendation.NOT_FOUND: "❓",
}

STYLES = {
    Recommendation.SAFE: "status.safe",
    Recommendation.SUSPICIOUS: "status.suspicious",
    Recommendation.HIGH_RISK: "status.high_risk",
    Recommendation.NOT_FOUND: "status.not_found",
}
```

---

### Afternoon Session (3h) - Panels, Spinners & Integration

#### Step 4: Implement Alert Panels (1h)

```python
# src/phantom_guard/cli/output.py - ADD PANELS

def show_warning_panel(console: Console, package: str, signals: list[str]) -> None:
    """Display warning panel for suspicious packages."""
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


def show_danger_panel(console: Console, package: str, signals: list[str]) -> None:
    """Display danger panel for high-risk packages."""
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
```

#### Step 5: Implement Ghost Spinner (30min)

```python
# src/phantom_guard/cli/output.py - ADD SPINNER

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

def create_scanner_progress(console: Console) -> Progress:
    """Create themed progress bar with ghost spinner."""
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
```

#### Step 6: Implement Summary with Tree Formatting (1h)

```python
# src/phantom_guard/cli/output.py - ADD SUMMARY

def show_result_with_signals(
    console: Console,
    result: "PackageRisk",
    verbose: bool = False,
) -> None:
    """Display result with optional signal tree."""
    icon = ICONS[result.recommendation]
    style = STYLES[result.recommendation]

    # Main result line
    console.print(
        f"  {icon} {result.name:<20} {result.recommendation.value:<12} "
        f"[phantom.dim]\\[{result.risk_score:.2f}\\][/phantom.dim]",
        style=style,
    )

    # Signal tree (if verbose or high risk)
    if verbose or result.recommendation in (Recommendation.HIGH_RISK, Recommendation.SUSPICIOUS):
        for i, signal in enumerate(result.signals):
            prefix = "└─" if i == len(result.signals) - 1 else "├─"
            console.print(f"     [phantom.dim]{prefix}[/phantom.dim] {signal.message}")


def show_summary(
    console: Console,
    results: list["PackageRisk"],
    elapsed_ms: float,
) -> None:
    """Display scan summary with colored counts."""
    counts = {"SAFE": 0, "SUSPICIOUS": 0, "HIGH_RISK": 0, "NOT_FOUND": 0}
    for r in results:
        counts[r.recommendation.value] = counts.get(r.recommendation.value, 0) + 1

    console.print()
    console.print("─" * 50, style="phantom.overlay")
    summary = Text()
    summary.append(f"👻 Complete in {elapsed_ms:.0f}ms | ", style="phantom.dim")
    summary.append(f"{len(results)} packages", style="phantom.text")
    summary.append(" | ", style="phantom.dim")
    summary.append(f"{counts['SAFE']} safe", style="status.safe")
    summary.append(" | ", style="phantom.dim")
    summary.append(f"{counts['SUSPICIOUS']} suspicious", style="status.suspicious")
    summary.append(" | ", style="phantom.dim")
    summary.append(f"{counts['HIGH_RISK']} high-risk", style="status.high_risk")
    console.print(summary)
```

#### Step 7: Integrate Theme into CLI (30min)

```python
# src/phantom_guard/cli/main.py - UPDATE

from rich.console import Console
from phantom_guard.cli.theme import PHANTOM_THEME
from phantom_guard.cli.branding import get_banner_type, show_banner

# Create themed console
console = Console(theme=PHANTOM_THEME)

# Update validate command to use new output
@app.command()
def validate(...):
    banner_type = get_banner_type("validate", no_banner, quiet, output)
    show_banner(console, banner_type, __version__)
    # ... rest of command
```

---

## PART 2: Performance Optimization (W4.2b) — 4 hours

## Pre-Existing State Analysis

### What Already Exists (Optimized Code)

| Component | Status | Optimization Level |
|:----------|:-------|:-------------------|
| `patterns.py` | ✅ 273 lines | Pre-compiled regex, frozen dataclass |
| `typosquat.py` | ✅ 579 lines | LRU-cached Levenshtein |
| `memory.py` | ⚠️ Basic | Needs __slots__ + OrderedDict |
| `batch.py` | ✅ Implemented | Semaphore-based concurrency |

### Patterns Module (Already Optimized)
```python
# src/phantom_guard/core/patterns.py - ALREADY OPTIMIZED
# - Pre-compiled regex patterns (re.compile at module load)
# - Frozen dataclass with __slots__
# - 10 hallucination patterns defined
```

### Typosquat Module (Already Optimized)
```python
# src/phantom_guard/core/typosquat.py - ALREADY OPTIMIZED
# - LRU cache on levenshtein_distance (maxsize=10000)
# - Early exit for length differences
# - 172 popular packages (needs expansion in W4.3)
```

---

## Revised Task Breakdown

### Morning Session (3h) - Profile & Identify Remaining Hotspots

#### Step 1: Run W4.1 Benchmarks and Profile (1h)

```bash
# Run all benchmarks from Day 1
pytest tests/benchmarks/ -v --benchmark-only --benchmark-autosave

# Generate CPU profile for critical paths
python -m cProfile -o validate_profile.stats -c "
import asyncio
from phantom_guard.core.detector import Detector

async def main():
    detector = Detector()
    for _ in range(100):
        await detector.validate('flask')

asyncio.run(main())
"

# Analyze profile
python -c "
import pstats
p = pstats.Stats('validate_profile.stats')
p.strip_dirs()
p.sort_stats('cumulative')
p.print_stats(20)
"
```

#### Step 2: Optimize Memory Cache (1.5h)

The memory cache can be optimized with `__slots__` and `OrderedDict`:

```python
# src/phantom_guard/cache/memory.py - OPTIMIZE
"""
IMPLEMENTS: S040
OPTIMIZED: Add __slots__ + OrderedDict for O(1) LRU.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from threading import Lock
from time import time
from typing import Any


@dataclass(slots=True)
class CacheEntry:
    """Lightweight cache entry with slots for memory efficiency."""
    value: Any
    expires_at: float
    created_at: float = field(default_factory=time)


class MemoryCache:
    """
    IMPLEMENTS: S040
    OPTIMIZED: O(1) operations with OrderedDict LRU.
    """

    __slots__ = ('_cache', '_lock', '_max_size', '_default_ttl', '_hits', '_misses')

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: float = 300.0,
    ) -> None:
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """O(1) cache lookup with LRU update."""
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if time() > entry.expires_at:
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """O(1) cache set with automatic eviction."""
        ttl = ttl or self._default_ttl
        expires_at = time() + ttl

        with self._lock:
            if key in self._cache:
                self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
                self._cache.move_to_end(key)
                return

            while len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)

            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
```

#### Step 3: Verify Pattern Matching Performance (30min)

```bash
# Verify patterns are sub-millisecond
pytest tests/benchmarks/bench_patterns.py -v --benchmark-only

# Expected: <1ms per pattern check (already optimized)
```

---

### Afternoon Session (3h) - Batch & Cache Optimization

#### Step 4: Tune Batch Concurrency (1h)

Review and tune batch processing parameters:

```python
# src/phantom_guard/core/batch.py - REVIEW AND TUNE

# Current defaults (verify optimal):
# - max_concurrency: 10 (check API rate limits)
# - chunk_size: 20 (balance memory vs throughput)
# - timeout_per_package: 5.0 (adjust based on registry latency)

# Run batch benchmark
pytest tests/benchmarks/bench_detector.py::test_batch_validate_50_packages -v
```

#### Step 5: Optimize Registry Client Connection Pooling (1h)

```python
# src/phantom_guard/registry/base.py - VERIFY CONNECTION POOLING

# Ensure httpx client reuses connections:
# - limits=httpx.Limits(max_connections=20)
# - timeout=httpx.Timeout(10.0, connect=5.0)
```

#### Step 6: Re-run All Benchmarks (45min)

```bash
# Run full benchmark suite
pytest tests/benchmarks/ -v --benchmark-autosave

# Compare against baseline from Day 1
pytest tests/benchmarks/ --benchmark-compare=0001

# Verify all budgets met:
# - Pattern matching: <1ms ✓ (already optimized)
# - Cache hits: <1ms (after optimization)
# - Batch 50: <5s ✓ (verify)
```

#### Step 7: Update Baseline Document (15min)

Update `docs/performance/BASELINE_MEASUREMENTS.md` with:
- Post-optimization measurements
- Improvement percentages
- Any remaining hotspots

---

## End of Day Checklist

### UI/UX Implementation (W4.2a)
- [ ] `BannerType` enum implemented (LARGE/COMPACT/MEDIUM/NONE)
- [ ] Large block-letter banner works for `--version`
- [ ] Compact banner works for `validate`/`check`
- [ ] `PHANTOM_THEME` with Catppuccin Mocha colors
- [ ] Unicode icons (✓ ⚠ ✗ ❓) replacing ASCII
- [ ] Ghost spinner (👻) for scanning
- [ ] Alert panels for warning/danger
- [ ] Summary with tree formatting
- [ ] `--plain` flag disables colors

### Performance Optimizations (W4.2b)
- [ ] Memory cache uses `__slots__` + `OrderedDict`
- [ ] Batch concurrency parameters tuned
- [ ] Connection pooling verified

### Performance Verified
- [ ] Pattern matching <1ms (pre-existing)
- [ ] Memory cache <1ms (after optimization)
- [ ] Batch 50 <5s (verified)
- [ ] No memory leaks

### Code Quality
- [ ] `ruff check src/phantom_guard/` - No lint errors
- [ ] `mypy src/phantom_guard/ --strict` - No type errors
- [ ] All tests passing (including new UI tests)
- [ ] 100% coverage maintained

### Git Commits

#### UI/UX Commit
```bash
git add src/phantom_guard/cli/
git commit -m "feat(cli): Implement full BRANDING_GUIDE.md UI/UX

W4.2a: UI/UX Implementation COMPLETE

- Add tiered banner system (Large/Compact/Medium/None)
- Create PHANTOM_THEME with Catppuccin Mocha colors
- Replace ASCII icons with Unicode (✓ ⚠ ✗ ❓)
- Add ghost spinner (👻) for scanning operations
- Implement warning/danger alert panels
- Add summary with tree formatting
- Add --plain flag for no-color output

Reference: docs/design/BRANDING_GUIDE.md"
```

#### Performance Commit
```bash
git add src/phantom_guard/cache/ docs/performance/
git commit -m "perf: Optimize memory cache with __slots__ + OrderedDict

W4.2b: Performance optimization COMPLETE

- Add __slots__ to CacheEntry for memory efficiency
- Use OrderedDict for O(1) LRU operations
- Verify batch concurrency parameters
- Validate connection pooling
- All performance budgets met"
```

---

## Day 2 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.2a + W4.2b | |
| UI Features Implemented | 9 | |
| Performance Regressions | 0 | |
| Budget Violations | 0 | |
| Memory Cache Improvement | 2-3x | |
| Tests Passing | 100% | |
| Coverage | 100% | |

---

## Key Insights

### UI/UX (W4.2a)
- **Tiered banners** prevent output clutter for daily use
- **Catppuccin Mocha** theme is WCAG AAA accessible
- **Unicode icons** improve visual scanning
- **Ghost spinner** adds personality without being annoying

### Performance (W4.2b)
Most optimization is already done:
- **patterns.py**: Pre-compiled regex ✓
- **typosquat.py**: LRU-cached Levenshtein ✓

Focus on:
1. Memory cache `__slots__` optimization
2. Verifying existing optimizations meet budgets
3. Documenting baseline measurements

---

## Tomorrow Preview

**Day 3 Focus**: Popular Packages Database (W4.3)
- CRITICAL: Expand from 172 → 3000+ packages
- PyPI: 97 → 1000
- npm: 50 → 1000
- crates: 25 → 1000
