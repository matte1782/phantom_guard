<p align="center">
  <a href="https://pypi.org/project/phantom-guard/"><img src="https://img.shields.io/pypi/v/phantom-guard?color=blue&label=PyPI" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/phantom-guard/"><img src="https://img.shields.io/pypi/pyversions/phantom-guard?color=green" alt="Python Versions"></a>
  <a href="https://github.com/matte1782/phantom_guard/blob/main/LICENSE"><img src="https://img.shields.io/github/license/matte1782/phantom_guard?color=yellow" alt="MIT License"></a>
  <a href="https://github.com/matte1782/phantom_guard/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/matte1782/phantom_guard/ci.yml?label=Tests" alt="Tests"></a>
  <a href="https://codecov.io/gh/matte1782/phantom_guard"><img src="https://img.shields.io/codecov/c/github/matte1782/phantom_guard?color=brightgreen" alt="Coverage"></a>
</p>

<h1 align="center">Phantom Guard</h1>

<p align="center">
  <strong>Detect AI-hallucinated package attacks before they compromise your supply chain.</strong>
</p>

<p align="center">
  <a href="https://matte1782.github.io/phantom_guard/"><strong>Try the Interactive Demo</strong></a>
</p>

<p align="center">
  <a href="#the-problem">The Problem</a> •
  <a href="#the-solution">The Solution</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#cli-reference">CLI Reference</a> •
  <a href="#python-api">Python API</a> •
  <a href="#cicd-integration">CI/CD Integration</a>
</p>

---

## The Problem

### What is Slopsquatting?

**Slopsquatting** is a new class of supply chain attack that exploits AI code assistants. When developers use AI tools like ChatGPT, Claude, or Copilot to write code, these models sometimes "hallucinate" package names that don't exist.

```python
# AI might suggest this code:
from flask_gpt_helper import create_ai_endpoint  # This package doesn't exist!
```

Attackers monitor package registries for these hallucinated names and register malicious packages before developers realize the package doesn't exist. When the developer runs `pip install`, they unknowingly install malware.

### The Attack Vector

1. **AI Hallucination**: Developer asks AI for help, AI suggests non-existent package `flask-gpt-helper`
2. **Attacker Registration**: Attacker registers `flask-gpt-helper` with malicious code
3. **Developer Installation**: Developer runs `pip install flask-gpt-helper`
4. **Compromise**: Malicious package executes, stealing credentials, injecting backdoors, or exfiltrating data

### Why This Matters

- **30%+ of AI-generated code** contains package references that don't exist
- **Typosquatting** attacks have been successful for years; AI makes this worse
- Traditional security tools don't catch packages that *look* legitimate but are phantom attacks
- Once a malicious package is installed, the damage is done

---

## The Solution

Phantom Guard detects potentially dangerous packages **before installation** by analyzing:

| Detection Method | Description |
|-----------------|-------------|
| **Registry Verification** | Checks if the package actually exists on PyPI, npm, or crates.io |
| **Pattern Analysis** | Identifies AI hallucination patterns like `flask-gpt-helper`, `easy-requests`, `py-openai-utils` |
| **Typosquat Detection** | Uses Levenshtein distance to find suspicious similarities to popular packages |
| **Metadata Analysis** | Flags packages with few downloads, recent creation, or missing maintainers |
| **Multi-Signal Scoring** | Combines 10+ risk signals into a single actionable score |

---

## Quick Start

### Installation

```bash
pip install phantom-guard
```

### Basic Usage

```bash
# Validate a single package
phantom-guard validate flask-gpt-helper

# Check your requirements file
phantom-guard check requirements.txt

# Validate npm packages
phantom-guard validate lodash-utils --registry npm

# Check Cargo.toml for Rust projects
phantom-guard check Cargo.toml
```

### Example Output

