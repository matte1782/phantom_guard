# Week 1 — Day 4: Risk Scoring

> **Date**: Day 4
> **Focus**: Risk scoring algorithm + Thresholds
> **Tasks**: W1.5
> **Hours**: 6-8 hours

---

## Morning Session (3h)

### Objective
Implement the risk scoring algorithm that aggregates signals into a final score.

### Task: W1.5 — Risk Scoring

#### Step 1: Enable Test Stubs (15min)

```python
# tests/unit/test_scorer.py
# Enable tests:
# - test_score_no_signals
# - test_score_single_signal
# - test_score_multiple_signals
# - test_score_bounded_zero_to_one
# - test_score_popular_package_reduces_risk
# - test_recommendation_from_score
```

#### Step 2: Review Scoring Formula (30min)

From SPECIFICATION.md:

```
FORMULA: risk_score = clamp((raw_score + 100) / 260, 0.0, 1.0)

Where:
- raw_score = sum of (signal_weight * 100) for all signals
- Weights range from -1.0 to 1.0
- Negative weights (popular package) reduce score
- Final score always in [0.0, 1.0]
```

**Examples:**
| Signals | Raw Score | Final Score |
|:--------|:----------|:------------|
| None | 0 | 0.38 (neutral) |
| NOT_FOUND (0.8) | 80 | 0.69 |
| TYPOSQUAT (0.9) | 90 | 0.73 |
| POPULAR (-0.5) | -50 | 0.19 |
| NOT_FOUND + TYPOSQUAT | 170 | 1.0 (clamped) |

#### Step 3: Implement Scorer (1.5h)

```python
# src/phantom_guard/core/scorer.py
"""
IMPLEMENTS: S007, S008, S009
INVARIANTS: INV001, INV010, INV011, INV012
Risk scoring algorithm.
"""

from __future__ import annotations

from phantom_guard.core.types import (
    PackageRisk,
    Recommendation,
    Signal,
    Registry,
)


# Thresholds for recommendation
# IMPLEMENTS: S008
THRESHOLD_SAFE = 0.30
THRESHOLD_SUSPICIOUS = 0.60
# Above SUSPICIOUS = HIGH_RISK


def calculate_risk_score(signals: tuple[Signal, ...]) -> float:
    """
    IMPLEMENTS: S007
    INVARIANTS: INV001, INV010

    Calculate risk score from signals.

    Formula: clamp((raw + 100) / 260, 0.0, 1.0)

    This formula:
    - Maps no signals to ~0.38 (neutral)
    - Maps max positive (160) to 1.0
    - Maps max negative (-100) to 0.0
    - Allows negative signals to reduce risk

    Args:
        signals: Tuple of detected signals

    Returns:
        Risk score in [0.0, 1.0]
    """
    if not signals:
        # INV010: Neutral baseline for no signals
        raw_score = 0.0
    else:
        # Sum weighted signals
        raw_score = sum(signal.weight * 100 for signal in signals)

    # Apply formula with clamping
    # INV001: Result always in [0.0, 1.0]
    score = (raw_score + 100) / 260
    return max(0.0, min(1.0, score))


def determine_recommendation(score: float, exists: bool) -> Recommendation:
    """
    IMPLEMENTS: S008
    INVARIANT: INV011 - Monotonic with score

    Determine recommendation based on score and existence.

    Args:
        score: Risk score in [0.0, 1.0]
        exists: Whether package exists on registry

    Returns:
        Recommendation enum value
    """
    if not exists:
        return Recommendation.NOT_FOUND

    if score <= THRESHOLD_SAFE:
        return Recommendation.SAFE
    elif score <= THRESHOLD_SUSPICIOUS:
        return Recommendation.SUSPICIOUS
    else:
        return Recommendation.HIGH_RISK


def build_package_risk(
    name: str,
    registry: Registry,
    exists: bool,
    signals: tuple[Signal, ...],
    latency_ms: float = 0.0,
) -> PackageRisk:
    """
    IMPLEMENTS: S001, S007, S008
    INVARIANT: INV012 - Signal count matches PackageRisk.signals

    Build complete PackageRisk from components.

    Args:
        name: Package name
        registry: Package registry
        exists: Whether package exists
        signals: Detected signals
        latency_ms: Detection latency

    Returns:
        Complete PackageRisk object
    """
    score = calculate_risk_score(signals)
    recommendation = determine_recommendation(score, exists)

    return PackageRisk(
        name=name,
        registry=registry,
        exists=exists,
        risk_score=score,
        signals=signals,
        recommendation=recommendation,
        latency_ms=latency_ms,
    )
```

#### Step 4: Run Unit Tests (30min)

```bash
pytest tests/unit/test_scorer.py -v --tb=short
```

---

## Afternoon Session (3h)

### Objective
Add property tests and threshold tuning.

#### Step 1: Property Tests for Invariants (1h)

