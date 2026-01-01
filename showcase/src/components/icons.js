/**
 * Icon System for Phantom Guard Showcase
 *
 * Uses SVG sprite sheet loaded into the document.
 * Icons can be referenced with <svg class="icon"><use href="#icon-name"/></svg>
 */

import { logger } from '../utils/logger.js';

// Load SVG sprite into document
export async function loadIcons() {
  try {
    // [HOSTILE FIX] Use BASE_URL for GitHub Pages compatibility
    const response = await fetch(import.meta.env.BASE_URL + 'icons.svg');
    if (!response.ok) {
      throw new Error(`Failed to load icons: ${response.status}`);
    }
    const svgText = await response.text();
    const container = document.createElement('div');
    container.innerHTML = svgText;
    container.style.display = 'none';
    container.setAttribute('aria-hidden', 'true');
    document.body.insertBefore(container, document.body.firstChild);
    logger.log('[Icons] SVG sprite loaded successfully');
  } catch (error) {
    logger.error('[Icons] Failed to load SVG sprite:', error);
  }
}

// Create icon element as HTML string
export function icon(name, className = '') {
  return `<svg class="icon ${className}" aria-hidden="true"><use href="#${name}"/></svg>`;
}

// Create icon element as DOM node
export function createIconElement(name, className = '') {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.classList.add('icon');
  if (className) {
    className.split(' ').forEach(c => svg.classList.add(c));
  }
  svg.setAttribute('aria-hidden', 'true');

  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
  use.setAttribute('href', `#${name}`);
  svg.appendChild(use);

  return svg;
}
