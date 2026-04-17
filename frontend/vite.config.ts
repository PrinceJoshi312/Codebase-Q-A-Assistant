import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/ingest': 'http://127.0.0.1:8000',
      '/structure': 'http://127.0.0.1:8000',
      '/chat': 'http://127.0.0.1:8000'
    }
  }
})
