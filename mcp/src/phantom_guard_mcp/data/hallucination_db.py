"""
IMPLEMENTS: S307
INVARIANTS: INV303, INV310, INV311
TESTS: T307.1-T307.6 (Phase 2)

Phase 1 STUB: Uses frozenset instead of pybloom_live Bloom filter.
Full Bloom filter implementation is W15.2 (Phase 2).
"""
from __future__ import annotations


class HallucinationDB:
    """Stub HallucinationDB using frozenset for Phase 1.

    Phase 2 (W15.2) replaces this with pybloom_live BloomFilter
    over the USENIX 205K hallucinated names dataset.
    """

    def __init__(self) -> None:
        self._full_set: frozenset[str] = frozenset({
            "flask-gpt-helper", "django-openai-utils", "numpy-ai-toolkit",
            "requests-chatgpt", "huggingface-cli", "pytorch-gpt-wrapper",
        })
        self._repeatable_set: frozenset[str] = frozenset({
            "flask-gpt-helper", "huggingface-cli",
        })

    def contains(self, name: str) -> bool:
        """O(1) lookup. Normalizes: lowercase + underscore-to-hyphen."""
        return name.lower().replace("_", "-") in self._full_set

    def contains_repeatable(self, name: str) -> bool:
        """Check repeatable subset (43%, higher confidence)."""
        return name.lower().replace("_", "-") in self._repeatable_set
