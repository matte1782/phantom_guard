"""
SPEC: S005, S050-S059
TEST: Pattern matching tests for hallucination detection.

Tests cover:
- Pattern purity (INV008)
- AI suffix patterns (S050)
- Helper suffix patterns (S051)
- Combination patterns (S052)
- Integration patterns (S053)
- Generic prefix patterns (S054)
- Python-specific patterns (S055)
- No false positives for legitimate packages
"""

from __future__ import annotations

import pytest

from phantom_guard.core.patterns import (
    HALLUCINATION_PATTERNS,
    HallucinationPattern,
    PatternCategory,
    count_pattern_matches,
    get_highest_weight_pattern,
    get_pattern_by_id,
    list_patterns,
    match_patterns,
)
from phantom_guard.core.types import SignalType

# =============================================================================
# PURITY TESTS (INV008)
# =============================================================================


class TestPatternMatchingPurity:
    """INV008: Pattern matching must be pure (no side effects)."""

    def test_match_patterns_is_pure(self) -> None:
        """Calling match_patterns multiple times returns identical results."""
        name = "flask-gpt-helper"
        result1 = match_patterns(name)
        result2 = match_patterns(name)
        result3 = match_patterns(name)

        assert result1 == result2 == result3

    def test_match_patterns_does_not_mutate_input(self) -> None:
        """Input string is not modified."""
        name = "Flask-GPT-Helper"
        original = name
        _ = match_patterns(name)
        assert name == original

    def test_count_pattern_matches_is_pure(self) -> None:
        """count_pattern_matches is deterministic."""
        name = "flask-ai-utils"
        count1 = count_pattern_matches(name)
        count2 = count_pattern_matches(name)
        assert count1 == count2


# =============================================================================
# AI SUFFIX PATTERN TESTS (S050)
# =============================================================================


class TestAISuffixPatterns:
    """S050: AI-related suffix detection."""

    @pytest.mark.parametrize(
        "name",
        [
            "package-gpt",
            "package-ai",
            "package-llm",
            "package-openai",
            "package-chatgpt",
            "package-claude",
            "package-anthropic",
            "package-gemini",
        ],
    )
    def test_ai_suffix_detected(self, name: str) -> None:
        """AI suffixes should be detected."""
        signals = match_patterns(name)
        assert len(signals) > 0
        assert any(s.type == SignalType.HALLUCINATION_PATTERN for s in signals)

    def test_ai_infix_with_helper_detected(self) -> None:
        """AI component followed by helper suffix has high weight."""
        signals = match_patterns("package-gpt-helper")
        assert len(signals) > 0
        # Should match AI_GPT_INFIX pattern
        pattern_ids = [s.metadata.get("pattern_id") for s in signals if s.metadata]
        assert "AI_GPT_INFIX" in pattern_ids


# =============================================================================
# HELPER SUFFIX PATTERN TESTS (S051)
# =============================================================================


class TestHelperSuffixPatterns:
    """S051: Generic helper suffix detection."""

    @pytest.mark.parametrize(
        "name",
        [
            "package-helper",
            "package-utils",
            "package-tools",
            "package-wrapper",
            "package-client",
            "package-sdk",
        ],
    )
    def test_helper_suffix_detected(self, name: str) -> None:
        """Helper suffixes should be detected."""
        signals = match_patterns(name)
        assert len(signals) > 0
        pattern_ids = [s.metadata.get("pattern_id") for s in signals if s.metadata]
        assert "HELPER_SUFFIX" in pattern_ids


# =============================================================================
# COMBINATION PATTERN TESTS (S052)
# =============================================================================


class TestCombinationPatterns:
    """S052: High-risk combination patterns."""

    @pytest.mark.parametrize(
        "name",
        [
            "flask-gpt-helper",
            "django-ai-utils",
            "fastapi-llm-tools",
            "requests-openai-wrapper",
            "numpy-claude-client",
            "pandas-gpt-helper",
            "torch-ai-utils",
            "tensorflow-llm-tools",
        ],
    )
    def test_popular_ai_combo_highest_weight(self, name: str) -> None:
        """Popular package + AI + helper should have highest weight."""
        highest = get_highest_weight_pattern(name)
        assert highest is not None
        assert highest.id == "POPULAR_AI_COMBO"
        assert highest.weight == 0.85

    @pytest.mark.parametrize(
        "name",
        [
            "flask-gpt",
            "django-ai",
            "fastapi-openai",
            "requests-claude",
            "numpy-anthropic",
            "pandas-chatgpt",
        ],
    )
    def test_popular_ai_direct_detected(self, name: str) -> None:
        """Popular package + AI provider should be detected."""
        signals = match_patterns(name)
        pattern_ids = [s.metadata.get("pattern_id") for s in signals if s.metadata]
        assert "POPULAR_AI_DIRECT" in pattern_ids


