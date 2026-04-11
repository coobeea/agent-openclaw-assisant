import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:30080',
        changeOrigin: true,
        timeout: 300000,
        proxyTimeout: 300000,
        // 禁用代理缓冲，支持 SSE 流式输出
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 设置无缓冲
            proxyReq.setHeader('X-Accel-Buffering', 'no')
          })
        }
      }
    }
  }
})
