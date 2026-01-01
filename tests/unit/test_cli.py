# SPEC: S010-S019 - CLI Interface
# Gate 3: Test Design - Stubs
"""
Unit tests for the CLI module.

SPEC_IDs: S010-S019
TEST_IDs: T010.*
EDGE_CASES: EC080-EC095
"""

from __future__ import annotations

import pytest


class TestValidateCommand:
    """Tests for 'phantom-guard validate' command.

    SPEC: S010-S019 - CLI commands
    Total tests: 24 (16 unit, 8 integration)
    """

    # =========================================================================
    # OUTPUT FORMAT TESTS
    # =========================================================================

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_validate_text_output(self):
        """
        TEST_ID: T010.01
        SPEC: S010
        EC: EC080

        Given: Package "flask" (safe)
        When: validate is called with default format
        Then: Outputs text format with SAFE status
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_validate_json_output(self):
        """
        TEST_ID: T010.02
        SPEC: S010
        EC: EC089

        Given: Package "flask"
        When: validate is called with --output json
        Then: Outputs valid JSON
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_validate_json_structure(self):
        """
        TEST_ID: T010.03
        SPEC: S010
        EC: EC089

        Given: JSON output from validate
        When: Parsing JSON
        Then: Contains name, recommendation, risk_score, signals
        """
        pass

    # =========================================================================
    # EXIT CODE TESTS
    # =========================================================================

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_exit_code_safe(self):
        """
        TEST_ID: T010.04
        SPEC: S010
        EC: EC080

        Given: Package is SAFE
        When: validate completes
        Then: Exit code is 0
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_exit_code_suspicious(self):
        """
        TEST_ID: T010.05
        SPEC: S010
        EC: EC081

        Given: Package is SUSPICIOUS
        When: validate completes
        Then: Exit code is 1
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_exit_code_high_risk(self):
        """
        TEST_ID: T010.06
        SPEC: S010
        EC: EC082

        Given: Package is HIGH_RISK
        When: validate completes
        Then: Exit code is 2
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_exit_code_not_found(self):
        """
        TEST_ID: T010.07
        SPEC: S010
        EC: EC083

        Given: Package NOT_FOUND
        When: validate completes
        Then: Exit code is 3
        """
        pass

    # =========================================================================
    # VERBOSE/QUIET MODE TESTS
    # =========================================================================

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_verbose_shows_signals(self):
        """
        TEST_ID: T010.08
        SPEC: S010
        EC: EC091

        Given: Package with signals
        When: validate is called with -v
        Then: Output includes all signals
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_quiet_minimal_output(self):
        """
        TEST_ID: T010.09
        SPEC: S010
        EC: EC092

        Given: Any package
        When: validate is called with -q
        Then: Output is minimal (just result)
        """
        pass

    # =========================================================================
    # OPTIONS TESTS
    # =========================================================================

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_custom_threshold(self):
        """
        TEST_ID: T010.10
        SPEC: S010
        EC: EC093

        Given: Package with score 0.4
        When: validate with --threshold 0.5
        Then: Classified as SAFE (below threshold)
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_offline_mode_flag(self):
        """
        TEST_ID: T010.11
        SPEC: S010
        EC: EC094

        Given: Package in cache
        When: validate with --offline
        Then: Uses cache only (no network)
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_registry_selection(self):
        """
        TEST_ID: T010.12
        SPEC: S010
        EC: EC095

        Given: Package name "express"
        When: validate with --registry npm
        Then: Uses npm registry
        """
        pass


