#!/bin/bash

echo "🧪 OpenClaw WebSocket 流式输出测试"
echo "===================================="
echo ""
echo "选择测试方法："
echo "1. 本地测试（需要端口转发）"
echo "2. K8s 内部测试（推荐✨）"
echo "3. 查看实时日志"
echo ""
read -p "请输入选项 (1/2/3): " choice

case $choice in
  1)
    echo ""
    echo "📍 本地测试模式"
    echo ""
    kubectl port-forward -n openclaw svc/openclaw-scheduler 8080:8080 > /tmp/pf.log 2>&1 &
    PF_PID=$!
    echo "✅ 端口转发已启动 (PID: $PF_PID)"
    sleep 5
    
    echo "🚀 开始测试..."
    curl -N -X POST http://localhost:8080/api/chat/stream \
      -H 'Content-Type: application/json' \
      -d '{"agent_id":"test-agent","message":"你好，用10个字回复"}' &
    
    read -p "按 Enter 停止..."
    kill $PF_PID 2>/dev/null
    ;;
    
  2)
    echo ""
    echo "🐳 K8s 内部测试（推荐）"
    echo ""
    kubectl run streaming-test-$(date +%s) --rm -i --restart=Never \
      --image=curlimages/curl:latest -n openclaw -- \
      curl -N -X POST http://openclaw-scheduler:8080/api/chat/stream \
        -H 'Content-Type: application/json' \
        -d '{"agent_id":"test-agent","message":"你好，用10个字回复"}'
    ;;
    
  3)
    echo ""
    echo "📊 实时日志监控"
    echo ""
    kubectl logs -n openclaw -l app=openclaw-scheduler --follow --tail=20
    ;;
    
  *)
    echo "❌ 无效选项"
    ;;
esac
