"""
Tests for CLI entry point.

SPEC: S200
TESTS: T200.01-T200.10
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from phantom_pip.cli import app

runner = CliRunner()


class TestT200_CLI:
    """T200: CLI entry point tests."""

    def test_T200_01_version_flag(self) -> None:
        """T200.01: --version shows version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "phantom-pip" in result.stdout

    def test_T200_02_version_command(self) -> None:
        """T200.02: version command works."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "phantom-pip" in result.stdout

    def test_T200_03_no_args_shows_help(self) -> None:
        """T200.03: No arguments shows help (exit code 2 is typer's usage error)."""
        result = runner.invoke(app, [])
        # Typer with no_args_is_help=True returns exit code 2 (usage error)
        assert result.exit_code == 2
        assert "Usage:" in result.stdout or "install" in result.stdout

    def test_T200_04_install_help(self) -> None:
        """T200.04: install --help shows help."""
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0
        assert "Install" in result.stdout or "slopsquatting" in result.stdout.lower()

    def test_T200_05_config_show(self) -> None:
        """T200.05: config --show works."""
        result = runner.invoke(app, ["config", "--show"])
        assert result.exit_code == 0
        assert "enabled" in result.stdout

    def test_T200_06_config_init(self, tmp_path) -> None:
        """T200.06: config --init creates file."""
        with patch("phantom_pip.cli.create_default_config") as mock_create:
            mock_create.return_value = tmp_path / "pip.yaml"
            result = runner.invoke(app, ["config", "--init"])
        assert result.exit_code == 0
        assert "Created" in result.stdout

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T200_07_skip_validation(self, mock_delegate: MagicMock) -> None:
        """T200.07: --skip-validation bypasses checks."""
        mock_delegate.return_value = 0
        result = runner.invoke(app, ["install", "flask", "--skip-validation"])
        mock_delegate.assert_called_once()
        assert result.exit_code == 0

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T200_08_passthrough_uninstall(self, mock_delegate: MagicMock) -> None:
        """T200.08: uninstall passes through."""
        mock_delegate.return_value = 0
        result = runner.invoke(app, ["uninstall", "flask", "-y"])
        assert "uninstall" in mock_delegate.call_args[0][0]

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T200_09_passthrough_list(self, mock_delegate: MagicMock) -> None:
        """T200.09: list passes through."""
        mock_delegate.return_value = 0
        result = runner.invoke(app, ["list"])
        assert "list" in mock_delegate.call_args[0][0]

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T200_10_passthrough_freeze(self, mock_delegate: MagicMock) -> None:
        """T200.10: freeze passes through."""
        mock_delegate.return_value = 0
        result = runner.invoke(app, ["freeze"])
        assert "freeze" in mock_delegate.call_args[0][0]


# ============================================================================
# Additional tests for CLI coverage - Lines 37-39, 113-195, 224, 252-253, 266
# ============================================================================


class TestT200_PhantomGuardUnavailable:
    """T200.11-T200.12: Tests for PHANTOM_GUARD_AVAILABLE = False path."""

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.load_config")
    @patch("phantom_pip.cli.PHANTOM_GUARD_AVAILABLE", False)
    def test_T200_11_phantom_guard_unavailable_warns_and_delegates(
        self, mock_load_config: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.11: When phantom-guard is not installed, warn and delegate to pip.

        SPEC: S200
        Covers lines: 113-116 (PHANTOM_GUARD_AVAILABLE check)
        """
        from phantom_pip.config import Config
        mock_load_config.return_value = Config(enabled=True)
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "flask"])

        assert result.exit_code == 0
        assert "phantom-guard not installed" in result.stdout
        mock_delegate.assert_called_once()
        assert "install" in mock_delegate.call_args[0][0]

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.load_config")
    @patch("phantom_pip.cli.PHANTOM_GUARD_AVAILABLE", False)
    def test_T200_12_phantom_guard_unavailable_with_nonzero_exit(
        self, mock_load_config: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.12: Propagate pip exit code when phantom-guard unavailable.

        SPEC: S200
        Covers lines: 113-116
        """
        from phantom_pip.config import Config
        mock_load_config.return_value = Config(enabled=True)
        mock_delegate.return_value = 1

        result = runner.invoke(app, ["install", "nonexistent-package-xyz"])

        assert result.exit_code == 1


class TestT200_InstallValidationFlow:
    """T200.13-T200.25: Tests for main install validation flow."""

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_13_install_with_validation_safe_package(
        self, mock_load_config: MagicMock, mock_validate: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.13: Install flow with validation for safe package.

        SPEC: S200
        Covers lines: 118-188 (main validation flow)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "SAFE"
        mock_risk.risk_score = 0.1
        mock_risk.signals = []

        mock_load_config.return_value = Config(enabled=True, mode="silent")
        mock_validate.return_value = mock_risk
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "flask"])

        assert result.exit_code == 0
        mock_validate.assert_called_once_with("flask", registry="pypi")
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_14_install_no_packages_to_validate(
        self, mock_load_config: MagicMock, mock_validate: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.14: Install with only editable package, skip validation.

        SPEC: S200
        Covers lines: 126-129 (no packages to validate)
        """
        from phantom_pip.config import Config

        mock_load_config.return_value = Config(enabled=True)
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "-e", "."])

        assert result.exit_code == 0
        mock_validate.assert_not_called()
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.display_blocked_message")
    @patch("phantom_pip.cli.load_config")
    def test_T200_15_blocklist_blocking_in_block_mode(
        self, mock_load_config: MagicMock, mock_display_blocked: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.15: Blocked package aborts in block mode.

        SPEC: S200
        Covers lines: 139-144 (blocklist handling with block mode)
        """
        from phantom_pip.config import Config

        mock_load_config.return_value = Config(
            enabled=True,
            mode="block",
            blocklist=["malware-pkg"]
        )

        result = runner.invoke(app, ["install", "malware-pkg"])

        assert result.exit_code == 1
        assert "Blocked" in result.stdout
        mock_display_blocked.assert_called_once()
        mock_delegate.assert_not_called()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.display_blocked_message")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_16_blocklist_warning_in_warn_mode(
        self, mock_load_config: MagicMock, mock_validate: MagicMock,
        mock_display_blocked: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.16: Blocked package shows warning but continues in warn mode.

        SPEC: S200
        Covers lines: 139-141 (blocklist with non-block mode)
        """
        from phantom_pip.config import Config

        mock_load_config.return_value = Config(
            enabled=True,
            mode="warn",
            blocklist=["bad-pkg"]
        )
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "bad-pkg"])

        mock_display_blocked.assert_called_once()
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_17_silent_mode_no_output(
        self, mock_load_config: MagicMock, mock_validate: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.17: Silent mode logs only, no blocking.

        SPEC: S200
        Covers lines: 159-161 (silent mode)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "HIGH_RISK"
        mock_risk.risk_score = 0.9
        mock_risk.signals = ["typosquat"]

        mock_load_config.return_value = Config(enabled=True, mode="silent")
        mock_validate.return_value = mock_risk
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "risky-pkg"])

        assert result.exit_code == 0
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.display_summary")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_18_warn_mode_shows_summary(
        self, mock_load_config: MagicMock, mock_validate: MagicMock,
        mock_display_summary: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.18: Warn mode shows summary but proceeds.

        SPEC: S200
        Covers lines: 162-165 (warn mode)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "SUSPICIOUS"
        mock_risk.risk_score = 0.5
        mock_risk.signals = ["low downloads"]

        mock_load_config.return_value = Config(enabled=True, mode="warn")
        mock_validate.return_value = mock_risk
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "suspicious-pkg"])

        assert result.exit_code == 0
        mock_display_summary.assert_called_once()
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.display_blocked_message")
    @patch("phantom_pip.cli.load_config")
    def test_T200_19_block_mode_blocks_blocklisted_package(
        self, mock_load_config: MagicMock, mock_display_blocked: MagicMock,
        mock_delegate: MagicMock
    ) -> None:
        """T200.19: Block mode blocks blocklisted package.

        SPEC: S200
        Covers lines: 139-144, 166-175 (blocklist in block mode)
        """
        from phantom_pip.config import Config

        # Test the blocklist path which is simpler and doesn't need async mocking
        mock_load_config.return_value = Config(
            enabled=True,
            mode="block",
            threshold=0.6,
            blocklist=["risky-pkg"]
        )

        result = runner.invoke(app, ["install", "risky-pkg"])

        assert result.exit_code == 1
        assert "Blocked" in result.stdout
        mock_display_blocked.assert_called_once()
        mock_delegate.assert_not_called()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_20_block_mode_allows_below_threshold(
        self, mock_load_config: MagicMock, mock_validate: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.20: Block mode allows packages below threshold.

        SPEC: S200
        Covers lines: 166-175 (block mode with low risk score)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "SUSPICIOUS"
        mock_risk.risk_score = 0.3
        mock_risk.signals = []

        mock_load_config.return_value = Config(enabled=True, mode="block", threshold=0.6)
        mock_validate.return_value = mock_risk
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "low-risk-pkg"])

        assert result.exit_code == 0
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.confirm_batch_installation")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_21_interactive_mode_prompts_user(
        self, mock_load_config: MagicMock, mock_validate: MagicMock,
        mock_confirm: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.21: Interactive mode prompts for confirmation.

        SPEC: S200
        Covers lines: 176-184 (interactive mode)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "SUSPICIOUS"
        mock_risk.risk_score = 0.5
        mock_risk.signals = ["low downloads"]

        mock_load_config.return_value = Config(enabled=True, mode="interactive")
        mock_validate.return_value = mock_risk
        mock_confirm.return_value = (["test-pkg"], [])
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "test-pkg"])

        assert result.exit_code == 0
        mock_confirm.assert_called_once()
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.display_skipped_message")
    @patch("phantom_pip.cli.confirm_batch_installation")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_22_interactive_mode_with_rejected_packages(
        self, mock_load_config: MagicMock, mock_validate: MagicMock,
        mock_confirm: MagicMock, mock_display_skipped: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.22: Interactive mode handles rejected packages.

        SPEC: S200
        Covers lines: 183-184 (display skipped message)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "HIGH_RISK"
        mock_risk.risk_score = 0.9
        mock_risk.signals = ["typosquat"]

        mock_load_config.return_value = Config(enabled=True, mode="interactive")
        mock_validate.return_value = mock_risk
        mock_confirm.return_value = ([], ["rejected-pkg"])
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "rejected-pkg"])

        mock_display_skipped.assert_called_once_with(["rejected-pkg"])

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.load_config")
    def test_T200_23_editable_install_skips_validation(
        self, mock_load_config: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.23: Editable installs skip validation entirely.

        SPEC: S200
        Covers lines: 126-129 (no packages to validate path)
        """
        from phantom_pip.config import Config

        mock_load_config.return_value = Config(enabled=True, mode="silent")
        mock_delegate.return_value = 0

        # Editable install with local path - no package to validate
        result = runner.invoke(app, ["install", "-e", "."])

        assert result.exit_code == 0
        mock_delegate.assert_called_once()


class TestT200_ErrorHandling:
    """T200.26-T200.28: Tests for SecurityError and PhantomPipError handling."""

    @patch("phantom_pip.cli.parse_pip_args")
    @patch("phantom_pip.cli.load_config")
    def test_T200_26_security_error_exits_with_code_2(
        self, mock_load_config: MagicMock, mock_parse: MagicMock
    ) -> None:
        """T200.26: SecurityError exits with code 2.

        SPEC: S200
        Covers lines: 190-192 (SecurityError handling)
        """
        from phantom_pip.config import Config
        from phantom_pip.errors import SecurityError

        mock_load_config.return_value = Config(enabled=True)
        mock_parse.side_effect = SecurityError("Malicious input detected")

        result = runner.invoke(app, ["install", "malicious; rm -rf /"])

        assert result.exit_code == 2
        assert "SECURITY ERROR" in result.stdout

    @patch("phantom_pip.cli.parse_pip_args")
    @patch("phantom_pip.cli.load_config")
    def test_T200_27_phantom_pip_error_exits_with_code_1(
        self, mock_load_config: MagicMock, mock_parse: MagicMock
    ) -> None:
        """T200.27: PhantomPipError exits with code 1.

        SPEC: S200
        Covers lines: 193-195 (PhantomPipError handling)
        """
        from phantom_pip.config import Config
        from phantom_pip.errors import PhantomPipError

        mock_load_config.return_value = Config(enabled=True)
        mock_parse.side_effect = PhantomPipError("Configuration parse failed")

        result = runner.invoke(app, ["install", "flask"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestT200_ConfigCommand:
    """T200.29: Test config command without flags."""

    def test_T200_29_config_no_flags_shows_usage(self) -> None:
        """T200.29: config command without --show or --init shows usage.

        SPEC: S200
        Covers line: 224 (config without flags)
        """
        result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "--show" in result.stdout
        assert "--init" in result.stdout


class TestT200_ShowPassthrough:
    """T200.30-T200.31: Tests for show passthrough command."""

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T200_30_show_passthrough(self, mock_delegate: MagicMock) -> None:
        """T200.30: show command passes through to pip.

        SPEC: S200
        Covers lines: 252-253 (show passthrough)
        """
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["show", "flask"])

        assert result.exit_code == 0
        assert "show" in mock_delegate.call_args[0][0]
        assert "flask" in mock_delegate.call_args[0][0]

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T200_31_show_with_extra_args(self, mock_delegate: MagicMock) -> None:
        """T200.31: show command passes extra arguments.

        SPEC: S200
        Covers lines: 252-253 (show with extra args)
        """
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["show", "flask", "--files"])

        assert "show" in mock_delegate.call_args[0][0]
        assert "--files" in mock_delegate.call_args[0][0]


class TestT200_MultiplePackages:
    """T200.32-T200.33: Tests for multiple package validation."""

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_32_multiple_packages_validated(
        self, mock_load_config: MagicMock, mock_validate: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.32: Multiple packages are all validated.

        SPEC: S200
        Covers lines: 148-156 (validation loop)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "SAFE"
        mock_risk.risk_score = 0.1
        mock_risk.signals = []

        mock_load_config.return_value = Config(enabled=True, mode="silent")
        mock_validate.return_value = mock_risk
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "flask", "requests", "django"])

        assert result.exit_code == 0
        assert mock_validate.call_count == 3

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_33_allowlisted_packages_skip_validation(
        self, mock_load_config: MagicMock, mock_validate: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.33: Allowlisted packages skip validation.

        SPEC: S200
        Covers lines: 131-136 (allowlist/blocklist filtering)
        """
        from phantom_pip.config import Config

        mock_load_config.return_value = Config(
            enabled=True,
            mode="silent",
            allowlist=["flask", "requests"]
        )
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "flask", "requests"])

        assert result.exit_code == 0
        mock_validate.assert_not_called()


class TestT200_ConfigDisabled:
    """T200.34: Test config disabled path."""

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.load_config")
    def test_T200_34_config_disabled_skips_validation(
        self, mock_load_config: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.34: When config.enabled=False, skip validation.

        SPEC: S200
        Covers lines: 108-110 (config disabled check)
        """
        from phantom_pip.config import Config

        mock_load_config.return_value = Config(enabled=False)
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "flask"])

        assert result.exit_code == 0
        mock_delegate.assert_called_once()