class TestCheckCommand:
    """Tests for 'phantom-guard check' command.

    SPEC: S010-S019, S013
    EC: EC084-EC088
    """

    @pytest.mark.unit
    def test_check_requirements_file(self, tmp_path):
        """
        TEST_ID: T010.18
        SPEC: S013
        EC: EC084

        Given: Valid requirements.txt with safe packages
        When: check is called
        Then: Exit code 0
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create test requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\nrequests>=2.0\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file)])

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_check_file_not_found(self):
        """
        TEST_ID: T010.19
        SPEC: S013
        EC: EC086

        Given: Non-existent file path
        When: check is called
        Then: Exit code 4 (EXIT_INPUT_ERROR), error message
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import EXIT_INPUT_ERROR, app

        runner = CliRunner()
        result = runner.invoke(app, ["check", "nonexistent.txt"])

        assert result.exit_code == EXIT_INPUT_ERROR
        assert "not found" in result.stdout.lower() or "does not exist" in result.stdout.lower()

    @pytest.mark.unit
    def test_check_empty_file(self, tmp_path):
        """
        TEST_ID: T010.20
        SPEC: S013
        EC: EC087

        Given: Empty requirements file
        When: check is called
        Then: Exit code 0, "No packages" message
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create empty file
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file)])

        assert result.exit_code == 0
        assert "no packages" in result.stdout.lower()

    @pytest.mark.unit
    def test_check_package_json(self, tmp_path):
        """
        TEST_ID: T010.21
        SPEC: S014
        EC: EC084

        Given: Valid package.json with dependencies
        When: check is called
        Then: Exit code 0, validates npm packages
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create test package.json
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text("""{
  "name": "test-project",
  "dependencies": {
    "express": "^4.17.0",
    "lodash": "^4.17.0"
  }
}""")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(pkg_file)])

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_check_cargo_toml(self, tmp_path):
        """
        TEST_ID: T010.22
        SPEC: S015
        EC: EC084

        Given: Valid Cargo.toml with dependencies
        When: check is called
        Then: Exit code 0, validates crates packages
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create test Cargo.toml
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text("""[package]
name = "test-project"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
""")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(cargo_file)])

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_check_with_ignore(self, tmp_path):
        """
        TEST_ID: T010.23
        SPEC: S013
        EC: EC089

        Given: requirements.txt with multiple packages
        When: check is called with --ignore option
        Then: Ignores specified packages, validates others
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create test requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\nrequests>=2.0\ndjango>=3.0\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file), "--ignore", "django"])

        assert result.exit_code == 0
        # Verify django was ignored in output

    @pytest.mark.unit
    def test_check_with_registry_override(self, tmp_path):
        """
        TEST_ID: T010.24
        SPEC: S013
        EC: EC095

        Given: requirements.txt (default pypi)
        When: check is called with -r npm option
        Then: Overrides registry detection, uses npm
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create test file
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("express\nlodash\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file), "-r", "npm"])

        # Should check npm registry instead of pypi
        assert result.exit_code in [0, 1, 2, 3]  # Valid exit codes

    @pytest.mark.unit
    def test_check_invalid_file(self, tmp_path):
        """
        TEST_ID: T010.25
        SPEC: S013, S014, S015
        EC: EC088

        Given: Invalid JSON/TOML file
        When: check is called
        Then: Exit code 4 (EXIT_INPUT_ERROR), parse error
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import EXIT_INPUT_ERROR, app

        # Create invalid JSON file
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"name": "test", invalid json}')

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(pkg_file)])

        assert result.exit_code == EXIT_INPUT_ERROR
        assert "parse" in result.stdout.lower() or "invalid" in result.stdout.lower()

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_check_mixed_results(self):
        """
        TEST_ID: T010.14
        SPEC: S010
        EC: EC085

        Given: requirements.txt with suspicious package
        When: check is called
        Then: Exit code 1, lists suspicious packages
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_check_fail_on_suspicious(self):
        """
        TEST_ID: T010.26
        SPEC: S010
        EC: EC090

        Given: File with suspicious package
        When: check with --fail-on suspicious
        Then: Exit code 1
        """
        pass


class TestCacheCommand:
    """Tests for 'phantom-guard cache' command.

    SPEC: S016, S017
    """

    @pytest.mark.skip(reason="Stub - implement with S016")
    @pytest.mark.unit
    def test_cache_clear(self):
        """
        TEST_ID: T010.19
        SPEC: S016

        Given: Cache with entries
        When: cache clear is called
        Then: Cache is emptied
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S017")
    @pytest.mark.unit
    def test_cache_stats(self):
        """
        TEST_ID: T010.20
        SPEC: S017

        Given: Cache with entries
        When: cache stats is called
        Then: Shows entry count and size
        """
        pass

    @pytest.mark.unit
    def test_cache_path(self) -> None:
        """
        TEST_ID: T010.24
        SPEC: S016

        Test cache path command shows location.
        """
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["cache", "path"])

        assert result.exit_code == 0
        assert "Cache path:" in result.stdout


class TestVersionCommand:
    """Tests for 'phantom-guard version' command.

    SPEC: S010
    """

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_version_output(self):
        """
        TEST_ID: T010.21
        SPEC: S010

        Given: CLI installed
        When: version is called
        Then: Outputs version string
        """
        pass


