"""
Pytest configuration and fixtures for phantom-pip tests.

IMPLEMENTS: S207, S208
"""

import sys
from pathlib import Path

# Add src to sys.path for tests to import phantom_pip
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest
from unittest.mock import MagicMock
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MockPackageRisk:
    """Mock PackageRisk for testing - properly typed."""

    risk_level: str = "SAFE"
    risk_score: float = 0.1
    signals: list[str] = field(default_factory=list)
    recommendation: Optional[str] = None


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Create temporary config directory."""
    config_dir = tmp_path / ".phantom-guard"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def sample_config(temp_config_dir: Path) -> Path:
    """Create sample configuration file."""
    config_file = temp_config_dir / "pip.yaml"
    config_file.write_text("""
enabled: true
mode: interactive
auto_approve: false
allowlist:
  - my-internal-package
blocklist:
  - known-malware
threshold: 0.6
timeout: 30
""")
    return config_file


@pytest.fixture
def mock_pip() -> MagicMock:
    """Mock pip subprocess."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = b""
    mock.stderr = b""
    return mock


@pytest.fixture
def mock_phantom_guard() -> MagicMock:
    """Mock phantom-guard validation."""
    mock = MagicMock()
    return mock


@pytest.fixture
def safe_risk() -> MockPackageRisk:
    """Create a SAFE risk result."""
    return MockPackageRisk(
        risk_level="SAFE",
        risk_score=0.1,
        signals=[],
        recommendation=None,
    )


@pytest.fixture
def high_risk() -> MockPackageRisk:
    """Create a HIGH_RISK result."""
    return MockPackageRisk(
        risk_level="HIGH_RISK",
        risk_score=0.95,
        signals=["Package not found", "Matches hallucination pattern"],
        recommendation="DO NOT INSTALL",
    )


@pytest.fixture
def suspicious_risk() -> MockPackageRisk:
    """Create a SUSPICIOUS risk result."""
    return MockPackageRisk(
        risk_level="SUSPICIOUS",
        risk_score=0.6,
        signals=["Low download count"],
        recommendation="REVIEW",
    )
