# AgentHub Windows 安装脚本 (本地测试版)
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Info { Write-Host "  > $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "  ✓ $args" -ForegroundColor Green }
function Write-Warn { Write-Host "  ! $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "  x $args" -ForegroundColor Red }
function Write-Dim { Write-Host "  $args" -ForegroundColor DarkGray }

$INSTALL_DIR = "$env:USERPROFILE\.agenthub"
$BACKUP_DIR = "$env:USERPROFILE\.agenthub.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host ""
Write-Host "  ▸ 检查系统依赖" -ForegroundColor White
Write-Host ""

$allOk = $true

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    $ver = (git --version 2>&1) -replace "^git version ", ""
    Write-Host "    ✓ git $ver" -ForegroundColor Green
} else {
    Write-Host "    x git (未找到)" -ForegroundColor Red
    $allOk = $false
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $ver = (python --version 2>&1) -replace "^Python ", ""
    Write-Host "    ✓ python $ver" -ForegroundColor Green

    $verNum = $ver -split '\.'
    if ([int]$verNum[0] -lt 3 -or ([int]$verNum[0] -eq 3 -and [int]$verNum[1] -lt 10)) {
        Write-Host "    x Python 版本过低 (需要 >= 3.10)" -ForegroundColor Red
        $allOk = $false
    }
} else {
    Write-Host "    x python (未找到)" -ForegroundColor Red
    $allOk = $false
}

if (-not $allOk) {
    Write-Host ""
    Write-Err "缺少系统依赖"
    Write-Host ""
    Write-Host "  下载 Git: https://git-scm.com/download/win" -ForegroundColor Cyan
    Write-Host "  下载 Python: https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Success "依赖检查通过"
Write-Host ""

# 准备目录
Write-Host "  ▸ 准备安装目录" -ForegroundColor White
Write-Host ""

if (Test-Path "$INSTALL_DIR\pyproject.toml") {
    if ($Force) {
        Write-Info "强制重装，删除旧目录"
        Remove-Item -Recurse -Force $INSTALL_DIR -ErrorAction SilentlyContinue
    } else {
        Write-Host -n "  检测到已安装，是否重装? [y/N]: " -ForegroundColor Yellow
        $resp = Read-Host
        Write-Host ""
        if ($resp -notmatch "^[Yy]$") {
            Write-Info "跳过安装"
            exit 0
        }
        Write-Info "删除旧目录"
        Remove-Item -Recurse -Force $INSTALL_DIR -ErrorAction SilentlyContinue
    }
}

New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null
Write-Success "目录已创建: $INSTALL_DIR"
Write-Host ""

# 克隆仓库
Write-Host "  ▸ 下载代码" -ForegroundColor White
Write-Host ""

$repoUrl = "https://github.com/xuanyuanluoxue/AgentHub.git"

Write-Info "正在克隆仓库..."
Write-Host "    来源: $repoUrl" -ForegroundColor DarkGray
Write-Host "    目标: $INSTALL_DIR" -ForegroundColor DarkGray
Write-Host ""

try {
    git clone --depth 1 $repoUrl $INSTALL_DIR 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Success "下载完成"
        Write-Host ""
    } else {
        throw "git clone failed"
    }
} catch {
    Write-Host ""
    Write-Err "克隆失败，请检查网络连接"
    exit 1
}

# 安装 Python 包
Write-Host "  ▸ 安装 Python 包" -ForegroundColor White
Write-Host ""

Set-Location $INSTALL_DIR

if (-not (Test-Path "pyproject.toml")) {
    Write-Err "pyproject.toml 不存在"
    exit 1
}

Write-Info "正在安装..."
Write-Host ""

$ok = $false

foreach ($cmd in @(
    { python -m pip install --user -e . },
    { python -m pip install --break-system-packages -e . },
    { pip install --user -e . }
)) {
    Write-Dim "  尝试: $($cmd.ToString().Split('{')[0].Trim())"
    try {
        & $cmd 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $ok = $true
            break
        }
    } catch { }
    Write-Host ""
}

if ($ok) {
    Write-Success "安装完成"
} else {
    Write-Err "安装失败"
    Write-Host "  请手动执行: pip install --user -e ." -ForegroundColor Cyan
    exit 1
}

Write-Host ""

$cmd = Get-Command agenthub -ErrorAction SilentlyContinue
if ($cmd) {
    try {
        $ver = (agenthub --version 2>&1) -replace "agenthub, version ", ""
        Write-Host "    ✓ agenthub v$ver" -ForegroundColor Green
    } catch {
        Write-Host "    ✓ agenthub" -ForegroundColor Green
    }
} else {
    Write-Warn "请重新打开 PowerShell 以使用 agenthub 命令"
}
Write-Host ""

# 初始化配置
Write-Host "  ▸ 初始化配置" -ForegroundColor White
Write-Host ""

foreach ($d in @("skills", "agents", "profile", "apps")) {
    New-Item -ItemType Directory -Force -Path "$INSTALL_DIR\$d" | Out-Null
}

if (Test-Path "$INSTALL_DIR\profile\identity.yaml") {
    Write-Info "配置已存在，跳过"
} else {
    @"
name: Your Name
bio: AI enthusiast and developer
contact:
  email: your@email.com
  github: https://github.com/your-username
preferences:
  language: zh-CN
  theme: auto
"@ | Out-File -FilePath "$INSTALL_DIR\profile\identity.yaml" -Encoding UTF8

    @"
{
  "skills": [],
  "agents": [],
  "version": "1.0"
}
"@ | Out-File -FilePath "$INSTALL_DIR\registry.json" -Encoding UTF8

    Write-Success "配置创建完成"
}

Write-Host ""
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "    安装完成！" -ForegroundColor Green
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "  下一步:"
Write-Host "    notepad `$env:USERPROFILE\.agenthub\profile\identity.yaml"
Write-Host "    agenthub status"
Write-Host ""
Write-Host "  帮助: https://github.com/xuanyuanluoxue/AgentHub" -ForegroundColor DarkGray
Write-Host ""
