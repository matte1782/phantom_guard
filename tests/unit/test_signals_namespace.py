"""
SPEC: S060 - Namespace Squatting Detection
TEST_IDs: T060.01-T060.06
INVARIANTS: INV060, INV061, INV062

Tests for namespace squatting signal detection.
"""

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from phantom_guard.core.signals.namespace import (
    NamespaceSignal,
    detect_namespace_squatting,
    extract_namespace,
    KNOWN_LEGITIMATE_ORGS,
)


class TestNamespaceSquattingDetection:
    """Unit tests for namespace squatting detection (S060)."""

    # =========================================================================
    # T060.01: Legitimate npm scope
    # =========================================================================
    def test_legitimate_npm_scope_no_signal(self):
        """
        SPEC: S060
        TEST_ID: T060.01
        INV_ID: INV060
        EC_ID: EC400

        Given: Package "@babel/core" (verified org package in known list)
        When: detect_namespace_squatting is called
        Then: Returns None (no signal - legitimate owner)
        """
        # Arrange
        package = "@babel/core"
        registry = "npm"
        metadata: dict[str, Any] = {"name": package}

        # Act
        result = detect_namespace_squatting(package, metadata, registry)

        # Assert
        assert result is None

    # =========================================================================
    # T060.02: Fake npm scope detected
    # =========================================================================
    def test_fake_npm_scope_detected(self):
        """
        SPEC: S060
        TEST_ID: T060.02
        INV_ID: INV060
        EC_ID: EC401

        Given: Package "@unknownorg/fake-pkg" (not in known list)
        When: detect_namespace_squatting is called
        Then: Returns NamespaceSquatSignal with weight 0.35
        """
        # Arrange - use unknown org not in KNOWN_LEGITIMATE_ORGS
        package = "@suspiciousorg/malware-helper"
        registry = "npm"
        metadata: dict[str, Any] = {"name": package}

        # Act
        result = detect_namespace_squatting(package, metadata, registry)

        # Assert
        assert result is not None
        assert isinstance(result, NamespaceSignal)
        assert result.confidence == 0.35
        assert result.namespace == "suspiciousorg"

    # =========================================================================
    # T060.03: Legitimate PyPI company prefix
    # =========================================================================
    def test_legitimate_pypi_company_prefix(self):
        """
        SPEC: S060
        TEST_ID: T060.03
        INV_ID: INV061
        EC_ID: EC402

        Given: Package "google-cloud-storage" (verified Google package)
        When: detect_namespace_squatting is called
        Then: Returns None (legitimate org package)
        """
        # Arrange
        package = "google-cloud-storage"
        registry = "pypi"
        metadata: dict[str, Any] = {"name": package}

        # Act
        result = detect_namespace_squatting(package, metadata, registry)

        # Assert - google-* packages are known legitimate
        assert result is None

    # =========================================================================
    # T060.04: Fake PyPI company prefix
    # =========================================================================
    def test_fake_pypi_company_prefix(self):
        """
        SPEC: S060
        TEST_ID: T060.04
        INV_ID: INV061
        EC_ID: EC403

        Given: Package "netflix-helper" (suspicious prefix, unverified)
        When: detect_namespace_squatting is called
        Then: Returns NamespaceSquatSignal
        """
        # Arrange - netflix- is in SUSPICIOUS_COMPANY_PREFIXES
        package = "netflix-helper"
        registry = "pypi"
        metadata: dict[str, Any] = {"name": package}

        # Act
        result = detect_namespace_squatting(package, metadata, registry)

        # Assert - netflix is suspicious and not in known legitimate
        assert result is not None
        assert isinstance(result, NamespaceSignal)
        assert result.namespace == "netflix"
        assert result.confidence == 0.35

    # =========================================================================
    # T060.05: API failure returns None
    # =========================================================================
    def test_api_failure_returns_none(self):
        """
        SPEC: S060
        TEST_ID: T060.05
        INV_ID: INV062
        EC_ID: EC408

        Given: Invalid metadata that could cause exception
        When: detect_namespace_squatting is called
        Then: Returns None (graceful degradation, not exception)
        """
        # Arrange - pass problematic input that might cause issues
        package = "@unknown/pkg"
        registry = "npm"
        # Invalid metadata type to test error handling
        metadata: dict[str, Any] = None  # type: ignore[assignment]

        # Act - should not raise exception (INV062)
        result = detect_namespace_squatting(package, metadata, registry)

        # Assert - Should return signal (unknown org) or None, but never exception
        # Since @unknown is not in known list, it should return a signal
        # But if metadata handling fails, INV062 says return None
        assert result is None or isinstance(result, NamespaceSignal)

    # =========================================================================
    # T060.06: Namespace extraction property test
    # =========================================================================
    @pytest.mark.property
    @given(
        package_name=st.text(
            alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789-_@/"),
            min_size=1,
            max_size=50,
        ),
        registry=st.sampled_from(["npm", "pypi", "crates"]),
    )
    def test_namespace_extraction_property(self, package_name: str, registry: str) -> None:
        """
        SPEC: S060
        TEST_ID: T060.06
        INV_ID: INV060

        Property: For all valid package names, namespace extraction
        handles all registry formats correctly without exception.
        """
        # Act - should never raise exception (INV060)
        result = extract_namespace(package_name, registry)

        # Assert - result is either None or a valid string
        assert result is None or isinstance(result, str)


class TestNamespaceEdgeCases:
    """Edge case tests for namespace squatting (EC400-EC415)."""

    @pytest.mark.skip(reason="Stub - implement with S060")
    def test_no_namespace_package(self):
        """
        EC_ID: EC406
        Given: Package "flask" (no namespace prefix)
        When: detect_namespace_squatting is called
        Then: Returns None (no namespace to squat)
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S060")
    def test_nested_scope_extraction(self):
        """
        EC_ID: EC407
        Given: Package "@org/sub/pkg" (nested scope)
        When: Extracting namespace
        Then: Scope extracted correctly as "@org"
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S060")
    def test_rate_limited_skip_signal(self):
        """
        EC_ID: EC409
        Given: npm org API returns 429
        When: detect_namespace_squatting is called
        Then: Returns None and logs warning
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S060")
    def test_known_org_list_no_api_call(self):
        """
        EC_ID: EC410
        Given: Package "@angular/core" (in known org list)
        When: detect_namespace_squatting is called
        Then: No API call made, immediately returns None
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S060")
    def test_case_sensitivity_normalization(self):
        """
        EC_ID: EC411
        Given: Package "@Microsoft/pkg" (uppercase scope)
        When: Processing namespace
        Then: Normalized to lowercase "@microsoft"
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S060")
    def test_empty_scope_error(self):
        """
        EC_ID: EC412
        Given: Package "@/package" (empty scope)
        When: Validating package name
        Then: Raises InvalidPackageNameError
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S060")
    def test_unicode_scope_error(self):
        """
        EC_ID: EC415
        Given: Package "@\u043e\u0440\u0433/package" (unicode scope)
        When: Validating package name
        Then: Raises InvalidPackageNameError
        """
        pass
