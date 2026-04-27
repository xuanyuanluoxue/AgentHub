#!/bin/bash
# AgentHub Linux/macOS/WSL 安装脚本 (本地测试版)
#
set -e

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

for arg in "$@"; do
    case $arg in
        -f|--force) FORCE_REINSTALL=true ;;
    esac
done

# ============================================
# 日志
# ============================================
log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_success() { echo -e "  ${GREEN}✓${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}!${NC} $1"; }
log_error() { echo -e "  ${RED}x${NC} $1"; }
log_dim() { echo -e "  ${DIM}$1${NC}"; }

# ============================================
# 检查依赖
# ============================================
check_deps() {
    echo -e "  ${BOLD}▸ 检查系统依赖${NC}"
    echo ""

    local all_ok=true

    for dep in git python3; do
        if command -v $dep &>/dev/null; then
            local ver=$($dep --version 2>/dev/null | head -1 | cut -d' ' -f1-2 | tr -d ' ')
            echo -e "    ${GREEN}✓${NC} ${CYAN}${dep}${NC} ${DIM}(${ver})${NC}"
        else
            echo -e "    ${RED}x${NC} ${CYAN}${dep}${NC} ${DIM}(未找到)${NC}"
            all_ok=false
        fi
    done

    if [ "$all_ok" = false ]; then
        echo ""
        log_error "缺少系统依赖"
        echo ""
        echo "  Ubuntu: sudo apt install git python3 python3-pip"
        echo "  macOS: brew install git python"
        exit 1
    fi

    local py_ver=$(python3 --version 2>&1 | cut -d' ' -f2)
    local py_maj=$(echo $py_ver | cut -d'.' -f1)
    local py_min=$(echo $py_ver | cut -d'.' -f2)
    if [ "$py_maj" -lt 3 ] || ([ "$py_maj" -eq 3 ] && [ "$py_min" -lt 10 ]); then
        echo ""
        log_error "Python 版本过低: $py_ver (需要 >= 3.10)"
        exit 1
    fi

    echo ""
    log_success "依赖检查通过"
}

# ============================================
# 准备目录
# ============================================
prepare_dir() {
    echo -e "  ${BOLD}▸ 准备安装目录${NC}"
    echo ""

    if [ -d "${INSTALL_DIR}" ] && [ -f "${INSTALL_DIR}/pyproject.toml" ]; then
        if [ "$FORCE_REINSTALL" = true ]; then
            log_info "强制重装，删除旧目录"
            rm -rf "${INSTALL_DIR}"
        else
            echo -n "  检测到已安装，是否重装? [y/N]: "
            read -r REPLY
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "跳过安装"
                exit 0
            fi
            log_info "删除旧目录"
            rm -rf "${INSTALL_DIR}"
        fi
    fi

    mkdir -p "${INSTALL_DIR}"
    log_success "目录已创建: ${INSTALL_DIR}"
}

# ============================================
# 克隆仓库
# ============================================
clone_repo() {
    echo ""
    echo -e "  ${BOLD}▸ 下载代码${NC}"
    echo ""

    log_info "正在克隆仓库..."
    echo "    来源: ${REPO_URL}"
    echo "    目标: ${INSTALL_DIR}"
    echo ""

    if git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}" 2>&1; then
        echo ""
        log_success "下载完成"
    else
        echo ""
        log_error "克隆失败，请检查网络连接"
        exit 1
    fi
}

# ============================================
# 安装 Python 包
# ============================================
install_package() {
    echo ""
    echo -e "  ${BOLD}▸ 安装 Python 包${NC}"
    echo ""

    cd "${INSTALL_DIR}"

    if [ ! -f "pyproject.toml" ]; then
        log_error "pyproject.toml 不存在"
        exit 1
    fi

    log_info "正在安装..."
    echo ""

    local ok=false
    local method=""

    for cmd in \
        "pip install --user -e ." \
        "pip install --break-system-packages -e ." \
        "python3 -m pip install --user -e ." \
        "sudo python3 -m pip install -e ."; do

        log_dim "  尝试: $cmd"
        if eval "$cmd" 2>/dev/null; then
            ok=true
            method="$cmd"
            break
        fi
        echo ""
    done

    if [ "$ok" = true ]; then
        log_success "安装完成"
    else
        echo ""
        log_error "安装失败，请手动执行:"
        echo "    pip install --user -e ."
        exit 1
    fi
    echo ""

    if [ -d "${HOME}/.local/bin" ] && [[ ":$PATH:" != *":${HOME}/.local/bin:"* ]]; then
        echo -e "  ${YELLOW}!${NC} 建议添加 ${CYAN}~/.local/bin${NC} 到 PATH"
        echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        echo ""
    fi

    if command -v agenthub &>/dev/null; then
        local ver=$(agenthub --version 2>/dev/null || echo "unknown")
        echo -e "  ${GREEN}✓${NC} ${CYAN}agenthub${NC} ${DIM}(v${ver})${NC}"
    else
        echo -e "  ${YELLOW}!${NC} 请重新打开终端以使用 agenthub 命令"
    fi
}

# ============================================
# 初始化配置
# ============================================
init_config() {
    echo ""
    echo -e "  ${BOLD}▸ 初始化配置${NC}"
    echo ""

    for d in skills agents profile apps; do
        mkdir -p "${INSTALL_DIR}/$d"
    done

    if [ -f "${INSTALL_DIR}/profile/identity.yaml" ]; then
        log_info "配置已存在，跳过"
        return
    fi

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
    log_success "配置创建完成"
}

# ============================================
# 完成
# ============================================
print_complete() {
    echo ""
    echo -e "  ${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${GREEN}✓ 安装完成！${NC}"
    echo -e "  ${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  下一步:"
    echo "    vim ~/.agenthub/profile/identity.yaml"
    echo "    agenthub status"
    echo ""
    echo -e "  ${DIM}帮助: https://github.com/xuanyuanluoxue/AgentHub${NC}"
    echo ""
}

# ============================================
# 主流程
# ============================================
main() {
    check_deps
    prepare_dir
    clone_repo
    install_package
    init_config
    print_complete
}

main
