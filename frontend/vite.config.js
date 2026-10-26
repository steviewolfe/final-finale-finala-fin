import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// In development, /api requests go to the FastAPI server on port 8000.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
