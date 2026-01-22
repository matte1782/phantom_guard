"""
Tests for pip argument parser.

SPEC: S201
TESTS: T201.01-T201.10
"""

import pytest
from phantom_pip.parser import parse_pip_args, ParsedArgs, is_validatable_package


class TestT201_ArgumentParser:
    """T201: pip argument parsing tests."""

    def test_T201_01_simple_install(self) -> None:
        """T201.01: Parse 'pip install flask'."""
        result = parse_pip_args(["install", "flask"])
        assert result.command == "install"
        assert result.packages == ["flask"]
        assert result.raw_args == ["install", "flask"]

    def test_T201_02_multiple_packages(self) -> None:
        """T201.02: Parse 'pip install flask requests django'."""
        result = parse_pip_args(["install", "flask", "requests", "django"])
        assert result.packages == ["flask", "requests", "django"]

    def test_T201_03_version_specifiers(self) -> None:
        """T201.03: Parse 'pip install flask>=2.0 requests==2.28.0'."""
        result = parse_pip_args(["install", "flask>=2.0", "requests==2.28.0"])
        assert "flask>=2.0" in result.packages
        assert "requests==2.28.0" in result.packages

    def test_T201_04_requirements_file(self) -> None:
        """T201.04: Parse 'pip install -r requirements.txt'."""
        result = parse_pip_args(["install", "-r", "requirements.txt"])
        assert result.requirements_files == ["requirements.txt"]
        assert result.packages == []

    def test_T201_04b_requirements_equals(self) -> None:
        """T201.04b: Parse 'pip install --requirement=requirements.txt'."""
        result = parse_pip_args(["install", "--requirement=requirements.txt"])
        assert result.requirements_files == ["requirements.txt"]

    def test_T201_05_editable_install(self) -> None:
        """T201.05: Parse 'pip install -e .'."""
        result = parse_pip_args(["install", "-e", "."])
        assert result.editable == ["."]
        assert result.packages == []

    def test_T201_05b_editable_path(self) -> None:
        """T201.05b: Parse 'pip install -e ./mypackage'."""
        result = parse_pip_args(["install", "-e", "./mypackage"])
        assert result.editable == ["./mypackage"]

    def test_T201_06_extras(self) -> None:
        """T201.06: Parse 'pip install flask[async]'."""
        result = parse_pip_args(["install", "flask[async]"])
        assert "flask[async]" in result.packages

    def test_T201_06b_multiple_extras(self) -> None:
        """T201.06b: Parse 'pip install flask[async,dotenv]'."""
        result = parse_pip_args(["install", "flask[async,dotenv]"])
        assert "flask[async,dotenv]" in result.packages

    def test_T201_07_url_install(self) -> None:
        """T201.07: Parse 'pip install git+https://...'."""
        result = parse_pip_args(["install", "git+https://github.com/user/repo.git"])
        # URL installs should be in options, not packages
        assert result.packages == []
        assert "git+https://github.com/user/repo.git" in result.options

    def test_T201_07b_http_url(self) -> None:
        """T201.07b: Parse 'pip install https://...'."""
        result = parse_pip_args(["install", "https://example.com/pkg.whl"])
        assert result.packages == []

    def test_T201_08_preserves_raw_args(self) -> None:
        """T201.08: INV200 - Raw args preserved for passthrough."""
        args = ["install", "flask", "--upgrade", "--no-cache-dir"]
        result = parse_pip_args(args)
        assert result.raw_args == args

    def test_T201_09_mixed_args(self) -> None:
        """T201.09: Parse complex mixed arguments."""
        result = parse_pip_args([
            "install", "flask", "requests>=2.0",
            "-r", "requirements.txt",
            "-e", "./local",
            "--upgrade",
            "django[async]",
        ])
        assert "flask" in result.packages
        assert "requests>=2.0" in result.packages
        assert "django[async]" in result.packages
        assert "requirements.txt" in result.requirements_files
        assert "./local" in result.editable
        assert "--upgrade" in result.options

    def test_T201_10_local_wheel(self) -> None:
        """T201.10: Parse 'pip install ./package.whl'."""
        result = parse_pip_args(["install", "./package-1.0.0-py3-none-any.whl"])
        assert result.packages == []  # Local wheel not validatable

    def test_T201_11_empty_args(self) -> None:
        """T201.11: Handle empty arguments."""
        result = parse_pip_args([])
        assert result.command == ""
        assert result.packages == []

    def test_T201_12_constraint_file(self) -> None:
        """T201.12: Parse constraint file."""
        result = parse_pip_args(["install", "-c", "constraints.txt", "flask"])
        assert result.constraints_files == ["constraints.txt"]
        assert "flask" in result.packages


class TestT201_ValidatablePackage:
    """T201: is_validatable_package tests."""

    def test_validatable_simple(self) -> None:
        """Simple package names are validatable."""
        assert is_validatable_package("flask") is True
        assert is_validatable_package("requests") is True

    def test_validatable_with_version(self) -> None:
        """Package with version is validatable."""
        assert is_validatable_package("flask>=2.0") is True

    def test_not_validatable_url(self) -> None:
        """URLs are not validatable."""
        assert is_validatable_package("git+https://github.com/user/repo") is False
        assert is_validatable_package("https://example.com/pkg.whl") is False

    def test_not_validatable_path(self) -> None:
        """Paths are not validatable."""
        assert is_validatable_package("./local") is False
        assert is_validatable_package("/absolute/path") is False
        assert is_validatable_package("../relative") is False

    def test_not_validatable_wheel(self) -> None:
        """Wheel files are not validatable."""
        assert is_validatable_package("package.whl") is False
