#!/bin/bash
# AgentHub 初始化脚本 - Linux/macOS/WSL

set -e

echo "🚀 AgentHub 初始化..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未安装${NC}"
    exit 1
fi

# 检查 Python (可选)
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python3 已安装${NC}"
else
    echo -e "${YELLOW}⚠ Python3 未安装 (可选)${NC}"
fi

# 检查 Node.js (可选)
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js 已安装${NC}"
else
    echo -e "${YELLOW}⚠ Node.js 未安装 (可选)${NC}"
fi

echo ""
echo "📁 目录结构:"
echo "├── profile/      # 用户画像"
echo "├── skills/       # 共享技能库"
echo "├── agents/       # Agent 配置"
echo "├── projects/     # 项目配置"
echo "└── docs/         # 文档"

echo ""
echo -e "${GREEN}✅ 初始化完成！${NC}"
echo ""
echo "下一步:"
echo "  1. 编辑 profile/identity.md 填写你的信息"
echo "  2. 查看 agents/router.md 了解路由规则"
echo "  3. 查看 skills/ 了解可用技能"