```
$ phantom-guard validate flask-gpt-helper

  Phantom Guard v0.1.0

  Package: flask-gpt-helper
  Registry: pypi
  Status: HIGH RISK

  Signals:
    - Package not found on PyPI (weight: 0.90)
    - Matches hallucination pattern: Popular package + AI + helper (weight: 0.85)
    - Possible typosquat of 'flask' (distance: 2) (weight: 0.76)

  Risk Score: 0.92
  Recommendation: DO NOT INSTALL
```

---

## Features

### Multi-Registry Support

Phantom Guard validates packages across major package registries:

| Registry | File Types | Auto-Detection |
|----------|-----------|----------------|
| **PyPI** (Python) | `requirements.txt`, `pyproject.toml`, `Pipfile` | Yes |
| **npm** (JavaScript) | `package.json` | Yes |
| **crates.io** (Rust) | `Cargo.toml` | Yes |

### Risk Levels

Phantom Guard classifies packages into four risk levels:

| Level | Exit Code | Description | Action |
|-------|-----------|-------------|--------|
| **SAFE** | 0 | Package exists, no suspicious signals | Proceed with installation |
| **SUSPICIOUS** | 1 | Some risk signals detected | Review before installing |
| **HIGH_RISK** | 2 | Strong hallucination indicators | Do not install |
| **NOT_FOUND** | 3 | Package does not exist | Verify package name |

### Detection Signals

Phantom Guard analyzes packages for multiple risk indicators:

| Signal Type | Weight | Description |
|-------------|--------|-------------|
| `NOT_FOUND` | 0.90 | Package doesn't exist on registry |
| `HALLUCINATION_PATTERN` | 0.30-0.85 | Matches known AI hallucination patterns |
| `TYPOSQUAT` | 0.30-0.95 | Similar to popular package name |
| `RECENTLY_CREATED` | 0.40 | Package created less than 30 days ago |
| `LOW_DOWNLOADS` | 0.30 | Less than 1,000 downloads/month |
| `NO_REPOSITORY` | 0.25 | No source repository linked |
| `NO_MAINTAINER` | 0.30 | No maintainers listed |
| `FEW_RELEASES` | 0.20 | Less than 3 releases |
| `SHORT_DESCRIPTION` | 0.15 | Description under 10 characters |
| `POPULAR_PACKAGE` | -0.50 | Known popular package (reduces risk) |
| `LONG_HISTORY` | -0.20 | Package older than 1 year (reduces risk) |

---

## CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `validate <package>` | Validate a single package |
| `check <file>` | Check all packages in a dependency file |
| `cache clear` | Clear the local cache |
| `cache stats` | Show cache statistics |
| `cache path` | Display cache file location |

### Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | `-V` | Show version and exit |
| `--help` | | Show help and exit |

### Validate Command Options

```bash
phantom-guard validate <package> [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--registry` | `-r` | `pypi` | Target registry: `pypi`, `npm`, `crates` |
| `--verbose` | `-v` | `false` | Show detailed signal information |
| `--quiet` | `-q` | `false` | Show only the result |
| `--no-banner` | | `false` | Hide the banner |
| `--plain` | | `false` | Disable colors (plain text output) |

### Check Command Options

```bash
phantom-guard check <file> [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--registry` | `-r` | auto | Override registry detection |
| `--fail-on` | | `high_risk` | Exit non-zero on: `suspicious`, `high_risk` |
| `--ignore` | | | Comma-separated packages to skip |
| `--parallel` | | `10` | Number of concurrent validations |
| `--fail-fast` | | `false` | Stop on first HIGH_RISK package |
| `--output` | `-o` | `text` | Output format: `text`, `json` |
| `--quiet` | `-q` | `false` | Minimal output |
| `--no-banner` | | `false` | Hide the banner |
| `--plain` | | `false` | Disable colors |

### Examples

```bash
# Verbose output with all signals
phantom-guard validate some-package -v

# Check requirements with JSON output
phantom-guard check requirements.txt -o json

# Fail on any suspicious package in CI
phantom-guard check requirements.txt --fail-on suspicious

# Skip known packages and run fast
phantom-guard check requirements.txt --ignore boto3,requests --parallel 20

# Stop immediately on first high-risk package
phantom-guard check requirements.txt --fail-fast

# Plain output for scripting
phantom-guard validate flask-helper --plain --quiet
```

