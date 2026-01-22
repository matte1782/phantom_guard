"""
Integration tests for phantom-pip.

SPEC: S208
TESTS: T208.01-T208.10
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from dataclasses import dataclass, field
from typing import Optional

from typer.testing import CliRunner

from phantom_pip.cli import app
from phantom_pip.parser import parse_pip_args
from phantom_pip.extract import extract_packages, get_package_names
from phantom_pip.config import Config, load_config, save_config
from phantom_pip.lists import filter_packages_by_lists


runner = CliRunner()


@dataclass
class MockPackageRisk:
    """Mock PackageRisk for integration tests."""

    name: str = ""
    risk_level: str = "SAFE"
    risk_score: float = 0.1
    signals: list[str] = field(default_factory=list)
    recommendation: Optional[str] = None


class TestT208_EndToEnd:
    """T208: End-to-end integration tests."""

    def test_T208_01_safe_package_flow(self) -> None:
        """T208.01: Full flow for safe package."""
        # Parse -> Extract -> Validate -> Delegate
        parsed = parse_pip_args(["install", "flask"])
        packages = extract_packages(parsed)
        names = get_package_names(packages)

        assert "flask" in names

        # Filter by lists
        allowed, blocked, to_validate = filter_packages_by_lists(
            names, allowlist=[], blocklist=[]
        )
        assert "flask" in to_validate
        assert blocked == []

    def test_T208_02_blocked_package_flow(self) -> None:
        """T208.02: Full flow for blocked package."""
        parsed = parse_pip_args(["install", "malware-pkg"])
        packages = extract_packages(parsed)
        names = get_package_names(packages)

        # Filter with blocklist
        allowed, blocked, to_validate = filter_packages_by_lists(
            names, allowlist=[], blocklist=["malware-pkg"]
        )
        assert "malware-pkg" in blocked
        assert "malware-pkg" not in to_validate

    def test_T208_03_allowlisted_package_flow(self) -> None:
        """T208.03: Allowlisted packages skip validation."""
        parsed = parse_pip_args(["install", "my-internal-lib"])
        packages = extract_packages(parsed)
        names = get_package_names(packages)

        # Filter with allowlist
        allowed, blocked, to_validate = filter_packages_by_lists(
            names, allowlist=["my-internal-lib"], blocklist=[]
        )
        assert "my-internal-lib" in allowed
        assert "my-internal-lib" not in to_validate

    def test_T208_04_requirements_file_flow(self, tmp_path: Path) -> None:
        """T208.04: Full flow with requirements.txt."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask>=2.0\ndjango\n# comment\nrequests")

        parsed = parse_pip_args(["install", "-r", str(req_file)])
        packages = extract_packages(parsed)
        names = get_package_names(packages)

        assert "flask" in names
        assert "django" in names
        assert "requests" in names

    def test_T208_05_mixed_args_flow(self) -> None:
        """T208.05: Full flow with mixed arguments."""
        parsed = parse_pip_args([
            "install",
            "flask",
            "django[async]>=4.0",
            "-e", ".",
            "--upgrade",
        ])
        packages = extract_packages(parsed)
        names = get_package_names(packages)

        # Should have flask and django, not editable
        assert "flask" in names
        assert "django" in names
        assert len(names) == 2  # -e . is not validatable

    def test_T208_06_config_integration(self, tmp_path: Path) -> None:
        """T208.06: Config file integration."""
        config_file = tmp_path / "pip.yaml"
        config_file.write_text("""
enabled: true
mode: block
threshold: 0.8
allowlist:
  - internal-*
blocklist:
  - banned-pkg
""")

        config = load_config(config_file)
        assert config.mode == "block"
        assert config.threshold == 0.8
        assert "internal-*" in config.allowlist
        assert "banned-pkg" in config.blocklist


