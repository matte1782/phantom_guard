/**
 * Debug Logger Utility
 *
 * Only outputs logs in development mode.
 * Tree-shaken out in production builds.
 */

const isDev = import.meta.env.DEV;

export const logger = {
  log: (...args) => {
    if (isDev) console.log(...args);
  },
  warn: (...args) => {
    if (isDev) console.warn(...args);
  },
  error: (...args) => {
    // Always log errors, even in production
    console.error(...args);
  }
};
