#!/bin/bash
# AgentHub 一键安装脚本 - Linux/macOS/WSL
#
# 用法:
#   curl -fsSL https://.../install.sh | bash        # 非交互模式（管道）
#   curl -fsSL https://.../install.sh | bash -s -- -y  # 强制非交互
#   bash install.sh                              # 交互模式
#   bash install.sh -y                           # 非交互模式
#

set -e

# ============================================
# 检测是否为管道输入（非交互必须）
# ============================================
# 方法: 如果 /dev/stdin 是管道文件而非终端，始终非交互
is_piped() {
    # 管道: [ -p /dev/stdin ] 为真
    # FIFO: [ -p /dev/fd/0 ] 为真
    # 终端: [ -c /dev/stdin ] 为真 (character device)
    # 文件: [ -f /dev/stdin ] 为真

    if [ -p /dev/stdin ] || [ -p /dev/fd/0 ]; then
        return 0  # 是管道
    fi

    # 如果 stdin 是文件且有内容（重定向）
    if [ -f /dev/stdin ]; then
        local bytes=$(cat /dev/stdin 2>/dev/null | wc -c)
        if [ "$bytes" -gt 0 ]; then
            return 0  # 有输入内容
        fi
    fi

    return 1  # 非管道
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
INTERACTIVE=true

# 解析参数（必须在任何提示之前）
while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yes|--non-interactive)
            INTERACTIVE=false
            shift
            ;;
        -h|--help)
            echo "用法: $0 [-y] [安装目录]"
            echo "  -y, --yes  非交互模式，自动确认所有提示"
            exit 0
            ;;
        *)
            INSTALL_DIR="$1"
            shift
            ;;
    esac
done

# 如果是管道输入，自动非交互
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
log_step() { echo -e "${CYAN}▸${NC} $1"; }
log_dim() { echo -e "${DIM}$1${NC}"; }

# ============================================
# 分隔线
# ============================================
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
# 确认提示（仅交互模式）
# ============================================
confirm() {
    local message="$1"
    local default="${2:-N}"

    if [ "$INTERACTIVE" = false ]; then
        return 0  # 非交互模式，始终确认
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
# 备份现有配置
# ============================================
backup_existing() {
    if [ -d "${INSTALL_DIR}" ]; then
        echo -e "${BOLD}▸ 备份现有配置${NC}"
        print_divider
        log_warn "发现已存在的 AgentHub 配置"

        if confirm "  是否备份?"; then
            log_info "正在备份到 ${BACKUP_DIR}..."
            if mv "${INSTALL_DIR}" "${BACKUP_DIR}" 2>/dev/null; then
                log_success "备份完成"
            else
                log_error "备份失败"
                exit 1
            fi
        else
            log_warn "跳过备份，现有配置将被覆盖"
            rm -rf "${INSTALL_DIR}"
        fi
        echo ""
    fi
}

# ============================================
# 克隆仓库
# ============================================
clone_repo() {
    echo -e "${BOLD}▸ 下载 AgentHub${NC}"
    print_divider

    if [ -d "${INSTALL_DIR}" ] && [ -f "${INSTALL_DIR}/pyproject.toml" ]; then
        log_info "发现已安装的 AgentHub，跳过下载"
        echo -e "  ${DIM}目录: ${INSTALL_DIR}${NC}"
        echo ""
        return 0
    fi

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

    # 方法 1: pip install --user (推荐)
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
        log_info "或创建虚拟环境:"
        echo -e "  ${CYAN}python3 -m venv ~/.agenthub/.venv${NC}"
        echo -e "  ${CYAN}~/.agenthub/.venv/bin/pip install -e .${NC}"
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
        return 0
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
    backup_existing
    clone_repo
    install_package
    init_config
    print_complete
}

main
