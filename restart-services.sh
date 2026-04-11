#!/bin/bash

# OpenClaw 服务重启脚本

echo "🔄 重启 OpenClaw 服务..."
echo ""

# 先停止
./stop-services.sh

echo ""
echo "⏳ 等待清理完成（5秒）..."
sleep 5

# 再启动
./start-services.sh
