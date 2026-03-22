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
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
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
    FOUND_PORT=$(grep "\"name\": \"$INSTANCE_ID\"" "$AGENTS_DB" | grep -o '"gateway_port": [0-9]*' | awk '{print $2}' || true)
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

# 配置 Docker 构建时的代理 (使用宿主机 IP)
# 获取宿主机 IP (macOS)
HOST_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")
export HTTP_PROXY=http://${HOST_IP}:7890
export HTTPS_PROXY=http://${HOST_IP}:7890
export NO_PROXY=localhost,127.0.0.1

# 确保 Nginx 配置和启动脚本存在
if [ ! -f "$TEMPLATES_DIR/nginx.conf" ]; then
    echo "❌ nginx.conf 不存在，请检查模板文件"
    exit 1
fi

if [ ! -f "$TEMPLATES_DIR/start-with-nginx.sh" ]; then
    echo "❌ start-with-nginx.sh 不存在，请检查模板文件"
    exit 1
fi

# 检查是否有本地源码，如果有，则使用源码构建
SOURCE_CODE_PATH="${PROJECT_ROOT}/workspace/source/openclaw"
if [ -d "$SOURCE_CODE_PATH" ]; then
    echo "🔧 发现本地源码，准备从源码构建..."
    
    # 复制源码到 templates 目录（作为 Docker 构建上下文）
    echo "📦 复制源码到构建目录..."
    rm -rf "$TEMPLATES_DIR/openclaw-source"
    cp -r "$SOURCE_CODE_PATH" "$TEMPLATES_DIR/openclaw-source"
    
    # 确保 dist 目录存在
    if [ ! -d "$TEMPLATES_DIR/openclaw-source/dist" ]; then
        echo "❌ 源码未构建，请先运行: cd $SOURCE_CODE_PATH && npm run build"
        exit 1
    fi
    
    echo "✅ 将使用本地源码版本: $(cat $TEMPLATES_DIR/openclaw-source/package.json | grep '"version"' | head -1)"
else
    echo "📦 使用 npm 版本"
    # 如果 openclaw-source 目录存在（上次遗留），删除它并修改 Dockerfile
    if [ -d "$TEMPLATES_DIR/openclaw-source" ]; then
        rm -rf "$TEMPLATES_DIR/openclaw-source"
    fi
fi

# 切换到模板目录执行 docker-compose
cd "$TEMPLATES_DIR"

echo "🚀 构建并启动容器..."
docker-compose up -d --build

# 修改配置文件端口为 3000（Docker 内部端口，由 Nginx 代理）
echo "📝 调整容器内部端口为 3000（Nginx 代理模式）..."
CONFIG_FILE="$WORKSPACE_PATH/.openclaw/openclaw.json"
if [ -f "$CONFIG_FILE" ]; then
    python3 -c "
import json
config_file = '$CONFIG_FILE'
with open(config_file, 'r') as f:
    config = json.load(f)
if 'gateway' in config:
    config['gateway']['port'] = 3000
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
"
fi

# 更新 agents.jsonl 中的 deploy_mode
if [ -f "$AGENTS_DB" ]; then
    echo "📝 更新实例部署模式为 docker..."
    # 使用 Python 脚本更新 JSONL 文件
    python3 -c "
import json
import sys

db_path = '$AGENTS_DB'
instance_id = '$INSTANCE_ID'

lines = []
with open(db_path, 'r') as f:
    lines = f.readlines()

with open(db_path, 'w') as f:
    for line in lines:
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            if data.get('id') == instance_id or data.get('name') == instance_id:
                data['deploy_mode'] = 'docker'
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except:
            f.write(line)
"
fi

echo "✅ 部署完成"
echo "查看状态: docker ps | grep $INSTANCE_ID"
echo "查看日志: docker logs -f $INSTANCE_ID"

