#!/bin/bash
# OpenClaw 技能包验证脚本

set -euo pipefail

echo "🔍 OpenClaw 龙虾军团管理系统 - 验证脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    pass_count=$((pass_count + 1))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    fail_count=$((fail_count + 1))
}

check_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo "1️⃣ 检查项目结构..."
echo ""

# 检查主要目录
if [ -d "skills" ]; then
    check_pass "skills/ 目录存在"
else
    check_fail "skills/ 目录缺失"
fi

if [ -d "shared" ]; then
    check_pass "shared/ 目录存在"
else
    check_fail "shared/ 目录缺失"
fi

if [ -d "docs" ]; then
    check_pass "docs/ 目录存在"
else
    check_fail "docs/ 目录缺失"
fi

if [ -d ".cursor" ]; then
    check_pass ".cursor/ 目录存在"
else
    check_fail ".cursor/ 目录缺失"
fi

if [ -d ".cursor/skills" ]; then
    check_pass ".cursor/skills/ 目录存在"
else
    check_fail ".cursor/skills/ 目录缺失"
fi

echo ""
echo "2️⃣ 检查技能包..."
echo ""

# 检查所有技能包
for skill in openclaw-manager openclaw-deploy openclaw-plugin openclaw-channel openclaw-model openclaw-agent; do
    if [ -d "skills/$skill" ]; then
        check_pass "skills/$skill 存在"
        
        # 检查 SKILL.md
        if [ -f "skills/$skill/SKILL.md" ]; then
            check_pass "  → SKILL.md 存在"
        else
            check_fail "  → SKILL.md 缺失"
        fi
        
        # 检查目录
        if [ -d "skills/$skill/reference" ]; then
            check_pass "  → reference/ 存在"
        else
            check_fail "  → reference/ 缺失"
        fi
        
        if [ -d "skills/$skill/scripts" ]; then
            check_pass "  → scripts/ 存在"
        else
            check_fail "  → scripts/ 缺失"
        fi
    else
        check_fail "skills/$skill 缺失"
    fi
done

echo ""
echo "3️⃣ 检查软链接..."
echo ""

# 检查软链接
for skill in openclaw-manager openclaw-deploy openclaw-plugin openclaw-channel openclaw-model openclaw-agent; do
    if [ -L ".cursor/skills/$skill" ]; then
        target=$(readlink ".cursor/skills/$skill")
        if [ -d ".cursor/skills/$skill" ]; then
            check_pass ".cursor/skills/$skill → $target"
        else
            check_fail ".cursor/skills/$skill 链接已损坏"
        fi
    else
        check_fail ".cursor/skills/$skill 软链接缺失"
    fi
done

echo ""
echo "4️⃣ 检查共享工具..."
echo ""

if [ -f "shared/utils/common.py" ]; then
    check_pass "common.py 存在"
else
    check_fail "common.py 缺失"
fi

if [ -f "shared/utils/logger.py" ]; then
    check_pass "logger.py 存在"
else
    check_fail "logger.py 缺失"
fi

if [ -f "shared/utils/crypto.py" ]; then
    check_pass "crypto.py 存在"
else
    check_fail "crypto.py 缺失"
fi

if [ -f "shared/configs/global.yaml.template" ]; then
    check_pass "global.yaml.template 存在"
else
    check_fail "global.yaml.template 缺失"
fi

echo ""
echo "5️⃣ 检查脚本执行权限..."
echo ""

python_scripts=$(find skills -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
executable_scripts=$(find skills -name "*.py" -perm +111 2>/dev/null | wc -l | tr -d ' ')

if [ "$python_scripts" -eq "$executable_scripts" ]; then
    check_pass "所有 Python 脚本有执行权限 ($executable_scripts/$python_scripts)"
else
    check_fail "部分脚本缺少执行权限 ($executable_scripts/$python_scripts)"
fi

bash_scripts=$(find skills -name "*.sh" 2>/dev/null | wc -l | tr -d ' ')
executable_bash=$(find skills -name "*.sh" -perm +111 2>/dev/null | wc -l | tr -d ' ')

if [ "$bash_scripts" -eq "$executable_bash" ]; then
    check_pass "所有 Bash 脚本有执行权限 ($executable_bash/$bash_scripts)"
else
    check_fail "部分脚本缺少执行权限 ($executable_bash/$bash_scripts)"
fi

echo ""
echo "6️⃣ 检查文档..."
echo ""

if [ -f "README.md" ]; then
    check_pass "README.md 存在"
else
    check_fail "README.md 缺失"
fi

if [ -f "docs/需求分析.md" ]; then
    check_pass "需求分析.md 存在"
else
    check_fail "需求分析.md 缺失"
fi

if [ -f "docs/快速开始.md" ]; then
    check_pass "快速开始.md 存在"
else
    check_fail "快速开始.md 缺失"
fi

if [ -f "docs/技能包索引.md" ]; then
    check_pass "技能包索引.md 存在"
else
    check_fail "技能包索引.md 缺失"
fi

if [ -f "docs/开发进度.md" ]; then
    check_pass "开发进度.md 存在"
else
    check_fail "开发进度.md 缺失"
fi

echo ""
echo "=========================================="
echo "验证完成！"
echo ""
echo -e "${GREEN}通过: $pass_count${NC}"
echo -e "${RED}失败: $fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}🎉 所有检查通过！项目已就绪。${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有 $fail_count 项检查失败，请修复。${NC}"
    exit 1
fi
