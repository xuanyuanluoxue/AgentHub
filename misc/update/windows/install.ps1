# AgentHub Windows 更新脚本
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$INSTALL_DIR = "$env:USERPROFILE\.agenthub"

function Write-Info { param($m) Write-Host "  > $m" -ForegroundColor Cyan }
function Write-Success { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "  [!] $m" -ForegroundColor Yellow }
function Write-Err { param($m) Write-Host "  [X] $m" -ForegroundColor Red }

function Show-Banner {
    Write-Host ""
    Write-Host "    _                    _   _   _       _     " -ForegroundColor Cyan
    Write-Host "   / \   __ _  ___ _ __ | |_| | | |_   _| |__  " -ForegroundColor Cyan
    Write-Host "  / _ \ / _\` |/ _ \ '_ \| __| |_| | | | | '_ \ " -ForegroundColor Cyan
    Write-Host " / ___ \ (_| |  __/ | | | |_|  _  | |_| | |_) |" -ForegroundColor Cyan
    Write-Host "/_/   \_\__, |\___|_| |_|\__|_| |_|\__,_|_.__/ " -ForegroundColor Cyan
    Write-Host "        |___/                               " -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  AgentHub 更新" -ForegroundColor Cyan
    Write-Host ""
}

if (-not (Test-Path "$INSTALL_DIR\pyproject.toml")) {
    Write-Warn "AgentHub 未安装，请先安装"
    Write-Host "  安装命令:" -ForegroundColor White
    Write-Host "    irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install/windows/install.ps1 | iex" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Show-Banner

Write-Info "正在更新..."
Set-Location $INSTALL_DIR

Write-Info "拉取最新代码..."
git pull 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "代码更新完成"
} else {
    Write-Err "更新失败"
    exit 1
}

Write-Host ""
Write-Info "更新 Python 包..."
pip install --user -e . 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Python 包更新完成"
} else {
    Write-Warn "Python 包更新失败，代码已更新"
}

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Green
Write-Success "更新完成！"
Write-Host "  ============================================" -ForegroundColor Green
Write-Host ""