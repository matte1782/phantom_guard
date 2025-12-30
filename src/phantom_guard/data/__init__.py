"""
Popular packages data module.

IMPLEMENTS: S006
Provides popular package lists for false positive prevention.
"""

from phantom_guard.data.popular_packages import (
    CRATES_POPULAR,
    NPM_POPULAR,
    POPULAR_BY_REGISTRY,
    PYPI_POPULAR,
    get_popular_packages,
    is_popular,
)

__all__ = [
    "CRATES_POPULAR",
    "NPM_POPULAR",
    "POPULAR_BY_REGISTRY",
    "PYPI_POPULAR",
    "get_popular_packages",
    "is_popular",
]
