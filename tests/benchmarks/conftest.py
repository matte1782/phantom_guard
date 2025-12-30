# SPEC: Shared fixtures and configuration for benchmark tests
# Gate 3: Test Design
"""
Phantom Guard Benchmark Test Configuration

Provides shared fixtures, markers, and configuration for all benchmark tests.
Includes pytest-benchmark settings, HTTP mocking with respx, and pre-configured
cache/detector instances.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import pytest
import respx
from httpx import Response

from phantom_guard.cache.memory import MemoryCache
from phantom_guard.cache.sqlite import AsyncSQLiteCache
from phantom_guard.core.types import PackageMetadata, Signal, SignalType
from phantom_guard.core.typosquat import TyposquatDetector
from phantom_guard.data import POPULAR_BY_REGISTRY as POPULAR_PACKAGES

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.fixtures import FixtureRequest

# =============================================================================
# PYTEST-BENCHMARK CONFIGURATION
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest-benchmark settings and custom markers."""
    # Register benchmark-specific markers
    config.addinivalue_line(
        "markers", "benchmark_group(name): Group related benchmarks for comparison"
    )
    config.addinivalue_line(
        "markers", "benchmark_budget(ms): Expected performance budget in milliseconds"
    )


@pytest.fixture(scope="session")
def benchmark_config() -> dict[str, Any]:
    """
    Pytest-benchmark configuration settings.

    Returns:
        Dict with benchmark configuration options
    """
    return {
        "min_rounds": 5,
        "max_time": 1.0,
        "min_time": 0.000005,
        "warmup": True,
        "warmup_iterations": 100,
        "disable_gc": True,
        "calibration_precision": 10,
        "timer": "perf_counter",
    }


# =============================================================================
# SAMPLE PACKAGE DATA FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def sample_packages() -> list[str]:
    """
    List of 100 sample package names for benchmarks.

    SPEC: Performance budgets
    Used for: Batch validation benchmarks, throughput testing

    Returns:
        List of 100 package names with realistic distribution:
        - 50 legitimate popular packages
        - 30 suspicious pattern packages
        - 20 typosquat candidates
    """
    # Legitimate popular packages (50)
    popular = [
        "requests",
        "flask",
        "django",
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "pillow",
        "sqlalchemy",
        "pytest",
        "boto3",
        "pyyaml",
        "cryptography",
        "urllib3",
        "certifi",
        "setuptools",
        "wheel",
        "pip",
        "packaging",
        "six",
        "jinja2",
        "markupsafe",
        "click",
        "werkzeug",
        "itsdangerous",
        "fastapi",
        "uvicorn",
        "starlette",
        "pydantic",
        "httpx",
        "aiohttp",
        "tornado",
        "gunicorn",
        "gevent",
        "eventlet",
        "attrs",
        "decorator",
        "wrapt",
        "typing-extensions",
        "dataclasses",
        "redis",
        "celery",
        "kombu",
        "billiard",
        "amqp",
        "tqdm",
        "colorama",
        "rich",
        "python-dateutil",
        "pytz",
    ]

    # Suspicious pattern packages (30)
    suspicious = [
        "flask-gpt",
        "django-ai",
        "react-chatgpt",
        "numpy-helper",
        "pandas-wrapper",
        "easy-requests",
        "simple-flask",
        "auto-django",
        "flask-gpt-helper",
        "django-ai-utils",
        "fastapi-openai-client",
        "requests-llm-wrapper",
        "numpy-ml-helper",
        "pandas-ai-utils",
        "easy-numpy",
        "simple-pandas",
        "auto-pytest",
        "py-gpt-helper",
        "flask-chatbot",
        "django-llm",
        "react-ai-helper",
        "vue-gpt",
        "express-ai",
        "lodash-helper",
        "axios-wrapper",
        "moment-utils",
        "typescript-helper",
        "webpack-ai",
        "babel-gpt",
        "eslint-helper",
    ]

    # Typosquat candidates (20)
    typosquats = [
        "reqeusts",
        "flak",
        "djagno",
        "numppy",
        "padas",
        "requets",
        "djnago",
        "flaask",
        "panads",
        "npumy",
        "reuqests",
        "flasks",
        "djangoo",
        "numpty",
        "pandsa",
        "requst",
        "flanks",
        "djang",
        "nympy",
        "pnadas",
    ]

    return popular + suspicious + typosquats


