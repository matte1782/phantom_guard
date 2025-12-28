"""
Unit tests for dependency file parsers.

SPEC: S010 (CLI Interface)
MODULE: phantom_guard.cli.parsers
"""

import json
import pytest
from pathlib import Path

from phantom_guard.cli.parsers import (
    parse_requirements_txt,
    parse_package_json,
    parse_cargo_toml,
    detect_and_parse,
    ParserError,
    ParsedPackage,
)


# ============================================================================
# Requirements.txt Parser Tests
# ============================================================================


def test_parse_requirements_simple():
    """
    TEST_ID: T010.13
    SPEC: S010

    Test parsing simple package names from requirements.txt.
    Should extract clean package names without versions.
    """
    content = "flask\ndjango\nrequests\n"

    packages = parse_requirements_txt(content)

    assert len(packages) == 3
    assert packages[0].name == "flask"
    assert packages[0].registry == "pypi"
    assert packages[1].name == "django"
    assert packages[2].name == "requests"


def test_parse_requirements_versioned():
    """
    TEST_ID: T010.14
    SPEC: S010

    Test parsing packages with version specifications.
    Should extract package name, discarding version specs (==, >=, <, etc).
    """
    content = """
flask==2.0.1
django>=3.2,<4.0
requests>=2.25.0
numpy~=1.21.0
    """.strip()

    packages = parse_requirements_txt(content)

    assert len(packages) == 4
    assert packages[0].name == "flask"
    assert packages[1].name == "django"
    assert packages[2].name == "requests"
    assert packages[3].name == "numpy"


def test_parse_requirements_with_comments():
    """
    SPEC: S010
    TEST_ID: T010.13.1

    Test handling of comments in requirements.txt.
    Should skip full-line comments and inline comments.
    """
    content = """
# Core dependencies
flask==2.0.1
django  # Web framework
# requests
pytest  # Testing framework
    """.strip()

    packages = parse_requirements_txt(content)

    assert len(packages) == 3
    assert packages[0].name == "flask"
    assert packages[1].name == "django"
    assert packages[2].name == "pytest"


def test_parse_requirements_with_extras():
    """
    SPEC: S010
    TEST_ID: T010.13.2

    Test handling of package extras (e.g., flask[async]).
    Should extract base package name without extras.
    """
    content = """
flask[async]
requests[security,socks]
celery[redis]==5.0.0
    """.strip()

    packages = parse_requirements_txt(content)

    assert len(packages) == 3
    assert packages[0].name == "flask"
    assert packages[1].name == "requests"
    assert packages[2].name == "celery"


def test_parse_requirements_skip_urls():
    """
    SPEC: S010
    TEST_ID: T010.13.3

    Test skipping URL-based dependencies.
    Should ignore -e editable installs, git+, http URLs.
    """
    content = """
flask==2.0.1
-e git+https://github.com/user/repo.git#egg=package
git+https://github.com/user/repo2.git
https://example.com/package.tar.gz
django>=3.2
    """.strip()

    packages = parse_requirements_txt(content)

    # Should only get flask and django, URLs should be skipped
    assert len(packages) == 2
    assert packages[0].name == "flask"
    assert packages[1].name == "django"


def test_parse_requirements_empty_lines():
    """
    SPEC: S010
    TEST_ID: T010.13.4

    Test handling of blank lines and whitespace.
    Should skip empty lines and strip whitespace.
    """
    content = """

flask==2.0.1

django>=3.2

requests

    """.strip()

    packages = parse_requirements_txt(content)

    assert len(packages) == 3
    assert packages[0].name == "flask"
    assert packages[1].name == "django"
    assert packages[2].name == "requests"


# ============================================================================
# package.json Parser Tests
# ============================================================================


def test_parse_package_json():
    """
    TEST_ID: T010.15
    SPEC: S010

    Test parsing basic dependencies from package.json.
    Should extract package names from dependencies section.
    """
    content = json.dumps({
        "name": "my-app",
        "dependencies": {
            "express": "^4.17.1",
            "lodash": "~4.17.21",
            "axios": "0.21.1"
        }
    })

    packages = parse_package_json(content)

    assert len(packages) == 3
    assert packages[0].name == "express"
    assert packages[0].registry == "npm"
    assert packages[1].name == "lodash"
    assert packages[2].name == "axios"


def test_parse_package_json_scoped():
    """
    SPEC: S010
    TEST_ID: T010.15.1

    Test handling of scoped packages (@org/package).
    Should preserve scope in package name.
    """
    content = json.dumps({
        "dependencies": {
            "@types/node": "^16.0.0",
            "@babel/core": "^7.15.0",
            "express": "^4.17.1"
        }
    })

    packages = parse_package_json(content)

    assert len(packages) == 3
    assert packages[0].name == "@types/node"
    assert packages[1].name == "@babel/core"
    assert packages[2].name == "express"


