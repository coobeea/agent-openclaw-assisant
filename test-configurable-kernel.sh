#!/bin/bash
# 可配置内核完整测试脚本

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║        🧪 可配置内核 - 完整测试脚本 🧪                         ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SCHEDULER_URL="http://localhost:30080"
TEST_AGENT_ID="test-agent-$(date +%s)"

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 辅助函数
print_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

run_test() {
    local test_name=$1
    local test_cmd=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}[测试 $TOTAL_TESTS]${NC} $test_name"
    
    if eval "$test_cmd"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        print_success "通过"
        return 0
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        print_error "失败"
        return 1
    fi
}

# ========== 测试 1: 健康检查 ==========
print_step "测试 1: Scheduler 健康检查"

run_test "健康检查端点" \
    "curl -s -f $SCHEDULER_URL/health > /dev/null"

# ========== 测试 2: 系统状态 ==========
print_step "测试 2: 系统状态检查"

run_test "获取系统状态" \
    "curl -s $SCHEDULER_URL/api/status | jq -e '.database' > /dev/null"

# ========== 测试 3: V1 API（原版）==========
print_step "测试 3: V1 API（原版流式接口）"

echo "发送测试请求..."
RESPONSE=$(curl -s -N -X POST $SCHEDULER_URL/api/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\":\"$TEST_AGENT_ID\",\"message\":\"测试V1 API\"}" \
  --max-time 30 2>&1 | head -5)

if echo "$RESPONSE" | grep -q "connected"; then
    print_success "V1 API 响应正常"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "V1 API 响应异常"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# ========== 测试 4: V2 API - OpenClaw 内核 ==========
print_step "测试 4: V2 API - OpenClaw 内核"

echo "发送 OpenClaw 测试请求..."
RESPONSE=$(curl -s -N -X POST $SCHEDULER_URL/api/chat/stream/v2 \
  -H "Content-Type: application/json" \
  -H "X-Kernel-Type: openclaw" \
  -d "{\"agent_id\":\"$TEST_AGENT_ID\",\"message\":\"Hello, OpenClaw!\"}" \
  --max-time 30 2>&1 | head -10)

echo "响应（前10行）："
echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "connected"; then
    print_success "OpenClaw 内核连接成功"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_warning "OpenClaw 内核连接可能失败（需要检查 Pod）"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# ========== 测试 5: V2 API - QwenPaw 内核 ==========
print_step "测试 5: V2 API - QwenPaw 内核"

echo "发送 QwenPaw 测试请求..."
RESPONSE=$(curl -s -N -X POST $SCHEDULER_URL/api/chat/stream/v2 \
  -H "Content-Type: application/json" \
  -H "X-Kernel-Type: qwenpaw" \
  -d "{\"agent_id\":\"$TEST_AGENT_ID\",\"message\":\"Hello, QwenPaw!\"}" \
  --max-time 30 2>&1 | head -10)

echo "响应（前10行）："
echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "connected"; then
    print_success "QwenPaw 内核连接成功"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_warning "QwenPaw 内核连接失败（可能未部署 QwenPaw Pod）"
    # 不计入失败，因为 QwenPaw 是可选的
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# ========== 测试 6: K8s Pod 状态 ==========
print_step "测试 6: K8s Pod 状态检查"

if command -v kubectl &> /dev/null; then
    echo "检查 OpenClaw Pods..."
    kubectl get pods -n openclaw -l app=openclaw-pool 2>/dev/null || print_warning "无法访问 K8s 集群"
    
    echo ""
    echo "检查 Scheduler Pods..."
    kubectl get pods -n openclaw -l app=openclaw-scheduler 2>/dev/null || print_warning "无法访问 K8s 集群"
    
    echo ""
    echo "检查 QwenPaw Pods（如果存在）..."
    kubectl get pods -n openclaw -l app=qwenpaw-pool 2>/dev/null || echo "QwenPaw Pod 未部署（可选）"
else
    print_warning "kubectl 未安装，跳过 K8s 检查"
fi

# ========== 测试 7: 内核切换测试 ==========
print_step "测试 7: 动态内核切换"

echo "【测试 7.1】默认内核（不指定 Header）"
RESPONSE=$(curl -s -N -X POST $SCHEDULER_URL/api/chat/stream/v2 \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\":\"$TEST_AGENT_ID\",\"message\":\"Default kernel test\"}" \
  --max-time 20 2>&1 | head -3)

if echo "$RESPONSE" | grep -q "connected"; then
    print_success "默认内核工作正常"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "默认内核失败"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "【测试 7.2】显式指定 OpenClaw"
RESPONSE=$(curl -s -N -X POST $SCHEDULER_URL/api/chat/stream/v2 \
  -H "Content-Type: application/json" \
  -H "X-Kernel-Type: openclaw" \
  -d "{\"agent_id\":\"$TEST_AGENT_ID\",\"message\":\"OpenClaw explicit test\"}" \
  --max-time 20 2>&1 | head -3)

if echo "$RESPONSE" | grep -q "connected"; then
    print_success "显式 OpenClaw 工作正常"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_error "显式 OpenClaw 失败"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# ========== 测试总结 ==========
echo ""
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║                    📊 测试总结                                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "总测试数:   ${BLUE}$TOTAL_TESTS${NC}"
echo -e "通过:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败:       ${RED}$FAILED_TESTS${NC}"
echo -e "成功率:     ${YELLOW}$(( PASSED_TESTS * 100 / TOTAL_TESTS ))%${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║            🎉 所有测试通过！系统工作正常！ 🎉                  ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                                                                ║${NC}"
    echo -e "${YELLOW}║         ⚠️  部分测试失败，请检查日志和配置 ⚠️                 ║${NC}"
    echo -e "${YELLOW}║                                                                ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "故障排查建议："
    echo "1. 检查 Scheduler 日志: kubectl logs -f deployment/openclaw-scheduler -n openclaw"
    echo "2. 检查 Pod 状态: kubectl get pods -n openclaw"
    echo "3. 检查配置: kubectl get configmap scheduler-config -n openclaw -o yaml"
    echo "4. 查看文档: docs/25-可配置内核使用指南.md"
    exit 1
fi
