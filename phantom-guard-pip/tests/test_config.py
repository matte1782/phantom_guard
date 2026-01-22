"""
Tests for configuration system.

SPEC: S204
TESTS: T204.01-T204.10
"""

import pytest
from pathlib import Path
from phantom_pip.config import (
    Config,
    load_config,
    save_config,
    create_default_config,
    merge_cli_options,
    get_config_path,
)


class TestT204_Config:
    """T204: Configuration tests."""

    def test_T204_01_default_values(self) -> None:
        """T204.01: Config has sensible defaults."""
        config = Config()
        assert config.enabled is True
        assert config.mode == "interactive"
        assert config.auto_approve is False
        assert config.threshold == 0.6
        assert config.timeout == 30

    def test_T204_02_load_missing_file(self, tmp_path: Path) -> None:
        """T204.02: INV207 - Missing file returns defaults."""
        config = load_config(tmp_path / "nonexistent.yaml")
        assert config.enabled is True
        assert config.mode == "interactive"

    def test_T204_03_load_valid_file(self, tmp_path: Path) -> None:
        """T204.03: Load valid configuration file."""
        config_file = tmp_path / "pip.yaml"
        config_file.write_text("""
enabled: true
mode: block
auto_approve: true
threshold: 0.8
allowlist:
  - my-package
blocklist:
  - bad-package
""")
        config = load_config(config_file)
        assert config.mode == "block"
        assert config.auto_approve is True
        assert config.threshold == 0.8
        assert "my-package" in config.allowlist
        assert "bad-package" in config.blocklist

    def test_T204_04_invalid_yaml(self, tmp_path: Path) -> None:
        """T204.04: INV207 - Invalid YAML returns defaults."""
        config_file = tmp_path / "pip.yaml"
        config_file.write_text("this: is: not: valid: yaml: [[[[")
        config = load_config(config_file)
        # Should return defaults, not crash
        assert config.enabled is True
        assert config.mode == "interactive"

    def test_T204_05_invalid_values_normalized(self, tmp_path: Path) -> None:
        """T204.05: INV207 - Invalid values normalized to defaults."""
        config_file = tmp_path / "pip.yaml"
        config_file.write_text("""
mode: invalid_mode
threshold: 999
timeout: -5
""")
        config = load_config(config_file)
        # Invalid values should be normalized
        assert config.mode == "interactive"  # normalized
        assert config.threshold == 0.6  # normalized
        assert config.timeout == 30  # normalized

    def test_T204_06_save_and_load(self, tmp_path: Path) -> None:
        """T204.06: Save and reload config."""
        config_file = tmp_path / "pip.yaml"
        original = Config(
            enabled=False,
            mode="warn",
            threshold=0.9,
            allowlist=["pkg1", "pkg2"],
        )
        save_config(original, config_file)

        loaded = load_config(config_file)
        assert loaded.enabled is False
        assert loaded.mode == "warn"
        assert loaded.threshold == 0.9
        assert loaded.allowlist == ["pkg1", "pkg2"]

    def test_T204_07_create_default(self, tmp_path: Path) -> None:
        """T204.07: Create default config with comments."""
        config_file = tmp_path / "pip.yaml"
        path = create_default_config(config_file)
        assert path.exists()
        content = path.read_text()
        assert "enabled:" in content
        assert "mode:" in content
        assert "#" in content  # Has comments

    def test_T204_08_merge_cli_options(self) -> None:
        """T204.08: CLI options override config."""
        config = Config(mode="interactive", auto_approve=False)
        merged = merge_cli_options(config, yes=True, mode="block")
        assert merged.auto_approve is True  # from yes
        assert merged.mode == "block"  # overridden
        assert merged.threshold == 0.6  # unchanged

    def test_T204_09_empty_file(self, tmp_path: Path) -> None:
        """T204.09: Empty file returns defaults."""
        config_file = tmp_path / "pip.yaml"
        config_file.write_text("")
        config = load_config(config_file)
        assert config.enabled is True

    def test_T204_10_creates_parent_dirs(self, tmp_path: Path) -> None:
        """T204.10: save_config creates parent directories."""
        config_file = tmp_path / "deep" / "nested" / "pip.yaml"
        save_config(Config(), config_file)
        assert config_file.exists()

    def test_T204_11_non_dict_config(self, tmp_path: Path) -> None:
        """T204.11: INV207 - Non-dict YAML returns defaults."""
        config_file = tmp_path / "pip.yaml"
        config_file.write_text("just a string")
        config = load_config(config_file)
        assert config.enabled is True
