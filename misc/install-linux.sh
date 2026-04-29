#!/bin/bash
# AgentHub Linux/macOS 安装脚本
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

REPO_URL="https://github.com/xuanyuanluoxue/AgentHub.git"
INSTALL_DIR="${HOME}/.agenthub"
BACKUP_DIR="${HOME}/.agenthub.backup.$(date +%Y%m%d%H%M%S)"

log_info() { echo -e "  ${BLUE}>${NC} $1"; }
log_success() { echo -e "  ${GREEN}✓${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}!${NC} $1"; }
log_error() { echo -e "  ${RED}x${NC} $1"; }

check_deps() {
    echo -e "  ${BOLD}▸ 检查系统依赖${NC}"
    echo ""
    local all_ok=true

    local git_ver=$(git --version 2>&1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1)
    if [ -n "$git_ver" ]; then
        echo -e "    ${GREEN}✓${NC} git ${git_ver}"
    else
        echo -e "    ${RED}x${NC} git (未找到)"
        all_ok=false
    fi

    local python_ver=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    if [ -n "$python_ver" ]; then
        echo -e "    ${GREEN}✓${NC} python ${python_ver}"
    else
        python_ver=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        if [ -n "$python_ver" ]; then
            echo -e "    ${GREEN}✓${NC} python ${python_ver}"
        else
            echo -e "    ${RED}x${NC} python (未找到)"
            all_ok=false
        fi
    fi

    echo ""
    if ! $all_ok; then
        log_error "缺少系统依赖"
        echo "  下载 Git: https://git-scm.com/download/linux"
        echo "  下载 Python: https://www.python.org/downloads/"
        exit 1
    fi
    log_success "依赖检查通过"
    echo ""
}

backup_old() {
    if [ -d "${INSTALL_DIR}" ]; then
        echo -e "  ${BOLD}▸ 备份旧数据${NC}"
        echo ""
        log_info "备份到 ${BACKUP_DIR}..."
        mv "${INSTALL_DIR}" "${BACKUP_DIR}"
        log_success "备份完成"
        echo "    备份目录: ${BACKUP_DIR}"
        echo ""
    fi
}

clone_repo() {
    echo -e "  ${BOLD}▸ 下载代码${NC}"
    echo ""
    log_info "正在克隆仓库..."
    echo "    来源: ${REPO_URL}" | sed "s|https://||" | sed "s|github.com/||" | sed "s|xuanyuanluoxue/||"
    echo "    目标: ${INSTALL_DIR}"
    echo ""

    if git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}" 2>&1 | grep -v "Cloning"; then
        :
    fi

    if [ -d "${INSTALL_DIR}/.git" ]; then
        log_success "下载完成"
    else
        log_error "克隆失败"
        exit 1
    fi
    echo ""
}

install_python_pkg() {
    echo -e "  ${BOLD}▸ 安装 Python 包${NC}"
    echo ""

    cd "${INSTALL_DIR}"

    for cmd in "python3 -m pip install --user -e ." "python3 -m pip install -e ." "pip install --user -e ."; do
        log_info "尝试: $cmd"
        if eval "$cmd" 2>&1 | grep -qv "error"; then
            log_success "安装完成"
            echo ""
            return
        fi
        echo ""
    done

    log_error "安装失败，请手动执行: pip install --user -e ."
    echo ""
}

verify_installation() {
    echo -e "  ${BOLD}▸ 验证安装${NC}"
    echo ""

    if command -v agenthub &> /dev/null; then
        local ver=$(agenthub --version 2>&1 || echo "unknown")
        echo -e "    ${GREEN}✓${NC} agenthub ${ver}"
    else
        echo -e "    ${YELLOW}!${NC} 请重新打开终端以使用 agenthub 命令"
    fi
    echo ""
}

main() {
    print_banner() {
        echo ""
        echo -e "  ${GREEN}    _                    _   _   _       _     ${NC}"
        echo -e "  ${GREEN}   / \\   __ _  ___ _ __ | |_| | | |_   _| |__  ${NC}"
        echo -e "  ${GREEN}  / _ \\ / _\` |/ _ \\ '_ \\| __| |_| | | | | '_ \\ ${NC}"
        echo -e "  ${GREEN} / ___ \\ (_| |  __/ | | | |_|  _  | |_| | |_) |${NC}"
        echo -e "  ${GREEN}/_/   \\_\\__, |\\___|_| |_|\__|_| |_|\\__,_|_.__/ ${NC}"
        echo -e "  ${GREEN}        |___/                               ${NC}"
        echo ""
    }

    print_banner

    check_deps
    backup_old
    clone_repo
    install_python_pkg
    verify_installation

    echo -e "  ${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${GREEN}✓ 安装完成！${NC}"
    echo -e "  ${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  下一步:"
    echo "    agenthub --help"
    echo ""
    echo "  帮助: https://github.com/xuanyuanluoxue/AgentHub"
    echo ""
}

main "$@"