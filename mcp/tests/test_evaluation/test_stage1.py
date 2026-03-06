"""
Tests for Stage 1 evaluation engine.
SPEC: S305
INVARIANTS: INV300, INV301
TESTS: T305.1, T305.2, T305.3, T305.4, T305.5, T305.6
EDGE CASES: EC340-EC342
"""
import pytest
import respx


@pytest.mark.unit
@pytest.mark.stage1
async def test_safe_early_exit_popular_package(hallucination_db_stub):
    """TEST_ID: T305.1 | SPEC: S305 | INV: INV301
    Score <0.10 triggers SAFE early exit for a popular package.
    EC: EC340
    """
    from phantom_guard_mcp.evaluation.stage1 import run_stage1

    result = await run_stage1("requests", ecosystem="pypi")

    assert result.score < 0.10
    assert result.early_exit is True
    assert result.recommendation == "SAFE"


@pytest.mark.unit
@pytest.mark.stage1
async def test_high_risk_early_exit_hallucination(hallucination_db_stub):
    """TEST_ID: T305.2 | SPEC: S305 | INV: INV301
    Score >0.60 triggers HIGH_RISK early exit for a known hallucination.
    EC: EC341
    """
    from phantom_guard_mcp.evaluation.stage1 import run_stage1

    result = await run_stage1("flask-gpt-helper", ecosystem="pypi")

    assert result.score > 0.60
    assert result.early_exit is True
    assert result.recommendation == "HIGH_RISK"


@pytest.mark.unit
@pytest.mark.stage1
async def test_ambiguous_score_no_early_exit(hallucination_db_stub):
    """TEST_ID: T305.3 | SPEC: S305 | INV: INV301
    Score in [0.10, 0.60] range produces no early exit and recommendation=None.
    EC: EC342

    Uses 'numpy-ai-toolkit' which is in the hallucination DB full set but NOT
    in the repeatable set, giving it a non-repeatable hallucination weight of
    0.40 per spec S307.
    """
    from phantom_guard_mcp.evaluation.stage1 import run_stage1

    result = await run_stage1("numpy-ai-toolkit", ecosystem="pypi")

    assert 0.10 <= result.score <= 0.60
    assert result.early_exit is False
    assert result.recommendation is None


@pytest.mark.unit
@pytest.mark.stage1
async def test_deterministic_signal_order(hallucination_db_stub):
    """TEST_ID: T305.4 | SPEC: S305 | INV: INV301
    Same input always produces identical signals in the same order.
    """
    from phantom_guard_mcp.evaluation.stage1 import run_stage1

    result_a = await run_stage1("flask-gpt-helper", ecosystem="pypi")
    result_b = await run_stage1("flask-gpt-helper", ecosystem="pypi")

    assert result_a.signals == result_b.signals
    assert result_a.score == result_b.score


@pytest.mark.unit
@pytest.mark.stage1
async def test_zero_network_calls(hallucination_db_stub):
    """TEST_ID: T305.5 | SPEC: S305 | INV: INV301
    Stage 1 must make exactly zero network calls (pre-computed only).
    """
    with respx.mock(assert_all_called=False) as router:
        from phantom_guard_mcp.evaluation.stage1 import run_stage1

        await run_stage1("flask-gpt-helper", ecosystem="pypi")

        assert len(router.calls) == 0, (
            f"Expected 0 network calls (INV301), got {len(router.calls)}"
        )


@pytest.mark.benchmark
@pytest.mark.stage1
async def test_stage1_performance_under_5ms(hallucination_db_stub, timer):
    """TEST_ID: T305.6 | SPEC: S305 | INV: INV300
    Stage 1 evaluation must complete in <5ms (performance budget).
    """
    from phantom_guard_mcp.evaluation.stage1 import run_stage1

    t = timer()
    with t:
        await run_stage1("flask-gpt-helper", ecosystem="pypi")

    assert t.elapsed_ms < 5.0, (
        f"Stage 1 took {t.elapsed_ms:.2f}ms, budget is <5ms (INV300)"
    )
