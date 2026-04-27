#!/bin/bash
# AgentHub 一键安装脚本 - Linux/macOS/WSL
#
# 用法:
#   curl -fsSL https://.../install.sh | bash        # 一键安装（检测到已安装则询问）
#   curl -fsSL https://.../install.sh | bash -s -- -f  # 强制重装
#   bash install.sh                              # 交互模式
#   bash install.sh -f                           # 强制重装
#

set -e

# ============================================
# 检测管道输入
# ============================================
is_piped() {
    if [ -p /dev/stdin ] || [ -p /dev/fd/0 ]; then
        return 0
    fi
    if [ -f /dev/stdin ]; then
        local bytes=$(cat /dev/stdin 2>/dev/null | wc -c)
        if [ "$bytes" -gt 0 ]; then
            return 0
        fi
    fi
    return 1
}

# ============================================
# 颜色定义
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ============================================
# 配置
# ============================================
REPO_URL="https://github.com/xuanyuanluoxue/AgentHub.git"
INSTALL_DIR="${HOME}/.agenthub"
BACKUP_DIR="${HOME}/.agenthub.backup.$(date +%Y%m%d%H%M%S)"
FORCE_REINSTALL=false
INTERACTIVE=true

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE_REINSTALL=true
            shift
            ;;
        -y|--yes)
            INTERACTIVE=false
            FORCE_REINSTALL=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 [-f] [安装目录]"
            echo "  -f, --force  强制重装（覆盖现有配置）"
            echo "  -y, --yes    非交互模式，自动确认"
            exit 0
            ;;
        *)
            INSTALL_DIR="$1"
            shift
            ;;
    esac
done

# 管道输入时，非交互但不强制的
if is_piped; then
    INTERACTIVE=false
fi

# ============================================
# 日志函数
# ============================================
log_info() { echo -e "${BLUE}➜${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_dim() { echo -e "${DIM}$1${NC}"; }

print_divider() {
    echo -e "${DIM}$(printf '─%.0s' $(seq 1 50))${NC}"
}

# ============================================
# Banner
# ============================================
print_banner() {
    echo ""
    echo -e "${BOLD}${MAGENTA}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${MAGENTA}║${NC}          ${BOLD}${GREEN}██╗   ██╗ ██████╗ ██████╗ ██████╗ ██╗   ██╗${NC}          ${BOLD}${MAGENTA}║${NC}"
    echo -e "${BOLD}${MAGENTA}║${NC}          ${BOLD}${GREEN}██║   ██║██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝${NC}          ${BOLD}${MAGENTA}║${NC}"
    echo -e "${BOLD}${MAGENTA}║${NC}          ${BOLD}${GREEN}██║   ██║██║   ██║██████╔╝██████╔╝ ╚████╔╝ ${NC}          ${BOLD}${MAGENTA}║${NC}"
    echo -e "${BOLD}${MAGENTA}║${NC}          ${BOLD}${GREEN}╚██╗ ██╔╝██║   ██║██╔══██╗██╔══██╗  ╚██╔╝  ${NC}          ${BOLD}${MAGENTA}║${NC}"
    echo -e "${BOLD}${MAGENTA}║${NC}          ${BOLD}${GREEN} ╚████╔╝ ╚██████╔╝██████╔╝██████╔╝   ██║   ${NC}          ${BOLD}${MAGENTA}║${NC}"
    echo -e "${BOLD}${MAGENTA}║${NC}                     ${BOLD}${CYAN}统一 AI 工具四大共享生态${NC}                    ${BOLD}${MAGENTA}║${NC}"
    echo -e "${BOLD}${MAGENTA}║${NC}                     ${DIM}Skill · Agent · 画像 · 记忆系统${NC}                     ${BOLD}${MAGENTA}║${NC}"
    echo -e "${BOLD}${MAGENTA}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ============================================
# 确认提示
# ============================================
confirm() {
    local message="$1"
    local default="${2:-N}"

    if [ "$INTERACTIVE" = false ]; then
        return 1  # 非交互模式，返回 false（不确认）
    fi

    if [ "$default" = "Y" ]; then
        echo -n "$message [Y/n]: "
    else
        echo -n "$message [y/N]: "
    fi

    read -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY && "$default" == "Y" ]]; then
        return 0
    fi
    return 1
}

