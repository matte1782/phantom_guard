/**
 * SPEC: S122 - Hover Provider
 * TEST_IDs: T122.01-T122.03
 * INVARIANTS: INV123
 * EDGE_CASES: EC340-EC350
 *
 * Tests for VS Code hover information.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Uri, Position, CancellationToken } from './__mocks__/vscode';

// Mock vscode module
vi.mock('vscode', () => import('./__mocks__/vscode'));

// Mock core module
vi.mock('../src/core', () => ({
  PhantomGuardCore: vi.fn().mockImplementation(() => ({
    validatePackage: vi.fn().mockResolvedValue(null),
    dispose: vi.fn(),
  })),
}));

// Mock TextDocument
function createMockDocument(content: string, fileName: string) {
  const lines = content.split('\n');
  return {
    uri: Uri.file(fileName),
    getText: () => content,
    lineAt: (line: number) => ({
      text: lines[line] || '',
      range: { start: { line, character: 0 }, end: { line, character: lines[line]?.length || 0 } },
    }),
    languageId: 'plaintext',
  };
}

describe('Hover Provider (S122)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // T122.01: Hover on package line shows risk tooltip
  // =========================================================================
  it('T122.01: hover on package line shows tooltip', async () => {
    /**
     * SPEC: S122
     * TEST_ID: T122.01
     * INV_ID: INV123
     * EC_ID: EC340
     *
     * Given: Cursor on "flask" in requirements.txt
     * When: Hover triggered
     * Then: Tooltip shows package risk info
     */
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    vi.mocked(mockCore.validatePackage).mockResolvedValue({
      name: 'flask',
      risk_level: 'SUSPICIOUS',
      risk_score: 0.65,
      signals: ['ai_suffix'],
    });

    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('flask==2.0.0\nrequests>=1.0', '/test/requirements.txt');
    const position = new Position(0, 2); // On "flask"

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).not.toBeNull();
    expect(hover!.contents.value).toContain('flask');
    expect(hover!.contents.value).toContain('Suspicious');
    expect(hover!.contents.value).toContain('65%');
  });

  // =========================================================================
  // T122.02: No hover on comment line
  // =========================================================================
  it('T122.02: no hover on comment line', async () => {
    /**
     * SPEC: S122
     * TEST_ID: T122.02
     * INV_ID: INV123
     * EC_ID: EC341
     *
     * Given: Cursor on "# comment" line
     * When: Hover triggered
     * Then: Returns null (no hover)
     */
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('# This is a comment\nflask==2.0.0', '/test/requirements.txt');
    const position = new Position(0, 5); // On comment line

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).toBeNull();
  });

  // =========================================================================
  // T122.03: Safe package shows "safe" tooltip
  // =========================================================================
  it('T122.03: safe package shows safe status', async () => {
    /**
     * SPEC: S122
     * TEST_ID: T122.03
     * INV_ID: INV123
     * EC_ID: EC347
     *
     * Given: Cursor on "flask" (known safe)
     * When: Hover triggered
     * Then: Tooltip shows "Safe" status with checkmark
     */
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    vi.mocked(mockCore.validatePackage).mockResolvedValue({
      name: 'flask',
      risk_level: 'SAFE',
      risk_score: 0.1,
      signals: [],
    });

    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('flask==2.0.0', '/test/requirements.txt');
    const position = new Position(0, 2);

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).not.toBeNull();
    expect(hover!.contents.value).toContain('✅');
    expect(hover!.contents.value).toContain('Safe');
  });
});

describe('Hover Edge Cases (EC340-EC350)', () => {
  it('EC342: empty line = no hover', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('flask==2.0.0\n\nrequests>=1.0', '/test/requirements.txt');
    const position = new Position(1, 0); // Empty line

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).toBeNull();
  });

  it('EC343: version specifier position = no hover (outside package range)', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('flask==2.0.0', '/test/requirements.txt');
    const position = new Position(0, 10); // On version specifier, outside "flask"

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    // Should return null because position is outside package name range
    expect(hover).toBeNull();
  });

  it.skip('EC344: JSON key = package tooltip', () => {});
  it.skip('EC345: JSON value = no hover (version)', () => {});
  it.skip('EC346: multiple signals listed in tooltip', () => {});
  it.skip('EC348: cached result = instant response', () => {});
  it.skip('EC349: pending validation = shows validating', () => {});
  it.skip('EC350: long signal list = scrollable/truncated', () => {});
});

