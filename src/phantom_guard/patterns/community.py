"""
IMPLEMENTS: S058
INVARIANTS: INV058, INV058a
Community Pattern Manager for Phantom Guard.

Manages loading, storing, and updating pattern databases from
multiple sources: built-in, user, and community.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from phantom_guard.core.patterns import HALLUCINATION_PATTERNS

logger = logging.getLogger(__name__)


# =============================================================================
# TYPES
# =============================================================================


class PatternSource(Enum):
    """Source of a pattern."""

    BUILTIN = "builtin"
    USER = "user"
    COMMUNITY = "community"


class PatternType(Enum):
    """Type of pattern matching."""

    PREFIX = "prefix"
    SUFFIX = "suffix"
    COMPOUND = "compound"
    REGEX = "regex"


@dataclass(frozen=True, slots=True)
class Pattern:
    """
    IMPLEMENTS: S058
    INVARIANT: INV058 - Pattern is validated before loading

    A pattern for hallucination detection.
    """

    id: str
    pattern_type: PatternType
    value: str
    confidence: float
    source: PatternSource
    description: str = ""
    base_package: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate pattern invariants."""
        # INV059: Confidence must be in [0.0, 1.0]
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Pattern confidence must be in [0.0, 1.0], got {self.confidence}")


@dataclass
class SignatureVerificationResult:
    """
    IMPLEMENTS: S058
    Result of signature verification for community patterns.
    """

    success: bool
    patterns: list[Pattern] = field(default_factory=list)
    error: str = ""


# =============================================================================
# COMMUNITY PATTERN MANAGER
# =============================================================================


