import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Позволява връзки отвън (Windows)
    port: 3000,      // Форсира порт 3000
    watch: {
      usePolling: true, // Нужно за WSL2
    },
  },
})