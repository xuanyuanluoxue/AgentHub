# AgentHub Windows 重装脚本 - 恢复出厂设置
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$INSTALL_DIR = "$env:USERPROFILE\.agenthub"
$REPO_URL = "https://github.com/xuanyuanluoxue/AgentHub.git"

function Write-Info { param($m) Write-Host "  > $m" -ForegroundColor Cyan }
function Write-Success { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "  [!] $m" -ForegroundColor Yellow }
function Write-Err { param($m) Write-Host "  [X] $m" -ForegroundColor Red }

function Show-Banner {
    Write-Host ""
    Write-Host "    _                    _   _   _       _     " -ForegroundColor Red
    Write-Host "   / \   __ _  ___ _ __ | |_| | | |_   _| |__  " -ForegroundColor Red
    Write-Host "  / _ \ / _\` |/ _ \ '_ \| __| |_| | | | | '_ \ " -ForegroundColor Red
    Write-Host " / ___ \ (_| |  __/ | | | |_|  _  | |_| | |_) |" -ForegroundColor Red
    Write-Host "/_/   \_\__, |\___|_| |_|\__|_| |_|\__,_|_.__/ " -ForegroundColor Red
    Write-Host "        |___/                               " -ForegroundColor Red
    Write-Host ""
    Write-Host "  AgentHub 恢复出厂设置" -ForegroundColor Cyan
    Write-Host ""
}

Show-Banner

Write-Warn "即将删除所有数据并重新安装"
Write-Host "    目录: $INSTALL_DIR"
Write-Host ""

if (-not $Force) {
    Write-Host -n "  确认? [y/N]: " -ForegroundColor Yellow
    $resp = Read-Host
    if ($resp -notmatch "^[Yy]$") {
        Write-Info "取消操作"
        exit 0
    }
}
Write-Host ""

if (Test-Path $INSTALL_DIR) {
    Write-Info "删除旧版本..."
    Remove-Item -Recurse -Force $INSTALL_DIR -ErrorAction SilentlyContinue
}

Write-Info "正在下载..."
Write-Host "    来源: $REPO_URL" -ForegroundColor DarkGray
Write-Host "    目标: $INSTALL_DIR" -ForegroundColor DarkGray
Write-Host ""

try {
    git clone --depth 1 $REPO_URL $INSTALL_DIR 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Success "下载完成"
} catch {
    Write-Err "克隆失败"
    exit 1
}

Write-Info "排除 misc/ 目录..."
Remove-Item -Recurse -Force "$INSTALL_DIR\misc" -ErrorAction SilentlyContinue

Write-Host ""
Write-Info "安装 Python 包..."
Set-Location $INSTALL_DIR

$ok = $false
foreach ($cmd in @(
    { python -m pip install --user -e . },
    { python -m pip install --break-system-packages -e . },
    { pip install --user -e . }
)) {
    Write-Dim "  尝试: $($cmd.ToString().Split('{')[0].Trim())"
    try {
        & $cmd 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $ok = $true; break }
    } catch { }
    Write-Host ""
}

if ($ok) {
    Write-Success "安装完成"
} else {
    Write-Err "安装失败"
    exit 1
}

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Green
Write-Success "恢复出厂设置完成！"
Write-Host "  ============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  下一步:" -ForegroundColor White
Write-Host "    agenthub --help"
Write-Host ""