describe('Hover Returns Null on Non-Package Lines (INV123)', () => {
  it('returns null for comment lines', async () => {
    /**
     * INV123: Hover provider returns null on non-package lines
     */
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    // Test isCommentLine directly
    const uri = Uri.file('/test/requirements.txt');
    expect(provider.isCommentLine('# comment', uri)).toBe(true);
    expect(provider.isCommentLine('flask==1.0', uri)).toBe(false);
  });

  it('returns null for empty lines', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('', '/test/requirements.txt');
    const position = new Position(0, 0);

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).toBeNull();
  });

  it('returns null for whitespace-only lines', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('   \t  ', '/test/requirements.txt');
    const position = new Position(0, 2);

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).toBeNull();
  });

  it('returns null outside package name range', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('flask>=2.0.0', '/test/requirements.txt');
    const position = new Position(0, 8); // On >=2.0.0, outside "flask"

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).toBeNull();
  });
});

describe('Hover Content Format', () => {
  it('includes package name', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'test-package',
      risk_level: 'SAFE',
      risk_score: 0.1,
      signals: [],
    });

    expect(content.value).toContain('test-package');
  });

  it('includes risk classification', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'risky-pkg',
      risk_level: 'HIGH_RISK',
      risk_score: 0.9,
      signals: ['version_spike'],
    });

    expect(content.value).toContain('High Risk');
  });

  it('includes risk score as percentage', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'pkg',
      risk_level: 'SUSPICIOUS',
      risk_score: 0.75,
      signals: [],
    });

    expect(content.value).toContain('75%');
  });

  it('lists all detected signals', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'pkg',
      risk_level: 'HIGH_RISK',
      risk_score: 0.9,
      signals: ['signal1', 'signal2', 'signal3'],
    });

    expect(content.value).toContain('signal1');
    expect(content.value).toContain('signal2');
    expect(content.value).toContain('signal3');
  });

  it('uses correct status icons', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    expect(provider.getStatusIcon('SAFE')).toBe('✅');
    expect(provider.getStatusIcon('SUSPICIOUS')).toBe('⚠️');
    expect(provider.getStatusIcon('HIGH_RISK')).toBe('🚨');
    expect(provider.getStatusIcon('NOT_FOUND')).toBe('❓');
    expect(provider.getStatusIcon('ERROR')).toBe('❌');
  });

  it.skip('includes registry source', () => {});
  it.skip('uses markdown formatting', () => {});

  it('truncates signals list when more than 5', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'pkg',
      risk_level: 'HIGH_RISK',
      risk_score: 0.95,
      signals: ['sig1', 'sig2', 'sig3', 'sig4', 'sig5', 'sig6', 'sig7'],
    });

    // Should show first 5 signals and indicate more
    expect(content.value).toContain('sig1');
    expect(content.value).toContain('sig5');
    expect(content.value).toContain('...and 2 more');
  });

  it('includes recommendation when present', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'risky-pkg',
      risk_level: 'HIGH_RISK',
      risk_score: 0.9,
      signals: ['version_spike'],
      recommendation: 'Consider using an alternative package',
    });

    expect(content.value).toContain('Recommendation');
    expect(content.value).toContain('Consider using an alternative package');
  });

  it('handles unknown risk level with default icon', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    // Test with unknown level
    const icon = provider.getStatusIcon('UNKNOWN_LEVEL' as any);
    expect(icon).toBe('❔');
  });

  it('formats NOT_FOUND risk level correctly', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'missing-pkg',
      risk_level: 'NOT_FOUND',
      risk_score: 1.0,
      signals: [],
    });

    expect(content.value).toContain('❓');
    expect(content.value).toContain('Not Found');
  });

  it('formats ERROR risk level correctly', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'error-pkg',
      risk_level: 'ERROR',
      risk_score: 0,
      signals: [],
    });

    expect(content.value).toContain('❌');
    expect(content.value).toContain('Error');
  });

  it('handles unknown risk level with Unknown label', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const content = provider.createHoverContent({
      name: 'unknown-pkg',
      risk_level: 'SOME_NEW_LEVEL' as any,
      risk_score: 0.5,
      signals: [],
    });

    expect(content.value).toContain('Unknown');
  });
});

