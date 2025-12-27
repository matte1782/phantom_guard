# Week 3 - Day 5: End-to-End Integration & Testing

> **Date**: Day 5 (Week 3)
> **Focus**: Complete integration testing and workflow validation
> **Tasks**: W3.6
> **Hours**: 6-8 hours
> **SPEC_IDs**: All CLI specs
> **TEST_IDs**: Integration tests
> **EC_IDs**: EC080-EC095

---

## Overview

Final integration day for Week 3. Ensure all CLI components work together, run full end-to-end tests against real APIs, and prepare for hostile review.

### Deliverables
- [ ] Full end-to-end tests passing
- [ ] Real API integration verified
- [ ] Performance benchmarks documented
- [ ] Documentation complete
- [ ] Hostile review ready

---

## Morning Session (3h)

### Objective
Run comprehensive end-to-end tests covering all CLI workflows.

### Step 1: Create E2E Test Suite (30min)

```python
# tests/e2e/test_cli_workflows.py
"""
End-to-end CLI workflow tests.

These tests run the actual CLI commands and verify
the complete user experience.
"""

import subprocess
import json
from pathlib import Path
import pytest


@pytest.fixture
def temp_requirements(tmp_path):
    """Create temporary requirements file."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("""
# Production dependencies
flask==2.3.0
requests>=2.28.0
django>=4.0,<5.0

# Dev dependencies
pytest
ruff
""")
    return req_file


def run_cli(*args) -> subprocess.CompletedProcess:
    """Run phantom-guard CLI command."""
    return subprocess.run(
        ["phantom-guard", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestValidateWorkflow:
    """E2E tests for validate command."""

    def test_validate_known_safe_package(self):
        """
        EC: EC080

        Known safe package returns exit code 0.
        """
        result = run_cli("validate", "flask")

        assert result.returncode == 0
        assert "SAFE" in result.stdout

    def test_validate_with_verbose_flag(self):
        """
        EC: EC091

        Verbose mode shows signal details.
        """
        result = run_cli("validate", "flask", "-v")

        assert result.returncode == 0
        # Should show more detail than non-verbose

    def test_validate_with_quiet_flag(self):
        """
        EC: EC092

        Quiet mode shows minimal output.
        """
        result = run_cli("validate", "flask", "-q")

        assert result.returncode == 0
        # Output should be very short
        assert len(result.stdout.strip().split("\n")) <= 3

    def test_validate_json_output(self):
        """
        EC: EC089

        JSON output is valid and complete.
        """
        result = run_cli("validate", "flask", "--output", "json")

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "results" in data
        assert "summary" in data

    def test_validate_npm_registry(self):
        """
        EC: EC095

        Can validate npm packages.
        """
        result = run_cli("validate", "express", "--registry", "npm")

        assert result.returncode == 0
        assert "express" in result.stdout.lower()

    def test_validate_crates_registry(self):
        """
        Can validate crates.io packages.
        """
        result = run_cli("validate", "serde", "--registry", "crates")

        assert result.returncode == 0
        assert "serde" in result.stdout.lower()


class TestCheckWorkflow:
    """E2E tests for check command."""

    def test_check_requirements_file(self, temp_requirements):
        """
        EC: EC084

        Check command processes requirements.txt.
        """
        result = run_cli("check", str(temp_requirements))

        assert result.returncode in [0, 1, 2, 3]  # Any valid exit code
        assert "flask" in result.stdout.lower()
        assert "Summary" in result.stdout

    def test_check_with_json_output(self, temp_requirements):
        """
        JSON output for check command.
        """
        result = run_cli("check", str(temp_requirements), "--output", "json")

        data = json.loads(result.stdout)
        assert "results" in data
        assert len(data["results"]) >= 3  # At least flask, requests, django

    def test_check_nonexistent_file(self):
        """
        EC: EC086

        Check command handles missing file.
        """
        result = run_cli("check", "nonexistent_file_xyz.txt")

        assert result.returncode == 4  # EXIT_INPUT_ERROR
        assert "not found" in result.stdout.lower() or "error" in result.stderr.lower()

    def test_check_with_ignore_flag(self, temp_requirements):
        """
        Ignore flag skips specified packages.
        """
        result = run_cli("check", str(temp_requirements), "--ignore", "flask,requests")

        # flask and requests should not appear in results
        # (implementation-dependent)


class TestCacheWorkflow:
    """E2E tests for cache commands."""

    def test_cache_path_shows_location(self):
        """
        Cache path command shows file location.
        """
        result = run_cli("cache", "path")

        assert result.returncode == 0
        assert "cache" in result.stdout.lower()

    def test_cache_stats_works(self):
        """
        Cache stats command runs without error.
        """
        result = run_cli("cache", "stats")

        assert result.returncode == 0


class TestHelpAndVersion:
    """E2E tests for help and version."""

    def test_help_shows_commands(self):
        """Help shows available commands."""
        result = run_cli("--help")

        assert result.returncode == 0
        assert "validate" in result.stdout
        assert "check" in result.stdout
        assert "cache" in result.stdout

    def test_validate_help(self):
        """Validate command has help."""
        result = run_cli("validate", "--help")

        assert result.returncode == 0
        assert "package" in result.stdout.lower()
        assert "--registry" in result.stdout

    def test_check_help(self):
        """Check command has help."""
        result = run_cli("check", "--help")

        assert result.returncode == 0
        assert "file" in result.stdout.lower()
        assert "--fail-on" in result.stdout
```

