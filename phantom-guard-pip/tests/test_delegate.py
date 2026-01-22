"""
Tests for pip subprocess delegation.

SPEC: S206
TESTS: T206.01-T206.08
SECURITY: CRITICAL
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from phantom_pip.delegate import (
    delegate_to_pip,
    delegate_to_pip_capture,
    find_pip_executable,
    _validate_args_security,
    _security_audit_shell_false,
)
from phantom_pip.errors import DelegationError, SecurityError


class TestT206_Delegation:
    """T206: pip delegation tests."""

    def test_T206_01_find_pip(self) -> None:
        """T206.01: find_pip_executable returns valid path."""
        pip_path = find_pip_executable()
        assert pip_path is not None
        assert "pip" in pip_path.lower()

    @patch("subprocess.run")
    def test_T206_02_shell_false(self, mock_run: MagicMock) -> None:
        """T206.02: INV205 - subprocess uses shell=False."""
        mock_run.return_value = MagicMock(returncode=0)
        delegate_to_pip(["--version"], pip_path="pip")

        # Verify shell=False was passed
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get("shell") is False

    @patch("subprocess.run")
    def test_T206_03_returns_exit_code(self, mock_run: MagicMock) -> None:
        """T206.03: INV208 - Returns pip's exit code."""
        mock_run.return_value = MagicMock(returncode=42)
        result = delegate_to_pip(["install", "nonexistent-xyz"], pip_path="pip")
        assert result == 42

    @patch("subprocess.run")
    def test_T206_04_list_args_not_string(self, mock_run: MagicMock) -> None:
        """T206.04: Command is list, not string."""
        mock_run.return_value = MagicMock(returncode=0)
        delegate_to_pip(["install", "flask"], pip_path="pip")

        call_args = mock_run.call_args[0][0]
        assert isinstance(call_args, list)
        assert call_args[0] == "pip"
        assert call_args[1] == "install"
        assert call_args[2] == "flask"

    def test_T206_05_security_audit_passes(self) -> None:
        """T206.05: Security audit confirms shell=False."""
        assert _security_audit_shell_false() is True


class TestT206_Security:
    """T206: Security tests for delegation."""

    def test_T206_S01_reject_semicolon(self) -> None:
        """T206.S01: Reject arguments with semicolon."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask; rm -rf /"])

    def test_T206_S02_reject_pipe(self) -> None:
        """T206.S02: Reject arguments with pipe."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask | cat /etc/passwd"])

    def test_T206_S03_reject_backtick(self) -> None:
        """T206.S03: Reject arguments with backticks."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask`whoami`"])

    def test_T206_S04_allow_version_specifiers(self) -> None:
        """T206.S04: Allow < > = in version specifiers."""
        # Should not raise
        _validate_args_security(["install", "flask>=2.0"])
        _validate_args_security(["install", "flask<3.0"])
        _validate_args_security(["install", "flask==2.0.0"])

    def test_T206_S05_reject_dollar(self) -> None:
        """T206.S05: Reject arguments with $."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask$HOME"])

    def test_T206_S06_allow_flags(self) -> None:
        """T206.S06: Allow pip flags."""
        # Should not raise
        _validate_args_security(["install", "--upgrade", "flask"])
        _validate_args_security(["install", "-r", "requirements.txt"])