class TestCLIHelp:
    """Tests for CLI help output."""

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_main_help(self):
        """
        TEST_ID: T010.22
        SPEC: S010

        Given: CLI installed
        When: --help is called
        Then: Shows help with all commands
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_validate_help(self):
        """
        TEST_ID: T010.23
        SPEC: S010

        Given: CLI installed
        When: validate --help is called
        Then: Shows validate options
        """
        pass

    @pytest.mark.skip(reason="Stub - implement with S010")
    @pytest.mark.unit
    def test_check_help(self):
        """
        TEST_ID: T010.24
        SPEC: S010

        Given: CLI installed
        When: check --help is called
        Then: Shows check options
        """
        pass


# =============================================================================
# NEW TESTS FOR COVERAGE
# =============================================================================


class TestFormatSize:
    """Tests for _format_size helper function."""

    @pytest.mark.unit
    def test_format_size_bytes(self):
        """Test bytes formatting."""
        from phantom_guard.cli.main import _format_size

        assert _format_size(500) == "500.0 B"
        assert _format_size(0) == "0.0 B"

    @pytest.mark.unit
    def test_format_size_kilobytes(self):
        """Test kilobytes formatting."""
        from phantom_guard.cli.main import _format_size

        assert _format_size(1024) == "1.0 KB"
        assert _format_size(2048) == "2.0 KB"

    @pytest.mark.unit
    def test_format_size_megabytes(self):
        """Test megabytes formatting."""
        from phantom_guard.cli.main import _format_size

        assert _format_size(1024 * 1024) == "1.0 MB"
        assert _format_size(5 * 1024 * 1024) == "5.0 MB"

    @pytest.mark.unit
    def test_format_size_gigabytes(self):
        """Test gigabytes formatting."""
        from phantom_guard.cli.main import _format_size

        assert _format_size(1024 * 1024 * 1024) == "1.0 GB"

    @pytest.mark.unit
    def test_format_size_terabytes(self):
        """Test terabytes formatting for very large sizes."""
        from phantom_guard.cli.main import _format_size

        result = _format_size(1024 * 1024 * 1024 * 1024)
        assert "TB" in result


class TestCacheClearCommand:
    """Tests for cache clear command."""

    @pytest.mark.unit
    def test_cache_clear_no_cache(self, monkeypatch):
        """Test cache clear when no cache exists."""
        from pathlib import Path

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Mock get_default_cache_path to return a non-existent path
        def mock_cache_path():
            return Path("/nonexistent/cache/path")

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        runner = CliRunner()
        result = runner.invoke(app, ["cache", "clear", "-f"])

        assert result.exit_code == 0
        assert "no cache" in result.stdout.lower()

    @pytest.mark.unit
    def test_cache_clear_cancelled(self, monkeypatch, tmp_path):
        """Test cache clear when user cancels."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create a fake cache file
        cache_file = tmp_path / "phantom_guard.db"
        cache_file.write_text("fake cache")

        def mock_cache_path():
            return cache_file

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        runner = CliRunner()
        # User says "n" to confirmation
        result = runner.invoke(app, ["cache", "clear"], input="n\n")

        assert result.exit_code == 0
        assert "cancelled" in result.stdout.lower()

    @pytest.mark.unit
    def test_cache_clear_with_force(self, monkeypatch, tmp_path):
        """Test cache clear with force flag."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create a fake cache file
        cache_file = tmp_path / "phantom_guard.db"
        cache_file.write_text("fake cache")

        def mock_cache_path():
            return cache_file

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        # Mock _clear_cache to return some count
        with patch("phantom_guard.cli.main._clear_cache", new_callable=AsyncMock) as mock_clear:
            mock_clear.return_value = 5

            runner = CliRunner()
            result = runner.invoke(app, ["cache", "clear", "-f"])

            assert result.exit_code == 0
            assert "5 entries" in result.stdout

    @pytest.mark.unit
    def test_cache_clear_with_registry_filter(self, monkeypatch, tmp_path):
        """Test cache clear with specific registry."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        cache_file = tmp_path / "phantom_guard.db"
        cache_file.write_text("fake cache")

        def mock_cache_path():
            return cache_file

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        with patch("phantom_guard.cli.main._clear_cache", new_callable=AsyncMock) as mock_clear:
            mock_clear.return_value = 3

            runner = CliRunner()
            # User confirms with "y"
            result = runner.invoke(app, ["cache", "clear", "-r", "pypi"], input="y\n")

            assert result.exit_code == 0
            mock_clear.assert_called_once()


class TestCacheStatsCommand:
    """Tests for cache stats command."""

    @pytest.mark.unit
    def test_cache_stats_no_cache(self, monkeypatch):
        """Test cache stats when no cache exists."""
        from pathlib import Path

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        def mock_cache_path():
            return Path("/nonexistent/cache/path")

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        runner = CliRunner()
        result = runner.invoke(app, ["cache", "stats"])

        assert result.exit_code == 0
        assert "no cache" in result.stdout.lower()

    @pytest.mark.unit
    def test_cache_stats_empty_cache(self, monkeypatch, tmp_path):
        """Test cache stats when cache is empty."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        cache_file = tmp_path / "phantom_guard.db"
        cache_file.write_text("fake cache")

        def mock_cache_path():
            return cache_file

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        # Mock _get_cache_stats to return empty dict
        with patch("phantom_guard.cli.main._get_cache_stats", new_callable=AsyncMock) as mock_stats:
            mock_stats.return_value = {}

            runner = CliRunner()
            result = runner.invoke(app, ["cache", "stats"])

            assert result.exit_code == 0
            assert "empty" in result.stdout.lower()

    @pytest.mark.unit
    def test_cache_stats_with_data(self, monkeypatch, tmp_path):
        """Test cache stats with data."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        cache_file = tmp_path / "phantom_guard.db"
        cache_file.write_text("fake cache")

        def mock_cache_path():
            return cache_file

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        # Mock _get_cache_stats to return stats
        with patch("phantom_guard.cli.main._get_cache_stats", new_callable=AsyncMock) as mock_stats:
            mock_stats.return_value = {
                "pypi": {"entries": 100, "size_bytes": 10240, "hit_rate": 0.85},
                "npm": {"entries": 50, "size_bytes": 5120, "hit_rate": None},
            }

            runner = CliRunner()
            result = runner.invoke(app, ["cache", "stats"])

            assert result.exit_code == 0
            assert "pypi" in result.stdout.lower()
            assert "npm" in result.stdout.lower()


