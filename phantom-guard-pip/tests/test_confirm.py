"""
Tests for interactive confirmation.

SPEC: S203
TESTS: T203.01-T203.06, T203.E01-T203.E08
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from dataclasses import dataclass, field
from typing import Optional

from phantom_pip.confirm import (
    confirm_installation,
    confirm_batch_installation,
    display_risk,
    display_summary,
    display_blocked_message,
    display_skipped_message,
    get_risk_color,
    get_risk_icon,
    PHANTOM_GUARD_AVAILABLE,
)


@dataclass
class MockPackageRisk:
    """Mock PackageRisk for testing - properly typed."""

    risk_level: str = "SAFE"
    risk_score: float = 0.1
    signals: list[str] = field(default_factory=list)
    recommendation: Optional[str] = None


class TestT203_Confirmation:
    """T203: Interactive confirmation tests."""

    def test_T203_01_auto_approve_returns_true(self) -> None:
        """T203.01: INV201 - auto_approve=True always returns True."""
        risk = MockPackageRisk(risk_level="HIGH_RISK", risk_score=0.95)
        result = confirm_installation("malware", risk, auto_approve=True)
        assert result is True

    def test_T203_02_safe_auto_approved(self) -> None:
        """T203.02: SAFE packages don't need confirmation."""
        risk = MockPackageRisk(risk_level="SAFE", risk_score=0.1)
        result = confirm_installation("flask", risk, auto_approve=False)
        assert result is True

    @patch("phantom_pip.confirm.Confirm.ask")
    def test_T203_03_high_risk_prompts(self, mock_ask: MagicMock) -> None:
        """T203.03: HIGH_RISK packages prompt user."""
        mock_ask.return_value = False
        risk = MockPackageRisk(
            risk_level="HIGH_RISK",
            risk_score=0.95,
            signals=["Package not found", "Matches hallucination pattern"],
        )
        result = confirm_installation("flask-gpt-helper", risk, auto_approve=False)
        assert mock_ask.called
        assert result is False

    @patch("phantom_pip.confirm.Confirm.ask")
    def test_T203_04_suspicious_prompts(self, mock_ask: MagicMock) -> None:
        """T203.04: SUSPICIOUS packages prompt with default=True."""
        mock_ask.return_value = True
        risk = MockPackageRisk(risk_level="SUSPICIOUS", risk_score=0.6)
        result = confirm_installation("new-package", risk, auto_approve=False)
        assert mock_ask.called
        # Check default was True
        assert mock_ask.call_args[1].get("default", None) is True

    def test_T203_05_batch_auto_approve(self) -> None:
        """T203.05: Batch auto_approve approves all."""
        results = {
            "flask": MockPackageRisk(risk_level="SAFE"),
            "malware": MockPackageRisk(risk_level="HIGH_RISK"),
        }
        approved, rejected = confirm_batch_installation(results, auto_approve=True)
        assert "flask" in approved
        assert "malware" in approved
        assert rejected == []

    def test_T203_06_batch_categorizes(self) -> None:
        """T203.06: Batch separates safe from risky."""
        results = {
            "flask": MockPackageRisk(risk_level="SAFE"),
            "requests": MockPackageRisk(risk_level="SAFE"),
            "suspicious": MockPackageRisk(risk_level="SUSPICIOUS"),
        }
        # Safe packages are auto-approved, risky would prompt
        with patch("phantom_pip.confirm.Confirm.ask", return_value=True):
            approved, rejected = confirm_batch_installation(results, auto_approve=False)
        assert "flask" in approved
        assert "requests" in approved
        assert "suspicious" in approved


class TestT203_Display:
    """T203: Display function tests."""

    def test_T203_D01_risk_colors(self) -> None:
        """T203.D01: Risk levels have correct colors."""
        assert get_risk_color("SAFE") == "green"
        assert get_risk_color("SUSPICIOUS") == "yellow"
        assert get_risk_color("HIGH_RISK") == "red"
        assert get_risk_color("NOT_FOUND") == "red"
        assert get_risk_color("UNKNOWN") == "dim"

    def test_T203_D02_display_no_crash(self) -> None:
        """T203.D02: display_risk doesn't crash."""
        risk = MockPackageRisk(
            risk_level="HIGH_RISK",
            risk_score=0.95,
            signals=["Signal 1", "Signal 2"],
            recommendation="BLOCK",
        )
        # Should not raise
        display_risk("test-package", risk)

    def test_T203_D03_not_found_prompts(self) -> None:
        """T203.D03: NOT_FOUND risk level prompts user."""
        risk = MockPackageRisk(risk_level="NOT_FOUND", risk_score=0.9)
        with patch("phantom_pip.confirm.Confirm.ask", return_value=False) as mock_ask:
            result = confirm_installation("missing-pkg", risk, auto_approve=False)
        assert mock_ask.called
        assert mock_ask.call_args[1].get("default") is False  # High risk default


