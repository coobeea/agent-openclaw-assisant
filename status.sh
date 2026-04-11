#!/bin/bash

# OpenClaw 服务状态查看脚本

echo "╔══════════════════════════════════════════════════════╗"
echo "║         OpenClaw 服务状态                             ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# K8s 集群状态
echo "🌐 Kubernetes 集群："
if kubectl cluster-info &> /dev/null; then
    echo "  ✅ 运行正常"
else
    echo "  ❌ 未运行"
    exit 1
fi
echo ""

# Pod 状态
echo "📦 Pod 状态："
kubectl get pods -n openclaw -o wide
echo ""

# 服务状态
echo "🌐 服务状态："
kubectl get svc -n openclaw
echo ""

# 健康检查
echo "🧪 健康检查："
echo -n "  API 服务: "
if curl -s http://localhost:30080/health > /dev/null 2>&1; then
    echo "✅ 正常"
    curl -s http://localhost:30080/health | jq .
else
    echo "❌ 无法访问"
fi
echo ""

# 系统状态
echo "📊 系统状态："
curl -s http://localhost:30080/api/status 2>/dev/null | jq . || echo "  ❌ 无法获取"
echo ""

# 容器池状态
echo "🐚 容器池状态："
curl -s http://localhost:30080/api/containers/status 2>/dev/null | jq '.pods[] | {pod: .pod, status: .status, phase: .phase}' || echo "  ❌ 无法获取"
echo ""

# 数据目录
echo "📂 数据目录："
echo "  智能体: $(ls -1 workspace/lobsters/agents/ 2>/dev/null | wc -l) 个"
echo "  数据库: $(du -sh workspace/lobsters/database/ 2>/dev/null | cut -f1) (PostgreSQL)"
echo "  缓存: $(du -sh workspace/lobsters/cache/ 2>/dev/null | cut -f1) (Redis)"
echo "  存储: $(du -sh workspace/lobsters/storage/ 2>/dev/null | cut -f1) (MinIO)"
echo ""

echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "📍 快速访问："
echo "  - API: http://localhost:30080"
echo "  - 健康检查: curl http://localhost:30080/health"
echo "  - 系统状态: curl http://localhost:30080/api/status"
echo "  - 运行测试: ./test-api.sh"
echo ""
