#!/bin/bash
set -euo pipefail

# Docker 模式部署脚本

INSTANCE_ID="${1:-}"

if [ -z "$INSTANCE_ID" ]; then
    echo "用法: $0 <instance-id>"
    exit 1
fi

echo "🐳 Docker 模式部署: $INSTANCE_ID"

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
TEMPLATES_DIR="${PROJECT_ROOT}/skills/openclaw-deploy/templates"
WORKSPACE_PATH="${PROJECT_ROOT}/workspace/lobsters/${INSTANCE_ID}"

# 检查实例是否存在
if [ ! -d "$WORKSPACE_PATH" ]; then
    echo "❌ 实例工作空间不存在: $WORKSPACE_PATH"
    echo "请先使用 instance_manager.py create 创建实例"
    exit 1
fi

# 从 agents.jsonl 中获取端口
AGENTS_DB="${PROJECT_ROOT}/workspace/data/agents.jsonl"
PORT=3000
if [ -f "$AGENTS_DB" ]; then
    # 简单的 grep 和 awk 提取端口
    FOUND_PORT=$(grep "\"id\": \"$INSTANCE_ID\"" "$AGENTS_DB" | grep -o '"gateway_port": [0-9]*' | awk '{print $2}')
    if [ -n "$FOUND_PORT" ]; then
        PORT=$FOUND_PORT
    fi
fi

echo "📋 实例信息:"
echo "  - ID: $INSTANCE_ID"
echo "  - 端口: $PORT"
echo "  - 工作空间: $WORKSPACE_PATH"

# 导出环境变量供 docker-compose 使用
export INSTANCE_ID=$INSTANCE_ID
export PORT=$PORT
export WORKSPACE_PATH=$WORKSPACE_PATH
export PROJECT_ROOT=$PROJECT_ROOT

# 切换到模板目录执行 docker-compose
cd "$TEMPLATES_DIR"

echo "🚀 构建并启动容器..."
docker-compose up -d --build

echo "✅ 部署完成"
echo "查看状态: docker ps | grep $INSTANCE_ID"
echo "查看日志: docker logs -f $INSTANCE_ID"

