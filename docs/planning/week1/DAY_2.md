# Week 1 — Day 2: Signal Extraction

> **Date**: Day 2
> **Focus**: Signal extraction + Pattern matching start
> **Tasks**: W1.2, W1.3 (start)
> **Hours**: 6-8 hours

---

## Morning Session (3h)

### Objective
Implement signal extraction logic that analyzes package metadata and generates risk signals.

### Task: W1.2 — Signal Extraction

#### Step 1: Review Test Stubs (15min)

```python
# tests/unit/test_analyzer.py
# Tests to enable:
# - test_extract_signals_from_existing_package
# - test_extract_signals_from_nonexistent_package
# - test_extract_signals_low_downloads
# - test_extract_signals_no_repository
# - test_extract_signals_recently_created
# - test_extract_signals_popular_package
```

#### Step 2: Define Package Metadata Type (30min)

```python
# src/phantom_guard/core/types.py (add to existing)
"""
IMPLEMENTS: S004
Package metadata structure from registry APIs.
"""

from datetime import datetime


@dataclass(frozen=True, slots=True)
class PackageMetadata:
    """
    IMPLEMENTS: S004
    Metadata fetched from package registry.
    """
    name: str
    exists: bool
    created_at: datetime | None = None
    downloads_last_month: int | None = None
    repository_url: str | None = None
    maintainer_count: int | None = None
    latest_version: str | None = None
    description: str | None = None
    registry: Registry = "pypi"

    @property
    def age_days(self) -> int | None:
        """Days since package creation."""
        if self.created_at is None:
            return None
        return (datetime.now(tz=self.created_at.tzinfo) - self.created_at).days
```

#### Step 3: Implement Signal Extractor (1.5h)

```python
# src/phantom_guard/core/signals.py
"""
IMPLEMENTS: S004
INVARIANTS: INV007
Signal extraction from package metadata.
"""

from __future__ import annotations

from phantom_guard.core.types import (
    PackageMetadata,
    Signal,
    SignalType,
)

# Thresholds (configurable)
DOWNLOAD_THRESHOLD_LOW = 1000
DOWNLOAD_THRESHOLD_POPULAR = 1_000_000
AGE_THRESHOLD_NEW_DAYS = 30


def extract_signals(metadata: PackageMetadata) -> tuple[Signal, ...]:
    """
    IMPLEMENTS: S004
    INVARIANT: INV007 - Returns immutable tuple

    Extract risk signals from package metadata.

    Args:
        metadata: Package metadata from registry

    Returns:
        Tuple of detected signals (may be empty)
    """
    signals: list[Signal] = []

    # Check existence
    if not metadata.exists:
        signals.append(Signal(
            type=SignalType.NOT_FOUND,
            weight=0.8,
            message=f"Package '{metadata.name}' not found on {metadata.registry}",
        ))
        return tuple(signals)  # No further checks needed

    # Check downloads
    if metadata.downloads_last_month is not None:
        if metadata.downloads_last_month < DOWNLOAD_THRESHOLD_LOW:
            signals.append(Signal(
                type=SignalType.LOW_DOWNLOADS,
                weight=0.3,
                message=f"Low downloads: {metadata.downloads_last_month:,}/month",
                metadata={"downloads": metadata.downloads_last_month},
            ))
        elif metadata.downloads_last_month > DOWNLOAD_THRESHOLD_POPULAR:
            signals.append(Signal(
                type=SignalType.POPULAR_PACKAGE,
                weight=-0.5,  # Reduces risk
                message=f"Popular package: {metadata.downloads_last_month:,}/month",
                metadata={"downloads": metadata.downloads_last_month},
            ))

    # Check age
    if metadata.age_days is not None:
        if metadata.age_days < AGE_THRESHOLD_NEW_DAYS:
            signals.append(Signal(
                type=SignalType.RECENTLY_CREATED,
                weight=0.4,
                message=f"Recently created: {metadata.age_days} days old",
                metadata={"age_days": metadata.age_days},
            ))

    # Check repository
    if metadata.repository_url is None:
        signals.append(Signal(
            type=SignalType.NO_REPOSITORY,
            weight=0.2,
            message="No repository URL linked",
        ))

    # Check maintainers
    if metadata.maintainer_count is not None and metadata.maintainer_count == 0:
        signals.append(Signal(
            type=SignalType.NO_MAINTAINER,
            weight=0.3,
            message="No maintainers listed",
        ))

    return tuple(signals)


def merge_signals(*signal_groups: tuple[Signal, ...]) -> tuple[Signal, ...]:
    """
    IMPLEMENTS: S004
    Merge multiple signal groups, removing duplicates by type.
    """
    seen_types: set[SignalType] = set()
    merged: list[Signal] = []

    for group in signal_groups:
        for signal in group:
            if signal.type not in seen_types:
                seen_types.add(signal.type)
                merged.append(signal)

    return tuple(merged)
```

#### Step 4: Run Tests (15min)

```bash
# Enable tests in test_analyzer.py
pytest tests/unit/test_analyzer.py -v

# Expected: All signal extraction tests pass
```

---

## Afternoon Session (3h)

### Objective
Start pattern matching implementation for detecting hallucination patterns.

### Task: W1.3 — Pattern Matching (Start)

#### Step 1: Review Test Stubs (15min)

```python
# tests/unit/test_patterns.py
# Enable first batch:
# - test_match_gpt_pattern
# - test_match_ai_pattern
# - test_match_helper_pattern
# - test_no_match_clean_name
```

#### Step 2: Define Pattern Structure (30min)

