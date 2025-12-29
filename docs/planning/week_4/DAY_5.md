# Week 4 - Day 5: Documentation

> **Date**: Day 5 (Week 4)
> **Focus**: Comprehensive README and usage documentation
> **Tasks**: W4.5
> **Hours**: 6 hours
> **Dependencies**: W4.4 (Packaging) complete
> **Exit Criteria**: README complete with all sections, examples work

---

## Overview

Create comprehensive documentation that enables users to quickly understand, install, and use Phantom Guard. Good documentation is critical for adoption.

### Documentation Requirements

| Section | Status |
|:--------|:-------|
| Project overview | Pending |
| Installation instructions | Pending |
| Quick start guide | Pending |
| CLI reference | Pending |
| API reference | Pending |
| CI/CD integration | Pending |
| Configuration | Pending |
| Contributing guide | Pending |

### Deliverables
- [ ] README.md with all sections
- [ ] docs/USAGE.md with detailed examples
- [ ] docs/API.md with Python API reference
- [ ] docs/CI_CD.md with integration guides
- [ ] CONTRIBUTING.md

---

## Morning Session (3h)

### Objective
Write the main README.md with all essential sections.

### Step 1: Create README Structure (30min)

```markdown
# README.md

<div align="center">

# Phantom Guard

**Detect AI-hallucinated malicious packages in your dependencies**

[![PyPI version](https://badge.fury.io/py/phantom-guard.svg)](https://badge.fury.io/py/phantom-guard)
[![Python Versions](https://img.shields.io/pypi/pyversions/phantom-guard.svg)](https://pypi.org/project/phantom-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/phantom-guard/phantom-guard/workflows/Tests/badge.svg)](https://github.com/phantom-guard/phantom-guard/actions)
[![Coverage](https://codecov.io/gh/phantom-guard/phantom-guard/branch/main/graph/badge.svg)](https://codecov.io/gh/phantom-guard/phantom-guard)

</div>

---

When AI coding assistants hallucinate package names, attackers create those
packages with malicious code. Phantom Guard detects these attacks before
they compromise your supply chain.

## The Problem

AI assistants like ChatGPT, Claude, and Copilot sometimes suggest packages
that don't exist. Attackers monitor these hallucinations and publish malicious
packages with those names. When developers blindly install the suggested
package, they get compromised.

## The Solution

Phantom Guard analyzes package names and metadata to detect:

- **Typosquats** of popular packages (e.g., `reqeusts` → `requests`)
- **AI-hallucination patterns** (e.g., `flask-gpt-helper`, `easy-numpy`)
- **Non-existent packages** being installed
- **Suspicious metadata** (new packages, no downloads, etc.)

## Quick Start

### Installation

```bash
pip install phantom-guard
```

### Basic Usage

```bash
# Check a single package
phantom-guard validate flask-gpt-helper

# Output:
# ✗ flask-gpt-helper    HIGH_RISK    [0.82]
#   └─ Pattern: AI-related suffix detected
#   └─ Package does not exist on PyPI
```

### Check Your Requirements File

```bash
# Scan requirements.txt
phantom-guard check requirements.txt

# Scan package.json (npm)
phantom-guard check package.json --registry npm

# Scan Cargo.toml (Rust)
phantom-guard check Cargo.toml --registry crates
```

## Features

### Multi-Registry Support

| Registry | Status | Command |
|:---------|:-------|:--------|
| PyPI | Full support | `--registry pypi` (default) |
| npm | Full support | `--registry npm` |
| crates.io | Full support | `--registry crates` |

### Risk Levels

| Level | Exit Code | Description |
|:------|:----------|:------------|
| SAFE | 0 | Package appears legitimate |
| SUSPICIOUS | 1 | Some risk signals detected |
| HIGH_RISK | 2 | Likely malicious, do not install |
| NOT_FOUND | 3 | Package doesn't exist |

### Detection Signals

- **Typosquat Detection**: Edit distance against top 1000 popular packages
- **Pattern Matching**: AI-related suffixes, helper/wrapper patterns
- **Metadata Analysis**: Creation date, downloads, maintainer count
- **Existence Check**: Verify package exists in registry

## CLI Reference

### Commands

```bash
phantom-guard validate <package> [OPTIONS]
phantom-guard check <file> [OPTIONS]
phantom-guard cache [stats|clear|path]
```

### Options

| Option | Description |
|:-------|:------------|
| `-r, --registry` | Target registry (pypi, npm, crates) |
| `-o, --output` | Output format (text, json) |
| `-v, --verbose` | Show detailed signals |
| `-q, --quiet` | Minimal output |
| `--no-cache` | Bypass cache |
| `--fail-on` | Fail on level (suspicious, high_risk) |

### Examples

```bash
# JSON output for CI/CD
phantom-guard check requirements.txt --output json

