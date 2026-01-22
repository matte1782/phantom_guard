# phantom-guard-pip

> pip install wrapper with slopsquatting protection

[![PyPI](https://img.shields.io/badge/PyPI-v0.3.0-blue)](https://pypi.org/project/phantom-guard-pip/)
[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)](.)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

A drop-in replacement for `pip install` that validates packages against AI-hallucinated package names (slopsquatting attacks) before installation.

## The Problem

AI coding assistants sometimes suggest package names that don't exist. Attackers exploit this by:
1. Observing which fake packages AI suggests
2. Registering those names with malicious code
3. Waiting for developers to install them

`phantom-pip` intercepts `pip install` commands and validates packages before they reach your system.

## Installation

```bash
pip install phantom-guard-pip
```

## Quick Start

```bash
# Use phantom-pip instead of pip
phantom-pip install flask requests django

# It validates packages before delegating to pip
# If a package is suspicious, you'll be prompted:
#
#   Package: flask-gpt-helper
#   Status: HIGH RISK
#   Risk Score: 0.92
#   Signals:
#     - Package not found on PyPI
#     - Matches hallucination pattern
#
#   Proceed anyway? [y/N]
```

## Usage

### Basic Commands

```bash
# Install with validation
phantom-pip install flask

# Install multiple packages
phantom-pip install flask requests django

# Auto-approve all packages (CI mode)
phantom-pip install -y flask

# Skip validation entirely
phantom-pip install --skip-validation flask

# Override mode for this command
phantom-pip install --mode=warn flask
phantom-pip install --mode=block flask

# Override threshold
phantom-pip install --threshold=0.8 flask
```

### Passthrough Commands

These commands pass directly to pip without validation:

```bash
phantom-pip list
phantom-pip freeze
phantom-pip show flask
phantom-pip uninstall flask
```

### Configuration Management

```bash
# Show current configuration
phantom-pip config --show

# Create default config file
phantom-pip config --init
```

## Configuration

Configuration file location: `~/.phantom-guard/pip.yaml`

```yaml
# Enable/disable validation
enabled: true

# Mode: interactive | warn | block | silent
#   interactive: Prompt for confirmation on risky packages
#   warn: Show warnings but proceed
#   block: Block risky packages, fail install
#   silent: Log only, no output
mode: interactive

# Auto-approve packages without prompting
auto_approve: false

# Risk score threshold (0.0 - 1.0)
# Packages scoring above this are flagged
threshold: 0.6

# Registry to validate against
registry: pypi

# Network timeout in seconds
timeout: 30

# Packages to always allow (glob patterns supported)
allowlist:
  - my-company-*
  - internal-utils

# Packages to always block
blocklist:
  - known-malware
  - suspicious-pkg
```

## Modes

| Mode | Behavior |
|------|----------|
| `interactive` | Shows risk assessment, prompts for confirmation |
| `warn` | Shows risk assessment, proceeds without prompting |
| `block` | Blocks packages above threshold, fails install |
| `silent` | No output, logs only (for CI with external monitoring) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (or pip's exit code) |
| 1 | Blocked by policy or general error |
| 2 | Security error (malicious input detected) |

## Signals Detected

phantom-guard-pip validates against these risk signals:

- **Package Not Found**: Package doesn't exist on registry
- **Hallucination Pattern**: Name matches common AI hallucination patterns
- **Typosquatting**: Similar to popular package names
- **Namespace Squatting**: Mimics organization namespaces
- **Low Downloads**: Suspiciously low download count
- **Recent Creation**: Very recently published package
- **Version Spike**: Rapid version releases

## Shell Alias (Optional)

To use `phantom-pip` as your default pip:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias pip="phantom-pip"
```

## CI/CD Integration

For CI environments, use block mode with auto-approve disabled:

```yaml
# .github/workflows/ci.yml
- name: Install dependencies
  run: |
    pip install phantom-guard-pip
    phantom-pip install --mode=block -r requirements.txt
```

## Security

- **No shell=True**: All subprocess calls use `shell=False`
- **Input Validation**: Package names are validated against injection attacks
- **Argument Sanitization**: Shell metacharacters are rejected
- **Exit Code Preservation**: pip's exit code is always preserved

## Known Limitations

1. **Async/Sync**: The CLI calls phantom-guard's async validation function synchronously. This means validation may be skipped if phantom-guard core is installed but async runtime isn't configured. Use `phantom-guard` CLI directly for full async support.

2. **Version Specifiers**: Complex version specifiers are parsed but the base package name is extracted for validation.

## Development

```bash
# Clone and install in development mode
git clone https://github.com/matte1782/phantom_guard
cd phantom-guard/phantom-guard-pip
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/phantom_pip --cov-report=term-missing

# Lint
ruff check src/ tests/

# Type check
mypy src/ --strict
```

## Related Projects

- [phantom-guard](https://pypi.org/project/phantom-guard/) - Core detection library
- [phantom-guard-vscode](https://marketplace.visualstudio.com/items?itemName=phantom-guard.phantom-guard-vscode) - VS Code extension
- [phantom-guard-action](https://github.com/matte1782/phantom-guard-action) - GitHub Action

## License

MIT - see [LICENSE](./LICENSE)
