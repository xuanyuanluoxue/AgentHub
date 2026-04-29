#!/bin/bash
# AgentHub Linux/macOS 卸载脚本
set -e

INSTALL_DIR="${HOME}/.agenthub"
BACKUP_DIR="${HOME}/.agenthub.backup.$(date +%Y%m%d%H%M%S)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }

do_uninstall() {
    if [ ! -d "$INSTALL_DIR" ]; then
        log_info "AgentHub 未安装，无需卸载"
        exit 0
    fi

    log_warn "即将卸载 AgentHub"
    echo "    目录: $INSTALL_DIR"
    echo ""

    log_info "是否备份? [y/N]: "
    read -r REPLY
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "备份到 $BACKUP_DIR..."
        mv "$INSTALL_DIR" "$BACKUP_DIR"
        log_ok "备份完成"
    else
        log_info "删除所有数据..."
        rm -rf "$INSTALL_DIR"
        log_ok "删除完成"
    fi

    echo ""
    log_info "卸载 Python 包..."
    pip uninstall agenthub -y 2>/dev/null && log_ok "Python 包已卸载" || log_info "Python 包未安装或已移除"
    echo ""
}

main() {
    do_uninstall

    echo -e "  ${GREEN}============================================${NC}"
    log_ok "卸载完成！"
    echo -e "  ${GREEN}============================================${NC}"
    echo ""
}

main "$@"