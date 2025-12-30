# Week 4 - Day 4: Packaging for PyPI (OPTIMIZED)

> **Date**: Day 4 (Week 4)
> **Focus**: Complete packaging, create missing files
> **Tasks**: W4.4
> **Hours**: 6 hours
> **Status**: OPTIMIZED based on hostile review findings
> **Dependencies**: W4.1-W4.3 complete

---

## Pre-Existing State Analysis

### What Already Exists

| File | Status | Lines | Action Required |
|:-----|:-------|:------|:----------------|
| `pyproject.toml` | ✅ 90% done | 127 | Fix URLs, add sdist config |
| `LICENSE` | ❌ MISSING | 0 | CREATE |
| `CHANGELOG.md` | ❌ MISSING | 0 | CREATE |
| `src/phantom_guard/__init__.py` | ✅ Has version | - | Verify |

### pyproject.toml Analysis (127 lines)

```toml
# EXISTING - needs fixes:

[project.urls]
Homepage = "https://github.com/yourusername/phantom-guard"      # ❌ placeholder
Documentation = "https://github.com/yourusername/phantom-guard" # ❌ placeholder
Repository = "https://github.com/yourusername/phantom-guard"    # ❌ placeholder
Issues = "https://github.com/yourusername/phantom-guard/issues" # ❌ placeholder

# MISSING:
# - [tool.hatch.build.targets.sdist] include configuration
# - license = {file = "LICENSE"} format
```

---

## Revised Task Breakdown

### Morning Session (3h) - Fix pyproject.toml + Create Missing Files

#### Step 1: Update pyproject.toml URLs (30min)

```toml
# pyproject.toml - UPDATE these sections:

[project]
name = "phantom-guard"
version = "0.1.0"
description = "Detect AI-hallucinated malicious packages in your dependencies"
readme = "README.md"
requires-python = ">=3.11"
license = {file = "LICENSE"}  # Reference LICENSE file
authors = [{ name = "Phantom Guard Contributors" }]
keywords = [
    "security",
    "supply-chain",
    "typosquatting",
    "slopsquatting",
    "ai-security",
    "package-validation",
    "dependency-scanning",
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Security",
    "Topic :: Software Development :: Quality Assurance",
    "Typing :: Typed",
]

[project.urls]
Homepage = "https://github.com/phantom-guard/phantom-guard"
Documentation = "https://github.com/phantom-guard/phantom-guard#readme"
Repository = "https://github.com/phantom-guard/phantom-guard"
Changelog = "https://github.com/phantom-guard/phantom-guard/blob/main/CHANGELOG.md"
"Bug Tracker" = "https://github.com/phantom-guard/phantom-guard/issues"

[tool.hatch.build.targets.sdist]
include = [
    "src/",
    "tests/",
    "LICENSE",
    "README.md",
    "CHANGELOG.md",
    "pyproject.toml",
]
```

#### Step 2: Create LICENSE File (15min)

```text
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

#### Step 3: Create CHANGELOG.md (1h)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-XX-XX

### Added

#### Core Detection Engine
- Package validation with multi-signal risk assessment
- Pattern matching for AI-hallucinated package names (10 patterns)
- Typosquat detection against top 3000 popular packages
- Configurable risk scoring with SAFE/SUSPICIOUS/HIGH_RISK thresholds

#### Registry Support
- PyPI client with JSON API integration
- npm registry client with scoped package support
- crates.io client with proper User-Agent handling
- Two-tier caching (memory LRU + SQLite persistence)
- Retry logic with exponential backoff

#### CLI Interface
- `phantom-guard validate <package>` - Check single package
- `phantom-guard check <file>` - Batch validate from manifest files
- `phantom-guard cache stats|clear|path` - Cache management
- Rich terminal output with colors and progress indicators
- JSON output mode for CI/CD integration (`--output json`)
- Exit codes (0-5) for automation

#### File Format Support
- requirements.txt (Python)
- package.json (npm)
- Cargo.toml (Rust)

#### Performance
- Single package (cached): <10ms P99
- Single package (uncached): <200ms P99
- Batch 50 packages: <5s P99
- Pattern matching: <1ms P99

### Security
- No shell command execution
- No eval/exec usage
- Input validation on all package names
- Rate limit handling for all registries
- Graceful degradation on errors

### Technical
- 100% test coverage (835+ tests)
- Full type annotations (mypy --strict)
- Pre-compiled regex patterns
- LRU-cached Levenshtein distance
- Async/await throughout

## [Unreleased]

### Planned
- GitHub Actions integration
- Pre-commit hook support
- SBOM generation
- Custom pattern configuration
- VS Code extension
```

