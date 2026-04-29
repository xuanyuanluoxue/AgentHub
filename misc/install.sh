#!/bin/bash
# AgentHub 安装路由脚本
# 用法:
#   curl -fsSL ... | bash              # 交互模式
#   curl -fsSL ... | bash -s -- install   # 非交互模式
set -e

REPO_RAW="https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install"

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
    echo -e "  ${GREEN}    _                    _   _   _       _     ${NC}"
    echo -e "  ${GREEN}   / \\   __ _  ___ _ __ | |_| | | |_   _| |__  ${NC}"
    echo -e "  ${GREEN}  / _ \\ / _\` |/ _ \\ '_ \\| __| |_| | | | | '_ \\ ${NC}"
    echo -e "  ${GREEN} / ___ \\ (_| |  __/ | | | |_|  _  | |_| | |_) |${NC}"
    echo -e "  ${GREEN}/_/   \\_\\__, |\\___|_| |_|\__|_| |_|\\__,_|_.__/ ${NC}"
    echo -e "  ${GREEN}        |___/                               ${NC}"
    echo ""
    echo -e "  ${CYAN}统一 AI 工具四大共享生态${NC}"
    echo -e "  ${CYAN}Skill · Agent · 画像 · 记忆${NC}"
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

# 下载并执行对应系统的脚本
download_and_run() {
    local os="$1"
    shift
    curl -fsSL "${REPO_RAW}/${os}/install.sh" | bash -s -- "$@"
}

main() {
    local action=""

    for arg in "$@"; do
        case $arg in
            install|i) action="install" ;;
            uninstall|u) action="uninstall" ;;
            update) action="update" ;;
            reinstall|r) action="reinstall" ;;
            --help|-h)
                echo "用法: $0 [install|uninstall|update|reinstall]"
                echo "  install, i     安装"
                echo "  uninstall, u   卸载"
                echo "  update         更新"
                echo "  reinstall, r   恢复出厂设置"
                exit 0
                ;;
        esac
    done

    local os_type=$(detect_os)

    if [ -n "$action" ]; then
        download_and_run "$os_type" "$@"
        return
    fi

    # 交互模式
    if [ -t 0 ]; then
        show_banner
        log_info "检测到系统: ${CYAN}${os_type}${NC}"
        echo ""
        echo "  请选择操作:"
        echo ""
        echo -e "    ${GREEN}[1]${NC} 安装 AgentHub"
        echo -e "    ${YELLOW}[2]${NC} 卸载 AgentHub"
        echo -e "    ${CYAN}[3]${NC} 更新 AgentHub"
        echo -e "    ${RED}[4]${NC} 恢复出厂设置"
        echo -e "    ${DIM}[5]${NC} 退出"
        echo ""
        echo -n "  请输入选项 [1-5]: "
        read choice
        echo ""

        case "$choice" in
            1) action="install" ;;
            2) action="uninstall" ;;
            3) action="update" ;;
            4) action="reinstall" ;;
            *) log_info "退出"; exit 0 ;;
        esac

        download_and_run "$os_type" "$action"
    else
        log_err "管道模式需要指定操作"
        echo ""
        echo "  用法: curl -fsSL ... | bash -s -- install"
        echo "        curl -fsSL ... | bash -s -- uninstall"
        echo "        curl -fsSL ... | bash -s -- update"
        echo "        curl -fsSL ... | bash -s -- reinstall"
        exit 1
    fi
}

main "$@"