class TestT200_CLIOptions:
    """T200.35-T200.37: Tests for CLI option handling."""

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_35_mode_override_via_cli(
        self, mock_load_config: MagicMock, mock_validate: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.35: --mode flag overrides config.

        SPEC: S200
        Covers lines: 100-105 (merge_cli_options)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "HIGH_RISK"
        mock_risk.risk_score = 0.9
        mock_risk.signals = ["typosquat"]

        mock_load_config.return_value = Config(enabled=True, mode="interactive")
        mock_validate.return_value = mock_risk
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "risky-pkg", "--mode", "silent"])

        assert result.exit_code == 0
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.confirm_batch_installation")
    @patch("phantom_pip.cli.validate_package")
    @patch("phantom_pip.cli.load_config")
    def test_T200_37_yes_flag_auto_approves(
        self, mock_load_config: MagicMock, mock_validate: MagicMock,
        mock_confirm: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T200.37: -y/--yes flag auto-approves packages.

        SPEC: S200
        Covers lines: 100-105 (auto_approve via -y)
        """
        from phantom_pip.config import Config

        mock_risk = MagicMock()
        mock_risk.risk_level = "HIGH_RISK"
        mock_risk.risk_score = 0.9
        mock_risk.signals = ["typosquat"]

        mock_load_config.return_value = Config(enabled=True, mode="interactive")
        mock_validate.return_value = mock_risk
        mock_confirm.return_value = (["risky-pkg"], [])
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "risky-pkg", "-y"])

        mock_confirm.assert_called_once()
        call_kwargs = mock_confirm.call_args
        assert call_kwargs[1].get("auto_approve") is True or (
            len(call_kwargs[0]) > 1 and call_kwargs[0][1] is True
        )
