#!/bin/bash
# AgentHub 卸载脚本 - Linux/macOS/WSL
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

log_info() { echo -e "${BLUE}➜${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
print_divider() { echo -e "${DIM}$(printf '─%.0s' $(seq 1 50))${NC}"; }

INSTALL_DIR="${HOME}/.agenthub"
BACKUP_DIR="${HOME}/.agenthub.backup.$(date +%Y%m%d%H%M%S)"

# 确认卸载
confirm_uninstall() {
    echo -e "${BOLD}▸ 确认卸载${NC}"
    print_divider

    if [ ! -d "${INSTALL_DIR}" ]; then
        log_info "AgentHub 未安装，无需卸载"
        exit 0
    fi

    echo -e "${YELLOW}即将卸载 AgentHub${NC}"
    echo "  安装目录: ${INSTALL_DIR}"
    echo ""

    if [ -e /dev/tty ]; then
        echo -n "  是否备份当前配置? [y/N]: "
        read -n 1 -r < /dev/tty
        echo ""
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "备份到 ${BACKUP_DIR}..."
            mv "${INSTALL_DIR}" "${BACKUP_DIR}"
            log_success "备份完成"
            echo ""
            echo "  备份目录: ${BACKUP_DIR}"
            echo ""
        else
            log_warn "跳过备份，删除所有数据"
            rm -rf "${INSTALL_DIR}"
            log_success "卸载完成"
        fi
    else
        echo -n "  确认卸载? [y/N]: "
        read -n 1 -r
        echo ""
        echo ""

        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "取消卸载"
            exit 0
        fi

        rm -rf "${INSTALL_DIR}"
        log_success "卸载完成"
    fi

    # 尝试卸载 Python 包
    echo ""
    echo -e "${BOLD}▸ 卸载 Python 包${NC}"
    print_divider

    log_info "尝试卸载 agenthub Python 包..."
    pip uninstall agenthub -y 2>/dev/null && log_success "Python 包已卸载" || log_info "Python 包未安装或已移除"

    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  卸载完成！${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  如需重新安装:"
    echo "    curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/install.sh | bash"
    echo ""
}

confirm_uninstall
