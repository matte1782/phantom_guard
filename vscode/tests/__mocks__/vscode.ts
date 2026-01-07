/**
 * Mock VS Code API for testing
 */

import { vi } from 'vitest';

// Mock DiagnosticSeverity enum
export enum DiagnosticSeverity {
  Error = 0,
  Warning = 1,
  Information = 2,
  Hint = 3,
}

// Mock Range class
export class Range {
  constructor(
    public startLine: number,
    public startCharacter: number,
    public endLine: number,
    public endCharacter: number
  ) {}

  get start() {
    return { line: this.startLine, character: this.startCharacter };
  }

  get end() {
    return { line: this.endLine, character: this.endCharacter };
  }
}

// Mock Position class
export class Position {
  constructor(public line: number, public character: number) {}
}

// Mock MarkdownString class
export class MarkdownString {
  value: string = '';
  isTrusted: boolean = false;

  appendMarkdown(value: string): MarkdownString {
    this.value += value;
    return this;
  }

  appendText(value: string): MarkdownString {
    this.value += value;
    return this;
  }
}

// Mock Hover class
export class Hover {
  constructor(
    public contents: MarkdownString | string,
    public range?: Range
  ) {}
}

// Mock CancellationToken
export const CancellationToken = {
  isCancellationRequested: false,
  onCancellationRequested: vi.fn(),
};

// Mock CodeActionKind
export const CodeActionKind = {
  QuickFix: { value: 'quickfix' },
  Refactor: { value: 'refactor' },
  Source: { value: 'source' },
};

// Mock CodeAction class
export class CodeAction {
  edit?: WorkspaceEdit;
  command?: any;
  diagnostics?: Diagnostic[];
  isPreferred?: boolean;

  constructor(
    public title: string,
    public kind?: typeof CodeActionKind.QuickFix
  ) {}
}

// Mock WorkspaceEdit class
export class WorkspaceEdit {
  private edits: Array<{ uri: Uri; range: Range; newText: string }> = [];
  private deletes: Array<{ uri: Uri; range: Range }> = [];
  private inserts: Array<{ uri: Uri; position: Position; text: string }> = [];

  replace(uri: Uri, range: Range, newText: string): void {
    this.edits.push({ uri, range, newText });
  }

  delete(uri: Uri, range: Range): void {
    this.deletes.push({ uri, range });
  }

  insert(uri: Uri, position: Position, text: string): void {
    this.inserts.push({ uri, position, text });
  }

  get size(): number {
    return this.edits.length + this.deletes.length + this.inserts.length;
  }
}

// Mock StatusBarAlignment
export enum StatusBarAlignment {
  Left = 1,
  Right = 2,
}

// Mock ThemeColor
export class ThemeColor {
  constructor(public id: string) {}
}

// Mock StatusBarItem
export class MockStatusBarItem {
  text: string = '';
  tooltip: string = '';
  command?: string;
  backgroundColor?: ThemeColor;
  alignment: StatusBarAlignment = StatusBarAlignment.Right;
  priority: number = 0;

  show = vi.fn();
  hide = vi.fn();
  dispose = vi.fn();
}

// Mock Diagnostic class
export class Diagnostic {
  source?: string;
  code?: string | number;

  constructor(
    public range: Range,
    public message: string,
    public severity: DiagnosticSeverity = DiagnosticSeverity.Error
  ) {}
}

// Mock Uri class
export class Uri {
  constructor(public fsPath: string) {}

  toString(): string {
    return this.fsPath;
  }

  static file(path: string): Uri {
    return new Uri(path);
  }

  static parse(url: string): Uri {
    return new Uri(url);
  }
}

// Mock TextDocument
export class MockTextDocument {
  constructor(
    public uri: Uri,
    private content: string = ''
  ) {}

  getText(): string {
    return this.content;
  }

  get languageId(): string {
    return 'plaintext';
  }
}

// Mock DiagnosticCollection
export class MockDiagnosticCollection {
  private diagnostics: Map<string, Diagnostic[]> = new Map();

  set(uri: Uri, diagnostics: Diagnostic[]): void {
    this.diagnostics.set(uri.toString(), diagnostics);
  }

  get(uri: Uri): Diagnostic[] | undefined {
    return this.diagnostics.get(uri.toString());
  }

  delete(uri: Uri): void {
    this.diagnostics.delete(uri.toString());
  }

  clear(): void {
    this.diagnostics.clear();
  }

  dispose(): void {
    this.clear();
  }
}

// Mock workspace
export const workspace = {
  onDidCloseTextDocument: vi.fn(() => ({ dispose: vi.fn() })),
  onDidSaveTextDocument: vi.fn(() => ({ dispose: vi.fn() })),
  onDidChangeTextDocument: vi.fn(() => ({ dispose: vi.fn() })),
  onDidOpenTextDocument: vi.fn(() => ({ dispose: vi.fn() })),
};

// Mock languages
export const languages = {
  createDiagnosticCollection: vi.fn(() => new MockDiagnosticCollection()),
  registerHoverProvider: vi.fn(() => ({ dispose: vi.fn() })),
  registerCodeActionsProvider: vi.fn(() => ({ dispose: vi.fn() })),
};

// Mock window
export const window = {
  showErrorMessage: vi.fn().mockResolvedValue(undefined),
  showWarningMessage: vi.fn().mockResolvedValue(undefined),
  showInformationMessage: vi.fn().mockResolvedValue(undefined),
  createStatusBarItem: vi.fn(() => new MockStatusBarItem()),
};

// Mock env
export const env = {
  openExternal: vi.fn().mockResolvedValue(true),
};

export default {
  DiagnosticSeverity,
  Range,
  Position,
  MarkdownString,
  Hover,
  CancellationToken,
  CodeActionKind,
  CodeAction,
  WorkspaceEdit,
  StatusBarAlignment,
  ThemeColor,
  Diagnostic,
  Uri,
  workspace,
  languages,
  window,
  env,
};
