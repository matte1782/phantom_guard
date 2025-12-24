"""
IMPLEMENTS: S006
INVARIANTS: INV009
Typosquat detection using edit distance.

This module provides functions to detect potential typosquatting attacks
by comparing package names against a database of popular packages using
Levenshtein (edit) distance.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from phantom_guard.core.types import Signal, SignalType

# =============================================================================
# TYPE ALIASES
# =============================================================================

Registry = Literal["pypi", "npm", "crates"]

# =============================================================================
# CONSTANTS
# =============================================================================

# Maximum edit distance to consider as typosquat
MAX_EDIT_DISTANCE: int = 2

# Minimum name length for typosquat detection (short names have too many matches)
MIN_NAME_LENGTH: int = 4

# Default similarity threshold (0.0, 1.0) exclusive - INV009
# Set to 0.65 to catch common typos like "reqeusts" (similarity ~0.75)
DEFAULT_SIMILARITY_THRESHOLD: float = 0.65

# =============================================================================
# POPULAR PACKAGES DATABASE
# =============================================================================

# Top 100 most popular packages per registry
# These are the most likely typosquat targets
POPULAR_PACKAGES: dict[str, frozenset[str]] = {
    "pypi": frozenset(
        {
            # Core/Essential
            "requests",
            "numpy",
            "pandas",
            "flask",
            "django",
            "scipy",
            "matplotlib",
            "pillow",
            "sqlalchemy",
            "pytest",
            "boto3",
            "pyyaml",
            "cryptography",
            "urllib3",
            "certifi",
            "setuptools",
            "wheel",
            "pip",
            "packaging",
            "six",
            # Web frameworks
            "jinja2",
            "markupsafe",
            "click",
            "werkzeug",
            "itsdangerous",
            "fastapi",
            "uvicorn",
            "starlette",
            "pydantic",
            "httpx",
            "aiohttp",
            "tornado",
            "gunicorn",
            "gevent",
            "eventlet",
            # Data processing
            "attrs",
            "decorator",
            "wrapt",
            "typing-extensions",
            "dataclasses",
            "idna",
            "chardet",
            "charset-normalizer",
            "beautifulsoup4",
            "lxml",
            # Database
            "redis",
            "celery",
            "kombu",
            "billiard",
            "amqp",
            "psycopg2",
            "pymysql",
            "pymongo",
            "elasticsearch",
            "alembic",
            # ML/AI
            "tensorflow",
            "keras",
            "torch",
            "transformers",
            "scikit-learn",
            "xgboost",
            "lightgbm",
            "catboost",
            "nltk",
            "spacy",
            # AWS
            "botocore",
            "s3transfer",
            "awscli",
            "boto",
            "moto",
            # Utilities
            "tqdm",
            "colorama",
            "rich",
            "python-dateutil",
            "pytz",
            "pathlib2",
            "filelock",
            "watchdog",
            "schedule",
            "apscheduler",
            # CLI
            "argparse",
            "docopt",
            "fire",
            "typer",
            "prompt-toolkit",
            # Testing
            "mock",
            "nose",
            "coverage",
            "tox",
            "hypothesis",
            # Linting/Formatting
            "black",
            "ruff",
            "mypy",
            "flake8",
            "pylint",
            "isort",
            "autopep8",
            "yapf",
            "bandit",
            "safety",
            # Other popular
            "openai",
            "anthropic",
            "langchain",
            "chromadb",
            "pinecone",
        }
    ),
    "npm": frozenset(
        {
            # Core
            "react",
            "lodash",
            "axios",
            "express",
            "moment",
            "typescript",
            "webpack",
            "babel-core",
            "eslint",
            "prettier",
            # Frameworks
            "next",
            "vue",
            "angular",
            "jquery",
            "underscore",
            "svelte",
            "nuxt",
            "gatsby",
            "remix",
            "astro",
            # Utilities
            "uuid",
            "chalk",
            "debug",
            "dotenv",
            "commander",
            "yargs",
            "inquirer",
            "ora",
            "cross-env",
            "rimraf",
            # React ecosystem
            "react-dom",
            "react-router",
            "redux",
            "mobx",
            "zustand",
            "react-query",
            "swr",
            "formik",
            "react-hook-form",
            "styled-components",
            # Node.js
            "fs-extra",
            "glob",
            "chokidar",
            "nodemon",
            "pm2",
            "cors",
            "helmet",
            "morgan",
            "body-parser",
            "cookie-parser",
        }
    ),
    "crates": frozenset(
        {
            # Core
            "serde",
            "tokio",
            "reqwest",
            "clap",
            "rand",
            "log",
            "regex",
            "chrono",
            "anyhow",
            "thiserror",
            # Async
            "async-trait",
            "futures",
            "async-std",
            "smol",
            "actix",
            # Web
            "hyper",
            "axum",
            "warp",
            "rocket",
            "actix-web",
            # Serialization
            "serde-json",
            "toml",
            "yaml-rust",
            "csv",
            "bincode",
            # Utilities
            "lazy-static",
            "once-cell",
            "parking-lot",
            "crossbeam",
            "rayon",
            "itertools",
            "num",
            "uuid",
            "base64",
            "sha2",
        }
    ),
}


def get_popular_packages(registry: str) -> frozenset[str]:
    """
    Get set of popular packages for a registry.

    Args:
        registry: Registry name (pypi, npm, crates)

    Returns:
        Frozenset of popular package names
    """
    return POPULAR_PACKAGES.get(registry.lower(), frozenset())


def is_popular_package(name: str, registry: str) -> bool:
    """
    Check if a package name is in the popular packages list.

    Args:
        name: Package name to check
        registry: Registry name

    Returns:
        True if the package is popular, False otherwise
    """
    return name.lower() in get_popular_packages(registry)


# =============================================================================
# LEVENSHTEIN DISTANCE
# =============================================================================


@lru_cache(maxsize=10000)
def levenshtein_distance(s1: str, s2: str) -> int:
    """
    IMPLEMENTS: S006
    INVARIANT: Result is always non-negative integer

    Calculate Levenshtein (edit) distance between two strings.

    Uses dynamic programming with O(min(m,n)) space complexity.
    Results are cached for performance.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Minimum number of single-character edits to transform s1 to s2
    """
    # Ensure s1 is the shorter string for space optimization
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    if len(s1) == 0:
        return len(s2)

    # Use only two rows instead of full matrix
    previous_row: list[int] = list(range(len(s1) + 1))
    current_row: list[int] = [0] * (len(s1) + 1)

    for i, c2 in enumerate(s2):
        current_row[0] = i + 1
        for j, c1 in enumerate(s1):
            # Cost is 0 if characters match, 1 otherwise
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row[j + 1] = min(insertions, deletions, substitutions)
        previous_row, current_row = current_row, previous_row

    return previous_row[len(s1)]


def normalized_distance(s1: str, s2: str) -> float:
    """
    Calculate normalized edit distance (0.0 to 1.0).

    Args:
        s1: First string
        s2: Second string

    Returns:
        0.0 for identical strings, 1.0 for completely different
    """
    if not s1 and not s2:
        return 0.0
    max_len = max(len(s1), len(s2))
    return levenshtein_distance(s1, s2) / max_len


def similarity(s1: str, s2: str) -> float:
    """
    Calculate similarity between two strings (0.0 to 1.0).

    Args:
        s1: First string
        s2: Second string

    Returns:
        1.0 for identical strings, 0.0 for completely different
    """
    return 1.0 - normalized_distance(s1, s2)


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass(frozen=True, slots=True)
class TyposquatMatch:
    """
    IMPLEMENTS: S006
    A potential typosquat match result.
    """

    target: str  # The popular package this might be typosquatting
    distance: int  # Edit distance
    similarity: float  # Similarity score (1.0 = identical)


# =============================================================================
# TYPOSQUAT DETECTOR
# =============================================================================


class TyposquatDetector:
    """
    IMPLEMENTS: S006
    INVARIANT: INV009 - threshold in (0.0, 1.0) exclusive

    Detector for typosquatting attacks.
    """

    def __init__(
        self,
        threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        max_distance: int = MAX_EDIT_DISTANCE,
    ) -> None:
        """
        Initialize the typosquat detector.

        Args:
            threshold: Similarity threshold for detection (0.0, 1.0) exclusive
            max_distance: Maximum edit distance to consider

        Raises:
            ValueError: If threshold is not in (0.0, 1.0) exclusive
        """
        # INV009: Validate threshold bounds
        if threshold <= 0.0 or threshold >= 1.0:
            raise ValueError(f"Threshold must be in (0.0, 1.0) exclusive, got {threshold}")
        self._threshold = threshold
        self._max_distance = max_distance

    @property
    def threshold(self) -> float:
        """Get the current similarity threshold."""
        return self._threshold

    @property
    def max_distance(self) -> int:
        """Get the maximum edit distance."""
        return self._max_distance

    def find_matches(
        self,
        name: str,
        registry: Registry,
    ) -> list[TyposquatMatch]:
        """
        Find potential typosquat targets for a package name.

        Args:
            name: Package name to check
            registry: Which registry to check against

        Returns:
            List of potential targets, sorted by similarity (highest first)
        """
        if len(name) < MIN_NAME_LENGTH:
            return []

        name_lower = name.lower()
        popular = get_popular_packages(registry)
        matches: list[TyposquatMatch] = []

        for target in popular:
            if target == name_lower:
                continue  # Exact match, not a typosquat

            # Quick length filter (distance can't be less than length diff)
            if abs(len(target) - len(name_lower)) > self._max_distance:
                continue

            distance = levenshtein_distance(name_lower, target)
            if distance <= self._max_distance and distance > 0:
                sim = similarity(name_lower, target)
                if sim >= self._threshold:
                    matches.append(
                        TyposquatMatch(
                            target=target,
                            distance=distance,
                            similarity=sim,
                        )
                    )

        return sorted(matches, key=lambda m: m.similarity, reverse=True)


# =============================================================================
# PURE FUNCTIONS (for direct use)
# =============================================================================

# Default detector instance
_default_detector = TyposquatDetector()


def find_typosquat_targets(
    name: str,
    registry: Registry,
    max_distance: int = MAX_EDIT_DISTANCE,
) -> list[TyposquatMatch]:
    """
    IMPLEMENTS: S006
    Find potential typosquat targets for a package name.

    This is a convenience function using the default detector.

    Args:
        name: Package name to check
        registry: Which registry to check against
        max_distance: Maximum edit distance to consider

    Returns:
        List of potential targets, sorted by similarity (highest first)
    """
    if max_distance != MAX_EDIT_DISTANCE:
        detector = TyposquatDetector(max_distance=max_distance)
        return detector.find_matches(name, registry)
    return _default_detector.find_matches(name, registry)


def check_typosquat(
    name: str,
    registry: Registry = "pypi",
) -> TyposquatMatch | None:
    """
    IMPLEMENTS: S006
    Check if a package name is a potential typosquat.

    Args:
        name: Package name to check
        registry: Registry to check against

    Returns:
        The best typosquat match, or None if no match found
    """
    matches = find_typosquat_targets(name, registry)
    return matches[0] if matches else None


def detect_typosquat(
    name: str,
    registry: Registry = "pypi",
) -> tuple[Signal, ...]:
    """
    IMPLEMENTS: S006

    Check if package name is a potential typosquat and return signals.

    This is the main entry point for integrating with the signal system.

    Args:
        name: Package name to check
        registry: Registry to check against

    Returns:
        Tuple of typosquat signals (empty if no match)
    """
    matches = find_typosquat_targets(name, registry)

    if not matches:
        return ()

    signals: list[Signal] = []

    for match in matches[:3]:  # Top 3 matches
        # Weight based on similarity (higher similarity = higher risk)
        # similarity of 0.85+ gets weight 0.7-0.9
        weight = 0.5 + (match.similarity * 0.4)

        signals.append(
            Signal(
                type=SignalType.TYPOSQUAT,
                weight=min(0.95, max(0.3, weight)),  # Clamp to [0.3, 0.95]
                message=f"Possible typosquat of '{match.target}' (distance: {match.distance})",
                metadata={
                    "target": match.target,
                    "distance": match.distance,
                    "similarity": round(match.similarity, 3),
                },
            )
        )

    return tuple(signals)
