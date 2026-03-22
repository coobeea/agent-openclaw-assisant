#!/bin/bash
set -e

echo "Starting OpenClaw with Nginx proxy..."

# Start Nginx
echo "Starting Nginx..."
nginx -c /etc/nginx/nginx.conf

# Wait for Nginx
sleep 2

# Start OpenClaw (listening on 127.0.0.1:3000)
echo "Starting OpenClaw..."

# 创建调试文件并设置权限
touch /tmp/debug-openclaw.log
chmod 666 /tmp/debug-openclaw.log
echo "[STARTUP] $(date) - OpenClaw starting" > /tmp/debug-openclaw.log

exec node /usr/local/lib/node_modules/openclaw/dist/entry.js gateway --port 3000