# ============================================
# 检查是否已安装
# ============================================
is_installed() {
    if [ -d "${INSTALL_DIR}" ] && [ -f "${INSTALL_DIR}/pyproject.toml" ]; then
        return 0
    fi
    return 1
}

# ============================================
# 检查依赖
# ============================================
check_dependencies() {
    echo -e "${BOLD}▸ 检查系统依赖${NC}"
    print_divider

    local deps=("git" "python3")
    local all_ok=true

    for dep in "${deps[@]}"; do
        if command -v $dep &> /dev/null; then
            local version=$(eval "$dep --version 2>/dev/null" | head -1 | cut -d' ' -f1-2 | tr -d ' ')
            echo -e "  ${GREEN}✓${NC} ${CYAN}${dep}${NC} ${DIM}(${version})${NC}"
        else
            echo -e "  ${RED}✗${NC} ${CYAN}${dep}${NC} ${DIM}(未找到)${NC}"
            all_ok=false
        fi
    done

    if [ "$all_ok" = false ]; then
        echo ""
        log_error "缺少必要的系统依赖"
        echo ""
        echo -e "${DIM}请先安装缺失的依赖:${NC}"
        echo -e "  Ubuntu/Debian: ${GREEN}sudo apt install git python3 python3-pip${NC}"
        echo -e "  macOS:         ${GREEN}brew install git python${NC}"
        echo ""
        exit 1
    fi

    # 检查 Python 版本
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        echo ""
        log_error "Python 版本过低: $PYTHON_VERSION (需要 >= 3.10)"
        echo ""
        exit 1
    fi

    echo ""
    log_success "所有依赖检查通过"
    echo ""
}

# ============================================
# 备份/清理现有配置
# ============================================
prepare_existing() {
    echo -e "${BOLD}▸ 准备现有配置${NC}"
    print_divider

    if confirm "  检测到已安装 AgentHub，是否重装?"; then
        log_info "正在备份到 ${BACKUP_DIR}..."
        if mv "${INSTALL_DIR}" "${BACKUP_DIR}" 2>/dev/null; then
            log_success "备份完成 (位于 ${BACKUP_DIR})"
        else
            log_error "备份失败"
            exit 1
        fi
        echo ""
        return 0  # 需要重装
    else
        echo ""
        log_info "跳过重装，现有配置保持不变"
        echo ""
        echo -e "${BOLD}▸ 下一步${NC}"
        print_divider
        echo -e "  ${CYAN}1.${NC} 验证安装: ${DIM}agenthub status${NC}"
        echo -e "  ${CYAN}2.${NC} 搜索 Skills: ${DIM}agenthub clawhub search github${NC}"
        echo ""
        exit 0
    fi
}

# ============================================
# 克隆仓库
# ============================================
clone_repo() {
    echo -e "${BOLD}▸ 下载 AgentHub${NC}"
    print_divider

    log_info "正在克隆仓库..."
    echo -e "  ${DIM}来源: ${REPO_URL}${NC}"
    echo -e "  ${DIM}目标: ${INSTALL_DIR}${NC}"
    echo ""

    if git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}" 2>&1; then
        echo ""
        log_success "仓库克隆完成"
        echo ""
    else
        echo ""
        log_error "克隆失败，请检查网络连接"
        echo ""
        exit 1
    fi
}

