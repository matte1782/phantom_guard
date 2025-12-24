# Phantom Guard

Detect AI-hallucinated package attacks (slopsquatting).

## Installation

```bash
pip install phantom-guard
```

## Usage

```bash
# Validate a single package
phantom-guard validate flask

# Check a requirements file
phantom-guard check requirements.txt
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/
```

## License

MIT
