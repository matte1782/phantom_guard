"""
Shared test fixtures and configuration.

Test Philosophy:
- Focus tests on CRITICAL paths that affect security/accuracy
- Don't over-test: internal helpers don't need exhaustive coverage
- Mock external APIs in unit tests, use real APIs in integration tests
- Every test should answer: "What user-facing bug does this prevent?"
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

# =============================================================================
# CRITICAL PATH TEST DATA
# These represent the core scenarios that MUST work correctly
# =============================================================================


@pytest.fixture
def legitimate_package_data() -> dict[str, Any]:
    """
    Data representing a well-established, safe package.
    This MUST score as SAFE - if it doesn't, we have a false positive.
    """
    return {
        "name": "flask",
        "exists": True,
        "release_count": 63,
        "downloads_last_month": 180_000_000,
        "has_repository": True,
        "repository_url": "https://github.com/pallets/flask",
        "maintainer_count": 5,
        "created_at": datetime(2010, 4, 6),
        "has_description": True,
    }


@pytest.fixture
def nonexistent_package_data() -> dict[str, Any]:
    """
    Data for a package that doesn't exist.
    This MUST score as BLOCKED - missing this is a critical security failure.
    """
    return {
        "name": "flask-gpt-helper",
        "exists": False,
    }


@pytest.fixture
def suspicious_package_data() -> dict[str, Any]:
    """
    Data for a package with multiple risk signals.
    This MUST score as SUSPICIOUS or higher.
    """
    return {
        "name": "gpt4-api",
        "exists": True,
        "release_count": 3,
        "downloads_last_month": 42,
        "has_repository": False,
        "repository_url": None,
        "maintainer_count": 1,
        "created_at": datetime(2024, 6, 1),
        "has_description": False,
    }


# =============================================================================
# HALLUCINATION PATTERN TEST DATA
# =============================================================================


@pytest.fixture
def hallucination_pattern_matches() -> list[str]:
    """Package names that MUST match hallucination patterns."""
    return [
        "flask-gpt-helper",
        "django-ai-utils",
        "requests-openai-client",
        "numpy-chatgpt",
        "pandas-gpt4",
        "fastapi-llm-helper",
    ]


@pytest.fixture
def legitimate_similar_names() -> list[str]:
    """Package names that look similar but are legitimate - must NOT match."""
    return [
        "django-rest-framework",
        "requests-oauthlib",
        "flask-sqlalchemy",
        "numpy-financial",
    ]


# =============================================================================
# API RESPONSE MOCKS
# =============================================================================


@pytest.fixture
def mock_pypi_flask_response() -> dict[str, Any]:
    """Mock PyPI API response for Flask package."""
    return {
        "info": {
            "name": "Flask",
            "author": "Pallets",
            "summary": "A simple framework for building complex web applications.",
            "home_page": "https://palletsprojects.com/p/flask",
            "project_urls": {
                "Source": "https://github.com/pallets/flask",
            },
        },
        "releases": {f"2.{i}.0": [{"upload_time": "2023-01-01T00:00:00"}] for i in range(10)},
    }


@pytest.fixture
def mock_pypi_404_response() -> dict[str, Any]:
    """Mock PyPI API 404 response."""
    return {"message": "Not Found"}


# =============================================================================
# TEST MARKERS
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "critical: marks tests for critical security/accuracy paths (run first)",
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require network access",
    )
    config.addinivalue_line(
        "markers",
        "e2e: marks end-to-end tests",
    )


# =============================================================================
# TEST COLLECTION HOOKS
# =============================================================================


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Reorder tests to run critical tests first.
    If critical tests fail, we want to know immediately.
    """
    critical_tests = []
    other_tests = []

    for item in items:
        if "critical" in item.keywords:
            critical_tests.append(item)
        else:
            other_tests.append(item)

    items[:] = critical_tests + other_tests
