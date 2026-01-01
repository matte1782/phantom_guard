/**
 * Performance Section
 *
 * Showcases Phantom Guard's speed and efficiency with animated metrics.
 * Features GSAP-powered number counters and comparison bars.
 */

import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { logger } from '../utils/logger.js';

gsap.registerPlugin(ScrollTrigger);

// Performance metrics data
const METRICS = [
  {
    id: 'cached',
    label: 'Cached Response',
    value: 8,
    unit: 'ms',
    comparison: 'vs 200ms uncached',
    percentage: 4,
    description: 'Lightning-fast repeated lookups with smart LRU caching'
  },
  {
    id: 'uncached',
    label: 'Fresh Validation',
    value: 180,
    unit: 'ms',
    comparison: 'P99 latency',
    percentage: 90,
    description: 'Real-time registry checks with parallel requests'
  },
  {
    id: 'batch',
    label: 'Batch (50 packages)',
    value: 3.2,
    unit: 's',
    comparison: 'concurrent processing',
    percentage: 64,
    description: 'Validate entire requirements.txt in seconds'
  }
];

// Comparison data for visual bars
const COMPARISONS = [
  {
    label: 'Phantom Guard',
    time: 180,
    color: 'var(--color-green)',
    highlight: true
  },
  {
    label: 'Manual Check',
    time: 5000,
    color: 'var(--color-subtext)',
    highlight: false
  },
  {
    label: 'Basic Validator',
    time: 800,
    color: 'var(--color-subtext)',
    highlight: false
  }
];

/**
 * Creates the performance section HTML
 */
export function createPerformanceSection() {
  return `
    <div class="performance-container">
      <!-- Section Header -->
      <div class="performance-header">
        <span class="section-eyebrow">Speed</span>
        <h2 class="section-title">Built for Performance</h2>
        <p class="section-subtitle">
          Sub-200ms validation for production workloads.
          Every millisecond counts in your CI/CD pipeline.
        </p>
      </div>

      <!-- Metrics Grid -->
      <div class="metrics-grid">
        ${METRICS.map(metric => `
          <div class="metric-card" data-metric="${metric.id}">
            <div class="metric-card__header">
              <span class="metric-label">${metric.label}</span>
              <span class="metric-comparison">${metric.comparison}</span>
            </div>
            <div class="metric-card__value">
              <span class="metric-number" data-value="${metric.value}" data-unit="${metric.unit}">0</span>
              <span class="metric-unit">${metric.unit}</span>
            </div>
            <div class="metric-card__bar">
              <div class="metric-bar-fill" data-percentage="${metric.percentage}"></div>
            </div>
            <p class="metric-description">${metric.description}</p>
          </div>
        `).join('')}
      </div>

      <!-- Speed Comparison -->
      <div class="comparison-section">
        <h3 class="comparison-title">How We Compare</h3>
        <div class="comparison-bars">
          ${COMPARISONS.map(comp => `
            <div class="comparison-row ${comp.highlight ? 'comparison-row--highlight' : ''}">
              <span class="comparison-label">${comp.label}</span>
              <div class="comparison-bar-wrapper">
                <div class="comparison-bar"
                     data-time="${comp.time}"
                     style="--bar-color: ${comp.color}">
                </div>
                <span class="comparison-time">${comp.time >= 1000 ? (comp.time / 1000) + 's' : comp.time + 'ms'}</span>
              </div>
            </div>
          `).join('')}
        </div>
        <p class="comparison-note">
          * Based on single package validation to PyPI registry
        </p>
      </div>

      <!-- Code Example -->
      <div class="performance-code">
        <div class="code-header">
          <span class="code-filename">benchmark.py</span>
          <div class="code-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
        <pre class="code-content"><code><span class="code-comment"># Validate 50 packages in parallel</span>
<span class="code-keyword">from</span> phantom_guard <span class="code-keyword">import</span> validate_batch

packages = [<span class="code-string">"flask"</span>, <span class="code-string">"django"</span>, <span class="code-string">"requests"</span>, ...]  <span class="code-comment"># 50 packages</span>
results = <span class="code-keyword">await</span> validate_batch(packages)

<span class="code-comment"># Result: 50 packages validated in 3.2s</span>
<span class="code-comment"># 15 HIGH_RISK flagged, 2 typosquats detected</span></code></pre>
      </div>
    </div>
  `;
}

/**
 * Initialize performance section animations
 */
export function initPerformanceSection() {
  const section = document.querySelector('#performance');
  if (!section) return;

  const metricCards = gsap.utils.toArray('.metric-card');
  const comparisonRows = gsap.utils.toArray('.comparison-row');
  const codeBlock = document.querySelector('.performance-code');

  // Animate header
  const header = section.querySelector('.performance-header');
  if (header) {
    gsap.fromTo(header.children,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: 0.7,
        stagger: 0.12,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: header,
          start: 'top 80%'
        }
      }
    );
  }

  // Animate metric cards with number counting
  metricCards.forEach((card, index) => {
    const numberEl = card.querySelector('.metric-number');
    const barFill = card.querySelector('.metric-bar-fill');
    const value = parseFloat(numberEl.dataset.value);
    const percentage = parseInt(barFill.dataset.percentage);

    // Initial state
    gsap.set(card, { opacity: 0, y: 40, scale: 0.95 });
    gsap.set(barFill, { scaleX: 0, transformOrigin: 'left' });

    ScrollTrigger.create({
      trigger: card,
      start: 'top 85%',
      once: true,
      onEnter: () => {
        // Card entrance
        gsap.to(card, {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.6,
          delay: index * 0.15,
          ease: 'power3.out'
        });

        // Number counter animation
        gsap.to({ val: 0 }, {
          val: value,
          duration: 1.5,
          delay: index * 0.15 + 0.3,
          ease: 'power2.out',
          onUpdate: function() {
            const current = this.targets()[0].val;
            // Format based on whether it's a decimal
            if (value % 1 !== 0) {
              numberEl.textContent = current.toFixed(1);
            } else {
              numberEl.textContent = Math.round(current);
            }
          }
        });

        // Bar fill animation
        gsap.to(barFill, {
          scaleX: percentage / 100,
          duration: 1.2,
          delay: index * 0.15 + 0.4,
          ease: 'power2.out'
        });
      }
    });
  });

  // Animate comparison bars
  const maxTime = Math.max(...COMPARISONS.map(c => c.time));

  comparisonRows.forEach((row, index) => {
    const bar = row.querySelector('.comparison-bar');
    const time = parseInt(bar.dataset.time);
    const widthPercentage = (time / maxTime) * 100;

    gsap.set(bar, { width: 0 });

    ScrollTrigger.create({
      trigger: row,
      start: 'top 90%',
      once: true,
      onEnter: () => {
        gsap.to(bar, {
          width: `${widthPercentage}%`,
          duration: 1,
          delay: index * 0.2,
          ease: 'power2.out'
        });
      }
    });
  });

  // Animate code block
  if (codeBlock) {
    gsap.fromTo(codeBlock,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: codeBlock,
          start: 'top 85%'
        }
      }
    );

    // Typewriter effect for code lines
    const codeLines = codeBlock.querySelectorAll('code > *');
    codeLines.forEach((line, i) => {
      gsap.fromTo(line,
        { opacity: 0, x: -10 },
        {
          opacity: 1,
          x: 0,
          duration: 0.4,
          delay: i * 0.1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: codeBlock,
            start: 'top 80%'
          }
        }
      );
    });
  }

  logger.log('[Performance] Section initialized');
}
