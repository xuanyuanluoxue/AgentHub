#!/bin/bash
# AgentHub Linux/macOS/WSL 安装脚本
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

# 解析 -f 参数
for arg in "$@"; do
    case $arg in
        -f|--force) FORCE_REINSTALL=true ;;
    esac
done

# ============================================
# 日志
# ============================================
log_info() { echo -e "${BLUE}➜${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_dim() { echo -e "${DIM}$1${NC}"; }
print_divider() { echo -e "${DIM}$(printf '─%.0s' $(seq 1 50))${NC}"; }

# ============================================
# 检查依赖
# ============================================
check_deps() {
    echo -e "${BOLD}▸ 检查依赖${NC}"
    print_divider

    local all_ok=true

    for dep in git python3; do
        if command -v $dep &>/dev/null; then
            local ver=$($dep --version 2>/dev/null | head -1 | cut -d' ' -f1-2 | tr -d ' ')
            echo -e "  ${GREEN}✓${NC} ${CYAN}${dep}${NC} ${DIM}(${ver})${NC}"
        else
            echo -e "  ${RED}✗${NC} ${CYAN}${dep}${NC} ${DIM}(未找到)${NC}"
            all_ok=false
        fi
    done

    if [ "$all_ok" = false ]; then
        echo ""
        log_error "缺少依赖"
        echo "  Ubuntu: sudo apt install git python3 python3-pip"
        echo "  macOS: brew install git python"
        exit 1
    fi

    # 检查 Python 版本
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
    echo ""
}

# ============================================
# 准备目录
# ============================================
prepare_dir() {
    echo -e "${BOLD}▸ 准备安装目录${NC}"
    print_divider

    if [ -d "${INSTALL_DIR}" ] && [ -f "${INSTALL_DIR}/pyproject.toml" ]; then
        if [ "$FORCE_REINSTALL" = true ]; then
            log_info "强制重装，删除旧目录"
            rm -rf "${INSTALL_DIR}"
        else
            # 询问
            if [ -e /dev/tty ]; then
                echo -n "  检测到已安装，是否重装? [y/N]: "
                read -n 1 -r < /dev/tty
                echo ""
                echo ""
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log_info "跳过安装"
                    exit 0
                fi
            fi
            log_info "删除旧目录"
            rm -rf "${INSTALL_DIR}"
        fi
    fi

    log_info "创建目录: ${INSTALL_DIR}"
    mkdir -p "${INSTALL_DIR}"
    echo ""
}

# ============================================
# 克隆仓库
# ============================================
clone_repo() {
    echo -e "${BOLD}▸ 下载代码${NC}"
    print_divider

    log_info "克隆仓库..."
    echo "  来源: ${REPO_URL}"
    echo "  目标: ${INSTALL_DIR}"
    echo ""

    if git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}" 2>&1; then
        echo ""
        log_success "下载完成"
        echo ""
    else
        echo ""
        log_error "克隆失败，请检查网络"
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

    log_info "安装中..."
    echo ""

    local ok=false
    local method=""

    # 尝试多种安装方法
    for cmd in \
        "pip install --user -e ." \
        "pip install --break-system-packages -e ." \
        "python3 -m pip install --user -e ." \
        "sudo python3 -m pip install -e ."; do

        log_dim "  尝试: $cmd"
        if eval "$cmd" 2>/dev/null; then
            ok=true
            method=$cmd
            break
        fi
        echo ""
    done

    if [ "$ok" = true ]; then
        log_success "安装完成 ($method)"
    else
        log_error "安装失败，请手动执行: pip install --user -e ."
        exit 1
    fi
    echo ""

    # PATH 提示
    if [ -d "${HOME}/.local/bin" ] && [[ ":$PATH:" != *":${HOME}/.local/bin:"* ]]; then
        echo -e "  ${YELLOW}⚠${NC} 建议添加 ~/.local/bin 到 PATH"
        echo -e "  ${DIM}echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc${NC}"
        echo ""
    fi

    # 验证
    if command -v agenthub &>/dev/null; then
        local ver=$(agenthub --version 2>/dev/null || echo "unknown")
        echo -e "  ${GREEN}✓${NC} ${CYAN}agenthub${NC} ${DIM}(v${ver})${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} 请重新打开终端"
    fi
    echo ""
}

# ============================================
# 初始化配置
# ============================================
init_config() {
    echo -e "${BOLD}▸ 初始化配置${NC}"
    print_divider

    for d in skills agents profile apps; do
        mkdir -p "${INSTALL_DIR}/$d"
    done

    if [ -f "${INSTALL_DIR}/profile/identity.yaml" ]; then
        log_info "配置已存在，跳过"
        echo ""
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
    echo ""
}

# ============================================
# 完成
# ============================================
print_complete() {
    echo ""
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${GREEN}  安装完成！${NC}"
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  下一步:"
    echo "    vim ~/.agenthub/profile/identity.yaml"
    echo "    agenthub status"
    echo ""
    echo -e "${DIM}帮助: https://github.com/xuanyuanluoxue/AgentHub${NC}"
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