```python
# src/phantom_guard/core/patterns.py
"""
IMPLEMENTS: S005, S050-S059
INVARIANT: INV008, INV018
Pattern matching for hallucination detection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Pattern


class PatternCategory(Enum):
    """Categories of hallucination patterns."""
    AI_SUFFIX = "ai_suffix"          # *-ai, *-gpt, *-llm
    HELPER_SUFFIX = "helper_suffix"  # *-helper, *-utils, *-tool
    COMBO_PATTERN = "combo_pattern"  # flask-gpt-helper
    TYPO_VARIANT = "typo_variant"    # reqeusts (handled separately)


@dataclass(frozen=True, slots=True)
class HallucinationPattern:
    """
    IMPLEMENTS: S050
    A pattern that indicates potential hallucination.
    """
    id: str
    category: PatternCategory
    regex: Pattern[str]
    weight: float
    description: str

    def matches(self, name: str) -> bool:
        """Check if package name matches this pattern."""
        return bool(self.regex.search(name.lower()))


# Pattern registry
# IMPLEMENTS: S050-S059
HALLUCINATION_PATTERNS: tuple[HallucinationPattern, ...] = (
    # S050: AI-related suffixes
    HallucinationPattern(
        id="AI_GPT_SUFFIX",
        category=PatternCategory.AI_SUFFIX,
        regex=re.compile(r"-(gpt|ai|llm|openai|chatgpt|claude)$"),
        weight=0.6,
        description="Package name ends with AI-related suffix",
    ),
    HallucinationPattern(
        id="AI_GPT_INFIX",
        category=PatternCategory.AI_SUFFIX,
        regex=re.compile(r"-(gpt|ai|llm)-"),
        weight=0.5,
        description="Package name contains AI-related component",
    ),

    # S051: Helper pattern
    HallucinationPattern(
        id="HELPER_SUFFIX",
        category=PatternCategory.HELPER_SUFFIX,
        regex=re.compile(r"-(helper|utils|tools|wrapper|client)$"),
        weight=0.3,
        description="Generic helper suffix (common in hallucinations)",
    ),

    # S052: Combination patterns (most suspicious)
    HallucinationPattern(
        id="POPULAR_AI_COMBO",
        category=PatternCategory.COMBO_PATTERN,
        regex=re.compile(
            r"^(flask|django|fastapi|requests|numpy|pandas)-"
            r"(gpt|ai|llm|openai|claude)-"
            r"(helper|utils|tools|wrapper|client)$"
        ),
        weight=0.8,
        description="Popular package + AI + helper (high hallucination probability)",
    ),

    # S053: Integration patterns
    HallucinationPattern(
        id="INTEGRATION_PATTERN",
        category=PatternCategory.COMBO_PATTERN,
        regex=re.compile(r"^(py|python)?(flask|django|fastapi)-(openai|anthropic|gpt)$"),
        weight=0.5,
        description="Framework + AI provider integration",
    ),
)
```

#### Step 3: Implement Pattern Matcher (1h)

```python
# src/phantom_guard/core/patterns.py (continue)

from phantom_guard.core.types import Signal, SignalType


def match_patterns(name: str) -> tuple[Signal, ...]:
    """
    IMPLEMENTS: S005
    INVARIANT: INV008 - Pure function, no side effects

    Check package name against hallucination patterns.

    Args:
        name: Package name to check

    Returns:
        Tuple of signals for matched patterns
    """
    signals: list[Signal] = []
    normalized = name.lower().strip()

    for pattern in HALLUCINATION_PATTERNS:
        if pattern.matches(normalized):
            signals.append(Signal(
                type=SignalType.HALLUCINATION_PATTERN,
                weight=pattern.weight,
                message=pattern.description,
                metadata={
                    "pattern_id": pattern.id,
                    "category": pattern.category.value,
                },
            ))

    return tuple(signals)


def get_pattern_by_id(pattern_id: str) -> HallucinationPattern | None:
    """Look up a pattern by its ID."""
    for pattern in HALLUCINATION_PATTERNS:
        if pattern.id == pattern_id:
            return pattern
    return None


def list_patterns() -> list[dict[str, str]]:
    """
    List all registered patterns (for debugging/documentation).
    """
    return [
        {
            "id": p.id,
            "category": p.category.value,
            "weight": str(p.weight),
            "description": p.description,
        }
        for p in HALLUCINATION_PATTERNS
    ]
```

#### Step 4: Run Tests (15min)

```bash
pytest tests/unit/test_patterns.py -v

# Expected: Pattern matching tests pass
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/` — No lint errors
- [ ] `mypy src/phantom_guard/core/` — No type errors
- [ ] Tests passing for W1.2

### Property Tests (Bonus)

```bash
# Enable and run property tests
pytest tests/property/test_detector_props.py -v
```

### Git Commit

```bash
git add src/phantom_guard/core/signals.py src/phantom_guard/core/patterns.py
git commit -m "$(cat <<'EOF'
feat(core): Implement signal extraction and pattern matching

IMPLEMENTS: S004, S005, S050-S052
INVARIANTS: INV007, INV008

- Add PackageMetadata dataclass
- Add extract_signals function with threshold logic
- Add HallucinationPattern with regex matching
- Add pattern registry for common hallucination patterns

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Day 2 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W1.2, W1.3 (partial) | |
| Tests Passing | 12+ | |
| Type Coverage | 100% | |
| Patterns Defined | 5+ | |

---

## Tomorrow Preview

**Day 3 Focus**: Typosquat detection (W1.4)
- Levenshtein distance calculation
- Popular package database
- Edit distance threshold tuning