def test_parse_package_json_dev_deps():
    """
    SPEC: S010
    TEST_ID: T010.15.2

    Test inclusion of devDependencies.
    Should extract from both dependencies and devDependencies.
    """
    content = json.dumps({
        "dependencies": {
            "express": "^4.17.1"
        },
        "devDependencies": {
            "jest": "^27.0.0",
            "eslint": "^7.32.0"
        }
    })

    packages = parse_package_json(content)

    assert len(packages) == 3
    names = {pkg.name for pkg in packages}
    assert names == {"express", "jest", "eslint"}


def test_parse_package_json_invalid():
    """
    SPEC: S010
    TEST_ID: T010.15.3

    Test error handling for invalid JSON.
    Should raise ParserError on malformed JSON.
    """
    content = "{ invalid json }"

    with pytest.raises(ParserError) as exc_info:
        parse_package_json(content)

    assert "Failed to parse package.json" in str(exc_info.value)


# ============================================================================
# Cargo.toml Parser Tests
# ============================================================================


def test_parse_cargo_toml():
    """
    TEST_ID: T010.16
    SPEC: S010

    Test parsing basic dependencies from Cargo.toml.
    Should extract package names from dependencies section.
    """
    content = """
[package]
name = "my-crate"

[dependencies]
serde = "1.0"
tokio = "1.15"
reqwest = "0.11"
    """

    packages = parse_cargo_toml(content)

    assert len(packages) == 3
    assert packages[0].name == "serde"
    assert packages[0].registry == "crates"
    assert packages[1].name == "tokio"
    assert packages[2].name == "reqwest"


def test_parse_cargo_toml_complex():
    """
    SPEC: S010
    TEST_ID: T010.16.1

    Test handling of complex dependency specifications.
    Should extract package name from { version = "...", features = [...] } syntax.
    """
    content = """
[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.15", features = ["full"], default-features = false }
reqwest = "0.11"
    """

    packages = parse_cargo_toml(content)

    assert len(packages) == 3
    assert packages[0].name == "serde"
    assert packages[1].name == "tokio"
    assert packages[2].name == "reqwest"


def test_parse_cargo_toml_dev():
    """
    SPEC: S010
    TEST_ID: T010.16.2

    Test inclusion of dev-dependencies.
    Should extract from both dependencies and dev-dependencies.
    """
    content = """
[dependencies]
serde = "1.0"

[dev-dependencies]
criterion = "0.3"
mockall = "0.11"
    """

    packages = parse_cargo_toml(content)

    assert len(packages) == 3
    names = {pkg.name for pkg in packages}
    assert names == {"serde", "criterion", "mockall"}


def test_parse_cargo_toml_invalid():
    """
    SPEC: S010
    TEST_ID: T010.16.3

    Test error handling for invalid TOML.
    Should raise ParserError on malformed TOML.
    """
    content = """
[dependencies
serde = "1.0"
    """

    with pytest.raises(ParserError) as exc_info:
        parse_cargo_toml(content)

    assert "Failed to parse Cargo.toml" in str(exc_info.value)


# ============================================================================
# Auto-Detection Tests
# ============================================================================


def test_auto_detect_requirements(tmp_path: Path):
    """
    TEST_ID: T010.17
    SPEC: S010

    Test auto-detection of requirements.txt format.
    Should detect format by filename and parse correctly.
    """
    file_path = tmp_path / "requirements.txt"
    file_path.write_text("flask==2.0.1\ndjango>=3.2\n")

    packages = detect_and_parse(file_path)

    assert len(packages) == 2
    assert packages[0].name == "flask"
    assert packages[0].registry == "pypi"
    assert packages[1].name == "django"


def test_auto_detect_package_json(tmp_path: Path):
    """
    TEST_ID: T010.17.1
    SPEC: S010

    Test auto-detection of package.json format.
    Should detect format by filename and parse correctly.
    """
    file_path = tmp_path / "package.json"
    content = json.dumps({
        "dependencies": {
            "express": "^4.17.1",
            "lodash": "^4.17.21"
        }
    })
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    assert len(packages) == 2
    assert packages[0].name == "express"
    assert packages[0].registry == "npm"
    assert packages[1].name == "lodash"


def test_auto_detect_cargo(tmp_path: Path):
    """
    TEST_ID: T010.17.2
    SPEC: S010

    Test auto-detection of Cargo.toml format.
    Should detect format by filename and parse correctly.
    """
    file_path = tmp_path / "Cargo.toml"
    content = """
[dependencies]
serde = "1.0"
tokio = "1.15"
    """
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    assert len(packages) == 2
    assert packages[0].name == "serde"
    assert packages[0].registry == "crates"
    assert packages[1].name == "tokio"


def test_auto_detect_by_content(tmp_path: Path):
    """
    TEST_ID: T010.17.3
    SPEC: S010

    Test detection by content when filename is ambiguous.
    Should fall back to content-based detection for non-standard filenames.
    """
    # JSON content with .txt extension
    file_path = tmp_path / "deps.txt"
    content = json.dumps({
        "dependencies": {
            "express": "^4.17.1"
        }
    })
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    # Should detect as package.json by content
    assert len(packages) == 1
    assert packages[0].name == "express"
    assert packages[0].registry == "npm"
