#!/usr/bin/env bash
# 虚拟环境快速检查脚本（macOS/Linux）
# 功能：检查项目根目录下的虚拟环境是否存在
# 使用：bash check.sh
# 退出码：0=存在, 1=不存在

set -euo pipefail

# 获取脚本所在目录（env-checker/scripts）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录：env-checker/scripts -> env-checker -> skills -> 根目录
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# 虚拟环境路径
VENV_DIR="${PROJECT_ROOT}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

# 检查虚拟环境是否存在
if [[ -x "$VENV_PYTHON" ]]; then
    # 虚拟环境存在
    PYTHON_VERSION=$("$VENV_PYTHON" --version 2>&1 || echo "Unknown")
    echo "VENV_EXISTS=true"
    echo "VENV_PYTHON=$VENV_PYTHON"
    echo "VENV_DIR=$VENV_DIR"
    echo "PROJECT_ROOT=$PROJECT_ROOT"
    echo "PYTHON_VERSION=$PYTHON_VERSION"
    exit 0
else
    # 虚拟环境不存在
    SETUP_SCRIPT="${SCRIPT_DIR}/setup.sh"
    echo "VENV_EXISTS=false"
    echo "VENV_DIR=$VENV_DIR"
    echo "PROJECT_ROOT=$PROJECT_ROOT"
    echo "SETUP_COMMAND=bash $SETUP_SCRIPT"
    exit 1
fi
