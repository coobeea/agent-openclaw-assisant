#!/bin/bash

# Vue3 前端启动脚本

echo "🚀 启动 Vue3 前端服务..."
echo ""

cd frontend-vue

# 检查依赖是否安装
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
    echo ""
fi

# 启动开发服务器
echo "🌐 启动 Vite 开发服务器..."
npm run dev

# 注意：这个脚本会阻塞终端
# 如果需要后台运行，使用：npm run dev > /tmp/frontend.log 2>&1 &
