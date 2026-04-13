#!/bin/bash
# 可配置内核一键部署脚本

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║        🚀 可配置内核 - 一键部署脚本 🚀                         ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查依赖
check_dependencies() {
    print_step "检查依赖工具"
    
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    else
        print_success "Docker 已安装"
    fi
    
    if ! command -v kubectl &> /dev/null; then
        missing_deps+=("kubectl")
    else
        print_success "kubectl 已安装"
    fi
    
    if ! command -v go &> /dev/null; then
        missing_deps+=("go")
    else
        print_success "Go 已安装"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "缺少依赖: ${missing_deps[*]}"
        echo "请安装缺少的依赖后重试"
        exit 1
    fi
}

# 步骤 1: 编译 Go 代码
compile_scheduler() {
    print_step "步骤 1: 编译 Scheduler"
    
    cd scheduler-go
    echo "更新依赖..."
    go mod tidy
    
    echo "编译..."
    go build -o bin/scheduler cmd/server/main.go
    
    if [ -f bin/scheduler ]; then
        print_success "编译成功"
        ls -lh bin/scheduler
    else
        print_error "编译失败"
        exit 1
    fi
    
    cd ..
}

# 步骤 2: 构建 Docker 镜像
build_docker_image() {
    print_step "步骤 2: 构建 Docker 镜像"
    
    cd scheduler-go
    
    echo "构建镜像: scheduler-go:configurable-kernel"
    docker build -t scheduler-go:configurable-kernel .
    
    if [ $? -eq 0 ]; then
        print_success "镜像构建成功"
        docker images | grep scheduler-go
    else
        print_error "镜像构建失败"
        exit 1
    fi
    
    cd ..
}

# 步骤 3: 检查 K8s 集群
check_k8s_cluster() {
    print_step "步骤 3: 检查 K8s 集群"
    
    if kubectl cluster-info &> /dev/null; then
        print_success "K8s 集群连接正常"
        kubectl cluster-info | head -3
    else
        print_error "无法连接到 K8s 集群"
        echo "请确保 K8s 集群正在运行（如 Docker Desktop Kubernetes）"
        exit 1
    fi
}

# 步骤 4: 创建 namespace
create_namespace() {
    print_step "步骤 4: 创建 Namespace"
    
    if kubectl get namespace openclaw &> /dev/null; then
        print_warning "Namespace 'openclaw' 已存在，跳过创建"
    else
        kubectl create namespace openclaw
        print_success "Namespace 'openclaw' 创建成功"
    fi
}

# 步骤 5: 部署配置和服务
deploy_resources() {
    print_step "步骤 5: 部署 K8s 资源"
    
    echo "【5.1】部署 OpenClaw Pool..."
    if [ -f k8s-manifests/04-openclaw-pool.yaml ]; then
        kubectl apply -f k8s-manifests/04-openclaw-pool.yaml
        print_success "OpenClaw Pool 部署完成"
    else
        print_warning "OpenClaw Pool 配置文件不存在"
    fi
    
    echo ""
    echo "【5.2】部署 Scheduler（可配置内核）..."
    if [ -f k8s-manifests/05-scheduler-configurable-kernel.yaml ]; then
        kubectl apply -f k8s-manifests/05-scheduler-configurable-kernel.yaml
        print_success "Scheduler 部署完成"
    else
        print_error "Scheduler 配置文件不存在"
        exit 1
    fi
    
    echo ""
    echo "【5.3】部署 Frontend（可选）..."
    if [ -f k8s-manifests/06-frontend.yaml ]; then
        kubectl apply -f k8s-manifests/06-frontend.yaml
        print_success "Frontend 部署完成"
    else
        print_warning "Frontend 配置文件不存在，跳过"
    fi
    
    echo ""
    echo "【5.4】部署 QwenPaw Pool（可选）..."
    if [ -f k8s-manifests/07-qwenpaw-pool.yaml ]; then
        read -p "是否部署 QwenPaw Pool？(y/N): " deploy_qwenpaw
        if [[ $deploy_qwenpaw =~ ^[Yy]$ ]]; then
            kubectl apply -f k8s-manifests/07-qwenpaw-pool.yaml
            print_success "QwenPaw Pool 部署完成"
        else
            print_warning "跳过 QwenPaw Pool 部署"
        fi
    else
        print_warning "QwenPaw Pool 配置文件不存在，跳过"
    fi
}

# 步骤 6: 等待 Pod 就绪
wait_for_pods() {
    print_step "步骤 6: 等待 Pod 就绪"
    
    echo "等待 Scheduler Pod 就绪..."
    kubectl wait --for=condition=ready pod -l app=openclaw-scheduler -n openclaw --timeout=120s || {
        print_error "Scheduler Pod 启动超时"
        kubectl get pods -n openclaw -l app=openclaw-scheduler
        exit 1
    }
    print_success "Scheduler Pod 已就绪"
    
    echo ""
    echo "等待 OpenClaw Pod 就绪..."
    kubectl wait --for=condition=ready pod -l app=openclaw-pool -n openclaw --timeout=120s || {
        print_warning "OpenClaw Pod 启动超时（可能需要手动检查）"
    }
    print_success "OpenClaw Pod 已就绪"
}

# 步骤 7: 显示部署状态
show_deployment_status() {
    print_step "步骤 7: 部署状态"
    
    echo "【Pods 状态】"
    kubectl get pods -n openclaw
    
    echo ""
    echo "【Services 状态】"
    kubectl get svc -n openclaw
    
    echo ""
    echo "【ConfigMaps】"
    kubectl get configmap -n openclaw
}

# 步骤 8: 显示访问信息
show_access_info() {
    print_step "部署完成"
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║            🎉 可配置内核部署成功！ 🎉                          ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "【访问地址】"
    echo "  • Scheduler API:  http://localhost:30080"
    echo "  • Health Check:   http://localhost:30080/health"
    echo "  • Frontend:       http://localhost:30000 (如已部署)"
    echo ""
    echo "【测试命令】"
    echo "  # 测试 OpenClaw 内核"
    echo "  curl -X POST http://localhost:30080/api/chat/stream/v2 \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -H 'X-Kernel-Type: openclaw' \\"
    echo "    -d '{\"agent_id\":\"test\",\"message\":\"Hello\"}'"
    echo ""
    echo "  # 运行完整测试"
    echo "  ./test-configurable-kernel.sh"
    echo ""
    echo "【查看日志】"
    echo "  kubectl logs -f deployment/openclaw-scheduler -n openclaw"
    echo ""
    echo "【查看文档】"
    echo "  docs/25-可配置内核使用指南.md"
}

# 主流程
main() {
    check_dependencies
    compile_scheduler
    build_docker_image
    check_k8s_cluster
    create_namespace
    deploy_resources
    wait_for_pods
    show_deployment_status
    show_access_info
}

# 执行主流程
main
