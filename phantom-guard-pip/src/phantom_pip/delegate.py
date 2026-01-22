"""
pip subprocess delegation.

IMPLEMENTS: S206
INVARIANTS: INV205 (never shell=True), INV208 (preserve exit code)
TESTS: T206.*
SECURITY: CRITICAL - subprocess handling

SECURITY REVIEW REQUIRED BEFORE MERGE
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from phantom_pip.errors import DelegationError, SecurityError


def find_pip_executable() -> str:
    """
    Find the pip executable path.

    Returns pip from the same environment as Python.
    """
    # Try pip in same directory as Python
    python_dir = Path(sys.executable).parent

    # Check for pip in Scripts (Windows) or bin (Unix)
    for name in ["pip", "pip3", "pip.exe", "pip3.exe"]:
        pip_path = python_dir / name
        if pip_path.exists():
            return str(pip_path)

        # Check Scripts subdirectory (Windows venv)
        scripts_path = python_dir / "Scripts" / name
        if scripts_path.exists():
            return str(scripts_path)

    # Fallback to shutil.which
    which_pip = shutil.which("pip") or shutil.which("pip3")
    if which_pip:
        return which_pip

    raise DelegationError("Could not find pip executable")


def _validate_args_security(args: list[str]) -> None:
    """
    SECURITY: Validate arguments before subprocess call.

    INV205: Prevents shell injection via argument validation.

    Raises SecurityError if dangerous patterns detected.
    """
    # Check for shell metacharacters in any argument
    # SECURITY: Include newlines (\n\r) and null bytes to prevent injection
    shell_specific = set(";|&$`\\\"'()\n\r\x00")

    for arg in args:
        # Skip known safe options
        if arg.startswith("-"):
            continue

        # Check for dangerous characters
        if any(c in arg for c in shell_specific):
            raise SecurityError(
                f"Potentially dangerous characters in argument: {arg!r}"
            )


def delegate_to_pip(args: list[str], pip_path: Optional[str] = None) -> int:
    """
    Delegate to real pip with original arguments.

    INV205: Uses subprocess with shell=False (array args).
    INV208: Returns pip's exit code.

    SECURITY: NEVER uses shell=True.

    Args:
        args: pip arguments (e.g., ['install', 'flask'])
        pip_path: Optional custom pip path

    Returns:
        pip's exit code
    """
    # SECURITY: Validate arguments
    _validate_args_security(args)

    # Find pip executable
    pip = pip_path or find_pip_executable()

    # Build command as LIST (not string!)
    # SECURITY: shell=False ensures no shell interpretation
    cmd = [pip] + args

    try:
        # SECURITY CRITICAL: shell=False is MANDATORY
        # Never change this to shell=True
        result = subprocess.run(
            cmd,
            shell=False,  # SECURITY: MUST be False
            check=False,  # Don't raise on non-zero exit
            # Inherit stdin/stdout/stderr for interactive pip
        )

        # INV208: Return pip's exit code
        return result.returncode

    except FileNotFoundError as e:
        raise DelegationError(f"pip executable not found: {pip}") from e
    except PermissionError as e:
        raise DelegationError(f"Permission denied executing pip: {pip}") from e
    except subprocess.SubprocessError as e:
        raise DelegationError(f"Subprocess error: {e}") from e


def delegate_to_pip_capture(
    args: list[str],
    pip_path: Optional[str] = None,
    timeout: Optional[int] = None,
) -> tuple[int, str, str]:
    """
    Delegate to pip and capture output.

    For non-interactive operations where output capture is needed.

    Args:
        args: pip arguments
        pip_path: Optional custom pip path
        timeout: Optional timeout in seconds

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    # SECURITY: Validate arguments
    _validate_args_security(args)

    pip = pip_path or find_pip_executable()
    cmd = [pip] + args

    try:
        # SECURITY CRITICAL: shell=False
        result = subprocess.run(
            cmd,
            shell=False,  # SECURITY: MUST be False
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired as e:
        raise DelegationError(f"pip timeout after {timeout}s") from e
    except FileNotFoundError as e:
        raise DelegationError(f"pip executable not found: {pip}") from e


# SECURITY: Test that shell=False is enforced
def _security_audit_shell_false() -> bool:
    """
    Security audit: Verify shell=False is used in subprocess calls.

    This function exists for automated security scanning.
    Returns True if code passes audit.
    """
    import ast
    import inspect

    source = inspect.getsource(delegate_to_pip)
    tree = ast.parse(source)

    # Find all subprocess.run calls and verify shell=False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for shell keyword argument
            for keyword in node.keywords:
                if keyword.arg == "shell":
                    # Must be shell=False
                    if isinstance(keyword.value, ast.Constant):
                        if keyword.value.value is True:
                            return False  # FAIL: shell=True found!

    # Also check that shell=False appears (explicit is better than implicit)
    return "shell=False" in source
