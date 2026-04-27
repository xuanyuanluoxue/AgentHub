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
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ============================================
# 日志
# ============================================
log_info() { echo -e "${BLUE}>${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}!${NC} $1"; }
log_error() { echo -e "${RED}x${NC} $1"; }

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
    local os_name=""
    local os_type=""

    case "$(uname -s)" in
        Linux*)
            if grep -qiE "(microsoft|wsl)" /proc/version 2>/dev/null; then
                os_name="WSL"
                os_type="linux"
            elif [ -d "/data/data/com.termux/files/home" ]; then
                os_name="Termux"
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
            os_name="Windows"
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

    echo -e "  ${DIM}正在下载 ${name}...${NC}"

    local content
    content=$(curl -fsSL --connect-timeout 15 --max-time 60 "$url" 2>&1) || {
        local err=$?
        echo ""
        log_error "下载失败 (错误码: $err)"
        echo ""
        echo -e "  ${YELLOW}可能的原因:${NC}"
        echo "    1. 网络连接不稳定"
        echo "    2. DNS 解析失败"
        echo "    3. 该网络环境限制了对 GitHub 的访问"
        echo ""
        echo -e "  ${CYAN}解决方案:${NC}"
        echo "    1. 稍后重试"
        echo "    2. 切换到手机热点或其他网络"
        echo "    3. 使用 VPN"
        echo "    4. 直接克隆: git clone https://github.com/xuanyuanluoxue/AgentHub.git ~/.agenthub"
        echo ""
        exit 1
    }

    echo -e "  ${GREEN}下载成功${NC}"
    echo ""

    bash -c "$content" -- "$@"
}

# ============================================
# 显示菜单
# ============================================
show_menu() {
    echo "  请选择操作:"
    echo ""
    echo -e "    ${GREEN}[1]${NC} 安装 AgentHub"
    echo -e "    ${YELLOW}[2]${NC} 卸载 AgentHub"
    echo -e "    ${DIM}[3]${NC} 退出"
    echo ""
}

# ============================================
# 读取用户选择
# ============================================
get_choice() {
    echo -n "  请输入选项 [1-3]: "
    read -r choice
    echo ""
    echo "$choice"
}

# ============================================
# 主流程
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

main() {
    local action=""

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

    local os_type=$(detect_os | head -1)
    local os_name=$(detect_os | tail -1)

    log_info "检测到操作系统: ${CYAN}${os_name}${NC}"
    echo ""

    if [ -z "$action" ]; then
        if ! [ -t 0 ]; then
            echo -e "  ${RED}x 错误: 管道模式必须指定操作${NC}"
            echo ""
            print_usage
            exit 1
        fi

        if is_installed; then
            echo -e "  ${YELLOW}! 检测到已安装 AgentHub${NC}"
            echo ""
        fi

        show_menu
        local choice=$(get_choice)

        case "$choice" in
            1) action="install" ;;
            2) action="uninstall" ;;
            3) log_info "退出"; exit 0 ;;
            *) echo -e "  ${YELLOW}! 无效选项${NC}"; exit 1 ;;
        esac
    fi

    case "$action" in
        install)
            if is_installed; then
                echo -e "  ${YELLOW}! 检测到已安装 AgentHub${NC}"
                echo ""
                echo -n "  是否重新安装? [y/N]: "
                read -r reply
                echo ""
                if [[ ! $reply =~ ^[Yy]$ ]]; then
                    log_info "跳过安装"
                    exit 0
                fi
            fi
            ;;

        uninstall)
            case "$os_type" in
                linux|macos)
                    log_info "正在启动 ${os_name} 卸载程序..."
                    download_and_run \
                        "https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/${os_type}/uninstall.sh" \
                        "${os_name} 卸载脚本"
                    exit 0
                    ;;
                windows)
                    log_info "正在启动 Windows 卸载程序..."
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
            echo "  请手动安装: https://github.com/xuanyuanluoxue/AgentHub"
            exit 1
            ;;
    esac
}

main "$@"