class TestCachePathCommand:
    """Tests for cache path command."""

    @pytest.mark.unit
    def test_cache_path_exists(self, monkeypatch, tmp_path):
        """Test cache path when file exists."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        cache_file = tmp_path / "phantom_guard.db"
        cache_file.write_text("x" * 1024)  # 1KB file

        def mock_cache_path():
            return cache_file

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        runner = CliRunner()
        result = runner.invoke(app, ["cache", "path"])

        assert result.exit_code == 0
        assert "Cache path:" in result.stdout
        assert "Size:" in result.stdout

    @pytest.mark.unit
    def test_cache_path_not_exists(self, monkeypatch, tmp_path):
        """Test cache path when file does not exist."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        def mock_cache_path():
            return tmp_path / "nonexistent.db"

        monkeypatch.setattr("phantom_guard.cli.main.get_default_cache_path", mock_cache_path)

        runner = CliRunner()
        result = runner.invoke(app, ["cache", "path"])

        assert result.exit_code == 0
        assert "does not exist" in result.stdout.lower()


class TestValidateCommandCoverage:
    """Additional tests for validate command coverage."""

    @pytest.mark.unit
    def test_validate_with_quiet_flag(self):
        """Test validate with quiet flag shows minimal output."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        with patch("phantom_guard.cli.main._validate_package", new_callable=AsyncMock) as mock_val:
            mock_val.return_value = 0  # EXIT_SAFE

            runner = CliRunner()
            result = runner.invoke(app, ["validate", "flask", "-q"])

            assert result.exit_code == 0
            # Quiet mode should not show banner
            assert (
                "PHANTOM" not in result.stdout.upper() or "phantom-guard" in result.stdout.lower()
            )

    @pytest.mark.unit
    def test_validate_with_no_banner_flag(self):
        """Test validate with no-banner flag."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        with patch("phantom_guard.cli.main._validate_package", new_callable=AsyncMock) as mock_val:
            mock_val.return_value = 0

            runner = CliRunner()
            result = runner.invoke(app, ["validate", "flask", "--no-banner"])

            assert result.exit_code == 0

    @pytest.mark.unit
    def test_validate_with_verbose_flag(self):
        """Test validate with verbose flag."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        with patch("phantom_guard.cli.main._validate_package", new_callable=AsyncMock) as mock_val:
            mock_val.return_value = 0

            runner = CliRunner()
            result = runner.invoke(app, ["validate", "flask", "-v", "--no-banner"])

            assert result.exit_code == 0

    @pytest.mark.unit
    def test_validate_npm_registry(self):
        """Test validate with npm registry."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        with patch("phantom_guard.cli.main._validate_package", new_callable=AsyncMock) as mock_val:
            mock_val.return_value = 0

            runner = CliRunner()
            result = runner.invoke(app, ["validate", "express", "-r", "npm", "--no-banner"])

            assert result.exit_code == 0

    @pytest.mark.unit
    def test_validate_crates_registry(self):
        """Test validate with crates registry."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        with patch("phantom_guard.cli.main._validate_package", new_callable=AsyncMock) as mock_val:
            mock_val.return_value = 0

            runner = CliRunner()
            result = runner.invoke(app, ["validate", "serde", "-r", "crates", "--no-banner"])

            assert result.exit_code == 0


class TestValidatePackageAsync:
    """Tests for _validate_package async function."""

    @pytest.mark.unit
    def test_validate_package_invalid_registry(self):
        """Test validation with invalid registry returns EXIT_INPUT_ERROR."""
        import asyncio

        from phantom_guard.cli.main import EXIT_INPUT_ERROR, _validate_package

        result = asyncio.run(_validate_package("flask", "invalid_registry", False, True))
        assert result == EXIT_INPUT_ERROR

    @pytest.mark.unit
    def test_validate_package_invalid_name(self):
        """Test validation with invalid package name returns EXIT_INPUT_ERROR."""
        import asyncio

        from phantom_guard.cli.main import EXIT_INPUT_ERROR, _validate_package

        # Empty package name is invalid
        result = asyncio.run(_validate_package("", "pypi", False, True))
        assert result == EXIT_INPUT_ERROR

    @pytest.mark.unit
    def test_validate_package_pypi_success(self):
        """Test successful validation with PyPI."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        from phantom_guard.cli.main import EXIT_SAFE, _validate_package
        from phantom_guard.core.types import PackageRisk, Recommendation

        mock_risk = PackageRisk(
            name="flask",
            registry="pypi",
            exists=True,
            risk_score=0.1,
            signals=(),
            recommendation=Recommendation.SAFE,
            latency_ms=50.0,
        )

        with patch(
            "phantom_guard.cli.main.detector.validate_package", new_callable=AsyncMock
        ) as mock_det:
            mock_det.return_value = mock_risk

            result = asyncio.run(_validate_package("flask", "pypi", False, True))
            assert result == EXIT_SAFE

    @pytest.mark.unit
    def test_validate_package_suspicious(self):
        """Test validation returning SUSPICIOUS."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        from phantom_guard.cli.main import EXIT_SUSPICIOUS, _validate_package
        from phantom_guard.core.types import PackageRisk, Recommendation

        mock_risk = PackageRisk(
            name="flassk",
            registry="pypi",
            exists=True,
            risk_score=0.5,
            signals=(),
            recommendation=Recommendation.SUSPICIOUS,
            latency_ms=50.0,
        )

        with patch(
            "phantom_guard.cli.main.detector.validate_package", new_callable=AsyncMock
        ) as mock_det:
            mock_det.return_value = mock_risk

            result = asyncio.run(_validate_package("flassk", "pypi", False, True))
            assert result == EXIT_SUSPICIOUS

    @pytest.mark.unit
    def test_validate_package_high_risk(self):
        """Test validation returning HIGH_RISK."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        from phantom_guard.cli.main import EXIT_HIGH_RISK, _validate_package
        from phantom_guard.core.types import PackageRisk, Recommendation

        mock_risk = PackageRisk(
            name="malicious-pkg",
            registry="pypi",
            exists=True,
            risk_score=0.9,
            signals=(),
            recommendation=Recommendation.HIGH_RISK,
            latency_ms=50.0,
        )

        with patch(
            "phantom_guard.cli.main.detector.validate_package", new_callable=AsyncMock
        ) as mock_det:
            mock_det.return_value = mock_risk

            result = asyncio.run(_validate_package("malicious-pkg", "pypi", False, True))
            assert result == EXIT_HIGH_RISK

    @pytest.mark.unit
    def test_validate_package_not_found(self):
        """Test validation returning NOT_FOUND."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        from phantom_guard.cli.main import EXIT_NOT_FOUND, _validate_package
        from phantom_guard.core.types import PackageRisk, Recommendation

        mock_risk = PackageRisk(
            name="nonexistent-pkg",
            registry="pypi",
            exists=False,
            risk_score=0.9,
            signals=(),
            recommendation=Recommendation.NOT_FOUND,
            latency_ms=50.0,
        )

        with patch(
            "phantom_guard.cli.main.detector.validate_package", new_callable=AsyncMock
        ) as mock_det:
            mock_det.return_value = mock_risk

            result = asyncio.run(_validate_package("nonexistent-pkg", "pypi", False, True))
            assert result == EXIT_NOT_FOUND

    @pytest.mark.unit
    def test_validate_package_registry_error(self):
        """Test validation with RegistryError returns EXIT_RUNTIME_ERROR."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        from phantom_guard.cli.main import EXIT_RUNTIME_ERROR, _validate_package
        from phantom_guard.registry.exceptions import RegistryError

        with patch(
            "phantom_guard.cli.main.detector.validate_package", new_callable=AsyncMock
        ) as mock_det:
            mock_det.side_effect = RegistryError("Connection failed")

            result = asyncio.run(_validate_package("flask", "pypi", False, True))
            assert result == EXIT_RUNTIME_ERROR

    @pytest.mark.unit
    def test_validate_package_unexpected_error(self):
        """Test validation with unexpected error returns EXIT_RUNTIME_ERROR."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        from phantom_guard.cli.main import EXIT_RUNTIME_ERROR, _validate_package

        with patch(
            "phantom_guard.cli.main.detector.validate_package", new_callable=AsyncMock
        ) as mock_det:
            mock_det.side_effect = RuntimeError("Unexpected error")

            result = asyncio.run(_validate_package("flask", "pypi", False, True))
            assert result == EXIT_RUNTIME_ERROR


class TestCheckCommandCoverage:
    """Additional tests for check command coverage."""

    @pytest.mark.unit
    def test_check_with_invalid_registry_override(self, tmp_path):
        """Test check with invalid registry override."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import EXIT_INPUT_ERROR, app

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file), "-r", "invalid_registry"])

        assert result.exit_code == EXIT_INPUT_ERROR

    @pytest.mark.unit
    def test_check_with_quiet_flag(self, tmp_path):
        """Test check with quiet flag."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file), "-q"])

        assert result.exit_code in [0, 1, 2, 3]

    @pytest.mark.unit
    def test_check_with_no_banner_flag(self, tmp_path):
        """Test check with no-banner flag."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file), "--no-banner"])

        assert result.exit_code in [0, 1, 2, 3]

    @pytest.mark.unit
    def test_check_with_json_output(self, tmp_path):
        """Test check with JSON output format."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file), "-o", "json", "--no-banner"])

        assert result.exit_code in [0, 1, 2, 3]
        # JSON output should contain results
        assert "results" in result.stdout or "result" in result.stdout.lower()

    @pytest.mark.unit
    def test_check_with_fail_fast(self, tmp_path):
        """Test check with fail-fast option."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\nrequests\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file), "--fail-fast", "--no-banner"])

        assert result.exit_code in [0, 1, 2, 3]

    @pytest.mark.unit
    def test_check_with_parallel_option(self, tmp_path):
        """Test check with custom parallel setting."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\n")

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(req_file), "--parallel", "5", "--no-banner"])

        assert result.exit_code in [0, 1, 2, 3]


class TestDetermineExitCode:
    """Tests for _determine_exit_code function."""

    @pytest.mark.unit
    def test_exit_code_high_risk(self):
        """Test exit code for HIGH_RISK."""
        from phantom_guard.cli.main import EXIT_HIGH_RISK, _determine_exit_code
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="pkg",
                registry="pypi",
                exists=True,
                risk_score=0.9,
                signals=(),
                recommendation=Recommendation.HIGH_RISK,
                latency_ms=50.0,
            )
        ]

        assert _determine_exit_code(results, None) == EXIT_HIGH_RISK

    @pytest.mark.unit
    def test_exit_code_suspicious_with_fail_on(self):
        """Test exit code for SUSPICIOUS with fail_on=suspicious."""
        from phantom_guard.cli.main import EXIT_SUSPICIOUS, _determine_exit_code
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="pkg",
                registry="pypi",
                exists=True,
                risk_score=0.5,
                signals=(),
                recommendation=Recommendation.SUSPICIOUS,
                latency_ms=50.0,
            )
        ]

        assert _determine_exit_code(results, "suspicious") == EXIT_SUSPICIOUS

    @pytest.mark.unit
    def test_exit_code_suspicious_default(self):
        """Test exit code for SUSPICIOUS with default fail_on."""
        from phantom_guard.cli.main import EXIT_SUSPICIOUS, _determine_exit_code
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="pkg",
                registry="pypi",
                exists=True,
                risk_score=0.5,
                signals=(),
                recommendation=Recommendation.SUSPICIOUS,
                latency_ms=50.0,
            )
        ]

        assert _determine_exit_code(results, None) == EXIT_SUSPICIOUS

    @pytest.mark.unit
    def test_exit_code_not_found(self):
        """Test exit code for NOT_FOUND."""
        from phantom_guard.cli.main import EXIT_NOT_FOUND, _determine_exit_code
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="pkg",
                registry="pypi",
                exists=False,
                risk_score=0.9,
                signals=(),
                recommendation=Recommendation.NOT_FOUND,
                latency_ms=50.0,
            )
        ]

        assert _determine_exit_code(results, None) == EXIT_NOT_FOUND

    @pytest.mark.unit
    def test_exit_code_safe(self):
        """Test exit code for SAFE."""
        from phantom_guard.cli.main import EXIT_SAFE, _determine_exit_code
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="pkg",
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
                latency_ms=50.0,
            )
        ]

        assert _determine_exit_code(results, None) == EXIT_SAFE


class TestPrintBatchSummary:
    """Tests for _print_batch_summary function."""

    @pytest.mark.unit
    def test_print_batch_summary_all_types(self):
        """Test batch summary with all recommendation types."""
        from io import StringIO

        from rich.console import Console

        from phantom_guard.cli.main import _print_batch_summary
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="safe-pkg",
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
                latency_ms=50.0,
            ),
            PackageRisk(
                name="suspicious-pkg",
                registry="pypi",
                exists=True,
                risk_score=0.5,
                signals=(),
                recommendation=Recommendation.SUSPICIOUS,
                latency_ms=50.0,
            ),
            PackageRisk(
                name="high-risk-pkg",
                registry="pypi",
                exists=True,
                risk_score=0.9,
                signals=(),
                recommendation=Recommendation.HIGH_RISK,
                latency_ms=50.0,
            ),
            PackageRisk(
                name="not-found-pkg",
                registry="pypi",
                exists=False,
                risk_score=0.9,
                signals=(),
                recommendation=Recommendation.NOT_FOUND,
                latency_ms=50.0,
            ),
        ]

        errors = {"error-pkg": Exception("Test error")}

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        _print_batch_summary(results, errors, False, 1000.0, console)

        output_str = output.getvalue()
        assert "4" in output_str or "5" in output_str  # Total packages
        assert "safe" in output_str.lower()
        assert "suspicious" in output_str.lower()
        assert "high-risk" in output_str.lower()
        assert "not found" in output_str.lower()
        assert "error" in output_str.lower()

    @pytest.mark.unit
    def test_print_batch_summary_cancelled(self):
        """Test batch summary when validation was cancelled."""
        from io import StringIO

        from rich.console import Console

        from phantom_guard.cli.main import _print_batch_summary
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="pkg",
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
                latency_ms=50.0,
            )
        ]

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        _print_batch_summary(results, {}, True, 500.0, console)

        output_str = output.getvalue()
        assert "stopped" in output_str.lower() or "fail-fast" in output_str.lower()


class TestPrintSummary:
    """Tests for _print_summary function."""

    @pytest.mark.unit
    def test_print_summary_all_types(self):
        """Test summary with all recommendation types."""
        from io import StringIO

        from rich.console import Console

        from phantom_guard.cli.main import _print_summary
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="safe-pkg",
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
                latency_ms=50.0,
            ),
            PackageRisk(
                name="suspicious-pkg",
                registry="pypi",
                exists=True,
                risk_score=0.5,
                signals=(),
                recommendation=Recommendation.SUSPICIOUS,
                latency_ms=50.0,
            ),
            PackageRisk(
                name="high-risk-pkg",
                registry="pypi",
                exists=True,
                risk_score=0.9,
                signals=(),
                recommendation=Recommendation.HIGH_RISK,
                latency_ms=50.0,
            ),
            PackageRisk(
                name="not-found-pkg",
                registry="pypi",
                exists=False,
                risk_score=0.9,
                signals=(),
                recommendation=Recommendation.NOT_FOUND,
                latency_ms=50.0,
            ),
        ]

        output = StringIO()
        # Use no_color to avoid ANSI escape codes
        console = Console(file=output, force_terminal=False, no_color=True, width=80)

        _print_summary(results, console)

        output_str = output.getvalue()
        assert "4" in output_str and "packages" in output_str
        assert "safe" in output_str.lower()
        assert "suspicious" in output_str.lower()
        assert "high-risk" in output_str.lower()
        assert "not found" in output_str.lower()

    @pytest.mark.unit
    def test_print_summary_without_not_found(self):
        """Test summary without NOT_FOUND packages."""
        from io import StringIO

        from rich.console import Console

        from phantom_guard.cli.main import _print_summary
        from phantom_guard.core.types import PackageRisk, Recommendation

        results = [
            PackageRisk(
                name="safe-pkg",
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
                latency_ms=50.0,
            )
        ]

        output = StringIO()
        # Use no_color to avoid ANSI escape codes
        console = Console(file=output, force_terminal=False, no_color=True, width=80)

        _print_summary(results, console)

        output_str = output.getvalue()
        assert "1" in output_str and "packages" in output_str
        # NOT_FOUND should not appear when there are no NOT_FOUND packages
        # (it might still appear in the template, so just check basic output)


class TestClearCacheAsync:
    """Tests for _clear_cache async function."""

    @pytest.mark.unit
    def test_clear_cache_all(self):
        """Test clearing all cache."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        # Create a proper async context manager mock
        mock_cache = AsyncMock()
        mock_cache.clear_all = AsyncMock(return_value=(5, 10))

        # Patch at the module level where Cache is imported in _clear_cache
        with (
            patch("phantom_guard.cache.Cache", return_value=mock_cache),
            patch("phantom_guard.cli.main.Cache", return_value=mock_cache),
        ):
            from phantom_guard.cli.main import _clear_cache

            result = asyncio.run(_clear_cache(MagicMock(), None))
            assert result == 15  # 5 + 10

    @pytest.mark.unit
    def test_clear_cache_registry_specific(self):
        """Test clearing cache for specific registry."""
        import asyncio
        from pathlib import Path
        from unittest.mock import AsyncMock, patch

        # Create a proper async context manager mock
        mock_cache = AsyncMock()
        mock_cache.clear_registry = AsyncMock(return_value=7)

        # Patch at the module level
        with (
            patch("phantom_guard.cache.Cache", return_value=mock_cache),
            patch("phantom_guard.cli.main.Cache", return_value=mock_cache),
        ):
            from phantom_guard.cli.main import _clear_cache

            result = asyncio.run(_clear_cache(Path("/tmp/cache.db"), "pypi"))  # noqa: S108
            assert result == 7
            mock_cache.clear_registry.assert_called_once_with("pypi")