# Verbose mode shows all signals
phantom-guard validate somepackage -v

# Fail build on suspicious packages
phantom-guard check requirements.txt --fail-on suspicious
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Check

on: [push, pull_request]

jobs:
  phantom-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Phantom Guard
        run: pip install phantom-guard

      - name: Check dependencies
        run: phantom-guard check requirements.txt --output json > report.json

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: report.json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: phantom-guard
        name: Check package security
        entry: phantom-guard check requirements.txt --fail-on suspicious
        language: system
        pass_filenames: false
        always_run: true
```

### GitLab CI

```yaml
security-check:
  image: python:3.11
  script:
    - pip install phantom-guard
    - phantom-guard check requirements.txt --output json
  artifacts:
    reports:
      security: report.json
```

## Python API

```python
from phantom_guard import Detector
from phantom_guard.core.types import Recommendation

# Create detector
detector = Detector()

# Validate single package
result = await detector.validate("flask")

if result.recommendation == Recommendation.HIGH_RISK:
    print(f"Warning: {result.name} is high risk!")
    for signal in result.signals:
        print(f"  - {signal.signal_type.value}")

# Batch validation
results = await detector.validate_batch([
    "flask",
    "reqeusts",  # typosquat
    "flask-gpt-helper",  # hallucination
])

for result in results:
    print(f"{result.name}: {result.recommendation.value}")
```

## Performance

| Operation | Time | Notes |
|:----------|:-----|:------|
| Single package (cached) | <10ms | Memory cache hit |
| Single package (uncached) | <200ms | Network + cache write |
| Batch 50 packages | <5s | Concurrent processing |
| Pattern matching | <1ms | Pre-compiled regex |

## Configuration

### Cache Location

```bash
# View cache path
phantom-guard cache path

# Clear cache
phantom-guard cache clear

# Cache statistics
phantom-guard cache stats
```

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `PHANTOM_GUARD_CACHE_DIR` | Cache directory | `~/.cache/phantom-guard` |
| `PHANTOM_GUARD_CACHE_TTL` | Cache TTL in seconds | `3600` |
| `PHANTOM_GUARD_TIMEOUT` | API timeout in seconds | `10` |

## Security

Phantom Guard is designed with security in mind:

- No shell command execution
- No eval/exec usage
- All inputs validated
- Rate limit handling for registries
- Graceful degradation on errors

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [hugovk/top-pypi-packages](https://github.com/hugovk/top-pypi-packages) for PyPI download data
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [Typer](https://github.com/tiangolo/typer) for CLI framework
```

### Step 2: Create Usage Documentation (1h)

```markdown
# docs/USAGE.md

# Phantom Guard Usage Guide

This guide covers all features and usage patterns for Phantom Guard.

## Table of Contents

1. [Installation](#installation)
2. [Basic Commands](#basic-commands)
3. [Checking Package Files](#checking-package-files)
4. [Understanding Results](#understanding-results)
5. [Output Formats](#output-formats)
6. [Cache Management](#cache-management)
7. [Advanced Usage](#advanced-usage)

## Installation

### From PyPI (Recommended)

```bash
pip install phantom-guard
```

### From Source

```bash
git clone https://github.com/phantom-guard/phantom-guard
cd phantom-guard
pip install -e .
```

### Verify Installation

```bash
phantom-guard --version
# phantom-guard 0.1.0
```

## Basic Commands

### Validate Single Package

```bash
# Check a PyPI package
phantom-guard validate flask

# Check npm package
phantom-guard validate express --registry npm

# Check crates.io package
phantom-guard validate serde --registry crates
```

### Validate with Details

```bash
# Verbose mode shows all signals
phantom-guard validate somepackage -v

