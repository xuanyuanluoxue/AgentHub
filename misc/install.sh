#!/bin/bash
# AgentHub 安装路由脚本
#
set -e

# ============================================
# 颜色定义
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
# 配置
# ============================================
REPO_RAW="https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc"
INSTALL_DIR="${HOME}/.agenthub"

# ============================================
# 日志
# ============================================
log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_success() { echo -e "  ${GREEN}✓${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}!${NC} $1"; }
log_error() { echo -e "  ${RED}x${NC} $1"; }

# ============================================
# Banner
# ============================================
print_banner() {
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
    [ -d "${HOME}/.agenthub" ] && [ -f "${HOME}/.agenthub/pyproject.toml" ]
}

# ============================================
# 下载并执行远程脚本
# ============================================
download_and_run() {
    local script="$1"
    shift
    curl -fsSL "${REPO_RAW}/${script}" | bash -s -- "$@"
}

# ============================================
# 主流程
# ============================================
main() {
    local action=""

    for arg in "$@"; do
        case $arg in
            --install|-i) action="install" ;;
            --uninstall|-u) action="uninstall" ;;
            --help|-h)
                echo "用法: $0 [--install|--uninstall]"
                echo "  --install, -i   安装"
                echo "  --uninstall, -u  卸载"
                exit 0
                ;;
        esac
    done

    print_banner

    local os_type=$(detect_os)
    log_info "检测到操作系统: ${CYAN}${os_type}${NC}"
    echo ""

    # 非交互模式：管道输入时必须指定参数
    if [ -z "$action" ]; then
        if [ -t 0 ]; then
            # 终端模式，显示菜单
            if is_installed; then
                echo -e "  ${YELLOW}! 检测到已安装 AgentHub${NC}"
                echo ""
            fi
            echo "  请选择操作:"
            echo ""
            echo -e "    ${GREEN}[1]${NC} 安装 AgentHub"
            echo -e "    ${YELLOW}[2]${NC} 卸载 AgentHub"
            echo -e "    ${DIM}[3]${NC} 退出"
            echo ""
            echo -n "  请输入选项 [1-3]: "
            read choice
            echo ""
            case "$choice" in
                1) action="install" ;;
                2) action="uninstall" ;;
                *) log_info "退出"; exit 0 ;;
            esac
        else
            log_error "管道模式需要指定参数: --install 或 --uninstall"
            echo "  用法: curl -fsSL ... | bash -s -- --install"
            exit 1
        fi
    fi

    case "$action" in
        install)
            if is_installed; then
                echo -e "  ${YELLOW}! 检测到已安装${NC}"
                echo ""
                echo -n "  是否重新安装? [y/N]: "
                read -r REPLY
                echo ""
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log_info "跳过安装"
                    exit 0
                fi
            fi
            download_and_run "install-${os_type}.sh" "$@"
            ;;
        uninstall)
            download_and_run "uninstall-${os_type}.sh" "$@"
            ;;
    esac
}

main "$@"