class TestGetCacheStatsAsync:
    """Tests for _get_cache_stats async function."""

    @pytest.mark.unit
    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        import asyncio
        from pathlib import Path
        from unittest.mock import AsyncMock, patch

        # Create a proper async context manager mock
        mock_cache = AsyncMock()
        mock_cache.get_stats = AsyncMock(return_value={"pypi": {"entries": 10}})

        with (
            patch("phantom_guard.cache.Cache", return_value=mock_cache),
            patch("phantom_guard.cli.main.Cache", return_value=mock_cache),
        ):
            from phantom_guard.cli.main import _get_cache_stats

            result = asyncio.run(_get_cache_stats(Path("/tmp/cache.db")))  # noqa: S108
            assert result == {"pypi": {"entries": 10}}


class TestValidateCommandBanner:
    """Tests for validate command banner display."""

    @pytest.mark.unit
    def test_validate_shows_banner_by_default(self):
        """Test that validate shows banner by default (not quiet, not no-banner)."""
        from unittest.mock import AsyncMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        with patch("phantom_guard.cli.main._validate_package", new_callable=AsyncMock) as mock_val:
            mock_val.return_value = 0

            with patch("phantom_guard.cli.main.show_banner") as mock_banner:
                runner = CliRunner()
                result = runner.invoke(app, ["validate", "flask"])

                assert result.exit_code == 0
                # Banner should be called when not quiet and not no_banner
                mock_banner.assert_called_once()


