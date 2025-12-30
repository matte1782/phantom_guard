# SPEC: S006 - Typosquat Detection
# Gate 3: Test Design - Implementation
"""
Unit tests for the Typosquat module.

SPEC_IDs: S006
TEST_IDs: T006.*
INVARIANTS: INV009
EDGE_CASES: EC046
"""

from __future__ import annotations

import pytest

from phantom_guard.core.types import SignalType
from phantom_guard.core.typosquat import (
    DEFAULT_SIMILARITY_THRESHOLD,
    MAX_EDIT_DISTANCE,
    MIN_NAME_LENGTH,
    TyposquatDetector,
    TyposquatMatch,
    check_typosquat,
    detect_typosquat,
    find_typosquat_targets,
    get_popular_packages,
    is_popular_package,
    levenshtein_distance,
    normalized_distance,
    similarity,
)
from phantom_guard.data import POPULAR_BY_REGISTRY as POPULAR_PACKAGES


class TestTyposquatDetection:
    """Tests for typosquat detection.

    SPEC: S006 - Typosquat detection
    Total tests: 14 (10 unit, 2 property, 1 fuzz, 1 bench)
    """

    # =========================================================================
    # KNOWN TYPOSQUAT TESTS
    # =========================================================================

    @pytest.mark.unit
    def test_typosquat_reqeusts(self) -> None:
        """
        TEST_ID: T006.01
        SPEC: S006
        EC: EC046

        Given: Package name "reqeusts"
        When: check_typosquat is called
        Then: Returns match with target="requests"
        """
        match = check_typosquat("reqeusts", "pypi")
        assert match is not None
        assert match.target == "requests"
        assert match.distance == 2  # Transposition + swap

    @pytest.mark.unit
    def test_typosquat_djagno(self) -> None:
        """
        TEST_ID: T006.02
        SPEC: S006
        EC: EC046

        Given: Package name "djagno"
        When: check_typosquat is called
        Then: Returns match with target="django"
        """
        match = check_typosquat("djagno", "pypi")
        assert match is not None
        assert match.target == "django"
        assert match.distance == 2  # Two transpositions

    @pytest.mark.unit
    def test_typosquat_flak(self) -> None:
        """
        TEST_ID: T006.03
        SPEC: S006
        EC: EC046

        Given: Package name "flak"
        When: check_typosquat is called
        Then: Returns match with target="flask"
        """
        match = check_typosquat("flak", "pypi")
        assert match is not None
        assert match.target == "flask"
        assert match.distance == 1  # Missing 's'

    @pytest.mark.unit
    def test_typosquat_numppy(self) -> None:
        """
        TEST_ID: T006.04
        SPEC: S006
        EC: EC046

        Given: Package name "numppy"
        When: check_typosquat is called
        Then: Returns match with target="numpy"
        """
        match = check_typosquat("numppy", "pypi")
        assert match is not None
        assert match.target == "numpy"
        assert match.distance == 1  # Extra 'p'

    @pytest.mark.unit
    def test_typosquat_padas(self) -> None:
        """
        TEST_ID: T006.05
        SPEC: S006
        EC: EC046

        Given: Package name "padas"
        When: check_typosquat is called
        Then: Returns match with target="pandas"
        """
        match = check_typosquat("padas", "pypi")
        assert match is not None
        assert match.target == "pandas"
        assert match.distance == 1  # Missing 'n'

    # =========================================================================
    # LEGITIMATE PACKAGE TESTS (NO FALSE POSITIVES)
    # =========================================================================

    @pytest.mark.unit
    def test_legitimate_flask_no_match(self) -> None:
        """
        TEST_ID: T006.06
        SPEC: S006

        Given: Package name "flask" (legitimate)
        When: check_typosquat is called
        Then: Returns None
        """
        match = check_typosquat("flask", "pypi")
        assert match is None

    @pytest.mark.unit
    def test_legitimate_requests_no_match(self) -> None:
        """
        TEST_ID: T006.07
        SPEC: S006

        Given: Package name "requests" (legitimate)
        When: check_typosquat is called
        Then: Returns None
        """
        match = check_typosquat("requests", "pypi")
        assert match is None

    @pytest.mark.unit
    def test_similar_but_distinct_no_match(self) -> None:
        """
        TEST_ID: T006.08
        SPEC: S006

        Given: Package name similar but distinct (e.g., "flask-cors")
        When: check_typosquat is called
        Then: Returns None (not a typosquat)
        """
        # flask-cors is a real package, not a typosquat of flask
        match = check_typosquat("flask-cors", "pypi")
        # The name is long enough that it won't match closely
        assert match is None

    # =========================================================================
    # THRESHOLD TESTS (INV009)
    # =========================================================================

    @pytest.mark.unit
    def test_threshold_in_valid_range(self) -> None:
        """
        TEST_ID: T006.09
        SPEC: S006
        INV: INV009

        Given: Typosquat detector initialized
        When: Checking threshold value
        Then: Threshold is in (0.0, 1.0) exclusive
        """
        detector = TyposquatDetector()
        assert 0.0 < detector.threshold < 1.0

    @pytest.mark.unit
    def test_threshold_zero_rejected(self) -> None:
        """
        TEST_ID: T006.10
        SPEC: S006
        INV: INV009

        Given: Attempting to set threshold = 0.0
        When: Typosquat detector initialized
        Then: Raises ValueError
        """
        with pytest.raises(ValueError, match="exclusive"):
            TyposquatDetector(threshold=0.0)

    @pytest.mark.unit
    def test_threshold_one_rejected(self) -> None:
        """
        TEST_ID: T006.11
        SPEC: S006
        INV: INV009

        Given: Attempting to set threshold = 1.0
        When: Typosquat detector initialized
        Then: Raises ValueError
        """
        with pytest.raises(ValueError, match="exclusive"):
            TyposquatDetector(threshold=1.0)

    @pytest.mark.unit
    def test_threshold_affects_sensitivity(self) -> None:
        """
        TEST_ID: T006.12
        SPEC: S006

        Given: Same input with different thresholds
        When: check_typosquat is called
        Then: Higher threshold = fewer matches
        """
        # Lower threshold = more sensitive (catches more)
        low_threshold = TyposquatDetector(threshold=0.7)
        high_threshold = TyposquatDetector(threshold=0.95)

        # "requets" is distance 2 from "requests"
        low_matches = low_threshold.find_matches("requets", "pypi")
        high_matches = high_threshold.find_matches("requets", "pypi")

        assert len(low_matches) >= len(high_matches)

    # =========================================================================
    # EDGE CASE TESTS
    # =========================================================================

    @pytest.mark.unit
    def test_single_char_difference(self) -> None:
        """
        TEST_ID: T006.13
        SPEC: S006

        Given: Package name with single char typo
        When: check_typosquat is called
        Then: Detects as typosquat
        """
        # "flusk" instead of "flask" - single substitution
        match = check_typosquat("flusk", "pypi")
        assert match is not None
        assert match.target == "flask"
        assert match.distance == 1

    @pytest.mark.unit
    def test_transposed_chars(self) -> None:
        """
        TEST_ID: T006.14
        SPEC: S006

        Given: Package name with transposed chars
        When: check_typosquat is called
        Then: Detects as typosquat
        """
        # "flaask" - extra character
        match = check_typosquat("flaask", "pypi")
        assert match is not None
        assert match.target == "flask"

    @pytest.mark.unit
    def test_added_char(self) -> None:
        """
        TEST_ID: T006.15
        SPEC: S006

        Given: Package name with added char
        When: check_typosquat is called
        Then: Detects as typosquat
        """
        # "numpyy" - extra y
        match = check_typosquat("numpyy", "pypi")
        assert match is not None
        assert match.target == "numpy"
        assert match.distance == 1

    @pytest.mark.unit
    def test_removed_char(self) -> None:
        """
        TEST_ID: T006.16
        SPEC: S006

        Given: Package name with removed char
        When: check_typosquat is called
        Then: Detects as typosquat
        """
        # "panads" - swapped 'n' and 'a'
        match = check_typosquat("panads", "pypi")
        assert match is not None
        assert match.target == "pandas"