# =============================================================================
# INTEGRATION PATTERN TESTS (S053)
# =============================================================================


class TestIntegrationPatterns:
    """S053: Framework + AI integration patterns."""

    @pytest.mark.parametrize(
        "name",
        [
            "flask-openai",
            "django-anthropic",
            "fastapi-gpt",
            "starlette-claude",
        ],
    )
    def test_integration_pattern_detected(self, name: str) -> None:
        """Framework-AI integration patterns should be detected."""
        signals = match_patterns(name)
        assert len(signals) > 0


# =============================================================================
# GENERIC PREFIX PATTERN TESTS (S054)
# =============================================================================


class TestGenericPrefixPatterns:
    """S054: Generic prefix patterns (easy-, simple-, auto-)."""

    @pytest.mark.parametrize(
        "name",
        [
            "easy-requests",
            "easy-flask",
            "easy-django",
            "easy-api",
            "easy-http",
        ],
    )
    def test_easy_prefix_detected(self, name: str) -> None:
        """'easy-' prefix with popular package should be detected."""
        signals = match_patterns(name)
        pattern_ids = [s.metadata.get("pattern_id") for s in signals if s.metadata]
        assert "EASY_PREFIX" in pattern_ids

    @pytest.mark.parametrize(
        "name",
        [
            "simple-requests",
            "simple-flask",
            "simple-django",
            "simple-api",
            "simple-http",
        ],
    )
    def test_simple_prefix_detected(self, name: str) -> None:
        """'simple-' prefix with popular package should be detected."""
        signals = match_patterns(name)
        pattern_ids = [s.metadata.get("pattern_id") for s in signals if s.metadata]
        assert "SIMPLE_PREFIX" in pattern_ids

    @pytest.mark.parametrize(
        "name",
        [
            "auto-flask",
            "auto-django",
            "auto-api",
            "auto-deploy",
            "auto-build",
        ],
    )
    def test_auto_prefix_detected(self, name: str) -> None:
        """'auto-' prefix should be detected."""
        signals = match_patterns(name)
        pattern_ids = [s.metadata.get("pattern_id") for s in signals if s.metadata]
        assert "AUTO_PREFIX" in pattern_ids


# =============================================================================
# PYTHON PREFIX PATTERN TESTS (S055)
# =============================================================================


class TestPythonPrefixPatterns:
    """S055: Python-specific patterns (py prefix + AI)."""

    @pytest.mark.parametrize(
        "name",
        [
            "pygpt",
            "pyopenai",
            "pyclaude",
            "pyanthropic",
            "pyllm",
        ],
    )
    def test_py_prefix_ai_detected(self, name: str) -> None:
        """'py' prefix with AI provider should be detected."""
        signals = match_patterns(name)
        pattern_ids = [s.metadata.get("pattern_id") for s in signals if s.metadata]
        assert "PY_PREFIX_AI" in pattern_ids


# =============================================================================
# LEGITIMATE PACKAGE TESTS (No False Positives)
# =============================================================================


class TestLegitimatePackages:
    """Ensure legitimate packages don't trigger false positives."""

    @pytest.mark.parametrize(
        "name",
        [
            "requests",
            "flask",
            "django",
            "numpy",
            "pandas",
            "pytest",
            "black",
            "ruff",
            "mypy",
            "sqlalchemy",
            "pydantic",
            "fastapi",
            "celery",
            "redis",
            "boto3",
            "beautifulsoup4",
            "pillow",
            "matplotlib",
            "scipy",
            "scikit-learn",
        ],
    )
    def test_popular_packages_not_flagged(self, name: str) -> None:
        """Popular legitimate packages should not be flagged."""
        signals = match_patterns(name)
        assert len(signals) == 0

    @pytest.mark.parametrize(
        "name",
        [
            "my-custom-package",
            "company-internal-lib",
            "data-processor",
            "file-handler",
        ],
    )
    def test_generic_names_no_signals(self, name: str) -> None:
        """Generic custom names should not have signals."""
        signals = match_patterns(name)
        assert len(signals) == 0