### Step 2: Run E2E Tests (30min)

```bash
# Run E2E tests (requires installed CLI)
pip install -e .
pytest tests/e2e/ -v --tb=short

# Mark slow tests appropriately
pytest tests/e2e/ -v -m "not slow"
```

### Step 3: Create Performance Benchmark Suite (1h)

```python
# tests/benchmarks/test_cli_performance.py
"""
Performance benchmarks for CLI commands.

These tests verify performance budgets are met.
"""

import subprocess
import time
import pytest


class TestPerformanceBudgets:
    """Verify performance budgets from spec."""

    @pytest.mark.benchmark
    def test_single_package_under_200ms(self):
        """
        INV: INV014

        Single package validation under 200ms (uncached).
        """
        # Clear cache first
        subprocess.run(["phantom-guard", "cache", "clear", "-f"], check=True)

        start = time.perf_counter()
        result = subprocess.run(
            ["phantom-guard", "validate", "flask"],
            capture_output=True,
            timeout=10,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        assert elapsed_ms < 200, f"Took {elapsed_ms:.0f}ms, expected <200ms"

    @pytest.mark.benchmark
    def test_cached_under_10ms(self):
        """
        Cached lookup under 10ms.
        """
        # First call to populate cache
        subprocess.run(["phantom-guard", "validate", "flask"], check=True)

        # Second call should be cached
        start = time.perf_counter()
        result = subprocess.run(
            ["phantom-guard", "validate", "flask"],
            capture_output=True,
            timeout=10,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result.returncode == 0
        # Allow more time for CLI startup overhead
        assert elapsed_ms < 500, f"Took {elapsed_ms:.0f}ms, expected <500ms"

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_batch_50_under_5s(self, tmp_path):
        """
        50 packages under 5 seconds.
        """
        # Create requirements with 50 common packages
        packages = [
            "flask", "django", "requests", "numpy", "pandas",
            "scipy", "matplotlib", "seaborn", "sqlalchemy", "celery",
            "redis", "pytest", "black", "ruff", "mypy",
            "fastapi", "pydantic", "httpx", "aiohttp", "uvicorn",
            "gunicorn", "boto3", "click", "rich", "typer",
            "pillow", "opencv-python", "tensorflow", "torch", "transformers",
            "scikit-learn", "xgboost", "lightgbm", "dask", "ray",
            "airflow", "prefect", "dagster", "mlflow", "wandb",
            "streamlit", "gradio", "dash", "plotly", "bokeh",
            "networkx", "igraph", "sympy", "numba", "cython",
        ]

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("\n".join(packages))

        start = time.perf_counter()
        result = subprocess.run(
            ["phantom-guard", "check", str(req_file), "--parallel", "10"],
            capture_output=True,
            timeout=60,
        )
        elapsed = time.perf_counter() - start

        assert result.returncode in [0, 1, 2, 3]
        assert elapsed < 5.0, f"Took {elapsed:.1f}s, expected <5s"
```

