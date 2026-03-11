#!/bin/bash
set -euo pipefail

# OpenClaw 安装脚本
# 自动检测系统环境并选择最佳安装方式

VERSION="${1:-latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测包管理器
detect_package_manager() {
    if command -v pnpm &> /dev/null; then
        echo "pnpm"
    elif command -v yarn &> /dev/null; then
        echo "yarn"
    elif command -v npm &> /dev/null; then
        echo "npm"
    else
        echo "none"
    fi
}

# 安装 OpenClaw
install_openclaw() {
    local version="$1"
    local pm="$2"
    
    info "开始安装 OpenClaw ${version}..."
    
    case "$pm" in
        npm)
            info "使用 npm 安装..."
            if [ "$version" = "latest" ]; then
                npm install -g openclaw
            else
                npm install -g "openclaw@${version}"
            fi
            ;;
        yarn)
            info "使用 yarn 安装..."
            if [ "$version" = "latest" ]; then
                yarn global add openclaw
            else
                yarn global add "openclaw@${version}"
            fi
            ;;
        pnpm)
            info "使用 pnpm 安装..."
            if [ "$version" = "latest" ]; then
                pnpm add -g openclaw
            else
                pnpm add -g "openclaw@${version}"
            fi
            ;;
        *)
            error "未找到包管理器 (npm/yarn/pnpm)"
            error "请先安装 Node.js: https://nodejs.org/"
            exit 1
            ;;
    esac
}

# 验证安装
verify_installation() {
    info "验证安装..."
    
    if ! command -v openclaw &> /dev/null; then
        error "OpenClaw 安装失败，未找到 openclaw 命令"
        exit 1
    fi
    
    local installed_version
    installed_version=$(openclaw --version 2>/dev/null || echo "unknown")
    
    info "✅ OpenClaw 安装成功！"
    info "版本: ${installed_version}"
    info ""
    info "使用方法:"
    info "  openclaw --help     # 查看帮助"
    info "  openclaw init       # 初始化实例"
}

# 主函数
main() {
    info "OpenClaw 安装工具"
    info "版本: ${VERSION}"
    echo ""
    
    # 检测包管理器
    local pm
    pm=$(detect_package_manager)
    
    if [ "$pm" = "none" ]; then
        error "未找到 Node.js 包管理器"
        error "请先安装 Node.js: https://nodejs.org/"
        exit 1
    fi
    
    info "检测到包管理器: $pm"
    echo ""
    
    # 安装
    install_openclaw "$VERSION" "$pm"
    
    # 验证
    verify_installation
}

main "$@"