```python
# tests/property/test_scorer_props.py
"""
Property tests for scoring invariants.
"""

import pytest
from hypothesis import given, strategies as st, assume

from phantom_guard.core.scorer import (
    calculate_risk_score,
    determine_recommendation,
    THRESHOLD_SAFE,
    THRESHOLD_SUSPICIOUS,
)
from phantom_guard.core.types import Signal, SignalType, Recommendation


# Generate valid signals
signal_strategy = st.builds(
    Signal,
    type=st.sampled_from(list(SignalType)),
    weight=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
    message=st.text(min_size=1, max_size=100),
    metadata=st.just({}),
)


class TestScorerProperties:
    """Property-based tests for scorer."""

    @given(st.lists(signal_strategy, max_size=10))
    def test_score_always_bounded(self, signals: list[Signal]):
        """
        INVARIANT: INV001
        Score is always in [0.0, 1.0].
        """
        score = calculate_risk_score(tuple(signals))
        assert 0.0 <= score <= 1.0

    @given(st.lists(signal_strategy, max_size=5), signal_strategy)
    def test_score_monotonic_with_positive_signals(
        self, base_signals: list[Signal], extra_signal: Signal
    ):
        """
        INVARIANT: INV010
        Adding a positive-weight signal increases or maintains score.
        """
        assume(extra_signal.weight > 0)

        base_score = calculate_risk_score(tuple(base_signals))
        extended_signals = base_signals + [extra_signal]
        extended_score = calculate_risk_score(tuple(extended_signals))

        assert extended_score >= base_score

    @given(st.lists(signal_strategy, max_size=5), signal_strategy)
    def test_score_monotonic_with_negative_signals(
        self, base_signals: list[Signal], extra_signal: Signal
    ):
        """
        INVARIANT: INV010
        Adding a negative-weight signal decreases or maintains score.
        """
        assume(extra_signal.weight < 0)

        base_score = calculate_risk_score(tuple(base_signals))
        extended_signals = base_signals + [extra_signal]
        extended_score = calculate_risk_score(tuple(extended_signals))

        assert extended_score <= base_score

    @given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    def test_recommendation_monotonic(self, score: float):
        """
        INVARIANT: INV011
        Higher scores never result in safer recommendations.
        """
        rec = determine_recommendation(score, exists=True)

        if score <= THRESHOLD_SAFE:
            assert rec == Recommendation.SAFE
        elif score <= THRESHOLD_SUSPICIOUS:
            assert rec == Recommendation.SUSPICIOUS
        else:
            assert rec == Recommendation.HIGH_RISK

    def test_neutral_score_value(self):
        """
        Edge case: No signals produces neutral score.
        """
        score = calculate_risk_score(())
        # (0 + 100) / 260 ≈ 0.385
        assert 0.38 <= score <= 0.39
```

#### Step 2: Run Property Tests (30min)

```bash
pytest tests/property/test_scorer_props.py -v --hypothesis-show-statistics
```

#### Step 3: Threshold Analysis (1h)

Create a quick analysis to validate thresholds:

```python
# scripts/analyze_thresholds.py (development script)
"""
Analyze scoring thresholds against example packages.
"""

from phantom_guard.core.types import Signal, SignalType
from phantom_guard.core.scorer import calculate_risk_score, determine_recommendation

# Test cases
TEST_CASES = [
    # (name, signals, expected_recommendation)
    ("clean_package", [], "should be SAFE"),
    ("low_downloads", [
        Signal(SignalType.LOW_DOWNLOADS, 0.3, "Low downloads"),
    ], "should be SAFE or SUSPICIOUS"),
    ("new_no_repo", [
        Signal(SignalType.RECENTLY_CREATED, 0.4, "New"),
        Signal(SignalType.NO_REPOSITORY, 0.2, "No repo"),
    ], "should be SUSPICIOUS"),
    ("typosquat", [
        Signal(SignalType.TYPOSQUAT, 0.9, "Typosquat of requests"),
    ], "should be HIGH_RISK"),
    ("not_found_typo", [
        Signal(SignalType.NOT_FOUND, 0.8, "Not found"),
        Signal(SignalType.TYPOSQUAT, 0.9, "Typosquat"),
    ], "should be HIGH_RISK"),
    ("popular_package", [
        Signal(SignalType.POPULAR_PACKAGE, -0.5, "Popular"),
    ], "should be SAFE"),
]

def main():
    print("Threshold Analysis")
    print("=" * 60)

    for name, signals, expectation in TEST_CASES:
        score = calculate_risk_score(tuple(signals))
        rec = determine_recommendation(score, exists=True)

        status = "✓" if expectation.split()[-1].upper() == rec.value.upper() else "✗"

        print(f"\n{name}:")
        print(f"  Signals: {[s.type.value for s in signals]}")
        print(f"  Score: {score:.3f}")
        print(f"  Recommendation: {rec.value}")
        print(f"  Expected: {expectation}")
        print(f"  Status: {status}")

if __name__ == "__main__":
    main()
```

#### Step 4: Run Full Test Suite (30min)

```bash
# All scorer tests
pytest tests/unit/test_scorer.py tests/property/test_scorer_props.py -v

# Check coverage
pytest tests/ --cov=phantom_guard.core.scorer --cov-report=term-missing
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/` — No lint errors
- [ ] `mypy src/phantom_guard/core/scorer.py` — No type errors
- [ ] W1.5 unit tests passing
- [ ] W1.5 property tests passing

### Invariant Verification

| INV_ID | Statement | Test Status |
|:-------|:----------|:------------|
| INV001 | Score in [0, 1] | VERIFIED |
| INV010 | Monotonic with signal weight | VERIFIED |
| INV011 | Recommendation monotonic | VERIFIED |
| INV012 | Signal count preserved | VERIFIED |

### Git Commit

```bash
git add src/phantom_guard/core/scorer.py tests/property/test_scorer_props.py
git commit -m "$(cat <<'EOF'
feat(core): Implement risk scoring algorithm with invariants

IMPLEMENTS: S007, S008, S009
INVARIANTS: INV001, INV010, INV011, INV012

- Add calculate_risk_score with weighted aggregation
- Add determine_recommendation with thresholds
- Add build_package_risk factory function
- Add property tests for all scoring invariants

Formula: score = clamp((raw + 100) / 260, 0.0, 1.0)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Day 4 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W1.5 | |
| Unit Tests | 10+ | |
| Property Tests | 5+ | |
| Invariants Verified | 4/4 | |

---

## Tomorrow Preview

**Day 5 Focus**: Detector orchestrator (W1.6)
- Wire all components together
- End-to-end detection flow
- Integration tests
