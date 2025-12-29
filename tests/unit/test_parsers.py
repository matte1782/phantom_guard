"""
Unit tests for dependency file parsers.

SPEC: S010 (CLI Interface)
MODULE: phantom_guard.cli.parsers
"""

import json
from pathlib import Path

import pytest

from phantom_guard.cli.parsers import (
    ParserError,
    detect_and_parse,
    parse_cargo_toml,
    parse_package_json,
    parse_requirements_txt,
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
    content = json.dumps(
        {
            "name": "my-app",
            "dependencies": {"express": "^4.17.1", "lodash": "~4.17.21", "axios": "0.21.1"},
        }
    )

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
    content = json.dumps(
        {"dependencies": {"@types/node": "^16.0.0", "@babel/core": "^7.15.0", "express": "^4.17.1"}}
    )

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
    content = json.dumps(
        {
            "dependencies": {"express": "^4.17.1"},
            "devDependencies": {"jest": "^27.0.0", "eslint": "^7.32.0"},
        }
    )

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
    content = json.dumps({"dependencies": {"express": "^4.17.1", "lodash": "^4.17.21"}})
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
    content = json.dumps({"dependencies": {"express": "^4.17.1"}})
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    # Should detect as package.json by content
    assert len(packages) == 1
    assert packages[0].name == "express"
    assert packages[0].registry == "npm"


def test_auto_detect_file_not_found(tmp_path: Path):
    """
    TEST_ID: T010.17.4
    SPEC: S010
    EC: EC086

    Test FileNotFoundError for missing files.
    """
    file_path = tmp_path / "nonexistent.txt"

    with pytest.raises(FileNotFoundError, match="File not found"):
        detect_and_parse(file_path)


def test_auto_detect_toml_by_content(tmp_path: Path):
    """
    TEST_ID: T010.17.5
    SPEC: S010

    Test TOML content detection when filename is ambiguous.
    """
    file_path = tmp_path / "deps.unknown"
    content = """
[dependencies]
serde = "1.0"
tokio = "1.15"
    """
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    # Should detect as Cargo.toml by content
    assert len(packages) == 2
    assert packages[0].name == "serde"
    assert packages[0].registry == "crates"


def test_auto_detect_requirements_by_content(tmp_path: Path):
    """
    TEST_ID: T010.17.6
    SPEC: S010

    Test requirements.txt fallback detection when other formats fail.
    """
    file_path = tmp_path / "deps.unknown"
    content = """
flask==2.0.1
django>=3.2
requests
    """
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    # Should fall back to requirements.txt parsing
    assert len(packages) == 3
    assert packages[0].name == "flask"
    assert packages[0].registry == "pypi"


def test_parse_package_json_non_dict_dependencies():
    """
    TEST_ID: T010.15.4
    SPEC: S010

    Test handling of non-dict dependencies section.
    """
    content = json.dumps(
        {
            "name": "test-app",
            "dependencies": "invalid",  # Not a dict
            "devDependencies": {"jest": "^27.0.0"},
        }
    )

    packages = parse_package_json(content)

    # Should skip invalid dependencies, only parse devDependencies
    assert len(packages) == 1
    assert packages[0].name == "jest"


def test_parse_cargo_toml_non_dict_dependencies():
    """
    TEST_ID: T010.16.4
    SPEC: S010

    Test handling of non-dict dependencies section in Cargo.toml.
    """
    content = """
[package]
name = "my-crate"

[dependencies]

[dev-dependencies]
criterion = "0.3"
    """
    # Test with empty dependencies section
    packages = parse_cargo_toml(content)

    assert len(packages) == 1
    assert packages[0].name == "criterion"


def test_parse_cargo_toml_unknown_spec_type():
    """
    TEST_ID: T010.16.5
    SPEC: S010

    Test handling of unknown spec type in Cargo.toml.
    """
    content = """
[dependencies]
serde = "1.0"
unknown_pkg = 123
    """
    packages = parse_cargo_toml(content)

    # Both should be parsed, unknown_pkg should have None version
    assert len(packages) == 2
    names = {pkg.name for pkg in packages}
    assert names == {"serde", "unknown_pkg"}

    # Find the unknown_pkg entry
    unknown = next(p for p in packages if p.name == "unknown_pkg")
    assert unknown.version_spec is None


def test_parse_requirements_dev_variant(tmp_path: Path):
    """
    TEST_ID: T010.17.7
    SPEC: S010

    Test requirements-dev.txt detection.
    """
    file_path = tmp_path / "requirements-dev.txt"
    file_path.write_text("pytest==7.0.0\nblack>=22.0.0\n")

    packages = detect_and_parse(file_path)

    assert len(packages) == 2
    assert packages[0].name == "pytest"
    assert packages[0].registry == "pypi"


def test_parse_requirements_test_variant(tmp_path: Path):
    """
    TEST_ID: T010.17.8
    SPEC: S010

    Test requirements-test.txt detection.
    """
    file_path = tmp_path / "requirements-test.txt"
    file_path.write_text("pytest==7.0.0\ncoverage>=6.0\n")

    packages = detect_and_parse(file_path)

    assert len(packages) == 2
    assert packages[0].name == "pytest"


def test_parse_package_json_empty_version():
    """
    TEST_ID: T010.15.5
    SPEC: S010

    Test handling of empty version string in package.json.
    """
    content = json.dumps(
        {
            "dependencies": {
                "express": "^4.17.1",
                "lodash": "",  # Empty version
            }
        }
    )

    packages = parse_package_json(content)

    assert len(packages) == 2
    # Find lodash entry
    lodash = next(p for p in packages if p.name == "lodash")
    assert lodash.version_spec is None  # Empty string becomes None


# ============================================================================
# Additional Coverage Tests
# ============================================================================


def test_parse_requirements_pure_empty_lines():
    """
    TEST_ID: T010.13.5
    SPEC: S010

    Test handling of pure empty lines (not just whitespace).
    Exercises line 93 (continue after empty line check).
    """
    content = "\n\n\nflask\n\n\n"

    packages = parse_requirements_txt(content)

    assert len(packages) == 1
    assert packages[0].name == "flask"


def test_parse_requirements_pure_comment_lines():
    """
    TEST_ID: T010.13.6
    SPEC: S010

    Test handling of pure comment lines.
    Exercises line 97 (continue after comment check).
    """
    content = "# This is a comment\n# Another comment\nflask"

    packages = parse_requirements_txt(content)

    assert len(packages) == 1
    assert packages[0].name == "flask"


def test_parse_requirements_option_lines():
    """
    TEST_ID: T010.13.7
    SPEC: S010

    Test handling of option lines starting with - or --.
    Exercises lines 100-101 (continue after option check).
    """
    content = """
--index-url https://pypi.org/simple
-i https://pypi.org/simple
-r other-requirements.txt
--extra-index-url https://private.pypi.org
flask==2.0.1
-e local_package
--find-links https://example.com/wheels
django>=3.2
    """.strip()

    packages = parse_requirements_txt(content)

    assert len(packages) == 2
    assert packages[0].name == "flask"
    assert packages[1].name == "django"


def test_parse_requirements_url_lines():
    """
    TEST_ID: T010.13.8
    SPEC: S010

    Test handling of URL lines (http, https, git+).
    Exercises lines 104-105 (continue after URL check).
    """
    content = """
http://example.com/package.tar.gz
https://example.com/package.whl
git+https://github.com/user/repo.git@main
flask
git+ssh://git@github.com/user/repo.git
django
    """.strip()

    packages = parse_requirements_txt(content)

    assert len(packages) == 2
    assert packages[0].name == "flask"
    assert packages[1].name == "django"


def test_parse_requirements_inline_comments_removal():
    """
    TEST_ID: T010.13.9
    SPEC: S010

    Test handling of inline comments with proper stripping.
    Exercises lines 108-109 (inline comment removal).
    """
    content = """
flask==2.0.1 # Web framework
django  # Another framework
requests # HTTP library
    """.strip()

    packages = parse_requirements_txt(content)

    assert len(packages) == 3
    assert packages[0].name == "flask"
    assert packages[0].version_spec == "==2.0.1"
    assert packages[1].name == "django"
    assert packages[2].name == "requests"


def test_parse_requirements_no_pattern_match():
    """
    TEST_ID: T010.13.10
    SPEC: S010

    Test lines that don't match the package pattern.
    Exercises line 113 (pattern not matching).
    """
    # The pattern ^([a-zA-Z0-9]...) matches alphanumeric starts
    # _underscore_start and @scope/package don't match the pattern
    # -dash-start is skipped earlier as an option (starts with -)
    content = """
flask
_underscore_start
@scope/package
.dotfile
    """.strip()

    packages = parse_requirements_txt(content)

    # Only flask should match (valid package name starting with alphanumeric)
    # Others don't match the pattern starting with [a-zA-Z0-9]
    assert len(packages) == 1
    assert packages[0].name == "flask"


def test_parse_package_json_dependencies_not_dict():
    """
    TEST_ID: T010.15.6
    SPEC: S010

    Test handling when dependencies section is not a dict.
    Exercises line 160 (continue when deps is not dict).
    """
    content = json.dumps(
        {
            "name": "test-app",
            "dependencies": ["express", "lodash"],  # Array instead of dict
            "devDependencies": {"jest": "^27.0.0"},
        }
    )

    packages = parse_package_json(content)

    # Should skip array dependencies, only parse devDependencies
    assert len(packages) == 1
    assert packages[0].name == "jest"


def test_parse_package_json_both_sections_not_dict():
    """
    TEST_ID: T010.15.7
    SPEC: S010

    Test handling when both dependencies sections are not dicts.
    Exercises line 160 for both sections.
    """
    content = json.dumps(
        {
            "name": "test-app",
            "dependencies": "invalid-string",
            "devDependencies": None,
        }
    )

    packages = parse_package_json(content)

    # Should return empty list when both sections are invalid
    assert len(packages) == 0


def test_parse_cargo_toml_invalid_toml_syntax():
    """
    TEST_ID: T010.16.6
    SPEC: S010

    Test error handling for invalid TOML syntax.
    Exercises lines 202-203 (ParserError on invalid TOML).
    """
    content = """
[dependencies]
serde = "1.0
tokio = unclosed
    """

    with pytest.raises(ParserError) as exc_info:
        parse_cargo_toml(content)

    assert "Failed to parse Cargo.toml" in str(exc_info.value)


def test_parse_cargo_toml_dependencies_not_dict():
    """
    TEST_ID: T010.16.7
    SPEC: S010

    Test handling when dependencies section is not a dict.
    Exercises line 209 (continue when deps is not dict).
    """
    # Create TOML where dependencies is a root-level non-dict value
    # (not using section header [dependencies])
    content = """
dependencies = "invalid"

[dev-dependencies]
criterion = "0.3"
    """

    packages = parse_cargo_toml(content)

    # Should skip invalid dependencies, only parse dev-dependencies
    assert len(packages) == 1
    assert packages[0].name == "criterion"


def test_parse_cargo_toml_both_sections_not_dict():
    """
    TEST_ID: T010.16.9
    SPEC: S010

    Test handling when both dependency sections are not dicts.
    Exercises line 209 for both iterations.
    """
    # Create TOML where both sections are root-level non-dict values
    # (not using section headers like [dependencies])
    content = """
dependencies = "invalid-string"
dev-dependencies = 123
    """

    packages = parse_cargo_toml(content)

    # Should return empty list when both sections are invalid
    assert len(packages) == 0


def test_parse_cargo_toml_unknown_spec_type_none():
    """
    TEST_ID: T010.16.8
    SPEC: S010

    Test handling of unknown spec type (neither string nor dict).
    Exercises line 219 (version_spec = None for unknown types).
    """
    content = """
[dependencies]
valid_pkg = "1.0"
int_version = 123
float_version = 1.5
bool_version = true
    """

    packages = parse_cargo_toml(content)

    assert len(packages) == 4

    # Valid package should have version
    valid = next(p for p in packages if p.name == "valid_pkg")
    assert valid.version_spec == "1.0"

    # Invalid types should have None version
    int_pkg = next(p for p in packages if p.name == "int_version")
    assert int_pkg.version_spec is None

    float_pkg = next(p for p in packages if p.name == "float_version")
    assert float_pkg.version_spec is None

    bool_pkg = next(p for p in packages if p.name == "bool_version")
    assert bool_pkg.version_spec is None


def test_detect_and_parse_file_not_found(tmp_path: Path):
    """
    TEST_ID: T010.17.9
    SPEC: S010

    Test FileNotFoundError for non-existent file.
    Exercises line 252 (FileNotFoundError).
    """
    file_path = tmp_path / "does_not_exist.txt"

    with pytest.raises(FileNotFoundError) as exc_info:
        detect_and_parse(file_path)

    assert "File not found" in str(exc_info.value)


def test_detect_and_parse_json_content_fallback(tmp_path: Path):
    """
    TEST_ID: T010.17.10
    SPEC: S010

    Test content-based detection falling back to JSON.
    Exercises lines 267-270 (try JSON detection).
    """
    file_path = tmp_path / "deps.unknown"
    content = json.dumps({"dependencies": {"express": "^4.17.1", "lodash": "~4.17.21"}})
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    assert len(packages) == 2
    assert all(pkg.registry == "npm" for pkg in packages)


def test_detect_and_parse_toml_content_fallback(tmp_path: Path):
    """
    TEST_ID: T010.17.11
    SPEC: S010

    Test content-based detection falling back to TOML.
    Exercises lines 273-276 (try TOML detection after JSON fails).
    """
    file_path = tmp_path / "deps.config"
    content = """
[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
    """
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    assert len(packages) == 2
    assert all(pkg.registry == "crates" for pkg in packages)


def test_detect_and_parse_requirements_content_fallback(tmp_path: Path):
    """
    TEST_ID: T010.17.12
    SPEC: S010

    Test content-based detection falling back to requirements.txt.
    Exercises lines 279-280 (fall back to requirements.txt).
    """
    file_path = tmp_path / "dependencies.lock"
    content = """
flask==2.0.1
django>=3.2
requests
    """
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    assert len(packages) == 3
    assert all(pkg.registry == "pypi" for pkg in packages)


def test_detect_and_parse_invalid_json_falls_through(tmp_path: Path):
    """
    TEST_ID: T010.17.13
    SPEC: S010

    Test that invalid JSON falls through to TOML detection.
    Exercises lines 269-270 (except ParserError/JSONDecodeError: pass).
    """
    file_path = tmp_path / "mixed.data"
    # Valid TOML but invalid JSON
    content = """
[dependencies]
serde = "1.0"
    """
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    # Should detect as TOML after JSON fails
    assert len(packages) == 1
    assert packages[0].name == "serde"
    assert packages[0].registry == "crates"


def test_detect_and_parse_invalid_toml_falls_through(tmp_path: Path):
    """
    TEST_ID: T010.17.14
    SPEC: S010

    Test that invalid TOML falls through to requirements.txt.
    Exercises lines 275-276 (except ParserError: pass).
    """
    file_path = tmp_path / "packages.list"
    # Valid requirements.txt format, not JSON or TOML
    content = """
flask==2.0.1
django>=3.2
    """
    file_path.write_text(content)

    packages = detect_and_parse(file_path)

    # Should fall back to requirements.txt parsing
    assert len(packages) == 2
    assert packages[0].name == "flask"
    assert packages[0].registry == "pypi"
