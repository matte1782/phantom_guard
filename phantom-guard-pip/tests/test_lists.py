"""
Tests for allowlist/blocklist management.

SPEC: S205
TESTS: T205.01-T205.08
"""

import pytest
from phantom_pip.lists import (
    is_allowed,
    is_blocked,
    get_list_status,
    filter_packages_by_lists,
    normalize_package_name,
    add_to_list,
    remove_from_list,
)


class TestT205_Lists:
    """T205: Allowlist/blocklist tests."""

    def test_T205_01_allowlist_exact_match(self) -> None:
        """T205.01: INV202 - Exact match returns True."""
        assert is_allowed("flask", ["flask"]) is True
        assert is_allowed("django", ["flask"]) is False

    def test_T205_02_blocklist_exact_match(self) -> None:
        """T205.02: INV203 - Exact match returns True."""
        assert is_blocked("malware", ["malware"]) is True
        assert is_blocked("flask", ["malware"]) is False

    def test_T205_03_wildcard_patterns(self) -> None:
        """T205.03: Wildcard patterns work."""
        assert is_allowed("flask-login", ["flask-*"]) is True
        assert is_allowed("flask-wtf", ["flask-*"]) is True
        assert is_allowed("django", ["flask-*"]) is False

    def test_T205_04_case_insensitive(self) -> None:
        """T205.04: Matching is case-insensitive."""
        assert is_allowed("Flask", ["flask"]) is True
        assert is_allowed("FLASK", ["flask"]) is True
        assert is_blocked("MALWARE", ["malware"]) is True

    def test_T205_05_hyphen_underscore_equivalent(self) -> None:
        """T205.05: Hyphens and underscores are equivalent."""
        assert is_allowed("flask_login", ["flask-login"]) is True
        assert is_allowed("flask-login", ["flask_login"]) is True

    def test_T205_06_allowlist_precedence(self) -> None:
        """T205.06: Allowlist takes precedence over blocklist."""
        status = get_list_status(
            "my-package",
            allowlist=["my-package"],
            blocklist=["my-package"],
        )
        assert status == "allowed"

    def test_T205_07_filter_packages(self) -> None:
        """T205.07: filter_packages_by_lists categorizes correctly."""
        packages = ["flask", "malware", "requests", "company-internal"]
        allowed, blocked, to_validate = filter_packages_by_lists(
            packages,
            allowlist=["company-internal"],
            blocklist=["malware"],
        )
        assert "company-internal" in allowed
        assert "malware" in blocked
        assert "flask" in to_validate
        assert "requests" in to_validate

    def test_T205_08_empty_lists(self) -> None:
        """T205.08: Empty lists return False."""
        assert is_allowed("flask", []) is False
        assert is_blocked("flask", []) is False


class TestT205_Normalization:
    """T205: Package name normalization tests."""

    def test_T205_N01_basic_normalization(self) -> None:
        """T205.N01: Basic normalization."""
        assert normalize_package_name("Flask") == "flask"
        assert normalize_package_name("DJANGO") == "django"

    def test_T205_N02_hyphen_underscore(self) -> None:
        """T205.N02: Hyphens and underscores normalized."""
        assert normalize_package_name("flask-login") == "flask-login"
        assert normalize_package_name("flask_login") == "flask-login"
        assert normalize_package_name("flask__login") == "flask-login"

    def test_T205_N03_consecutive_separators(self) -> None:
        """T205.N03: Consecutive separators collapsed."""
        assert normalize_package_name("my--package") == "my-package"
        assert normalize_package_name("my__package") == "my-package"


class TestT205_ListManagement:
    """T205: List management operations."""

    def test_T205_M01_add_to_list(self) -> None:
        """T205.M01: Add package to list."""
        original = ["flask"]
        updated = add_to_list("django", original)
        assert "django" in updated
        assert original == ["flask"]  # Immutable

    def test_T205_M02_add_duplicate(self) -> None:
        """T205.M02: Adding duplicate doesn't create duplicate."""
        original = ["flask"]
        updated = add_to_list("flask", original)
        assert updated.count("flask") == 1

    def test_T205_M03_remove_from_list(self) -> None:
        """T205.M03: Remove package from list."""
        original = ["flask", "django"]
        updated = remove_from_list("flask", original)
        assert "flask" not in updated
        assert "django" in updated

    def test_T205_M04_suffix_wildcard(self) -> None:
        """T205.M04: Suffix wildcard matching."""
        assert is_allowed("django-utils", ["*-utils"]) is True
        assert is_allowed("flask-utils", ["*-utils"]) is True
        assert is_allowed("flask", ["*-utils"]) is False

    def test_T205_M05_question_mark_wildcard(self) -> None:
        """T205.M05: Question mark wildcard."""
        assert is_allowed("flask1", ["flask?"]) is True
        assert is_allowed("flask12", ["flask?"]) is False
