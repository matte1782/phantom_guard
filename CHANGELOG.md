# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- GitHub Actions integration
- Pre-commit hook support
- SBOM generation
- Custom pattern configuration
- VS Code extension

## [0.1.0] - 2024-12-30

### Added

#### Core Detection Engine
- Package validation with multi-signal risk assessment
- Pattern matching for AI-hallucinated package names (10 patterns)
- Typosquat detection against top 3000 popular packages
- Configurable risk scoring with SAFE/SUSPICIOUS/HIGH_RISK thresholds

#### Registry Support
- PyPI client with JSON API integration
- npm registry client with scoped package support
- crates.io client with proper User-Agent handling
- Two-tier caching (memory LRU + SQLite persistence)
- Retry logic with exponential backoff

#### CLI Interface
- `phantom-guard validate <package>` - Check single package
- `phantom-guard check <file>` - Batch validate from manifest files
- `phantom-guard cache stats|clear|path` - Cache management
- Rich terminal output with colors and progress indicators
- JSON output mode for CI/CD integration (`--output json`)
- Exit codes (0-5) for automation

#### File Format Support
- requirements.txt (Python)
- package.json (npm)
- Cargo.toml (Rust)

#### Performance
- Single package (cached): <10ms P99
- Single package (uncached): <200ms P99
- Batch 50 packages: <5s P99
- Pattern matching: <1ms P99

### Security
- No shell command execution
- No eval/exec usage
- Input validation on all package names
- Rate limit handling for all registries
- Graceful degradation on errors

### Technical
- 99% test coverage (950+ tests)
- Full type annotations (mypy --strict)
- Pre-compiled regex patterns
- LRU-cached Levenshtein distance
- Async/await throughout