---

## CI/CD Integration

### GitHub Actions

Add Phantom Guard to your CI pipeline to catch dangerous packages before they're installed:

```yaml
# .github/workflows/security.yml
name: Security Check

on:
  push:
    paths:
      - 'requirements.txt'
      - 'pyproject.toml'
      - 'package.json'
      - 'Cargo.toml'
  pull_request:
    paths:
      - 'requirements.txt'
      - 'pyproject.toml'
      - 'package.json'
      - 'Cargo.toml'

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

      - name: Scan Python dependencies
        run: phantom-guard check requirements.txt --fail-on suspicious

      - name: Scan JavaScript dependencies (if exists)
        if: hashFiles('package.json') != ''
        run: phantom-guard check package.json --fail-on suspicious
```

### Pre-commit Hook

Prevent dangerous packages from being committed:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: phantom-guard
        name: Phantom Guard
        entry: phantom-guard check
        language: system
        files: ^(requirements.*\.txt|pyproject\.toml|package\.json|Cargo\.toml)$
        pass_filenames: true
```

Install the hook:

```bash
pip install pre-commit
pre-commit install
```

### GitLab CI

```yaml
# .gitlab-ci.yml
phantom-guard:
  stage: security
  image: python:3.11
  script:
    - pip install phantom-guard
    - phantom-guard check requirements.txt --fail-on suspicious
  only:
    changes:
      - requirements.txt
      - pyproject.toml
```

---

## Python API

Phantom Guard provides a Python API for programmatic access.

### Single Package Validation (Async)

```python
import asyncio
from phantom_guard.core import validate_package, PackageRisk, Recommendation

async def check_package(name: str) -> None:
    """Validate a single package asynchronously."""
    risk: PackageRisk = await validate_package(name, registry="pypi")

    print(f"Package: {risk.name}")
    print(f"Exists: {risk.exists}")
    print(f"Risk Score: {risk.risk_score:.2f}")
    print(f"Recommendation: {risk.recommendation.value}")

    if risk.signals:
        print("Signals:")
        for signal in risk.signals:
            print(f"  - {signal.message} (weight: {signal.weight:.2f})")

    # Take action based on recommendation
    if risk.recommendation == Recommendation.HIGH_RISK:
        print("WARNING: Do not install this package!")
    elif risk.recommendation == Recommendation.SUSPICIOUS:
        print("CAUTION: Review this package before installing.")
    else:
        print("OK: Package appears safe.")

asyncio.run(check_package("flask-gpt-helper"))
```

### Single Package Validation (Sync)

```python
from phantom_guard.core import validate_package_sync, Recommendation

# Synchronous wrapper for non-async code
risk = validate_package_sync("requests", registry="pypi")

if risk.recommendation == Recommendation.SAFE:
    print(f"{risk.name} is safe to install")
```

### Batch Validation (Async)

```python
import asyncio
from phantom_guard.core import validate_batch

async def scan_requirements() -> None:
    """Scan multiple packages concurrently."""
    packages = [
        "flask",
        "flask-gpt-helper",  # Suspicious
        "reqeusts",          # Typosquat of 'requests'
        "django",
        "numpy",
    ]

    results = await validate_batch(
        packages,
        registry="pypi",
        concurrency=10,  # Max parallel validations
    )

    for risk in results:
        status = risk.recommendation.value.upper()
        print(f"[{status:10}] {risk.name} (score: {risk.risk_score:.2f})")

asyncio.run(scan_requirements())
```

### Batch Validation (Sync)

```python
from phantom_guard.core import validate_batch_sync

# Synchronous wrapper
results = validate_batch_sync(
    ["flask", "django", "pyramid"],
    registry="pypi",
    concurrency=5,
)

for result in results:
    print(f"{result.name}: {result.recommendation.value}")
```

### Typosquat Detection

```python
from phantom_guard.core import detect_typosquat, check_typosquat

