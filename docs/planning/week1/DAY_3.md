# Week 1 — Day 3: Typosquat Detection

> **Date**: Day 3
> **Focus**: Typosquat detection + Pattern matching completion
> **Tasks**: W1.3 (finish), W1.4
> **Hours**: 6-8 hours

---

## Morning Session (2h)

### Objective
Complete pattern matching implementation with additional patterns.

### Task: W1.3 — Pattern Matching (Complete)

#### Step 1: Add Remaining Patterns (45min)

```python
# src/phantom_guard/core/patterns.py (extend HALLUCINATION_PATTERNS)

# S054: Version confusion patterns
HallucinationPattern(
    id="VERSION_SUFFIX",
    category=PatternCategory.COMBO_PATTERN,
    regex=re.compile(r"^(.+)-(v\d+|2|3|ng|next|new|pro)$"),
    weight=0.2,
    description="Version-like suffix that could be hallucinated",
),

# S055: Namespace confusion
HallucinationPattern(
    id="AWS_PATTERN",
    category=PatternCategory.COMBO_PATTERN,
    regex=re.compile(r"^aws-sdk-(.+)-(helper|utils|wrapper)$"),
    weight=0.7,
    description="AWS SDK helper pattern (common hallucination)",
),

# S056: ML/Data science patterns
HallucinationPattern(
    id="ML_PATTERN",
    category=PatternCategory.AI_SUFFIX,
    regex=re.compile(r"^(tensorflow|pytorch|scikit)-(.+)-(utils|helper|tools)$"),
    weight=0.6,
    description="ML framework helper pattern",
),

# S057: Database patterns
HallucinationPattern(
    id="DB_PATTERN",
    category=PatternCategory.COMBO_PATTERN,
    regex=re.compile(r"^(postgres|mysql|redis|mongo)-(python|py|async)-(client|helper)$"),
    weight=0.5,
    description="Database client helper pattern",
),

# S058: Cloud patterns
HallucinationPattern(
    id="CLOUD_PATTERN",
    category=PatternCategory.COMBO_PATTERN,
    regex=re.compile(r"^(azure|gcp|google)-(.+)-(sdk|client|api)$"),
    weight=0.4,
    description="Cloud provider SDK pattern",
),

# S059: Generic dangerous patterns
HallucinationPattern(
    id="GENERIC_DANGEROUS",
    category=PatternCategory.COMBO_PATTERN,
    regex=re.compile(r"^python-(.+)-(module|package|lib)$"),
    weight=0.3,
    description="Overly generic Python package pattern",
),
```

#### Step 2: Run Full Pattern Tests (30min)

```bash
pytest tests/unit/test_patterns.py -v --tb=short

# Expected: All pattern tests pass
```

#### Step 3: Add Pattern Edge Cases (45min)

```python
# tests/unit/test_patterns.py (add edge cases)

def test_pattern_case_insensitive():
    """Patterns should match regardless of case."""
    signals = match_patterns("Flask-GPT-Helper")
    assert len(signals) > 0

def test_pattern_no_partial_match():
    """Patterns should not match partial words."""
    signals = match_patterns("flaskgpthelper")  # No hyphens
    # Should not match the combo pattern
    assert not any(s.metadata.get("pattern_id") == "POPULAR_AI_COMBO" for s in signals)

def test_pattern_legitimate_packages():
    """Known legitimate packages should not trigger high-weight patterns."""
    legitimate = ["flask", "requests", "numpy", "django", "fastapi"]
    for name in legitimate:
        signals = match_patterns(name)
        total_weight = sum(s.weight for s in signals)
        assert total_weight < 0.3, f"{name} triggered too many patterns"
```

---

## Afternoon Session (4h)

### Objective
Implement typosquat detection using Levenshtein distance.

### Task: W1.4 — Typosquat Detection

#### Step 1: Enable Test Stubs (15min)

```python
# tests/unit/test_typosquat.py
# Enable tests:
# - test_detect_typosquat_simple
# - test_detect_typosquat_transposition
# - test_detect_typosquat_missing_char
# - test_no_typosquat_exact_match
# - test_no_typosquat_unrelated
```

#### Step 2: Implement Levenshtein Distance (45min)

```python
# src/phantom_guard/core/typosquat.py
"""
IMPLEMENTS: S006
INVARIANT: INV009
Typosquat detection using edit distance.
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=10000)
def levenshtein_distance(s1: str, s2: str) -> int:
    """
    IMPLEMENTS: S006
    INVARIANT: INV009 - Result is always non-negative integer

    Calculate Levenshtein (edit) distance between two strings.

    Uses dynamic programming with O(min(m,n)) space.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Minimum number of single-character edits to transform s1 to s2
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost is 0 if characters match, 1 otherwise
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def normalized_distance(s1: str, s2: str) -> float:
    """
    Calculate normalized edit distance (0.0 to 1.0).

    Returns:
        0.0 for identical strings, 1.0 for completely different
    """
    if not s1 and not s2:
        return 0.0
    max_len = max(len(s1), len(s2))
    return levenshtein_distance(s1, s2) / max_len
```

#### Step 3: Create Popular Package Database (30min)

