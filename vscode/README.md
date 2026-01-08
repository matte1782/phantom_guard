# Phantom Guard for VS Code

Detect AI-hallucinated package attacks (slopsquatting) directly in your editor.

## Features

- **Real-time Validation** - Validates packages as you edit dependency files
- **Inline Diagnostics** - Shows warnings directly in the editor with risk scores
- **Hover Information** - Hover over package names to see detailed risk analysis
- **Quick Fixes** - One-click actions to ignore packages or view details
- **Status Bar** - Shows validation status at a glance

## Supported Files

- `requirements.txt` (Python/PyPI)
- `package.json` (JavaScript/npm)
- `pyproject.toml` (Python/PyPI)
- `Cargo.toml` (Rust/crates.io)

## Requirements

- Python 3.11+ with `phantom-guard` installed:
  ```bash
  pip install phantom-guard
  ```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `phantomGuard.enabled` | `true` | Enable/disable validation |
| `phantomGuard.pythonPath` | auto | Path to Python with phantom-guard |
| `phantomGuard.threshold` | `0.5` | Risk score threshold (0.0-1.0) |
| `phantomGuard.ignoredPackages` | `[]` | Packages to skip |

## Detection Signals

Phantom Guard analyzes 15 risk signals including:

- Package not found on registry
- AI hallucination patterns
- Typosquatting detection
- Namespace squatting (e.g., fake `aws-`, `google-` packages)
- Suspicious download patterns
- Recent ownership transfers
- Rapid version releases

## Links

- [PyPI Package](https://pypi.org/project/phantom-guard/)
- [GitHub Repository](https://github.com/matte1782/phantom_guard)
- [Interactive Demo](https://matte1782.github.io/phantom_guard/)

## License

MIT License - See [LICENSE](LICENSE) for details.
