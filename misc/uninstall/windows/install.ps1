# AgentHub Windows 卸载脚本
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$INSTALL_DIR = "$env:USERPROFILE\.agenthub"
$BACKUP_DIR = "$env:USERPROFILE\.agenthub.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"

function Write-Info { param($m) Write-Host "  > $m" -ForegroundColor Cyan }
function Write-Success { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "  [!] $m" -ForegroundColor Yellow }
function Write-Err { param($m) Write-Host "  [X] $m" -ForegroundColor Red }

function Show-Banner {
    Write-Host ""
    Write-Host "    _                    _   _   _       _     " -ForegroundColor Yellow
    Write-Host "   / \   __ _  ___ _ __ | |_| | | |_   _| |__  " -ForegroundColor Yellow
    Write-Host "  / _ \ / _\` |/ _ \ '_ \| __| |_| | | | | '_ \ " -ForegroundColor Yellow
    Write-Host " / ___ \ (_| |  __/ | | | |_|  _  | |_| | |_) |" -ForegroundColor Yellow
    Write-Host "/_/   \_\__, |\___|_| |_|\__|_| |_|\__,_|_.__/ " -ForegroundColor Yellow
    Write-Host "        |___/                               " -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  AgentHub 卸载" -ForegroundColor Cyan
    Write-Host ""
}

if (-not (Test-Path "$INSTALL_DIR\pyproject.toml")) {
    Write-Info "AgentHub 未安装，无需卸载"
    exit 0
}

Show-Banner

Write-Warn "即将卸载 AgentHub"
Write-Host "    目录: $INSTALL_DIR"
Write-Host ""

if ($Force) {
    $backup = $false
} else {
    Write-Host -n "  是否备份? [y/N]: " -ForegroundColor Yellow
    $resp = Read-Host
    $backup = ($resp -match "^[Yy]$")
}
Write-Host ""

if ($backup) {
    Write-Info "备份到 $BACKUP_DIR..."
    Move-Item -Path $INSTALL_DIR -Destination $BACKUP_DIR -Force
    Write-Success "备份完成"
} else {
    Write-Info "删除所有数据..."
    Remove-Item -Recurse -Force $INSTALL_DIR -ErrorAction SilentlyContinue
    Write-Success "删除完成"
}

Write-Host ""
Write-Info "卸载 Python 包..."
try {
    pip uninstall agenthub -y 2>$null | Out-Null
    Write-Success "Python 包已卸载"
} catch {
    Write-Info "Python 包未安装或已移除"
}

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Green
Write-Success "卸载完成！"
Write-Host "  ============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  重新安装:" -ForegroundColor White
Write-Host "    irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install/windows/install.ps1 | iex" -ForegroundColor Cyan
Write-Host ""