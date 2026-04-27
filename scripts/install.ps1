<#
AgentHub 一键安装脚本 - Windows PowerShell

用法:
  irm https://raw.githubusercontent.com/your-org/agenthub/main/scripts/install.ps1 | iex
  或
  .\install.ps1
#>

param(
    [string]$InstallDir = "$env:USERPROFILE\.agenthub"
)

$ErrorActionPreference = "Stop"

# ============================================
# 颜色和输出函数
# ============================================
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Err { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }

# ============================================
# Banner
# ============================================
Write-Host ""
Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         AgentHub 安装程序                    ║" -ForegroundColor Green
Write-Host "║   统一 AI 工具的 Skill · Agent · 画像      ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# ============================================
# 检查依赖
# ============================================
Write-Info "检查依赖..."

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    Write-Success "Git 已安装"
} else {
    Write-Err "Git 未安装，请先安装 Git"
    Write-Host "   下载: https://git-scm.com/download/win"
    exit 1
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $version = python --version 2>&1
    Write-Success "Python 已安装 ($version)"
} else {
    Write-Err "Python 未安装，请先安装 Python >= 3.10"
    Write-Host "   下载: https://www.python.org/downloads/"
    exit 1
}

$pip = Get-Command pip -ErrorAction SilentlyContinue
if (-not $pip) {
    Write-Warn "pip 未安装，尝试使用 python -m pip"
}

# ============================================
# 备份现有配置
# ============================================
if (Test-Path $InstallDir) {
    Write-Warn "发现已存在的 AgentHub 配置"
    $backup = "$env:USERPROFILE\.agenthub.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
    $confirm = Read-Host "是否备份现有配置? (y/N)"
    if ($confirm -match "^[Yy]$") {
        Write-Info "备份现有配置到 $backup"
        Copy-Item -Path $InstallDir -Destination $backup -Recurse
        Write-Success "备份完成"
    } else {
        Write-Warn "跳过备份，现有配置将被覆盖"
    }
}

# ============================================
# 克隆仓库
# ============================================
$repoUrl = "https://github.com/your-org/agenthub.git"

if (-not (Test-Path $InstallDir)) {
    Write-Info "克隆 AgentHub 仓库到 $InstallDir..."
    git clone --depth 1 $repoUrl $InstallDir
    Write-Success "仓库克隆完成"
} else {
    Write-Info "发现已安装的 AgentHub，跳过下载"
}

# ============================================
# 安装 Python 包
# ============================================
Write-Info "安装 AgentHub Python 包..."

Set-Location $InstallDir

if (Test-Path "pyproject.toml") {
    python -m pip install -e . --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python 包安装完成"
    } else {
        Write-Err "Python 包安装失败"
        exit 1
    }
} else {
    Write-Err "pyproject.toml 不存在，请确认安装目录正确"
    exit 1
}

# ============================================
# 添加到 PATH
# ============================================
$scriptsPath = "$env:LOCALAPPDATA\Python\Python*\Scripts"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

$addedToPath = $false
foreach ($sp in Get-ChildItem $scriptsPath -ErrorAction SilentlyContinue) {
    if ($userPath -notlike "*$sp*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$sp", "User")
        $addedToPath = $true
        break
    }
}

# ============================================
# 初始化配置
# ============================================
Write-Info "初始化 AgentHub 配置..."
$initConfirm = Read-Host "是否初始化配置? (Y/n)"
if ($initConfirm -notmatch "^[Nn]$") {
    agenthub init --template
    Write-Success "配置初始化完成"
}

# ============================================
# 完成
# ============================================
Write-Host ""
Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║            安装完成！                     ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:"
Write-Host "  1. 编辑 $InstallDir\profile\identity.yaml 填入你的信息"
Write-Host "  2. 运行 $($env:LOCALAPPDATA)\Python\Python*\Scripts\agenthub skill list 查看 Skills"
Write-Host "  3. 运行 $($env:LOCALAPPDATA)\Python\Python*\Scripts\agenthub agent list 查看 Agents"
Write-Host ""
Write-Host "帮助:"
Write-Host "  agenthub --help              查看帮助"
Write-Host "  agenthub init --help        查看初始化选项"
Write-Host ""

if ($addedToPath) {
    Write-Warn "已将 Python Scripts 目录添加到 PATH"
    Write-Host "如果 agenthub 命令不可用，请重新打开终端或运行: refreshenv"
}
