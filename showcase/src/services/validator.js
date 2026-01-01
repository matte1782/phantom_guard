/**
 * Mock Validator Service
 *
 * Simulates the phantom-guard API with realistic responses.
 * Includes artificial delay to show loading states.
 */

// Known safe packages (popular ones)
const SAFE_PACKAGES = new Set([
  'flask', 'django', 'requests', 'numpy', 'pandas', 'react', 'vue', 'angular',
  'express', 'lodash', 'axios', 'moment', 'typescript', 'webpack', 'babel',
  'pytest', 'black', 'mypy', 'ruff', 'fastapi', 'sqlalchemy', 'celery',
  'redis', 'pillow', 'scipy', 'matplotlib', 'seaborn', 'tensorflow', 'pytorch',
  'serde', 'tokio', 'actix-web', 'rocket', 'clap', 'reqwest', 'hyper'
]);

// Known typosquats and their targets
const TYPOSQUATS = {
  'reqeusts': 'requests',
  'requets': 'requests',
  'reqests': 'requests',
  'requestes': 'requests',
  'flaks': 'flask',
  'flaask': 'flask',
  'djang': 'django',
  'dajngo': 'django',
  'numppy': 'numpy',
  'pandsa': 'pandas',
  'recat': 'react',
  'raect': 'react',
  'lodasch': 'lodash',
  'axois': 'axios',
  'axio': 'axios'
};

// AI-related suffixes that trigger hallucination detection
const AI_SUFFIXES = [
  '-gpt', '-ai', '-llm', '-openai', '-chatgpt', '-claude', '-copilot',
  '-assistant', '-helper', '-agent', '-ml', '-neural', '-transformer'
];

// Hallucination patterns
const HALLUCINATION_PATTERNS = [
  /^[a-z]+-gpt-[a-z]+$/,
  /^[a-z]+-ai-[a-z]+$/,
  /^gpt-[a-z]+-[a-z]+$/,
  /^ai-[a-z]+-helper$/,
  /^[a-z]+-llm-utils$/,
  /^langchain-[a-z]+-[a-z]+$/
];

/**
 * Calculate Levenshtein distance between two strings
 */
