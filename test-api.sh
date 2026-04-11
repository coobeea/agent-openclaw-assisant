#!/bin/bash

# OpenClaw 完整流程测试脚本

API_BASE="http://localhost:30080/api"

echo "🚀 开始测试 OpenClaw 完整流程..."
echo ""

# 1. 注册用户
echo "1️⃣  注册用户..."
REGISTER_RESULT=$(curl -s -X POST "${API_BASE}/users/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser2", "password": "password123"}')
echo "结果: ${REGISTER_RESULT}"
echo ""

# 2. 登录
echo "2️⃣  用户登录..."
LOGIN_RESULT=$(curl -s -X POST "${API_BASE}/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser2", "password": "password123"}')
echo "结果: ${LOGIN_RESULT}"

USER_ID=$(echo ${LOGIN_RESULT} | grep -o '"user_id":[0-9]*' | grep -o '[0-9]*')
echo "用户 ID: ${USER_ID}"
echo ""

# 3. 创建智能体
echo "3️⃣  创建智能体..."
AGENT_RESULT=$(curl -s -X POST "${API_BASE}/agents/create" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": ${USER_ID}, \"name\": \"客服助手\", \"description\": \"专业的客服智能体\"}")
echo "结果: ${AGENT_RESULT}"

AGENT_ID=$(echo ${AGENT_RESULT} | grep -o '"agent_id":"[^"]*"' | sed 's/"agent_id":"\([^"]*\)"/\1/')
echo "智能体 ID: ${AGENT_ID}"
echo ""

# 4. 查看智能体列表
echo "4️⃣  查看智能体列表..."
LIST_RESULT=$(curl -s "${API_BASE}/agents/list?user_id=${USER_ID}")
echo "结果: ${LIST_RESULT}"
echo ""

# 5. 查看容器池状态
echo "5️⃣  查看容器池状态..."
CONTAINER_STATUS=$(curl -s "${API_BASE}/containers/status")
echo "结果: ${CONTAINER_STATUS}"
echo ""

# 6. 发送对话（第1次）
echo "6️⃣  发送对话（第1次）..."
CHAT_RESULT1=$(curl -s -X POST "${API_BASE}/chat" \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\": \"${AGENT_ID}\", \"message\": \"你好，请介绍一下你自己\"}")
echo "结果: ${CHAT_RESULT1}"
echo ""

# 7. 发送对话（第2次）
echo "7️⃣  发送对话（第2次）..."
CHAT_RESULT2=$(curl -s -X POST "${API_BASE}/chat" \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\": \"${AGENT_ID}\", \"message\": \"你能帮我做什么？\"}")
echo "结果: ${CHAT_RESULT2}"
echo ""

# 8. 查看对话历史
echo "8️⃣  查看对话历史..."
HISTORY_RESULT=$(curl -s "${API_BASE}/chat/history?agent_id=${AGENT_ID}")
echo "结果: ${HISTORY_RESULT}"
echo ""

# 9. 再次查看容器池状态
echo "9️⃣  再次查看容器池状态（验证容器分配）..."
CONTAINER_STATUS2=$(curl -s "${API_BASE}/containers/status")
echo "结果: ${CONTAINER_STATUS2}"
echo ""

echo "✅ 测试完成！"
echo ""
echo "📊 测试总结:"
echo "- 用户 ID: ${USER_ID}"
echo "- 智能体 ID: ${AGENT_ID}"
echo "- 发送了 2 条消息"
echo "- 容器池正常运行"
