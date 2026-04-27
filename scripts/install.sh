#!/bin/bash
# AgentHub 一键安装脚本 - Linux/macOS/WSL
#
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/install.sh | bash
#   或
#   bash install.sh
#

set -e

# ============================================
# 颜色定义
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# 配置
# ============================================
REPO_URL="https://github.com/xuanyuanluoxue/AgentHub.git"
INSTALL_DIR="${HOME}/.agenthub"
BACKUP_DIR="${HOME}/.agenthub.backup.$(date +%Y%m%d%H%M%S)"

# ============================================
# 函数
# ============================================
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

print_banner() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         AgentHub 安装程序                ║${NC}"
    echo -e "${GREEN}║   统一 AI 工具的 Skill · Agent · 画像    ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
}

check_dependencies() {
    log_info "检查依赖..."

    if ! command -v git &> /dev/null; then
        log_error "Git 未安装，请先安装 Git"
        echo "   Ubuntu/Debian: sudo apt install git"
        echo "   macOS: brew install git"
        exit 1
    fi
    log_success "Git 已安装"

    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装 Python >= 3.10"
        echo "   Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "   macOS: brew install python"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_success "Python3 已安装 (${PYTHON_VERSION})"
}

backup_existing() {
    if [ -d "${INSTALL_DIR}" ]; then
        log_warn "发现已存在的 AgentHub 配置"
        read -p "是否备份现有配置? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "备份现有配置到 ${BACKUP_DIR}"
            mv "${INSTALL_DIR}" "${BACKUP_DIR}"
            log_success "备份完成"
        else
            log_warn "跳过备份，现有配置将被覆盖"
        fi
    fi
}

install_package() {
    log_info "安装 AgentHub Python 包..."

    cd "${INSTALL_DIR}"

    if [ ! -f "pyproject.toml" ]; then
        log_error "pyproject.toml 不存在，请确认安装目录正确"
        exit 1
    fi

    pip install -e . --quiet
    log_success "Python 包安装完成"
}

run_init() {
    log_info "初始化 AgentHub 配置..."

    if command -v agenthub &> /dev/null; then
        read -p "是否初始化配置? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            agenthub init --template
            log_success "配置初始化完成"
        fi
    else
        log_warn "agenthub 命令未安装到 PATH，请重新登录或运行: source ~/.bashrc"
    fi
}

print_next_steps() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            安装完成！                     ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 编辑 ~/.agenthub/profile/identity.yaml 填入你的信息"
    echo "  2. 运行 ${GREEN}agenthub skill list${NC} 查看 Skills"
    echo "  3. 运行 ${GREEN}agenthub agent list${NC} 查看 Agents"
    echo ""
    echo "帮助:"
    echo "  agenthub --help           # 查看帮助"
    echo "  agenthub init --help     # 查看初始化选项"
    echo ""
}

# ============================================
# 主流程
# ============================================
main() {
    print_banner

    check_dependencies

    if [ -d "${INSTALL_DIR}" ] && [ -f "${INSTALL_DIR}/pyproject.toml" ]; then
        log_info "发现已安装的 AgentHub，跳过下载"
        BACKUP_DIR="${INSTALL_DIR}"
    else
        backup_existing

        log_info "克隆 AgentHub 仓库到 ${INSTALL_DIR}..."
        git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}"
        log_success "仓库克隆完成"
    fi

    install_package
    run_init
    print_next_steps
}

# 检查是否提供了安装目录参数
if [ -n "$1" ]; then
    INSTALL_DIR="$1"
fi

main
