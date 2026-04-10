#!/bin/bash
set -e

echo "========================================="
echo "OpenClaw 源码更新脚本"
echo "========================================="

cd /Users/lifeng/git/git-claw/agent-openclaw-assisant

echo ""
echo "第1步：清理旧源码..."
rm -rf workspace/source/openclaw
echo "✅ 旧源码已删除"

echo ""
echo "第2步：从GitHub克隆最新版本..."
cd workspace/source
git clone https://github.com/openclaw/openclaw.git openclaw

echo ""
echo "第3步：检查版本信息..."
cd openclaw
echo "  Git提交:"
git log -1 --format="    %h - %s (%ci)"
echo ""
echo "  Package版本:"
grep '"version"' package.json | head -1

echo ""
echo "========================================="
echo "✅ 完成！最新源码位置:"
echo "   /Users/lifeng/git/git-claw/agent-openclaw-assisant/workspace/source/openclaw"
echo "========================================="
