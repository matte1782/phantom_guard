# Week 4 - Day 4: Packaging for PyPI

> **Date**: Day 4 (Week 4)
> **Focus**: Finalize packaging, build artifacts, test installation
> **Tasks**: W4.4
> **Hours**: 6 hours
> **Dependencies**: W4.1-W4.3 complete
> **Exit Criteria**: `pip install phantom-guard` works from local build

---

## Overview

Prepare the package for PyPI release. This includes finalizing metadata, building distribution artifacts, and testing the installation process.

### Packaging Requirements

| Requirement | Status |
|:------------|:-------|
| pyproject.toml complete | Pending |
| Version 0.1.0 set | Pending |
| License file | Pending |
| Changelog | Pending |
| Build artifacts (wheel + sdist) | Pending |
| Local install test | Pending |

### Deliverables
- [ ] Complete pyproject.toml with all metadata
- [ ] LICENSE file (MIT)
- [ ] CHANGELOG.md for v0.1.0
- [ ] Build wheel and source distribution
- [ ] Test installation from local build
- [ ] Test CLI works after pip install

---

## Morning Session (3h)

### Objective
Finalize pyproject.toml and add required metadata files.

### Step 1: Update pyproject.toml (1h)

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "phantom-guard"
version = "0.1.0"
description = "Detect AI-hallucinated malicious packages in your dependencies"
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.10"
authors = [
    {name = "Phantom Guard Contributors", email = "phantom-guard@example.com"}
]
maintainers = [
    {name = "Phantom Guard Contributors", email = "phantom-guard@example.com"}
]
keywords = [
    "security",
    "supply-chain",
    "typosquatting",
    "dependency-scanning",
    "ai-hallucination",
    "package-security",
    "pypi",
    "npm",
    "crates",
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Security",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: System :: Systems Administration",
    "Typing :: Typed",
]

dependencies = [
    "httpx>=0.25.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "aiosqlite>=0.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pytest-benchmark>=4.0.0",
    "respx>=0.20.0",
    "hypothesis>=6.90.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "memory-profiler>=0.61.0",
]

[project.urls]
Homepage = "https://github.com/phantom-guard/phantom-guard"
Documentation = "https://phantom-guard.readthedocs.io"
Repository = "https://github.com/phantom-guard/phantom-guard"
Changelog = "https://github.com/phantom-guard/phantom-guard/blob/main/CHANGELOG.md"
"Bug Tracker" = "https://github.com/phantom-guard/phantom-guard/issues"

[project.scripts]
phantom-guard = "phantom_guard.cli.main:app"

[tool.hatch.build.targets.wheel]
packages = ["src/phantom_guard"]

[tool.hatch.build.targets.sdist]
include = [
    "src/",
    "tests/",
    "LICENSE",
    "README.md",
    "CHANGELOG.md",
    "pyproject.toml",
]

# Ruff configuration
[tool.ruff]
target-version = "py310"
line-length = 100
src = ["src"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "SIM",    # flake8-simplify
    "RUF",    # ruff-specific
]
ignore = [
    "E501",   # line too long (handled by formatter)
    "SIM117", # multiple with statements (sometimes clearer)
]

[tool.ruff.lint.isort]
known-first-party = ["phantom_guard"]

# Mypy configuration
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
plugins = []

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

# Pytest configuration
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
filterwarnings = [
    "ignore::DeprecationWarning",
]
markers = [
    "slow: marks tests as slow",
    "network: marks tests that require network access",
    "e2e: marks end-to-end tests",
    "benchmark: marks benchmark tests",
]
addopts = "-v --tb=short"

# Coverage configuration
[tool.coverage.run]
source = ["src/phantom_guard"]
branch = true
omit = ["*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@abstractmethod",
]
show_missing = true
fail_under = 90
```

### Step 2: Create LICENSE File (15min)

```text
# LICENSE
MIT License

Copyright (c) 2024 Phantom Guard Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Step 3: Create CHANGELOG (45min)

```markdown
# CHANGELOG.md

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-XX-XX

### Added

#### Core Detection Engine
- Package validation with multi-signal risk assessment
- Pattern matching for AI-hallucinated package names
- Typosquat detection against top 1000 popular packages
- Configurable risk scoring with safe/suspicious/high-risk thresholds

#### Registry Support
- PyPI client with pypistats.org integration
- npm registry client with scoped package support
- crates.io client with proper User-Agent handling
- Two-tier caching (memory LRU + SQLite persistence)

#### CLI Interface
- `phantom-guard validate <package>` - Check single package
- `phantom-guard check <file>` - Batch validate from manifest files
- `phantom-guard cache` - Cache management commands
- Rich terminal output with colors and progress indicators
- JSON output mode for CI/CD integration
- Exit codes (0-5) for automation

#### File Format Support
- requirements.txt (Python)
- package.json (npm)
- Cargo.toml (Rust)

#### Performance
- Single package (cached): <10ms
- Single package (uncached): <200ms
- Batch 50 packages: <5s
- Pattern matching: <1ms

### Security
- No shell command execution
- No eval/exec usage
- Input validation on all package names
- Rate limit handling for all registries

## [Unreleased]

### Planned
- GitHub Actions integration
- Pre-commit hook support
- SBOM generation
- Custom pattern configuration
```

