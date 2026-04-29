#!/bin/bash
# AgentHub Linux/macOS 安装脚本
set -e

INSTALL_DIR="${HOME}/.agenthub"
REPO_URL="https://github.com/xuanyuanluoxue/AgentHub.git"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
log_err() { echo -e "  ${RED}[X]${NC} $1"; }

check_deps() {
    echo "  检查系统依赖..."

    local git_ver=$(git --version 2>&1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1)
    if [ -n "$git_ver" ]; then
        log_ok "git $git_ver"
    else
        log_err "git 未找到"
        exit 1
    fi

    local python_cmd="python3"
    if ! command -v python3 &> /dev/null; then
        python_cmd="python"
    fi

    if command -v $python_cmd &> /dev/null; then
        local python_ver=$($python_cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        log_ok "python $python_ver"
    else
        log_err "python 未找到"
        exit 1
    fi

    echo ""
}

do_install() {
    log_info "正在下载..."
    echo "    来源: $REPO_URL" | sed 's|https://||'
    echo "    目标: $INSTALL_DIR"
    echo ""

    if git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" 2>&1 | grep -qv "Cloning"; then
        :
    fi

    if [ -d "$INSTALL_DIR/.git" ]; then
        log_ok "下载完成"
    else
        log_err "克隆失败"
        exit 1
    fi
    echo ""

    log_info "安装 Python 包..."
    cd "$INSTALL_DIR"

    local ok=false
    for cmd in "python3 -m pip install --user -e ." "python3 -m pip install -e ." "pip install --user -e ."; do
        log_info "尝试: $cmd"
        if eval "$cmd" 2>&1 | grep -qv "error"; then
            ok=true
            break
        fi
    done

    if $ok; then
        log_ok "安装完成"
    else
        log_err "安装失败，请手动执行: pip install --user -e ."
        exit 1
    fi
    echo ""
}

verify() {
    if command -v agenthub &> /dev/null; then
        local ver=$(agenthub --version 2>&1 || echo "unknown")
        log_ok "agenthub $ver"
    else
        log_warn "请重新打开终端以使用 agenthub 命令"
    fi
    echo ""
}

main() {
    check_deps
    do_install
    verify

    echo -e "  ${GREEN}============================================${NC}"
    log_ok "安装完成！"
    echo -e "  ${GREEN}============================================${NC}"
    echo ""
    echo "  下一步:"
    echo "    agenthub --help"
    echo ""
}

main "$@"