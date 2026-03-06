"""
Shared validation constants and utilities for MCP tools.
IMPLEMENTS: S300, S302, S303 (shared input validation, INV304)
"""
from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator


PACKAGE_NAME_REGEX = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$")
MAX_PACKAGE_NAME_LENGTH = 214  # npm standard, per core
VALID_ECOSYSTEMS = {"pypi", "npm", "crates"}

# Visual confusables preprocessing (S308, INV312)
# Only these 3 allowlisted pairs are expanded.
VISUAL_CONFUSABLES: dict[str, str] = {"rn": "m", "vv": "w", "cl": "d"}


def normalize_visual(name: str) -> str:
    """Apply visual confusable substitutions. IMPLEMENTS: S308, INV312"""
    result = name
    for seq, replacement in VISUAL_CONFUSABLES.items():
        result = result.replace(seq, replacement)
    return result


class NameInput(BaseModel):
    """Base input validation for package name. IMPLEMENTS: INV304"""
    name: str = Field(min_length=1, max_length=MAX_PACKAGE_NAME_LENGTH)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not PACKAGE_NAME_REGEX.match(v):
            raise ValueError(f"Invalid package name: {v!r}")
        return v


class NameEcosystemInput(NameInput):
    """Input validation for name + ecosystem. IMPLEMENTS: INV304"""
    ecosystem: str = Field(default="pypi")

    @field_validator("ecosystem")
    @classmethod
    def validate_ecosystem(cls, v: str) -> str:
        if v not in VALID_ECOSYSTEMS:
            raise ValueError(f"Invalid ecosystem: {v!r}. Must be one of {VALID_ECOSYSTEMS}")
        return v
