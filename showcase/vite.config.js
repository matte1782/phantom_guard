import { defineConfig } from 'vite';

export default defineConfig({
  base: '/phantom-guard/',  // For GitHub Pages
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    minify: 'esbuild',  // Use esbuild (default, faster)
    target: 'es2020',
  },
  esbuild: {
    drop: ['console', 'debugger'],  // Remove console/debugger in production
  },
  server: {
    port: 5173,
    open: true,
  },
  json: {
    stringify: false, // Allow importing package.json for version
  },
});
