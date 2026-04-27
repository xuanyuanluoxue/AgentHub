# AgentHub Windows 卸载脚本
param(
    [switch]$Force
)

$ErrorActionPreference = "Continue"

function Write-Info { Write-Host "  > $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "  ✓ $args" -ForegroundColor Green }
function Write-Warn { Write-Host "  ! $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "  x $args" -ForegroundColor Red }

$INSTALL_DIR = "$env:USERPROFILE\.agenthub"
$BACKUP_DIR = "$env:USERPROFILE\.agenthub.backup.$( Get-Date -Format 'yyyyMMddHHmmss' )"

Write-Host ""
Write-Host "  ▸ 确认卸载" -ForegroundColor White
Write-Host ""

if (-not (Test-Path $INSTALL_DIR)) {
    Write-Info "AgentHub 未安装，无需卸载"
    exit 0
}

Write-Warn "即将卸载 AgentHub"
Write-Host "    目录: $INSTALL_DIR"
Write-Host ""

if ($Force) {
    $backup = $true
} else {
    Write-Host -n "  是否备份当前配置? [y/N]: " -ForegroundColor Yellow
    $resp = Read-Host
    Write-Host ""
    $backup = ($resp -match "^[Yy]$")
}

if ($backup) {
    Write-Info "备份到 $BACKUP_DIR..."
    Move-Item -Path $INSTALL_DIR -Destination $BACKUP_DIR -Force
    Write-Success "备份完成"
    Write-Host "    备份目录: $BACKUP_DIR" -ForegroundColor DarkGray
} else {
    Write-Warn "跳过备份，删除所有数据"
    Remove-Item -Recurse -Force $INSTALL_DIR -ErrorAction SilentlyContinue
    Write-Success "卸载完成"
}

Write-Host ""
Write-Host "  ▸ 卸载 Python 包" -ForegroundColor White
Write-Host ""

Write-Info "正在卸载 agenthub..."
try {
    pip uninstall agenthub -y 2>$null | Out-Null
    Write-Success "Python 包已卸载"
} catch {
    Write-Info "Python 包未安装或已移除"
}

Write-Host ""
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "    卸载完成！" -ForegroundColor Green
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "  重新安装:"
Write-Host "    irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/install.ps1 | iex" -ForegroundColor Cyan
Write-Host ""
