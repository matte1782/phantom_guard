"""
Unit tests for the popular packages data module.

IMPLEMENTS: S006
TESTS: Data module integrity and false positive prevention
"""

from __future__ import annotations

import pytest

from phantom_guard.data import (
    CRATES_POPULAR,
    NPM_POPULAR,
    POPULAR_BY_REGISTRY,
    PYPI_POPULAR,
    get_popular_packages,
    is_popular,
)


class TestDataModuleStructure:
    """Tests for data module structure and exports."""

    def test_pypi_popular_is_frozenset(self) -> None:
        """PYPI_POPULAR should be a frozenset."""
        assert isinstance(PYPI_POPULAR, frozenset)

    def test_npm_popular_is_frozenset(self) -> None:
        """NPM_POPULAR should be a frozenset."""
        assert isinstance(NPM_POPULAR, frozenset)

    def test_crates_popular_is_frozenset(self) -> None:
        """CRATES_POPULAR should be a frozenset."""
        assert isinstance(CRATES_POPULAR, frozenset)

    def test_popular_by_registry_has_all_registries(self) -> None:
        """POPULAR_BY_REGISTRY should have all three registries."""
        assert "pypi" in POPULAR_BY_REGISTRY
        assert "npm" in POPULAR_BY_REGISTRY
        assert "crates" in POPULAR_BY_REGISTRY

    def test_popular_by_registry_values_match(self) -> None:
        """POPULAR_BY_REGISTRY values should match individual constants."""
        assert POPULAR_BY_REGISTRY["pypi"] is PYPI_POPULAR
        assert POPULAR_BY_REGISTRY["npm"] is NPM_POPULAR
        assert POPULAR_BY_REGISTRY["crates"] is CRATES_POPULAR


class TestPackageCounts:
    """Tests for package count targets (3000+ total)."""

    def test_pypi_has_minimum_packages(self) -> None:
        """PyPI should have at least 500 packages."""
        assert len(PYPI_POPULAR) >= 500, f"Expected >=500, got {len(PYPI_POPULAR)}"

    def test_npm_has_minimum_packages(self) -> None:
        """npm should have at least 500 packages."""
        assert len(NPM_POPULAR) >= 500, f"Expected >=500, got {len(NPM_POPULAR)}"

    def test_crates_has_minimum_packages(self) -> None:
        """crates.io should have at least 500 packages."""
        assert len(CRATES_POPULAR) >= 500, f"Expected >=500, got {len(CRATES_POPULAR)}"

    def test_total_packages_exceeds_3000(self) -> None:
        """Total packages across all registries should exceed 3000."""
        total = len(PYPI_POPULAR) + len(NPM_POPULAR) + len(CRATES_POPULAR)
        assert total >= 3000, f"Expected >=3000 total, got {total}"


class TestKnownPopularPackages:
    """Tests that known popular packages are included."""

    @pytest.mark.parametrize(
        "package",
        [
            "requests",
            "numpy",
            "pandas",
            "flask",
            "django",
            "pytest",
            "boto3",
            "pyyaml",
            "cryptography",
            "urllib3",
        ],
    )
    def test_pypi_contains_known_packages(self, package: str) -> None:
        """PyPI list should contain well-known packages."""
        assert package in PYPI_POPULAR, f"Missing popular PyPI package: {package}"

    @pytest.mark.parametrize(
        "package",
        [
            "react",
            "lodash",
            "axios",
            "express",
            "webpack",
            "eslint",
            "vue",
            "jquery",
        ],
    )
    def test_npm_contains_known_packages(self, package: str) -> None:
        """npm list should contain well-known packages."""
        assert package in NPM_POPULAR, f"Missing popular npm package: {package}"

    @pytest.mark.parametrize(
        "package",
        [
            "serde",
            "tokio",
            "reqwest",
            "clap",
            "rand",
            "log",
            "regex",
            "chrono",
        ],
    )
    def test_crates_contains_known_packages(self, package: str) -> None:
        """crates.io list should contain well-known packages."""
        assert package in CRATES_POPULAR, f"Missing popular crate: {package}"