@pytest.fixture(scope="session")
def popular_packages_sample() -> dict[str, list[str]]:
    """
    Sample from popular packages list per registry.

    SPEC: S006
    Used for: Typosquat detection benchmarks

    Returns:
        Dict mapping registry to list of popular packages
    """
    return {
        "pypi": list(POPULAR_PACKAGES["pypi"])[:50],
        "npm": list(POPULAR_PACKAGES["npm"])[:30],
        "crates": list(POPULAR_PACKAGES["crates"])[:20],
    }


@pytest.fixture(scope="session")
def legitimate_packages() -> list[str]:
    """
    List of 50 legitimate package names that should not trigger false positives.

    SPEC: S006 - False positive prevention
    Used for: Accuracy benchmarks
    """
    return [
        "requests",
        "flask",
        "django",
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "pillow",
        "sqlalchemy",
        "pytest",
        "boto3",
        "pyyaml",
        "cryptography",
        "urllib3",
        "certifi",
        "setuptools",
        "wheel",
        "pip",
        "packaging",
        "six",
        "jinja2",
        "markupsafe",
        "click",
        "werkzeug",
        "itsdangerous",
        "fastapi",
        "uvicorn",
        "starlette",
        "pydantic",
        "httpx",
        "aiohttp",
        "tornado",
        "gunicorn",
        "gevent",
        "eventlet",
        "attrs",
        "decorator",
        "wrapt",
        "typing-extensions",
        "dataclasses",
        "redis",
        "celery",
        "kombu",
        "billiard",
        "amqp",
        "tqdm",
        "colorama",
        "rich",
        "python-dateutil",
        "pytz",
    ]


# =============================================================================
# MOCK REGISTRY RESPONSE FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def mock_pypi_response() -> dict[str, Any]:
    """
    Mocked PyPI API response for benchmark tests.

    SPEC: S020-S026
    Used for: Registry client benchmarks with mocked HTTP

    Returns:
        Dict mimicking PyPI JSON API response structure
    """
    return {
        "info": {
            "name": "flask",
            "version": "2.3.0",
            "summary": "A simple framework for building complex web applications.",
            "author": "Armin Ronacher",
            "author_email": "armin@palletsprojects.com",
            "home_page": "https://palletsprojects.com/p/flask",
            "license": "BSD-3-Clause",
            "project_url": "https://pypi.org/project/flask/",
            "project_urls": {
                "Source": "https://github.com/pallets/flask",
                "Documentation": "https://flask.palletsprojects.com/",
            },
            "maintainer": "Pallets Team",
            "maintainer_email": "contact@palletsprojects.com",
            "keywords": "flask web framework wsgi",
            "classifiers": [
                "Development Status :: 5 - Production/Stable",
                "Framework :: Flask",
                "Programming Language :: Python :: 3",
            ],
        },
        "releases": {
            "2.3.0": [
                {
                    "upload_time": "2023-04-25T12:00:00",
                    "upload_time_iso_8601": "2023-04-25T12:00:00.000000Z",
                    "size": 94863,
                    "python_version": "py3",
                }
            ],
            "2.2.0": [
                {
                    "upload_time": "2022-08-01T12:00:00",
                    "upload_time_iso_8601": "2022-08-01T12:00:00.000000Z",
                    "size": 93876,
                    "python_version": "py3",
                }
            ],
            "2.1.0": [{"upload_time": "2022-03-28T12:00:00"}],
            "2.0.0": [{"upload_time": "2021-05-11T12:00:00"}],
            "1.1.4": [{"upload_time": "2021-05-06T12:00:00"}],
        },
        "urls": [
            {
                "filename": "flask-2.3.0-py3-none-any.whl",
                "url": "https://files.pythonhosted.org/packages/.../flask-2.3.0.whl",
                "size": 94863,
                "md5_digest": "abc123",
            }
        ],
    }


@pytest.fixture(scope="session")
def mock_pypi_not_found_response() -> dict[str, Any]:
    """
    Mocked PyPI 404 response.

    SPEC: S020-S026
    Used for: Registry client benchmarks for non-existent packages
    """
    return {"message": "Not Found"}