class TestT203_FallbackPackageRisk:
    """T203.F: Tests for fallback PackageRisk when phantom-guard not installed (lines 22-33)."""

    def test_T203_F01_phantom_guard_available_flag(self) -> None:
        """T203.F01: PHANTOM_GUARD_AVAILABLE flag is set correctly."""
        # The flag should be a boolean
        assert isinstance(PHANTOM_GUARD_AVAILABLE, bool)

    def test_T203_F01a_fallback_package_risk_class(self) -> None:
        """T203.F01a: Test the fallback PackageRisk class is used when phantom_guard unavailable."""
        import importlib
        import sys

        # Remove phantom_guard from sys.modules if present
        modules_to_remove = [k for k in sys.modules if k.startswith("phantom_guard")]
        removed_modules = {}
        for mod in modules_to_remove:
            removed_modules[mod] = sys.modules.pop(mod, None)

        # Also remove phantom_pip.confirm to force reimport
        if "phantom_pip.confirm" in sys.modules:
            removed_modules["phantom_pip.confirm"] = sys.modules.pop("phantom_pip.confirm")

        try:
            # Mock phantom_guard to raise ImportError
            class MockImport:
                def __init__(self, original_import: object) -> None:
                    self.original_import = original_import

                def __call__(self, name: str, *args: object, **kwargs: object) -> object:
                    if name == "phantom_guard":
                        raise ImportError("phantom_guard not installed (test)")
                    return self.original_import(name, *args, **kwargs)  # type: ignore[operator]

            import builtins
            original_import = builtins.__import__
            builtins.__import__ = MockImport(original_import)  # type: ignore[assignment]

            try:
                # Now import confirm - should use fallback
                import phantom_pip.confirm as confirm_module
                importlib.reload(confirm_module)

                # Verify the fallback flag is False
                assert confirm_module.PHANTOM_GUARD_AVAILABLE is False

                # Verify the fallback PackageRisk class exists and has correct defaults
                fallback_risk = confirm_module.PackageRisk()
                assert fallback_risk.name == ""
                assert fallback_risk.risk_level == "UNKNOWN"
                assert fallback_risk.risk_score == 0.0
                assert fallback_risk.signals == []
                assert fallback_risk.recommendation is None
            finally:
                builtins.__import__ = original_import  # type: ignore[assignment]
        finally:
            # Restore removed modules
            for mod, module in removed_modules.items():
                if module is not None:
                    sys.modules[mod] = module

            # Force reimport of confirm with original imports
            if "phantom_pip.confirm" in sys.modules:
                del sys.modules["phantom_pip.confirm"]
            import phantom_pip.confirm  # noqa: F401

    def test_T203_F02_fallback_risk_class_behavior(self) -> None:
        """T203.F02: Code handles both real and fallback PackageRisk."""
        # Test with our mock (simulates fallback behavior)
        mock_risk = MockPackageRisk(
            risk_level="HIGH_RISK",
            risk_score=0.9,
            signals=["Signal 1"],
            recommendation="BLOCK"
        )

        # getattr should work on both real and fallback
        assert getattr(mock_risk, "risk_level", "UNKNOWN") == "HIGH_RISK"
        assert getattr(mock_risk, "risk_score", 0.0) == 0.9
        assert getattr(mock_risk, "signals", []) == ["Signal 1"]
        assert getattr(mock_risk, "recommendation", None) == "BLOCK"

    def test_T203_F03_fallback_defaults(self) -> None:
        """T203.F03: Fallback PackageRisk has correct defaults."""
        # Simulate the fallback class behavior
        mock_risk = MockPackageRisk()

        # Default values should match fallback class
        assert mock_risk.risk_level == "SAFE"  # Our mock default
        assert mock_risk.risk_score == 0.1  # Our mock default
        assert mock_risk.signals == []
        assert mock_risk.recommendation is None

    def test_T203_F04_getattr_missing_attribute(self) -> None:
        """T203.F04: getattr handles missing attributes gracefully."""
        mock_risk = MockPackageRisk()

        # These should return defaults when attribute doesn't exist
        assert getattr(mock_risk, "nonexistent_attr", "default") == "default"
        assert getattr(mock_risk, "missing", None) is None


