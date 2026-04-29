#!/bin/bash
# AgentHub Linux/macOS 更新脚本
set -e

INSTALL_DIR="${HOME}/.agenthub"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }

do_update() {
    if [ ! -d "$INSTALL_DIR" ]; then
        log_err "AgentHub 未安装"
        exit 1
    fi

    log_info "拉取最新代码..."
    cd "$INSTALL_DIR"
    git pull 2>&1 | grep -v "Already up to date" || true

    log_info "更新 Python 包..."
    pip install --user -e . 2>&1 | grep -qv "error" && log_ok "Python 包更新完成" || log_warn "Python 包更新失败"

    echo ""
}

main() {
    do_update

    echo -e "  ${GREEN}============================================${NC}"
    log_ok "更新完成！"
    echo -e "  ${GREEN}============================================${NC}"
    echo ""
}

main "$@"