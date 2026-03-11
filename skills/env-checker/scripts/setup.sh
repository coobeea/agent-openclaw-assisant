#!/usr/bin/env bash
# env-checker: 跨平台 Python 环境全自动检测、安装、初始化、验证 (macOS/Linux)
# 目标版本: Python 3.12
# 全程无需人工干预，执行完毕即可运行所有 Skill

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
# 项目根目录：env-checker 的上一级即项目根
PROJECT_ROOT="$(cd "${SKILL_DIR}/.." && pwd)"

REQUIRED_MAJOR=3
REQUIRED_MINOR=12
REQUIRED_VERSION="${REQUIRED_MAJOR}.${REQUIRED_MINOR}"
PYTHON_FULL_VERSION="3.12.8"

MACOS_INSTALLER_URL="https://www.python.org/ftp/python/${PYTHON_FULL_VERSION}/python-${PYTHON_FULL_VERSION}-macos11.pkg"
MACOS_INSTALLER_URL_BACKUP="https://registry.npmmirror.com/-/binary/python/${PYTHON_FULL_VERSION}/python-${PYTHON_FULL_VERSION}-macos11.pkg"

UNIFIED_REQUIREMENTS="${SKILL_DIR}/requirements.txt"
VERIFY_SCRIPT="${SCRIPT_DIR}/verify.py"

# 默认 project-dir 指向项目根目录（而非调用目录），确保 .venv 始终建在根目录
PROJECT_DIR="$PROJECT_ROOT"
REQUIREMENTS_FILE=""
CHECK_ONLY=false
VERBOSE=false
VENV_NAME=".venv"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1" >&2; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
log_step()  { echo -e "${BLUE}[STEP]${NC} $1" >&2; }
log_debug() { if $VERBOSE; then echo -e "[DEBUG] $1" >&2; fi; }

while [[ $# -gt 0 ]]; do
    case $1 in
        --project-dir)  PROJECT_DIR="$2"; shift 2 ;;
        --requirements) REQUIREMENTS_FILE="$2"; shift 2 ;;
        --check-only)   CHECK_ONLY=true; shift ;;
        --verbose)      VERBOSE=true; shift ;;
        --venv-name)    VENV_NAME="$2"; shift 2 ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

detect_os() {
    local uname_out
    uname_out="$(uname -s)"
    case "$uname_out" in
        Darwin*) echo "macos" ;;
        Linux*)  echo "linux" ;;
        *)       echo "unknown" ;;
    esac
}

detect_arch() {
    local arch
    arch="$(uname -m)"
    case "$arch" in
        x86_64|amd64) echo "x64" ;;
        arm64|aarch64) echo "arm64" ;;
        *) echo "$arch" ;;
    esac
}

version_ge() {
    local major minor
    major=$(echo "$1" | cut -d. -f1)
    minor=$(echo "$1" | cut -d. -f2)
    if [[ "$major" -gt "$REQUIRED_MAJOR" ]]; then return 0; fi
    if [[ "$major" -eq "$REQUIRED_MAJOR" && "$minor" -ge "$REQUIRED_MINOR" ]]; then return 0; fi
    return 1
}

version_eq_minor() {
    local major minor
    major=$(echo "$1" | cut -d. -f1)
    minor=$(echo "$1" | cut -d. -f2)
    [[ "$major" -eq "$REQUIRED_MAJOR" && "$minor" -eq "$REQUIRED_MINOR" ]]
}

get_python_version() {
    local cmd="$1"
    "$cmd" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1
}