describe('Registry Detection', () => {
  it('detects npm registry for package.json', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    vi.mocked(mockCore.validatePackage).mockResolvedValue({
      name: 'lodash',
      risk_level: 'SAFE',
      risk_score: 0.05,
      signals: [],
    });

    const provider = new PhantomGuardHoverProvider(mockCore);

    // Create a package.json document
    const document = createMockDocument('"lodash": "^4.17.21"', '/test/package.json');
    const position = new Position(0, 3); // On "lodash"

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).not.toBeNull();
    expect(mockCore.validatePackage).toHaveBeenCalledWith('lodash', 'npm');
  });

  it('detects crates registry for Cargo.toml', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    vi.mocked(mockCore.validatePackage).mockResolvedValue({
      name: 'serde',
      risk_level: 'SAFE',
      risk_score: 0.02,
      signals: [],
    });

    const provider = new PhantomGuardHoverProvider(mockCore);

    // Create a Cargo.toml document with quoted package name
    const document = createMockDocument('"serde" = "1.0"', '/test/Cargo.toml');
    const position = new Position(0, 2); // On "serde"

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).not.toBeNull();
    expect(mockCore.validatePackage).toHaveBeenCalledWith('serde', 'crates');
  });

  it('detects crates registry for Cargo.toml key-value style', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    vi.mocked(mockCore.validatePackage).mockResolvedValue({
      name: 'tokio',
      risk_level: 'SAFE',
      risk_score: 0.02,
      signals: [],
    });

    const provider = new PhantomGuardHoverProvider(mockCore);

    // Test keyMatch path - no quotes before package name
    const document = createMockDocument('tokio = { }', '/test/Cargo.toml');
    const position = new Position(0, 2); // On "tokio"

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).not.toBeNull();
    expect(mockCore.validatePackage).toHaveBeenCalledWith('tokio', 'crates');
  });

  it('detects pypi registry for requirements.txt', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    vi.mocked(mockCore.validatePackage).mockResolvedValue({
      name: 'flask',
      risk_level: 'SAFE',
      risk_score: 0.05,
      signals: [],
    });

    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('flask==2.0.0', '/test/requirements.txt');
    const position = new Position(0, 2);

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).not.toBeNull();
    expect(mockCore.validatePackage).toHaveBeenCalledWith('flask', 'pypi');
  });

  it('detects pypi registry for pyproject.toml', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    vi.mocked(mockCore.validatePackage).mockResolvedValue({
      name: 'django',
      risk_level: 'SAFE',
      risk_score: 0.05,
      signals: [],
    });

    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('"django>=4.0"', '/test/pyproject.toml');
    const position = new Position(0, 3); // On "django"

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).not.toBeNull();
    expect(mockCore.validatePackage).toHaveBeenCalledWith('django', 'pypi');
  });
});

describe('TOML Comment Detection', () => {
  it('returns null for TOML comment lines', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('# This is a TOML comment\nflask = "2.0"', '/test/pyproject.toml');
    const position = new Position(0, 5); // On comment line

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).toBeNull();
  });

  it('isCommentLine returns true for TOML comments', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const tomlUri = Uri.file('/test/pyproject.toml');
    expect(provider.isCommentLine('# TOML comment', tomlUri)).toBe(true);
    expect(provider.isCommentLine('flask = "2.0"', tomlUri)).toBe(false);
  });

  it('returns null for Cargo.toml comment lines', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const document = createMockDocument('# Comment in Cargo.toml', '/test/Cargo.toml');
    const position = new Position(0, 5);

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).toBeNull();
  });
});

describe('Hover Cache', () => {
  it('updateCache stores risk info', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    const risk = {
      name: 'cached-pkg',
      risk_level: 'SAFE' as const,
      risk_score: 0.1,
      signals: [],
    };

    provider.updateCache('cached-pkg', risk);

    // Now hover should use cached value
    vi.mocked(mockCore.validatePackage).mockResolvedValue(null);

    const document = createMockDocument('cached-pkg==1.0', '/test/requirements.txt');
    const position = new Position(0, 5);

    const hover = await provider.provideHover(document as any, position, CancellationToken as any);

    expect(hover).not.toBeNull();
    expect(hover!.contents.value).toContain('cached-pkg');
    // validatePackage should not be called because we used cache
    expect(mockCore.validatePackage).not.toHaveBeenCalled();
  });

  it('clearCache removes all cached entries', async () => {
    const { PhantomGuardHoverProvider } = await import('../src/hover');
    const { PhantomGuardCore } = await import('../src/core');

    const mockCore = new PhantomGuardCore();
    const provider = new PhantomGuardHoverProvider(mockCore);

    provider.updateCache('pkg1', { name: 'pkg1', risk_level: 'SAFE', risk_score: 0.1, signals: [] });
    provider.clearCache();

    // After clearing, validatePackage should be called
    vi.mocked(mockCore.validatePackage).mockResolvedValue(null);

    const document = createMockDocument('pkg1==1.0', '/test/requirements.txt');
    const position = new Position(0, 2);

    await provider.provideHover(document as any, position, CancellationToken as any);

    expect(mockCore.validatePackage).toHaveBeenCalled();
  });
});