#### Step 4: Verify Package Structure (30min)

```bash
# Verify all required files exist
ls -la LICENSE README.md CHANGELOG.md pyproject.toml

# Verify package structure
find src/phantom_guard -name "*.py" | wc -l
# Expected: 27 files

# Check version
python -c "from phantom_guard import __version__; print(__version__)"
# Expected: 0.1.0
```

---

### Afternoon Session (3h) - Build & Test Installation

#### Step 5: Build Distribution Artifacts (45min)

```bash
# Install build tools
pip install build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Build wheel and sdist
python -m build

# Verify artifacts created
ls -la dist/
# Expected:
# phantom_guard-0.1.0-py3-none-any.whl
# phantom_guard-0.1.0.tar.gz

# Check wheel contents
unzip -l dist/phantom_guard-0.1.0-py3-none-any.whl | head -30

# Check sdist contents
tar -tzf dist/phantom_guard-0.1.0.tar.gz | head -30
```

#### Step 6: Test Local Installation from Wheel (1h)

```bash
# Create clean virtual environment
python -m venv test_wheel_env
source test_wheel_env/bin/activate  # Windows: .\test_wheel_env\Scripts\activate

# Install from wheel
pip install dist/phantom_guard-0.1.0-py3-none-any.whl

# Verify version
phantom-guard --version
# Expected: phantom-guard 0.1.0

# Test basic commands
phantom-guard --help
phantom-guard validate flask
phantom-guard validate reqeusts  # Typosquat test

# Test imports
python -c "from phantom_guard import Detector; print('Detector OK')"
python -c "from phantom_guard.cache import Cache; print('Cache OK')"
python -c "from phantom_guard.registry import PyPIClient; print('Registry OK')"

# Clean up
deactivate
rm -rf test_wheel_env
```

#### Step 7: Test from Source Distribution (30min)

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

#### Step 8: Validate with Twine (30min)

```bash
# Check package metadata renders correctly
twine check dist/*

# Expected output:
# Checking dist/phantom_guard-0.1.0-py3-none-any.whl: PASSED
# Checking dist/phantom_guard-0.1.0.tar.gz: PASSED

# Optional: Test upload to TestPyPI
# twine upload --repository testpypi dist/*
```

#### Step 9: Create Installation Test (15min)

```python
# tests/e2e/test_installation.py - VERIFY EXISTS
"""
End-to-end installation tests.
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
- [ ] pyproject.toml URLs fixed (no placeholders)
- [ ] pyproject.toml sdist include added
- [ ] LICENSE file created
- [ ] CHANGELOG.md created
- [ ] Version verified as 0.1.0

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
git commit -m "build: Complete packaging for PyPI release

W4.4: Packaging COMPLETE

- Fix pyproject.toml URLs (remove placeholders)
- Add sdist include configuration
- Create MIT LICENSE file
- Create CHANGELOG.md for v0.1.0
- Add Development Status :: 4 - Beta classifier

Build artifacts verified:
- Wheel: phantom_guard-0.1.0-py3-none-any.whl
- Sdist: phantom_guard-0.1.0.tar.gz
- twine check: PASSED

Installation tested and working from both wheel and sdist."
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

## Key Insight from Hostile Review

pyproject.toml is **90% complete** but has critical issues:
1. URLs use placeholder `yourusername` - MUST FIX
2. Missing `[tool.hatch.build.targets.sdist]` include
3. LICENSE file missing - MUST CREATE
4. CHANGELOG.md missing - MUST CREATE

These are quick fixes, not full rewrites.

---

## Tomorrow Preview

**Day 5 Focus**: Documentation (W4.5)
- Expand README.md from 40 → 320+ lines
- Create docs/USAGE.md
- Create docs/API.md
- Create docs/CI_CD.md
- Create CONTRIBUTING.md
