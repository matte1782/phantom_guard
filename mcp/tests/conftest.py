"""
Shared fixtures for phantom-guard MCP server tests.
SPEC: S300-S309
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest
import respx
from httpx import Response


# -- Markers -------------------------------------------------------------------

def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: Unit tests (fast, no I/O)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "benchmark: Performance benchmarks")
    config.addinivalue_line("markers", "statistical: Statistical validation tests")
    config.addinivalue_line("markers", "static: Static analysis tests")
    config.addinivalue_line("markers", "network: Tests requiring live network")
    config.addinivalue_line("markers", "stage1: Stage 1 evaluation tests (INV301)")
    config.addinivalue_line("markers", "stage2: Stage 2 evaluation tests (INV302)")
    config.addinivalue_line("markers", "parity: Result parity tests")
    config.addinivalue_line("markers", "mcp: MCP protocol tests")


# -- Package Name Fixtures -----------------------------------------------------

@pytest.fixture
def popular_packages() -> list[str]:
    return ["requests", "flask", "django", "numpy", "pandas",
            "fastapi", "torch", "scipy", "sqlalchemy", "celery"]


@pytest.fixture
def hallucinated_names() -> list[str]:
    return ["flask-gpt-helper", "django-openai-utils", "numpy-ai-toolkit",
            "requests-chatgpt", "py-easy-api", "auto-ml-helper"]


@pytest.fixture
def typosquat_pairs() -> list[tuple[str, str]]:
    return [("reqeusts", "requests"), ("flaks", "flask"),
            ("djnago", "django"), ("numppy", "numpy"), ("pnadas", "pandas")]


@pytest.fixture
def visual_similarity_attacks() -> list[tuple[str, str]]:
    return [("rnatplotlib", "matplotlib"), ("cljango", "django"),
            ("flasvv", "flask")]


# -- Mock Registry Fixtures ----------------------------------------------------

@pytest.fixture
def pypi_metadata_response() -> dict[str, Any]:
    return {
        "info": {"name": "flask", "version": "3.0.0",
                 "summary": "A simple framework for building complex web applications.",
                 "author": "Pallets", "license": "BSD-3-Clause",
                 "project_urls": {"Source Code": "https://github.com/pallets/flask"},
                 "requires_dist": ["Werkzeug>=3.0.0", "Jinja2>=3.1.2"]},
        "releases": {"0.1": [{"upload_time": "2010-04-06T00:00:00"}],
                     "1.0": [{"upload_time": "2018-04-26T00:00:00"}],
                     "3.0.0": [{"upload_time": "2023-09-30T00:00:00"}]},
    }


@pytest.fixture
def mock_pypi_api(pypi_metadata_response: dict) -> respx.MockRouter:
    with respx.mock(assert_all_called=False) as router:
        router.get("https://pypi.org/pypi/flask/json").mock(
            return_value=Response(200, json=pypi_metadata_response))
        router.get(url__regex=r"https://pypi\.org/pypi/(flask-gpt-helper|xyznotreal)/json").mock(
            return_value=Response(404, json={"message": "Not Found"}))
        router.get(url__regex=r"https://pypi\.org/pypi/.+/json").mock(
            return_value=Response(404, json={"message": "Not Found"}))
        yield router


@pytest.fixture
def mock_all_registries(pypi_metadata_response: dict) -> respx.MockRouter:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__regex=r"https://pypi\.org/pypi/.+/json").mock(
            return_value=Response(200, json=pypi_metadata_response))
        router.get(url__regex=r"https://registry\.npmjs\.org/.+").mock(
            return_value=Response(200, json={"name": "express", "versions": {}}))
        router.get(url__regex=r"https://crates\.io/api/v1/crates/.+").mock(
            return_value=Response(200, json={"crate": {"name": "serde"}}))
        yield router


# -- Cache Fixtures ------------------------------------------------------------

@pytest.fixture
async def mcp_cache(tmp_path: Path):
    from phantom_guard.cache import Cache
    cache = Cache(cache_dir=tmp_path / "cache")
    await cache.initialize()
    yield cache
    await cache.close()


# -- Hallucination DB Stub -----------------------------------------------------

@pytest.fixture
def hallucination_db_stub():
    """Stub HallucinationDB using frozenset for unit tests."""
    class StubHallucinationDB:
        def __init__(self):
            self._full_set = frozenset({
                "flask-gpt-helper", "django-openai-utils", "numpy-ai-toolkit",
                "requests-chatgpt", "huggingface-cli", "pytorch-gpt-wrapper"})
            self._repeatable_set = frozenset({"flask-gpt-helper", "huggingface-cli"})

        def contains(self, name: str) -> bool:
            return name.lower().replace("_", "-") in self._full_set

        def contains_repeatable(self, name: str) -> bool:
            return name.lower().replace("_", "-") in self._repeatable_set

    return StubHallucinationDB()


# -- Performance Thresholds ----------------------------------------------------

@pytest.fixture(scope="session")
def mcp_performance_thresholds() -> dict[str, float]:
    return {"stage1": 0.005, "is_hallucinated": 0.005, "check_typosquat": 0.005,
            "stage2_cached": 0.010, "stage2_uncached": 0.200,
            "check_package_cached": 0.010, "check_package_uncached": 0.200,
            "batch_50": 5.0, "explain_risk": 0.500, "startup": 2.0}


# -- Timer Helper --------------------------------------------------------------

class Timer:
    def __init__(self): self.elapsed_ms: float = 0.0
    def __enter__(self):
        self._start = time.perf_counter()
        return self
    def __exit__(self, *args):
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000

@pytest.fixture
def timer() -> type[Timer]:
    return Timer