function levenshteinDistance(a, b) {
  const matrix = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Find closest match in safe packages
 */
function findClosestMatch(name) {
  let closest = null;
  let minDistance = Infinity;

  for (const pkg of SAFE_PACKAGES) {
    const distance = levenshteinDistance(name.toLowerCase(), pkg);
    if (distance < minDistance && distance <= 2) {
      minDistance = distance;
      closest = pkg;
    }
  }

  return closest ? { name: closest, distance: minDistance } : null;
}

/**
 * Check if name has AI-related suffix
 */
function hasAISuffix(name) {
  const lower = name.toLowerCase();
  return AI_SUFFIXES.find(suffix => lower.endsWith(suffix));
}

/**
 * Check if name matches hallucination pattern
 */
function matchesHallucinationPattern(name) {
  const lower = name.toLowerCase();
  return HALLUCINATION_PATTERNS.some(pattern => pattern.test(lower));
}

/**
 * Generate realistic validation response
 */
function generateResponse(packageName, registry) {
  const name = packageName.toLowerCase().trim();
  const signals = [];
  let riskScore = 0;

  // Check if it's a known safe package
  if (SAFE_PACKAGES.has(name)) {
    return {
      package: name,
      registry,
      risk_level: 'SAFE',
      risk_score: 0.02 + Math.random() * 0.03,
      signals: [
        {
          type: 'EXISTS',
          severity: 'info',
          message: `Package exists on ${registry}`,
          icon: 'check-circle'
        },
        {
          type: 'POPULAR',
          severity: 'info',
          message: 'Package is in top 1000 most downloaded',
          icon: 'check-circle'
        }
      ],
      recommendation: 'ALLOW',
      validation_time_ms: 80 + Math.floor(Math.random() * 60)
    };
  }

  // Check for known typosquats
  if (TYPOSQUATS[name]) {
    const target = TYPOSQUATS[name];
    signals.push({
      type: 'TYPOSQUAT',
      severity: 'high',
      message: `Typosquat of "${target}" (edit distance: 1)`,
      icon: 'alert-triangle',
      details: { target, distance: 1 }
    });
    riskScore += 0.45;
  }

  // Check for similar names to popular packages
  const closestMatch = findClosestMatch(name);
  if (closestMatch && !TYPOSQUATS[name]) {
    signals.push({
      type: 'SIMILAR_NAME',
      severity: closestMatch.distance === 1 ? 'high' : 'medium',
      message: `Similar to "${closestMatch.name}" (edit distance: ${closestMatch.distance})`,
      icon: 'alert-triangle',
      details: closestMatch
    });
    riskScore += closestMatch.distance === 1 ? 0.3 : 0.15;
  }

  // Check for AI suffixes
  const aiSuffix = hasAISuffix(name);
  if (aiSuffix) {
    signals.push({
      type: 'AI_SUFFIX',
      severity: 'medium',
      message: `AI-related suffix detected ("${aiSuffix}")`,
      icon: 'zap'
    });
    riskScore += 0.2;
  }

  // Check for hallucination patterns
  if (matchesHallucinationPattern(name)) {
    signals.push({
      type: 'HALLUCINATION_PATTERN',
      severity: 'high',
      message: 'Matches known LLM hallucination pattern',
      icon: 'alert-triangle'
    });
    riskScore += 0.25;
  }

  // Package doesn't exist (simulated)
  if (!SAFE_PACKAGES.has(name)) {
    signals.push({
      type: 'NOT_FOUND',
      severity: 'high',
      message: `Package not found on ${registry}`,
      icon: 'x-circle'
    });
    riskScore += 0.3;
  }

  // Clamp risk score
  riskScore = Math.min(0.99, riskScore);

  // Determine risk level
  let riskLevel = 'SAFE';
  let recommendation = 'ALLOW';

  if (riskScore >= 0.7) {
    riskLevel = 'HIGH_RISK';
    recommendation = 'BLOCK';
  } else if (riskScore >= 0.4) {
    riskLevel = 'SUSPICIOUS';
    recommendation = 'WARN';
  } else if (riskScore >= 0.2) {
    riskLevel = 'UNKNOWN';
    recommendation = 'REVIEW';
  }

  return {
    package: name,
    registry,
    risk_level: riskLevel,
    risk_score: riskScore,
    signals,
    recommendation,
    validation_time_ms: 120 + Math.floor(Math.random() * 80)
  };
}

/**
 * Validate a package name
 * @param {string} packageName - Package name to validate
 * @param {string} registry - Registry (pypi, npm, crates)
 * @returns {Promise<object>} Validation result
 */
export async function validatePackage(packageName, registry = 'pypi') {
  // Simulate network delay (100-250ms)
  const delay = 100 + Math.floor(Math.random() * 150);
  await new Promise(resolve => setTimeout(resolve, delay));

  if (!packageName || packageName.trim().length === 0) {
    throw new Error('Package name is required');
  }

  if (packageName.length > 100) {
    throw new Error('Package name too long');
  }

  return generateResponse(packageName, registry);
}

/**
 * Get example packages for demo purposes
 */
export function getExamplePackages() {
  return [
    { name: 'flask', description: 'Safe - Popular package', expected: 'SAFE' },
    { name: 'reqeusts', description: 'Typosquat of requests', expected: 'HIGH_RISK' },
    { name: 'flask-gpt-helper', description: 'AI hallucination pattern', expected: 'HIGH_RISK' },
    { name: 'pandas-ai-utils', description: 'Suspicious AI suffix', expected: 'SUSPICIOUS' },
    { name: 'my-cool-package', description: 'Unknown package', expected: 'UNKNOWN' }
  ];
}