# ============================================
# 安装 Python 包
# ============================================
install_package() {
    echo -e "${BOLD}▸ 安装 Python 包${NC}"
    print_divider

    cd "${INSTALL_DIR}"

    if [ ! -f "pyproject.toml" ]; then
        log_error "pyproject.toml 不存在"
        exit 1
    fi

    log_info "正在安装 AgentHub CLI..."
    echo ""

    local install_ok=false
    local install_method=""

    # 方法 1: pip install --user
    log_dim "  尝试: pip install --user..."
    if pip install --user -e . 2>&1; then
        install_ok=true
        install_method="pip --user"
    fi

    # 方法 2: pip install --break-system-packages
    if [ "$install_ok" = false ]; then
        echo ""
        log_dim "  尝试: pip install --break-system-packages..."
        if pip install --break-system-packages -e . 2>&1; then
            install_ok=true
            install_method="pip --break-system-packages"
        fi
    fi

    # 方法 3: python3 -m pip install --user
    if [ "$install_ok" = false ]; then
        echo ""
        log_dim "  尝试: python3 -m pip install --user..."
        if python3 -m pip install --user -e . 2>&1; then
            install_ok=true
            install_method="python3 -m pip --user"
        fi
    fi

    # 方法 4: sudo python3 -m pip
    if [ "$install_ok" = false ]; then
        echo ""
        log_dim "  尝试: sudo python3 -m pip..."
        if sudo python3 -m pip install -e . 2>&1; then
            install_ok=true
            install_method="sudo python3 -m pip"
        fi
    fi

    echo ""

    if [ "$install_ok" = true ]; then
        log_success "Python 包安装完成 ($install_method)"
    else
        log_error "所有安装方法都失败了"
        echo ""
        log_info "请手动安装:"
        echo -e "  ${CYAN}cd ~/.agenthub${NC}"
        echo -e "  ${CYAN}pip install --user -e .${NC}"
        echo ""
        exit 1
    fi
    echo ""

    # PATH 提示
    local user_bin="${HOME}/.local/bin"
    if [ -d "$user_bin" ] && [[ ":$PATH:" != *":$user_bin:"* ]]; then
        echo -e "  ${YELLOW}⚠${NC} 建议将 ${CYAN}$user_bin${NC} 添加到 PATH"
        echo -e "  ${DIM}echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc${NC}"
        echo ""
    fi

    # 验证安装
    if command -v agenthub &> /dev/null; then
        AGENTHUB_VERSION=$(agenthub --version 2>/dev/null || echo "unknown")
        echo -e "  ${GREEN}✓${NC} ${CYAN}agenthub${NC} ${DIM}(v${AGENTHUB_VERSION})${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} ${CYAN}agenthub${NC} ${DIM}(未添加到 PATH，请重新打开终端)${NC}"
    fi
    echo ""
}

# ============================================
# 初始化配置
# ============================================
init_config() {
    echo -e "${BOLD}▸ 初始化配置${NC}"
    print_divider

    mkdir -p "${INSTALL_DIR}/skills"
    mkdir -p "${INSTALL_DIR}/agents"
    mkdir -p "${INSTALL_DIR}/profile"
    mkdir -p "${INSTALL_DIR}/apps"

    if [ -f "${INSTALL_DIR}/profile/identity.yaml" ]; then
        log_info "配置文件已存在，跳过初始化"
        echo ""
        return
    fi

    log_info "创建默认配置文件..."

    cat > "${INSTALL_DIR}/profile/identity.yaml" << 'EOF'
name: Your Name
bio: AI enthusiast and developer
contact:
  email: your@email.com
  github: https://github.com/your-username
preferences:
  language: zh-CN
  theme: auto
EOF

    echo '{"skills": [], "agents": [], "version": "1.0"}' > "${INSTALL_DIR}/registry.json"

    log_success "配置文件创建完成"
    echo ""
}

# ============================================
# 完成
# ============================================
print_complete() {
    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║${NC}                    ${BOLD}安装完成！${NC}                          ${BOLD}${GREEN}║${NC}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}▸ 下一步${NC}"
    print_divider
    echo -e "  ${CYAN}1.${NC} 编辑配置文件"
    echo -e "     ${DIM}vim ~/.agenthub/profile/identity.yaml${NC}"
    echo ""
    echo -e "  ${CYAN}2.${NC} 尝试验证安装"
    echo -e "     ${DIM}agenthub status${NC}"
    echo ""
    echo -e "  ${CYAN}3.${NC} 搜索 ClawHub Skills"
    echo -e "     ${DIM}agenthub clawhub search github${NC}"
    echo ""

    if command -v agenthub &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} ${CYAN}agenthub${NC} 已添加到 PATH"
    else
        echo -e "  ${YELLOW}⚠${NC} agenthub 未找到，请重新打开终端"
    fi

    echo ""
    echo -e "${DIM}帮助文档: https://github.com/xuanyuanluoxue/AgentHub${NC}"
    echo ""
}

# ============================================
# 主流程
# ============================================
main() {
    print_banner
    check_dependencies

    # 检测已安装
    if is_installed; then
        if [ "$FORCE_REINSTALL" = true ]; then
            # 强制重装
            log_info "强制重装模式，跳过备份"
            rm -rf "${INSTALL_DIR}"
            echo ""
        else
            # 询问是否重装
            prepare_existing
        fi
    fi

    clone_repo
    install_package
    init_config
    print_complete
}

main
