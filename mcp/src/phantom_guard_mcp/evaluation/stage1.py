"""
Stage 1 evaluation engine -- Pre-computed checks, no network calls.
IMPLEMENTS: S305
INVARIANTS: INV300, INV301, INV304
TESTS: T305.1, T305.2, T305.3, T305.4, T305.5, T305.6
"""
from __future__ import annotations

from dataclasses import dataclass

from phantom_guard.core.types import Signal, SignalType

from phantom_guard_mcp.tools._validation import NameEcosystemInput, normalize_visual


# Module-level hallucination DB for dependency injection.
# In production: set at startup. In tests: monkeypatched via conftest autouse fixture.
_hallucination_db: object | None = None


@dataclass
class Stage1Result:
    """Result of Stage 1 evaluation. IMPLEMENTS: S305 Section 2.6"""

    score: float  # Combined Stage 1 score [0.0, 1.0]
    signals: tuple[Signal, ...]  # Stage 1 signals (deterministic order)
    early_exit: bool  # True if score triggers early exit
    recommendation: str | None  # Set if early_exit is True ("SAFE" or "HIGH_RISK")


async def run_stage1(name: str, ecosystem: str = "pypi") -> Stage1Result:
    """Run Stage 1 pre-computed checks in deterministic order.

    IMPLEMENTS: S305
    INVARIANTS: INV301 (deterministic order), INV300 (score range)

    Checks (in order):
      1. Popular package → immediate SAFE
      2. Hallucination DB lookup
      3. Pattern matching
      4. Visual similarity
      5. Typosquat detection

    No network I/O. All checks are O(1) or O(n) on name length.
    """
    # Validate input (INV304)
    validated = NameEcosystemInput(name=name, ecosystem=ecosystem)
    normalized = validated.name.lower().replace("_", "-")
    signals: list[Signal] = []

    # --- Check 1: Popular package (fast path) ---
    try:
        from phantom_guard.core.typosquat import is_popular_package

        if is_popular_package(normalized, ecosystem):
            return Stage1Result(
                score=0.0,
                signals=(),
                early_exit=True,
                recommendation="SAFE",
            )
    except ImportError:
        pass

    # --- Check 2: Hallucination DB lookup ---
    # NOTE: Stage 1 uses spec S307 weights (0.40/0.60) for combined multi-signal scoring.
    # Fast-path tools (is_hallucinated, check_package) use 0.85/0.95 where DB is primary evidence.
    if _hallucination_db is not None:
        if hasattr(_hallucination_db, "contains") and _hallucination_db.contains(normalized):
            if hasattr(_hallucination_db, "contains_repeatable") and _hallucination_db.contains_repeatable(normalized):
                weight = 0.60
                message = f"'{normalized}' found in repeatable hallucination set (high confidence)"
            else:
                weight = 0.40
                message = f"'{normalized}' found in hallucination database"
            signals.append(Signal(
                type=SignalType.HALLUCINATION_PATTERN,
                weight=weight,
                message=message,
                metadata={},
            ))

    # --- Check 3: Pattern matching ---
    try:
        from phantom_guard.core.patterns import match_patterns

        pattern_signals = match_patterns(normalized)
        signals.extend(pattern_signals)
    except ImportError:
        pass

    # --- Check 4: Visual similarity ---
    visual_normalized = normalize_visual(normalized)
    if visual_normalized != normalized:
        try:
            from phantom_guard.core.typosquat import is_popular_package as _is_popular

            if _is_popular(visual_normalized, ecosystem):
                signals.append(Signal(
                    type=SignalType.TYPOSQUAT,
                    weight=0.80,
                    message=f"'{normalized}' visually similar to popular package '{visual_normalized}'",
                    metadata={"visual_target": visual_normalized},
                ))
        except ImportError:
            pass

    # --- Check 5: Typosquat detection ---
    try:
        from phantom_guard.core.typosquat import detect_typosquat

        typosquat_signals = detect_typosquat(normalized, ecosystem)
        signals.extend(typosquat_signals)
    except ImportError:
        pass

    # --- Scoring ---
    score = max(sig.weight for sig in signals) if signals else 0.0

    # --- Early exit decision ---
    if score < 0.10:
        early_exit = True
        recommendation = "SAFE"
    elif score > 0.60:
        early_exit = True
        recommendation = "HIGH_RISK"
    else:
        early_exit = False
        recommendation = None

    return Stage1Result(
        score=score,
        signals=tuple(signals),
        early_exit=early_exit,
        recommendation=recommendation,
    )
