import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  root: path.resolve(__dirname, 'frontend'),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'frontend'),
      '~backend/client': path.resolve(__dirname, 'frontend/client'),
      '~backend': path.resolve(__dirname, 'backend'),
    },
  },
  plugins: [tailwindcss(), react()],
  mode: "development",
  build: {
    minify: false,
  }
})
