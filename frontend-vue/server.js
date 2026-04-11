const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = 80;

// API 代理 - 专门优化 SSE 流式传输
app.use('/api', createProxyMiddleware({
  target: 'http://openclaw-scheduler:8080',
  changeOrigin: true,
  ws: true,
  pathRewrite: {
    '^/api': '/api'
  },
  // 关键：禁用所有缓冲，确保流式传输
  selfHandleResponse: false,
  buffer: null,
  onProxyReq: (proxyReq, req) => {
    // SSE 请求头
    proxyReq.setHeader('Accept', 'text/event-stream');
    proxyReq.setHeader('Cache-Control', 'no-cache');
    proxyReq.setHeader('Connection', 'keep-alive');
    proxyReq.setHeader('X-Accel-Buffering', 'no');
    console.log(`[Proxy] ${req.method} ${req.url}`);
  },
  onProxyRes: (proxyRes, req, res) => {
    // 强制设置 SSE 响应头
    proxyRes.headers['content-type'] = 'text/event-stream';
    proxyRes.headers['cache-control'] = 'no-cache';
    proxyRes.headers['connection'] = 'keep-alive';
    proxyRes.headers['x-accel-buffering'] = 'no';
    delete proxyRes.headers['content-length']; // SSE 不应该有 content-length
    
    console.log(`[Proxy] Response: ${proxyRes.statusCode} - ${req.url}`);
    console.log(`[Proxy] Content-Type: ${proxyRes.headers['content-type']}`);
  },
  logLevel: 'debug'
}));

// 静态文件服务
app.use(express.static(path.join(__dirname, 'dist')));

// SPA fallback - 必须放在最后
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ 前端服务启动在端口 ${PORT}`);
  console.log(`📡 API 代理: /api -> http://openclaw-scheduler:8080`);
});
