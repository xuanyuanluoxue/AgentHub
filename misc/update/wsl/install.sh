#!/bin/bash
# AgentHub 更新脚本 (Linux/macOS/WSL)
set -e

INSTALL_DIR="${HOME}/.agenthub"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }

show_banner() {
    echo ""
    echo -e "  ${CYAN}    _                    _   _   _       _     ${NC}"
    echo -e "  ${CYAN}   / \   __ _  ___ _ __ | |_| | | |_   _| |__  ${NC}"
    echo -e "  ${CYAN}  / _ \ / _\` |/ _ \ '_ \| __| |_| | | | | '_ \ ${NC}"
    echo -e "  ${CYAN} / ___ \ (_| |  __/ | | | |_|  _  | |_| | |_) |${NC}"
    echo -e "  ${CYAN}/_/   \_\__, |\___|_| |_|\__|_| |_|\__,_|_.__/ ${NC}"
    echo -e "  ${CYAN}        |___/                               ${NC}"
    echo ""
    echo -e "  ${CYAN}AgentHub 更新${NC}"
    echo ""
}

do_update() {
    if [ ! -d "$INSTALL_DIR" ]; then
        log_warn "AgentHub 未安装，请先安装"
        echo "  安装命令:"
        echo "    curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash"
        echo ""
        exit 1
    fi

    log_info "拉取最新代码..."
    cd "$INSTALL_DIR"
    git pull 2>&1 | grep -v "Already up to date" || true
    echo ""

    log_info "更新 Python 包..."
    if pip install --user -e . 2>&1 | grep -qv "error"; then
        log_ok "Python 包已更新"
    else
        log_warn "Python 包更新失败，代码已更新"
    fi
    echo ""
}

main() {
    show_banner
    do_update

    echo -e "  ${GREEN}============================================${NC}"
    log_ok "更新完成！"
    echo -e "  ${GREEN}============================================${NC}"
    echo ""
}

main "$@"