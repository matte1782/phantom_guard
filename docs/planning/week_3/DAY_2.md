# Week 3 - Day 2: CLI Check Command (File Parsing)

> **Date**: Day 2 (Week 3)
> **Focus**: CLI `check` command for dependency files
> **Tasks**: W3.2
> **Hours**: 6-8 hours
> **SPEC_IDs**: S013-S015
> **TEST_IDs**: T010.13-T010.18
> **EC_IDs**: EC084-EC088

---

## Overview

Implement the `check` command that parses dependency files (requirements.txt, package.json, Cargo.toml) and validates all packages. This is the primary CI/CD integration point.

### Deliverables
- [ ] `check` command implementation
- [ ] requirements.txt parser
- [ ] package.json parser
- [ ] Cargo.toml parser
- [ ] Auto-detect file format
- [ ] Progress bar for multiple packages

---

## Morning Session (3h)

### Objective
Implement dependency file parsers and the `check` command structure.

### Step 1: Create Parser Module (15min)

```bash
# Create parser module
touch src/phantom_guard/cli/parsers.py
```

### Step 2: Implement Requirements.txt Parser (45min)

```python
# src/phantom_guard/cli/parsers.py
"""
IMPLEMENTS: S013-S015
Dependency file parsers.
"""

from __future__ import annotations

import re
import tomllib
import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ParsedPackage:
    """Parsed package from dependency file."""
    name: str
    version_spec: str | None = None
    registry: str = "pypi"


class ParserError(Exception):
    """Parsing failed."""
    pass


def parse_requirements_txt(content: str) -> list[ParsedPackage]:
    """
    IMPLEMENTS: S013
    TEST: T010.13, T010.14
    EC: EC084, EC087, EC088

    Parse requirements.txt format.

    Handles:
        - Simple: flask
        - Versioned: flask==2.0.0
        - Ranges: flask>=2.0,<3.0
        - Comments: # comment
        - Extras: flask[async]
        - URLs: -e git+https://...
    """
    packages = []
    # Regex for package name (handles extras like [async])
    package_pattern = re.compile(
        r'^([a-zA-Z0-9][\w.-]*)'  # Package name
        r'(?:\[[\w,]+\])?'        # Optional extras
        r'(.*)$'                   # Version spec
    )

    for line in content.splitlines():
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Skip URLs and editable installs
        if line.startswith('-e') or line.startswith('http') or line.startswith('git+'):
            continue

        # Skip options
        if line.startswith('-'):
            continue

        match = package_pattern.match(line)
        if match:
            name = match.group(1).lower()
            version_spec = match.group(2).strip() or None
            packages.append(ParsedPackage(name=name, version_spec=version_spec))

    return packages


def parse_package_json(content: str) -> list[ParsedPackage]:
    """
    IMPLEMENTS: S014
    TEST: T010.15
    EC: EC084

    Parse package.json dependencies.
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ParserError(f"Invalid JSON: {e}")

    packages = []

    # Combine dependencies and devDependencies
    for dep_key in ("dependencies", "devDependencies"):
        deps = data.get(dep_key, {})
        for name, version in deps.items():
            packages.append(ParsedPackage(
                name=name,
                version_spec=version,
                registry="npm",
            ))

    return packages


def parse_cargo_toml(content: str) -> list[ParsedPackage]:
    """
    IMPLEMENTS: S015
    TEST: T010.16
    EC: EC084

    Parse Cargo.toml dependencies.
    """
    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError as e:
        raise ParserError(f"Invalid TOML: {e}")

    packages = []

    # Parse [dependencies] and [dev-dependencies]
    for dep_key in ("dependencies", "dev-dependencies"):
        deps = data.get(dep_key, {})
        for name, spec in deps.items():
            # Handle both simple and complex specs
            if isinstance(spec, str):
                version_spec = spec
            elif isinstance(spec, dict):
                version_spec = spec.get("version", None)
            else:
                version_spec = None

            packages.append(ParsedPackage(
                name=name,
                version_spec=version_spec,
                registry="crates",
            ))

    return packages


def detect_and_parse(file_path: Path) -> list[ParsedPackage]:
    """
    IMPLEMENTS: S013-S015
    TEST: T010.17

    Auto-detect file format and parse.
    """
    content = file_path.read_text()
    name = file_path.name.lower()

    if name == "requirements.txt" or name.endswith(".txt"):
        return parse_requirements_txt(content)
    elif name == "package.json":
        return parse_package_json(content)
    elif name == "cargo.toml":
        return parse_cargo_toml(content)
    else:
        # Try to auto-detect by content
        if content.strip().startswith("{"):
            return parse_package_json(content)
        elif "[package]" in content or "[dependencies]" in content:
            return parse_cargo_toml(content)
        else:
            return parse_requirements_txt(content)
```

### Step 3: Enable Parser Tests (15min)

