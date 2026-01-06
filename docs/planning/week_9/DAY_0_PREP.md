# Week 9, Day 0 — Pre-Implementation Setup

> **Date**: Day 0 of Week 9 (Prep Day)
> **Focus**: VS Code Extension project scaffold
> **Hours**: 2-3 (can be done evening before Day 1)
> **Prerequisites**: Week 8 complete, test stubs exist in vscode/tests/

---

## Purpose

This prep day sets up the VS Code extension project structure so Day 1 can focus entirely on implementation. This addresses P1-HOUR-001 from hostile review.

---

## Tasks

### Task 1: Project Scaffold (2 hours)

Create the VS Code extension project structure:

```
vscode/
├── .vscode/
│   ├── launch.json          # Debug configuration
│   └── tasks.json           # Build tasks
├── src/
│   ├── extension.ts         # Entry point stub
│   ├── core.ts              # CLI integration stub
│   ├── diagnostics.ts       # Diagnostic provider stub
│   ├── hover.ts             # Hover provider stub
│   ├── actions.ts           # Code action provider stub
│   ├── statusbar.ts         # Status bar stub
│   ├── config.ts            # Configuration stub
│   ├── errors.ts            # Error types
│   └── types.ts             # Type definitions
├── tests/                   # Already exists with stubs
├── package.json             # Extension manifest
├── tsconfig.json            # TypeScript config
├── .vscodeignore            # Files to exclude from package
└── README.md                # Extension documentation
```

---

### package.json

```json
{
  "name": "phantom-guard-vscode",
  "displayName": "Phantom Guard",
  "description": "Detect AI-hallucinated package attacks in your dependencies",
  "version": "0.1.0",
  "publisher": "phantom-guard",
  "repository": {
    "type": "git",
    "url": "https://github.com/matte1782/phantom-guard"
  },
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["Linters", "Other"],
  "keywords": ["security", "dependencies", "slopsquatting", "supply-chain"],
  "activationEvents": [
    "workspaceContains:requirements.txt",
    "workspaceContains:package.json",
    "workspaceContains:Cargo.toml"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "configuration": {
      "title": "Phantom Guard",
      "properties": {
        "phantomGuard.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable Phantom Guard validation"
        },
        "phantomGuard.pythonPath": {
          "type": "string",
          "default": "",
          "description": "Path to Python executable (leave empty for auto-detect)"
        },
        "phantomGuard.threshold": {
          "type": "number",
          "default": 0.5,
          "minimum": 0,
          "maximum": 1,
          "description": "Risk score threshold for warnings (0.0-1.0)"
        },
        "phantomGuard.ignoredPackages": {
          "type": "array",
          "items": { "type": "string" },
          "default": [],
          "description": "Packages to ignore during validation"
        }
      }
    },
    "commands": [
      {
        "command": "phantom-guard.showSummary",
        "title": "Phantom Guard: Show Validation Summary"
      },
      {
        "command": "phantom-guard.ignorePackage",
        "title": "Phantom Guard: Ignore Package"
      },
      {
        "command": "phantom-guard.revalidate",
        "title": "Phantom Guard: Revalidate Current File"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "lint": "eslint src --ext ts",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:integration": "node ./out/tests/integration/setup.js",
    "pretest:integration": "npm run compile"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0",
    "@vitest/coverage-v8": "^1.0.0",
    "@vscode/test-electron": "^2.3.0",
    "eslint": "^8.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0"
  }
}
```

---

### tsconfig.json

```json
{
  "compilerOptions": {
    "module": "Node16",
    "target": "ES2022",
    "outDir": "out",
    "lib": ["ES2022"],
    "sourceMap": true,
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "Node16"
  },
  "exclude": ["node_modules", ".vscode-test", "out", "tests"]
}
```

---

### .vscode/launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Extension",
      "type": "extensionHost",
      "request": "launch",
      "args": [
        "--extensionDevelopmentPath=${workspaceFolder}"
      ],
      "outFiles": ["${workspaceFolder}/out/**/*.js"],
      "preLaunchTask": "npm: compile"
    },
    {
      "name": "Extension Tests",
      "type": "extensionHost",
      "request": "launch",
      "args": [
        "--extensionDevelopmentPath=${workspaceFolder}",
        "--extensionTestsPath=${workspaceFolder}/out/tests/integration"
      ],
      "outFiles": ["${workspaceFolder}/out/**/*.js"],
      "preLaunchTask": "npm: compile"
    }
  ]
}
```

---

### .vscode/tasks.json

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "type": "npm",
      "script": "compile",
      "problemMatcher": "$tsc",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    },
    {
      "type": "npm",
      "script": "watch",
      "problemMatcher": "$tsc-watch",
      "isBackground": true
    }
  ]
}
```

---

### src/types.ts (Stub)

```typescript
/**
 * IMPLEMENTS: S120-S126
 * Type definitions for Phantom Guard VS Code Extension
 */

export type RiskLevel = 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK' | 'NOT_FOUND' | 'ERROR';

export interface PackageRisk {
  name: string;
  risk_level: RiskLevel;
  risk_score: number;
  signals: string[];
  recommendation?: string;
}

export interface ValidationResult {
  packages: PackageRisk[];
  total: number;
  safe: number;
  suspicious: number;
  highRisk: number;
  notFound: number;
}
```

---

### src/errors.ts (Stub)

```typescript
/**
 * IMPLEMENTS: S120, S126
 * Error types for VS Code Extension
 */

export class ExtensionError extends Error {
  constructor(message: string, public readonly recoverable: boolean = true) {
    super(message);
    this.name = 'ExtensionError';
  }
}

export class ActivationError extends ExtensionError {
  constructor(reason: string) {
    super(`Extension activation failed: ${reason}`, false);
    this.name = 'ActivationError';
  }
}

export class CoreSpawnError extends ExtensionError {
  constructor(reason: string) {
    super(`Failed to spawn phantom-guard process: ${reason}`, true);
    this.name = 'CoreSpawnError';
  }
}

export class CoreTimeoutError extends ExtensionError {
  constructor(timeoutMs: number) {
    super(`Core process timed out after ${timeoutMs}ms`, true);
    this.name = 'CoreTimeoutError';
  }
}

export class CoreParseError extends ExtensionError {
  constructor(output: string) {
    super(`Failed to parse core output: ${output.slice(0, 100)}...`, true);
    this.name = 'CoreParseError';
  }
}

export class PythonNotFoundError extends ExtensionError {
  constructor() {
    super('Python 3.11+ not found. Please install Python or configure path.', false);
    this.name = 'PythonNotFoundError';
  }
}
```

---

### .vscodeignore

```
.vscode/**
.vscode-test/**
src/**
tests/**
node_modules/**
.gitignore
tsconfig.json
*.ts
!out/**
```

---

## Checklist

- [ ] Create vscode/package.json
- [ ] Create vscode/tsconfig.json
- [ ] Create vscode/.vscode/launch.json
- [ ] Create vscode/.vscode/tasks.json
- [ ] Create vscode/src/types.ts
- [ ] Create vscode/src/errors.ts
- [ ] Create vscode/.vscodeignore
- [ ] Run `npm install`
- [ ] Verify `npm run compile` works (with empty stubs)

---

## Commit

```bash
git add vscode/
git commit -m "chore: VS Code extension scaffold (Day 0 prep)

Prepare project structure for Week 9 implementation:
- Add package.json with extension manifest
- Add tsconfig.json for TypeScript compilation
- Add VS Code debug/task configurations
- Add type definitions and error types
- Add .vscodeignore for packaging

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

**Day 0 prepares the foundation. Day 1 focuses on implementation.**
