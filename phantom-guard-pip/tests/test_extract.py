"""
Tests for package extraction.

SPEC: S202
TESTS: T202.01-T202.06, T202.R01-R05
"""

import pytest
from pathlib import Path
from phantom_pip.extract import (
    extract_package,
    extract_packages,
    extract_from_requirements_file,
    get_package_names,
    validate_package_name,
    ExtractedPackage,
)
from phantom_pip.parser import parse_pip_args


class TestT202_Extraction:
    """T202: Package extraction tests."""

    def test_T202_01_simple_package(self) -> None:
        """T202.01: Extract simple package name."""
        pkg = extract_package("flask")
        assert pkg is not None
        assert pkg.name == "flask"
        assert pkg.full_spec == "flask"
        assert pkg.extras == []
        assert pkg.version_spec is None

    def test_T202_02_versioned_package(self) -> None:
        """T202.02: Extract package with version."""
        pkg = extract_package("flask>=2.0.0")
        assert pkg is not None
        assert pkg.name == "flask"
        assert pkg.full_spec == "flask>=2.0.0"
        assert pkg.version_spec == ">=2.0.0"

    def test_T202_03_package_with_extras(self) -> None:
        """T202.03: Extract package with extras."""
        pkg = extract_package("flask[async,dotenv]")
        assert pkg is not None
        assert pkg.name == "flask"
        assert pkg.extras == ["async", "dotenv"]

    def test_T202_04_complex_spec(self) -> None:
        """T202.04: Extract complex package specification."""
        pkg = extract_package("requests[security]>=2.28.0")
        assert pkg is not None
        assert pkg.name == "requests"
        assert pkg.extras == ["security"]
        assert pkg.version_spec == ">=2.28.0"

    def test_T202_05_from_parsed_args(self) -> None:
        """T202.05: Extract from ParsedArgs."""
        parsed = parse_pip_args(["install", "flask", "requests>=2.0", "django[async]"])
        packages = extract_packages(parsed)
        names = get_package_names(packages)
        assert "flask" in names
        assert "requests" in names
        assert "django" in names

    def test_T202_06_skip_urls(self) -> None:
        """T202.06: Skip URL packages."""
        pkg = extract_package("git+https://github.com/user/repo.git")
        assert pkg is None


class TestT202_RequirementsFile:
    """T202: Requirements file extraction tests."""

    def test_T202_R01_simple_file(self, tmp_path: Path) -> None:
        """T202.R01: Extract from simple requirements.txt."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask\nrequests>=2.0\ndjango")

        packages = extract_from_requirements_file(str(req_file))
        names = [p.name for p in packages]

        assert "flask" in names
        assert "requests" in names
        assert "django" in names

    def test_T202_R02_with_comments(self, tmp_path: Path) -> None:
        """T202.R02: Handle comments in requirements.txt."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("""
# This is a comment
flask  # web framework
requests>=2.0
# Another comment
django
""")

        packages = extract_from_requirements_file(str(req_file))
        names = [p.name for p in packages]

        assert len(names) == 3
        assert "flask" in names

    def test_T202_R03_skip_flags(self, tmp_path: Path) -> None:
        """T202.R03: Skip -r, -e flags in requirements.txt."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("""
flask
-r other-requirements.txt
-e ./local-package
requests
--index-url https://pypi.org/simple
django
""")

        packages = extract_from_requirements_file(str(req_file))
        names = [p.name for p in packages]

        assert len(names) == 3
        assert "flask" in names
        assert "requests" in names
        assert "django" in names

    def test_T202_R04_missing_file(self) -> None:
        """T202.R04: Handle missing requirements file."""
        packages = extract_from_requirements_file("/nonexistent/requirements.txt")
        assert packages == []

    def test_T202_R05_environment_markers(self, tmp_path: Path) -> None:
        """T202.R05: Handle environment markers."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("""
flask
pywin32; sys_platform == 'win32'
requests; python_version >= '3.8'
""")

        packages = extract_from_requirements_file(str(req_file))
        names = [p.name for p in packages]

        assert "flask" in names
        assert "pywin32" in names
        assert "requests" in names


class TestT202_Security:
    """T202: Security tests for package validation."""

    def test_T202_S01_semicolon_injection(self) -> None:
        """T202.S01: Reject package names with semicolon."""
        assert validate_package_name("flask; rm -rf /") is False

    def test_T202_S02_pipe_injection(self) -> None:
        """T202.S02: Reject package names with pipe."""
        assert validate_package_name("flask | cat /etc/passwd") is False

    def test_T202_S03_backtick_injection(self) -> None:
        """T202.S03: Reject package names with backticks."""
        assert validate_package_name("flask`whoami`") is False

    def test_T202_S04_dollar_injection(self) -> None:
        """T202.S04: Reject package names with dollar."""
        assert validate_package_name("flask$HOME") is False

    def test_T202_S05_ampersand_injection(self) -> None:
        """T202.S05: Reject package names with ampersand."""
        assert validate_package_name("flask && rm -rf /") is False


class TestT202_ValidPackages:
    """T202: Valid package name acceptance tests."""

    def test_T202_V01_simple_name(self) -> None:
        """T202.V01: Accept simple package names."""
        assert validate_package_name("flask") is True

    def test_T202_V02_scoped_name(self) -> None:
        """T202.V02: Accept scoped package names."""
        assert validate_package_name("@scope/package") is True

    def test_T202_V03_hyphen_underscore(self) -> None:
        """T202.V03: Accept hyphens and underscores."""
        assert validate_package_name("my-package_name") is True

    def test_T202_V04_numbers(self) -> None:
        """T202.V04: Accept numbers."""
        assert validate_package_name("package123") is True

    def test_T202_V05_version_specifier(self) -> None:
        """T202.V05: Accept version specifiers."""
        assert validate_package_name("flask>=2.0.0") is True
        assert validate_package_name("requests==2.28.0") is True

    def test_T202_V06_empty_rejected(self) -> None:
        """T202.V06: Reject empty package names."""
        assert validate_package_name("") is False
