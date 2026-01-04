"""
SPEC: S059 - Pattern Validation
TEST_IDs: T059.01-T059.06
INVARIANTS: INV059, INV059a
EDGE_CASES: EC483-EC488

Tests for pattern validation.
"""

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from phantom_guard.patterns.validate import validate_pattern


class TestPatternValidation:
    """Unit tests for pattern validation (S059)."""

    # =========================================================================
    # T059.01: Invalid confidence rejected
    # =========================================================================
    def test_invalid_confidence_rejected(self):
        """
        SPEC: S059
        TEST_ID: T059.01
        INV_ID: INV059
        EC_ID: EC484

        Given: Pattern with confidence = 1.5 (out of bounds)
        When: Validating pattern
        Then: Rejected with error
        """
        # Arrange
        pattern = {
            "id": "test-pattern",
            "type": "suffix",
            "base": "flask",
            "suffixes": ["-gpt"],
            "confidence": 1.5,  # Invalid: > 1.0
        }

        # Act
        result = validate_pattern(pattern)

        # Assert
        assert result.success is False
        assert "confidence" in result.errors[0].lower()

    # =========================================================================
    # T059.02: Invalid type rejected
    # =========================================================================
    def test_invalid_type_rejected(self):
        """
        SPEC: S059
        TEST_ID: T059.02
        INV_ID: INV059
        EC_ID: EC485

        Given: Pattern with type = "unknown"
        When: Validating pattern
        Then: Rejected with error
        """
        # Arrange
        pattern = {
            "id": "test-pattern",
            "type": "unknown",  # Invalid type
            "confidence": 0.8,
        }

        # Act
        result = validate_pattern(pattern)

        # Assert
        assert result.success is False
        assert "type" in result.errors[0].lower()

    # =========================================================================
    # T059.03: FP check catches issues
    # =========================================================================
    def test_fp_check_catches_popular_package(self):
        """
        SPEC: S059
        TEST_ID: T059.03
        INV_ID: INV059a
        EC_ID: EC488

        Given: Pattern that matches "requests" (popular package)
        When: Validating pattern
        Then: Rejected (would cause false positive)
        """
        # Arrange
        pattern = {
            "id": "too-broad",
            "type": "regex",
            "pattern": r"^req.*",  # Would match "requests"
            "confidence": 0.9,
        }

        # Act
        result = validate_pattern(pattern)

        # Assert
        assert result.success is False
        assert "false positive" in result.errors[0].lower()

    # =========================================================================
    # T059.04: Invalid regex rejected
    # =========================================================================
    def test_invalid_regex_rejected(self):
        """
        SPEC: S059
        TEST_ID: T059.04
        EC_ID: EC487

        Given: Pattern with invalid regex "[invalid"
        When: Validating pattern
        Then: Rejected with regex error
        """
        # Arrange
        pattern = {
            "id": "bad-regex",
            "type": "regex",
            "pattern": "[invalid",  # Invalid regex
            "confidence": 0.8,
        }

        # Act
        result = validate_pattern(pattern)

        # Assert
        assert result.success is False
        assert "regex" in result.errors[0].lower()

    # =========================================================================
    # T059.05: Random pattern input fuzz
    # =========================================================================
    @pytest.mark.fuzz
    @given(
        id_val=st.text(max_size=100),
        type_val=st.text(max_size=50),
        confidence_val=st.one_of(
            st.floats(allow_nan=True, allow_infinity=True),
            st.text(max_size=20),
            st.none(),
            st.integers(),
        ),
        pattern_val=st.text(max_size=100),
    )
    def test_random_pattern_input_fuzz(
        self, id_val: str, type_val: str, confidence_val: Any, pattern_val: str
    ) -> None:
        """
        SPEC: S059
        TEST_ID: T059.05

        Fuzz: Random pattern inputs should not crash validator.
        """
        # Arrange
        pattern: dict[str, Any] = {
            "id": id_val,
            "type": type_val,
            "confidence": confidence_val,
            "pattern": pattern_val,
        }

        # Act - should not crash
        result = validate_pattern(pattern)

        # Assert - result should always be valid structure
        assert isinstance(result.success, bool)
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)

    # =========================================================================
    # T059.06: Confidence bounds property
    # =========================================================================
    @pytest.mark.property
    @given(
        confidence=st.floats(
            min_value=-1000.0,
            max_value=1000.0,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    def test_confidence_bounds_property(self, confidence: float) -> None:
        """
        SPEC: S059
        TEST_ID: T059.06
        INV_ID: INV059

        Property: Confidence outside [0.0, 1.0] is always rejected.
        Confidence inside [0.0, 1.0] may pass (if other fields valid).
        """
        # Arrange
        pattern: dict[str, Any] = {
            "id": "test-pattern",
            "type": "suffix",
            "confidence": confidence,
        }

        # Act
        result = validate_pattern(pattern)

        # Assert - confidence out of bounds MUST fail
        if confidence < 0.0 or confidence > 1.0:
            assert result.success is False
            # Should have at least one error mentioning confidence
            confidence_errors = [e for e in result.errors if "confidence" in e.lower()]
            assert len(confidence_errors) > 0, f"Expected confidence error for {confidence}"


class TestPatternValidationEdgeCases:
    """Edge case tests for pattern validation (EC483-EC488)."""

    @pytest.mark.skip(reason="Stub - implement with S059")
    def test_duplicate_pattern_id_rejected(self):
        """
        EC_ID: EC483
        Given: Pattern with duplicate ID
        When: Adding to pattern database
        Then: Rejected with error
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S059")
    def test_valid_regex_compiled(self):
        """
        EC_ID: EC486
        Given: Pattern with valid regex
        When: Validating pattern
        Then: Regex compiled successfully and used
        """
        pass