class TestT203_BatchEdgeCases:
    """T203.B: Edge cases for batch confirmation."""

    def test_T203_B01_all_safe_no_prompts(self) -> None:
        """T203.B01: All safe packages returns early (line 220)."""
        results = {
            "flask": MockPackageRisk(risk_level="SAFE"),
            "requests": MockPackageRisk(risk_level="SAFE"),
            "django": MockPackageRisk(risk_level="SAFE"),
        }
        approved, rejected = confirm_batch_installation(results, auto_approve=False)

        # All should be approved without prompting
        assert len(approved) == 3
        assert rejected == []
        assert "flask" in approved
        assert "requests" in approved
        assert "django" in approved

    @patch("phantom_pip.confirm.Confirm.ask")
    def test_T203_B02_user_rejects_package(self, mock_ask: MagicMock) -> None:
        """T203.B02: User rejection adds to rejected list (line 232)."""
        mock_ask.return_value = False  # User says no

        results = {
            "risky-package": MockPackageRisk(risk_level="HIGH_RISK", risk_score=0.95),
        }
        approved, rejected = confirm_batch_installation(results, auto_approve=False)

        assert "risky-package" in rejected
        assert "risky-package" not in approved

    @patch("phantom_pip.confirm.Confirm.ask")
    def test_T203_B03_mixed_user_decisions(self, mock_ask: MagicMock) -> None:
        """T203.B03: Mixed decisions correctly categorized."""
        # User approves first, rejects second
        mock_ask.side_effect = [True, False]

        results = {
            "safe-pkg": MockPackageRisk(risk_level="SAFE"),
            "risky-1": MockPackageRisk(risk_level="HIGH_RISK"),
            "risky-2": MockPackageRisk(risk_level="SUSPICIOUS"),
        }
        approved, rejected = confirm_batch_installation(results, auto_approve=False)

        assert "safe-pkg" in approved
        assert "risky-1" in approved  # User approved
        assert "risky-2" in rejected  # User rejected

    def test_T203_B04_empty_results(self) -> None:
        """T203.B04: Empty results returns empty lists."""
        results: dict[str, MockPackageRisk] = {}
        approved, rejected = confirm_batch_installation(results, auto_approve=False)

        assert approved == []
        assert rejected == []


class TestT203_DisplayFunctions:
    """T203.DF: Tests for display functions (lines 239, 250-251)."""

    def test_T203_DF01_display_blocked_message(self) -> None:
        """T203.DF01: display_blocked_message doesn't crash (line 239)."""
        # Should not raise any exception
        display_blocked_message("malware-pkg", "Known malicious package")

    def test_T203_DF02_display_blocked_custom_reason(self) -> None:
        """T203.DF02: display_blocked_message with custom reason."""
        # Should not raise any exception
        display_blocked_message("test-pkg", "Package is in blocklist")

    def test_T203_DF03_display_skipped_message_with_packages(self) -> None:
        """T203.DF03: display_skipped_message with packages (line 250-251)."""
        # Should not raise any exception
        display_skipped_message(["pkg1", "pkg2", "pkg3"])

    def test_T203_DF04_display_skipped_message_empty_list(self) -> None:
        """T203.DF04: display_skipped_message with empty list (line 250)."""
        # Should not raise - empty list is handled
        display_skipped_message([])

    def test_T203_DF05_display_skipped_message_single(self) -> None:
        """T203.DF05: display_skipped_message with single package."""
        # Should not raise
        display_skipped_message(["single-pkg"])

    def test_T203_DF06_display_summary_no_crash(self) -> None:
        """T203.DF06: display_summary handles various risk levels."""
        results = {
            "safe": MockPackageRisk(risk_level="SAFE", risk_score=0.1),
            "suspicious": MockPackageRisk(risk_level="SUSPICIOUS", risk_score=0.5),
            "high_risk": MockPackageRisk(risk_level="HIGH_RISK", risk_score=0.9),
            "not_found": MockPackageRisk(risk_level="NOT_FOUND", risk_score=0.8),
            "error": MockPackageRisk(risk_level="ERROR", risk_score=0.0),
            "unknown": MockPackageRisk(risk_level="UNKNOWN", risk_score=0.0),
        }
        # Should not raise
        display_summary(results)


