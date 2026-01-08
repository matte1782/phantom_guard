# SPEC: Shared test fixtures and configuration
# Gate 3: Test Design
"""
Phantom Guard Test Configuration

Provides shared fixtures, markers, and configuration for all tests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no I/O)")
    config.addinivalue_line("markers", "property: Property-based tests (hypothesis)")
    config.addinivalue_line("markers", "fuzz: Fuzz tests (random input generation)")
    config.addinivalue_line("markers", "integration: Integration tests (live APIs)")
    config.addinivalue_line("markers", "network: Tests requiring network access")
    config.addinivalue_line("markers", "benchmark: Performance benchmarks")
    config.addinivalue_line("markers", "security: Security-focused tests (attack vectors)")
    config.addinivalue_line("markers", "slow: Slow tests (>1s)")


# =============================================================================
# MARKERS FOR TEST TYPES
# =============================================================================

# Usage in tests:
# @pytest.mark.unit
# @pytest.mark.property
# @pytest.mark.integration
# @pytest.mark.benchmark


# =============================================================================
# SAMPLE PACKAGE DATA FIXTURES
# =============================================================================


@pytest.fixture
def valid_package_names() -> list[str]:
    """Valid package names for testing.

    SPEC: S001
    Used for: Positive validation tests
    """
    return [
        "flask",
        "requests",
        "django",
        "numpy",
        "pandas",
        "flask-redis-helper",
        "py3-redis",
        "flask_cors",
        "a",  # Minimum length
        "a" * 214,  # Maximum length
    ]


@pytest.fixture
def invalid_package_names() -> list[tuple[str, str]]:
    """Invalid package names with reason.

    SPEC: S001
    EDGE_CASES: EC001-EC015
    Used for: Negative validation tests
    """
    return [
        ("", "empty"),
        ("   ", "whitespace only"),
        ("a" * 300, "too long"),
        ("flask-", "trailing hyphen"),
        ("-flask", "leading hyphen"),
        ("flask--redis", "double hyphen"),
        ("flask@redis", "special character @"),
        ("flask>1.0", "special character >"),
        ("flask redis", "contains space"),
    ]


@pytest.fixture
def popular_packages() -> list[str]:
    """Top packages that should never flag as suspicious.

    SPEC: S006
    EDGE_CASE: EC043
    Used for: False positive prevention tests
    """
    return [
        "requests",
        "flask",
        "django",
        "numpy",
        "pandas",
        "boto3",
        "urllib3",
        "six",
        "certifi",
        "python-dateutil",
    ]


@pytest.fixture
def suspicious_package_names() -> list[str]:
    """Package names with hallucination patterns.

    SPEC: S005
    EDGE_CASES: EC100-EC110
    Used for: Pattern detection tests
    """
    return [
        "flask-gpt",
        "django-ai",
        "react-chatgpt",
        "requests-helper",
        "numpy-wrapper",
        "easy-requests",
        "simple-flask",
        "auto-django",
        "flask-gpt-helper",  # Compound pattern
    ]


@pytest.fixture
def typosquat_pairs() -> list[tuple[str, str]]:
    """(typosquat, legitimate) package pairs.

    SPEC: S006
    EDGE_CASE: EC046
    Used for: Typosquat detection tests
    """
    return [
        ("reqeusts", "requests"),
        ("djagno", "django"),
        ("flak", "flask"),
        ("numppy", "numpy"),
        ("padas", "pandas"),
        ("requets", "requests"),
        ("djnago", "django"),
    ]


# =============================================================================
# MOCK REGISTRY RESPONSE FIXTURES
# =============================================================================


@pytest.fixture
def pypi_success_response() -> dict:
    """Mock successful PyPI API response.

    SPEC: S020-S026
    EDGE_CASE: EC020
    """
    return {
        "info": {
            "name": "flask",
            "version": "2.3.0",
            "summary": "A simple framework for building complex web applications.",
            "author": "Armin Ronacher",
            "home_page": "https://palletsprojects.com/p/flask",
            "project_urls": {
                "Source": "https://github.com/pallets/flask",
            },
        },
        "releases": {
            "2.3.0": [{"upload_time": "2023-01-01T00:00:00"}],
            "2.2.0": [{"upload_time": "2022-06-01T00:00:00"}],
        },
    }


@pytest.fixture
def pypi_not_found_response() -> dict:
    """Mock PyPI 404 response.

    SPEC: S020-S026
    EDGE_CASE: EC021
    """
    return {"message": "Not Found"}


@pytest.fixture
def npm_success_response() -> dict:
    """Mock successful npm API response.

    SPEC: S027-S032
    EDGE_CASE: EC020
    """
    return {
        "name": "express",
        "version": "4.18.2",
        "description": "Fast, unopinionated, minimalist web framework",
        "repository": {
            "type": "git",
            "url": "git+https://github.com/expressjs/express.git",
        },
        "author": {"name": "TJ Holowaychuk"},
        "time": {
            "created": "2010-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
        },
    }


@pytest.fixture
def crates_success_response() -> dict:
    """Mock successful crates.io API response.

    SPEC: S033-S039
    EDGE_CASE: EC020
    """
    return {
        "crate": {
            "name": "serde",
            "max_version": "1.0.180",
            "description": "A generic serialization/deserialization framework",
            "homepage": "https://serde.rs",
            "repository": "https://github.com/serde-rs/serde",
            "downloads": 100000000,
            "created_at": "2015-01-01T00:00:00.000000+00:00",
        },
    }


# =============================================================================
# MOCK SIGNAL FIXTURES
# =============================================================================


@pytest.fixture
def all_risk_signals() -> list[str]:
    """All possible risk signals for maximum risk score.

    SPEC: S007
    EDGE_CASE: EC041
    """
    return [
        "TYPOSQUAT",
        "HALLUCINATION_PATTERN",
        "NEW_PACKAGE",
        "LOW_DOWNLOADS",
        "NO_REPOSITORY",
        "FEW_RELEASES",
        "NO_AUTHOR",
        "SHORT_DESCRIPTION",
    ]


@pytest.fixture
def no_risk_signals() -> list[str]:
    """No risk signals for minimum risk score.

    SPEC: S007
    EDGE_CASE: EC040
    """
    return []


# =============================================================================
# ASYNC FIXTURES
# =============================================================================


@pytest.fixture
async def async_client():
    """Async HTTP client for integration tests.

    SPEC: S020+
    Used for: Integration tests with live APIs
    """
    # Will be implemented during Gate 4-5
    pytest.skip("Stub - implement with registry clients")


# =============================================================================
# CACHE FIXTURES
# =============================================================================


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Temporary directory for cache tests.

    SPEC: S040-S049
    Used for: Cache isolation between tests
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


# =============================================================================
# BENCHMARK FIXTURES
# =============================================================================


@pytest.fixture
def benchmark_packages() -> list[str]:
    """Packages for benchmark tests.

    SPEC: Performance budgets
    Used for: Latency measurement
    """
    return ["flask", "requests", "django", "numpy", "pandas"] * 10  # 50 packages


# =============================================================================
# HYPOTHESIS PROFILES
# =============================================================================

try:
    from hypothesis import settings

    settings.register_profile("ci", max_examples=1000, deadline=None)
    settings.register_profile("dev", max_examples=100, deadline=500)
    settings.register_profile("quick", max_examples=10, deadline=200)

except ImportError:
    pass  # Hypothesis not installed yet
