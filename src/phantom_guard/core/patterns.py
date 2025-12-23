"""Hallucination pattern matching for package names.

Detects package names that match common AI hallucination patterns.
These patterns are characteristic of names AI assistants make up.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class HallucinationPattern:
    """Pattern that suggests AI hallucination.

    Attributes:
        name: Short identifier for the pattern.
        pattern: Regular expression to match.
        description: Human-readable explanation.
        examples: Example package names that match.
    """

    name: str
    pattern: str
    description: str
    examples: tuple[str, ...]


# Common AI hallucination patterns
# These are names AI assistants frequently invent
HALLUCINATION_PATTERNS: tuple[HallucinationPattern, ...] = (
    HallucinationPattern(
        name="framework_ai_suffix",
        pattern=r"^(flask|django|fastapi|express|react|vue|angular|rails|spring|laravel)-?(gpt|ai|chatgpt|openai|llm|ml|claude|anthropic|gemini|bard)",
        description="Popular framework + AI suffix",
        examples=("flask-gpt", "django-chatgpt", "react-ai", "fastapi-llm"),
    ),
    HallucinationPattern(
        name="ai_generic_suffix",
        pattern=r"^(gpt|chatgpt|openai|claude|anthropic|gemini|bard|llama|mistral)-?(api|client|sdk|wrapper|helper|utils|tools|lib|py|js)",
        description="AI provider + generic suffix",
        examples=("gpt-api", "openai-helper", "chatgpt-wrapper", "claude-sdk"),
    ),
    HallucinationPattern(
        name="py_ai_prefix",
        pattern=r"^py-?(gpt|openai|chatgpt|claude|anthropic|gemini|bard|llm)",
        description="py prefix + AI provider",
        examples=("pygpt", "py-openai", "pychatgpt", "pyllm"),
    ),
    HallucinationPattern(
        name="simplicity_ai",
        pattern=r"^(easy|simple|quick|fast|super|auto|smart)-?(gpt|ai|openai|chatgpt|llm|ml)",
        description="Simplicity adjective + AI term",
        examples=("easy-gpt", "simple-ai", "auto-chatgpt", "smart-llm"),
    ),
    HallucinationPattern(
        name="ai_for_x",
        pattern=r"^(gpt|ai|openai|chatgpt|llm)-?(for|to|with|and)-",
        description="AI + connector + purpose",
        examples=("gpt-for-docs", "ai-to-sql", "chatgpt-with-memory"),
    ),
    HallucinationPattern(
        name="langchain_variant",
        pattern=r"^langchain-?(gpt|openai|claude|anthropic|helper|utils|extra|plus)",
        description="LangChain + variant suffix",
        examples=("langchain-gpt", "langchain-helper", "langchain-plus"),
    ),
    HallucinationPattern(
        name="vector_db_ai",
        pattern=r"^(pinecone|weaviate|milvus|qdrant|chroma)-?(gpt|ai|llm|helper|utils)",
        description="Vector DB + AI suffix",
        examples=("pinecone-gpt", "chroma-ai", "weaviate-llm"),
    ),
    HallucinationPattern(
        name="agent_framework",
        pattern=r"^(auto|super|mega|ultra|hyper)-?(agent|gpt|ai|assistant)",
        description="Superlative + agent/AI term",
        examples=("auto-agent", "super-gpt", "mega-assistant"),
    ),
    HallucinationPattern(
        name="generic_ai_helper",
        pattern=r"^(ai|ml|llm|gpt)-?(helper|utils|tools|toolkit|framework|engine|core)",
        description="Generic AI + helper suffix",
        examples=("ai-helper", "llm-toolkit", "gpt-framework"),
    ),
    HallucinationPattern(
        name="chat_completion",
        pattern=r"^(chat|completion|prompt)-?(gpt|openai|ai|helper|utils)",
        description="Chat/Completion + AI suffix",
        examples=("chat-gpt-helper", "completion-utils", "prompt-ai"),
    ),
)


class PatternMatcher:
    """Match package names against hallucination patterns.

    Compiled patterns are cached for performance.

    Usage:
        matcher = PatternMatcher()
        if pattern := matcher.match("flask-gpt"):
            print(f"Suspicious: {pattern.description}")
    """

    def __init__(
        self,
        patterns: tuple[HallucinationPattern, ...] | None = None,
    ) -> None:
        """Initialize pattern matcher.

        Args:
            patterns: Custom patterns to use. Defaults to HALLUCINATION_PATTERNS.
        """
        self.patterns = patterns or HALLUCINATION_PATTERNS
        self._compiled: list[tuple[re.Pattern[str], HallucinationPattern]] = [
            (re.compile(p.pattern, re.IGNORECASE), p) for p in self.patterns
        ]

    def match(self, package_name: str) -> HallucinationPattern | None:
        """Check if package name matches any hallucination pattern.

        Args:
            package_name: Name to check.

        Returns:
            Matching pattern, or None if no match.
        """
        for regex, pattern in self._compiled:
            if regex.search(package_name):
                return pattern
        return None

    def is_suspicious_name(self, package_name: str) -> bool:
        """Quick check if name is suspicious.

        Args:
            package_name: Name to check.

        Returns:
            True if name matches any pattern.
        """
        return self.match(package_name) is not None

    def all_matches(
        self,
        package_name: str,
    ) -> tuple[HallucinationPattern, ...]:
        """Find all patterns that match a package name.

        Args:
            package_name: Name to check.

        Returns:
            Tuple of all matching patterns.
        """
        matches = []
        for regex, pattern in self._compiled:
            if regex.search(package_name):
                matches.append(pattern)
        return tuple(matches)