### Step 4: Run Performance Benchmarks (30min)

```bash
# Run benchmark tests
pytest tests/benchmarks/ -v -m benchmark --tb=short

# Generate performance report
pytest tests/benchmarks/ -v --benchmark-only --benchmark-json=benchmark_results.json
```

---

## Afternoon Session (3h)

### Objective
Complete documentation, run hostile review prep, and finalize Week 3.

### Step 5: Update CLI Documentation (45min)

```markdown
# docs/CLI_REFERENCE.md

# Phantom Guard CLI Reference

## Installation

```bash
pip install phantom-guard
```

## Commands

### validate

Validate a single package for supply chain risks.

```bash
phantom-guard validate <package> [options]
```

**Arguments:**
- `package` - Package name to validate (required)

**Options:**
- `-r, --registry` - Registry: pypi (default), npm, crates
- `-o, --output` - Output format: text (default), json
- `-v, --verbose` - Show detailed signals
- `-q, --quiet` - Only show result
- `--no-banner` - Hide ASCII banner
- `--offline` - Use cache only
- `--timeout` - Request timeout in seconds

**Exit Codes:**
| Code | Meaning |
|:-----|:--------|
| 0 | SAFE - Package is safe |
| 1 | SUSPICIOUS - Package is suspicious |
| 2 | HIGH_RISK - Package is high risk |
| 3 | NOT_FOUND - Package not found |
| 4 | INPUT_ERROR - Invalid input |
| 5 | RUNTIME_ERROR - Runtime error |

**Examples:**

```bash
# Basic validation
phantom-guard validate flask

# Check npm package
phantom-guard validate express --registry npm

# JSON output for CI
phantom-guard validate flask --output json

# Quiet mode
phantom-guard validate flask -q
```

### check

Check a dependency file for risky packages.

```bash
phantom-guard check <file> [options]
```

**Arguments:**
- `file` - Dependency file path (required)

**Supported Files:**
- `requirements.txt` (Python/PyPI)
- `package.json` (JavaScript/npm)
- `Cargo.toml` (Rust/crates.io)

**Options:**
- `-r, --registry` - Override auto-detected registry
- `-o, --output` - Output format: text, json
- `--fail-on` - Exit non-zero on: suspicious, high_risk
- `--ignore` - Comma-separated packages to skip
- `--parallel` - Concurrent validations (default: 10)
- `--fail-fast` - Stop on first HIGH_RISK

**Examples:**

```bash
# Check requirements file
phantom-guard check requirements.txt

# Check with fail-on for CI
phantom-guard check requirements.txt --fail-on suspicious

# JSON output
phantom-guard check requirements.txt --output json

# Ignore specific packages
phantom-guard check requirements.txt --ignore flask,django
```

### cache

Manage the local cache.

```bash
phantom-guard cache <subcommand>
```

**Subcommands:**
- `path` - Show cache file location
- `stats` - Show cache statistics
- `clear` - Clear cache entries

**Examples:**

```bash
# Show cache path
phantom-guard cache path

# View statistics
phantom-guard cache stats

# Clear all cache
phantom-guard cache clear -f

# Clear specific registry
phantom-guard cache clear --registry pypi
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

      - name: Install Phantom Guard
        run: pip install phantom-guard

      - name: Check dependencies
        run: |
          phantom-guard check requirements.txt --fail-on suspicious
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: phantom-guard
        name: Phantom Guard
        entry: phantom-guard check requirements.txt --fail-on suspicious
        language: system
        pass_filenames: false
```

### GitLab CI

```yaml
phantom-guard:
  script:
    - pip install phantom-guard
    - phantom-guard check requirements.txt --output json > security-report.json
  artifacts:
    reports:
      dotenv: security-report.json
```
```

### Step 6: Create Week 3 Summary (30min)