class TestT206_ErrorHandling:
    """T206: Error handling tests."""

    @patch("subprocess.run")
    def test_T206_E01_file_not_found(self, mock_run: MagicMock) -> None:
        """T206.E01: Handle missing pip executable."""
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(DelegationError) as exc_info:
            delegate_to_pip(["--version"], pip_path="/nonexistent/pip")
        assert "not found" in str(exc_info.value).lower()

    @patch("subprocess.run")
    def test_T206_E02_permission_denied(self, mock_run: MagicMock) -> None:
        """T206.E02: Handle permission denied."""
        mock_run.side_effect = PermissionError()
        with pytest.raises(DelegationError) as exc_info:
            delegate_to_pip(["--version"], pip_path="pip")
        assert "permission" in str(exc_info.value).lower()

    @patch("subprocess.run")
    def test_T206_E03_timeout(self, mock_run: MagicMock) -> None:
        """T206.E03: Handle timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("pip", 30)
        with pytest.raises(DelegationError) as exc_info:
            delegate_to_pip_capture(["install", "flask"], pip_path="pip", timeout=30)
        assert "timeout" in str(exc_info.value).lower()

    @patch("subprocess.run")
    def test_T206_E04_subprocess_error(self, mock_run: MagicMock) -> None:
        """T206.E04: Handle generic subprocess error (line 116-117)."""
        mock_run.side_effect = subprocess.SubprocessError("Generic subprocess failure")
        with pytest.raises(DelegationError) as exc_info:
            delegate_to_pip(["--version"], pip_path="pip")
        assert "subprocess error" in str(exc_info.value).lower()

    @patch("subprocess.run")
    def test_T206_E05_capture_file_not_found(self, mock_run: MagicMock) -> None:
        """T206.E05: Handle missing pip in delegate_to_pip_capture (line 159-160)."""
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(DelegationError) as exc_info:
            delegate_to_pip_capture(["--version"], pip_path="/nonexistent/pip")
        assert "not found" in str(exc_info.value).lower()


class TestT206_FindPipEdgeCases:
    """T206.F: Edge cases for find_pip_executable."""

    @patch("pathlib.Path.exists")
    @patch("shutil.which")
    def test_T206_F01_fallback_to_which(
        self, mock_which: MagicMock, mock_exists: MagicMock
    ) -> None:
        """T206.F01: Falls back to shutil.which when pip not in python dir (line 42-44)."""
        # Simulate pip not found in python directory or Scripts
        mock_exists.return_value = False
        mock_which.return_value = "/usr/bin/pip"

        result = find_pip_executable()
        assert result == "/usr/bin/pip"
        # Verify shutil.which was called
        assert mock_which.called

    @patch("pathlib.Path.exists")
    @patch("shutil.which")
    def test_T206_F02_which_pip3_fallback(
        self, mock_which: MagicMock, mock_exists: MagicMock
    ) -> None:
        """T206.F02: Falls back to pip3 if pip not found (line 42)."""
        mock_exists.return_value = False
        # pip not found, but pip3 is
        mock_which.side_effect = lambda name: "/usr/bin/pip3" if name == "pip3" else None

        result = find_pip_executable()
        assert result == "/usr/bin/pip3"

    @patch("pathlib.Path.exists")
    @patch("shutil.which")
    def test_T206_F03_pip_not_found_raises(
        self, mock_which: MagicMock, mock_exists: MagicMock
    ) -> None:
        """T206.F03: Raises DelegationError when pip not found anywhere (line 46)."""
        mock_exists.return_value = False
        mock_which.return_value = None

        with pytest.raises(DelegationError) as exc_info:
            find_pip_executable()
        assert "could not find pip" in str(exc_info.value).lower()

    @patch("pathlib.Path.exists")
    def test_T206_F04_finds_pip_in_python_dir(self, mock_exists: MagicMock) -> None:
        """T206.F04: Finds pip in same directory as Python (line 34)."""
        # Return True for the first pip found
        call_count = [0]

        def exists_side_effect() -> bool:
            call_count[0] += 1
            # Return True on first check (pip in python dir)
            return call_count[0] == 1

        mock_exists.side_effect = exists_side_effect

        result = find_pip_executable()
        assert "pip" in result.lower()


class TestT206_CaptureSuccess:
    """T206.C: Tests for delegate_to_pip_capture success path."""

    @patch("subprocess.run")
    def test_T206_C01_capture_returns_tuple(self, mock_run: MagicMock) -> None:
        """T206.C01: delegate_to_pip_capture returns (code, stdout, stderr) (line 155)."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "pip 23.0.1"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        code, stdout, stderr = delegate_to_pip_capture(["--version"], pip_path="pip")

        assert code == 0
        assert stdout == "pip 23.0.1"
        assert stderr == ""

    @patch("subprocess.run")
    def test_T206_C02_capture_with_nonzero_exit(self, mock_run: MagicMock) -> None:
        """T206.C02: delegate_to_pip_capture preserves non-zero exit code."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: package not found"
        mock_run.return_value = mock_result

        code, stdout, stderr = delegate_to_pip_capture(
            ["install", "nonexistent"], pip_path="pip"
        )

        assert code == 1
        assert stderr == "Error: package not found"

    @patch("subprocess.run")
    def test_T206_C03_capture_shell_false(self, mock_run: MagicMock) -> None:
        """T206.C03: delegate_to_pip_capture uses shell=False."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        delegate_to_pip_capture(["--version"], pip_path="pip")

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get("shell") is False

    @patch("subprocess.run")
    def test_T206_C04_capture_text_mode(self, mock_run: MagicMock) -> None:
        """T206.C04: delegate_to_pip_capture uses text mode."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        delegate_to_pip_capture(["--version"], pip_path="pip")

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get("text") is True
        assert call_kwargs.get("capture_output") is True


class TestT206_SecurityEdgeCases:
    """T206.SE: Additional security validation edge cases."""

    def test_T206_SE01_reject_newline(self) -> None:
        """T206.SE01: Reject arguments with newlines."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask\nrm -rf /"])

    def test_T206_SE02_reject_carriage_return(self) -> None:
        """T206.SE02: Reject arguments with carriage return."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask\rrm -rf /"])

    def test_T206_SE03_reject_null_byte(self) -> None:
        """T206.SE03: Reject arguments with null bytes."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask\x00malicious"])

    def test_T206_SE04_reject_ampersand(self) -> None:
        """T206.SE04: Reject arguments with ampersand."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask & rm -rf /"])

    def test_T206_SE05_reject_parentheses(self) -> None:
        """T206.SE05: Reject arguments with parentheses."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask$(whoami)"])

    def test_T206_SE06_reject_quotes(self) -> None:
        """T206.SE06: Reject arguments with quotes."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask'test'"])
        with pytest.raises(SecurityError):
            _validate_args_security(["install", 'flask"test"'])

    def test_T206_SE07_reject_backslash(self) -> None:
        """T206.SE07: Reject arguments with backslash."""
        with pytest.raises(SecurityError):
            _validate_args_security(["install", "flask\\test"])

    def test_T206_SE08_allow_safe_packages(self) -> None:
        """T206.SE08: Allow typical safe package names."""
        # Should not raise
        _validate_args_security(["install", "flask"])
        _validate_args_security(["install", "django-rest-framework"])
        _validate_args_security(["install", "python_dateutil"])
        _validate_args_security(["install", "numpy123"])
