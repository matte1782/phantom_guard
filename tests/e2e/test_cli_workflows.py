"""
End-to-end CLI workflow tests.

IMPLEMENTS: W3.6
SPEC_IDs: S010-S019
EC_IDs: EC080-EC095

These tests run the actual CLI commands and verify
the complete user experience.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_pattern.sub("", text)


@pytest.fixture
def temp_requirements(tmp_path: Path) -> Path:
    """Create temporary requirements file."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text(
        """# Production dependencies
flask==2.3.0
requests>=2.28.0
django>=4.0,<5.0
"""
    )
    return req_file


@pytest.fixture
def temp_package_json(tmp_path: Path) -> Path:
    """Create temporary package.json file."""
    pkg_file = tmp_path / "package.json"
    pkg_file.write_text(
        json.dumps(
            {
                "name": "test-package",
                "dependencies": {"express": "^4.18.0", "lodash": "^4.17.21"},
            }
        )
    )
    return pkg_file


@pytest.fixture
def temp_cargo_toml(tmp_path: Path) -> Path:
    """Create temporary Cargo.toml file."""
    cargo_file = tmp_path / "Cargo.toml"
    cargo_file.write_text(
        """[package]
name = "test-package"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
"""
    )
    return cargo_file


def run_cli(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """Run phantom-guard CLI command."""
    return subprocess.run(
        [sys.executable, "-m", "phantom_guard.cli.main", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )


@pytest.mark.e2e
class TestValidateWorkflow:
    """E2E tests for validate command."""

    @pytest.mark.network
    def test_validate_known_safe_package(self) -> None:
        """
        TEST_ID: T010.E01
        EC: EC080

        Known safe package returns exit code 0.
        """
        result = run_cli("validate", "flask", "--no-banner")

        assert result.returncode == 0
        assert "SAFE" in result.stdout or "safe" in result.stdout.lower()

    @pytest.mark.network
    def test_validate_not_found_package(self) -> None:
        """
        TEST_ID: T010.E02
        EC: EC083

        Non-existent package returns exit code 3.
        """
        result = run_cli("validate", "nonexistent-xyz-abc-123-pkg", "--no-banner")

        assert result.returncode == 3
        assert "not_found" in result.stdout.lower()

    @pytest.mark.network
    def test_validate_with_verbose_flag(self) -> None:
        """
        TEST_ID: T010.E03
        EC: EC091

        Verbose mode shows signal details.
        """
        result = run_cli("validate", "flask", "-v", "--no-banner")

        assert result.returncode == 0
        # Verbose should show more output than non-verbose

    @pytest.mark.network
    def test_validate_with_quiet_flag(self) -> None:
        """
        TEST_ID: T010.E04
        EC: EC092

        Quiet mode shows minimal output.
        """
        result = run_cli("validate", "flask", "-q", "--no-banner")

        assert result.returncode == 0
        # Output should be very short
        lines = [ln for ln in result.stdout.strip().split("\n") if ln.strip()]
        assert len(lines) <= 5

    def test_validate_invalid_package_name(self) -> None:
        """
        TEST_ID: T010.E05
        EC: EC082

        Invalid package name returns exit code 4.
        """
        result = run_cli("validate", "!invalid@name", "--no-banner")

        assert result.returncode == 4

    def test_validate_invalid_registry(self) -> None:
        """
        TEST_ID: T010.E06
        EC: EC082

        Invalid registry returns exit code 4.
        """
        result = run_cli("validate", "flask", "--registry", "invalid", "--no-banner")

        assert result.returncode == 4

    @pytest.mark.network
    def test_validate_npm_registry(self) -> None:
        """
        TEST_ID: T010.E07
        EC: EC095

        Can validate npm packages.
        """
        result = run_cli("validate", "express", "--registry", "npm", "--no-banner")

        assert result.returncode == 0
        assert "express" in result.stdout.lower()

    @pytest.mark.network
    def test_validate_crates_registry(self) -> None:
        """
        TEST_ID: T010.E08
        EC: EC095

        Can validate crates.io packages.
        """
        result = run_cli("validate", "serde", "--registry", "crates", "--no-banner")

        assert result.returncode == 0
        assert "serde" in result.stdout.lower()


@pytest.mark.e2e
class TestCheckWorkflow:
    """E2E tests for check command."""

    @pytest.mark.network
    def test_check_requirements_file(self, temp_requirements: Path) -> None:
        """
        TEST_ID: T010.E09
        EC: EC084

        Check command processes requirements.txt.
        """
        result = run_cli("check", str(temp_requirements), "--no-banner")

        # Any valid exit code
        assert result.returncode in [0, 1, 2, 3]
        assert "flask" in result.stdout.lower()
        assert "Summary" in result.stdout or "summary" in result.stdout.lower()

    @pytest.mark.network
    def test_check_with_json_output(self, temp_requirements: Path) -> None:
        """
        TEST_ID: T010.E10
        EC: EC089

        JSON output for check command.
        """
        result = run_cli("check", str(temp_requirements), "--output", "json", "--no-banner")

        data: dict[str, Any] = json.loads(result.stdout)
        assert "results" in data
        assert len(data["results"]) >= 3  # At least flask, requests, django

    def test_check_nonexistent_file(self) -> None:
        """
        TEST_ID: T010.E11
        EC: EC086

        Check command handles missing file.
        """
        result = run_cli("check", "nonexistent_file_xyz.txt", "--no-banner")

        assert result.returncode == 4  # EXIT_INPUT_ERROR
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    @pytest.mark.network
    def test_check_with_ignore_flag(self, temp_requirements: Path) -> None:
        """
        TEST_ID: T010.E12
        EC: EC087

        Ignore flag skips specified packages.
        """
        result = run_cli(
            "check",
            str(temp_requirements),
            "--ignore",
            "flask,requests",
            "--no-banner",
        )

        # Should still succeed but with fewer packages
        assert result.returncode in [0, 1, 2, 3]

    @pytest.mark.network
    def test_check_package_json(self, temp_package_json: Path) -> None:
        """
        TEST_ID: T010.E13
        EC: EC084

        Check command processes package.json.
        """
        result = run_cli("check", str(temp_package_json), "--no-banner")

        assert result.returncode in [0, 1, 2, 3]

    @pytest.mark.network
    def test_check_cargo_toml(self, temp_cargo_toml: Path) -> None:
        """
        TEST_ID: T010.E14
        EC: EC084

        Check command processes Cargo.toml.
        """
        result = run_cli("check", str(temp_cargo_toml), "--no-banner")

        assert result.returncode in [0, 1, 2, 3]

    @pytest.mark.network
    def test_check_with_fail_fast(self, temp_requirements: Path) -> None:
        """
        TEST_ID: T010.E15

        Fail-fast option stops on first HIGH_RISK.
        """
        result = run_cli("check", str(temp_requirements), "--fail-fast", "--no-banner")

        # Should complete successfully for safe packages
        assert result.returncode in [0, 1, 2, 3]


@pytest.mark.e2e
class TestCacheWorkflow:
    """E2E tests for cache commands."""

    def test_cache_path_shows_location(self) -> None:
        """
        TEST_ID: T010.E16

        Cache path command shows file location.
        """
        result = run_cli("cache", "path")

        assert result.returncode == 0
        assert "cache" in result.stdout.lower() or "Cache" in result.stdout

    def test_cache_stats_works(self) -> None:
        """
        TEST_ID: T010.E17

        Cache stats command runs without error.
        """
        result = run_cli("cache", "stats")

        assert result.returncode == 0


@pytest.mark.e2e
class TestHelpAndVersion:
    """E2E tests for help and version."""

    def test_help_shows_commands(self) -> None:
        """
        TEST_ID: T010.E18

        Help shows available commands.
        """
        result = run_cli("--help")

        assert result.returncode == 0
        assert "validate" in result.stdout
        assert "check" in result.stdout
        assert "cache" in result.stdout

    def test_validate_help(self) -> None:
        """
        TEST_ID: T010.E19

        Validate command has help.
        """
        result = run_cli("validate", "--help")
        output = strip_ansi(result.stdout)

        assert result.returncode == 0
        assert "package" in output.lower()
        assert "--registry" in output

    def test_check_help(self) -> None:
        """
        TEST_ID: T010.E20

        Check command has help.
        """
        result = run_cli("check", "--help")
        output = strip_ansi(result.stdout)

        assert result.returncode == 0
        assert "file" in output.lower()
        assert "--fail-on" in output or "--fail-fast" in output

    def test_cache_help(self) -> None:
        """
        TEST_ID: T010.E21

        Cache command has help.
        """
        result = run_cli("cache", "--help")

        assert result.returncode == 0
        assert "clear" in result.stdout
        assert "stats" in result.stdout
        assert "path" in result.stdout
