import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/sip': 'http://localhost:8000',
      '/api': 'http://localhost:8000',
      '/gsm': 'http://localhost:8000',
      '/upload_sa': 'http://localhost:8000',
    },
  },
  build: {
    outDir: 'dist',
  },
})
