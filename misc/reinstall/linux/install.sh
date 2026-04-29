#!/bin/bash
# AgentHub 重装脚本 (Linux/macOS/WSL) - 恢复出厂设置
set -e

INSTALL_DIR="${HOME}/.agenthub"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }

show_banner() {
    echo ""
    echo -e "  ${RED}    _                    _   _   _       _     ${NC}"
    echo -e "  ${RED}   / \   __ _  ___ _ __ | |_| | | |_   _| |__  ${NC}"
    echo -e "  ${RED}  / _ \ / _\` |/ _ \ '_ \| __| |_| | | | | '_ \ ${NC}"
    echo -e "  ${RED} / ___ \ (_| |  __/ | | | |_|  _  | |_| | |_) |${NC}"
    echo -e "  ${RED}/_/   \_\__, |\___|_| |_|\__|_| |_|\__,_|_.__/ ${NC}"
    echo -e "  ${RED}        |___/                               ${NC}"
    echo ""
    echo -e "  ${CYAN}AgentHub 恢复出厂设置${NC}"
    echo ""
}

REPO_URL="https://github.com/xuanyuanluoxue/AgentHub.git"

do_reinstall() {
    log_warn "即将删除所有数据并重新安装"
    echo "    目录: $INSTALL_DIR"
    echo ""

    if [ -d "$INSTALL_DIR" ]; then
        log_info "删除旧版本..."
        rm -rf "$INSTALL_DIR"
    fi

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

    log_info "排除 misc/ 目录..."
    rm -rf "$INSTALL_DIR/misc"
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
        log_err "安装失败"
        exit 1
    fi
    echo ""
}

main() {
    show_banner
    do_reinstall

    echo -e "  ${GREEN}============================================${NC}"
    log_ok "恢复出厂设置完成！"
    echo -e "  ${GREEN}============================================${NC}"
    echo ""
    echo "  下一步:"
    echo "    agenthub --help"
    echo ""
}

main "$@"