"""
check_typosquat MCP tool -- Fast-path typosquat check (Stage 1 only).
IMPLEMENTS: S303
INVARIANTS: INV300, INV301, INV304
TESTS: T303.1, T303.2, T303.3, T303.4, T303.5
"""
from __future__ import annotations

from phantom_guard_mcp.tools._validation import NameEcosystemInput, normalize_visual


async def check_typosquat(name: str, ecosystem: str = "pypi") -> dict:
    """Check if a package name is a typosquat of a popular package.
    IMPLEMENTS: S303
    INVARIANTS: INV300, INV301, INV304

    Uses Levenshtein distance and ASCII visual-similarity detection
    against 3000+ popular packages. No network calls needed.
    """
    # 1. Validate input (INV304)
    validated = NameEcosystemInput(name=name, ecosystem=ecosystem)
    normalized = validated.name.lower().replace("_", "-")

    # 2. Popular package -> not a typosquat
    try:
        from phantom_guard.core.typosquat import is_popular_package
        if is_popular_package(normalized, validated.ecosystem):
            return {
                "name": normalized,
                "is_typosquat": False,
                "similar_to": None,
                "distance": None,
                "confidence": 0.95,
                "method": "exact",
            }
    except ImportError:
        pass

    # 3. Visual similarity check (S308: rn->m, vv->w, cl->d)
    visual_normalized = normalize_visual(normalized)
    if visual_normalized != normalized:
        try:
            from phantom_guard.core.typosquat import is_popular_package
            if is_popular_package(visual_normalized, validated.ecosystem):
                return {
                    "name": normalized,
                    "is_typosquat": True,
                    "similar_to": visual_normalized,
                    "distance": None,
                    "confidence": 0.90,
                    "method": "visual_similarity",
                }
        except ImportError:
            pass

    # 4. Levenshtein typosquat detection via core
    try:
        from phantom_guard.core.typosquat import check_typosquat as core_check_typosquat
        match = core_check_typosquat(normalized, validated.ecosystem)
        if match is not None:
            return {
                "name": normalized,
                "is_typosquat": True,
                "similar_to": match.target,
                "distance": match.distance,
                "confidence": match.similarity,
                "method": "levenshtein",
            }
    except ImportError:
        pass

    # 5. No match found
    return {
        "name": normalized,
        "is_typosquat": False,
        "similar_to": None,
        "distance": None,
        "confidence": 0.0,
        "method": "none",
    }
