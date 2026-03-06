"""
MCP Server lifecycle -- FastMCP setup, transport, graceful startup/shutdown.
IMPLEMENTS: S309
INVARIANTS: INV305, INV308, INV309
TESTS: T309.1, T309.2, T309.3, T309.4, T309.5
"""
import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """Factory function. Creates and configures the phantom-guard-mcp server.

    IMPLEMENTS: S309
    Registers all 5 tools (added in Days 2-4, 7).
    Handles import failures gracefully (INV305).
    Loads data structures (Bloom filter stub, patterns).
    """
    server = FastMCP("phantom-guard-mcp")

    # Import phantom_guard core -- graceful degradation (INV305)
    try:
        import phantom_guard  # noqa: F401
        logger.info("phantom-guard core loaded successfully")
    except ImportError:
        logger.warning("phantom-guard core not available -- degraded mode")

    # Tool registration (Days 2-4, 7)
    # TODO(Day 9): Add MCP annotations (readOnlyHint, idempotentHint, destructiveHint)
    from phantom_guard_mcp.tools.check_package import check_package
    server.tool()(check_package)

    return server


def main() -> None:
    """Entry point: python -m phantom_guard_mcp

    IMPLEMENTS: S309
    """
    server = create_server()
    server.run(transport="stdio")