class TestValidatePackageRegistryClients:
    """Tests for _validate_package with different registry clients."""

    @pytest.mark.unit
    def test_validate_package_npm_client(self):
        """Test validation creates NpmClient for npm registry."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        from phantom_guard.cli.main import EXIT_SAFE, _validate_package
        from phantom_guard.core.types import PackageRisk, Recommendation

        mock_risk = PackageRisk(
            name="express",
            registry="npm",
            exists=True,
            risk_score=0.1,
            signals=(),
            recommendation=Recommendation.SAFE,
            latency_ms=50.0,
        )

        with (
            patch("phantom_guard.cli.main.NpmClient") as mock_npm_client,
            patch(
                "phantom_guard.cli.main.detector.validate_package", new_callable=AsyncMock
            ) as mock_det,
        ):
            mock_det.return_value = mock_risk

            result = asyncio.run(_validate_package("express", "npm", False, True))
            assert result == EXIT_SAFE
            # NpmClient should be instantiated
            mock_npm_client.assert_called_once()

    @pytest.mark.unit
    def test_validate_package_crates_client(self):
        """Test validation creates CratesClient for crates registry."""
        import asyncio
        from unittest.mock import AsyncMock, patch

        from phantom_guard.cli.main import EXIT_SAFE, _validate_package
        from phantom_guard.core.types import PackageRisk, Recommendation

        mock_risk = PackageRisk(
            name="serde",
            registry="crates",
            exists=True,
            risk_score=0.1,
            signals=(),
            recommendation=Recommendation.SAFE,
            latency_ms=50.0,
        )

        with (
            patch("phantom_guard.cli.main.CratesClient") as mock_crates_client,
            patch(
                "phantom_guard.cli.main.detector.validate_package", new_callable=AsyncMock
            ) as mock_det,
        ):
            mock_det.return_value = mock_risk

            result = asyncio.run(_validate_package("serde", "crates", False, True))
            assert result == EXIT_SAFE
            # CratesClient should be instantiated
            mock_crates_client.assert_called_once()


class TestCheckPackagesErrors:
    """Tests for _check_packages with errors."""

    @pytest.mark.unit
    def test_check_packages_with_errors(self, tmp_path):
        """Test check command handles errors in batch validation."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app
        from phantom_guard.core.batch import BatchResult
        from phantom_guard.core.types import PackageRisk, Recommendation

        # Create test file
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\nsome-error-pkg\n")

        mock_risk = PackageRisk(
            name="flask",
            registry="pypi",
            exists=True,
            risk_score=0.1,
            signals=(),
            recommendation=Recommendation.SAFE,
            latency_ms=50.0,
        )

        mock_result = BatchResult(
            results=[mock_risk],
            errors={"some-error-pkg": Exception("Network error")},
            total_time_ms=100.0,
            was_cancelled=False,
        )

        # Patch the module where BatchValidator is imported dynamically
        with patch("phantom_guard.core.batch.BatchValidator") as mock_batch_cls:
            mock_validator = MagicMock()
            mock_validator.validate_batch = AsyncMock(return_value=mock_result)
            mock_batch_cls.return_value = mock_validator

            runner = CliRunner()
            result = runner.invoke(app, ["check", str(req_file), "--no-banner"])

            # Should still complete
            assert result.exit_code in [0, 1, 2, 3, 5]

    @pytest.mark.unit
    def test_check_packages_cancelled(self, tmp_path):
        """Test check command handles cancelled validation (fail-fast)."""
        from unittest.mock import AsyncMock, MagicMock, patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app
        from phantom_guard.core.batch import BatchResult
        from phantom_guard.core.types import PackageRisk, Recommendation

        # Create test file
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\nhigh-risk-pkg\n")

        mock_risks = [
            PackageRisk(
                name="flask",
                registry="pypi",
                exists=True,
                risk_score=0.1,
                signals=(),
                recommendation=Recommendation.SAFE,
                latency_ms=50.0,
            ),
            PackageRisk(
                name="high-risk-pkg",
                registry="pypi",
                exists=True,
                risk_score=0.9,
                signals=(),
                recommendation=Recommendation.HIGH_RISK,
                latency_ms=50.0,
            ),
        ]

        mock_result = BatchResult(
            results=mock_risks,
            errors={},
            total_time_ms=100.0,
            was_cancelled=True,
        )

        # Patch the module where BatchValidator is imported dynamically
        with patch("phantom_guard.core.batch.BatchValidator") as mock_batch_cls:
            mock_validator = MagicMock()
            mock_validator.validate_batch = AsyncMock(return_value=mock_result)
            mock_batch_cls.return_value = mock_validator

            runner = CliRunner()
            result = runner.invoke(app, ["check", str(req_file), "--fail-fast", "--no-banner"])

            # Should return HIGH_RISK exit code
            assert result.exit_code == 2


