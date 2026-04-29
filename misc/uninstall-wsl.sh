#!/bin/bash
# AgentHub 卸载脚本 (Linux/macOS/WSL)
#
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="${HOME}/.agenthub"
BACKUP_DIR="${HOME}/.agenthub.backup.$(date +%Y%m%d%H%M%S)"

log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_success() { echo -e "  ${GREEN}✓${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}!${NC} $1"; }

main() {
    echo ""
    echo -e "  ${YELLOW}▸ 确认卸载${NC}"
    echo ""

    if [ ! -d "${INSTALL_DIR}" ]; then
        log_info "AgentHub 未安装，无需卸载"
        exit 0
    fi

    log_warn "即将卸载 AgentHub"
    echo "    目录: ${INSTALL_DIR}"
    echo ""

    echo -n "  是否备份当前配置? [y/N]: "
    read -r REPLY
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "备份到 ${BACKUP_DIR}..."
        mv "${INSTALL_DIR}" "${BACKUP_DIR}"
        log_success "备份完成"
        echo "    备份目录: ${BACKUP_DIR}"
    else
        log_warn "跳过备份，删除所有数据"
        rm -rf "${INSTALL_DIR}"
        log_success "卸载完成"
    fi

    echo ""
    echo -e "  ${BOLD}▸ 卸载 Python 包${NC}"
    echo ""

    log_info "正在卸载 agenthub..."
    pip uninstall agenthub -y 2>/dev/null && log_success "Python 包已卸载" || log_info "Python 包未安装或已移除"

    echo ""
    echo -e "  ${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${GREEN}✓ 卸载完成！${NC}"
    echo -e "  ${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  重新安装:"
    echo "    curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash"
    echo ""
}

main "$@"