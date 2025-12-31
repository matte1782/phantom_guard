# CI/CD Integration Guide

This guide provides comprehensive integration examples for incorporating Phantom Guard into your CI/CD pipelines. All configurations are production-ready and can be copied directly into your projects.

## Table of Contents

1. [Exit Codes Reference](#exit-codes-reference)
2. [GitHub Actions](#github-actions)
3. [GitLab CI](#gitlab-ci)
4. [Jenkins](#jenkins)
5. [Azure Pipelines](#azure-pipelines)
6. [CircleCI](#circleci)
7. [Pre-commit Hooks](#pre-commit-hooks)
8. [Best Practices](#best-practices)

---

## Exit Codes Reference

Phantom Guard uses semantic exit codes to communicate validation results:

| Code | Status | Description |
|------|--------|-------------|
| `0` | SAFE | All packages verified as legitimate |
| `1` | SUSPICIOUS | One or more packages flagged as suspicious |
| `2` | HIGH_RISK | One or more packages flagged as high risk |
| `3` | NOT_FOUND | One or more packages not found in registry |
| `4` | INPUT_ERROR | Invalid input (bad package name, unknown registry) |
| `5` | RUNTIME_ERROR | Unexpected runtime error |

**CI/CD Recommendation**: Fail builds on exit codes `1`, `2`, and `3`. Exit code `4` and `5` indicate configuration issues that should also fail the build.

---

## GitHub Actions

### Basic Workflow

```yaml
# .github/workflows/phantom-guard.yml
name: Phantom Guard Security Scan

on:
  push:
    branches: [main, develop]
    paths:
      - 'requirements*.txt'
      - 'package.json'
      - 'Cargo.toml'
  pull_request:
    branches: [main]
  schedule:
    # Run weekly on Monday at 9 AM UTC
    - cron: '0 9 * * 1'

jobs:
  security-scan:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Phantom Guard
        run: pip install phantom-guard

      - name: Scan dependencies
        run: phantom-guard check requirements.txt --output json > report.json
        continue-on-error: true
        id: scan

      - name: Upload security report
        uses: actions/upload-artifact@v4
        with:
          name: phantom-guard-report
          path: report.json
          retention-days: 30

      - name: Fail on risks
        if: steps.scan.outcome == 'failure'
        run: |
          echo "Security risks detected in dependencies!"
          cat report.json
          exit 1
```

### Matrix Testing with Multiple Python Versions

```yaml
# .github/workflows/phantom-guard-matrix.yml
name: Phantom Guard Matrix Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  scan:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12', '3.13']

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ matrix.python-version }}-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-${{ matrix.python-version }}-
            ${{ runner.os }}-pip-

      - name: Install Phantom Guard
        run: pip install phantom-guard

      - name: Run security scan
        run: phantom-guard check requirements.txt --fail-on suspicious

      - name: Generate JSON report
        if: always()
        run: |
          phantom-guard check requirements.txt --output json > report-${{ matrix.os }}-${{ matrix.python-version }}.json || true

      - name: Upload report artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: report-${{ matrix.os }}-${{ matrix.python-version }}
          path: report-*.json
          retention-days: 14
```

### Caching Pip Dependencies

```yaml
# .github/workflows/phantom-guard-cached.yml
name: Phantom Guard with Caching

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.local/share/phantom-guard
          key: ${{ runner.os }}-phantom-guard-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-phantom-guard-

      - name: Install Phantom Guard
        run: pip install phantom-guard

      - name: Warm cache (optional - speeds up subsequent runs)
        run: phantom-guard check requirements.txt --quiet || true

      - name: Security scan with report
        run: |
          phantom-guard check requirements.txt \
            --output json \
            --parallel 20 \
            > security-report.json

      - name: Upload security report
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: security-report.json
```

---

## GitLab CI

### Complete .gitlab-ci.yml Configuration

```yaml
# .gitlab-ci.yml
stages:
  - security
  - test
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - .phantom-guard-cache/

phantom-guard-scan:
  stage: security
  image: python:3.11-slim

  before_script:
    - pip install --upgrade pip
    - pip install phantom-guard

  script:
    - |
      echo "Scanning Python dependencies..."
      phantom-guard check requirements.txt --output json > phantom-guard-report.json

  after_script:
    - |
      if [ -f phantom-guard-report.json ]; then
        echo "=== Security Scan Results ==="
        cat phantom-guard-report.json
      fi

  artifacts:
    name: "phantom-guard-report-$CI_COMMIT_SHORT_SHA"
    paths:
      - phantom-guard-report.json
    reports:
      dotenv: phantom-guard.env
    expire_in: 30 days
    when: always

  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_PIPELINE_SOURCE == "schedule"

# Multi-registry scan
phantom-guard-multi-registry:
  stage: security
  image: python:3.11-slim

  before_script:
    - pip install phantom-guard

  script:
    - |
      echo "Scanning Python dependencies..."
      phantom-guard check requirements.txt -o json > pypi-report.json || PYPI_EXIT=$?

      if [ -f package.json ]; then
        echo "Scanning npm dependencies..."
        phantom-guard check package.json -o json > npm-report.json || NPM_EXIT=$?
      fi

      if [ -f Cargo.toml ]; then
        echo "Scanning Rust dependencies..."
        phantom-guard check Cargo.toml -o json > crates-report.json || CRATES_EXIT=$?
      fi

      # Combine results
      echo '{"scans": [' > combined-report.json
      cat pypi-report.json >> combined-report.json
      [ -f npm-report.json ] && echo ',' >> combined-report.json && cat npm-report.json >> combined-report.json
      [ -f crates-report.json ] && echo ',' >> combined-report.json && cat crates-report.json >> combined-report.json
      echo ']}' >> combined-report.json

      # Exit with highest risk code
      exit $(( ${PYPI_EXIT:-0} > ${NPM_EXIT:-0} ? ${PYPI_EXIT:-0} : ${NPM_EXIT:-0} ))

  artifacts:
    paths:
      - "*-report.json"
    expire_in: 7 days
    when: always

  allow_failure: false
```

---

## Jenkins

### Jenkinsfile Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-u root'
        }
    }

    environment {
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install phantom-guard
                '''
            }
        }

        stage('Security Scan') {
            steps {
                script {
                    def scanResult = sh(
                        script: '''
                            phantom-guard check requirements.txt \
                                --output json \
                                --parallel 10 \
                                > phantom-guard-report.json
                        ''',
                        returnStatus: true
                    )

                    // Archive report regardless of result
                    archiveArtifacts artifacts: 'phantom-guard-report.json', allowEmptyArchive: true

                    // Interpret exit codes
                    switch(scanResult) {
                        case 0:
                            echo 'All dependencies are SAFE'
                            break
                        case 1:
                            unstable('SUSPICIOUS packages detected')
                            break
                        case 2:
                            error('HIGH_RISK packages detected - failing build')
                            break
                        case 3:
                            unstable('Some packages NOT_FOUND in registry')
                            break
                        default:
                            error("Scan failed with error code: ${scanResult}")
                    }
                }
            }
        }

        stage('Generate Report') {
            when {
                expression { fileExists('phantom-guard-report.json') }
            }
            steps {
                sh '''
                    echo "=== Phantom Guard Security Report ==="
                    cat phantom-guard-report.json | python -m json.tool
                '''

                publishHTML(target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'phantom-guard-report.json',
                    reportName: 'Phantom Guard Report'
                ])
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        failure {
            emailext(
                subject: "Security Alert: ${currentBuild.fullDisplayName}",
                body: '''Phantom Guard detected security risks in dependencies.

Please review the attached report.

Build: ${BUILD_URL}''',
                attachmentsPattern: 'phantom-guard-report.json',
                recipientProviders: [developers(), requestor()]
            )
        }
    }
}
```

### Declarative Pipeline with Parallel Scans

```groovy
// Jenkinsfile-parallel
pipeline {
    agent any

    stages {
        stage('Parallel Security Scans') {
            parallel {
                stage('Python Dependencies') {
                    agent {
                        docker { image 'python:3.11-slim' }
                    }
                    when {
                        expression { fileExists('requirements.txt') }
                    }
                    steps {
                        sh 'pip install phantom-guard'
                        sh 'phantom-guard check requirements.txt -o json > pypi-report.json || true'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'pypi-report.json', allowEmptyArchive: true
                        }
                    }
                }

                stage('npm Dependencies') {
                    agent {
                        docker { image 'python:3.11-slim' }
                    }
                    when {
                        expression { fileExists('package.json') }
                    }
                    steps {
                        sh 'pip install phantom-guard'
                        sh 'phantom-guard check package.json -o json > npm-report.json || true'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'npm-report.json', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
    }
}
```

---

## Azure Pipelines

### azure-pipelines.yml Configuration

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - requirements*.txt
      - package.json
      - Cargo.toml

pr:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'

stages:
  - stage: SecurityScan
    displayName: 'Phantom Guard Security Scan'
    jobs:
      - job: ScanDependencies
        displayName: 'Scan Dependencies'

        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
              addToPath: true
            displayName: 'Use Python $(pythonVersion)'

          - task: Cache@2
            inputs:
              key: 'pip | "$(Agent.OS)" | requirements.txt'
              path: $(PIP_CACHE_DIR)
              restoreKeys: |
                pip | "$(Agent.OS)"
            displayName: 'Cache pip packages'

          - script: |
              python -m pip install --upgrade pip
              pip install phantom-guard
            displayName: 'Install Phantom Guard'

          - script: |
              phantom-guard check requirements.txt \
                --output json \
                --parallel 10 \
                > $(Build.ArtifactStagingDirectory)/phantom-guard-report.json
            displayName: 'Run Security Scan'
            continueOnError: true

          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: '$(Build.ArtifactStagingDirectory)/phantom-guard-report.json'
              artifactName: 'SecurityReport'
            displayName: 'Publish Security Report'
            condition: always()

          - script: |
              echo "Checking scan results..."
              phantom-guard check requirements.txt --fail-on suspicious
            displayName: 'Verify No Risks'

  - stage: MultiPlatformScan
    displayName: 'Multi-Platform Validation'
    dependsOn: SecurityScan
    jobs:
      - job: MatrixScan
        strategy:
          matrix:
            Linux_Python311:
              vmImage: 'ubuntu-latest'
              python: '3.11'
            Windows_Python311:
              vmImage: 'windows-latest'
              python: '3.11'
            macOS_Python311:
              vmImage: 'macos-latest'
              python: '3.11'

        pool:
          vmImage: $(vmImage)

        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(python)'

          - script: pip install phantom-guard
            displayName: 'Install'

          - script: phantom-guard check requirements.txt
            displayName: 'Scan'
```

---

## CircleCI

### .circleci/config.yml Configuration

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  python: circleci/python@2.1

executors:
  python-executor:
    docker:
      - image: cimg/python:3.11
    working_directory: ~/project

commands:
  install-phantom-guard:
    steps:
      - run:
          name: Install Phantom Guard
          command: pip install phantom-guard

  run-security-scan:
    parameters:
      file:
        type: string
        default: requirements.txt
      output:
        type: string
        default: phantom-guard-report.json
    steps:
      - run:
          name: Run Phantom Guard Scan
          command: |
            phantom-guard check << parameters.file >> \
              --output json \
              --parallel 10 \
              > << parameters.output >> || true
      - store_artifacts:
          path: << parameters.output >>
          destination: security-reports/<< parameters.output >>

jobs:
  security-scan:
    executor: python-executor
    steps:
      - checkout

      - restore_cache:
          keys:
            - pip-cache-{{ checksum "requirements.txt" }}
            - pip-cache-

      - install-phantom-guard

      - save_cache:
          key: pip-cache-{{ checksum "requirements.txt" }}
          paths:
            - ~/.cache/pip

      - run-security-scan:
          file: requirements.txt
          output: phantom-guard-report.json

      - run:
          name: Check for High Risk Packages
          command: phantom-guard check requirements.txt --fail-on suspicious

  multi-registry-scan:
    executor: python-executor
    steps:
      - checkout
      - install-phantom-guard

      - run:
          name: Scan All Dependency Files
          command: |
            for file in requirements*.txt package.json Cargo.toml; do
              if [ -f "$file" ]; then
                echo "Scanning $file..."
                phantom-guard check "$file" --output json > "report-${file%.*}.json" || true
              fi
            done

      - store_artifacts:
          path: .
          destination: security-reports

  scheduled-scan:
    executor: python-executor
    steps:
      - checkout
      - install-phantom-guard
      - run-security-scan
      - run:
          name: Notify on Risks
          command: |
            if ! phantom-guard check requirements.txt --quiet; then
              echo "Security risks detected - notification would be sent"
              # Add Slack/email notification here
            fi

workflows:
  version: 2

  on-commit:
    jobs:
      - security-scan:
          filters:
            branches:
              only:
                - main
                - develop

  weekly-scan:
    triggers:
      - schedule:
          cron: "0 9 * * 1"
          filters:
            branches:
              only:
                - main
    jobs:
      - scheduled-scan
```

---

## Pre-commit Hooks

### .pre-commit-config.yaml Setup

```yaml
# .pre-commit-config.yaml
repos:
  # Phantom Guard security scan
  - repo: local
    hooks:
      - id: phantom-guard
        name: Phantom Guard Security Scan
        entry: phantom-guard check
        language: system
        files: ^(requirements.*\.txt|package\.json|Cargo\.toml)$
        pass_filenames: true
        stages: [commit, push]
        verbose: true

      - id: phantom-guard-strict
        name: Phantom Guard Strict Mode
        entry: phantom-guard check --fail-on suspicious
        language: system
        files: ^requirements.*\.txt$
        pass_filenames: true
        stages: [push]

  # Standard pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Local Hook Configuration (Alternative)

Create a local hook script for more control:

```bash
#!/bin/bash
# .git/hooks/pre-commit (or use pre-commit framework)

echo "Running Phantom Guard security scan..."

# Find dependency files that changed
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

EXIT_CODE=0

for file in $CHANGED_FILES; do
    case "$file" in
        requirements*.txt|package.json|Cargo.toml)
            echo "Scanning $file..."
            phantom-guard check "$file" --quiet
            RESULT=$?
            if [ $RESULT -gt $EXIT_CODE ]; then
                EXIT_CODE=$RESULT
            fi
            ;;
    esac
done

if [ $EXIT_CODE -eq 2 ]; then
    echo ""
    echo "ERROR: High-risk packages detected!"
    echo "Run 'phantom-guard check <file>' for details."
    echo "Use 'git commit --no-verify' to bypass (not recommended)."
    exit 1
elif [ $EXIT_CODE -eq 1 ]; then
    echo ""
    echo "WARNING: Suspicious packages detected."
    echo "Run 'phantom-guard check <file>' for details."
    # Allow commit but warn
fi

exit 0
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

### Installing Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks defined in .pre-commit-config.yaml
pre-commit install

# Run against all files (initial scan)
pre-commit run phantom-guard --all-files

# Run on push hooks as well
pre-commit install --hook-type pre-push
```

---

## Best Practices

### When to Fail Builds

| Risk Level | Recommended Action | Rationale |
|------------|-------------------|-----------|
| HIGH_RISK (2) | **Always fail** | Potential malicious package |
| SUSPICIOUS (1) | Fail in production branches | May be legitimate but needs review |
| NOT_FOUND (3) | Warn or fail | Package may be hallucinated |
| SAFE (0) | Pass | Verified legitimate |

**Recommended strategy by branch:**

```yaml
# Production branches (main, master)
phantom-guard check requirements.txt --fail-on suspicious

# Development branches
phantom-guard check requirements.txt  # Fail only on HIGH_RISK

# Feature branches
phantom-guard check requirements.txt --quiet || true  # Warn only
```

### JSON Output for Processing

Use JSON output for programmatic processing:

```bash
# Get structured output
phantom-guard check requirements.txt --output json > report.json

# Process with jq
cat report.json | jq '.[] | select(.recommendation == "HIGH_RISK")'

# Count by risk level
cat report.json | jq 'group_by(.recommendation) | map({recommendation: .[0].recommendation, count: length})'
```

### Caching Recommendations

1. **Cache Phantom Guard's internal cache**: `~/.local/share/phantom-guard/` (Linux/macOS) or `%LOCALAPPDATA%\phantom-guard\` (Windows)

2. **Cache pip packages**: Standard pip cache location

3. **Warm the cache** before main scan:
   ```bash
   phantom-guard check requirements.txt --quiet || true
   phantom-guard check requirements.txt --output json > report.json
   ```

4. **TTL considerations**: Registry metadata cache expires after 24 hours by default

### Performance Optimization

```yaml
# Parallel validation (default: 10)
phantom-guard check requirements.txt --parallel 20

# Fail fast on first HIGH_RISK
phantom-guard check requirements.txt --fail-fast

# Skip known-good packages
phantom-guard check requirements.txt --ignore numpy,pandas,requests
```

### Integration with Security Dashboards

```bash
# SARIF output for GitHub Security tab (future)
phantom-guard check requirements.txt --output sarif > results.sarif

# Integration with Snyk/Dependabot
# Run Phantom Guard as complement to traditional vulnerability scanners
```

### Recommended CI/CD Pipeline Order

```
1. Checkout code
2. Restore caches
3. Install Phantom Guard
4. Run Phantom Guard scan (fail on HIGH_RISK)
5. Run traditional security scans (Snyk, etc.)
6. Run tests
7. Build artifacts
8. Deploy (if all passed)
```

---

## Troubleshooting

### Common Issues

**Issue**: Scan times out in CI
```yaml
# Increase timeout and reduce parallelism
phantom-guard check requirements.txt --parallel 5 --timeout 300
```

**Issue**: Rate limiting from registries
```yaml
# Use caching and reduce concurrent requests
phantom-guard check requirements.txt --parallel 3
```

**Issue**: False positives
```yaml
# Review and add to ignore list
phantom-guard check requirements.txt --ignore legitimate-package-name
```

---

## Support

- Documentation: https://phantom-guard.readthedocs.io
- Issues: https://github.com/phantom-guard/phantom-guard/issues
- Security: security@phantom-guard.dev