@pytest.fixture(scope="session")
def mock_npm_response() -> dict[str, Any]:
    """
    Mocked npm registry API response.

    SPEC: S027-S032
    Used for: npm registry client benchmarks
    """
    return {
        "name": "express",
        "version": "4.18.2",
        "description": "Fast, unopinionated, minimalist web framework",
        "main": "index.js",
        "author": {"name": "TJ Holowaychuk", "email": "tj@vision-media.ca"},
        "repository": {
            "type": "git",
            "url": "git+https://github.com/expressjs/express.git",
        },
        "homepage": "http://expressjs.com/",
        "license": "MIT",
        "keywords": ["express", "framework", "web", "rest", "router"],
        "maintainers": [
            {"name": "dougwilson", "email": "doug@somethingdoug.com"},
            {"name": "jasnell", "email": "jasnell@gmail.com"},
        ],
        "time": {
            "created": "2010-12-29T19:38:25.450Z",
            "modified": "2023-02-24T20:00:00.000Z",
            "4.18.2": "2022-10-08T20:00:00.000Z",
        },
        "versions": {"4.18.2": {}, "4.18.1": {}, "4.18.0": {}},
    }


@pytest.fixture(scope="session")
def mock_crates_response() -> dict[str, Any]:
    """
    Mocked crates.io API response.

    SPEC: S033-S039
    Used for: crates.io registry client benchmarks
    """
    return {
        "crate": {
            "name": "serde",
            "max_version": "1.0.193",
            "description": "A generic serialization/deserialization framework",
            "homepage": "https://serde.rs",
            "repository": "https://github.com/serde-rs/serde",
            "documentation": "https://docs.rs/serde",
            "downloads": 250000000,
            "recent_downloads": 15000000,
            "created_at": "2015-02-27T00:00:00.000000+00:00",
            "updated_at": "2023-12-15T00:00:00.000000+00:00",
            "categories": ["encoding", "parsing"],
            "keywords": ["serde", "serialization", "deserialization"],
        },
        "versions": [
            {"num": "1.0.193", "created_at": "2023-12-15T00:00:00.000000+00:00"},
            {"num": "1.0.192", "created_at": "2023-11-28T00:00:00.000000+00:00"},
        ],
    }


# =============================================================================
# CACHE FIXTURES
# =============================================================================


@pytest.fixture
def memory_cache() -> MemoryCache:
    """
    Pre-configured MemoryCache instance for benchmarks.

    SPEC: S040-S042
    Scope: function (fresh cache per test)

    Returns:
        MemoryCache instance with default configuration
    """
    return MemoryCache(max_size=1000, default_ttl=3600)


@pytest.fixture
def memory_cache_session(request: FixtureRequest) -> MemoryCache:
    """
    Session-scoped MemoryCache for cross-test benchmarks.

    SPEC: S040-S042
    Scope: session (shared across tests)
    """
    cache = MemoryCache(max_size=5000, default_ttl=7200)
    return cache


@pytest.fixture
async def sqlite_cache(tmp_path: Path) -> AsyncSQLiteCache:
    """
    Temporary SQLite cache for benchmarks.

    SPEC: S040-S042
    Scope: function (isolated database per test)

    Args:
        tmp_path: Pytest-provided temporary directory

    Returns:
        Connected AsyncSQLiteCache instance (auto-closed after test)
    """
    db_path = tmp_path / "benchmark_cache.db"
    cache = AsyncSQLiteCache(db_path=db_path, default_ttl=86400)
    await cache.connect()
    yield cache
    await cache.close()


@pytest.fixture
async def sqlite_cache_with_data(tmp_path: Path, sample_packages: list[str]) -> AsyncSQLiteCache:
    """
    SQLite cache pre-populated with sample data for read benchmarks.

    SPEC: S040-S042
    Used for: Cache lookup benchmarks with warm cache

    Returns:
        AsyncSQLiteCache with 100 pre-populated entries
    """
    db_path = tmp_path / "benchmark_cache_populated.db"
    cache = AsyncSQLiteCache(db_path=db_path, default_ttl=86400)
    await cache.connect()

    # Pre-populate with sample package data
    for i, pkg_name in enumerate(sample_packages):
        await cache.set(
            f"pypi:{pkg_name}",
            {
                "name": pkg_name,
                "exists": True,
                "version": f"1.0.{i}",
                "downloads": 1000 * (i + 1),
            },
            ttl=86400,
        )

    yield cache
    await cache.close()


