#!/bin/bash
# AgentHub 安装路由脚本 (单文件版)
# 自动检测 OS 并下载对应子脚本执行
set -e

# ============================================
# 颜色
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

# ============================================
# 日志
# ============================================
log_info()  { echo -e "  ${BLUE}>${NC} $1"; }
log_success() { echo -e "  ${GREEN}✓${NC} $1"; }
log_warn()  { echo -e "  ${YELLOW}!${NC} $1"; }
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
                echo "linux"
            elif [ -d "/data/data/com.termux/files/home" ]; then
                echo "linux"
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
# 用法
# ============================================
print_usage() {
    echo ""
    echo -e "  ${CYAN}用法:${NC}"
    echo "    $0              # 交互式菜单"
    echo "    $0 --install    # 非交互式安装"
    echo "    $0 --uninstall  # 非交互式卸载"
    echo "    $0 --help       # 显示帮助"
    echo ""
    echo -e "  ${DIM}管道模式示例:${NC}"
    echo "    curl -fsSL .../install.sh | bash -- --install"
    echo ""
}

# ============================================
# 下载并执行子脚本
# ============================================
download_and_run() {
    local url="$1"
    local name="$2"

    echo -e "  ${DIM}下载 ${name}...${NC}"

    local content
    content=$(curl -fsSL --connect-timeout 15 --max-time 60 "$url" 2>&1) || {
        echo ""
        log_error "下载失败: $url"
        echo ""
        echo -e "  ${YELLOW}请检查网络连接，或稍后重试${NC}"
        echo ""
        exit 1
    }

    echo -e "  ${GREEN}下载成功${NC}"
    echo ""

    bash -c "$content"
}

# ============================================
# 主流程
# ============================================
main() {
    local action=""
    local os_type=""

    for arg in "$@"; do
        case $arg in
            --install|-i) action="install" ;;
            --uninstall|-u) action="uninstall" ;;
            --help|-h)
                print_banner
                print_usage
                exit 0
                ;;
        esac
    done

    print_banner

    os_type=$(detect_os)

    log_info "检测到操作系统: ${CYAN}${os_type}${NC}"
    echo ""

    if [ -z "$action" ]; then
        if ! [ -t 0 ]; then
            echo -e "  ${RED}x 管道模式需要 --install 或 --uninstall${NC}"
            echo ""
            print_usage
            exit 1
        fi

        echo "  请选择操作:"
        echo ""
        echo -e "    ${GREEN}[1]${NC} 安装 AgentHub"
        echo -e "    ${YELLOW}[2]${NC} 卸载 AgentHub"
        echo -e "    ${DIM}[3]${NC} 退出"
        echo ""
        echo -n "  请输入选项 [1-3]: "
        read -r choice
        echo ""

        case "$choice" in
            1) action="install" ;;
            2) action="uninstall" ;;
            3) log_info "退出"; exit 0 ;;
            *) echo -e "  ${YELLOW}! 无效选项${NC}"; exit 1 ;;
        esac
    fi

    local base_url="https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts"

    case "$action" in
        install)
            case "$os_type" in
                linux)
                    download_and_run "${base_url}/linux/install.sh" "Linux 安装脚本"
                    ;;
                macos)
                    download_and_run "${base_url}/macos/install.sh" "macOS 安装脚本"
                    ;;
                windows)
                    echo -e "  ${DIM}启动 Windows 安装程序...${NC}"
                    powershell -ExecutionPolicy Bypass -Command "irm ${base_url}/windows/install.ps1 | iex"
                    ;;
                *)
                    log_error "不支持的操作系统: $os_type"
                    exit 1
                    ;;
            esac
            ;;
        uninstall)
            case "$os_type" in
                linux)
                    download_and_run "${base_url}/linux/uninstall.sh" "Linux 卸载脚本"
                    ;;
                macos)
                    download_and_run "${base_url}/macos/uninstall.sh" "macOS 卸载脚本"
                    ;;
                windows)
                    echo -e "  ${DIM}启动 Windows 卸载程序...${NC}"
                    powershell -ExecutionPolicy Bypass -Command "irm ${base_url}/windows/uninstall.ps1 | iex"
                    ;;
                *)
                    log_error "不支持的操作系统: $os_type"
                    exit 1
                    ;;
            esac
            ;;
    esac
}

main "$@"