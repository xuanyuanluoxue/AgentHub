#!/bin/bash
# AgentHub 打开项目目录 (Linux/macOS/WSL)
set -e

INSTALL_DIR="${HOME}/.agenthub"

CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "  ${CYAN}>${NC} $1"; }

do_open() {
    if [ ! -d "$INSTALL_DIR" ]; then
        echo "  AgentHub 未安装"
        exit 1
    fi

    log_info "打开目录: $INSTALL_DIR"
    echo ""

    case "$(uname -s)" in
        Darwin*)
            open "$INSTALL_DIR"
            ;;
        Linux*)
            if command -v xdg-open &> /dev/null; then
                xdg-open "$INSTALL_DIR"
            elif command -v nautilus &> /dev/null; then
                nautilus "$INSTALL_DIR"
            else
                echo "  无法自动打开，请手动打开: $INSTALL_DIR"
            fi
            ;;
    esac

    echo ""
    log_info "已打开项目目录"
}

do_open