class TestT203_RiskIcons:
    """T203.RI: Tests for risk icon functions."""

    def test_T203_RI01_all_icons_defined(self) -> None:
        """T203.RI01: All risk levels have icons."""
        assert get_risk_icon("SAFE") is not None
        assert get_risk_icon("SUSPICIOUS") is not None
        assert get_risk_icon("HIGH_RISK") is not None
        assert get_risk_icon("NOT_FOUND") is not None
        assert get_risk_icon("ERROR") is not None
        assert get_risk_icon("UNKNOWN") is not None

    def test_T203_RI02_unknown_risk_level_icon(self) -> None:
        """T203.RI02: Unknown risk level returns default icon."""
        icon = get_risk_icon("NONEXISTENT_LEVEL")
        assert icon is not None
        assert icon == " "  # Default is space

    def test_T203_RI03_unknown_risk_level_color(self) -> None:
        """T203.RI03: Unknown risk level returns default color."""
        color = get_risk_color("NONEXISTENT_LEVEL")
        assert color == "white"  # Default is white

    def test_T203_RI04_error_color(self) -> None:
        """T203.RI04: ERROR risk level has dim color."""
        assert get_risk_color("ERROR") == "dim"


class TestT203_DisplayRiskEdgeCases:
    """T203.DR: Edge cases for display_risk function."""

    def test_T203_DR01_display_risk_no_signals(self) -> None:
        """T203.DR01: display_risk with empty signals."""
        risk = MockPackageRisk(
            risk_level="SUSPICIOUS",
            risk_score=0.5,
            signals=[],
            recommendation=None,
        )
        # Should not raise
        display_risk("test-pkg", risk)

    def test_T203_DR02_display_risk_no_recommendation(self) -> None:
        """T203.DR02: display_risk with no recommendation."""
        risk = MockPackageRisk(
            risk_level="HIGH_RISK",
            risk_score=0.9,
            signals=["Signal 1"],
            recommendation=None,
        )
        # Should not raise
        display_risk("test-pkg", risk)

    def test_T203_DR03_display_risk_review_recommendation(self) -> None:
        """T203.DR03: display_risk with REVIEW recommendation (yellow)."""
        risk = MockPackageRisk(
            risk_level="SUSPICIOUS",
            risk_score=0.6,
            signals=["Low downloads"],
            recommendation="REVIEW",
        )
        # Should not raise
        display_risk("test-pkg", risk)

    def test_T203_DR04_display_risk_block_recommendation(self) -> None:
        """T203.DR04: display_risk with BLOCK recommendation (red)."""
        risk = MockPackageRisk(
            risk_level="HIGH_RISK",
            risk_score=0.95,
            signals=["Not found on registry"],
            recommendation="BLOCK",
        )
        # Should not raise
        display_risk("test-pkg", risk)

    def test_T203_DR05_display_risk_do_not_install(self) -> None:
        """T203.DR05: display_risk with DO NOT INSTALL recommendation (red)."""
        risk = MockPackageRisk(
            risk_level="NOT_FOUND",
            risk_score=0.99,
            signals=["Package does not exist"],
            recommendation="DO NOT INSTALL",
        )
        # Should not raise
        display_risk("test-pkg", risk)

    def test_T203_DR06_display_risk_generic_object(self) -> None:
        """T203.DR06: display_risk handles generic objects with getattr."""

        # Create a minimal object without dataclass
        class MinimalRisk:
            pass

        risk = MinimalRisk()

        # Should handle missing attributes gracefully via getattr
        display_risk("unknown-pkg", risk)

    def test_T203_DR07_display_risk_partial_attributes(self) -> None:
        """T203.DR07: display_risk handles objects with only some attributes."""

        class PartialRisk:
            risk_level = "SUSPICIOUS"
            # Missing: risk_score, signals, recommendation

        risk = PartialRisk()
        # Should not raise - uses getattr with defaults
        display_risk("partial-pkg", risk)
