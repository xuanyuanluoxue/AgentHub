#!/bin/bash
# AgentHub 卸载脚本
set -e

REPO_RAW="https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc"

CYAN='\033[0;36m'
NC='\033[0m'

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
    local os="$1"
    curl -fsSL "${REPO_RAW}/uninstall/${os}/install.sh" | bash
}

main() {
    local os_type=$(detect_os)
    echo ""
    echo -e "  ${CYAN}AgentHub 卸载${NC}"
    echo ""
    download_and_run "$os_type"
}

main "$@"