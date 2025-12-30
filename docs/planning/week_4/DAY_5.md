# Week 4 - Day 5: Documentation (OPTIMIZED)

> **Date**: Day 5 (Week 4)
> **Focus**: Expand README and create user documentation
> **Tasks**: W4.5
> **Hours**: 6 hours
> **Status**: OPTIMIZED based on hostile review findings
> **Dependencies**: W4.4 (Packaging) complete

---

## Pre-Existing State Analysis

### What Already Exists

| File | Status | Lines | Target |
|:-----|:-------|:------|:-------|
| `README.md` | ✅ Minimal | 40 | 320+ |
| `docs/USAGE.md` | ❌ MISSING | 0 | 200+ |
| `docs/API.md` | ❌ MISSING | 0 | 150+ |
| `docs/CI_CD.md` | ❌ MISSING | 0 | 150+ |
| `CONTRIBUTING.md` | ❌ MISSING | 0 | 80+ |

### Current README.md (40 lines)

```markdown
# Phantom Guard

Detect AI-hallucinated package attacks (slopsquatting).

## Installation
pip install phantom-guard

## Usage
phantom-guard validate flask
phantom-guard check requirements.txt

## Development
pip install -e ".[dev]"
pytest

## License
MIT
```

**Issues:**
- No badges
- No problem explanation
- No feature list
- No CLI reference
- No API examples
- No CI/CD guides
- No performance info

---

## Revised Task Breakdown

### Morning Session (3h) - README.md Expansion

#### Step 1: Create Complete README.md (2h)

Expand from 40 → 320+ lines with all sections:

```markdown
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

## The Problem

When AI coding assistants (ChatGPT, Claude, Copilot) hallucinate package names,
attackers create those packages with malicious code. When developers install
the suggested package, they get compromised.

**This is called "slopsquatting"** - and it's a growing supply chain attack vector.

## The Solution

Phantom Guard analyzes package names and metadata to detect:

- **Typosquats** of popular packages (e.g., `reqeusts` → `requests`)
- **AI-hallucination patterns** (e.g., `flask-gpt-helper`, `easy-numpy`)
- **Non-existent packages** being installed
- **Suspicious metadata** (new packages, no downloads, single maintainer)

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

### Check Requirements File

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
| NOT_FOUND | 3 | Package doesn't exist in registry |

### Detection Signals

- **Typosquat Detection**: Levenshtein distance against top 3000 popular packages
- **Pattern Matching**: AI-related suffixes, helper/wrapper patterns
- **Metadata Analysis**: Creation date, download counts, maintainer count
- **Existence Verification**: Confirm package exists in registry

## CLI Reference

### Commands

```bash
phantom-guard validate <package> [OPTIONS]  # Check single package
phantom-guard check <file> [OPTIONS]        # Batch check from file
phantom-guard cache stats|clear|path        # Cache management
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
| `--no-banner` | Hide banner for clean output |

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
        run: phantom-guard check requirements.txt --fail-on suspicious
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

## Python API

```python
import asyncio
from phantom_guard import Detector
from phantom_guard.core.types import Recommendation

async def main():
    detector = Detector()

    # Validate single package
    result = await detector.validate("flask")

    if result.recommendation == Recommendation.HIGH_RISK:
        print(f"Warning: {result.name} is high risk!")
        for signal in result.signals:
            print(f"  - {signal.message}")

    # Batch validation
    results = await detector.validate_batch([
        "flask",
        "reqeusts",        # typosquat
        "flask-gpt-helper", # hallucination
    ])

    for r in results:
        print(f"{r.name}: {r.recommendation.value}")

asyncio.run(main())
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
phantom-guard cache path   # View cache path
phantom-guard cache stats  # View statistics
phantom-guard cache clear  # Clear all cache
```

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `PHANTOM_GUARD_CACHE_DIR` | Cache directory | `~/.cache/phantom-guard` |
| `PHANTOM_GUARD_CACHE_TTL` | Cache TTL (seconds) | `3600` |
| `PHANTOM_GUARD_TIMEOUT` | API timeout (seconds) | `10` |

## Security

Phantom Guard is designed with security in mind:

