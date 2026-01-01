/**
 * Terminal Demo Animation
 *
 * Uses GSAP to create a typing animation that demonstrates Phantom Guard
 * detecting a suspicious package (flask-gpt-helper).
 *
 * [HOSTILE FIX] All GSAP animations target Shadow DOM elements directly.
 * Standard CSS selectors like '#line-1' won't work inside Shadow DOM.
 * Solution: Cache all element references from shadowRoot before animating.
 */

import gsap from 'gsap';

export function animateTerminalDemo(terminal) {
  const shadow = terminal.shadowRoot;
  if (!shadow) {
    console.error('[Terminal Animation] No shadowRoot found');
    return null;
  }

  const command = 'phantom-guard validate flask-gpt-helper';

  // [HOSTILE FIX] Cache all Shadow DOM element references
  const elements = {
    line1: shadow.querySelector('#line-1'),
    line2: shadow.querySelector('#line-2'),
    line3: shadow.querySelector('#line-3'),
    line4: shadow.querySelector('#line-4'),
    line5: shadow.querySelector('#line-5'),
    line6: shadow.querySelector('#line-6'),
    command: shadow.querySelector('#command'),
    cursor: shadow.querySelector('#cursor'),
    progressFill: shadow.querySelector('#progress-fill'),
    progress: shadow.querySelector('#progress'),
  };

  // Verify all elements exist
  const missingElements = Object.entries(elements)
    .filter(([, el]) => !el)
    .map(([name]) => name);

  if (missingElements.length > 0) {
    console.error('[Terminal Animation] Missing elements:', missingElements);
    return null;
  }

  const lines = [
    { el: elements.line2, text: '<span class="spinner">⠋</span> Checking PyPI...', delay: 0.8 },
    { el: elements.line3, text: '<span class="error">✗</span> Package not found on PyPI', delay: 1.3 },
    { el: elements.line4, text: '<span class="warning">⚠</span> Matches hallucination pattern', delay: 1.6 },
    { el: elements.line5, text: '<span class="warning">⚠</span> AI-related suffix detected', delay: 1.9 },
  ];

  // Create timeline with infinite loop
  const tl = gsap.timeline({ repeat: -1, repeatDelay: 3 });

  // Track state for reset
  let charIndex = 0;
  let timingLabel = null;

  // [HOSTILE FIX] Use element reference, not CSS selector
  tl.to(elements.line1, { opacity: 1, y: 0, duration: 0.3 });

  // Type command character by character
  tl.to({}, {
    duration: command.length * 0.05,
    onUpdate: function() {
      const progress = this.progress();
      const chars = Math.floor(progress * command.length);
      if (chars > charIndex) {
        charIndex = chars;
        elements.command.textContent = command.slice(0, charIndex);
      }
    }
  });

  // Hide cursor after typing
  tl.to(elements.cursor, { opacity: 0, duration: 0.1 });

  // [HOSTILE FIX] Use element references for all output lines
  lines.forEach(({ el, text, delay }) => {
    tl.to(el, {
      opacity: 1,
      y: 0,
      duration: 0.3,
      onStart: () => {
        el.innerHTML = text;
      }
    }, delay);
  });

  // Show result with risk badge - [HOSTILE FIX] use element reference
  tl.to(elements.line6, {
    opacity: 1,
    y: 0,
    duration: 0.3,
    onStart: () => {
      elements.line6.innerHTML = `
        <span class="error">flask-gpt-helper</span>
        <span class="risk-badge high-risk">HIGH_RISK</span>
        <span class="info">[0.82]</span>
      `;
    }
  }, 2.2);

  // [HOSTILE FIX] Use element reference for progress bar
  tl.to(elements.progressFill, { width: '100%', duration: 0.3 }, 2.5);

  // Add timing label
  tl.to({}, {
    duration: 0.1,
    onComplete: () => {
      timingLabel = document.createElement('div');
      timingLabel.className = 'timing-label';
      timingLabel.textContent = '━━━━━━━━━━━━━━━━━━━━━━ 147ms';
      elements.progress.after(timingLabel);
    }
  }, 2.8);

  // Hold for viewing
  tl.to({}, { duration: 2 });

  // Reset for loop
  tl.to({}, {
    duration: 0.5,
    onComplete: () => {
      // Reset character index
      charIndex = 0;
      elements.command.textContent = '';

      // Reset cursor
      gsap.set(elements.cursor, { opacity: 1 });

      // Reset all lines
      [elements.line1, elements.line2, elements.line3, elements.line4, elements.line5, elements.line6].forEach((el, i) => {
        gsap.set(el, { opacity: 0, y: 10 });
        if (i > 0) el.innerHTML = '';
      });

      // Reset progress bar
      gsap.set(elements.progressFill, { width: 0 });

      // Remove timing label
      if (timingLabel) {
        timingLabel.remove();
        timingLabel = null;
      }
    }
  });

  return tl;
}