# =============================================================================
# CASE INSENSITIVITY TESTS
# =============================================================================


class TestCaseInsensitivity:
    """Pattern matching should be case insensitive."""

    @pytest.mark.parametrize(
        "name",
        [
            "Flask-GPT-Helper",
            "FLASK-GPT-HELPER",
            "flask-gpt-helper",
            "Flask-Gpt-Helper",
            "FLASK-gpt-HELPER",
        ],
    )
    def test_case_variations_detected(self, name: str) -> None:
        """All case variations should be detected equally."""
        signals = match_patterns(name)
        assert len(signals) > 0
        # All should match the same patterns
        base_signals = match_patterns("flask-gpt-helper")
        assert len(signals) == len(base_signals)


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestGetPatternById:
    """Test get_pattern_by_id function."""

    def test_existing_pattern_found(self) -> None:
        """Existing pattern IDs should be found."""
        pattern = get_pattern_by_id("AI_GPT_SUFFIX")
        assert pattern is not None
        assert pattern.id == "AI_GPT_SUFFIX"

    def test_nonexistent_pattern_returns_none(self) -> None:
        """Nonexistent pattern IDs should return None."""
        pattern = get_pattern_by_id("NONEXISTENT_PATTERN")
        assert pattern is None

    def test_all_registered_patterns_findable(self) -> None:
        """All patterns in registry should be findable by ID."""
        for pattern in HALLUCINATION_PATTERNS:
            found = get_pattern_by_id(pattern.id)
            assert found is not None
            assert found.id == pattern.id


class TestGetHighestWeightPattern:
    """Test get_highest_weight_pattern function."""

    def test_highest_weight_returned(self) -> None:
        """Should return pattern with highest weight."""
        # flask-gpt-helper matches multiple patterns
        highest = get_highest_weight_pattern("flask-gpt-helper")
        assert highest is not None
        assert highest.id == "POPULAR_AI_COMBO"
        assert highest.weight == 0.85

    def test_no_match_returns_none(self) -> None:
        """Non-matching name should return None."""
        highest = get_highest_weight_pattern("requests")
        assert highest is None

    def test_single_match_returns_that_pattern(self) -> None:
        """Single matching pattern should be returned."""
        highest = get_highest_weight_pattern("package-helper")
        assert highest is not None
        assert highest.id == "HELPER_SUFFIX"


class TestCountPatternMatches:
    """Test count_pattern_matches function."""

    def test_zero_matches_for_legitimate(self) -> None:
        """Legitimate packages should have zero matches."""
        count = count_pattern_matches("requests")
        assert count == 0

    def test_multiple_matches_counted(self) -> None:
        """Multiple matching patterns should be counted."""
        count = count_pattern_matches("flask-gpt-helper")
        assert count >= 2  # At least POPULAR_AI_COMBO and AI_GPT_INFIX

    def test_single_match_counted(self) -> None:
        """Single matching pattern should return 1."""
        count = count_pattern_matches("package-helper")
        assert count == 1


class TestListPatterns:
    """Test list_patterns function."""

    def test_returns_list_of_dicts(self) -> None:
        """Should return list of pattern dictionaries."""
        patterns = list_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert all(isinstance(p, dict) for p in patterns)

    def test_dict_has_required_keys(self) -> None:
        """Each dict should have id, category, weight, description."""
        patterns = list_patterns()
        required_keys = {"id", "category", "weight", "description"}
        for pattern in patterns:
            assert required_keys.issubset(pattern.keys())

    def test_all_registered_patterns_listed(self) -> None:
        """All registered patterns should be in the list."""
        patterns = list_patterns()
        pattern_ids = {p["id"] for p in patterns}
        for pattern in HALLUCINATION_PATTERNS:
            assert pattern.id in pattern_ids


# =============================================================================
# PATTERN REGISTRY TESTS
# =============================================================================