# Quiet mode for scripts
phantom-guard validate flask -q
```

## Checking Package Files

### Python (requirements.txt)

```bash
phantom-guard check requirements.txt
phantom-guard check requirements-dev.txt
```

### Node.js (package.json)

```bash
phantom-guard check package.json --registry npm
```

### Rust (Cargo.toml)

```bash
phantom-guard check Cargo.toml --registry crates
```

## Understanding Results

### Risk Levels

| Level | Icon | Meaning | Action |
|:------|:-----|:--------|:-------|
| SAFE | ✓ | Legitimate package | Proceed |
| SUSPICIOUS | ⚠ | Some risk signals | Review manually |
| HIGH_RISK | ✗ | Likely malicious | Do NOT install |
| NOT_FOUND | ? | Doesn't exist | Verify package name |

### Risk Signals

Phantom Guard detects multiple risk signals:

1. **Typosquat**: Similar to popular package
2. **AI Pattern**: Matches hallucination patterns
3. **New Package**: Created recently
4. **Low Downloads**: Minimal usage
5. **No Maintainers**: Single maintainer
6. **Missing Repo**: No source repository

## Output Formats

### Text (Default)

```bash
phantom-guard check requirements.txt
```

### JSON

```bash
phantom-guard check requirements.txt --output json
```

```json
{
  "results": [
    {
      "name": "flask",
      "recommendation": "safe",
      "risk_score": 0.05,
      "signals": []
    }
  ],
  "summary": {
    "total": 10,
    "safe": 8,
    "suspicious": 1,
    "high_risk": 1
  }
}
```

## Cache Management

### View Cache Statistics

```bash
phantom-guard cache stats
# Hits: 1523
# Misses: 42
# Hit Rate: 97.3%
# Size: 2.3MB
```

### Clear Cache

```bash
# Clear all
phantom-guard cache clear

# Clear specific registry
phantom-guard cache clear --registry pypi
```

### Cache Location

```bash
phantom-guard cache path
# /home/user/.cache/phantom-guard/
```

## Advanced Usage

### Fail on Specific Level

```bash
# Fail if any package is suspicious or worse
phantom-guard check requirements.txt --fail-on suspicious

# Fail only on high risk
phantom-guard check requirements.txt --fail-on high_risk
```

### Batch Processing

```bash
# Check multiple files
for file in requirements*.txt; do
    phantom-guard check "$file"
done
```

### Python API

```python
import asyncio
from phantom_guard import Detector

async def main():
    detector = Detector()

    # Single package
    result = await detector.validate("flask")
    print(f"{result.name}: {result.recommendation.value}")

    # Batch
    results = await detector.validate_batch(["flask", "django", "requests"])
    for r in results:
        print(f"{r.name}: {r.risk_score}")

asyncio.run(main())
```
```

### Step 3: Create API Documentation (1h)

```markdown
# docs/API.md

# Phantom Guard Python API

## Quick Start

```python
from phantom_guard import Detector
from phantom_guard.core.types import Recommendation

detector = Detector()
result = await detector.validate("flask")
```

## Core Classes

### Detector

Main entry point for package validation.

```python
class Detector:
    async def validate(
        self,
        name: str,
        registry: str = "pypi",
    ) -> PackageRisk:
        """Validate a single package."""

    async def validate_batch(
        self,
        packages: list[str],
        registry: str = "pypi",
        fail_fast: bool = False,
    ) -> list[PackageRisk]:
        """Validate multiple packages concurrently."""
```

### PackageRisk

Result of package validation.

```python
@dataclass
class PackageRisk:
    name: str                      # Package name
    recommendation: Recommendation  # SAFE, SUSPICIOUS, HIGH_RISK, NOT_FOUND
    risk_score: float              # 0.0 (safe) to 1.0 (dangerous)
    signals: tuple[Signal, ...]    # Detected risk signals
    metadata: PackageMetadata | None
