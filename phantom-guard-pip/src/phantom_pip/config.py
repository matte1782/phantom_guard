"""
Configuration system for phantom-pip.

IMPLEMENTS: S204
INVARIANTS: INV207 (parse errors handled gracefully)
TESTS: T204.*
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class Config:
    """phantom-pip configuration."""

    enabled: bool = True
    mode: str = "interactive"  # interactive | warn | block | silent
    auto_approve: bool = False
    allowlist: list[str] = field(default_factory=list)
    blocklist: list[str] = field(default_factory=list)
    threshold: float = 0.6
    timeout: int = 30
    registry: str = "pypi"

    def __post_init__(self) -> None:
        """Validate configuration values."""
        valid_modes = {"interactive", "warn", "block", "silent"}
        if self.mode not in valid_modes:
            self.mode = "interactive"

        if not 0.0 <= self.threshold <= 1.0:
            self.threshold = 0.6

        if self.timeout < 1:
            self.timeout = 30


def get_config_dir() -> Path:
    """Get configuration directory path."""
    # Check XDG_CONFIG_HOME first (Linux)
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "phantom-guard"

    # Check APPDATA (Windows)
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "phantom-guard"

    # Default to ~/.phantom-guard
    return Path.home() / ".phantom-guard"


def get_config_path() -> Path:
    """Get configuration file path."""
    return get_config_dir() / "pip.yaml"


def _parse_config_dict(data: dict[str, Any]) -> Config:
    """
    Parse configuration dictionary into Config object.

    INV207: Invalid values replaced with defaults.
    """
    return Config(
        enabled=bool(data.get("enabled", True)),
        mode=str(data.get("mode", "interactive")),
        auto_approve=bool(data.get("auto_approve", False)),
        allowlist=list(data.get("allowlist", [])),
        blocklist=list(data.get("blocklist", [])),
        threshold=float(data.get("threshold", 0.6)),
        timeout=int(data.get("timeout", 30)),
        registry=str(data.get("registry", "pypi")),
    )


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from file.

    INV207: Returns default config on parse error.

    Args:
        config_path: Optional custom config path

    Returns:
        Config object (defaults if file missing/invalid)
    """
    path = config_path or get_config_path()

    if not path.exists():
        return Config()

    try:
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        if data is None:
            return Config()

        if not isinstance(data, dict):
            # INV207: Invalid format, return defaults
            return Config()

        return _parse_config_dict(data)

    except yaml.YAMLError:
        # INV207: Parse error, return defaults
        return Config()
    except OSError:
        # INV207: Read error, return defaults
        return Config()


def save_config(config: Config, config_path: Optional[Path] = None) -> None:
    """
    Save configuration to file.

    Creates parent directory if needed.
    """
    path = config_path or get_config_path()

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "enabled": config.enabled,
        "mode": config.mode,
        "auto_approve": config.auto_approve,
        "allowlist": config.allowlist,
        "blocklist": config.blocklist,
        "threshold": config.threshold,
        "timeout": config.timeout,
        "registry": config.registry,
    }

    content = yaml.dump(data, default_flow_style=False, sort_keys=False)
    path.write_text(content, encoding="utf-8")


def create_default_config(config_path: Optional[Path] = None) -> Path:
    """
    Create default configuration file with comments.

    Returns path to created file.
    """
    path = config_path or get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    content = """\
# Phantom Guard pip Wrapper Configuration
# See: https://github.com/matte1782/phantom_guard

# Enable/disable validation
enabled: true

# Mode: interactive | warn | block | silent
#   interactive: Prompt for risky packages (default)
#   warn: Show warnings but don't block
#   block: Block all risky packages
#   silent: Log only, no output
mode: interactive

# Auto-approve all packages (like --yes flag)
auto_approve: false

# Packages to always allow (skip validation)
allowlist:
  # - my-internal-package
  # - company-utils

# Packages to always block
blocklist:
  # - known-malware-package

# Risk score threshold (0.0 - 1.0)
# Packages scoring above this are flagged
threshold: 0.6

# Validation timeout in seconds
timeout: 30

# Default registry (pypi | npm | crates)
registry: pypi
"""

    path.write_text(content, encoding="utf-8")
    return path


def merge_cli_options(config: Config, **cli_options: Any) -> Config:
    """
    Merge CLI options into config (CLI takes precedence).

    Args:
        config: Base configuration
        **cli_options: CLI options to override

    Returns:
        New Config with CLI overrides applied
    """
    # SECURITY: Validate threshold from CLI options
    threshold = cli_options.get("threshold")
    if threshold is not None:
        # Clamp to valid range [0.0, 1.0]
        threshold = max(0.0, min(1.0, float(threshold)))
    else:
        threshold = config.threshold

    # Create copy with overrides
    return Config(
        enabled=cli_options.get("enabled", config.enabled),
        mode=cli_options.get("mode") or config.mode,
        auto_approve=cli_options.get("auto_approve", cli_options.get("yes", config.auto_approve)),
        allowlist=cli_options.get("allowlist", config.allowlist),
        blocklist=cli_options.get("blocklist", config.blocklist),
        threshold=threshold,
        timeout=cli_options.get("timeout", config.timeout),
        registry=cli_options.get("registry", config.registry),
    )