class TestLevenshteinDistance:
    """Tests for Levenshtein distance calculation.

    SPEC: S006
    """

    @pytest.mark.unit
    def test_identical_strings_distance_zero(self) -> None:
        """
        TEST_ID: T006.17
        SPEC: S006

        Given: Two identical strings
        When: Calculating distance
        Then: Returns 0
        """
        assert levenshtein_distance("flask", "flask") == 0
        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("a", "a") == 0

    @pytest.mark.unit
    def test_empty_string_distance(self) -> None:
        """
        TEST_ID: T006.18
        SPEC: S006

        Given: One empty string
        When: Calculating distance
        Then: Returns length of other string
        """
        assert levenshtein_distance("", "flask") == 5
        assert levenshtein_distance("flask", "") == 5
        assert levenshtein_distance("", "abc") == 3

    @pytest.mark.unit
    def test_single_substitution_distance_one(self) -> None:
        """
        TEST_ID: T006.19
        SPEC: S006

        Given: Strings differing by one char
        When: Calculating distance
        Then: Returns 1
        """
        assert levenshtein_distance("cat", "bat") == 1
        assert levenshtein_distance("cat", "car") == 1
        assert levenshtein_distance("cat", "cut") == 1

    @pytest.mark.unit
    def test_single_insertion_distance_one(self) -> None:
        """
        TEST_ID: T006.20
        SPEC: S006

        Given: One string has one extra character
        When: Calculating distance
        Then: Returns 1
        """
        assert levenshtein_distance("cat", "cats") == 1
        assert levenshtein_distance("cat", "cart") == 1
        assert levenshtein_distance("cat", "chat") == 1

    @pytest.mark.unit
    def test_single_deletion_distance_one(self) -> None:
        """
        TEST_ID: T006.21
        SPEC: S006

        Given: One string has one fewer character
        When: Calculating distance
        Then: Returns 1
        """
        assert levenshtein_distance("cats", "cat") == 1
        assert levenshtein_distance("cart", "cat") == 1

    @pytest.mark.unit
    def test_distance_symmetry(self) -> None:
        """
        TEST_ID: T006.22
        SPEC: S006

        Given: Any two strings
        When: Calculating distance both ways
        Then: Results are equal
        """
        assert levenshtein_distance("flask", "flak") == levenshtein_distance("flak", "flask")
        assert levenshtein_distance("abc", "xyz") == levenshtein_distance("xyz", "abc")
        assert levenshtein_distance("", "test") == levenshtein_distance("test", "")


