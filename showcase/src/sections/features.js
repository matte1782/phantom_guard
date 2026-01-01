/**
 * Features Section - "How It Works"
 *
 * Premium feature cards with scroll-triggered GSAP animations.
 * Uses ScrollTrigger for reveal animations and stagger effects.
 */

import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { logger } from '../utils/logger.js';

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

// Feature data with icons and descriptions
const FEATURES = [
  {
    id: 'detect',
    icon: 'shield-check',
    title: 'Detect Phantom Packages',
    description: 'Identify packages that exist only in AI hallucinations. Our detection engine checks real registries in milliseconds.',
    stat: '<200ms',
    statLabel: 'Detection Time'
  },
  {
    id: 'typosquat',
    icon: 'type',
    title: 'Catch Typosquats',
    description: 'Levenshtein distance analysis catches subtle misspellings that attackers use to hijack your installs.',
    stat: '2-char',
    statLabel: 'Edit Distance'
  },
  {
    id: 'patterns',
    icon: 'cpu',
    title: 'AI Pattern Recognition',
    description: 'Detects naming patterns that LLMs commonly hallucinate: *-gpt-*, *-ai-*, langchain-*-* and more.',
    stat: '15+',
    statLabel: 'Patterns'
  },
  {
    id: 'registry',
    icon: 'database',
    title: 'Multi-Registry Support',
    description: 'Validate packages across PyPI, npm, and Cargo. One tool for your entire polyglot stack.',
    stat: '3',
    statLabel: 'Registries'
  },
  {
    id: 'cicd',
    icon: 'git-branch',
    title: 'CI/CD Integration',
    description: 'Pre-commit hooks, GitHub Actions, and GitLab CI. Block phantom packages before they reach production.',
    stat: '100%',
    statLabel: 'Automated'
  },
  {
    id: 'cache',
    icon: 'zap',
    title: 'Smart Caching',
    description: 'LRU cache with TTL ensures lightning-fast repeated lookups. Batch validation for large projects.',
    stat: '<10ms',
    statLabel: 'Cached Response'
  }
];

// SVG Icons
const ICONS = {
  'shield-check': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <path d="m9 12 2 2 4-4"/>
  </svg>`,
  'type': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="4 7 4 4 20 4 20 7"/>
    <line x1="9" y1="20" x2="15" y2="20"/>
    <line x1="12" y1="4" x2="12" y2="20"/>
  </svg>`,
  'cpu': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
    <rect x="9" y="9" width="6" height="6"/>
    <line x1="9" y1="1" x2="9" y2="4"/>
    <line x1="15" y1="1" x2="15" y2="4"/>
    <line x1="9" y1="20" x2="9" y2="23"/>
    <line x1="15" y1="20" x2="15" y2="23"/>
    <line x1="20" y1="9" x2="23" y2="9"/>
    <line x1="20" y1="14" x2="23" y2="14"/>
    <line x1="1" y1="9" x2="4" y2="9"/>
    <line x1="1" y1="14" x2="4" y2="14"/>
  </svg>`,
  'database': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3"/>
    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
  </svg>`,
  'git-branch': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="6" y1="3" x2="6" y2="15"/>
    <circle cx="18" cy="6" r="3"/>
    <circle cx="6" cy="18" r="3"/>
    <path d="M18 9a9 9 0 0 1-9 9"/>
  </svg>`,
  'zap': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
  </svg>`
};

/**
 * Creates the features section HTML
 */
export function createFeaturesSection() {
  return `
    <div class="features-container">
      <!-- Section Header -->
      <div class="features-header">
        <span class="section-eyebrow">Capabilities</span>
        <h2 class="section-title">How It Works</h2>
        <p class="section-subtitle">
          Multi-layered protection against supply chain attacks.
          Every package validated before it can harm your project.
        </p>
      </div>

      <!-- Features Grid -->
      <div class="features-grid">
        ${FEATURES.map((feature, index) => `
          <article class="feature-card" data-feature="${feature.id}" data-index="${index}">
            <div class="feature-card__glow"></div>
            <div class="feature-card__content">
              <div class="feature-card__icon">
                ${ICONS[feature.icon]}
              </div>
              <h3 class="feature-card__title">${feature.title}</h3>
              <p class="feature-card__description">${feature.description}</p>
              <div class="feature-card__stat">
                <span class="stat-value">${feature.stat}</span>
                <span class="stat-label">${feature.statLabel}</span>
              </div>
            </div>
            <div class="feature-card__border"></div>
          </article>
        `).join('')}
      </div>

      <!-- Floating Connector Lines (decorative) -->
      <div class="features-connectors" aria-hidden="true">
        <svg class="connector-svg" viewBox="0 0 1200 400" preserveAspectRatio="none">
          <defs>
            <linearGradient id="connector-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="rgba(203, 166, 247, 0)" />
              <stop offset="50%" stop-color="rgba(203, 166, 247, 0.3)" />
              <stop offset="100%" stop-color="rgba(203, 166, 247, 0)" />
            </linearGradient>
          </defs>
          <path class="connector-line" d="M0,200 Q300,100 600,200 T1200,200" fill="none" stroke="url(#connector-gradient)" stroke-width="1"/>
        </svg>
      </div>
    </div>
  `;
}

