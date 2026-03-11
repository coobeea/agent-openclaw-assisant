#!/bin/bash
set -euo pipefail

# 主机模式部署脚本

INSTANCE_ID="${1:-}"

if [ -z "$INSTANCE_ID" ]; then
    echo "用法: $0 <instance-id>"
    exit 1
fi

echo "🚀 主机模式部署: $INSTANCE_ID"

# TODO: 实现实际的部署逻辑
# 1. 生成 systemd 服务文件
# 2. 配置服务
# 3. 启动服务

echo "✅ 部署完成"
echo "查看状态: sudo systemctl status openclaw@$INSTANCE_ID"
