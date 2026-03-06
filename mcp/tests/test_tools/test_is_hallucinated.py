"""
Tests for is_hallucinated MCP tool.
SPEC: S302
INVARIANTS: INV300, INV301, INV304
TESTS: T302.1, T302.2, T302.3, T302.4, T302.5, T302.6
EDGE CASES: EC320-EC329
"""
import pytest
import respx


@pytest.mark.unit
@pytest.mark.stage1
async def test_known_hallucination_returns_true(hallucination_db_stub):
    """TEST_ID: T302.1 | SPEC: S302 | INV: INV301
    Known hallucination from DB returns hallucinated=true.
    EC: EC320
    """
    from phantom_guard_mcp.tools.is_hallucinated import is_hallucinated

    result = await is_hallucinated(name="huggingface-cli")
    assert result["hallucinated"] is True
    assert result["confidence"] >= 0.85


@pytest.mark.unit
@pytest.mark.stage1
async def test_popular_package_returns_false(hallucination_db_stub):
    """TEST_ID: T302.2 | SPEC: S302 | INV: INV301
    Popular package returns hallucinated=false with high confidence.
    EC: EC321
    """
    from phantom_guard_mcp.tools.is_hallucinated import is_hallucinated

    result = await is_hallucinated(name="numpy")
    assert result["hallucinated"] is False
    assert result["confidence"] >= 0.95


@pytest.mark.unit
@pytest.mark.stage1
async def test_pattern_match_returns_true_with_reason(hallucination_db_stub):
    """TEST_ID: T302.3 | SPEC: S302 | INV: INV301
    Pattern match (POPULAR_AI_COMBO) returns hallucinated=true with reason.
    EC: EC322
    """
    from phantom_guard_mcp.tools.is_hallucinated import is_hallucinated

    result = await is_hallucinated(name="flask-gpt-helper")
    assert result["hallucinated"] is True
    assert len(result["reasons"]) > 0
    assert any("pattern" in r.lower() or "hallucination" in r.lower() for r in result["reasons"])


@pytest.mark.unit
@pytest.mark.stage1
async def test_no_signals_returns_false(hallucination_db_stub):
    """TEST_ID: T302.4 | SPEC: S302 | INV: INV301
    Neutral name with no signals returns hallucinated=false.
    EC: EC323
    """
    from phantom_guard_mcp.tools.is_hallucinated import is_hallucinated

    result = await is_hallucinated(name="xyzabc123")
    assert result["hallucinated"] is False
    assert result["confidence"] == 1.0
    assert result["reasons"] == []


@pytest.mark.unit
@pytest.mark.stage1
async def test_visual_similarity_returns_true(hallucination_db_stub):
    """TEST_ID: T302.5 | SPEC: S302 | INV: INV301
    Visual similarity attack (rn->m) returns hallucinated=true.
    EC: EC324
    """
    from phantom_guard_mcp.tools.is_hallucinated import is_hallucinated

    result = await is_hallucinated(name="rnatplotlib")
    assert result["hallucinated"] is True
    assert any("visual" in r.lower() for r in result["reasons"])


@pytest.mark.unit
@pytest.mark.stage1
async def test_zero_network_calls(hallucination_db_stub):
    """TEST_ID: T302.6 | SPEC: S302 | INV: INV301
    Assert exactly 0 network calls during is_hallucinated (INV301).
    Mock httpx globally and assert no calls were made.
    """
    with respx.mock(assert_all_called=False) as router:
        from phantom_guard_mcp.tools.is_hallucinated import is_hallucinated
        await is_hallucinated(name="flask-gpt-helper")
        assert len(router.calls) == 0, (
            f"Expected 0 network calls (INV301), got {len(router.calls)}"
        )