class TestNormalizedDistance:
    """Tests for normalized distance calculation."""

    @pytest.mark.unit
    def test_identical_strings_zero(self) -> None:
        """Identical strings have 0 normalized distance."""
        assert normalized_distance("flask", "flask") == 0.0

    @pytest.mark.unit
    def test_completely_different_one(self) -> None:
        """Completely different strings have distance close to 1."""
        dist = normalized_distance("abc", "xyz")
        assert dist == 1.0  # All 3 chars different

    @pytest.mark.unit
    def test_empty_strings_zero(self) -> None:
        """Two empty strings have 0 distance."""
        assert normalized_distance("", "") == 0.0


class TestSimilarity:
    """Tests for similarity calculation."""

    @pytest.mark.unit
    def test_identical_strings_one(self) -> None:
        """Identical strings have similarity 1.0."""
        assert similarity("flask", "flask") == 1.0

    @pytest.mark.unit
    def test_completely_different_zero(self) -> None:
        """Completely different strings have similarity 0.0."""
        assert similarity("abc", "xyz") == 0.0

    @pytest.mark.unit
    def test_similar_high_score(self) -> None:
        """Similar strings have high similarity score."""
        sim = similarity("flask", "flak")
        assert sim > 0.7  # 1 char difference out of 5


class TestPopularPackages:
    """Tests for popular packages database."""

    @pytest.mark.unit
    def test_pypi_packages_present(self) -> None:
        """PyPI popular packages are present."""
        pypi = get_popular_packages("pypi")
        assert "requests" in pypi
        assert "flask" in pypi
        assert "django" in pypi
        assert "numpy" in pypi
        assert "pandas" in pypi

    @pytest.mark.unit
    def test_npm_packages_present(self) -> None:
        """npm popular packages are present."""
        npm = get_popular_packages("npm")
        assert "react" in npm
        assert "lodash" in npm
        assert "express" in npm

    @pytest.mark.unit
    def test_crates_packages_present(self) -> None:
        """crates.io popular packages are present."""
        crates = get_popular_packages("crates")
        assert "serde" in crates
        assert "tokio" in crates
        assert "reqwest" in crates

    @pytest.mark.unit
    def test_unknown_registry_fallback_to_pypi(self) -> None:
        """Unknown registry falls back to PyPI popular packages."""
        unknown_packages = get_popular_packages("unknown")
        pypi_packages = get_popular_packages("pypi")
        assert unknown_packages == pypi_packages

    @pytest.mark.unit
    def test_is_popular_package(self) -> None:
        """is_popular_package correctly identifies popular packages."""
        assert is_popular_package("flask", "pypi") is True
        assert is_popular_package("Flask", "pypi") is True  # Case insensitive
        assert is_popular_package("not-a-package", "pypi") is False

    @pytest.mark.unit
    def test_packages_are_frozenset(self) -> None:
        """Package sets are immutable frozensets."""
        for _registry, packages in POPULAR_PACKAGES.items():
            assert isinstance(packages, frozenset)


class TestDetectTyposquat:
    """Tests for detect_typosquat signal generation."""

    @pytest.mark.unit
    def test_returns_signals(self) -> None:
        """detect_typosquat returns Signal objects."""
        signals = detect_typosquat("reqeusts", "pypi")
        assert len(signals) > 0
        assert all(s.type == SignalType.TYPOSQUAT for s in signals)

    @pytest.mark.unit
    def test_signal_has_metadata(self) -> None:
        """Signal metadata contains target and distance."""
        signals = detect_typosquat("flak", "pypi")
        assert len(signals) > 0
        signal = signals[0]
        assert "target" in signal.metadata
        assert "distance" in signal.metadata
        assert "similarity" in signal.metadata
        assert signal.metadata["target"] == "flask"

    @pytest.mark.unit
    def test_no_match_empty_tuple(self) -> None:
        """No match returns empty tuple."""
        signals = detect_typosquat("completely-unique-name", "pypi")
        assert signals == ()

    @pytest.mark.unit
    def test_signal_weight_bounds(self) -> None:
        """Signal weights are within expected bounds."""
        signals = detect_typosquat("flak", "pypi")
        assert len(signals) > 0
        for signal in signals:
            assert 0.3 <= signal.weight <= 0.95