# =============================================================================
# DETECTOR FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def detector() -> TyposquatDetector:
    """
    Detector instance for benchmarks.

    SPEC: S006
    Used for: Typosquat detection benchmarks

    Returns:
        TyposquatDetector with default configuration
    """
    return TyposquatDetector(threshold=0.65, max_distance=2)


@pytest.fixture(scope="session")
def strict_detector() -> TyposquatDetector:
    """
    Stricter detector for comparison benchmarks.

    Returns:
        TyposquatDetector with higher threshold
    """
    return TyposquatDetector(threshold=0.80, max_distance=1)


# =============================================================================
# SIGNAL FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def benchmark_signals() -> list[Signal]:
    """
    Sample Signal objects for scorer benchmarks.

    SPEC: S007
    Used for: Risk scoring benchmarks

    Returns:
        List of sample signals with various types and weights
    """
    return [
        Signal(
            type=SignalType.NOT_FOUND,
            weight=0.9,
            message="Package not found on registry",
        ),
        Signal(
            type=SignalType.RECENTLY_CREATED,
            weight=0.4,
            message="Recently created: 5 days old",
            metadata={"age_days": 5},
        ),
        Signal(
            type=SignalType.LOW_DOWNLOADS,
            weight=0.3,
            message="Low downloads: 500/month",
            metadata={"downloads": 500},
        ),
        Signal(
            type=SignalType.NO_REPOSITORY,
            weight=0.25,
            message="No repository URL linked",
        ),
        Signal(
            type=SignalType.NO_MAINTAINER,
            weight=0.3,
            message="No maintainers listed",
        ),
        Signal(
            type=SignalType.FEW_RELEASES,
            weight=0.2,
            message="Few releases: 2",
            metadata={"release_count": 2},
        ),
        Signal(
            type=SignalType.SHORT_DESCRIPTION,
            weight=0.15,
            message="Short or missing description",
            metadata={"description_length": 5},
        ),
        Signal(
            type=SignalType.HALLUCINATION_PATTERN,
            weight=0.6,
            message="Matches hallucination pattern: AI_GPT_SUFFIX",
            metadata={"pattern": "AI_GPT_SUFFIX"},
        ),
        Signal(
            type=SignalType.TYPOSQUAT,
            weight=0.76,
            message="Possible typosquat of 'requests' (distance: 1)",
            metadata={"target": "requests", "distance": 1, "similarity": 0.875},
        ),
    ]


@pytest.fixture(scope="session")
def positive_signals() -> tuple[Signal, ...]:
    """
    Signals that reduce risk (negative weights).

    SPEC: S007
    Used for: Scorer benchmarks testing risk reduction
    """
    return (
        Signal(
            type=SignalType.POPULAR_PACKAGE,
            weight=-0.5,
            message="Popular package: 10,000,000/month",
            metadata={"downloads": 10000000},
        ),
        Signal(
            type=SignalType.LONG_HISTORY,
            weight=-0.2,
            message="Established package: 1825 days old",
            metadata={"age_days": 1825},
        ),
        Signal(
            type=SignalType.VERIFIED_PUBLISHER,
            weight=-0.3,
            message="Verified publisher",
        ),
    )


@pytest.fixture(scope="session")
def high_risk_signals() -> tuple[Signal, ...]:
    """
    Signals indicating high risk.

    SPEC: S007
    Used for: Scorer benchmarks testing high risk calculation
    """
    return (
        Signal(
            type=SignalType.NOT_FOUND,
            weight=0.9,
            message="Package not found",
        ),
        Signal(
            type=SignalType.TYPOSQUAT,
            weight=0.85,
            message="Possible typosquat of 'requests'",
            metadata={"target": "requests", "distance": 1, "similarity": 0.92},
        ),
        Signal(
            type=SignalType.HALLUCINATION_PATTERN,
            weight=0.7,
            message="Matches multiple patterns",
        ),
    )


