# SPEC: S001 - Core Types Tests
# Gate 3: Test Design - W1.1 Implementation Tests
"""
Unit tests for core types module.

SPEC_IDs: S001, S004
TEST_IDs: T001.05, T001.15, T001.16
INVARIANTS: INV001, INV002, INV006, INV007, INV019, INV020
"""

from __future__ import annotations

import pytest

from phantom_guard.core import (
    InvalidPackageNameError,
    InvalidRegistryError,
    PackageMetadata,
    PackageRisk,
    PhantomGuardError,
    Recommendation,
    Signal,
    SignalType,
    ValidationError,
    validate_package_name,
    validate_registry,
)


class TestExceptionHierarchy:
    """Tests for exception hierarchy.

    SPEC: S001
    """

    @pytest.mark.unit
    def test_validation_error_inherits_from_phantom_guard_error(self) -> None:
        """ValidationError is a PhantomGuardError."""
        assert issubclass(ValidationError, PhantomGuardError)

    @pytest.mark.unit
    def test_invalid_package_name_error_inherits_from_validation_error(self) -> None:
        """InvalidPackageNameError is a ValidationError."""
        assert issubclass(InvalidPackageNameError, ValidationError)
        assert issubclass(InvalidPackageNameError, PhantomGuardError)

    @pytest.mark.unit
    def test_invalid_registry_error_inherits_from_validation_error(self) -> None:
        """InvalidRegistryError is a ValidationError."""
        assert issubclass(InvalidRegistryError, ValidationError)
        assert issubclass(InvalidRegistryError, PhantomGuardError)

    @pytest.mark.unit
    def test_can_catch_validation_errors_generically(self) -> None:
        """All validation errors can be caught with ValidationError."""
        with pytest.raises(ValidationError):
            validate_package_name("")

        with pytest.raises(ValidationError):
            validate_registry("unknown")


class TestRecommendationEnum:
    """Tests for Recommendation enum.

    SPEC: S001
    """

    @pytest.mark.unit
    def test_recommendation_has_safe(self) -> None:
        """Recommendation enum has SAFE value."""
        assert Recommendation.SAFE.value == "safe"

    @pytest.mark.unit
    def test_recommendation_has_suspicious(self) -> None:
        """Recommendation enum has SUSPICIOUS value."""
        assert Recommendation.SUSPICIOUS.value == "suspicious"

    @pytest.mark.unit
    def test_recommendation_has_high_risk(self) -> None:
        """Recommendation enum has HIGH_RISK value."""
        assert Recommendation.HIGH_RISK.value == "high_risk"

    @pytest.mark.unit
    def test_recommendation_has_not_found(self) -> None:
        """Recommendation enum has NOT_FOUND value."""
        assert Recommendation.NOT_FOUND.value == "not_found"


class TestSignalType:
    """Tests for SignalType enum.

    SPEC: S004
    """

    @pytest.mark.unit
    def test_signal_type_has_existence_signals(self) -> None:
        """SignalType enum has all existence signals."""
        assert SignalType.NOT_FOUND.value == "not_found"
        assert SignalType.RECENTLY_CREATED.value == "recently_created"
        assert SignalType.LOW_DOWNLOADS.value == "low_downloads"
        assert SignalType.NO_REPOSITORY.value == "no_repository"

    @pytest.mark.unit
    def test_signal_type_has_pattern_signals(self) -> None:
        """SignalType enum has all pattern signals."""
        assert SignalType.HALLUCINATION_PATTERN.value == "hallucination_pattern"
        assert SignalType.TYPOSQUAT.value == "typosquat"

    @pytest.mark.unit
    def test_signal_type_has_positive_signals(self) -> None:
        """SignalType enum has positive signals."""
        assert SignalType.POPULAR_PACKAGE.value == "popular_package"


class TestSignal:
    """Tests for Signal dataclass.

    SPEC: S004
    INVARIANT: INV007
    """

    @pytest.mark.unit
    def test_signal_creation(self) -> None:
        """Signal can be created with valid data."""
        signal = Signal(
            type=SignalType.NOT_FOUND,
            weight=0.5,
            message="Package not found on PyPI",
        )
        assert signal.type == SignalType.NOT_FOUND
        assert signal.weight == 0.5
        assert signal.message == "Package not found on PyPI"
        assert signal.metadata == {}

    @pytest.mark.unit
    def test_signal_with_metadata(self) -> None:
        """Signal can include metadata."""
        signal = Signal(
            type=SignalType.TYPOSQUAT,
            weight=0.8,
            message="Typosquat of 'requests'",
            metadata={"target": "requests", "distance": 1},
        )
        assert signal.metadata["target"] == "requests"
        assert signal.metadata["distance"] == 1

    @pytest.mark.unit
    def test_signal_weight_bounds_positive(self) -> None:
        """INV007: Signal weight cannot exceed 1.0."""
        with pytest.raises(ValueError, match="weight must be in"):
            Signal(type=SignalType.NOT_FOUND, weight=1.5, message="test")

    @pytest.mark.unit
    def test_signal_weight_bounds_negative(self) -> None:
        """INV007: Signal weight cannot be less than -1.0."""
        with pytest.raises(ValueError, match="weight must be in"):
            Signal(type=SignalType.NOT_FOUND, weight=-1.5, message="test")

    @pytest.mark.unit
    def test_signal_allows_negative_weight(self) -> None:
        """Negative weights are valid for positive signals."""
        signal = Signal(
            type=SignalType.POPULAR_PACKAGE,
            weight=-0.3,
            message="Popular package",
        )
        assert signal.weight == -0.3

    @pytest.mark.unit
    def test_signal_is_immutable(self) -> None:
        """Signal is frozen (immutable)."""
        signal = Signal(type=SignalType.NOT_FOUND, weight=0.5, message="test")
        with pytest.raises(AttributeError):
            signal.weight = 0.8  # type: ignore[misc]


