# AgentHub 安装脚本 (Windows PowerShell)
param(
    [ValidateSet('install', 'uninstall', 'update', 'reinstall')]
    [string]$Action = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$INSTALL_DIR = "$env:USERPROFILE\.agenthub"
$REPO_URL = "https://github.com/xuanyuanluoxue/AgentHub.git"
$REPO_RAW = "https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc"

function Write-Info { param($m) Write-Host "  > $m" -ForegroundColor Cyan }
function Write-Success { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "  [!] $m" -ForegroundColor Yellow }
function Write-Err { param($m) Write-Host "  [X] $m" -ForegroundColor Red }

function Show-Banner {
    Write-Host ""
    Write-Host "    _                    _   _   _       _     " -ForegroundColor Green
    Write-Host "   / \   __ _  ___ _ __ | |_| | | |_   _| |__  " -ForegroundColor Green
    Write-Host "  / _ \ / _\` |/ _ \ '_ \| __| |_| | | | | '_ \ " -ForegroundColor Green
    Write-Host " / ___ \ (_| |  __/ | | | |_|  _  | |_| | |_) |" -ForegroundColor Green
    Write-Host "/_/   \_\__, |\___|_| |_|\__|_| |_|\__,_|_.__/ " -ForegroundColor Green
    Write-Host "        |___/                               " -ForegroundColor Green
    Write-Host ""
    Write-Host "  统一 AI 工具四大共享生态" -ForegroundColor Cyan
    Write-Host "  Skill · Agent · 画像 · 记忆" -ForegroundColor DarkGray
    Write-Host ""
}

function Test-Dependencies {
    Write-Host "  检查系统依赖..." -ForegroundColor White
    $allOk = $true

    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        $ver = (git --version 2>&1) -replace "^git version ", ""
        Write-Success "git $ver"
    } else {
        Write-Err "git 未找到"
        $allOk = $false
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
    if ($python) {
        $ver = (python --version 2>&1) -replace "^Python ", ""
        $verNum = $ver -split '\.'
        if ([int]$verNum[0] -lt 3 -or ([int]$verNum[0] -eq 3 -and [int]$verNum[1] -lt 10)) {
            Write-Err "Python 版本过低 (需要 >= 3.10)"
            $allOk = $false
        } else {
            Write-Success "Python $ver"
        }
    } else {
        Write-Err "python 未找到"
        $allOk = $false
    }

    if (-not $allOk) {
        Write-Host ""
        Write-Err "缺少系统依赖"
        Write-Host "  下载 Git: https://git-scm.com/download/win" -ForegroundColor Cyan
        Write-Host "  下载 Python: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
    Write-Host ""
}

function Get-InstallationStatus {
    Test-Path "$INSTALL_DIR\pyproject.toml"
}

function Do-Install {
    Show-Banner
    Test-Dependencies

    $isInstalled = Get-InstallationStatus
    if ($isInstalled) {
        Write-Warn "检测到已安装 AgentHub"
        Write-Host "    目录: $INSTALL_DIR"
        Write-Host ""
        if (-not $Force) {
            Write-Host -n "  是否覆盖安装? [y/N]: " -ForegroundColor Yellow
            $resp = Read-Host
            if ($resp -notmatch "^[Yy]$") {
                Write-Info "取消安装"
                exit 0
            }
        }
    }

    if ($isInstalled) {
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
        Write-Err "克隆失败，请检查网络连接"
        exit 1
    }

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
        Write-Err "安装失败，请手动执行: pip install --user -e ."
        exit 1
    }

    Write-Host ""
    $cmd = Get-Command agenthub -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Success "agenthub 已安装"
    } else {
        Write-Warn "请重新打开 PowerShell 以使用 agenthub 命令"
    }

    Write-Host ""
    Write-Host "  ============================================" -ForegroundColor Green
    Write-Success "安装完成！"
    Write-Host "  ============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  下一步:" -ForegroundColor White
    Write-Host "    agenthub --help"
    Write-Host ""
}

function Do-Uninstall {
    Show-Banner

    if (-not (Get-InstallationStatus)) {
        Write-Info "AgentHub 未安装，无需卸载"
        exit 0
    }

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
        $bakDir = "$env:USERPROFILE\.agenthub.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
        Write-Info "备份到 $bakDir..."
        Move-Item -Path $INSTALL_DIR -Destination $bakDir -Force
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
}

function Do-Update {
    Show-Banner

    if (-not (Get-InstallationStatus)) {
        Write-Err "AgentHub 未安装，请先安装"
        exit 1
    }

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
}

function Do-Reinstall {
    Show-Banner
    Do-Uninstall
    Write-Host ""
    Do-Install
}

function Show-Menu {
    Show-Banner

    if (Get-InstallationStatus) {
        Write-Host "  检测到已安装 AgentHub" -ForegroundColor Yellow
        Write-Host ""
    }

    Write-Host "  请选择操作:" -ForegroundColor White
    Write-Host ""
    Write-Host "    [1] 安装 AgentHub" -ForegroundColor Green
    Write-Host "    [2] 卸载 AgentHub" -ForegroundColor Yellow
    Write-Host "    [3] 更新 AgentHub" -ForegroundColor Cyan
    Write-Host "    [4] 恢复出厂设置" -ForegroundColor Red
    Write-Host "    [5] 退出" -ForegroundColor DarkGray
    Write-Host ""
}

# ============================================
# 主流程
# ============================================
if (-not $Action) {
    if ($PsInteractive -or ([Environment]::GetCommandLineArgs() -notmatch "-NonInteractive")) {
        Show-Menu
        Write-Host -n "  请输入选项 [1-5]: " -ForegroundColor Yellow
        $choice = Read-Host
        Write-Host ""

        switch ($choice) {
            "1" { $Action = "install" }
            "2" { $Action = "uninstall" }
            "3" { $Action = "update" }
            "4" { $Action = "reinstall" }
            default { Write-Info "退出"; exit 0 }
        }
    } else {
        Write-Err "非交互模式需要指定 -Action 参数"
        Write-Host "  用法: .\install.ps1 -Action install|uninstall|update|reinstall"
        exit 1
    }
}

switch ($Action) {
    "install" { Do-Install }
    "uninstall" { Do-Uninstall }
    "update" { Do-Update }
    "reinstall" { Do-Reinstall }
}