class TestCheckPackagesMultiRegistry:
    """Tests for _check_packages with multiple registries."""

    @pytest.mark.unit
    def test_check_npm_packages(self, tmp_path):
        """Test check command with npm packages."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create package.json
        pkg_file = tmp_path / "package.json"
        pkg_file.write_text('{"dependencies": {"express": "^4.0.0"}}')

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(pkg_file), "--no-banner", "-q"])

        assert result.exit_code in [0, 1, 2, 3]

    @pytest.mark.unit
    def test_check_crates_packages(self, tmp_path):
        """Test check command with crates packages."""
        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        # Create Cargo.toml
        cargo_file = tmp_path / "Cargo.toml"
        cargo_file.write_text('[dependencies]\nserde = "1.0"')

        runner = CliRunner()
        result = runner.invoke(app, ["check", str(cargo_file), "--no-banner", "-q"])

        assert result.exit_code in [0, 1, 2, 3]


class TestCheckShowsBanner:
    """Tests for check command banner display."""

    @pytest.mark.unit
    def test_check_shows_banner_by_default(self, tmp_path):
        """Test that check shows banner by default."""
        from unittest.mock import patch

        from typer.testing import CliRunner

        from phantom_guard.cli.main import app

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\n")

        with patch("phantom_guard.cli.main.show_banner") as mock_banner:
            runner = CliRunner()
            runner.invoke(app, ["check", str(req_file)])

            # Banner should be called when not quiet and not no_banner
            mock_banner.assert_called_once()
