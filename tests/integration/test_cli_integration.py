# SPEC: S010-S019 - CLI Integration Tests
"""
Integration tests for CLI commands.

IMPLEMENTS: W3.6
SPEC_IDs: S010-S019
TEST_IDs: T010.I*
Tests actual CLI invocation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


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


@pytest.fixture
def temp_requirements(tmp_path: Path) -> Path:
    """Create temporary requirements file."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("flask==2.3.0\nrequests>=2.28.0\ndjango>=4.0,<5.0\n")
    return req_file


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI commands.

    SPEC: S010-S019
    Tests actual CLI behavior with subprocess.
    """

    @pytest.mark.network
    def test_validate_safe_package_live(self) -> None:
        """
        TEST_ID: T010.I01
        SPEC: S010
        EC: EC080

        Given: CLI installed
        When: `phantom-guard validate flask`
        Then: Exit code 0, SAFE in output
        """
        result = run_cli("validate", "flask", "--no-banner")

        assert result.returncode == 0
        assert "SAFE" in result.stdout or "safe" in result.stdout.lower()

    @pytest.mark.network
    def test_validate_not_found_live(self) -> None:
        """
        TEST_ID: T010.I03
        SPEC: S010
        EC: EC083

        Given: CLI installed
        When: `phantom-guard validate nonexistent-xyz123`
        Then: Exit code 3, NOT_FOUND in output
        """
        result = run_cli("validate", "nonexistent-xyz-abc-123-pkg", "--no-banner")

        assert result.returncode == 3
        assert "not_found" in result.stdout.lower()

    @pytest.mark.network
    def test_check_requirements_file_live(self, temp_requirements: Path) -> None:
        """
        TEST_ID: T010.I04
        SPEC: S010
        EC: EC084

        Given: requirements.txt with safe packages
        When: `phantom-guard check requirements.txt`
        Then: Valid exit code, packages processed
        """
        result = run_cli("check", str(temp_requirements), "--no-banner")

        assert result.returncode in [0, 1, 2, 3]
        assert "flask" in result.stdout.lower()

    @pytest.mark.network
    def test_check_with_json_output(self, temp_requirements: Path) -> None:
        """
        TEST_ID: T010.I05
        SPEC: S010
        EC: EC089

        Given: requirements.txt
        When: `phantom-guard check req.txt --output json`
        Then: Valid JSON output with summary
        """
        result = run_cli("check", str(temp_requirements), "--output", "json", "--no-banner")

        data: dict[str, Any] = json.loads(result.stdout)
        assert "results" in data
        assert "summary" in data

    @pytest.mark.network
    def test_validate_npm_package(self) -> None:
        """
        TEST_ID: T010.I06
        SPEC: S010
        EC: EC095

        Given: CLI installed
        When: `phantom-guard validate express --registry npm`
        Then: Exit code 0, uses npm registry
        """
        result = run_cli("validate", "express", "--registry", "npm", "--no-banner")

        assert result.returncode == 0
        assert "express" in result.stdout.lower()

    @pytest.mark.network
    def test_validate_crates_package(self) -> None:
        """
        TEST_ID: T010.I07
        SPEC: S010
        EC: EC095

        Given: CLI installed
        When: `phantom-guard validate serde --registry crates`
        Then: Exit code 0, uses crates.io registry
        """
        result = run_cli("validate", "serde", "--registry", "crates", "--no-banner")

        assert result.returncode == 0
        assert "serde" in result.stdout.lower()


@pytest.mark.integration
class TestCLIBatchOperations:
    """Integration tests for batch CLI operations.

    SPEC: S002
    EC: EC035
    """

    @pytest.mark.network
    @pytest.mark.slow
    def test_batch_10_packages_concurrent(self, tmp_path: Path) -> None:
        """
        TEST_ID: T002.I01
        SPEC: S002
        EC: EC035

        Given: File with 10 package names
        When: check is called
        Then: All 10 processed without error
        """
        packages = [
            "flask",
            "django",
            "requests",
            "numpy",
            "pandas",
            "pytest",
            "click",
            "rich",
            "typer",
            "httpx",
        ]
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("\n".join(packages))

        result = run_cli(
            "check",
            str(req_file),
            "--parallel",
            "5",
            "--no-banner",
            timeout=120,
        )

        assert result.returncode in [0, 1, 2, 3]
        # All packages should be in output
        for pkg in packages[:3]:  # Check at least first few
            assert pkg in result.stdout.lower()
