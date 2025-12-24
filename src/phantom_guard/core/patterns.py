"""
IMPLEMENTS: S005, S050-S059
INVARIANTS: INV008, INV018
Pattern matching for hallucination detection.

This module provides pattern-based detection of package names that
exhibit characteristics commonly seen in AI-hallucinated packages.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from re import Pattern

from phantom_guard.core.types import Signal, SignalType

# =============================================================================
# ENUMS
# =============================================================================


class PatternCategory(Enum):
    """Categories of hallucination patterns."""

    AI_SUFFIX = "ai_suffix"  # *-ai, *-gpt, *-llm
    HELPER_SUFFIX = "helper_suffix"  # *-helper, *-utils, *-tool
    GENERIC_PREFIX = "generic_prefix"  # easy-*, simple-*, auto-*
    COMBO_PATTERN = "combo_pattern"  # flask-gpt-helper (multiple indicators)
    INTEGRATION_PATTERN = "integration_pattern"  # flask-openai, django-claude


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass(frozen=True, slots=True)
class HallucinationPattern:
    """
    IMPLEMENTS: S050
    INVARIANT: INV018 - Pattern is immutable

    A pattern that indicates potential hallucination.
    """

    id: str
    category: PatternCategory
    regex: Pattern[str]
    weight: float
    description: str

    def matches(self, name: str) -> bool:
        """
        Check if package name matches this pattern.

        Args:
            name: Package name to check

        Returns:
            True if the pattern matches
        """
        return bool(self.regex.search(name.lower()))


# =============================================================================
# PATTERN REGISTRY
# =============================================================================

# IMPLEMENTS: S050-S059
# These patterns are based on observed hallucination characteristics
HALLUCINATION_PATTERNS: tuple[HallucinationPattern, ...] = (
    # S050: AI-related suffixes (highest risk when combined)
    HallucinationPattern(
        id="AI_GPT_SUFFIX",
        category=PatternCategory.AI_SUFFIX,
        regex=re.compile(r"-(gpt|ai|llm|openai|chatgpt|claude|anthropic|gemini)$"),
        weight=0.6,
        description="Package name ends with AI-related suffix",
    ),
    HallucinationPattern(
        id="AI_GPT_INFIX",
        category=PatternCategory.AI_SUFFIX,
        regex=re.compile(r"-(gpt|ai|llm)-(helper|utils|tools|client|wrapper)"),
        weight=0.7,
        description="Package name contains AI component followed by helper suffix",
    ),
    # S051: Helper/utility patterns
    HallucinationPattern(
        id="HELPER_SUFFIX",
        category=PatternCategory.HELPER_SUFFIX,
        regex=re.compile(r"-(helper|utils|tools|wrapper|client|sdk)$"),
        weight=0.25,
        description="Generic helper suffix (common in hallucinations)",
    ),
    # S052: Combination patterns (most suspicious)
    HallucinationPattern(
        id="POPULAR_AI_COMBO",
        category=PatternCategory.COMBO_PATTERN,
        regex=re.compile(
            r"^(flask|django|fastapi|requests|numpy|pandas|torch|tensorflow)"
            r"-(gpt|ai|llm|openai|claude)"
            r"-(helper|utils|tools|wrapper|client)$"
        ),
        weight=0.85,
        description="Popular package + AI + helper (high hallucination probability)",
    ),
    HallucinationPattern(
        id="POPULAR_AI_DIRECT",
        category=PatternCategory.COMBO_PATTERN,
        regex=re.compile(
            r"^(flask|django|fastapi|requests|numpy|pandas|torch|tensorflow)"
            r"-(gpt|ai|llm|openai|claude|anthropic|chatgpt)$"
        ),
        weight=0.65,
        description="Popular package + AI provider",
    ),
    # S053: Integration patterns
    HallucinationPattern(
        id="INTEGRATION_PATTERN",
        category=PatternCategory.INTEGRATION_PATTERN,
        regex=re.compile(
            r"^(py|python)?(flask|django|fastapi|starlette)"
            r"-(openai|anthropic|gpt|claude)$"
        ),
        weight=0.55,
        description="Framework + AI provider integration pattern",
    ),
    # S054: Generic prefix patterns
    HallucinationPattern(
        id="EASY_PREFIX",
        category=PatternCategory.GENERIC_PREFIX,
        regex=re.compile(r"^easy[-_](requests|flask|django|api|http)"),
        weight=0.35,
        description="'easy-' prefix with popular package name",
    ),
    HallucinationPattern(
        id="SIMPLE_PREFIX",
        category=PatternCategory.GENERIC_PREFIX,
        regex=re.compile(r"^simple[-_](requests|flask|django|api|http)"),
        weight=0.35,
        description="'simple-' prefix with popular package name",
    ),
    HallucinationPattern(
        id="AUTO_PREFIX",
        category=PatternCategory.GENERIC_PREFIX,
        regex=re.compile(r"^auto[-_](flask|django|api|deploy|build)"),
        weight=0.3,
        description="'auto-' prefix pattern",
    ),
    # S055: Python-specific patterns
    HallucinationPattern(
        id="PY_PREFIX_AI",
        category=PatternCategory.AI_SUFFIX,
        regex=re.compile(r"^py(gpt|openai|claude|anthropic|llm)"),
        weight=0.5,
        description="'py' prefix with AI provider",
    ),
)


# =============================================================================
# PATTERN MATCHING FUNCTIONS
# =============================================================================


def match_patterns(name: str) -> tuple[Signal, ...]:
    """
    IMPLEMENTS: S005
    INVARIANT: INV008 - Pure function, no side effects

    Check package name against hallucination patterns.

    This is a pure function - calling it with the same input will
    always produce the same output, with no side effects.

    Args:
        name: Package name to check

    Returns:
        Tuple of signals for matched patterns (may be empty)
    """
    signals: list[Signal] = []
    normalized = name.lower().strip()

    for pattern in HALLUCINATION_PATTERNS:
        if pattern.matches(normalized):
            signals.append(
                Signal(
                    type=SignalType.HALLUCINATION_PATTERN,
                    weight=pattern.weight,
                    message=pattern.description,
                    metadata={
                        "pattern_id": pattern.id,
                        "category": pattern.category.value,
                    },
                )
            )

    return tuple(signals)


def get_pattern_by_id(pattern_id: str) -> HallucinationPattern | None:
    """
    Look up a pattern by its ID.

    Args:
        pattern_id: The pattern ID to find

    Returns:
        The matching pattern, or None if not found
    """
    for pattern in HALLUCINATION_PATTERNS:
        if pattern.id == pattern_id:
            return pattern
    return None


def list_patterns() -> list[dict[str, str]]:
    """
    List all registered patterns (for debugging/documentation).

    Returns:
        List of pattern dictionaries with id, category, weight, description
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


def get_highest_weight_pattern(name: str) -> HallucinationPattern | None:
    """
    Get the pattern with highest weight that matches the name.

    Useful for determining the primary reason a package was flagged.

    Args:
        name: Package name to check

    Returns:
        The highest-weight matching pattern, or None if no matches
    """
    normalized = name.lower().strip()
    matching_patterns = [p for p in HALLUCINATION_PATTERNS if p.matches(normalized)]

    if not matching_patterns:
        return None

    return max(matching_patterns, key=lambda p: p.weight)


def count_pattern_matches(name: str) -> int:
    """
    Count how many patterns match a package name.

    Multiple matches indicate higher hallucination probability.

    Args:
        name: Package name to check

    Returns:
        Number of matching patterns
    """
    normalized = name.lower().strip()
    return sum(1 for p in HALLUCINATION_PATTERNS if p.matches(normalized))
