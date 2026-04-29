# AgentHub Windows 打开项目目录
$INSTALL_DIR = "$env:USERPROFILE\.agenthub"

function Write-Info { param($m) Write-Host "  > $m" -ForegroundColor Cyan }

if (-not (Test-Path $INSTALL_DIR)) {
    Write-Host "  AgentHub 未安装" -ForegroundColor Red
    exit 1
}

Write-Info "打开目录: $INSTALL_DIR"
Write-Host ""

Start-Process explorer.exe $INSTALL_DIR

Write-Host ""
Write-Info "已打开项目目录"
Write-Host ""