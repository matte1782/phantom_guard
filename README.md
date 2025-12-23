# Phantom Guard

> Detect AI-hallucinated package attacks before they compromise your code.

[![PyPI version](https://badge.fury.io/py/phantom-guard.svg)](https://badge.fury.io/py/phantom-guard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## The Problem

AI coding assistants (Copilot, Claude, Cursor) sometimes hallucinate package names that don't exist. Attackers exploit this by:

1. Identifying commonly hallucinated package names
2. Registering those phantom names on PyPI/npm with malware
3. Waiting for developers to install the AI-suggested packages

This attack is called **slopsquatting**.

**The numbers are alarming:**
- 20% of AI-generated code references non-existent packages
- 43% of hallucinated packages appear consistently (predictable!)
- One install = compromised machine

## The Solution

Phantom Guard validates packages before installation:

```bash
pip install phantom-guard
phantom-guard check requirements.txt
```

**Output:**
```
Checking 15 packages...

 SAFE     flask (63 releases, 180M downloads/month)
 SAFE     requests (157 releases, 940M downloads/month)
 BLOCKED  flask-gpt-helper (does not exist!)
 SUSPICIOUS  gpt4-api (3 releases, 42 downloads, no repo)

 Result: 2 issues found
 - 1 non-existent package (slopsquatting risk)
 - 1 suspicious package (review recommended)
```

## Installation

```bash
pip install phantom-guard
```

## Quick Start

### Check a requirements file

```bash
phantom-guard check requirements.txt
phantom-guard check package.json
```

### Check a single package

```bash
phantom-guard check-package flask-gpt-helper
```

### Use as a library

```python
from phantom_guard import check, check_requirements

# Single package
result = check("flask-gpt-helper")
print(result.risk_level)  # RiskLevel.CRITICAL

# Requirements file
results = check_requirements("requirements.txt")
for pkg in results.blocked:
    print(f"BLOCKED: {pkg.name} - {pkg.signals}")
```

## Detection Signals

Phantom Guard analyzes multiple signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| Package exists | Critical | Non-existent = immediate block |
| Package age | High | <30 days = suspicious |
| Download count | High | <1000/month = suspicious |
| Repository link | Medium | No repo = suspicious |
| Release count | Medium | <3 releases = suspicious |
| Maintainer count | Low | Single maintainer = minor flag |
| Name pattern | High | Matches hallucination patterns |

## Supported Registries

- PyPI (Python)
- npm (JavaScript) - coming soon
- crates.io (Rust) - coming soon

## Configuration

Create `~/.phantom-guard.yaml`:

```yaml
# Risk threshold (0.0 - 1.0)
risk_threshold: 0.7

# Action on suspicious packages
on_suspicious: warn  # warn, block, ignore

# Block non-existent packages
block_not_found: true

# Enable caching
cache_enabled: true
cache_ttl_hours: 24
```

## CI/CD Integration

### GitHub Action

```yaml
- uses: phantom-guard/action@v1
  with:
    file: requirements.txt
    fail-on: suspicious
```

### Pre-commit Hook

```yaml
repos:
  - repo: https://github.com/phantom-guard/phantom-guard
    rev: v0.1.0
    hooks:
      - id: phantom-guard
```

## Performance

| Operation | Time |
|-----------|------|
| Single package (cached) | <10ms |
| Single package (uncached) | <200ms |
| 50 packages (concurrent) | <5s |

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

Priority areas:
- Hallucination pattern contributions
- New registry support
- False positive reports

## Security

This is a security tool. If you find a vulnerability, please report it privately.

See [SECURITY.md](SECURITY.md).

## License

MIT License. See [LICENSE](LICENSE).

## Acknowledgments

- Research on AI code hallucinations that inspired this project
- The security community for documenting slopsquatting attacks
