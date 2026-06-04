import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// `base` is '/static/' for production builds so the combined Django image serves
// the hashed assets via whitenoise under /static/. In dev (command !== 'build')
// it stays '/' so the Vite dev server serves index.html and assets from the root.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/static/' : '/',
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
}))