```python
# src/phantom_guard/core/typosquat.py (continue)

# Top 100 most popular packages per registry
# These are the most likely typosquat targets
POPULAR_PACKAGES: dict[str, set[str]] = {
    "pypi": {
        "requests", "numpy", "pandas", "flask", "django",
        "scipy", "matplotlib", "pillow", "sqlalchemy", "pytest",
        "boto3", "pyyaml", "cryptography", "urllib3", "certifi",
        "setuptools", "wheel", "pip", "packaging", "six",
        "jinja2", "markupsafe", "click", "werkzeug", "itsdangerous",
        "fastapi", "uvicorn", "starlette", "pydantic", "httpx",
        "aiohttp", "attrs", "decorator", "wrapt", "typing-extensions",
        "idna", "chardet", "charset-normalizer", "beautifulsoup4", "lxml",
        "redis", "celery", "kombu", "billiard", "amqp",
        "tensorflow", "keras", "torch", "transformers", "scikit-learn",
        # Add more as needed
    },
    "npm": {
        "react", "lodash", "axios", "express", "moment",
        "typescript", "webpack", "babel", "eslint", "prettier",
        "next", "vue", "angular", "jquery", "underscore",
        # Add more as needed
    },
    "crates": {
        "serde", "tokio", "reqwest", "clap", "rand",
        "log", "regex", "chrono", "anyhow", "thiserror",
        # Add more as needed
    },
}


def get_popular_packages(registry: str) -> set[str]:
    """Get set of popular packages for a registry."""
    return POPULAR_PACKAGES.get(registry, set())
```

#### Step 4: Implement Typosquat Detector (1h)

```python
# src/phantom_guard/core/typosquat.py (continue)

from phantom_guard.core.types import Signal, SignalType, Registry

# Thresholds
MAX_EDIT_DISTANCE = 2  # Maximum edits to consider typosquat
MIN_NAME_LENGTH = 4    # Minimum length for typosquat detection


@dataclass(frozen=True, slots=True)
class TyposquatMatch:
    """A potential typosquat match."""
    target: str
    distance: int
    normalized: float


def find_typosquat_targets(
    name: str,
    registry: Registry,
    max_distance: int = MAX_EDIT_DISTANCE,
) -> list[TyposquatMatch]:
    """
    IMPLEMENTS: S006
    Find potential typosquat targets for a package name.

    Args:
        name: Package name to check
        registry: Which registry to check against
        max_distance: Maximum edit distance to consider

    Returns:
        List of potential targets, sorted by distance
    """
    if len(name) < MIN_NAME_LENGTH:
        return []

    name_lower = name.lower()
    popular = get_popular_packages(registry)
    matches: list[TyposquatMatch] = []

    for target in popular:
        if target == name_lower:
            continue  # Exact match, not a typosquat

        # Quick length filter (distance can't be less than length diff)
        if abs(len(target) - len(name_lower)) > max_distance:
            continue

        distance = levenshtein_distance(name_lower, target)
        if distance <= max_distance:
            matches.append(TyposquatMatch(
                target=target,
                distance=distance,
                normalized=distance / max(len(name_lower), len(target)),
            ))

    return sorted(matches, key=lambda m: m.distance)


def detect_typosquat(name: str, registry: Registry) -> tuple[Signal, ...]:
    """
    IMPLEMENTS: S006
    INVARIANT: INV009 - Uses validated edit distance

    Check if package name is a potential typosquat.

    Args:
        name: Package name to check
        registry: Registry to check against

    Returns:
        Tuple of typosquat signals (empty if no match)
    """
    matches = find_typosquat_targets(name, registry)

    if not matches:
        return ()

    signals: list[Signal] = []

    for match in matches[:3]:  # Top 3 matches
        # Weight based on distance (closer = higher risk)
        weight = 0.9 - (match.distance * 0.3)  # 0.9, 0.6, 0.3

        signals.append(Signal(
            type=SignalType.TYPOSQUAT,
            weight=max(0.1, weight),  # Floor at 0.1
            message=f"Possible typosquat of '{match.target}' (distance: {match.distance})",
            metadata={
                "target": match.target,
                "distance": match.distance,
                "normalized_distance": round(match.normalized, 3),
            },
        ))

    return tuple(signals)
```

#### Step 5: Run Tests (30min)

```bash
# Unit tests
pytest tests/unit/test_typosquat.py -v

# Property tests for INV009
pytest tests/property/test_typosquat_props.py -v
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/` — No lint errors
- [ ] `mypy src/phantom_guard/core/` — No type errors
- [ ] W1.3 tests passing
- [ ] W1.4 tests passing

### Performance Check

```python
# Quick benchmark in Python REPL
from phantom_guard.core.typosquat import detect_typosquat
import time

start = time.perf_counter()
for _ in range(1000):
    detect_typosquat("reqeusts", "pypi")
elapsed = (time.perf_counter() - start) * 1000 / 1000

print(f"Average: {elapsed:.3f}ms")
# Should be < 1ms per call
```

### Git Commit

```bash
git add src/phantom_guard/core/typosquat.py src/phantom_guard/core/patterns.py
git commit -m "$(cat <<'EOF'
feat(core): Implement typosquat detection with Levenshtein distance

IMPLEMENTS: S006, S053-S059
INVARIANTS: INV009

- Add Levenshtein distance with LRU caching
- Add popular package database (PyPI, npm, crates)
- Add typosquat detection with configurable threshold
- Complete hallucination pattern registry

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Day 3 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W1.3, W1.4 | |
| Tests Passing | 20+ | |
| Typosquat Detection | <1ms | |
| Popular Packages | 50+ | |

---

## Tomorrow Preview

**Day 4 Focus**: Risk scoring algorithm (W1.5)
- Weighted signal aggregation
- Threshold tuning
- Property tests for INV001, INV010, INV011
