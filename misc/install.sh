#!/bin/bash
# AgentHub 管理脚本
# 用法:
#   curl -fsSL ... | bash              # 交互模式
#   curl -fsSL ... | bash -s -- <cmd>   # 非交互模式
set -e

REPO_RAW="https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc"

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

show_banner() {
    echo ""
    echo -e "  ${CYAN}    _                    _   _   _       _     ${NC}"
    echo -e "  ${CYAN}   / \   __ _  ___ _ __ | |_| | | |_   _| |__  ${NC}"
    echo -e "  ${CYAN}  / _ \ / _\` |/ _ \ '_ \| __| |_| | | | | '_ \ ${NC}"
    echo -e "  ${CYAN} / ___ \ (_| |  __/ | | | |_|  _  | |_| | |_) |${NC}"
    echo -e "  ${CYAN}/_/   \_\__, |\___|_| |_|\__|_| |_|\__,_|_.__/ ${NC}"
    echo -e "  ${CYAN}        |___/                               ${NC}"
    echo ""
    echo -e "  ${CYAN}AgentHub 管理工具${NC}"
    echo ""
}

detect_os() {
    case "$(uname -s)" in
        Linux*)
            if grep -qiE "(microsoft|wsl)" /proc/version 2>/dev/null; then
                echo "wsl"
            else
                echo "linux"
            fi
            ;;
        Darwin*)
            echo "macos"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

download_and_run() {
    local cmd="$1"
    local os="$2"
    curl -fsSL "${REPO_RAW}/${cmd}/${os}/install.sh" | bash
}

show_menu() {
    show_banner

    echo "  请选择操作:"
    echo ""
    echo -e "    ${GREEN}[1]${NC} 安装 AgentHub"
    echo -e "    ${YELLOW}[2]${NC} 卸载 AgentHub"
    echo -e "    ${CYAN}[3]${NC} 更新 AgentHub"
    echo -e "    ${RED}[4]${NC} 恢复出厂设置"
    echo -e "    ${BLUE}[5]${NC} 打开项目目录"
    echo -e "    ${DIM}[6]${NC} 退出"
    echo ""
    echo -n "  请输入选项 [1-6]: "
    read choice
    echo ""

    case "$choice" in
        1) cmd="install" ;;
        2) cmd="uninstall" ;;
        3) cmd="update" ;;
        4) cmd="reinstall" ;;
        5) cmd="open" ;;
        *) log_info "退出"; exit 0 ;;
    esac

    echo "$cmd"
}

main() {
    local cmd=""
    local os_type=$(detect_os)

    for arg in "$@"; do
        case $arg in
            install|i) cmd="install" ;;
            uninstall|u) cmd="uninstall" ;;
            update) cmd="update" ;;
            reinstall|r) cmd="reinstall" ;;
            open|o) cmd="open" ;;
            --help|-h)
                echo "用法: $0 [install|uninstall|update|reinstall|open]"
                echo "  install, i     安装"
                echo "  uninstall, u   卸载"
                echo "  update         更新"
                echo "  reinstall, r   恢复出厂设置"
                echo "  open, o       打开项目目录"
                exit 0
                ;;
        esac
    done

    # 交互模式
    if [ -z "$cmd" ]; then
        if [ -t 0 ]; then
            cmd=$(show_menu)
        else
            log_err "管道模式需要指定命令"
            echo ""
            echo "  用法: curl -fsSL ... | bash -s -- install"
            echo "        curl -fsSL ... | bash -s -- uninstall"
            echo "        curl -fsSL ... | bash -s -- update"
            echo "        curl -fsSL ... | bash -s -- reinstall"
            echo "        curl -fsSL ... | bash -s -- open"
            exit 1
        fi
    fi

    log_info "检测到系统: ${CYAN}${os_type}${NC}"
    echo ""

    download_and_run "$cmd" "$os_type"
}

main "$@"