### Step 4: Verify Package Structure (30min)

```bash
# Verify all required files exist
ls -la LICENSE README.md CHANGELOG.md pyproject.toml

# Verify package structure
tree src/phantom_guard/

# Expected:
# src/phantom_guard/
# ├── __init__.py
# ├── cache/
# ├── cli/
# ├── core/
# ├── data/
# └── registry/

# Check imports work
python -c "from phantom_guard import __version__; print(__version__)"
# Expected: 0.1.0
```

---

## Afternoon Session (3h)

### Objective
Build distribution artifacts and test installation.

### Step 5: Build Distribution Artifacts (45min)

```bash
# Install build tools
pip install build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build wheel and sdist
python -m build

# Expected output:
# dist/
# ├── phantom_guard-0.1.0-py3-none-any.whl
# └── phantom_guard-0.1.0.tar.gz

# Verify build contents
unzip -l dist/phantom_guard-0.1.0-py3-none-any.whl | head -30
tar -tzf dist/phantom_guard-0.1.0.tar.gz | head -30
```

### Step 6: Test Local Installation (1h)

```bash
# Create clean virtual environment
python -m venv test_install_env
source test_install_env/bin/activate  # or .\test_install_env\Scripts\activate on Windows

# Install from wheel
pip install dist/phantom_guard-0.1.0-py3-none-any.whl

# Verify installation
phantom-guard --version
# Expected: phantom-guard 0.1.0

# Test basic commands
phantom-guard --help
phantom-guard validate flask
phantom-guard validate reqeusts  # Typosquat test

# Test imports
python -c "from phantom_guard import Detector; print('Import OK')"
python -c "from phantom_guard.cache import Cache; print('Cache OK')"
python -c "from phantom_guard.registry import PyPIClient; print('Registry OK')"

# Deactivate and clean up
deactivate
rm -rf test_install_env
```

### Step 7: Test from Source Distribution (30min)

```bash
# Create another clean environment
python -m venv test_sdist_env
source test_sdist_env/bin/activate

# Install from sdist
pip install dist/phantom_guard-0.1.0.tar.gz

# Run same tests
phantom-guard --version
phantom-guard validate flask

deactivate
rm -rf test_sdist_env
```

### Step 8: Validate with Twine (30min)

```bash
# Check package description renders correctly
twine check dist/*

# Expected output:
# Checking dist/phantom_guard-0.1.0-py3-none-any.whl: PASSED
# Checking dist/phantom_guard-0.1.0.tar.gz: PASSED

# Optional: Test upload to TestPyPI
# twine upload --repository testpypi dist/*
```

### Step 9: Create Installation Test (15min)

```python
# tests/e2e/test_installation.py
"""
End-to-end installation tests.

These verify the package works after pip install.
"""

import subprocess
import sys


def test_cli_available_after_install():
    """CLI should be available after pip install."""
    result = subprocess.run(
        ["phantom-guard", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout or "0.1.0" in result.stderr


def test_validate_command_works():
    """validate command should work."""
    result = subprocess.run(
        ["phantom-guard", "validate", "flask", "--no-banner"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "flask" in result.stdout.lower()


def test_python_import_works():
    """Python imports should work."""
    result = subprocess.run(
        [sys.executable, "-c", "from phantom_guard import Detector; print('OK')"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "OK" in result.stdout
```

---

## End of Day Checklist

### Files Created/Updated
- [ ] pyproject.toml finalized
- [ ] LICENSE file created
- [ ] CHANGELOG.md created
- [ ] src/phantom_guard/__init__.py has __version__

### Build Artifacts
- [ ] Wheel built successfully
- [ ] Source distribution built successfully
- [ ] twine check passes

### Installation Tests
- [ ] pip install from wheel works
- [ ] pip install from sdist works
- [ ] CLI commands work after install
- [ ] Python imports work after install

### Git Commit

```bash
git add pyproject.toml LICENSE CHANGELOG.md
git commit -m "build: Finalize packaging for PyPI release

W4.4: Packaging complete

- Complete pyproject.toml with all metadata
- Add MIT LICENSE file
- Create CHANGELOG.md for v0.1.0
- Configure hatchling build system
- Add classifiers and keywords for PyPI
- Configure tool settings (ruff, mypy, pytest, coverage)

Build artifacts verified:
- Wheel: phantom_guard-0.1.0-py3-none-any.whl
- Sdist: phantom_guard-0.1.0.tar.gz

Installation tested and working."
```

---

## Day 4 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.4 | |
| Build Success | Yes | |
| Wheel Install | Works | |
| Sdist Install | Works | |
| CLI Works | Yes | |
| Twine Check | PASSED | |

---

## Tomorrow Preview

**Day 5 Focus**: Documentation (W4.5)
- Write comprehensive README.md
- Add installation instructions
- Add usage examples
- Add CI/CD integration guides
- Add API documentation