class TestT208_CLI_Integration:
    """T208: CLI integration tests with mocked pip."""

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T208_C01_version_no_pip(self, mock_delegate: MagicMock) -> None:
        """T208.C01: Version command doesn't call pip."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "phantom-pip" in result.stdout
        mock_delegate.assert_not_called()

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T208_C02_skip_validation(self, mock_delegate: MagicMock) -> None:
        """T208.C02: --skip-validation bypasses checks."""
        mock_delegate.return_value = 0
        result = runner.invoke(app, ["install", "--skip-validation", "flask"])
        assert result.exit_code == 0
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    @patch("phantom_pip.cli.load_config")
    def test_T208_C03_disabled_config(
        self, mock_config: MagicMock, mock_delegate: MagicMock
    ) -> None:
        """T208.C03: Disabled config bypasses validation."""
        mock_config.return_value = Config(enabled=False)
        mock_delegate.return_value = 0

        result = runner.invoke(app, ["install", "flask"])
        assert result.exit_code == 0
        mock_delegate.assert_called_once()

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T208_C04_passthrough_list(self, mock_delegate: MagicMock) -> None:
        """T208.C04: list command passes through."""
        mock_delegate.return_value = 0
        result = runner.invoke(app, ["list", "--format=json"])
        mock_delegate.assert_called_once_with(["list", "--format=json"])

    @patch("phantom_pip.cli.delegate_to_pip")
    def test_T208_C05_passthrough_freeze(self, mock_delegate: MagicMock) -> None:
        """T208.C05: freeze command passes through."""
        mock_delegate.return_value = 0
        result = runner.invoke(app, ["freeze"])
        mock_delegate.assert_called_once_with(["freeze"])


class TestT208_Security_Integration:
    """T208: Security integration tests."""

    def test_T208_S01_injection_blocked(self) -> None:
        """T208.S01: Shell injection in package name blocked."""
        # This should be rejected during extraction
        parsed = parse_pip_args(["install", "flask; rm -rf /"])
        packages = extract_packages(parsed)

        # Malicious package should be rejected
        names = get_package_names(packages)
        assert "flask; rm -rf /" not in names

    def test_T208_S02_pipe_injection_blocked(self) -> None:
        """T208.S02: Pipe injection blocked."""
        parsed = parse_pip_args(["install", "flask | cat /etc/passwd"])
        packages = extract_packages(parsed)
        names = get_package_names(packages)

        # Malicious package should be rejected
        assert "flask | cat /etc/passwd" not in names

    def test_T208_S03_backtick_injection_blocked(self) -> None:
        """T208.S03: Backtick injection blocked."""
        parsed = parse_pip_args(["install", "flask`whoami`"])
        packages = extract_packages(parsed)
        names = get_package_names(packages)

        # Malicious package should be rejected
        assert "flask`whoami`" not in names

    def test_T208_S04_valid_version_passes(self) -> None:
        """T208.S04: Valid version specifiers pass."""
        parsed = parse_pip_args(["install", "flask>=2.0,<3.0"])
        packages = extract_packages(parsed)
        names = get_package_names(packages)

        assert "flask" in names

    def test_T208_S05_null_byte_injection_blocked(self) -> None:
        """T208.S05: CRITICAL - Null byte injection blocked."""
        from phantom_pip.extract import validate_package_name

        # Null bytes must be rejected
        assert validate_package_name("flask\x00evil") is False
        assert validate_package_name("flask") is True

    def test_T208_S06_newline_injection_blocked(self) -> None:
        """T208.S06: CRITICAL - Newline injection blocked."""
        from phantom_pip.extract import validate_package_name

        # Newlines must be rejected
        assert validate_package_name("flask\nmalicious") is False
        assert validate_package_name("flask\rmalicious") is False

    def test_T208_S07_unc_path_not_validated(self) -> None:
        """T208.S07: UNC paths are not treated as package names."""
        from phantom_pip.parser import _is_url_or_path

        # UNC paths should be recognized as paths, not packages
        assert _is_url_or_path("//server/share") is True
        assert _is_url_or_path("\\\\server\\share") is True

    def test_T208_S08_threshold_validation(self) -> None:
        """T208.S08: CRITICAL - Threshold is validated in merge."""
        from phantom_pip.config import Config, merge_cli_options

        config = Config(threshold=0.6)

        # Invalid threshold should be clamped
        merged = merge_cli_options(config, threshold=999.0)
        assert merged.threshold == 1.0

        merged = merge_cli_options(config, threshold=-5.0)
        assert merged.threshold == 0.0


class TestT208_Performance:
    """T208: Performance sanity tests."""

    def test_T208_P01_parse_performance(self) -> None:
        """T208.P01: Parsing many packages is fast."""
        import time

        packages = [f"package-{i}" for i in range(100)]
        args = ["install"] + packages

        start = time.perf_counter()
        parsed = parse_pip_args(args)
        _ = extract_packages(parsed)
        elapsed = time.perf_counter() - start

        # Should complete in under 100ms
        assert elapsed < 0.1

    def test_T208_P02_filter_performance(self) -> None:
        """T208.P02: List filtering is fast for typical use cases."""
        import time

        # Typical case: 10 packages, 20 list entries
        packages = [f"package-{i}" for i in range(10)]
        allowlist = [f"allowed-{i}" for i in range(10)]
        blocklist = [f"blocked-{i}" for i in range(10)]

        start = time.perf_counter()
        _, _, _ = filter_packages_by_lists(packages, allowlist, blocklist)
        elapsed = time.perf_counter() - start

        # Should complete in under 10ms for typical usage
        assert elapsed < 0.01