class TestIsPopularFunction:
    """Tests for the is_popular() function."""

    def test_is_popular_returns_true_for_popular_pypi(self) -> None:
        """is_popular() should return True for popular PyPI packages."""
        assert is_popular("requests", "pypi") is True
        assert is_popular("numpy", "pypi") is True
        assert is_popular("flask", "pypi") is True

    def test_is_popular_returns_false_for_unknown(self) -> None:
        """is_popular() should return False for unknown packages."""
        assert is_popular("definitely-not-a-real-package-xyz", "pypi") is False
        assert is_popular("fake-npm-pkg-12345", "npm") is False

    def test_is_popular_case_insensitive(self) -> None:
        """is_popular() should be case-insensitive."""
        assert is_popular("REQUESTS", "pypi") is True
        assert is_popular("Requests", "pypi") is True
        assert is_popular("ReQuEsTs", "pypi") is True

    def test_is_popular_handles_npm_registry(self) -> None:
        """is_popular() should work for npm registry."""
        assert is_popular("react", "npm") is True
        assert is_popular("lodash", "npm") is True

    def test_is_popular_handles_crates_registry(self) -> None:
        """is_popular() should work for crates registry."""
        assert is_popular("serde", "crates") is True
        assert is_popular("tokio", "crates") is True

    def test_is_popular_unknown_registry_uses_pypi(self) -> None:
        """is_popular() with unknown registry should use PyPI as fallback."""
        assert is_popular("requests", "unknown") is True


class TestGetPopularPackagesFunction:
    """Tests for the get_popular_packages() function."""

    def test_get_popular_packages_pypi(self) -> None:
        """get_popular_packages() should return PyPI packages."""
        packages = get_popular_packages("pypi")
        assert isinstance(packages, frozenset)
        assert len(packages) >= 500

    def test_get_popular_packages_npm(self) -> None:
        """get_popular_packages() should return npm packages."""
        packages = get_popular_packages("npm")
        assert isinstance(packages, frozenset)
        assert len(packages) >= 500

    def test_get_popular_packages_crates(self) -> None:
        """get_popular_packages() should return crates packages."""
        packages = get_popular_packages("crates")
        assert isinstance(packages, frozenset)
        assert len(packages) >= 500

    def test_get_popular_packages_case_insensitive(self) -> None:
        """get_popular_packages() should be case-insensitive on registry."""
        assert get_popular_packages("PYPI") == get_popular_packages("pypi")
        assert get_popular_packages("NPM") == get_popular_packages("npm")
        assert get_popular_packages("Crates") == get_popular_packages("crates")


class TestPackageNameFormats:
    """Tests for package name normalization in data."""

    def test_pypi_packages_are_lowercase(self) -> None:
        """All PyPI package names should be lowercase."""
        for pkg in PYPI_POPULAR:
            assert pkg == pkg.lower(), f"Package {pkg} is not lowercase"

    def test_npm_packages_are_lowercase(self) -> None:
        """All npm package names should be lowercase."""
        for pkg in NPM_POPULAR:
            assert pkg == pkg.lower(), f"Package {pkg} is not lowercase"

    def test_crates_packages_are_lowercase(self) -> None:
        """All crates package names should be lowercase."""
        for pkg in CRATES_POPULAR:
            assert pkg == pkg.lower(), f"Package {pkg} is not lowercase"

    def test_no_empty_package_names(self) -> None:
        """No registry should contain empty package names."""
        assert "" not in PYPI_POPULAR
        assert "" not in NPM_POPULAR
        assert "" not in CRATES_POPULAR


class TestBackwardsCompatibility:
    """Tests for backwards compatibility with typosquat module."""

    def test_typosquat_get_popular_packages_works(self) -> None:
        """typosquat.get_popular_packages() should use new data module."""
        from phantom_guard.core.typosquat import get_popular_packages as typo_get

        packages = typo_get("pypi")
        assert len(packages) >= 500

    def test_typosquat_is_popular_package_works(self) -> None:
        """typosquat.is_popular_package() should use new data module."""
        from phantom_guard.core.typosquat import is_popular_package

        assert is_popular_package("requests", "pypi") is True
        assert is_popular_package("fake-pkg", "pypi") is False

    def test_core_popular_packages_export(self) -> None:
        """phantom_guard.core should export POPULAR_PACKAGES."""
        from phantom_guard.core import POPULAR_PACKAGES

        assert "pypi" in POPULAR_PACKAGES
        assert "npm" in POPULAR_PACKAGES
        assert "crates" in POPULAR_PACKAGES