find_suitable_python() {
    local candidates=(
        "python${REQUIRED_VERSION}"
        "python${REQUIRED_MAJOR}.${REQUIRED_MINOR}"
        "python${REQUIRED_MAJOR}"
        "python"
        "/usr/local/bin/python${REQUIRED_VERSION}"
        "/usr/local/bin/python${REQUIRED_MAJOR}"
        "/opt/homebrew/bin/python${REQUIRED_VERSION}"
        "/opt/homebrew/bin/python${REQUIRED_MAJOR}"
        "/Library/Frameworks/Python.framework/Versions/${REQUIRED_VERSION}/bin/python${REQUIRED_MAJOR}"
        "/Library/Frameworks/Python.framework/Versions/${REQUIRED_VERSION}/bin/python${REQUIRED_VERSION}"
    )

    local best_match=""
    local best_version=""

    for cmd in "${candidates[@]}"; do
        if command -v "$cmd" &>/dev/null || [[ -x "$cmd" ]]; then
            local ver
            ver=$(get_python_version "$cmd" 2>/dev/null) || continue
            if [[ -z "$ver" ]]; then continue; fi

            log_debug "检测到: $cmd -> Python $ver"

            if version_eq_minor "$ver"; then
                echo "$cmd"
                return 0
            fi

            if version_ge "$ver" && [[ -z "$best_match" ]]; then
                best_match="$cmd"
                best_version="$ver"
            fi
        fi
    done

    if [[ -n "$best_match" ]]; then
        log_warn "未找到 Python ${REQUIRED_VERSION}.x，使用兼容版本: $best_match (Python $best_version)"
        echo "$best_match"
        return 0
    fi

    return 1
}

install_python_macos() {
    log_step "开始在 macOS 上安装 Python ${PYTHON_FULL_VERSION}..."

    if command -v brew &>/dev/null; then
        log_info "检测到 Homebrew，尝试通过 brew 安装..."
        if brew install "python@${REQUIRED_VERSION}" 2>/dev/null; then
            log_info "Homebrew 安装成功"
            local brew_python
            brew_python="$(brew --prefix python@${REQUIRED_VERSION})/bin/python${REQUIRED_VERSION}"
            if [[ -x "$brew_python" ]]; then
                echo "$brew_python"
                return 0
            fi
            brew_python="$(brew --prefix)/bin/python${REQUIRED_VERSION}"
            if [[ -x "$brew_python" ]]; then
                echo "$brew_python"
                return 0
            fi
        fi
        log_warn "Homebrew 安装失败，回退到官方安装包..."
    fi

    local tmpdir
    tmpdir=$(mktemp -d)
    local pkg_path="${tmpdir}/python-${PYTHON_FULL_VERSION}.pkg"

    log_info "从 python.org 下载安装包..."
    if ! curl -fSL --progress-bar -o "$pkg_path" "$MACOS_INSTALLER_URL" 2>/dev/null; then
        log_warn "官方源下载失败，尝试镜像源..."
        if ! curl -fSL --progress-bar -o "$pkg_path" "$MACOS_INSTALLER_URL_BACKUP" 2>/dev/null; then
            log_error "下载失败，请检查网络连接"
            rm -rf "$tmpdir"
            return 1
        fi
    fi

    log_info "正在安装 Python (需要管理员权限)..."
    if sudo installer -pkg "$pkg_path" -target / 2>/dev/null; then
        log_info "安装成功"
    else
        log_error "安装失败。你可以手动下载安装："
        log_error "  ${MACOS_INSTALLER_URL}"
        rm -rf "$tmpdir"
        return 1
    fi

    rm -rf "$tmpdir"

    local framework_python="/Library/Frameworks/Python.framework/Versions/${REQUIRED_VERSION}/bin/python${REQUIRED_VERSION}"
    if [[ -x "$framework_python" ]]; then
        echo "$framework_python"
        return 0
    fi

    if command -v "python${REQUIRED_VERSION}" &>/dev/null; then
        echo "python${REQUIRED_VERSION}"
        return 0
    fi

    return 1
}