# Get signals for typosquat detection
signals = detect_typosquat("reqeusts", registry="pypi")
for signal in signals:
    print(f"Typosquat detected: {signal.message}")
    print(f"  Target: {signal.metadata.get('target')}")
    print(f"  Similarity: {signal.metadata.get('similarity')}")

# Simple check returning best match
match = check_typosquat("numpyy", registry="pypi")
if match:
    print(f"'{match.target}' might be the intended package (distance: {match.distance})")
```

### Types Reference

```python
from phantom_guard.core import (
    # Core types
    PackageRisk,       # Complete risk assessment
    Signal,            # Individual risk signal
    Recommendation,    # SAFE, SUSPICIOUS, HIGH_RISK, NOT_FOUND
    SignalType,        # NOT_FOUND, TYPOSQUAT, HALLUCINATION_PATTERN, etc.

    # Functions
    validate_package,       # Async single package validation
    validate_package_sync,  # Sync single package validation
    validate_batch,         # Async batch validation
    validate_batch_sync,    # Sync batch validation
    detect_typosquat,       # Typosquat signal detection
)
```

---

## Performance

Phantom Guard is optimized for speed with an intelligent caching layer:

| Operation | Time | Condition |
|-----------|------|-----------|
| Single package (cached) | <10ms | P99 latency |
| Single package (uncached) | <200ms | P99 latency |
| 50 packages (batch) | <5s | P99, concurrent |
| Pattern matching | <1ms | P99, in-memory |

### Caching

Results are cached locally to speed up repeated checks:

```bash
# Show cache location and size
phantom-guard cache path

# Display cache statistics
phantom-guard cache stats

# Clear entire cache
phantom-guard cache clear

# Clear only PyPI entries
phantom-guard cache clear --registry pypi
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NO_COLOR` | | Disable colored output when set |
| `PHANTOM_GUARD_CACHE_DIR` | Platform default | Override cache directory |
| `PHANTOM_GUARD_TIMEOUT` | `30` | API request timeout in seconds |

### Cache Location

The cache is stored in a platform-specific location:

| Platform | Default Location |
|----------|-----------------|
| Linux | `~/.cache/phantom-guard/cache.db` |
| macOS | `~/Library/Caches/phantom-guard/cache.db` |
| Windows | `%LOCALAPPDATA%\phantom-guard\cache.db` |

---

## Security

Phantom Guard is designed with security as a priority:

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **No shell execution** | All operations use Python libraries, never `subprocess.call()` with shell=True |
| **No eval/exec** | Package names and data are never executed as code |
| **Input validation** | All inputs are validated before processing |
| **Minimal dependencies** | Only well-established, audited dependencies |
| **No network for patterns** | Pattern matching is entirely local, no data exfiltration |
| **Read-only registry access** | Only reads public metadata, never writes or modifies |

### Threat Model

Phantom Guard protects against:

- AI-hallucinated package names
- Typosquatting attacks
- Newly registered malicious packages
- Packages mimicking popular libraries

It does **not** protect against:

- Already-compromised legitimate packages
- Malicious code in established packages
- Supply chain attacks on dependencies of dependencies

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/matte1782/phantom_guard.git
cd phantom-guard

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only (fast)
pytest -m unit

# Integration tests (requires network)
pytest -m integration

# With coverage
pytest --cov=phantom_guard --cov-report=html
```

---

## License

Phantom Guard is released under the [MIT License](LICENSE).

```
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

---

## Acknowledgments

Phantom Guard is built on the shoulders of giants:

- **[Rich](https://github.com/Textualize/rich)** - Beautiful terminal output
- **[Typer](https://github.com/tiangolo/typer)** - CLI framework built on Click
- **[HTTPX](https://github.com/encode/httpx)** - Modern async HTTP client
- **[hugovk/top-pypi-packages](https://hugovk.github.io/top-pypi-packages/)** - PyPI download statistics

---

<p align="center">
  <strong>Stay vigilant. Stay protected.</strong>
</p>

<p align="center">
  Made with care to protect the open source community.
</p>
