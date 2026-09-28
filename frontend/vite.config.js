import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The Django project serves the built bundle from /static/auth/ and mounts it
// inside templates/auth.html, so output filenames are kept stable (unhashed)
// to let the template reference them directly.
export default defineConfig({
  plugins: [react()],
  base: '/static/auth/',
  build: {
    outDir: '../static/auth',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'auth.js',
        chunkFileNames: 'auth-[name].js',
        assetFileNames: 'auth.[ext]',
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