class TestPackageRisk:
    """Tests for PackageRisk dataclass.

    SPEC: S001
    INVARIANTS: INV001, INV002, INV006
    """

    @pytest.mark.unit
    def test_package_risk_creation(self) -> None:
        """
        TEST_ID: T001.16
        PackageRisk can be created with valid data.
        """
        risk = PackageRisk(
            name="flask",
            registry="pypi",
            exists=True,
            risk_score=0.1,
            signals=(),
            recommendation=Recommendation.SAFE,
        )
        assert risk.name == "flask"
        assert risk.registry == "pypi"
        assert risk.exists is True
        assert risk.risk_score == 0.1
        assert risk.signals == ()
        assert risk.recommendation == Recommendation.SAFE

    @pytest.mark.unit
    def test_package_risk_with_signals(self) -> None:
        """
        TEST_ID: T001.15
        INV002: Signals must be a tuple.
        """
        signal = Signal(type=SignalType.NOT_FOUND, weight=0.5, message="test")
        risk = PackageRisk(
            name="fake-pkg",
            registry="pypi",
            exists=False,
            risk_score=0.7,
            signals=(signal,),
            recommendation=Recommendation.HIGH_RISK,
        )
        assert len(risk.signals) == 1
        assert risk.signals[0].type == SignalType.NOT_FOUND

    @pytest.mark.unit
    def test_package_risk_score_bounds_upper(self) -> None:
        """INV001: Risk score cannot exceed 1.0."""
        with pytest.raises(ValueError, match="risk_score must be in"):
            PackageRisk(
                name="test",
                registry="pypi",
                exists=True,
                risk_score=1.5,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

    @pytest.mark.unit
    def test_package_risk_score_bounds_lower(self) -> None:
        """INV001: Risk score cannot be less than 0.0."""
        with pytest.raises(ValueError, match="risk_score must be in"):
            PackageRisk(
                name="test",
                registry="pypi",
                exists=True,
                risk_score=-0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

    @pytest.mark.unit
    def test_package_risk_empty_name_rejected(self) -> None:
        """INV019: Package name cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            PackageRisk(
                name="",
                registry="pypi",
                exists=True,
                risk_score=0.0,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

    @pytest.mark.unit
    def test_package_risk_whitespace_name_rejected(self) -> None:
        """INV019: Package name cannot be whitespace only."""
        with pytest.raises(ValueError, match="cannot be empty"):
            PackageRisk(
                name="   ",
                registry="pypi",
                exists=True,
                risk_score=0.0,
                signals=(),
                recommendation=Recommendation.SAFE,
            )

    @pytest.mark.unit
    def test_package_risk_is_immutable(self) -> None:
        """PackageRisk is frozen (immutable)."""
        risk = PackageRisk(
            name="flask",
            registry="pypi",
            exists=True,
            risk_score=0.1,
            signals=(),
            recommendation=Recommendation.SAFE,
        )
        with pytest.raises(AttributeError):
            risk.risk_score = 0.5  # type: ignore[misc]


class TestValidatePackageName:
    """Tests for validate_package_name function.

    SPEC: S001
    INVARIANTS: INV019, INV020
    EDGE_CASES: EC001-EC015
    """

    @pytest.mark.unit
    def test_valid_simple_name(self) -> None:
        """EC007: Valid simple name accepted."""
        result = validate_package_name("flask")
        assert result == "flask"

    @pytest.mark.unit
    def test_valid_hyphenated_name(self) -> None:
        """EC008: Valid hyphenated name accepted."""
        result = validate_package_name("flask-redis")
        assert result == "flask-redis"

    @pytest.mark.unit
    def test_valid_underscored_name(self) -> None:
        """EC009: Valid underscored name accepted."""
        result = validate_package_name("flask_redis")
        assert result == "flask_redis"

    @pytest.mark.unit
    def test_valid_numeric_name(self) -> None:
        """EC010: Valid name with numbers accepted."""
        result = validate_package_name("py3redis")
        assert result == "py3redis"

    @pytest.mark.unit
    def test_case_normalization(self) -> None:
        """EC015: Names are normalized to lowercase."""
        result = validate_package_name("Flask")
        assert result == "flask"

    @pytest.mark.unit
    def test_empty_name_rejected(self) -> None:
        """EC001: Empty name rejected."""
        with pytest.raises(InvalidPackageNameError):
            validate_package_name("")

    @pytest.mark.unit
    def test_whitespace_name_rejected(self) -> None:
        """EC002: Whitespace-only name rejected."""
        with pytest.raises(InvalidPackageNameError):
            validate_package_name("   ")

    @pytest.mark.unit
    def test_oversized_name_rejected(self) -> None:
        """EC003, INV020: Name exceeding 214 chars rejected."""
        long_name = "a" * 215
        with pytest.raises(InvalidPackageNameError, match="exceeds maximum length"):
            validate_package_name(long_name)

    @pytest.mark.unit
    def test_max_length_name_accepted(self) -> None:
        """
        TEST_ID: T001.05
        EC004: Name of exactly 214 chars accepted.
        """
        max_name = "a" * 214
        result = validate_package_name(max_name)
        assert result == max_name

    @pytest.mark.unit
    def test_unicode_name_rejected(self) -> None:
        """EC005: Unicode characters rejected."""
        with pytest.raises(InvalidPackageNameError, match="non-ASCII"):
            validate_package_name("flask-日本語")

    @pytest.mark.unit
    def test_special_characters_rejected(self) -> None:
        """EC006: Special characters rejected."""
        with pytest.raises(InvalidPackageNameError):
            validate_package_name("flask@redis")

    @pytest.mark.unit
    def test_leading_hyphen_rejected(self) -> None:
        """EC011: Leading hyphen rejected."""
        with pytest.raises(InvalidPackageNameError, match="cannot start with"):
            validate_package_name("-flask")

    @pytest.mark.unit
    def test_trailing_hyphen_rejected(self) -> None:
        """EC012: Trailing hyphen rejected."""
        with pytest.raises(InvalidPackageNameError, match="cannot end with"):
            validate_package_name("flask-")

    @pytest.mark.unit
    def test_double_hyphen_rejected(self) -> None:
        """EC013: Double hyphen rejected."""
        with pytest.raises(InvalidPackageNameError, match="consecutive"):
            validate_package_name("flask--redis")


class TestValidateRegistry:
    """Tests for validate_registry function.

    SPEC: S001
    INVARIANT: INV021
    """

    @pytest.mark.unit
    def test_pypi_accepted(self) -> None:
        """PyPI registry is valid."""
        result = validate_registry("pypi")
        assert result == "pypi"

    @pytest.mark.unit
    def test_npm_accepted(self) -> None:
        """npm registry is valid."""
        result = validate_registry("npm")
        assert result == "npm"

    @pytest.mark.unit
    def test_crates_accepted(self) -> None:
        """crates.io registry is valid."""
        result = validate_registry("crates")
        assert result == "crates"

    @pytest.mark.unit
    def test_case_insensitive(self) -> None:
        """Registry names are case-insensitive."""
        assert validate_registry("PYPI") == "pypi"
        assert validate_registry("NPM") == "npm"

    @pytest.mark.unit
    def test_unknown_registry_rejected(self) -> None:
        """Unknown registry raises error."""
        with pytest.raises(InvalidRegistryError, match="Unknown registry"):
            validate_registry("unknown")


class TestPackageMetadata:
    """Tests for PackageMetadata dataclass.

    SPEC: S004
    """

    @pytest.mark.unit
    def test_age_days_with_naive_datetime(self) -> None:
        """age_days handles naive datetime by assuming UTC."""
        from datetime import datetime, timedelta

        # Create a naive datetime (no timezone)
        naive_created = datetime.now() - timedelta(days=10)

        metadata = PackageMetadata(
            name="test-pkg",
            exists=True,
            created_at=naive_created,
        )

        # Should work and return approximately 10 days
        assert metadata.age_days is not None
        assert 9 <= metadata.age_days <= 11

    @pytest.mark.unit
    def test_age_days_with_aware_datetime(self) -> None:
        """age_days works with timezone-aware datetime."""
        from datetime import UTC, datetime, timedelta

        aware_created = datetime.now(tz=UTC) - timedelta(days=5)

        metadata = PackageMetadata(
            name="test-pkg",
            exists=True,
            created_at=aware_created,
        )

        assert metadata.age_days is not None
        assert 4 <= metadata.age_days <= 6


class TestPackageRiskSignalsValidation:
    """Additional tests for PackageRisk signals validation.

    INV: INV002
    """

    @pytest.mark.unit
    def test_signals_none_rejected(self) -> None:
        """INV002: Signals cannot be None."""
        # This is a defensive check for runtime construction bypass
        # PackageRisk uses slots=True, so we use object.__setattr__
        with pytest.raises(ValueError, match="signals cannot be None"):
            risk = object.__new__(PackageRisk)
            object.__setattr__(risk, "name", "test")
            object.__setattr__(risk, "registry", "pypi")
            object.__setattr__(risk, "exists", True)
            object.__setattr__(risk, "risk_score", 0.5)
            object.__setattr__(risk, "signals", None)  # Deliberately set to None
            object.__setattr__(risk, "recommendation", Recommendation.SAFE)
            object.__setattr__(risk, "latency_ms", 0.0)
            risk.__post_init__()