```

### Recommendation

Risk recommendation enum.

```python
class Recommendation(Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"
    NOT_FOUND = "NOT_FOUND"
```

### Signal

Individual risk signal.

```python
@dataclass
class Signal:
    signal_type: SignalType  # TYPOSQUAT, AI_PATTERN, etc.
    weight: float            # -1.0 to 1.0
    metadata: dict[str, Any]
```

## Registry Clients

### PyPIClient

```python
from phantom_guard.registry import PyPIClient

async with PyPIClient() as client:
    metadata = await client.get_package_metadata("flask")
```

### NpmClient

```python
from phantom_guard.registry import NpmClient

async with NpmClient() as client:
    metadata = await client.get_package_metadata("express")
```

### CratesClient

```python
from phantom_guard.registry import CratesClient

async with CratesClient() as client:
    metadata = await client.get_package_metadata("serde")
```

## Cache

### Cache Class

```python
from phantom_guard.cache import Cache

cache = Cache(
    sqlite_path="/path/to/cache.db",  # None for memory-only
    memory_max_size=1000,
    memory_ttl=300.0,
    sqlite_ttl=3600.0,
)

async with cache:
    # Use cache
    await cache.set("pypi", "flask", data)
    result = await cache.get("pypi", "flask")
```

## Examples

### Custom Thresholds

```python
from phantom_guard import Detector
from phantom_guard.core.scorer import ThresholdConfig

config = ThresholdConfig(
    suspicious_threshold=0.3,  # Lower threshold
    high_risk_threshold=0.6,
)

detector = Detector(threshold_config=config)
```

### Progress Callback

```python
async def on_progress(completed: int, total: int):
    print(f"Progress: {completed}/{total}")

results = await detector.validate_batch(
    packages,
    on_progress=on_progress,
)
```
```

---

## Afternoon Session (3h)

### Objective
Complete additional documentation and contributing guide.

### Step 4: Create CI/CD Guide (45min)

Write `docs/CI_CD.md` with detailed examples for:
- GitHub Actions
- GitLab CI
- Jenkins
- Azure Pipelines
- CircleCI

### Step 5: Create Contributing Guide (1h)

```markdown
# CONTRIBUTING.md

# Contributing to Phantom Guard

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/phantom-guard/phantom-guard
cd phantom-guard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Code Standards

- **Type hints**: All functions must have type hints
- **Docstrings**: All public functions need docstrings
- **Tests**: All new code needs tests
- **Coverage**: Maintain >90% coverage
- **Linting**: Code must pass `ruff check`
- **Formatting**: Code must pass `ruff format`

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Write tests first (TDD)
4. Implement the feature
5. Run `ruff check src/` and `ruff format src/`
6. Run `mypy src/ --strict`
7. Run `pytest` (all tests must pass)
8. Submit PR with clear description

## Commit Messages

Use conventional commits:

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add tests
refactor: Refactor code
perf: Performance improvement
```

## Questions?

Open an issue or discussion on GitHub.
```

### Step 6: Validate Documentation (45min)

```bash
# Check all documentation files exist
ls -la README.md CONTRIBUTING.md docs/*.md

# Verify code examples work
python -c "
from phantom_guard import Detector
print('Import works')
"

# Run any code snippets from docs
# ...

# Check markdown rendering
pip install grip
grip README.md  # Preview in browser
```

### Step 7: Add Docstrings Check (30min)

```bash
# Verify all public functions have docstrings
python -c "
import phantom_guard
import inspect

for name, obj in inspect.getmembers(phantom_guard):
    if inspect.isfunction(obj) or inspect.isclass(obj):
        if not obj.__doc__:
            print(f'Missing docstring: {name}')
"
```

---

## End of Day Checklist

### Documentation Files
- [ ] README.md complete
- [ ] docs/USAGE.md created
- [ ] docs/API.md created
- [ ] docs/CI_CD.md created
- [ ] CONTRIBUTING.md created

### Quality
- [ ] All code examples tested
- [ ] All links valid
- [ ] Markdown renders correctly
- [ ] No spelling errors

### Git Commit

```bash
git add README.md CONTRIBUTING.md docs/
git commit -m "docs: Add comprehensive documentation

W4.5: Documentation complete

- Write README.md with all sections
- Create detailed USAGE.md guide
- Create API.md reference
- Create CI_CD.md integration guides
- Create CONTRIBUTING.md

All code examples tested and working."
```

---

## Day 5 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.5 | |
| README Sections | 10+ | |
| Code Examples | All tested | |
| API Documented | 100% public | |

---

## Tomorrow Preview

**Day 6 Focus**: Final Hostile Review + Release (W4.6 + W4.7)
- Run comprehensive hostile review
- Fix any issues found
- Build final release artifacts
- Upload to PyPI
- Verify installation works