install_python_linux() {
    log_step "开始在 Linux 上安装 Python ${REQUIRED_VERSION}..."

    if command -v apt-get &>/dev/null; then
        log_info "检测到 apt，通过 apt 安装..."
        sudo apt-get update -qq
        if sudo apt-get install -y "python${REQUIRED_VERSION}" "python${REQUIRED_VERSION}-venv" "python${REQUIRED_VERSION}-dev" 2>/dev/null; then
            echo "python${REQUIRED_VERSION}"
            return 0
        fi
        log_info "默认源没有 Python ${REQUIRED_VERSION}，添加 deadsnakes PPA..."
        sudo apt-get install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update -qq
        if sudo apt-get install -y "python${REQUIRED_VERSION}" "python${REQUIRED_VERSION}-venv" "python${REQUIRED_VERSION}-dev"; then
            echo "python${REQUIRED_VERSION}"
            return 0
        fi
    elif command -v yum &>/dev/null; then
        log_info "检测到 yum，通过 yum 安装..."
        if sudo yum install -y "python${REQUIRED_VERSION}" 2>/dev/null; then
            echo "python${REQUIRED_VERSION}"
            return 0
        fi
    elif command -v dnf &>/dev/null; then
        log_info "检测到 dnf，通过 dnf 安装..."
        if sudo dnf install -y "python${REQUIRED_VERSION}" 2>/dev/null; then
            echo "python${REQUIRED_VERSION}"
            return 0
        fi
    fi

    log_error "自动安装失败，请手动安装 Python ${REQUIRED_VERSION}"
    log_error "  Ubuntu/Debian: sudo apt install python${REQUIRED_VERSION}"
    log_error "  CentOS/RHEL:   sudo yum install python${REQUIRED_VERSION}"
    log_error "  或从源码编译: https://www.python.org/downloads/"
    return 1
}

create_venv() {
    local python_cmd="$1"
    local venv_dir="$2"

    if [[ -d "$venv_dir" ]]; then
        local venv_python="${venv_dir}/bin/python"
        if [[ -x "$venv_python" ]]; then
            local venv_ver
            venv_ver=$(get_python_version "$venv_python" 2>/dev/null)
            if [[ -n "$venv_ver" ]] && version_ge "$venv_ver"; then
                log_info "虚拟环境已存在且版本匹配 (Python $venv_ver): $venv_dir"
                echo "$venv_python"
                return 0
            fi
        fi
        log_warn "虚拟环境存在但不可用，重新创建..."
        rm -rf "$venv_dir"
    fi

    log_step "创建虚拟环境: $venv_dir"
    "$python_cmd" -m venv "$venv_dir"

    local venv_python="${venv_dir}/bin/python"
    if [[ ! -x "$venv_python" ]]; then
        log_error "虚拟环境创建失败"
        return 1
    fi

    log_info "升级 pip..."
    "$venv_python" -m pip install --upgrade pip --quiet 2>/dev/null || true

    echo "$venv_python"
    return 0
}

install_requirements() {
    local venv_python="$1"
    local req_file="$2"
    local label="${3:-}"

    if [[ ! -f "$req_file" ]]; then
        log_warn "未找到: $req_file，跳过"
        return 0
    fi

    if [[ -n "$label" ]]; then
        log_info "安装${label}: $req_file"
    else
        log_info "安装依赖: $req_file"
    fi
    "$venv_python" -m pip install -r "$req_file" --quiet
}

run_verify() {
    local venv_python="$1"

    if [[ ! -f "$VERIFY_SCRIPT" ]]; then
        log_warn "验证脚本不存在: $VERIFY_SCRIPT，跳过验证"
        return 0
    fi

    log_step "运行环境验证..."
    if "$venv_python" "$VERIFY_SCRIPT"; then
        return 0
    else
        log_error "环境验证未通过，请检查上方失败项"
        return 1
    fi
}

print_env_report() {
    local python_cmd="$1"
    local ver="$2"
    local os_type="$3"
    local arch="$4"

    echo "" >&2
    echo "==============================================" >&2
    echo -e "${GREEN}  环境检测报告${NC}" >&2
    echo "==============================================" >&2
    echo "" >&2
    echo "  操作系统:     $os_type ($arch)" >&2
    echo "  Python 路径:  $python_cmd" >&2
    echo "  Python 版本:  $ver" >&2
    echo "  目标版本:     ${REQUIRED_VERSION}.x" >&2
    if version_eq_minor "$ver"; then
        echo -e "  版本状态:     ${GREEN}完全匹配${NC}" >&2
    elif version_ge "$ver"; then
        echo -e "  版本状态:     ${YELLOW}兼容 (高于目标)${NC}" >&2
    fi
    echo "" >&2
    echo "==============================================" >&2
}

