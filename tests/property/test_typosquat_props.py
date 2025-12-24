# SPEC: S006 - Property Tests for Typosquat Detection
# Gate 3: Test Design - Implementation
"""
Property-based tests for Typosquat module invariants.

INVARIANTS: INV009
Uses Hypothesis for property-based testing.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from phantom_guard.core.typosquat import (
    TyposquatDetector,
    check_typosquat,
    detect_typosquat,
    levenshtein_distance,
    normalized_distance,
    similarity,
)


class TestTyposquatProperties:
    """Property-based tests for typosquat detection.

    INVARIANTS: INV009
    """

    # =========================================================================
    # INV009: Threshold in (0.0, 1.0) exclusive
    # =========================================================================

    @pytest.mark.property
    @given(st.floats(min_value=0.01, max_value=0.99, allow_nan=False))
    @settings(max_examples=50)
    def test_threshold_bounds(self, threshold: float) -> None:
        """
        TEST_ID: T006.P01
        SPEC: S006
        INV: INV009

        Property: For ANY valid threshold, it is in (0.0, 1.0) exclusive
        """
        detector = TyposquatDetector(threshold=threshold)
        assert 0.0 < detector.threshold < 1.0

    @pytest.mark.property
    def test_threshold_zero_rejected(self) -> None:
        """
        TEST_ID: T006.P02
        SPEC: S006
        INV: INV009

        Property: threshold=0.0 always raises ValueError
        """
        with pytest.raises(ValueError):
            TyposquatDetector(threshold=0.0)

    @pytest.mark.property
    def test_threshold_one_rejected(self) -> None:
        """
        TEST_ID: T006.P03
        SPEC: S006
        INV: INV009

        Property: threshold=1.0 always raises ValueError
        """
        with pytest.raises(ValueError):
            TyposquatDetector(threshold=1.0)

    # =========================================================================
    # Distance consistency
    # =========================================================================

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20), st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_distance_symmetry(self, a: str, b: str) -> None:
        """
        TEST_ID: T006.P04
        SPEC: S006

        Property: distance(a, b) == distance(b, a)
        """
        assert levenshtein_distance(a, b) == levenshtein_distance(b, a)

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_distance_identity(self, a: str) -> None:
        """
        TEST_ID: T006.P05
        SPEC: S006

        Property: distance(a, a) == 0 for any string a
        """
        assert levenshtein_distance(a, a) == 0

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20), st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_distance_non_negative(self, a: str, b: str) -> None:
        """
        TEST_ID: T006.P06
        SPEC: S006

        Property: distance(a, b) >= 0 for any strings a, b
        """
        assert levenshtein_distance(a, b) >= 0

    @pytest.mark.property
    @given(
        st.text(min_size=0, max_size=10),
        st.text(min_size=0, max_size=10),
        st.text(min_size=0, max_size=10),
    )
    @settings(max_examples=50)
    def test_distance_triangle_inequality(self, a: str, b: str, c: str) -> None:
        """
        TEST_ID: T006.P07
        SPEC: S006

        Property: distance(a, c) <= distance(a, b) + distance(b, c)
        """
        ab = levenshtein_distance(a, b)
        bc = levenshtein_distance(b, c)
        ac = levenshtein_distance(a, c)
        assert ac <= ab + bc

    # =========================================================================
    # Normalized distance properties
    # =========================================================================

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20), st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_normalized_distance_in_range(self, a: str, b: str) -> None:
        """
        Property: normalized_distance is always in [0.0, 1.0]
        """
        dist = normalized_distance(a, b)
        assert 0.0 <= dist <= 1.0

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_normalized_distance_identity(self, a: str) -> None:
        """
        Property: normalized_distance(a, a) == 0.0 for any string a
        """
        assert normalized_distance(a, a) == 0.0

    # =========================================================================
    # Similarity properties
    # =========================================================================

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20), st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_similarity_in_range(self, a: str, b: str) -> None:
        """
        Property: similarity is always in [0.0, 1.0]
        """
        sim = similarity(a, b)
        assert 0.0 <= sim <= 1.0

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_similarity_identity(self, a: str) -> None:
        """
        Property: similarity(a, a) == 1.0 for any string a
        """
        assert similarity(a, a) == 1.0

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20), st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_similarity_symmetry(self, a: str, b: str) -> None:
        """
        Property: similarity(a, b) == similarity(b, a)
        """
        assert similarity(a, b) == similarity(b, a)

    @pytest.mark.property
    @given(st.text(min_size=0, max_size=20), st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_similarity_plus_distance_equals_one(self, a: str, b: str) -> None:
        """
        Property: similarity(a, b) + normalized_distance(a, b) == 1.0
        """
        sim = similarity(a, b)
        dist = normalized_distance(a, b)
        assert abs(sim + dist - 1.0) < 1e-10


class TestTyposquatFuzz:
    """Fuzz tests for typosquat detection."""

    @pytest.mark.fuzz
    @given(
        st.text(
            min_size=0,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_"),
        )
    )
    @settings(max_examples=100)
    def test_fuzz_typosquat_never_crashes(self, name: str) -> None:
        """
        TEST_ID: T006.F01
        SPEC: S006

        Fuzz: Random strings never crash typosquat detection
        """
        # Should never raise an exception
        result = check_typosquat(name, "pypi")
        # Result is either None or a TyposquatMatch
        assert result is None or hasattr(result, "target")

    @pytest.mark.fuzz
    @given(
        st.text(
            min_size=0,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_"),
        )
    )
    @settings(max_examples=100)
    def test_fuzz_detect_typosquat_returns_tuple(self, name: str) -> None:
        """
        Fuzz: detect_typosquat always returns a tuple
        """
        result = detect_typosquat(name, "pypi")
        assert isinstance(result, tuple)

    @pytest.mark.fuzz
    @given(st.text(min_size=0, max_size=30))
    @settings(max_examples=100)
    def test_fuzz_levenshtein_never_crashes(self, s: str) -> None:
        """
        Fuzz: levenshtein_distance never crashes with arbitrary input
        """
        # Should handle any string without crashing
        result = levenshtein_distance(s, "requests")
        assert isinstance(result, int)
        assert result >= 0

    @pytest.mark.fuzz
    @given(st.sampled_from(["pypi", "npm", "crates", "unknown", ""]))
    @settings(max_examples=10)
    def test_fuzz_registry_values(self, registry: str) -> None:
        """
        Fuzz: Different registry values don't crash
        """
        # This might fail for invalid registries, but shouldn't crash
        try:
            result = check_typosquat("flak", registry)  # type: ignore[arg-type]
            assert result is None or hasattr(result, "target")
        except (ValueError, KeyError):
            # Expected for invalid registries
            pass


class TestDetectorProperties:
    """Property tests for TyposquatDetector class."""

    @pytest.mark.property
    @given(st.floats(min_value=-10.0, max_value=0.0, allow_nan=False))
    @settings(max_examples=20)
    def test_negative_threshold_rejected(self, threshold: float) -> None:
        """
        Property: Negative thresholds are always rejected
        """
        with pytest.raises(ValueError):
            TyposquatDetector(threshold=threshold)

    @pytest.mark.property
    @given(st.floats(min_value=1.0, max_value=10.0, allow_nan=False))
    @settings(max_examples=20)
    def test_threshold_above_one_rejected(self, threshold: float) -> None:
        """
        Property: Thresholds >= 1.0 are always rejected
        """
        with pytest.raises(ValueError):
            TyposquatDetector(threshold=threshold)

    @pytest.mark.property
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=10)
    def test_max_distance_accepted(self, max_dist: int) -> None:
        """
        Property: Positive max_distance values are accepted
        """
        detector = TyposquatDetector(max_distance=max_dist)
        assert detector.max_distance == max_dist


class TestPopularPackageProperties:
    """Property tests for popular package matching."""

    @pytest.mark.property
    @given(
        st.sampled_from(
            [
                "requests",
                "flask",
                "django",
                "numpy",
                "pandas",
                "react",
                "lodash",
                "express",
                "serde",
                "tokio",
                "reqwest",
            ]
        )
    )
    @settings(max_examples=20)
    def test_popular_packages_not_typosquats(self, name: str) -> None:
        """
        Property: Popular packages are never detected as typosquats of themselves
        """
        # Determine registry from package
        registry = "pypi"
        if name in {"react", "lodash", "express"}:
            registry = "npm"
        elif name in {"serde", "tokio", "reqwest"}:
            registry = "crates"

        result = check_typosquat(name, registry)  # type: ignore[arg-type]
        assert result is None, f"{name} should not be detected as a typosquat"