```python
# tests/unit/test_parsers.py
# Remove @pytest.mark.skip from:
# - test_parse_requirements_simple (T010.13)
# - test_parse_requirements_versioned (T010.14)
# - test_parse_package_json (T010.15)
# - test_parse_cargo_toml (T010.16)
# - test_auto_detect_format (T010.17)
```

**Run tests - must FAIL:**
```bash
pytest tests/unit/test_parsers.py -v
# Expected: ImportError
```

### Step 4: Run Parser Tests (15min)

```bash
pytest tests/unit/test_parsers.py -v --tb=short
# Expected: T010.13-T010.17 pass
```

### Step 5: Implement Check Command (1h)

```python
# src/phantom_guard/cli/main.py (add to existing)

from phantom_guard.cli.parsers import detect_and_parse, ParsedPackage, ParserError


@app.command()
def check(
    file: Annotated[Path, typer.Argument(help="Dependency file to check")],
    registry: Annotated[str | None, typer.Option("-r", "--registry", help="Override registry detection")] = None,
    fail_on: Annotated[str | None, typer.Option("--fail-on", help="Exit non-zero on: suspicious, high_risk")] = None,
    ignore: Annotated[str | None, typer.Option("--ignore", help="Comma-separated packages to skip")] = None,
    parallel: Annotated[int, typer.Option("--parallel", help="Concurrent validations")] = 10,
    output_format: Annotated[str, typer.Option("-o", "--output", help="Output format: text, json")] = "text",
    quiet: Annotated[bool, typer.Option("-q", "--quiet", help="Minimal output")] = False,
    no_banner: Annotated[bool, typer.Option("--no-banner", help="Hide banner")] = False,
) -> None:
    """
    IMPLEMENTS: S013-S015
    TEST: T010.18
    EC: EC084-EC090

    Check a dependency file for risky packages.

    Supports:
    - requirements.txt (Python/PyPI)
    - package.json (JavaScript/npm)
    - Cargo.toml (Rust/crates.io)
    """
    if not quiet and not no_banner:
        print_banner(console)

    # Validate file exists
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)

    # Parse file
    try:
        packages = detect_and_parse(file)
    except ParserError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)

    if not packages:
        console.print("[dim]No packages found in file[/dim]")
        raise typer.Exit(code=EXIT_SAFE)

    # Filter ignored packages
    ignored = set(ignore.split(",")) if ignore else set()
    packages = [p for p in packages if p.name not in ignored]

    # Override registry if specified
    if registry:
        for p in packages:
            p.registry = registry

    # Run validation
    exit_code = asyncio.run(_check_packages(
        packages, parallel, fail_on, output_format, quiet
    ))
    raise typer.Exit(code=exit_code)


async def _check_packages(
    packages: list[ParsedPackage],
    parallel: int,
    fail_on: str | None,
    output_format: str,
    quiet: bool,
) -> int:
    """Validate all packages from file."""
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

    detector = Detector()
    formatter = OutputFormatter(console, quiet=quiet)
    results = []

    console.print(f"\n[cyan]Scanning {len(packages)} packages...[/cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating", total=len(packages))

        # Validate packages (with semaphore for parallelism)
        import asyncio
        semaphore = asyncio.Semaphore(parallel)

        async def validate_one(pkg: ParsedPackage):
            async with semaphore:
                result = await detector.validate(pkg.name, registry=pkg.registry)
                progress.advance(task)
                return result

        results = await asyncio.gather(*[validate_one(p) for p in packages])

    # Print results
    console.print()
    for result in results:
        formatter.print_result(result)

    # Summary
    _print_summary(results, console)

    # Determine exit code
    return _determine_exit_code(results, fail_on)


def _print_summary(results: list, console: Console) -> None:
    """Print summary line."""
    safe = sum(1 for r in results if r.recommendation == Recommendation.SAFE)
    suspicious = sum(1 for r in results if r.recommendation == Recommendation.SUSPICIOUS)
    high_risk = sum(1 for r in results if r.recommendation == Recommendation.HIGH_RISK)
    not_found = sum(1 for r in results if r.recommendation == Recommendation.NOT_FOUND)

    console.print("\n" + "─" * 60)
    summary = f"Summary: {len(results)} packages | "
    summary += f"[green]{safe} safe[/green] | "
    summary += f"[yellow]{suspicious} suspicious[/yellow] | "
    summary += f"[red]{high_risk} high-risk[/red]"
    if not_found:
        summary += f" | [dim]{not_found} not found[/dim]"
    console.print(summary)
    console.print("─" * 60 + "\n")


def _determine_exit_code(results: list, fail_on: str | None) -> int:
    """Determine exit code based on results and fail_on setting."""
    has_high_risk = any(r.recommendation == Recommendation.HIGH_RISK for r in results)
    has_suspicious = any(r.recommendation == Recommendation.SUSPICIOUS for r in results)
    has_not_found = any(r.recommendation == Recommendation.NOT_FOUND for r in results)

    if has_high_risk:
        return EXIT_HIGH_RISK

    if fail_on == "suspicious" and has_suspicious:
        return EXIT_SUSPICIOUS

    if has_suspicious:
        return EXIT_SUSPICIOUS

    if has_not_found:
        return EXIT_NOT_FOUND

    return EXIT_SAFE
```