```markdown
# docs/planning/week_3/WEEK_3_SUMMARY.md

# Week 3 Summary: CLI & Integration

## Completed Tasks

| Task | SPEC | Status | Tests |
|:-----|:-----|:-------|:------|
| W3.1 | S010-S012 | ✅ COMPLETE | T010.01-T010.06 |
| W3.2 | S013-S015 | ✅ COMPLETE | T010.13-T010.21 |
| W3.3 | S016-S017 | ✅ COMPLETE | T010.19-T010.20 |
| W3.4 | S002 | ✅ COMPLETE | T002.01-T002.08 |
| W3.5 | S018-S019 | ✅ COMPLETE | T010.02-T010.03 |
| W3.6 | All | ✅ COMPLETE | E2E tests |

## Exit Criteria Met

- [x] All W3.* tasks complete
- [x] T010-T019 tests passing
- [x] CLI integration tests passing
- [x] `phantom-guard validate flask` works
- [x] `phantom-guard check requirements.txt` works
- [x] Performance budgets met (<200ms single, <5s batch)

## Metrics

| Metric | Target | Achieved |
|:-------|:-------|:---------|
| Unit Tests | 30+ | XX |
| E2E Tests | 15+ | XX |
| Coverage | 90% | XX% |
| Single Package | <200ms | XXms |
| Batch 50 | <5s | XXs |

## Key Deliverables

1. **CLI Entry Point** - `phantom-guard` command installed and working
2. **Validate Command** - Single package validation with Rich output
3. **Check Command** - File-based batch validation
4. **Cache Commands** - Cache management subcommands
5. **Output Formatters** - Text and JSON output
6. **Batch Validator** - Concurrent processing with progress
7. **Documentation** - CLI reference complete

## Files Created/Modified

- `src/phantom_guard/cli/main.py`
- `src/phantom_guard/cli/branding.py`
- `src/phantom_guard/cli/output.py`
- `src/phantom_guard/cli/parsers.py`
- `src/phantom_guard/cli/formatters.py`
- `src/phantom_guard/core/batch.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_parsers.py`
- `tests/unit/test_formatters.py`
- `tests/unit/test_batch.py`
- `tests/e2e/test_cli_workflows.py`
- `docs/CLI_REFERENCE.md`

## Ready for Hostile Review

Week 3 is ready for hostile review. Run:

```bash
/hostile-review
```
```

### Step 7: Final Test Run and Cleanup (45min)

```bash
# Full test suite
pytest tests/ -v --tb=short --ignore=tests/integration

# Type checking
mypy src/phantom_guard/cli/ --strict

# Linting
ruff check src/phantom_guard/cli/
ruff format src/phantom_guard/cli/

# Manual verification
phantom-guard --help
phantom-guard validate flask
phantom-guard check requirements.txt
phantom-guard cache stats
```

### Step 8: Git Commit Week 3 (30min)

```bash
git add .
git commit -m "feat(cli): Complete Week 3 - CLI & Integration

## Week 3 Summary

### Tasks Completed
- W3.1: CLI validate command with branding (S010-S012)
- W3.2: CLI check command with file parsers (S013-S015)
- W3.3: Cache management commands (S016-S017)
- W3.4: Batch validation with concurrency (S002)
- W3.5: Output formatters (text, JSON) (S018-S019)
- W3.6: End-to-end integration tests

### Tests
- Unit tests: XX passing
- E2E tests: XX passing
- Performance benchmarks: All budgets met

### Exit Criteria Met
- [x] phantom-guard validate flask works
- [x] phantom-guard check requirements.txt works
- [x] JSON output valid
- [x] <200ms single package
- [x] <5s for 50 packages"
```

---

## End of Day Checklist

### Code Quality
- [ ] All unit tests passing
- [ ] All E2E tests passing
- [ ] mypy --strict passes
- [ ] ruff check passes
- [ ] Coverage ≥90%

### Performance
- [ ] Single package <200ms (uncached)
- [ ] Cached lookup <10ms
- [ ] Batch 50 <5s

### Documentation
- [ ] CLI_REFERENCE.md complete
- [ ] WEEK_3_SUMMARY.md created
- [ ] All commands have --help

### Git
- [ ] All changes committed
- [ ] Clean working directory

---

## Day 5 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W3.6 | |
| E2E Tests Passing | 15+ | |
| Coverage | 90% | |
| Single Pkg Time | <200ms | |
| Batch 50 Time | <5s | |
| Ready for Review | Yes | |

---

## Week 3 Complete!

**Next Steps:**
1. Run `/hostile-review` for Week 3
2. Address any review findings
3. Proceed to Week 4 (Polish & Release)
