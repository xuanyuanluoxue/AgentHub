#!/bin/bash
# AgentHub 安装路由脚本
# 支持: install | uninstall | update | reinstall
set -e

# ============================================
# 配置
# ============================================
REPO_RAW="https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc"
INSTALL_DIR="${HOME}/.agenthub"

# ============================================
# 颜色
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ============================================
# 日志
# ============================================
log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
log_err() { echo -e "  ${RED}[X]${NC} $1"; }

# ============================================
# Banner
# ============================================
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
    echo -e "  ${DIM}Skill · Agent · 画像 · 记忆${NC}"
    echo ""
}

# ============================================
# 检测操作系统
# ============================================
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

# ============================================
# 检测是否已安装
# ============================================
is_installed() {
    [ -d "${INSTALL_DIR}" ] && [ -f "${INSTALL_DIR}/pyproject.toml" ]
}

# ============================================
# 下载并执行远程脚本
# ============================================
download_script() {
    local script="$1"
    curl -fsSL "${REPO_RAW}/${script}"
}

# ============================================
# 显示菜单
# ============================================
show_menu() {
    show_banner

    if is_installed; then
        echo -e "  ${YELLOW}检测到已安装 AgentHub${NC}"
        echo ""
    fi

    echo "  请选择操作:"
    echo ""
    echo -e "    ${GREEN}[1]${NC} 安装 AgentHub"
    echo -e "    ${YELLOW}[2]${NC} 卸载 AgentHub"
    echo -e "    ${CYAN}[3]${NC} 更新 AgentHub"
    echo -e "    ${RED}[4]${NC} 恢复出厂设置"
    echo -e "    ${DIM}[5]${NC} 退出"
    echo ""
}

# ============================================
# 主流程
# ============================================
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

    if [ -z "$action" ]; then
        if [ -t 0 ]; then
            show_menu
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
        else
            log_err "管道模式需要指定操作: install | uninstall | update | reinstall"
            echo "  用法: curl -fsSL ... | bash -s -- install"
            exit 1
        fi
    fi

    case "$os_type" in
        windows)
            case "$action" in
                install)
                    powershell -ExecutionPolicy Bypass -File "$0.ps1" -Action install
                    ;;
                uninstall)
                    powershell -ExecutionPolicy Bypass -File "$0.ps1" -Action uninstall
                    ;;
                update)
                    powershell -ExecutionPolicy Bypass -File "$0.ps1" -Action update
                    ;;
                reinstall)
                    powershell -ExecutionPolicy Bypass -File "$0.ps1" -Action reinstall
                    ;;
            esac
            ;;
        linux|macos|wsl)
            case "$action" in
                install)
                    show_banner
                    log_info "检测到系统: ${CYAN}${os_type}${NC}"
                    echo ""
                    download_script "install-${os_type}.sh" | bash
                    ;;
                uninstall)
                    show_banner
                    download_script "uninstall-${os_type}.sh" | bash
                    ;;
                update)
                    show_banner
                    download_script "update-${os_type}.sh" | bash
                    ;;
                reinstall)
                    show_banner
                    log_info "检测到系统: ${CYAN}${os_type}${NC}"
                    echo ""
                    download_script "uninstall-${os_type}.sh" | bash
                    echo ""
                    download_script "install-${os_type}.sh" | bash
                    ;;
            esac
            ;;
        *)
            log_err "不支持的操作系统: $(uname -s)"
            exit 1
            ;;
    esac
}

main "$@"