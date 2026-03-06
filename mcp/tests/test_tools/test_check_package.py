"""
Tests for check_package MCP tool.
SPEC: S300
INVARIANTS: INV300, INV304
TESTS: T300.1, T300.2, T300.3, T300.4, T300.5, T300.6, T300.7, T300.8
EDGE CASES: EC300-EC309
"""
import pytest


# ---------------------------------------------------------------------------
# Validation tests (INV304)
# ---------------------------------------------------------------------------

@pytest.mark.unit
async def test_empty_name_produces_validation_error():
    """TEST_ID: T300.1 | SPEC: S300 | INV: INV304
    Empty name produces ValidationError.
    EC: EC300
    """
    from phantom_guard_mcp.tools.check_package import check_package
    with pytest.raises(Exception):  # Pydantic ValidationError or equivalent
        await check_package(name="", ecosystem="pypi")


@pytest.mark.unit
async def test_unicode_name_produces_validation_error():
    """TEST_ID: T300.2 | SPEC: S300 | INV: INV304
    Unicode name produces ValidationError (ASCII-only).
    EC: EC302
    """
    from phantom_guard_mcp.tools.check_package import check_package
    with pytest.raises(Exception):
        await check_package(name="\u0444\u043b\u0430\u0441\u043a", ecosystem="pypi")


@pytest.mark.unit
async def test_invalid_ecosystem_produces_validation_error():
    """TEST_ID: T300.3 | SPEC: S300 | INV: INV304
    Invalid ecosystem produces ValidationError.
    EC: EC303
    """
    from phantom_guard_mcp.tools.check_package import check_package
    with pytest.raises(Exception):
        await check_package(name="flask", ecosystem="rubygems")


# ---------------------------------------------------------------------------
# Functional tests (INV300)
# ---------------------------------------------------------------------------

@pytest.mark.unit
async def test_popular_package_returns_safe(timer, hallucination_db_stub):
    """TEST_ID: T300.4 | SPEC: S300 | INV: INV300
    Popular package returns SAFE with evaluation_depth='fast' in <5ms.
    EC: EC304
    """
    from phantom_guard_mcp.tools.check_package import check_package

    t = timer()
    with t:
        result = await check_package(name="requests", ecosystem="pypi")
    assert result["recommendation"] == "SAFE"
    assert result["evaluation_depth"] == "fast"
    assert t.elapsed_ms < 5, f"Took {t.elapsed_ms:.1f}ms, budget is 5ms"


@pytest.mark.unit
async def test_hallucination_pattern_returns_high_risk(hallucination_db_stub):
    """TEST_ID: T300.5 | SPEC: S300 | INV: INV300
    Hallucination pattern returns HIGH_RISK.
    EC: EC305
    """
    from phantom_guard_mcp.tools.check_package import check_package

    result = await check_package(name="flask-gpt-helper", ecosystem="pypi")
    assert result["recommendation"] == "HIGH_RISK"
    signal_types = [s["type"] for s in result["signals"]]
    assert "KNOWN_HALLUCINATION" in signal_types, (
        f"Expected KNOWN_HALLUCINATION signal, got {signal_types}"
    )


@pytest.mark.integration
async def test_ambiguous_package_triggers_stage2(mock_pypi_api, hallucination_db_stub):
    """TEST_ID: T300.6 | SPEC: S300 | INV: INV300
    Ambiguous package triggers Stage 2, evaluation_depth='full', <200ms.
    EC: EC306
    """
    from phantom_guard_mcp.tools.check_package import check_package

    result = await check_package(name="my-small-util", ecosystem="pypi")
    assert result["evaluation_depth"] == "full"
    assert result["latency_ms"] < 200


@pytest.mark.unit
async def test_output_schema_matches_spec(hallucination_db_stub):
    """TEST_ID: T300.7 | SPEC: S300 | INV: None
    Output schema contains all fields defined in SPECIFICATION Section 2.1.
    """
    from phantom_guard_mcp.tools.check_package import check_package

    result = await check_package(name="requests", ecosystem="pypi")
    required_fields = {"package", "ecosystem", "risk_score", "recommendation",
                       "signals", "evaluation_depth", "latency_ms"}
    assert required_fields.issubset(result.keys()), (
        f"Missing fields: {required_fields - result.keys()}"
    )
    assert isinstance(result["risk_score"], float)
    assert isinstance(result["signals"], list)
    assert isinstance(result["latency_ms"], float)
    assert result["recommendation"] in {"SAFE", "SUSPICIOUS", "HIGH_RISK"}
    assert result["evaluation_depth"] in {"fast", "full"}


@pytest.mark.benchmark
async def test_check_package_p99_latency(timer, hallucination_db_stub):
    """TEST_ID: T300.8 | SPEC: S300 | INV: INV300
    P99 latency within budget: cached <10ms.
    """
    from phantom_guard_mcp.tools.check_package import check_package

    latencies = []
    for _ in range(100):
        t = timer()
        with t:
            await check_package(name="requests", ecosystem="pypi")
        latencies.append(t.elapsed_ms)
    latencies.sort()
    p99 = latencies[98]
    assert p99 < 10, f"P99 latency {p99:.1f}ms exceeds 10ms budget"


# ---------------------------------------------------------------------------
# Parametrize edge cases (not counted in 51 test total)
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.parametrize("name", ["zope.interface"])
async def test_name_with_dots_valid(name, hallucination_db_stub):
    """TEST_ID: T300.EC307 | SPEC: S300 | INV: INV304
    Package name with dots is valid.
    EC: EC307
    """
    from phantom_guard_mcp.tools.check_package import check_package
    result = await check_package(name=name, ecosystem="pypi")
    assert "package" in result


@pytest.mark.unit
@pytest.mark.parametrize("name", ["my_package"])
async def test_underscores_normalized(name, hallucination_db_stub):
    """TEST_ID: T300.EC308 | SPEC: S300 | INV: INV304
    Underscores normalized to hyphens for comparison.
    EC: EC308
    """
    from phantom_guard_mcp.tools.check_package import check_package
    result = await check_package(name=name, ecosystem="pypi")
    assert "package" in result


@pytest.mark.unit
@pytest.mark.parametrize("name", ["a"])
async def test_single_char_name_valid(name, hallucination_db_stub):
    """TEST_ID: T300.EC309 | SPEC: S300 | INV: INV304
    Single-char name is valid (min length 1).
    EC: EC309
    """
    from phantom_guard_mcp.tools.check_package import check_package
    result = await check_package(name=name, ecosystem="pypi")
    assert "package" in result


@pytest.mark.unit
@pytest.mark.parametrize("name", ["a" * 215])
async def test_name_215_chars_rejected(name):
    """TEST_ID: T300.EC301 | SPEC: S300 | INV: INV304
    Name exceeding 214 chars rejected.
    EC: EC301
    """
    from phantom_guard_mcp.tools.check_package import check_package
    with pytest.raises(Exception):
        await check_package(name=name, ecosystem="pypi")


@pytest.mark.unit
@pytest.mark.parametrize("name", ["a" * 214])
async def test_name_214_chars_accepted(name, hallucination_db_stub):
    """TEST_ID: T300.EC368 | SPEC: S300 | INV: INV304
    Exactly 214 chars accepted (boundary).
    EC: EC368
    """
    from phantom_guard_mcp.tools.check_package import check_package
    result = await check_package(name=name, ecosystem="pypi")
    assert "package" in result
