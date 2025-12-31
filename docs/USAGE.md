# Phantom Guard Usage Guide

A comprehensive guide to using Phantom Guard for detecting AI-hallucinated package attacks (slopsquatting).

---

## Table of Contents

1. [Installation](#installation)
2. [Command Reference](#command-reference)
3. [File Format Support](#file-format-support)
4. [Output Formats](#output-formats)
5. [Cache Management](#cache-management)
6. [Advanced Usage Patterns](#advanced-usage-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Option 1: Install from PyPI

The simplest way to install Phantom Guard:

```bash
pip install phantom-guard
```

### Option 2: Install from Source

Clone the repository and install:

```bash
git clone https://github.com/phantom-guard/phantom-guard.git
cd phantom-guard
pip install .
```

### Option 3: Development Install

For development with all test dependencies:

```bash
git clone https://github.com/phantom-guard/phantom-guard.git
cd phantom-guard
pip install -e ".[dev]"
```

This installs Phantom Guard in editable mode with development dependencies including:
- pytest, pytest-cov, pytest-asyncio (testing)
- mypy (type checking)
- ruff (linting)
- hypothesis (property-based testing)

### Verify Installation

After installation, verify it works:

```bash
phantom-guard --version
```

You should see the Phantom Guard banner with version information.

### Requirements

- Python 3.11 or higher
- Network access to package registries (PyPI, npm, crates.io)

---

## Command Reference

### Single Package Validation

Validate a single package for supply chain risks:

```bash
phantom-guard validate <package> [OPTIONS]
```

**Arguments:**
- `<package>`: Package name to validate (required)

**Options:**
- `-r, --registry`: Registry to check: `pypi`, `npm`, or `crates` (default: `pypi`)
- `-v, --verbose`: Show detailed signal information
- `-q, --quiet`: Show only the result, minimal output
- `--no-banner`: Hide the Phantom Guard banner
- `--plain`: Disable colors (plain text output)

**Examples:**

```bash
# Validate a PyPI package
phantom-guard validate requests

# Validate an npm package
phantom-guard validate express --registry npm

# Validate a Rust crate
phantom-guard validate serde --registry crates

# Verbose output with all signals
phantom-guard validate flask --verbose

# Quiet mode for scripts
phantom-guard validate numpy --quiet
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Package is SAFE |
| 1 | Package is SUSPICIOUS |
| 2 | Package is HIGH_RISK |
| 3 | Package NOT_FOUND |
| 4 | Input error (invalid package name or registry) |
| 5 | Runtime error (network issues, etc.) |

### Batch Validation (Check Command)

Check an entire dependency file for risky packages:

```bash
phantom-guard check <file> [OPTIONS]
```

**Arguments:**
- `<file>`: Path to dependency file (required)

**Options:**
- `-r, --registry`: Override auto-detected registry
- `--fail-on`: Exit non-zero on: `suspicious` or `high_risk`
- `--ignore`: Comma-separated list of packages to skip
- `--parallel`: Number of concurrent validations (default: 10)
- `--fail-fast`: Stop on first HIGH_RISK package
- `-o, --output`: Output format: `text` or `json` (default: `text`)
- `-q, --quiet`: Minimal output
- `--no-banner`: Hide banner
- `--plain`: Disable colors

**Examples:**

```bash
# Check a requirements.txt file
phantom-guard check requirements.txt

# Check package.json with JSON output for CI
phantom-guard check package.json --output json

# Check Cargo.toml and fail on suspicious packages
phantom-guard check Cargo.toml --fail-on suspicious

# Skip specific packages
phantom-guard check requirements.txt --ignore "my-internal-pkg,dev-tool"

# High concurrency for large files
phantom-guard check requirements.txt --parallel 20

# Stop immediately on high-risk package
phantom-guard check requirements.txt --fail-fast
```

### Cache Management

Manage the local cache for package metadata:

```bash
phantom-guard cache <command> [OPTIONS]
```

**Subcommands:**

#### Show Cache Statistics

```bash
phantom-guard cache stats
```

Displays a table with:
- Registry name
- Number of cached entries
- Cache size in bytes
- Hit rate (if available)

#### Clear Cache

```bash
phantom-guard cache clear [OPTIONS]
```

**Options:**
- `-r, --registry`: Only clear cache for specific registry
- `-f, --force`: Skip confirmation prompt

**Examples:**

```bash
# Clear entire cache (with confirmation)
phantom-guard cache clear

# Clear only PyPI cache
phantom-guard cache clear --registry pypi

# Force clear without confirmation (for scripts)
phantom-guard cache clear --force
```

#### Show Cache Path

```bash
phantom-guard cache path
```

Shows the location of the cache database file:
- Linux: `~/.cache/phantom-guard/cache.db`
- macOS: `~/Library/Caches/phantom-guard/cache.db`
- Windows: `C:\Users\<user>\AppData\Local\phantom-guard\Cache\cache.db`

---

## File Format Support

Phantom Guard auto-detects file formats based on filename. It supports:

### requirements.txt (Python/PyPI)

Standard Python requirements file format:

```text
# Production dependencies
flask==2.0.0
requests>=2.28.0,<3.0.0
sqlalchemy[asyncio]>=2.0

# Development dependencies
pytest>=7.0.0
black  # code formatter

# Skipped entries (URLs, options)
-e ./my-local-package
https://example.com/package.whl
--index-url https://pypi.org/simple
```

**Supported syntax:**
- Simple names: `flask`
- Version specs: `flask==2.0.0`, `flask>=2.0,<3.0`
- Extras: `flask[async]`
- Comments: `# comment` or inline `flask  # comment`

**Skipped entries:**
- URLs (`http://`, `https://`, `git+`)
- Editable installs (`-e`)
- Options (`--index-url`, `-r`, etc.)

### package.json (JavaScript/npm)

npm package manifest:

```json
{
  "name": "my-project",
  "dependencies": {
    "express": "^4.18.0",
    "@types/node": "^18.0.0"
  },
  "devDependencies": {
    "typescript": "~5.0.0",
    "jest": ">=29.0.0"
  }
}
```

**Parsed sections:**
- `dependencies`
- `devDependencies`

**Supported:**
- Scoped packages: `@types/node`, `@babel/core`
- All npm version specs: `^1.0.0`, `~1.0.0`, `>=1.0.0`, `*`

### Cargo.toml (Rust/crates.io)

Rust package manifest:

```toml
[package]
name = "my-project"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }

[dev-dependencies]
criterion = "0.5"
```

**Parsed sections:**
- `dependencies`
- `dev-dependencies`

**Supported:**
- Simple version strings: `serde = "1.0"`
- Complex specifications: `tokio = { version = "1.0", features = ["full"] }`

### pyproject.toml (Python)

Modern Python project configuration:

```toml
[project]
name = "my-project"
dependencies = [
    "flask>=2.0.0",
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "mypy>=1.0.0",
]
```

---

## Output Formats

### Text Format (Default)

Human-readable output with colors:

```bash
phantom-guard validate requests
```

Output:
```
SAFE: requests
  Registry: pypi
  Risk Score: 0.05
  Signals:
    [+] POPULAR_PACKAGE: High download count (10M+ monthly)
    [+] LONG_HISTORY: Package created 10+ years ago
```

### JSON Format

Machine-readable output for CI/CD integration:

```bash
phantom-guard check requirements.txt --output json
```

Output:
```json
{
  "results": [
    {
      "name": "requests",
      "registry": "pypi",
      "exists": true,
      "risk_score": 0.05,
      "recommendation": "safe",
      "signals": [
        {
          "type": "popular_package",
          "weight": -0.3,
          "message": "High download count (10M+ monthly)"
        }
      ]
    }
  ],
  "summary": {
    "total": 1,
    "safe": 1,
    "suspicious": 0,
    "high_risk": 0,
    "not_found": 0
  }
}
```

### Plain Text (No Colors)

For terminals that do not support ANSI colors:

```bash
phantom-guard validate requests --plain
```

Or set the `NO_COLOR` environment variable:

```bash
export NO_COLOR=1
phantom-guard validate requests
```

---

## Cache Management

### How Caching Works

Phantom Guard uses a two-tier cache system to improve performance:

**Tier 1: Memory Cache (LRU)**
- In-memory least-recently-used cache
- Instant access (<1ms)
- Default TTL: 1 hour
- Default max size: 1000 entries
- Cleared when process exits

**Tier 2: SQLite Cache (Persistent)**
- File-based persistent storage
- Fast access (<10ms)
- Default TTL: 24 hours
- No size limit
- Survives process restarts

**Cache Flow:**
1. Check memory cache (instant)
2. If miss, check SQLite cache
3. If SQLite hit, promote to memory
4. If miss, fetch from registry API
5. Store in both tiers

### Cache Configuration

Default cache settings:

| Setting | Value | Description |
|---------|-------|-------------|
| Memory TTL | 3600s (1 hour) | Time entries stay in memory |
| Memory Size | 1000 entries | Maximum memory cache entries |
| SQLite TTL | 86400s (24 hours) | Time entries stay on disk |
| SQLite Path | Platform-specific | See `phantom-guard cache path` |

### Cache Commands Summary

```bash
# View cache statistics
phantom-guard cache stats

# Clear all cached data
phantom-guard cache clear

# Clear only PyPI cache
phantom-guard cache clear --registry pypi

# Show cache file location
phantom-guard cache path
```

### When to Clear Cache

Clear the cache when:
- Package metadata may have changed (new version released)
- You see stale information
- Disk space is limited
- Troubleshooting validation issues

---

## Advanced Usage Patterns

### CI/CD Integration

#### GitHub Actions

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
        run: |
          phantom-guard check requirements.txt \
            --output json \
            --fail-on suspicious \
            > phantom-guard-report.json

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: phantom-guard-report.json
```

#### GitLab CI

```yaml
phantom-guard:
  stage: test
  image: python:3.11
  script:
    - pip install phantom-guard
    - phantom-guard check requirements.txt --fail-on suspicious
  only:
    - merge_requests
    - main
```

#### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: phantom-guard
        name: Phantom Guard Security Check
        entry: phantom-guard check requirements.txt --fail-on high_risk --quiet
        language: system
        files: requirements.*\.txt$
        pass_filenames: false
```

Or create a custom git hook at `.git/hooks/pre-commit`:

```bash
#!/bin/bash
set -e

echo "Running Phantom Guard security check..."
phantom-guard check requirements.txt --fail-on high_risk --quiet

if [ $? -ne 0 ]; then
    echo "Security check failed! Review the suspicious packages."
    exit 1
fi
```

### Batch Processing Large Files

For large dependency files (100+ packages):

```bash
# Increase parallelism for faster processing
phantom-guard check requirements.txt --parallel 20

# Use fail-fast to stop on first critical issue
phantom-guard check requirements.txt --fail-fast

# Combine for CI with large monorepos
phantom-guard check requirements.txt \
  --parallel 30 \
  --fail-fast \
  --output json \
  > results.json
```

### Using with Virtual Environments

Phantom Guard works with any Python environment:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install Phantom Guard
pip install phantom-guard

# Check your project dependencies
phantom-guard check requirements.txt

# Or generate requirements from pip freeze
pip freeze > requirements.txt
phantom-guard check requirements.txt
```

### Scanning Multiple Files

Check all dependency files in a project:

```bash
#!/bin/bash

exit_code=0

# Python
if [ -f "requirements.txt" ]; then
    phantom-guard check requirements.txt --fail-on suspicious || exit_code=1
fi

if [ -f "pyproject.toml" ]; then
    phantom-guard check pyproject.toml --fail-on suspicious || exit_code=1
fi

# Node.js
if [ -f "package.json" ]; then
    phantom-guard check package.json --fail-on suspicious || exit_code=1
fi

# Rust
if [ -f "Cargo.toml" ]; then
    phantom-guard check Cargo.toml --fail-on suspicious || exit_code=1
fi

exit $exit_code
```

### Ignoring Internal Packages

For monorepos with internal packages:

```bash
# Ignore specific packages
phantom-guard check requirements.txt \
  --ignore "my-company-utils,internal-lib,dev-tools"
```

---

## Troubleshooting

### Common Issues

#### Network Errors

**Problem:** `Registry error: Connection timeout`

**Solutions:**
1. Check internet connectivity
2. Verify firewall allows outbound HTTPS to:
   - `pypi.org` (PyPI)
   - `registry.npmjs.org` (npm)
   - `crates.io` (Rust)
3. If behind a proxy, set environment variables:
   ```bash
   export HTTP_PROXY=http://proxy:8080
   export HTTPS_PROXY=http://proxy:8080
   ```
4. Increase timeout by running with fewer parallel requests:
   ```bash
   phantom-guard check requirements.txt --parallel 5
   ```

#### Cache Issues

**Problem:** Stale or corrupted cache data

**Solutions:**
1. Clear the cache:
   ```bash
   phantom-guard cache clear --force
   ```
2. Delete cache file manually:
   ```bash
   rm -rf ~/.cache/phantom-guard/  # Linux
   rm -rf ~/Library/Caches/phantom-guard/  # macOS
   ```
3. Run without SQLite caching:
   ```bash
   # The CLI uses memory-only cache by default
   phantom-guard validate some-package
   ```

#### Invalid Package Name

**Problem:** `Invalid package name: contains invalid characters`

**Solutions:**
1. Check package name follows conventions:
   - Only ASCII alphanumeric, hyphens, underscores, dots
   - Cannot start/end with hyphen or underscore
   - Cannot have consecutive hyphens (`--`) or underscores (`__`)
   - Maximum 214 characters
2. For npm scoped packages, include the scope:
   ```bash
   phantom-guard validate @types/node --registry npm
   ```

#### File Parse Errors

**Problem:** `Failed to parse package.json: Invalid JSON`

**Solutions:**
1. Validate JSON syntax:
   ```bash
   python -m json.tool package.json
   ```
2. Check for trailing commas (not allowed in JSON)
3. Ensure UTF-8 encoding

**Problem:** `Could not detect file format`

**Solutions:**
1. Use standard filenames:
   - `requirements.txt` for Python
   - `package.json` for npm
   - `Cargo.toml` for Rust
2. Override registry detection:
   ```bash
   phantom-guard check deps.txt --registry pypi
   ```

#### Permission Errors

**Problem:** `Permission denied: cache.db`

**Solutions:**
1. Check cache directory permissions:
   ```bash
   ls -la ~/.cache/phantom-guard/
   ```
2. Fix permissions:
   ```bash
   chmod 755 ~/.cache/phantom-guard/
   chmod 644 ~/.cache/phantom-guard/cache.db
   ```
3. Use a different cache location (set `PHANTOM_GUARD_CACHE_DIR`)

### Getting Help

If you encounter issues not covered here:

1. Check the issue tracker: https://github.com/phantom-guard/phantom-guard/issues
2. Run with verbose output for debugging:
   ```bash
   phantom-guard validate package-name --verbose
   ```
3. Include in bug reports:
   - Phantom Guard version (`phantom-guard --version`)
   - Python version (`python --version`)
   - Operating system
   - Full error message
   - Minimal reproducible example

---

## Quick Reference

### Common Commands

```bash
# Single package validation
phantom-guard validate requests
phantom-guard validate express -r npm
phantom-guard validate serde -r crates

# Batch validation
phantom-guard check requirements.txt
phantom-guard check package.json -o json
phantom-guard check Cargo.toml --fail-on suspicious

# Cache management
phantom-guard cache stats
phantom-guard cache clear
phantom-guard cache path

# Get version
phantom-guard --version
```

### Exit Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | SAFE | All packages are safe |
| 1 | SUSPICIOUS | At least one suspicious package |
| 2 | HIGH_RISK | At least one high-risk package |
| 3 | NOT_FOUND | Package does not exist |
| 4 | INPUT_ERROR | Invalid input (package name, registry) |
| 5 | RUNTIME_ERROR | Network or system error |

### Supported Registries

| Registry | Flag | Example |
|----------|------|---------|
| PyPI | `--registry pypi` | `phantom-guard validate flask` |
| npm | `--registry npm` | `phantom-guard validate express -r npm` |
| crates.io | `--registry crates` | `phantom-guard validate serde -r crates` |