class TestFindTyposquatTargets:
    """Tests for find_typosquat_targets function."""

    @pytest.mark.unit
    def test_returns_sorted_by_similarity(self) -> None:
        """Results are sorted by similarity (highest first)."""
        matches = find_typosquat_targets("flak", "pypi")
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                assert matches[i].similarity >= matches[i + 1].similarity

    @pytest.mark.unit
    def test_short_names_no_matches(self) -> None:
        """Short names (< MIN_NAME_LENGTH) return no matches."""
        matches = find_typosquat_targets("ab", "pypi")
        assert matches == []
        matches = find_typosquat_targets("abc", "pypi")
        assert matches == []

    @pytest.mark.unit
    def test_exact_match_not_returned(self) -> None:
        """Exact matches are not returned as typosquats."""
        matches = find_typosquat_targets("flask", "pypi")
        assert all(m.target != "flask" for m in matches)

    @pytest.mark.unit
    def test_custom_max_distance(self) -> None:
        """Custom max_distance creates new detector."""
        # Default max_distance is 2, using 3 should find more matches
        matches_default = find_typosquat_targets("flak", "pypi")
        matches_custom = find_typosquat_targets("flak", "pypi", max_distance=3)
        # Both should find flask (distance 1)
        assert len(matches_default) > 0
        assert len(matches_custom) >= len(matches_default)


class TestTyposquatDetectorClass:
    """Tests for TyposquatDetector class."""

    @pytest.mark.unit
    def test_default_threshold(self) -> None:
        """Default threshold is set correctly."""
        detector = TyposquatDetector()
        assert detector.threshold == DEFAULT_SIMILARITY_THRESHOLD

    @pytest.mark.unit
    def test_custom_threshold(self) -> None:
        """Custom threshold is accepted."""
        detector = TyposquatDetector(threshold=0.5)
        assert detector.threshold == 0.5

    @pytest.mark.unit
    def test_max_distance_property(self) -> None:
        """max_distance property returns correct value."""
        detector = TyposquatDetector(max_distance=3)
        assert detector.max_distance == 3

    @pytest.mark.unit
    def test_threshold_edge_values_rejected(self) -> None:
        """Edge values 0.0 and 1.0 are rejected."""
        with pytest.raises(ValueError):
            TyposquatDetector(threshold=0.0)
        with pytest.raises(ValueError):
            TyposquatDetector(threshold=1.0)

    @pytest.mark.unit
    def test_negative_threshold_rejected(self) -> None:
        """Negative threshold is rejected."""
        with pytest.raises(ValueError):
            TyposquatDetector(threshold=-0.5)

    @pytest.mark.unit
    def test_threshold_greater_than_one_rejected(self) -> None:
        """Threshold > 1.0 is rejected."""
        with pytest.raises(ValueError):
            TyposquatDetector(threshold=1.5)


class TestTyposquatMatch:
    """Tests for TyposquatMatch dataclass."""

    @pytest.mark.unit
    def test_match_is_frozen(self) -> None:
        """TyposquatMatch is immutable."""
        match = TyposquatMatch(target="flask", distance=1, similarity=0.8)
        with pytest.raises(AttributeError):
            match.target = "django"  # type: ignore[misc]

    @pytest.mark.unit
    def test_match_has_slots(self) -> None:
        """TyposquatMatch uses slots for memory efficiency."""
        match = TyposquatMatch(target="flask", distance=1, similarity=0.8)
        assert hasattr(match, "__slots__")


class TestConstants:
    """Tests for module constants."""

    @pytest.mark.unit
    def test_max_edit_distance_positive(self) -> None:
        """MAX_EDIT_DISTANCE is a positive integer."""
        assert isinstance(MAX_EDIT_DISTANCE, int)
        assert MAX_EDIT_DISTANCE > 0

    @pytest.mark.unit
    def test_min_name_length_positive(self) -> None:
        """MIN_NAME_LENGTH is a positive integer."""
        assert isinstance(MIN_NAME_LENGTH, int)
        assert MIN_NAME_LENGTH > 0

    @pytest.mark.unit
    def test_default_threshold_valid(self) -> None:
        """DEFAULT_SIMILARITY_THRESHOLD is in valid range."""
        assert 0.0 < DEFAULT_SIMILARITY_THRESHOLD < 1.0
