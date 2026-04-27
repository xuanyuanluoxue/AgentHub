#!/bin/bash
# AgentHub 安装路由脚本
# 自动检测操作系统并路由到对应安装/卸载脚本
#
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/install.sh | bash
#   bash install.sh
#
# 卸载:
#   curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/install.sh | bash --uninstall
#   bash install.sh --uninstall
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
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ============================================
# 日志
# ============================================
log_info() { echo -e "${BLUE}➜${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

# ============================================
# Banner (无边框)
# ============================================
print_banner() {
    echo ""
    echo -e "${BOLD}${MAGENTA}  ██╗   ██╗ ██████╗ ██████╗ ██████╗ ██╗   ██╗${NC}"
    echo -e "${BOLD}${MAGENTA}  ██║   ██║██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝${NC}"
    echo -e "${BOLD}${MAGENTA}  ██║   ██║██║   ██║██████╔╝██████╔╝ ╚████╔╝ ${NC}"
    echo -e "${BOLD}${MAGENTA}  ╚██╗ ██╔╝██║   ██║██╔══██╗██╔══██╗  ╚██╔╝  ${NC}"
    echo -e "${BOLD}${MAGENTA}   ╚████╔╝ ╚██████╔╝██████╔╝██████╔╝   ██║   ${NC}"
    echo -e "${BOLD}${MAGENTA}    ╚═══╝   ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝   ${NC}"
    echo ""
    echo -e "  ${CYAN}统一 AI 工具四大共享生态${NC}"
    echo -e "  ${DIM}Skill · Agent · 画像 · 记忆系统${NC}"
    echo ""
}

# ============================================
# 检测操作系统
# ============================================
detect_os() {
    local os_name=""
    local os_type=""

    case "$(uname -s)" in
        Linux*)
            if grep -qiE "(microsoft|wsl)" /proc/version 2>/dev/null; then
                os_name="WSL (Windows Subsystem for Linux)"
                os_type="linux"
            else
                os_name="Linux"
                os_type="linux"
            fi
            ;;
        Darwin*)
            os_name="macOS"
            os_type="macos"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            os_name="Windows (Git Bash / MinGW)"
            os_type="windows"
            ;;
        *)
            os_name="$(uname -s)"
            os_type="unknown"
            ;;
    esac

    echo "$os_type"
    echo "$os_name"
}

# ============================================
# 检测是否为已安装
# ============================================
is_installed() {
    if [ -d "${HOME}/.agenthub" ] && [ -f "${HOME}/.agenthub/pyproject.toml" ]; then
        return 0
    fi
    return 1
}

# ============================================
# 下载并执行子脚本
# ============================================
download_and_run() {
    local url="$1"
    local name="$2"
    shift 2

    echo -e "${DIM}正在下载 ${name}...${NC}"

    local content
    content=$(curl -fsSL --connect-timeout 15 --max-time 60 "$url" 2>&1) || {
        local err=$?
        echo ""
        log_error "下载失败 (错误码: $err)"
        echo ""
        echo -e "${YELLOW}可能的原因:${NC}"
        echo "  1. 网络连接不稳定"
        echo "  2. DNS 解析失败"
        echo "  3. 该网络环境限制了对 GitHub 的访问"
        echo ""
        echo -e "${CYAN}解决方案:${NC}"
        echo "  1. 稍后重试"
        echo "  2. 切换到手机热点或其他网络"
        echo "  3. 使用 VPN"
        echo "  4. 直接克隆仓库: git clone https://github.com/xuanyuanluoxue/AgentHub.git ~/.agenthub"
        echo ""
        echo -e "${DIM}帮助文档: https://github.com/xuanyuanluoxue/AgentHub${NC}"
        echo ""
        exit 1
    }

    echo -e "${GREEN}下载成功${NC}"
    echo ""
    echo "$content" | bash -s -- "$@"
}

# ============================================
# 显示菜单
# ============================================
show_menu() {
    echo -e "${BOLD}请选择操作:${NC}"
    echo ""
    echo "  ${CYAN}1${NC}. 安装 AgentHub"
    echo "  ${CYAN}2${NC}. 卸载 AgentHub"
    echo "  ${CYAN}3${NC}. 退出"
    echo ""
}

# ============================================
# 主流程
# ============================================
main() {
    local action=""

    # 解析参数
    for arg in "$@"; do
        case $arg in
            --install|-i) action="install" ;;
            --uninstall|-u) action="uninstall" ;;
            --help|-h)
                echo "用法: $0 [--install|--uninstall]"
                echo "  --install, -i   安装"
                echo "  --uninstall, -u 卸载"
                exit 0
                ;;
        esac
    done

    print_banner

    # 检测操作系统
    local os_type=$(detect_os | head -1)
    local os_name=$(detect_os | tail -1)

    log_info "检测到操作系统: ${CYAN}${os_name}${NC}"
    echo ""

    # 如果没有指定操作，显示菜单
    if [ -z "$action" ]; then
        if is_installed; then
            echo -e "${YELLOW}⚠  检测到已安装 AgentHub${NC}"
            echo ""
        fi

        show_menu

        if [ -e /dev/tty ]; then
            echo -n "请输入选项 [1-3]: "
            read -n 1 -r choice < /dev/tty
            echo ""
        else
            echo -n "请输入选项 [1-3]: "
            read -n 1 -r choice
            echo ""
        fi
        echo ""

        case "$choice" in
            1) action="install" ;;
            2) action="uninstall" ;;
            *) log_info "退出"; exit 0 ;;
        esac
    fi

    # 执行操作
    case "$action" in
        install)
            if is_installed; then
                echo -e "${YELLOW}⚠  检测到已安装 AgentHub${NC}"
                echo ""

                if [ -e /dev/tty ]; then
                    echo -n "  是否重新安装? [y/N]: "
                    read -n 1 -r < /dev/tty
                    echo ""
                    echo ""
                    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                        log_info "跳过安装"
                        exit 0
                    fi
                else
                    log_warn "已安装，跳过安装"
                    exit 0
                fi
            fi
            ;;

        uninstall)
            case "$os_type" in
                linux|macos)
                    download_and_run \
                        "https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/${os_type}/uninstall.sh" \
                        "${os_name} 卸载脚本"
                    exit 0
                    ;;
                windows)
                    powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/windows/uninstall.ps1 | iex"
                    exit 0
                    ;;
                *)
                    log_error "不支持的操作系统: $os_name"
                    exit 1
                    ;;
            esac
            ;;
    esac

    # 安装流程
    case "$os_type" in
        linux|macos)
            log_info "正在启动 ${os_name} 安装程序..."
            echo ""
            download_and_run \
                "https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/${os_type}/install.sh" \
                "${os_name} 安装脚本"
            ;;
        windows)
            log_info "正在启动 Windows 安装程序..."
            echo ""
            powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/windows/install.ps1 | iex"
            ;;
        *)
            log_error "不支持的操作系统: $os_name"
            echo ""
            echo "请手动安装: https://github.com/xuanyuanluoxue/AgentHub"
            exit 1
            ;;
    esac
}

main "$@"
