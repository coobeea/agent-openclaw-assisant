#!/bin/bash

# OpenClaw 服务停止脚本

echo "🛑 停止 OpenClaw 服务..."
echo ""

# 删除所有部署
echo "📦 停止调度服务..."
kubectl delete -f k8s-manifests/05-scheduler-service.yaml --ignore-not-found=true

echo "🐚 停止 OpenClaw 容器池..."
kubectl delete -f k8s-manifests/04-openclaw-pool.yaml --ignore-not-found=true

echo "📦 停止基础设施..."
kubectl delete -f k8s-manifests/03-minio.yaml --ignore-not-found=true
kubectl delete -f k8s-manifests/02-redis.yaml --ignore-not-found=true
kubectl delete -f k8s-manifests/01-postgres.yaml --ignore-not-found=true

echo ""
echo "⏳ 等待所有资源清理完成（10秒）..."
sleep 10

echo ""
echo "📊 剩余资源："
kubectl get pods -n openclaw

echo ""
echo "✅ 服务已停止！"
echo ""
echo "⚠️  数据仍保留在："
echo "  workspace/lobsters/database/"
echo "  workspace/lobsters/cache/"
echo "  workspace/lobsters/storage/"
echo "  workspace/lobsters/agents/"
echo ""