# =============================================================================
# PACKAGE METADATA FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def sample_metadata() -> PackageMetadata:
    """
    Sample PackageMetadata for signal extraction benchmarks.

    SPEC: S004
    Used for: Signal extraction benchmarks
    """
    return PackageMetadata(
        name="flask",
        exists=True,
        registry="pypi",
        created_at=datetime.now(UTC) - timedelta(days=3650),  # 10 years old
        downloads_last_month=5000000,
        repository_url="https://github.com/pallets/flask",
        maintainer_count=5,
        release_count=100,
        latest_version="2.3.0",
        description="A simple framework for building complex web applications.",
    )


@pytest.fixture(scope="session")
def suspicious_metadata() -> PackageMetadata:
    """
    Suspicious PackageMetadata for signal extraction benchmarks.

    SPEC: S004
    Used for: Signal extraction benchmarks (suspicious case)
    """
    return PackageMetadata(
        name="flask-gpt-helper",
        exists=True,
        registry="pypi",
        created_at=datetime.now(UTC) - timedelta(days=5),  # 5 days old
        downloads_last_month=50,
        repository_url=None,
        maintainer_count=0,
        release_count=1,
        latest_version="0.1.0",
        description="AI",
    )


@pytest.fixture(scope="session")
def nonexistent_metadata() -> PackageMetadata:
    """
    Nonexistent PackageMetadata for signal extraction benchmarks.

    SPEC: S004
    Used for: Signal extraction benchmarks (not found case)
    """
    return PackageMetadata(
        name="reqeusts",
        exists=False,
        registry="pypi",
    )


# =============================================================================
# HTTP MOCKING FIXTURES
# =============================================================================


@pytest.fixture
def mock_pypi_api(mock_pypi_response: dict[str, Any]) -> respx.MockRouter:
    """
    HTTP mocking setup with respx for PyPI API.

    SPEC: S020-S026
    Used for: Registry client benchmarks with mocked HTTP

    Returns:
        Configured respx mock router
    """
    with respx.mock(assert_all_called=False) as router:
        # Mock successful package lookup
        router.get("https://pypi.org/pypi/flask/json").mock(
            return_value=Response(200, json=mock_pypi_response)
        )
        # Mock not found
        router.get("https://pypi.org/pypi/nonexistent-pkg-xyz/json").mock(
            return_value=Response(404, json={"message": "Not Found"})
        )
        yield router


@pytest.fixture
def mock_all_registries(
    mock_pypi_response: dict[str, Any],
    mock_npm_response: dict[str, Any],
    mock_crates_response: dict[str, Any],
) -> respx.MockRouter:
    """
    HTTP mocking for all registry APIs.

    Used for: Cross-registry benchmark tests
    """
    with respx.mock(assert_all_called=False) as router:
        # PyPI
        router.get(url__regex=r"https://pypi\.org/pypi/.+/json").mock(
            return_value=Response(200, json=mock_pypi_response)
        )
        # npm
        router.get(url__regex=r"https://registry\.npmjs\.org/.+").mock(
            return_value=Response(200, json=mock_npm_response)
        )
        # crates.io
        router.get(url__regex=r"https://crates\.io/api/v1/crates/.+").mock(
            return_value=Response(200, json=mock_crates_response)
        )
        yield router


# =============================================================================
# BENCHMARK HELPER FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def batch_sizes() -> list[int]:
    """
    Common batch sizes for throughput benchmarks.

    Returns:
        List of batch sizes: [10, 50, 100, 500, 1000]
    """
    return [10, 50, 100, 500, 1000]


@pytest.fixture(scope="session")
def concurrency_levels() -> list[int]:
    """
    Common concurrency levels for parallel benchmarks.

    Returns:
        List of concurrency levels: [1, 5, 10, 20, 50]
    """
    return [1, 5, 10, 20, 50]


@pytest.fixture(scope="session")
def performance_thresholds() -> dict[str, float]:
    """
    Performance budget thresholds in seconds.

    SPEC: Performance budgets from ARCHITECTURE.md

    Returns:
        Dict mapping operation to max allowed time in seconds
    """
    return {
        "single_cached": 0.010,  # 10ms
        "single_uncached": 0.200,  # 200ms
        "batch_50": 5.0,  # 5s
        "pattern_match": 0.001,  # 1ms
        "cache_get": 0.001,  # 1ms
        "cache_set": 0.001,  # 1ms
        "sqlite_get": 0.005,  # 5ms
        "sqlite_set": 0.010,  # 10ms
        "score_calculation": 0.0001,  # 0.1ms
    }