class TestPatternRegistry:
    """Test the HALLUCINATION_PATTERNS registry."""

    def test_registry_is_tuple(self) -> None:
        """Registry should be immutable tuple."""
        assert isinstance(HALLUCINATION_PATTERNS, tuple)

    def test_registry_not_empty(self) -> None:
        """Registry should contain patterns."""
        assert len(HALLUCINATION_PATTERNS) > 0

    def test_all_patterns_are_hallucination_pattern(self) -> None:
        """All entries should be HallucinationPattern instances."""
        for pattern in HALLUCINATION_PATTERNS:
            assert isinstance(pattern, HallucinationPattern)

    def test_unique_pattern_ids(self) -> None:
        """All pattern IDs should be unique."""
        ids = [p.id for p in HALLUCINATION_PATTERNS]
        assert len(ids) == len(set(ids))

    def test_weights_in_valid_range(self) -> None:
        """All weights should be in (0, 1] range."""
        for pattern in HALLUCINATION_PATTERNS:
            assert 0 < pattern.weight <= 1.0

    def test_all_categories_valid(self) -> None:
        """All categories should be valid PatternCategory values."""
        for pattern in HALLUCINATION_PATTERNS:
            assert isinstance(pattern.category, PatternCategory)


# =============================================================================
# HALLUCINATION PATTERN TESTS
# =============================================================================


class TestHallucinationPattern:
    """Test HallucinationPattern dataclass."""

    def test_pattern_is_frozen(self) -> None:
        """Pattern should be immutable."""
        pattern = HALLUCINATION_PATTERNS[0]
        with pytest.raises(AttributeError):
            pattern.id = "NEW_ID"  # type: ignore[misc]

    def test_matches_method_works(self) -> None:
        """matches() method should work correctly."""
        pattern = get_pattern_by_id("HELPER_SUFFIX")
        assert pattern is not None
        assert pattern.matches("package-helper") is True
        assert pattern.matches("package") is False

    def test_matches_is_case_insensitive(self) -> None:
        """matches() should be case insensitive."""
        pattern = get_pattern_by_id("HELPER_SUFFIX")
        assert pattern is not None
        assert pattern.matches("Package-Helper") is True
        assert pattern.matches("PACKAGE-HELPER") is True


# =============================================================================
# SIGNAL METADATA TESTS
# =============================================================================


class TestSignalMetadata:
    """Test that signals contain correct metadata."""

    def test_signals_have_pattern_id(self) -> None:
        """Signals should contain pattern_id in metadata."""
        signals = match_patterns("flask-gpt-helper")
        for signal in signals:
            assert "pattern_id" in signal.metadata

    def test_signals_have_category(self) -> None:
        """Signals should contain category in metadata."""
        signals = match_patterns("flask-gpt-helper")
        for signal in signals:
            assert "category" in signal.metadata

    def test_signal_type_is_hallucination_pattern(self) -> None:
        """All signals should be HALLUCINATION_PATTERN type."""
        signals = match_patterns("flask-gpt-helper")
        for signal in signals:
            assert signal.type == SignalType.HALLUCINATION_PATTERN

    def test_signal_weights_match_pattern_weights(self) -> None:
        """Signal weights should match their source pattern weights."""
        signals = match_patterns("flask-gpt-helper")
        for signal in signals:
            pattern_id = signal.metadata.get("pattern_id")
            pattern = get_pattern_by_id(str(pattern_id))
            assert pattern is not None
            assert signal.weight == pattern.weight


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self) -> None:
        """Empty string should return no signals."""
        signals = match_patterns("")
        assert len(signals) == 0

    def test_whitespace_only(self) -> None:
        """Whitespace-only string should return no signals."""
        signals = match_patterns("   ")
        assert len(signals) == 0

    def test_single_character(self) -> None:
        """Single character should return no signals."""
        signals = match_patterns("a")
        assert len(signals) == 0

    def test_very_long_name(self) -> None:
        """Very long name should still work."""
        long_name = "a" * 200 + "-gpt"
        signals = match_patterns(long_name)
        # Should detect AI suffix
        assert len(signals) > 0

    def test_special_regex_characters_in_name(self) -> None:
        """Names with regex special chars should not break matching."""
        # These shouldn't match any pattern but shouldn't crash
        signals = match_patterns("package[test]")
        assert isinstance(signals, tuple)

        signals = match_patterns("package(test)")
        assert isinstance(signals, tuple)

    def test_numeric_name(self) -> None:
        """Numeric-only names should not crash."""
        signals = match_patterns("12345")
        assert isinstance(signals, tuple)
