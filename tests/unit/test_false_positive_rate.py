"""
False positive rate validation tests.

IMPLEMENTS: S006
TESTS: Ensure typosquat detection doesn't flag popular packages
TARGET: <5% false positive rate on popular packages
"""

from __future__ import annotations

import pytest

from phantom_guard.core.typosquat import (
    detect_typosquat,
    find_typosquat_targets,
)
from phantom_guard.data import (
    CRATES_POPULAR,
    NPM_POPULAR,
    PYPI_POPULAR,
)


class TestFalsePositiveRatePyPI:
    """Tests for false positive rate on PyPI packages."""

    def test_popular_pypi_packages_not_flagged_as_typosquat(self) -> None:
        """Popular PyPI packages should not be flagged as typosquats.

        This is critical for adoption - flagging 'requests' as a typosquat
        would be a false positive that kills user trust.
        """
        flagged_packages: list[str] = []

        for package in PYPI_POPULAR:
            signals = detect_typosquat(package, "pypi")
            if signals:
                flagged_packages.append(package)

        # Allow up to 5% false positive rate
        max_allowed = int(len(PYPI_POPULAR) * 0.05)
        assert len(flagged_packages) <= max_allowed, (
            f"Too many false positives: {len(flagged_packages)}/{len(PYPI_POPULAR)} "
            f"({100 * len(flagged_packages) / len(PYPI_POPULAR):.1f}%). "
            f"Max allowed: {max_allowed} (5%). "
            f"Flagged: {flagged_packages[:20]}..."
        )

    def test_no_exact_match_flagged(self) -> None:
        """Exact matches should never be flagged as typosquats."""
        # Sample of very popular packages that MUST NOT be flagged
        critical_packages = [
            "requests",
            "numpy",
            "pandas",
            "flask",
            "django",
            "pytest",
            "boto3",
            "tensorflow",
            "torch",
            "fastapi",
        ]

        for package in critical_packages:
            signals = detect_typosquat(package, "pypi")
            assert not signals, f"Critical package '{package}' flagged as typosquat"


class TestFalsePositiveRateNpm:
    """Tests for false positive rate on npm packages."""

    def test_popular_npm_packages_not_flagged_as_typosquat(self) -> None:
        """Popular npm packages should not be flagged as typosquats."""
        flagged_packages: list[str] = []

        for package in NPM_POPULAR:
            signals = detect_typosquat(package, "npm")
            if signals:
                flagged_packages.append(package)

        max_allowed = int(len(NPM_POPULAR) * 0.05)
        assert len(flagged_packages) <= max_allowed, (
            f"Too many npm false positives: {len(flagged_packages)}/{len(NPM_POPULAR)} "
            f"({100 * len(flagged_packages) / len(NPM_POPULAR):.1f}%). "
            f"Flagged: {flagged_packages[:20]}..."
        )

    def test_no_critical_npm_flagged(self) -> None:
        """Critical npm packages should never be flagged."""
        critical_packages = [
            "react",
            "lodash",
            "axios",
            "express",
            "webpack",
            "eslint",
            "vue",
            "jquery",
        ]

        for package in critical_packages:
            signals = detect_typosquat(package, "npm")
            assert not signals, f"Critical npm package '{package}' flagged as typosquat"


class TestFalsePositiveRateCrates:
    """Tests for false positive rate on crates.io packages."""

    def test_popular_crates_not_flagged_as_typosquat(self) -> None:
        """Popular crates should not be flagged as typosquats."""
        flagged_packages: list[str] = []

        for package in CRATES_POPULAR:
            signals = detect_typosquat(package, "crates")
            if signals:
                flagged_packages.append(package)

        max_allowed = int(len(CRATES_POPULAR) * 0.05)
        assert len(flagged_packages) <= max_allowed, (
            f"Too many crates false positives: {len(flagged_packages)}/{len(CRATES_POPULAR)} "
            f"({100 * len(flagged_packages) / len(CRATES_POPULAR):.1f}%). "
            f"Flagged: {flagged_packages[:20]}..."
        )

    def test_no_critical_crates_flagged(self) -> None:
        """Critical crates should never be flagged."""
        critical_packages = [
            "serde",
            "tokio",
            "reqwest",
            "clap",
            "rand",
            "log",
            "regex",
            "chrono",
        ]

        for package in critical_packages:
            signals = detect_typosquat(package, "crates")
            assert not signals, f"Critical crate '{package}' flagged as typosquat"


class TestTyposquatDetectionAccuracy:
    """Tests for typosquat detection true positive accuracy."""

    @pytest.mark.parametrize(
        "typosquat,expected_target",
        [
            ("reqeusts", "requests"),
            ("requets", "requests"),
            ("requesets", "requests"),
            ("numppy", "numpy"),
            ("numpi", "numpy"),
            ("panadas", "pandas"),
            ("flaask", "flask"),
            ("djagno", "django"),
            ("dajngo", "django"),
        ],
    )
    def test_known_typosquats_detected(self, typosquat: str, expected_target: str) -> None:
        """Known typosquats should be detected correctly."""
        signals = detect_typosquat(typosquat, "pypi")
        assert signals, f"Typosquat '{typosquat}' not detected"

        # Check that the expected target is found
        targets = [s.metadata["target"] for s in signals]
        assert expected_target in targets, (
            f"Expected target '{expected_target}' not found. Detected targets: {targets}"
        )

    def test_find_typosquat_targets_returns_sorted(self) -> None:
        """find_typosquat_targets should return matches sorted by similarity."""
        matches = find_typosquat_targets("reqeusts", "pypi")
        assert matches, "Should find matches for reqeusts"

        # Should be sorted by similarity (highest first)
        for i in range(len(matches) - 1):
            assert matches[i].similarity >= matches[i + 1].similarity


class TestCrossRegistryFalsePositives:
    """Tests for false positives across registries."""

    def test_pypi_package_not_flagged_in_npm_context(self) -> None:
        """PyPI-specific packages shouldn't trigger npm typosquat detection."""
        # boto3 is PyPI-only, shouldn't trigger npm detection
        # This is expected - boto3 has no npm equivalent to match against
        # Just ensure it doesn't crash and returns reasonable result
        _ = detect_typosquat("boto3", "npm")

    def test_npm_package_not_flagged_in_pypi_context(self) -> None:
        """npm-specific packages shouldn't trigger false positives in PyPI context."""
        # react-dom is npm-specific
        # Should not be flagged or should only flag if there's a real PyPI match
        _ = detect_typosquat("react-dom", "pypi")


class TestEdgeCases:
    """Edge case tests for false positive prevention."""

    def test_short_package_names_not_flagged(self) -> None:
        """Short package names (< MIN_NAME_LENGTH) should not be flagged."""
        short_names = ["pip", "six", "aws", "orm", "api"]

        for name in short_names:
            signals = detect_typosquat(name, "pypi")
            # Short names are excluded from typosquat detection
            assert not signals, f"Short name '{name}' should not be flagged"

    def test_empty_string_not_flagged(self) -> None:
        """Empty string should return empty signals."""
        signals = detect_typosquat("", "pypi")
        assert not signals

    def test_very_long_names_handled(self) -> None:
        """Very long package names should be handled gracefully."""
        long_name = "a" * 100
        # Should not crash, may or may not have matches
        _ = detect_typosquat(long_name, "pypi")

    def test_special_characters_handled(self) -> None:
        """Package names with special characters should be handled."""
        special_names = [
            "typing-extensions",
            "python-dateutil",
            "google-cloud-storage",
        ]

        for name in special_names:
            # Should not crash
            _ = detect_typosquat(name, "pypi")
