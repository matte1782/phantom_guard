# Contributing to Phantom Guard

Thank you for your interest in contributing to Phantom Guard! We appreciate every contribution, whether it's reporting bugs, suggesting features, improving documentation, or submitting code changes.

Phantom Guard aims to protect developers from AI-hallucinated package attacks (slopsquatting), and your contributions help make the Python ecosystem safer for everyone.

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git

### Getting Started

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/phantom-guard.git
   cd phantom-guard
   ```

2. **Create a virtual environment**

   Using standard venv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

   Or using uv (recommended for faster installs):
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in development mode**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify your setup**

   ```bash
   pytest
   ```

---

## Code Standards

We maintain high code quality standards to ensure reliability and maintainability.

### Type Hints (Required)

All code must include type hints and pass strict mypy checking:

```bash
mypy --strict src/
```

### Test Coverage

We target **100% test coverage**. All new code must include tests:

```bash
pytest --cov=phantom_guard --cov-report=term-missing
```

### Linting and Formatting

We use ruff for both linting and formatting:

```bash
# Check for linting issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Docstrings

All public functions, classes, and modules must have docstrings following Google style:

```python
def validate_package(name: str, registry: str = "pypi") -> PackageRisk:
    """Validate a package name against the specified registry.

    Args:
        name: The package name to validate.
        registry: The package registry to check. Defaults to "pypi".

    Returns:
        A PackageRisk object containing the validation result.

    Raises:
        RegistryError: If the registry is unreachable.
    """
```

---

## Project Structure

```
phantom-guard/
├── src/phantom_guard/
│   ├── core/          # Detection engine and validation logic
│   ├── cli/           # Command-line interface
│   ├── registry/      # Package registry API clients
│   └── cache/         # Caching layer for API responses
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── e2e/           # End-to-end tests
└── docs/              # Documentation
```

---

## Testing Guidelines

### Test-Driven Development (TDD)

We follow TDD practices. When adding new features:

1. **Red**: Write a failing test first
2. **Green**: Write the minimum code to pass the test
3. **Refactor**: Clean up while keeping tests green

### Test Organization

- **Unit tests** (`tests/unit/`): Test individual functions and classes in isolation
- **Integration tests** (`tests/integration/`): Test component interactions
- **E2E tests** (`tests/e2e/`): Test complete workflows

### Property-Based Testing

We use hypothesis for property-based testing where appropriate:

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_package_name_handling(name: str) -> None:
    # Test that any input is handled gracefully
    result = sanitize_package_name(name)
    assert isinstance(result, str)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=phantom_guard

# Run specific test file
pytest tests/unit/test_validators.py

# Run tests matching a pattern
pytest -k "test_validate"
```

---

## Pull Request Process

1. **Fork the repository** and create your feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Write tests first** following TDD practices

3. **Implement your feature** to make tests pass

4. **Run all checks** before submitting:
   ```bash
   ruff check .
   ruff format .
   mypy --strict src/
   pytest --cov=phantom_guard
   ```

5. **Commit your changes** using conventional commits (see below)

6. **Push to your fork** and submit a Pull Request

7. **Describe your changes** clearly in the PR description:
   - What problem does this solve?
   - How did you test it?
   - Any breaking changes?

---

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/) for clear history:

| Prefix | Purpose |
|--------|---------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `test:` | Adding or updating tests |
| `refactor:` | Code refactoring (no feature change) |
| `perf:` | Performance improvements |
| `build:` | Build system or dependencies |
| `ci:` | CI/CD configuration |
| `chore:` | Maintenance tasks |

### Examples

```
feat(core): add typosquatting detection algorithm
fix(cli): handle empty package lists gracefully
docs: update installation instructions
test(registry): add integration tests for PyPI client
refactor(cache): simplify cache key generation
perf(core): optimize Levenshtein distance calculation
```

---

## Questions?

- **Bug reports**: Open a [GitHub issue](https://github.com/phantom-guard/phantom-guard/issues)
- **Feature requests**: Start a [GitHub discussion](https://github.com/phantom-guard/phantom-guard/discussions)
- **General questions**: Use GitHub discussions or check existing issues

---

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to make software development safer.

---

Thank you for contributing to Phantom Guard!
