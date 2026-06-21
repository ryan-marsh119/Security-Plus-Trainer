import { defineConfig } from 'vitest/config'

// The app relies on React's automatic JSX runtime (no `import React` anywhere).
// Configure esbuild to use it so component tests transform the same way the Vite
// build does. jsdom gives the React Testing Library tests a DOM; setup.js wires
// in jest-dom matchers.
export default defineConfig({
  esbuild: { jsx: 'automatic' },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    css: false,
  },
})
