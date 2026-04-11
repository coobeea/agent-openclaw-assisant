#!/bin/bash

# OpenClaw 服务启动脚本

echo "🚀 启动 OpenClaw 服务..."
echo ""

# 检查 K8s 是否运行
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes 未运行，请先启动 Docker Desktop K8s"
    exit 1
fi

echo "✅ Kubernetes 集群已就绪"
echo ""

# 创建命名空间
kubectl create namespace openclaw 2>/dev/null || echo "✅ 命名空间 openclaw 已存在"
echo ""

# 部署基础设施
echo "📦 部署基础设施..."
kubectl apply -f k8s-manifests/01-postgres.yaml
kubectl apply -f k8s-manifests/02-redis.yaml
kubectl apply -f k8s-manifests/03-minio.yaml
echo ""

# 等待基础设施就绪
echo "⏳ 等待基础设施启动（30秒）..."
sleep 30

# 部署 OpenClaw 容器池
echo "🐚 部署 OpenClaw 容器池..."
kubectl apply -f k8s-manifests/04-openclaw-pool.yaml
echo ""

# 等待容器池就绪
echo "⏳ 等待容器池启动（30秒）..."
sleep 30

# 部署调度服务
echo "🎯 部署调度服务..."
kubectl apply -f k8s-manifests/05-scheduler-service.yaml
echo ""

# 等待调度服务就绪
echo "⏳ 等待调度服务启动（20秒）..."
sleep 20

# 检查状态
echo ""
echo "📊 服务状态："
kubectl get pods -n openclaw

echo ""
echo "🌐 服务地址："
kubectl get svc -n openclaw

echo ""
echo "🧪 健康检查："
curl -s http://localhost:30080/health | jq . || echo "等待服务就绪..."

echo ""
echo "✅ 启动完成！"
echo ""
echo "📍 访问地址："
echo "  - API 服务: http://localhost:30080"
echo "  - 健康检查: http://localhost:30080/health"
echo "  - 系统状态: http://localhost:30080/api/status"
echo ""
echo "🧪 运行测试："
echo "  ./test-api.sh"
echo ""
