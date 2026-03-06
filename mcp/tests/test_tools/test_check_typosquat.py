"""
Tests for check_typosquat MCP tool.
SPEC: S303
INVARIANTS: INV300, INV301, INV304
TESTS: T303.1, T303.2, T303.3, T303.4, T303.5
EDGE CASES: EC325-EC329
"""
import pytest


@pytest.mark.unit
@pytest.mark.stage1
async def test_levenshtein_typosquat_detected():
    """TEST_ID: T303.1 | SPEC: S303 | INV: INV301
    Levenshtein typosquat of popular package detected.
    EC: EC325
    """
    from phantom_guard_mcp.tools.check_typosquat import check_typosquat

    result = await check_typosquat(name="reqeusts", ecosystem="pypi")
    assert result["is_typosquat"] is True
    assert result["similar_to"] == "requests"
    assert result["method"] == "levenshtein"


@pytest.mark.unit
@pytest.mark.stage1
async def test_visual_similarity_typosquat_detected():
    """TEST_ID: T303.2 | SPEC: S303 | INV: INV301
    Visual similarity typosquat (cl->d) detected.
    EC: EC326
    """
    from phantom_guard_mcp.tools.check_typosquat import check_typosquat

    result = await check_typosquat(name="cljango", ecosystem="pypi")
    assert result["is_typosquat"] is True
    assert result["similar_to"] == "django"
    assert result["method"] == "visual_similarity"


@pytest.mark.unit
@pytest.mark.stage1
async def test_no_match_returns_false():
    """TEST_ID: T303.3 | SPEC: S303 | INV: INV301
    Completely unique name returns is_typosquat=false.
    EC: EC327
    """
    from phantom_guard_mcp.tools.check_typosquat import check_typosquat

    result = await check_typosquat(name="completely-unique-pkg-name", ecosystem="pypi")
    assert result["is_typosquat"] is False
    assert result["similar_to"] is None


@pytest.mark.unit
@pytest.mark.stage1
async def test_popular_package_not_typosquat():
    """TEST_ID: T303.4 | SPEC: S303 | INV: INV301
    Popular package itself is not a typosquat.
    EC: EC328
    """
    from phantom_guard_mcp.tools.check_typosquat import check_typosquat

    result = await check_typosquat(name="flask", ecosystem="pypi")
    assert result["is_typosquat"] is False


@pytest.mark.unit
@pytest.mark.stage1
async def test_distance_1_typosquat_detected():
    """TEST_ID: T303.5 | SPEC: S303 | INV: INV301
    Distance=1 typosquat detected.
    EC: EC329
    NOTE: Uses 'numppy' not 'flaks' (plan errata: flaks has distance=2,
    similarity=0.6 < threshold 0.65).
    """
    from phantom_guard_mcp.tools.check_typosquat import check_typosquat

    result = await check_typosquat(name="numppy", ecosystem="pypi")
    assert result["is_typosquat"] is True
    assert result["distance"] == 1
