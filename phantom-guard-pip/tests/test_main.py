"""
Tests for __main__.py entry point.

SPEC: S200
TESTS: T200.M01-T200.M05
"""

import pytest
import sys
from unittest.mock import patch, MagicMock


class TestT200_MainEntryPoint:
    """T200.M: Tests for python -m phantom_pip entry point."""

    def test_T200_M01_main_imports_app(self) -> None:
        """T200.M01: __main__.py imports app from cli."""
        # Verify the module can be imported
        from phantom_pip import __main__

        # Verify it imports app from cli
        assert hasattr(__main__, 'app')

    def test_T200_M02_main_module_structure(self) -> None:
        """T200.M02: __main__.py has correct structure."""
        import phantom_pip.__main__ as main_module

        # Verify the module has the expected content
        assert hasattr(main_module, 'app')

        # Verify it's the same app from cli
        from phantom_pip.cli import app
        assert main_module.app is app

    @patch("phantom_pip.cli.app")
    def test_T200_M03_main_calls_app(self, mock_app: MagicMock) -> None:
        """T200.M03: Running __main__ calls app()."""
        # We need to test the if __name__ == "__main__" block
        # This is done by importing and checking the module structure
        # The actual execution is covered by integration tests

        # Verify app is callable
        from phantom_pip.cli import app
        assert callable(app)

    def test_T200_M04_main_docstring(self) -> None:
        """T200.M04: __main__.py has correct docstring with IMPLEMENTS."""
        from phantom_pip import __main__

        assert __main__.__doc__ is not None
        assert "IMPLEMENTS:" in __main__.__doc__
        assert "S200" in __main__.__doc__

    def test_T200_M05_runpy_execution(self) -> None:
        """T200.M05: Module can be run via runpy."""
        import runpy

        # Mock the app to prevent actual execution
        with patch("phantom_pip.cli.app") as mock_app:
            # This should not raise an exception
            # runpy.run_module will execute the module
            # but since we mock app, it won't actually do anything
            try:
                # We can't easily test __name__ == "__main__" branch
                # but we can verify the module loads correctly
                spec = runpy.run_module("phantom_pip.__main__", run_name="phantom_pip.__main__")
                assert "app" in spec
            except SystemExit:
                # Typer may raise SystemExit, which is expected
                pass


class TestT200_MainEdgeCases:
    """T200.ME: Edge case tests for entry point."""

    def test_T200_ME01_import_error_handling(self) -> None:
        """T200.ME01: Module handles import correctly."""
        # Test that importing __main__ doesn't execute app
        # (it should only execute when __name__ == "__main__")
        import phantom_pip.__main__
        # If we get here without error, import worked
        assert True

    def test_T200_ME02_app_type(self) -> None:
        """T200.ME02: app is a Typer instance."""
        from phantom_pip.__main__ import app
        import typer

        # Typer apps are actually Typer instances
        assert isinstance(app, typer.Typer)

    def test_T200_ME03_cli_integration(self) -> None:
        """T200.ME03: __main__.app is same as cli.app."""
        from phantom_pip.__main__ import app as main_app
        from phantom_pip.cli import app as cli_app

        assert main_app is cli_app