- No shell command execution
- No eval/exec usage
- All inputs validated
- Rate limit handling for registries
- Graceful degradation on errors

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [hugovk/top-pypi-packages](https://github.com/hugovk/top-pypi-packages) for PyPI download data
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [Typer](https://github.com/tiangolo/typer) for CLI framework
```

#### Step 2: Verify README Examples Work (1h)

```bash
# Test all code examples from README
phantom-guard --version
phantom-guard validate flask
phantom-guard validate flask-gpt-helper
phantom-guard check requirements.txt --output json 2>/dev/null | head -20

# Test Python API example
python -c "
import asyncio
from phantom_guard import Detector

async def main():
    detector = Detector()
    result = await detector.validate('flask')
    print(f'{result.name}: {result.recommendation.value}')

asyncio.run(main())
"
```

---

### Afternoon Session (3h) - Additional Documentation

#### Step 3: Create docs/USAGE.md (1h)

Detailed usage guide with:
- Installation options (pip, source)
- Command reference
- File format support
- Output formats
- Cache management
- Advanced usage patterns

#### Step 4: Create docs/API.md (45min)

Python API reference:
- Detector class
- PackageRisk dataclass
- Recommendation enum
- Signal types
- Registry clients
- Cache classes

#### Step 5: Create docs/CI_CD.md (30min)

CI/CD integration guides for:
- GitHub Actions
- GitLab CI
- Jenkins
- Azure Pipelines
- CircleCI
- Pre-commit hooks

#### Step 6: Create CONTRIBUTING.md (30min)

```markdown
# Contributing to Phantom Guard

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone repository
git clone https://github.com/phantom-guard/phantom-guard
cd phantom-guard

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/ --strict

# Linting
ruff check src/
ruff format src/
```

## Code Standards

- **Type hints**: All functions must have type hints
- **Docstrings**: All public functions need docstrings
- **Tests**: All new code needs tests (TDD preferred)
- **Coverage**: Maintain 100% coverage
- **Linting**: Code must pass `ruff check`
- **Types**: Code must pass `mypy --strict`

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Write tests first (TDD)
4. Implement the feature
5. Run `ruff check src/ && ruff format src/`
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
build: Build system changes
```

## Questions?

Open an issue or discussion on GitHub.
```

#### Step 7: Validate All Documentation (15min)

```bash
# Check all files exist
ls -la README.md CONTRIBUTING.md docs/

# Verify README rendering
pip install grip
grip README.md --export README.html

# Open in browser to verify
```

---

## End of Day Checklist

### Documentation Files
- [ ] README.md expanded (40 → 320+ lines)
- [ ] docs/USAGE.md created
- [ ] docs/API.md created
- [ ] docs/CI_CD.md created
- [ ] CONTRIBUTING.md created

### Quality Checks
- [ ] All code examples tested
- [ ] All CLI examples work
- [ ] Python API examples work
- [ ] Markdown renders correctly
- [ ] No broken links

### Git Commit

```bash
git add README.md CONTRIBUTING.md docs/
git commit -m "docs: Add comprehensive documentation

W4.5: Documentation COMPLETE

- Expand README.md from 40 → 320+ lines
  - Add badges
  - Add problem/solution explanation
  - Add full CLI reference
  - Add CI/CD integration examples
  - Add Python API examples
  - Add performance table
- Create docs/USAGE.md detailed guide
- Create docs/API.md reference
- Create docs/CI_CD.md integration guides
- Create CONTRIBUTING.md

All code examples tested and working."
```

---

## Day 5 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W4.5 | |
| README Lines | 320+ | |
| Code Examples Tested | All | |
| Docs Files Created | 4+ | |

---

## Key Insight from Hostile Review

README.md is **only 40 lines** - critically minimal for a public release.

Must expand to include:
- Problem/solution explanation
- Full CLI reference
- CI/CD integration guides
- Python API examples
- Performance information

---

## Tomorrow Preview

**Day 6 Focus**: UI Optimization + Hostile Review + Release (W4.6 + W4.7)
- Optimize CLI output and Rich formatting
- Add progress animations
- Run final hostile review
- Build final artifacts
- Upload to PyPI
- Verify installation
