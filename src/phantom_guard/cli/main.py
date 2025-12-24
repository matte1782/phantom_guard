"""
IMPLEMENTS: S010-S019
Command-line interface for Phantom Guard.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="phantom-guard",
    help="Detect AI-hallucinated package attacks (slopsquatting)",
    add_completion=False,
)


@app.command()
def validate(
    package: str = typer.Argument(..., help="Package name to validate"),
    registry: str = typer.Option("pypi", "--registry", "-r", help="Package registry"),
) -> None:
    """Validate a single package for slopsquatting risk."""
    # Stub - will be implemented in W3.1
    typer.echo(f"Validating {package} on {registry}...")


@app.command()
def check(
    file: str = typer.Argument(..., help="Requirements file to check"),
) -> None:
    """Check all packages in a requirements file."""
    # Stub - will be implemented in W3.2
    typer.echo(f"Checking packages in {file}...")


if __name__ == "__main__":
    app()
