"""
Tests for check_packages MCP tool.
SPEC: S301
INVARIANTS: INV300, INV304, INV306
TESTS: T301.1, T301.2, T301.3, T301.4, T301.5, T301.6
EDGE CASES: EC310, EC312, EC314, EC315, EC316, EC318
"""
import asyncio

import pytest


# ---------------------------------------------------------------------------
# Validation tests (INV304)
# ---------------------------------------------------------------------------

@pytest.mark.unit
async def test_empty_batch_produces_error():
    """TEST_ID: T301.1 | SPEC: S301 | INV: INV304
    Empty batch produces error with correct message.
    EC: EC310
    """
    from phantom_guard_mcp.tools.check_packages import check_packages

    with pytest.raises(ValueError, match="At least one package required"):
        await check_packages(packages=[])


@pytest.mark.unit
async def test_over_100_packages_produces_error(hallucination_db_stub):
    """TEST_ID: T301.3 | SPEC: S301 | INV: INV304
    Over 100 packages produces error with '100' in message.
    EC: EC314
    """
    from phantom_guard_mcp.tools.check_packages import (
        PackageRequest,
        check_packages,
    )

    packages = [PackageRequest(name=f"pkg-{i}", ecosystem="pypi") for i in range(101)]
    with pytest.raises(ValueError, match="100"):
        await check_packages(packages=packages)


@pytest.mark.unit
async def test_invalid_concurrency_produces_error():
    """TEST_ID: T301.3b | SPEC: S301 | INV: INV304
    Invalid concurrency values (0, 51) produce errors.
    """
    from phantom_guard_mcp.tools.check_packages import (
        PackageRequest,
        check_packages,
    )

    packages = [PackageRequest(name="flask", ecosystem="pypi")]
    with pytest.raises(ValueError, match="concurrency"):
        await check_packages(packages=packages, concurrency=0)
    with pytest.raises(ValueError, match="concurrency"):
        await check_packages(packages=packages, concurrency=51)


# ---------------------------------------------------------------------------
# Concurrency / batch tests (INV306)
# ---------------------------------------------------------------------------

@pytest.mark.integration
async def test_50_packages_within_5s(
    timer, mock_all_registries, hallucination_db_stub
):
    """TEST_ID: T301.2 | SPEC: S301 | INV: INV306
    50 packages complete within 5s budget.
    EC: EC312
    """
    from phantom_guard_mcp.tools.check_packages import (
        PackageRequest,
        check_packages,
    )

    packages = [
        PackageRequest(name=f"pkg-{i}", ecosystem="pypi") for i in range(50)
    ]
    t = timer()
    with t:
        result = await check_packages(packages=packages)

    assert result["summary"]["total"] == 50
    assert len(result["results"]) == 50
    assert t.elapsed_ms < 5000, f"Took {t.elapsed_ms:.1f}ms, budget is 5000ms"
    assert isinstance(result["latency_ms"], float)


@pytest.mark.unit
async def test_semaphore_enforced_at_concurrency_limit(
    hallucination_db_stub, monkeypatch
):
    """TEST_ID: T301.4 | SPEC: S301 | INV: INV306
    Semaphore enforced: concurrent active tasks never exceed concurrency limit.
    EC: EC318
    """
    import phantom_guard_mcp.tools.check_packages as cp_mod

    max_concurrent = 0
    current = 0

    _original_check = cp_mod.check_package

    async def counting_check(name: str, ecosystem: str = "pypi") -> dict:
        nonlocal max_concurrent, current
        current += 1
        if current > max_concurrent:
            max_concurrent = current
        await asyncio.sleep(0.01)
        result = await _original_check(name=name, ecosystem=ecosystem)
        current -= 1
        return result

    monkeypatch.setattr(cp_mod, "check_package", counting_check)

    from phantom_guard_mcp.tools.check_packages import PackageRequest, check_packages

    concurrency_limit = 3
    packages = [
        PackageRequest(name=f"pkg-{i}", ecosystem="pypi") for i in range(10)
    ]
    result = await check_packages(packages=packages, concurrency=concurrency_limit)

    assert result["summary"]["total"] == 10
    assert len(result["results"]) == 10
    assert max_concurrent <= concurrency_limit, (
        f"Max concurrent was {max_concurrent}, limit is {concurrency_limit}"
    )


# ---------------------------------------------------------------------------
# Functional tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
async def test_duplicate_packages_both_processed(
    mock_all_registries, hallucination_db_stub
):
    """TEST_ID: T301.5 | SPEC: S301 | INV: None
    Duplicate packages are both processed (no dedup).
    EC: EC315
    """
    from phantom_guard_mcp.tools.check_packages import (
        PackageRequest,
        check_packages,
    )

    packages = [
        PackageRequest(name="flask", ecosystem="pypi"),
        PackageRequest(name="flask", ecosystem="pypi"),
    ]
    result = await check_packages(packages=packages)

    assert result["summary"]["total"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["package"] == "flask"
    assert result["results"][1]["package"] == "flask"


@pytest.mark.unit
async def test_mixed_ecosystems_routed_correctly(
    mock_all_registries, hallucination_db_stub
):
    """TEST_ID: T301.6 | SPEC: S301 | INV: None
    Mixed ecosystems routed correctly.
    EC: EC316
    """
    from phantom_guard_mcp.tools.check_packages import (
        PackageRequest,
        check_packages,
    )

    packages = [
        PackageRequest(name="flask", ecosystem="pypi"),
        PackageRequest(name="express", ecosystem="npm"),
        PackageRequest(name="serde", ecosystem="crates"),
    ]
    result = await check_packages(packages=packages)

    assert result["summary"]["total"] == 3
    assert len(result["results"]) == 3

    ecosystems_in_results = {r["ecosystem"] for r in result["results"]}
    assert "pypi" in ecosystems_in_results
    assert "npm" in ecosystems_in_results
    assert "crates" in ecosystems_in_results
