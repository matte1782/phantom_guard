---
name: phantom:test
description: Testing workflow for quality assurance. Use after implementation to run tests, check coverage, and validate critical paths.
---

# Skill: Testing Workflow

> **Purpose**: Structured testing for quality assurance
> **Philosophy**: Tests are documentation that runs

---

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests (fast, isolated)
│   ├── test_scorer.py
│   ├── test_patterns.py
│   └── test_registry/
│       ├── test_pypi.py
│       ├── test_npm.py
│       └── test_crates.py
├── integration/          # Integration tests (slower, real APIs)
│   ├── test_detection.py
│   └── test_cli.py
└── e2e/                  # End-to-end tests (full workflows)
    └── test_requirements_check.py
```

---

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=phantom_guard --cov-report=html

# Unit tests only (fast)
pytest tests/unit -v

# Integration tests (needs network)
pytest tests/integration -v

# Specific test
pytest tests/unit/test_scorer.py::test_score_new_package -v

# Run tests matching pattern
pytest -k "pattern" -v
```

---

## Test Categories

### Unit Tests

Fast, isolated, mock external dependencies:

```python
# tests/unit/test_scorer.py
import pytest
from phantom_guard.core.scorer import RiskScorer
from phantom_guard.core.types import PackageMetadata

@pytest.fixture
def scorer():
    return RiskScorer()

class TestRiskScorer:
    def test_score_established_package(self, scorer):
        """Established packages score as safe."""
        metadata = PackageMetadata(
            name="requests",
            exists=True,
            release_count=150,
            downloads_last_month=1_000_000,
            has_repository=True,
            maintainer_count=5,
        )
        result = scorer.score(metadata)
        assert result.risk_level == RiskLevel.SAFE
        assert result.risk_score < 0.3

    def test_score_nonexistent_package(self, scorer):
        """Non-existent packages are blocked."""
        metadata = PackageMetadata(
            name="flask-gpt-helper",
            exists=False,
        )
        result = scorer.score(metadata)
        assert result.risk_level == RiskLevel.CRITICAL
        assert result.risk_score > 0.9

    def test_score_new_suspicious_package(self, scorer):
        """New packages with suspicious signals score high."""
        metadata = PackageMetadata(
            name="gpt4-api",
            exists=True,
            release_count=2,
            downloads_last_month=50,
            has_repository=False,
            maintainer_count=1,
        )
        result = scorer.score(metadata)
        assert result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
```

### Integration Tests

Test real API interactions:

```python
# tests/integration/test_pypi_client.py
import pytest
from phantom_guard.registry.pypi import PyPIClient

@pytest.mark.integration
class TestPyPIClient:
    @pytest.fixture
    def client(self):
        return PyPIClient()

    async def test_fetch_existing_package(self, client):
        """Can fetch metadata for existing package."""
        metadata = await client.fetch("requests")
        assert metadata.exists
        assert metadata.release_count > 100
        assert metadata.has_repository

    async def test_fetch_nonexistent_package(self, client):
        """Returns not-found for fake package."""
        metadata = await client.fetch("asdfjkl-nonexistent-xyz")
        assert not metadata.exists

    async def test_fetch_handles_timeout(self, client, mocker):
        """Gracefully handles timeout."""
        mocker.patch.object(
            client._http,
            'get',
            side_effect=httpx.TimeoutException("timeout")
        )
        with pytest.raises(RegistryTimeoutError):
            await client.fetch("requests")
```

### End-to-End Tests

Test full user workflows:

```python
# tests/e2e/test_requirements_check.py
import pytest
from click.testing import CliRunner
from phantom_guard.cli.main import app

@pytest.mark.e2e
class TestRequirementsCheck:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_check_clean_requirements(self, runner, tmp_path):
        """Clean requirements pass."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\nrequests==2.28.0\n")

        result = runner.invoke(app, ["check", str(req_file)])

        assert result.exit_code == 0
        assert "All packages safe" in result.output

    def test_check_suspicious_requirements(self, runner, tmp_path):
        """Suspicious packages are flagged."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("flask==2.0.0\nflask-gpt-helper==0.1.0\n")

        result = runner.invoke(app, ["check", str(req_file)])

        assert result.exit_code == 1
        assert "SUSPICIOUS" in result.output
        assert "flask-gpt-helper" in result.output
```

