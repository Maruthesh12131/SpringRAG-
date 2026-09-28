import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl = env.VITE_BACKEND_URL || 'http://localhost:8080'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      // Proxy API calls to Spring Boot so the browser sees a same-origin
      // request and no CORS configuration is needed on the backend.
      proxy: {
        '/api': { target: backendUrl, changeOrigin: true },
      },
    },
  }
})