---

## Afternoon Session (3h)

### Objective
Add comprehensive tests and handle edge cases.

### Step 6: Add Check Command Tests (1h)

```python
# tests/unit/test_cli.py

def test_check_requirements_file(tmp_path):
    """
    TEST_ID: T010.18
    SPEC: S013
    EC: EC084
    """
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("flask\nrequests\n")

    result = runner.invoke(app, ["check", str(req_file)])
    assert result.exit_code == 0
    assert "flask" in result.output


def test_check_file_not_found():
    """
    TEST_ID: T010.19
    EC: EC086
    """
    result = runner.invoke(app, ["check", "nonexistent.txt"])
    assert result.exit_code == EXIT_INPUT_ERROR
    assert "not found" in result.output.lower()


def test_check_empty_file(tmp_path):
    """
    TEST_ID: T010.20
    EC: EC087
    """
    empty_file = tmp_path / "requirements.txt"
    empty_file.write_text("")

    result = runner.invoke(app, ["check", str(empty_file)])
    assert result.exit_code == 0
    assert "no packages" in result.output.lower()


def test_check_with_fail_on_suspicious(tmp_path):
    """
    TEST_ID: T010.21
    EC: EC090
    """
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("flask\nflask-gpt-helper\n")

    result = runner.invoke(app, ["check", str(req_file), "--fail-on", "suspicious"])
    # Should exit non-zero due to suspicious package
    assert result.exit_code >= 1
```

### Step 7: Add Parser Edge Case Tests (1h)

```python
# tests/unit/test_parsers.py

def test_requirements_with_comments():
    """Handle comments in requirements.txt."""
    content = """
# This is a comment
flask  # inline comment
requests
# Another comment
django
"""
    packages = parse_requirements_txt(content)
    assert len(packages) == 3
    assert packages[0].name == "flask"


def test_requirements_with_extras():
    """Handle extras like flask[async]."""
    content = "flask[async]==2.0.0"
    packages = parse_requirements_txt(content)
    assert len(packages) == 1
    assert packages[0].name == "flask"
    assert packages[0].version_spec == "==2.0.0"


def test_package_json_with_scoped_packages():
    """Handle scoped npm packages."""
    content = '''
{
    "dependencies": {
        "@types/node": "^18.0.0",
        "express": "4.18.0"
    }
}
'''
    packages = parse_package_json(content)
    assert len(packages) == 2
    assert any(p.name == "@types/node" for p in packages)


def test_cargo_toml_complex_deps():
    """Handle complex Cargo.toml dependency specs."""
    content = '''
[package]
name = "myapp"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = "1.0"
'''
    packages = parse_cargo_toml(content)
    assert len(packages) == 2
    assert any(p.name == "serde" for p in packages)
```

### Step 8: Run All Tests and Manual Testing (1h)

```bash
# Run all CLI tests
pytest tests/unit/test_cli.py tests/unit/test_parsers.py -v --tb=short

# Manual testing
echo "flask
requests
django" > /tmp/test-requirements.txt

phantom-guard check /tmp/test-requirements.txt
phantom-guard check /tmp/test-requirements.txt --fail-on suspicious
phantom-guard check /tmp/test-requirements.txt -o json
```

---

## End of Day Checklist

### Code Quality
- [ ] `ruff check src/phantom_guard/cli/` - No lint errors
- [ ] `ruff format src/phantom_guard/cli/` - Code formatted
- [ ] `mypy src/phantom_guard/cli/ --strict` - No type errors
- [ ] All T010.13-T010.21 tests passing

### Documentation
- [ ] All parsers have IMPLEMENTS tags
- [ ] CLI help text is comprehensive
- [ ] Edge cases documented in code comments

### Git Commit

```bash
git add src/phantom_guard/cli/ tests/unit/
git commit -m "feat(cli): Implement check command with file parsers

IMPLEMENTS: S013-S015
TESTS: T010.13-T010.21
EC: EC084-EC090

- Add requirements.txt parser with extras/comments
- Add package.json parser with scoped packages
- Add Cargo.toml parser with complex deps
- Add auto-detection of file format
- Implement check command with progress bar
- Support --fail-on and --ignore flags"
```

---

## Day 2 Success Metrics

| Metric | Target | Actual |
|:-------|:-------|:-------|
| Tasks Complete | W3.2 | |
| Tests Passing | 9 (T010.13-T010.21) | |
| Type Coverage | 100% | |
| Lint Errors | 0 | |
| CLI Works | `phantom-guard check requirements.txt` | |

---

## Tomorrow Preview

**Day 3 Focus**: Cache management + Output formats (W3.3, W3.5)
- `cache clear` command
- `cache stats` command
- JSON output format
- SARIF output (optional)