---

## Test Fixtures

### Common Fixtures

```python
# tests/conftest.py
import pytest
from phantom_guard.core.types import PackageMetadata

@pytest.fixture
def safe_package_metadata():
    """Metadata for a known-safe package."""
    return PackageMetadata(
        name="flask",
        exists=True,
        release_count=63,
        downloads_last_month=180_000_000,
        has_repository=True,
        repository_url="https://github.com/pallets/flask",
        maintainer_count=5,
        created_at=datetime(2010, 4, 6),
    )

@pytest.fixture
def suspicious_package_metadata():
    """Metadata for a suspicious package."""
    return PackageMetadata(
        name="gpt4-api",
        exists=True,
        release_count=3,
        downloads_last_month=42,
        has_repository=False,
        maintainer_count=1,
        created_at=datetime(2024, 1, 15),
    )

@pytest.fixture
def nonexistent_package_metadata():
    """Metadata for a non-existent package."""
    return PackageMetadata(
        name="flask-gpt-helper",
        exists=False,
    )

@pytest.fixture
def mock_pypi_response():
    """Mock PyPI API response."""
    return {
        "info": {
            "name": "flask",
            "author": "Pallets",
            "summary": "A simple framework...",
            "project_urls": {"Source": "https://github.com/pallets/flask"},
        },
        "releases": {"2.0.0": [...], "2.1.0": [...]},
    }
```

---

## Test Data

### Hallucination Pattern Test Cases

```python
# tests/data/hallucination_patterns.py
HALLUCINATION_TEST_CASES = [
    # (package_name, should_match_pattern)
    ("flask-gpt-helper", True),
    ("django-ai-utils", True),
    ("requests-openai-client", True),
    ("numpy-chatgpt", True),
    ("flask", False),
    ("django-rest-framework", False),
    ("requests-oauthlib", False),
]

LEGITIMATE_PACKAGES = [
    "flask", "django", "requests", "numpy", "pandas",
    "fastapi", "pydantic", "httpx", "pytest", "typer",
]

SUSPICIOUS_PACKAGES = [
    "gpt4-api", "chatgpt-python", "openai-helper",
    "django-chatgpt", "flask-gpt", "requests-ai",
]
```

---

## Mocking Strategy

### Mock External APIs

```python
# Mock PyPI responses
@pytest.fixture
def mock_pypi(mocker):
    async def mock_get(url):
        if "requests" in url:
            return MockResponse(200, REQUESTS_METADATA)
        elif "nonexistent" in url:
            return MockResponse(404, {"message": "Not Found"})
        else:
            return MockResponse(200, DEFAULT_METADATA)

    mocker.patch("httpx.AsyncClient.get", side_effect=mock_get)
```

### Don't Mock These
- Core business logic (scorer, patterns)
- Data validation
- Configuration loading

---

## Coverage Requirements

| Component | Minimum | Target |
|-----------|---------|--------|
| Core (scorer, patterns) | 90% | 95% |
| Registry clients | 80% | 90% |
| CLI | 70% | 85% |
| Hooks | 70% | 80% |
| Overall | 80% | 85% |

---

## Test Commands

```bash
# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Run last failed
pytest --lf

# Run tests in parallel
pytest -n auto

# Generate coverage report
pytest --cov=phantom_guard --cov-report=term-missing

# Profile slow tests
pytest --durations=10
```

---

## CI Test Matrix

```yaml
# .github/workflows/test.yml
jobs:
  test:
    strategy:
      matrix:
        python: ["3.11", "3.12", "3.13"]
        os: [ubuntu-latest, macos-latest, windows-latest]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov
```