class CommunityPatternManager:
    """
    IMPLEMENTS: S058
    INVARIANTS: INV058, INV058a

    Manage community-contributed patterns.

    Storage locations:
        - Built-in: Loaded from phantom_guard.core.patterns
        - User: ~/.phantom-guard/patterns.yaml
        - Community: ~/.phantom-guard/community-patterns.json

    Update mechanism:
        - Check GitHub releases for new patterns
        - Auto-update with user consent (INV058a)
    """

    def __init__(
        self,
        user_patterns_path: Path | None = None,
        community_patterns_path: Path | None = None,
    ) -> None:
        """
        Initialize the pattern manager.

        Args:
            user_patterns_path: Path to user patterns file.
                Defaults to ~/.phantom-guard/patterns.yaml
            community_patterns_path: Path to community patterns file.
                Defaults to ~/.phantom-guard/community-patterns.json
        """
        home = Path.home()
        config_dir = home / ".phantom-guard"

        self._user_patterns_path = user_patterns_path or (config_dir / "patterns.yaml")
        self._community_patterns_path = community_patterns_path or (
            config_dir / "community-patterns.json"
        )

        # Cached patterns
        self._builtin_patterns: list[Pattern] | None = None
        self._user_patterns: list[Pattern] | None = None
        self._community_patterns: list[Pattern] | None = None

    def load_patterns(self) -> list[Pattern]:
        """
        IMPLEMENTS: S058
        INVARIANT: INV058 - Patterns are validated before loading

        Load all patterns from all sources (builtin, user, community).

        Returns:
            Combined list of validated patterns.
        """
        patterns: list[Pattern] = []

        # Load built-in patterns
        builtin = self._load_builtin_patterns()
        patterns.extend(builtin)

        # Load user patterns (if file exists)
        user = self._load_user_patterns()
        patterns.extend(user)

        # Load community patterns (if file exists and validated)
        community = self._load_community_patterns()
        patterns.extend(community)

        return patterns

    def _load_builtin_patterns(self) -> list[Pattern]:
        """
        Load built-in patterns from core.patterns module.

        Returns:
            List of builtin patterns converted to Pattern dataclass.
        """
        if self._builtin_patterns is not None:
            return self._builtin_patterns

        patterns: list[Pattern] = []

        for hp in HALLUCINATION_PATTERNS:
            # Convert HallucinationPattern to Pattern
            pattern = Pattern(
                id=hp.id,
                pattern_type=PatternType.REGEX,
                value=hp.regex.pattern,
                confidence=hp.weight,
                source=PatternSource.BUILTIN,
                description=hp.description,
                metadata={"category": hp.category.value},
            )
            patterns.append(pattern)

        self._builtin_patterns = patterns
        return patterns

    def _load_user_patterns(self) -> list[Pattern]:
        """
        INVARIANT: INV058 - Patterns validated before loading

        Load user patterns from ~/.phantom-guard/patterns.yaml.

        Returns:
            List of user patterns, empty if file doesn't exist.
        """
        if self._user_patterns is not None:
            return self._user_patterns

        if not self._user_patterns_path.exists():
            self._user_patterns = []
            return []

        try:
            with open(self._user_patterns_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None or "patterns" not in data:
                logger.debug("No patterns found in user patterns file")
                self._user_patterns = []
                return []

            patterns = self._parse_patterns_from_yaml(data["patterns"], PatternSource.USER)
            self._user_patterns = patterns
            logger.info("Loaded %d user patterns", len(patterns))
            return patterns

        except yaml.YAMLError as e:
            logger.warning("Failed to parse user patterns YAML: %s", e)
            self._user_patterns = []
            return []
        except OSError as e:
            logger.warning("Failed to read user patterns file: %s", e)
            self._user_patterns = []
            return []

    def _parse_patterns_from_yaml(
        self, patterns_data: list[dict[str, Any]], source: PatternSource
    ) -> list[Pattern]:
        """
        Parse pattern data from YAML format.

        Args:
            patterns_data: List of pattern dictionaries.
            source: Source of the patterns.

        Returns:
            List of validated Pattern objects.
        """
        patterns: list[Pattern] = []

        for item in patterns_data:
            try:
                pattern_type = self._parse_pattern_type(item.get("type", "regex"))
                pattern = Pattern(
                    id=item["id"],
                    pattern_type=pattern_type,
                    value=item.get("value", ""),
                    confidence=float(item.get("confidence", 0.5)),
                    source=source,
                    description=item.get("description", ""),
                    base_package=item.get("base"),
                    metadata=item.get("metadata", {}),
                )
                patterns.append(pattern)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Skipping invalid pattern: %s - %s", item, e)
                continue

        return patterns

    def _parse_pattern_type(self, type_str: str) -> PatternType:
        """Parse pattern type from string."""
        type_map = {
            "prefix": PatternType.PREFIX,
            "suffix": PatternType.SUFFIX,
            "compound": PatternType.COMPOUND,
            "regex": PatternType.REGEX,
        }
        return type_map.get(type_str.lower(), PatternType.REGEX)

    def _load_community_patterns(self) -> list[Pattern]:
        """
        INVARIANT: INV058 - Community patterns validated before loading

        Load community patterns from ~/.phantom-guard/community-patterns.json.

        Note: This method returns verified patterns only.
        For explicit verification result, use load_community_patterns_verified().

        Returns:
            List of community patterns, empty if file doesn't exist or invalid.
        """
        if self._community_patterns is not None:
            return self._community_patterns

        if not self._community_patterns_path.exists():
            self._community_patterns = []
            return []

        # Use verification and only return patterns if signature is valid
        result = self.load_community_patterns_verified()
        if result.success:
            self._community_patterns = result.patterns
            return result.patterns

        logger.warning("Community patterns signature verification failed: %s", result.error)
        self._community_patterns = []
        return []

    def load_community_patterns_verified(self) -> SignatureVerificationResult:
        """
        IMPLEMENTS: S058
        INVARIANT: INV058 - Patterns validated before loading

        Load community patterns with signature verification.

        Returns:
            SignatureVerificationResult with success/failure and patterns.
        """
        import json

        if not self._community_patterns_path.exists():
            return SignatureVerificationResult(success=True, patterns=[], error="")

        try:
            with open(self._community_patterns_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            return SignatureVerificationResult(
                success=False, error=f"Failed to read community patterns: {e}"
            )

        # Verify signature
        signature = data.get("signature", "")
        if not self._verify_signature(data, signature):
            return SignatureVerificationResult(success=False, error="Invalid or missing signature")

        # Parse patterns
        patterns_data = data.get("patterns", [])
        patterns = self._parse_patterns_from_yaml(patterns_data, PatternSource.COMMUNITY)

        logger.info("Loaded %d verified community patterns", len(patterns))
        return SignatureVerificationResult(success=True, patterns=patterns)

    def _verify_signature(self, data: dict[str, Any], signature: str) -> bool:
        """
        IMPLEMENTS: S058
        Verify GPG signature of community patterns.

        For now, this is a simple check that can be expanded to
        actual GPG verification in the future.

        Args:
            data: The pattern data dictionary.
            signature: The signature string.

        Returns:
            True if signature is valid, False otherwise.
        """
        # Security: Reject empty or obviously invalid signatures
        if not signature or len(signature) < 32:
            logger.warning("Community patterns have missing or short signature")
            return False

        # TODO: Implement actual GPG verification
        # For now, reject any non-empty signature as we don't have
        # the verification infrastructure yet. This is secure by default.
        # In production, this would verify against a known public key.
        logger.debug("Signature verification not yet implemented, rejecting")
        return False

    def add_user_pattern(self, pattern: Pattern) -> None:
        """
        Add a user-defined pattern.

        Args:
            pattern: Pattern to add to user patterns.

        Raises:
            ValueError: If pattern validation fails.
        """
        # INV058: Validate before adding
        # TODO: Add proper validation via patterns.validate module
        if pattern.source != PatternSource.USER:
            raise ValueError("Pattern must have USER source")

        # Clear cache to force reload
        self._user_patterns = None

        # TODO: Persist to user patterns file
        logger.info("Added user pattern: %s", pattern.id)

    async def check_for_updates(self) -> bool:
        """
        INVARIANT: INV058a - Update requires user consent

        Check if community pattern updates are available.

        Returns:
            True if updates are available.
        """
        # TODO: Implement GitHub release check
        # For now, return False (no updates)
        return False

    async def download_community_patterns(self, consent: bool = False) -> None:
        """
        INVARIANT: INV058a - Requires explicit user consent

        Download latest community patterns from GitHub.

        Args:
            consent: User has consented to download.

        Raises:
            PermissionError: If consent is False.
        """
        if not consent:
            raise PermissionError("User consent required to download community patterns (INV058a)")

        # TODO: Implement GitHub download with signature verification
        logger.info("Downloading community patterns (not yet implemented)")