/**
 * Initialize features section animations
 */
export function initFeaturesSection() {
  const cards = gsap.utils.toArray('.feature-card');
  const header = document.querySelector('.features-header');

  // Header reveal animation
  if (header) {
    gsap.fromTo(header.children,
      {
        opacity: 0,
        y: 40
      },
      {
        opacity: 1,
        y: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: header,
          start: 'top 80%',
          toggleActions: 'play none none reverse'
        }
      }
    );
  }

  // Card reveal animations with stagger
  cards.forEach((card, index) => {
    // Initial state
    gsap.set(card, {
      opacity: 0,
      y: 60,
      scale: 0.95
    });

    // Create individual ScrollTrigger for each card
    ScrollTrigger.create({
      trigger: card,
      start: 'top 85%',
      onEnter: () => {
        gsap.to(card, {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.7,
          delay: (index % 3) * 0.1, // Stagger within row
          ease: 'power3.out'
        });
      },
      onLeaveBack: () => {
        gsap.to(card, {
          opacity: 0,
          y: 60,
          scale: 0.95,
          duration: 0.4,
          ease: 'power2.in'
        });
      }
    });

    // Hover animation for glow effect
    const glow = card.querySelector('.feature-card__glow');
    const icon = card.querySelector('.feature-card__icon');

    card.addEventListener('mouseenter', () => {
      gsap.to(glow, {
        opacity: 1,
        duration: 0.3,
        ease: 'power2.out'
      });
      gsap.to(icon, {
        scale: 1.1,
        rotate: 5,
        duration: 0.4,
        ease: 'power2.out'
      });
      gsap.to(card, {
        y: -8,
        duration: 0.3,
        ease: 'power2.out'
      });
    });

    card.addEventListener('mouseleave', () => {
      gsap.to(glow, {
        opacity: 0,
        duration: 0.3,
        ease: 'power2.in'
      });
      gsap.to(icon, {
        scale: 1,
        rotate: 0,
        duration: 0.4,
        ease: 'power2.out'
      });
      gsap.to(card, {
        y: 0,
        duration: 0.3,
        ease: 'power2.out'
      });
    });
  });

  // Animate stat counters when visible
  const statValues = gsap.utils.toArray('.stat-value');
  statValues.forEach((stat) => {
    const value = stat.textContent;

    // Only animate numeric values
    if (/^\d+/.test(value)) {
      const numericPart = parseInt(value);
      const suffix = value.replace(/^\d+/, '');

      ScrollTrigger.create({
        trigger: stat,
        start: 'top 90%',
        once: true,
        onEnter: () => {
          gsap.fromTo(stat,
            { textContent: '0' + suffix },
            {
              textContent: numericPart + suffix,
              duration: 1.5,
              ease: 'power2.out',
              snap: { textContent: 1 },
              onUpdate: function() {
                const current = Math.round(gsap.getProperty(this.targets()[0], 'textContent'));
                stat.textContent = current + suffix;
              }
            }
          );
        }
      });
    }
  });

  // Connector line animation
  const connectorLine = document.querySelector('.connector-line');
  if (connectorLine) {
    const length = connectorLine.getTotalLength();
    gsap.set(connectorLine, {
      strokeDasharray: length,
      strokeDashoffset: length
    });

    ScrollTrigger.create({
      trigger: '.features-grid',
      start: 'top 60%',
      end: 'bottom 40%',
      scrub: 1,
      onUpdate: (self) => {
        gsap.set(connectorLine, {
          strokeDashoffset: length * (1 - self.progress)
        });
      }
    });
  }

  logger.log('[Features] Section initialized with ScrollTrigger animations');
}