main() {
    echo "" >&2
    log_step "===== 环境全自动初始化 (Python ${REQUIRED_VERSION}) ====="
    echo "" >&2

    local os_type arch
    os_type=$(detect_os)
    arch=$(detect_arch)
    log_info "操作系统: $os_type ($arch)"

    if [[ "$os_type" == "unknown" ]]; then
        log_error "不支持的操作系统: $(uname -s)"
        log_error "目前仅支持 macOS 和 Linux"
        exit 1
    fi

    # --- Step 1: 检测 Python ---
    log_step "1/5 检测 Python 环境..."
    local python_cmd
    if python_cmd=$(find_suitable_python); then
        local current_ver
        current_ver=$(get_python_version "$python_cmd")
        log_info "找到 Python: $python_cmd (版本 $current_ver)"

        if $CHECK_ONLY; then
            print_env_report "$python_cmd" "$current_ver" "$os_type" "$arch"
            exit 0
        fi
    else
        log_warn "未找到 Python ${REQUIRED_VERSION} 或兼容版本"

        if $CHECK_ONLY; then
            log_error "Python ${REQUIRED_VERSION} 未安装"
            exit 1
        fi

        # --- Step 2: 安装 Python ---
        log_step "2/5 自动安装 Python ${PYTHON_FULL_VERSION}..."
        case "$os_type" in
            macos) python_cmd=$(install_python_macos) ;;
            linux) python_cmd=$(install_python_linux) ;;
        esac

        if [[ -z "$python_cmd" ]]; then
            log_error "Python 安装失败"
            exit 1
        fi

        local installed_ver
        installed_ver=$(get_python_version "$python_cmd")
        log_info "Python 安装成功: $python_cmd (版本 $installed_ver)"
    fi

    # --- Step 3: 创建虚拟环境 ---
    log_step "3/5 配置虚拟环境..."
    local target_dir
    if [[ -n "$PROJECT_DIR" ]]; then
        target_dir="$PROJECT_DIR"
    else
        target_dir="$(pwd)"
    fi

    local venv_dir="${target_dir}/${VENV_NAME}"
    local venv_python
    venv_python=$(create_venv "$python_cmd" "$venv_dir")

    # --- Step 4: 安装依赖（统一依赖 + 项目依赖） ---
    log_step "4/5 安装依赖..."

    if [[ -f "$UNIFIED_REQUIREMENTS" ]]; then
        install_requirements "$venv_python" "$UNIFIED_REQUIREMENTS" "统一依赖(所有Skill)"
    fi

    if [[ -n "$REQUIREMENTS_FILE" && -f "$REQUIREMENTS_FILE" ]]; then
        install_requirements "$venv_python" "$REQUIREMENTS_FILE" "项目依赖"
    elif [[ -f "${target_dir}/requirements.txt" && "${target_dir}/requirements.txt" != "$UNIFIED_REQUIREMENTS" ]]; then
        install_requirements "$venv_python" "${target_dir}/requirements.txt" "项目依赖"
    fi

    log_info "所有依赖安装完成"

    # --- Step 5: 自动验证 ---
    log_step "5/5 验证环境..."
    run_verify "$venv_python"

    echo "" >&2
    echo "==============================================" >&2
    echo -e "${GREEN}  环境就绪${NC}" >&2
    echo "==============================================" >&2
    echo "" >&2
    echo "  Python:  $venv_python" >&2
    echo "  版本:    $(get_python_version "$venv_python")" >&2
    echo "  虚拟环境: $venv_dir" >&2
    echo "" >&2
    echo "==============================================" >&2

    echo "ENV_PYTHON=${venv_python}"
    echo "ENV_VENV_DIR=${venv_dir}"
}

main
