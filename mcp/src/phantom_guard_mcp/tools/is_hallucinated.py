"""
is_hallucinated MCP tool -- Fast-path hallucination check (Stage 1 only).
IMPLEMENTS: S302
INVARIANTS: INV300, INV301, INV304
TESTS: T302.1, T302.2, T302.3, T302.4, T302.5, T302.6
"""
from __future__ import annotations

from phantom_guard_mcp.tools._validation import NameInput, normalize_visual

HALLUCINATION_THRESHOLD = 0.30

# Module-level hallucination DB for DI (monkeypatched in tests)
# NOTE: Fast-path tools use 0.85/0.95 weights for DB hits (primary evidence).
# Stage 1 engine (Day 5) uses spec's 0.40-0.60 range for combined scoring.
_hallucination_db: object | None = None


async def is_hallucinated(name: str) -> dict:
    """Quick check: does this package name look AI-hallucinated?
    IMPLEMENTS: S302
    INVARIANTS: INV300, INV301, INV304

    Uses ONLY pre-computed checks (no network calls):
    - USENIX hallucination database (205K known names)
    - Hallucination pattern matching (AI/GPT/LLM patterns)
    - Visual similarity check (rn/m, vv/w confusables)
    - Popular package similarity check

    Returns in <5ms. Use check_package for full analysis.

    HALLUCINATION_THRESHOLD = 0.30 (same as core SUSPICIOUS threshold).
    """
    # 1. Validate input (INV304)
    validated = NameInput(name=name)
    normalized = validated.name.lower().replace("_", "-")
    reasons: list[str] = []
    score = 0.0

    # 2a. Popular package check -> not hallucinated (high confidence)
    try:
        from phantom_guard.core.typosquat import is_popular_package
        if is_popular_package(normalized, "pypi"):
            return {
                "name": normalized,
                "hallucinated": False,
                "confidence": 0.95,
                "reasons": [],
            }
    except ImportError:
        pass

    # 2b. Hallucination DB lookup
    if _hallucination_db is not None:
        if hasattr(_hallucination_db, "contains") and _hallucination_db.contains(normalized):
            score = max(score, 0.85)
            reasons.append("Found in hallucination database")
            if hasattr(_hallucination_db, "contains_repeatable") and _hallucination_db.contains_repeatable(normalized):
                score = max(score, 0.95)
                reasons.append("Repeatable hallucination (high confidence)")

    # 2c. Pattern matching
    try:
        from phantom_guard.core.patterns import match_patterns
        pattern_signals = match_patterns(normalized)
        for sig in pattern_signals:
            score = max(score, sig.weight)
            reasons.append(f"Pattern match: {sig.message}")
    except ImportError:
        pass

    # 2d. Visual similarity check
    visual_normalized = normalize_visual(normalized)
    if visual_normalized != normalized:
        try:
            from phantom_guard.core.typosquat import is_popular_package
            if is_popular_package(visual_normalized, "pypi"):
                score = max(score, 0.80)
                reasons.append(
                    f"Visual similarity: '{normalized}' looks like "
                    f"'{visual_normalized}' (confusable characters)"
                )
        except ImportError:
            pass

    # 3. Determine hallucinated status
    hallucinated = score > HALLUCINATION_THRESHOLD
    confidence = score if hallucinated else max(0.0, 1.0 - score)

    return {
        "name": normalized,
        "hallucinated": hallucinated,
        "confidence": confidence,
        "reasons": reasons,
    }
