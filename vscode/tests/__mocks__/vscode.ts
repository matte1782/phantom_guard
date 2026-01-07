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

// Mock ConfigurationTarget enum
export enum ConfigurationTarget {
  Global = 1,
  Workspace = 2,
  WorkspaceFolder = 3,
}

// Mock EventEmitter class
export class EventEmitter<T> {
  private listeners: Array<(e: T) => void> = [];

  event = (listener: (e: T) => void) => {
    this.listeners.push(listener);
    return { dispose: () => this.listeners = this.listeners.filter(l => l !== listener) };
  };

  fire(data: T): void {
    this.listeners.forEach(l => l(data));
  }

  dispose(): void {
    this.listeners = [];
  }
}

// Mock ConfigurationChangeEvent
export interface ConfigurationChangeEvent {
  affectsConfiguration(section: string): boolean;
}

// Storage for mock configuration values
let mockConfigValues: Record<string, Record<string, any>> = {};

// Function to set mock config values for testing
export function setMockConfig(section: string, values: Record<string, any>): void {
  mockConfigValues[section] = values;
}

// Function to clear mock config
export function clearMockConfig(): void {
  mockConfigValues = {};
}

// Configuration change listeners
const configChangeListeners: Array<(e: ConfigurationChangeEvent) => void> = [];

// Function to trigger config change for testing
export function triggerConfigChange(section: string): void {
  const event: ConfigurationChangeEvent = {
    affectsConfiguration: (s: string) => s === section || section.startsWith(s + '.'),
  };
  configChangeListeners.forEach(l => l(event));
}

// Mock WorkspaceConfiguration
export class MockWorkspaceConfiguration {
  constructor(private section: string) {}

  get<T>(key: string, defaultValue?: T): T {
    const sectionConfig = mockConfigValues[this.section] || {};
    if (key in sectionConfig) {
      return sectionConfig[key] as T;
    }
    return defaultValue as T;
  }

  update = vi.fn().mockImplementation(async (key: string, value: any, _target?: ConfigurationTarget) => {
    if (!mockConfigValues[this.section]) {
      mockConfigValues[this.section] = {};
    }
    mockConfigValues[this.section][key] = value;
    triggerConfigChange(this.section);
  });

  has(key: string): boolean {
    const sectionConfig = mockConfigValues[this.section] || {};
    return key in sectionConfig;
  }

  inspect<T>(_key: string): { defaultValue?: T; globalValue?: T; workspaceValue?: T } | undefined {
    return undefined;
  }
}

// Mock open text documents
let mockTextDocuments: MockTextDocument[] = [];

export function setMockTextDocuments(docs: MockTextDocument[]): void {
  mockTextDocuments = docs;
}

export function clearMockTextDocuments(): void {
  mockTextDocuments = [];
}

// Mock workspace
export const workspace = {
  onDidCloseTextDocument: vi.fn(() => ({ dispose: vi.fn() })),
  onDidSaveTextDocument: vi.fn(() => ({ dispose: vi.fn() })),
  onDidChangeTextDocument: vi.fn(() => ({ dispose: vi.fn() })),
  onDidOpenTextDocument: vi.fn(() => ({ dispose: vi.fn() })),
  onDidChangeConfiguration: vi.fn((listener: (e: ConfigurationChangeEvent) => void) => {
    configChangeListeners.push(listener);
    return { dispose: () => {
      const idx = configChangeListeners.indexOf(listener);
      if (idx >= 0) configChangeListeners.splice(idx, 1);
    }};
  }),
  getConfiguration: vi.fn((section: string) => new MockWorkspaceConfiguration(section)),
  get textDocuments(): MockTextDocument[] {
    return mockTextDocuments;
  },
};

// Mock languages
export const languages = {
  createDiagnosticCollection: vi.fn(() => new MockDiagnosticCollection()),
  registerHoverProvider: vi.fn(() => ({ dispose: vi.fn() })),
  registerCodeActionsProvider: vi.fn(() => ({ dispose: vi.fn() })),
};

// Mock ProgressLocation
export enum ProgressLocation {
  SourceControl = 1,
  Window = 10,
  Notification = 15,
}

// Mock window
export const window = {
  showErrorMessage: vi.fn().mockResolvedValue(undefined),
  showWarningMessage: vi.fn().mockResolvedValue(undefined),
  showInformationMessage: vi.fn().mockResolvedValue(undefined),
  createStatusBarItem: vi.fn(() => new MockStatusBarItem()),
  showInputBox: vi.fn().mockResolvedValue(undefined),
  activeTextEditor: undefined as any,
  withProgress: vi.fn().mockImplementation(async (_options: any, task: any) => {
    return await task({ report: vi.fn() });
  }),
};

// Mock commands
export const commands = {
  registerCommand: vi.fn((command: string, callback: (...args: any[]) => any) => {
    return { dispose: vi.fn() };
  }),
  executeCommand: vi.fn().mockResolvedValue(undefined),
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
  ConfigurationTarget,
  EventEmitter,
  ProgressLocation,
  workspace,
  languages,
  window,
  commands,
  env,
};
