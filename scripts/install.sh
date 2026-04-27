#!/bin/bash
# AgentHub 一键安装脚本 (单文件版)
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

log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_success() { echo -e "  ${GREEN}✓${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}!${NC} $1"; }
log_error() { echo -e "  ${RED}x${NC} $1"; }

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

detect_os() {
    case "$(uname -s)" in
        Linux*)
            if grep -qiE "(microsoft|wsl)" /proc/version 2>/dev/null; then
                echo "linux:wsl"
            elif [ -d "/data/data/com.termux/files/home" ]; then
                echo "linux:termux"
            else
                echo "linux:linux"
            fi
            ;;
        Darwin*)
            echo "macos:macos"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows:windows"
            ;;
        *)
            echo "unknown:$(uname -s)"
            ;;
    esac
}

is_installed() {
    [ -d "${HOME}/.agenthub" ] && [ -f "${HOME}/.agenthub/pyproject.toml" ]
}

confirm_reinstall() {
    echo -n "  是否重新安装? [y/N]: "
    read -r reply
    echo ""
    [[ $reply =~ ^[Yy]$ ]]
}

print_usage() {
    echo ""
    echo -e "  ${CYAN}用法:${NC}"
    echo "    $0              # 交互式安装（菜单）"
    echo "    $0 --install    # 非交互式安装"
    echo "    $0 --uninstall  # 非交互式卸载"
    echo "    $0 --help       # 显示帮助"
    echo ""
    echo -e "  ${DIM}管道模式:${NC}"
    echo "    curl -fsSL .../install.sh | bash -- --install"
    echo ""
}

# ========================================
# Linux/macOS 安装
# ========================================
do_linux_install() {
    local install_dir="${HOME}/.agenthub"
    local repo_url="https://github.com/xuanyuanluoxue/AgentHub.git"

    echo -e "  ${DIM}▸ 准备安装到 ${install_dir}${NC}"
    echo ""

    if is_installed; then
        echo -e "  ${YELLOW}! 检测到已安装 AgentHub${NC}"
        echo ""
        if ! confirm_reinstall; then
            log_info "跳过安装"
            return 0
        fi
        echo -e "  ${DIM}▸ 重新安装中...${NC}"
    fi

    echo -e "  ${DIM}▸ 检查依赖...${NC}"
    local missing=()
    for cmd in git curl; do
        if ! command -v $cmd &>/dev/null; then
            missing+=($cmd)
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "缺少依赖: ${missing[*]}"
        echo "  请先安装: sudo apt install ${missing[*]}"
        return 1
    fi
    echo -e "  ${GREEN}✓ 依赖检查通过${NC}"
    echo ""

    if [ -d "$install_dir" ]; then
        log_info "更新现有安装..."
        cd "$install_dir"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
    else
        log_info "克隆仓库..."
        git clone --depth 1 "$repo_url" "$install_dir"
    fi

    echo ""
    log_success "安装完成!"
    echo ""
    echo -e "  ${DIM}下一步:${NC}"
    echo "    cd $install_dir"
    echo "    pip install -e ."
    echo "    agenthub init"
    echo ""
}

do_linux_uninstall() {
    local install_dir="${HOME}/.agenthub"

    echo ""
    echo -e "  ${RED}⚠ 确认卸载 AgentHub${NC}"
    echo "    目录: $install_dir"
    echo ""

    echo -n "  此操作不可恢复，是否继续? [y/N]: "
    read -r reply
    echo ""

    if [[ ! $reply =~ ^[Yy]$ ]]; then
        log_info "取消卸载"
        return 0
    fi

    if [ -d "$install_dir" ]; then
        rm -rf "$install_dir"
        log_success "卸载完成"
    else
        log_warn "未检测到安装目录"
    fi
}

# ========================================
# Windows 安装
# ========================================
do_windows_install() {
    local install_dir="$HOME\.agenthub"

    echo -e "  ${DIM}▸ 准备安装到 ${install_dir}${NC}"
    echo ""

    if (Test-Path "$install_dir\pyproject.toml") {
        echo -e "  ${YELLOW}! 检测到已安装 AgentHub${NC}"
        echo ""
        if (-not $ForceReinstall) {
            echo -n "  是否重新安装? [y/N]: "
            $reply = Read-Host
            echo ""
            if ($reply -notmatch "^[Yy]$") {
                log_info "跳过安装"
                return 0
            }
        }
        echo -e "  ${DIM}▸ 重新安装中...${NC}"
    }

    echo -e "  ${DIM}▸ 检查依赖...${NC}"
    $hasGit = Get-Command git -ErrorAction SilentlyContinue
    $hasCurl = Get-Command curl -ErrorAction SilentlyContinue
    if (-not $hasGit -or -not $hasCurl) {
        log_error "缺少依赖"
        return 1
    }
    echo -e "  ${GREEN}✓ 依赖检查通过${NC}"
    echo ""

    if (Test-Path $install_dir) {
        log_info "更新现有安装..."
        Set-Location $install_dir
        git pull origin main 2>$null
    } else {
        log_info "克隆仓库..."
        git clone --depth 1 "https://github.com/xuanyuanluoxue/AgentHub.git" $install_dir
    }

    echo ""
    log_success "安装完成!"
    echo ""
    echo -e "  ${DIM}下一步:${NC}"
    echo "    cd $install_dir"
    echo "    pip install -e ."
    echo "    agenthub init"
    echo ""
}

do_windows_uninstall() {
    local install_dir="$HOME\.agenthub"

    echo ""
    echo -e "  ${RED}⚠ 确认卸载 AgentHub${NC}"
    echo "    目录: $install_dir"
    echo ""

    echo -n "  此操作不可恢复，是否继续? [y/N]: "
    $reply = Read-Host
    echo ""

    if ($reply -notmatch "^[Yy]$") {
        log_info "取消卸载"
        return 0
    }

    if (Test-Path $install_dir) {
        Remove-Item -Recurse -Force $install_dir
        log_success "卸载完成"
    } else {
        log_warn "未检测到安装目录"
    }
}

# ========================================
# 主流程
# ========================================
main() {
    local action=""
    local os_type=""
    local os_name=""

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

    local os_info=$(detect_os)
    os_type="${os_info%%:*}"
    os_name="${os_info##*:}"

    log_info "检测到操作系统: ${CYAN}${os_name}${NC}"
    echo ""

    if [ -z "$action" ]; then
        if ! [ -t 0 ]; then
            echo -e "  ${RED}x 错误: 管道模式必须指定操作${NC}"
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

    case "$action" in
        install)
            case "$os_type" in
                linux|macos) do_linux_install ;;
                windows) do_windows_install ;;
                *) log_error "不支持的操作系统: $os_name"; exit 1 ;;
            esac
            ;;
        uninstall)
            case "$os_type" in
                linux|macos) do_linux_uninstall ;;
                windows) do_windows_uninstall ;;
                *) log_error "不支持的操作系统: $os_name"; exit 1 ;;
            esac
            ;;
    esac
}

main "$@"