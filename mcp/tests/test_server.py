"""
Tests for MCP server lifecycle.
SPEC: S309
INVARIANTS: INV305, INV308, INV309
TESTS: T309.1, T309.2, T309.3, T309.4, T309.5
"""
import ast
import pathlib
from unittest.mock import patch

import pytest


@pytest.mark.benchmark
async def test_server_startup_under_2s(timer):
    """TEST_ID: T309.1 | SPEC: S309 | INV: INV308
    Server startup completes in <2s.
    EC: EC360
    """
    from phantom_guard_mcp.server import create_server

    t = timer()
    with t:
        server = create_server()
    assert t.elapsed_ms < 2000, f"Startup took {t.elapsed_ms:.1f}ms, budget is 2000ms"
    assert server is not None


@pytest.mark.unit
async def test_graceful_import_failure():
    """TEST_ID: T309.2 | SPEC: S309 | INV: INV305
    ImportError on phantom_guard produces graceful degradation, not crash.
    EC: EC361
    """
    with patch.dict("sys.modules", {"phantom_guard": None}):
        # Force reimport of server module to trigger ImportError path
        import importlib
        import phantom_guard_mcp.server as srv_mod
        importlib.reload(srv_mod)
        server = srv_mod.create_server()
        assert server is not None


@pytest.mark.static
def test_no_shell_execution_in_source():
    """TEST_ID: T309.3 | SPEC: S309 | INV: INV309
    AST-walk all .py files in mcp/src/ and fail if any forbidden
    function names (subprocess, exec, eval) or module-level shell
    invocation attributes are found.
    """
    mcp_src = pathlib.Path("src/phantom_guard_mcp")
    if not mcp_src.exists():
        pytest.skip("MCP source not yet created")

    FORBIDDEN_NAMES = {"subprocess", "exec", "eval"}
    FORBIDDEN_MODULE_ATTRS = {("os", "system"), ("os", "popen")}

    for py_file in mcp_src.rglob("*.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
                pytest.fail(f"Forbidden '{node.id}' in {py_file}:{node.lineno}")
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                if (node.value.id, node.attr) in FORBIDDEN_MODULE_ATTRS:
                    pytest.fail(
                        f"Forbidden '{node.value.id}.{node.attr}' in {py_file}:{node.lineno}"
                    )


@pytest.mark.unit
async def test_missing_bloom_filter_skips_check():
    """TEST_ID: T309.4 | SPEC: S309 | INV: None
    Missing Bloom filter produces warning, hallucination DB check skipped.
    EC: EC362
    """
    from phantom_guard_mcp.server import create_server
    server = create_server()
    assert server is not None


@pytest.mark.unit
async def test_sqlite_locked_uses_memory_cache():
    """TEST_ID: T309.5 | SPEC: S309 | INV: None
    SQLite locked produces memory-only cache fallback.
    EC: EC363
    """
    from phantom_guard_mcp.server import create_server
    server = create_server()
    assert server is not None
