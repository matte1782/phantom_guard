"""
check_packages MCP tool -- Batch validation with configurable concurrency.
IMPLEMENTS: S301
INVARIANTS: INV300, INV304, INV306
TESTS: T301.1, T301.2, T301.3, T301.4, T301.5, T301.6
"""
from __future__ import annotations

import asyncio
import time

from phantom_guard_mcp.tools._validation import NameEcosystemInput
from phantom_guard_mcp.tools.check_package import check_package

MAX_BATCH_SIZE = 100


class PackageRequest(NameEcosystemInput):
    """A single package to validate in a batch request.
    IMPLEMENTS: S301, INV304
    Inherits name/ecosystem validation from NameEcosystemInput.
    """


async def check_packages(
    packages: list[PackageRequest],
    concurrency: int = 10,
) -> dict:
    """Check multiple packages concurrently with bounded parallelism.

    IMPLEMENTS: S301
    INVARIANTS: INV300, INV304, INV306

    Validates a batch of packages using configurable concurrency via
    asyncio.Semaphore. Delegates each package to check_package and
    aggregates results with a summary.

    MCP Annotations: readOnlyHint=true, idempotentHint=true, destructiveHint=false
    """
    # 1. Validate inputs (INV304)
    if not packages:
        raise ValueError("At least one package required")
    if len(packages) > MAX_BATCH_SIZE:
        raise ValueError(f"Maximum {MAX_BATCH_SIZE} packages per batch")
    if not 1 <= concurrency <= 50:
        raise ValueError(f"concurrency must be between 1 and 50, got {concurrency}")

    # 2. Start timer
    start = time.perf_counter()

    # 3. Create semaphore for bounded concurrency (INV306)
    semaphore = asyncio.Semaphore(concurrency)

    async def _check_one(pkg: PackageRequest) -> dict:
        async with semaphore:
            try:
                return await check_package(name=pkg.name, ecosystem=pkg.ecosystem)
            except Exception as exc:
                return {
                    "package": pkg.name.lower().replace("_", "-"),
                    "ecosystem": pkg.ecosystem,
                    "risk_score": 0.0,
                    "recommendation": "ERROR",
                    "signals": [],
                    "evaluation_depth": "none",
                    "latency_ms": 0.0,
                    "error": str(exc),
                }

    # 4. Launch all checks concurrently
    results = list(await asyncio.gather(*[_check_one(pkg) for pkg in packages]))

    # 5. Compute summary
    safe = sum(1 for r in results if r["recommendation"] == "SAFE")
    suspicious = sum(1 for r in results if r["recommendation"] == "SUSPICIOUS")
    high_risk = sum(1 for r in results if r["recommendation"] == "HIGH_RISK")

    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "results": results,
        "summary": {
            "total": len(results),
            "safe": safe,
            "suspicious": suspicious,
            "high_risk": high_risk,
        },
        "latency_ms": latency_ms,
    }
