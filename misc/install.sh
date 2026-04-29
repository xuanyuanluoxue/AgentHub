#!/bin/bash
# AgentHub 安装脚本
# 支持: install | uninstall | update | reinstall
# 用法:
#   curl -fsSL ... | bash              # 交互模式（自动下载脚本）
#   curl -fsSL ... | bash -s -- install   # 指定操作
set -e

REPO_RAW="https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc"
INSTALL_DIR="${HOME}/.agenthub"

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
    echo -e "  ${GREEN}   / \   __ _  ___ _ __ | |_| | | |_   _| |__  ${NC}"
    echo -e "  ${GREEN}  / _ \ / _\` |/ _ \ '_ \| __| |_| | | | | '_ \ ${NC}"
    echo -e "  ${GREEN} / ___ \ (_| |  __/ | | | |_|  _  | |_| | |_) |${NC}"
    echo -e "  ${GREEN}/_/   \_\__, |\___|_| |_|\__|_| |_|\__,_|_.__/ ${NC}"
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

is_installed() {
    [ -d "${INSTALL_DIR}" ] && [ -f "${INSTALL_DIR}/pyproject.toml" ]
}

# ============================================
# Linux/macOS 安装
# ============================================
do_install_unix() {
    show_banner
    local os_type=$(detect_os)
    log_info "检测到系统: ${CYAN}${os_type}${NC}"
    echo ""

    local REPO_URL="https://github.com/xuanyuanluoxue/AgentHub.git"

    log_info "正在下载..."
    echo "    来源: $REPO_URL" | sed 's|https://||'
    echo "    目标: $INSTALL_DIR"
    echo ""

    if git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" 2>&1 | grep -qv "Cloning"; then
        :
    fi

    if [ -d "$INSTALL_DIR/.git" ]; then
        log_ok "下载完成"
    else
        log_err "克隆失败"
        exit 1
    fi

    log_info "排除 misc/ 目录..."
    rm -rf "$INSTALL_DIR/misc"
    echo ""

    log_info "安装 Python 包..."
    cd "$INSTALL_DIR"

    local ok=false
    for cmd in "python3 -m pip install --user -e ." "python3 -m pip install -e ." "pip install --user -e ."; do
        log_info "尝试: $cmd"
        if eval "$cmd" 2>&1 | grep -qv "error"; then
            ok=true
            break
        fi
    done

    if $ok; then
        log_ok "安装完成"
    else
        log_err "安装失败"
        exit 1
    fi
    echo ""

    if command -v agenthub &> /dev/null; then
        log_ok "agenthub 已安装"
    else
        log_warn "请重新打开终端以使用 agenthub 命令"
    fi
    echo ""

    echo -e "  ${GREEN}============================================${NC}"
    log_ok "安装完成！"
    echo -e "  ${GREEN}============================================${NC}"
    echo ""
    echo "  下一步:"
    echo "    agenthub --help"
    echo ""
}

# ============================================
# Linux/macOS 卸载
# ============================================
do_uninstall_unix() {
    show_banner

    if [ ! -d "$INSTALL_DIR" ]; then
        log_info "AgentHub 未安装，无需卸载"
        exit 0
    fi

    log_warn "即将卸载 AgentHub"
    echo "    目录: $INSTALL_DIR"
    echo ""

    echo -n "  是否备份? [y/N]: "
    read -r REPLY
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        local bak="${HOME}/.agenthub.backup.$(date +%Y%m%d%H%M%S)"
        log_info "备份到 $bak..."
        mv "$INSTALL_DIR" "$bak"
        log_ok "备份完成"
    else
        log_info "删除所有数据..."
        rm -rf "$INSTALL_DIR"
        log_ok "删除完成"
    fi

    echo ""
    log_info "卸载 Python 包..."
    pip uninstall agenthub -y 2>/dev/null && log_ok "Python 包已卸载" || log_info "Python 包未安装"
    echo ""

    echo -e "  ${GREEN}============================================${NC}"
    log_ok "卸载完成！"
    echo -e "  ${GREEN}============================================${NC}"
    echo ""
}

# ============================================
# Linux/macOS 更新
# ============================================
do_update_unix() {
    show_banner

    if [ ! -d "$INSTALL_DIR" ]; then
        log_err "AgentHub 未安装，请先安装"
        exit 1
    fi

    log_info "拉取最新代码..."
    cd "$INSTALL_DIR"
    git pull 2>&1 | grep -v "Already up to date" || true
    echo ""

    log_info "更新 Python 包..."
    pip install --user -e . 2>&1 | grep -qv "error" && log_ok "Python 包已更新" || log_warn "Python 包更新失败"
    echo ""

    echo -e "  ${GREEN}============================================${NC}"
    log_ok "更新完成！"
    echo -e "  ${GREEN}============================================${NC}"
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

    # 非交互模式
    if [ -n "$action" ]; then
        case "$action" in
            install) do_install_unix ;;
            uninstall) do_uninstall_unix ;;
            update) do_update_unix ;;
            reinstall)
                do_uninstall_unix
                echo ""
                do_install_unix
                ;;
        esac
        return
    fi

    # 交互模式：需要终端
    if [ -t 0 ]; then
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
        echo -n "  请输入选项 [1-5]: "
        read choice
        echo ""

        case "$choice" in
            1) do_install_unix ;;
            2) do_uninstall_unix ;;
            3) do_update_unix ;;
            4)
                do_uninstall_unix
                echo ""
                do_install_unix
                ;;
            *) log_info "退出"; exit 0 ;;
        esac
    else
        # 管道模式但未指定操作
        log_err "管道模式需要指定操作"
        echo ""
        echo "  用法: curl -fsSL ... | bash -s -- install"
        echo "        curl -fsSL ... | bash -s -- uninstall"
        echo "        curl -fsSL ... | bash -s -- update"
        echo "        curl -fsSL ... | bash -s -- reinstall"
        echo ""
        echo "  或直接运行（需要终端）:"
        echo "        curl -fsSL ... | bash"
        echo "        下载脚本后手动执行: bash install.sh"
        exit 1
    fi
}

main "$@"