<#
AgentHub 一键安装脚本 - Windows PowerShell

用法:
  irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/scripts/install.ps1 | iex
  或
  .\install.ps1
#>

param(
    [string]$InstallDir = "$env:USERPROFILE\.agenthub"
)

$ErrorActionPreference = "Continue"

# ============================================
# 颜色定义
# ============================================
function Write-Info { Write-Host "➜ $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Warn { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Step { Write-Host "▸ $args" -ForegroundColor Cyan }
function Write-Dim { Write-Host $args -ForegroundColor DarkGray }
function Write-Banner { Write-Host $args -ForegroundColor Magenta }

# ============================================
# Banner
# ============================================
function Print-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║          ██╗   ██╗ ██████╗ ██████╗ ██████╗ ██╗   ██╗   ║" -ForegroundColor Magenta
    Write-Host "║          ██║   ██║██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝   ║" -ForegroundColor Magenta
    Write-Host "║          ██║   ██║██║   ██║██████╔╝██████╔╝ ╚████╔╝    ║" -ForegroundColor Magenta
    Write-Host "║          ╚██╗ ██╔╝██║   ██║██╔══██╗██╔══██╗  ╚██╔╝     ║" -ForegroundColor Magenta
    Write-Host "║           ╚████╔╝ ╚██████╔╝██████╔╝██████╔╝   ██║      ║" -ForegroundColor Magenta
    Write-Host "║            ╚═══╝   ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝      ║" -ForegroundColor Magenta
    Write-Host "║                 统一 AI 工具四大共享生态                ║" -ForegroundColor Cyan
    Write-Host "║                 Skill · Agent · 画像 · 记忆系统         ║" -ForegroundColor DarkGray
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

# ============================================
# 分隔线
# ============================================
function Print-Divider {
    Write-Host ("─" * 56) -ForegroundColor DarkGray
}

# ============================================
# 检查依赖
# ============================================
function Check-Dependencies {
    Write-Host ""
    Write-Host "▸ 检查系统依赖" -ForegroundColor White
    Print-Divider

    $allOk = $true

    # Git
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        $gitVersion = (git --version 2>&1) -replace "^git version ", ""
        Write-Host "  ✓ git $gitVersion" -ForegroundColor Green
    } else {
        Write-Host "  ✗ git (未找到)" -ForegroundColor Red
        $allOk = $false
    }

    # Python
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $pythonVersion = (python --version 2>&1) -replace "^Python ", ""
        Write-Host "  ✓ python $pythonVersion" -ForegroundColor Green

        # 检查版本
        $ver = $pythonVersion -split '\.'
        if ([int]$ver[0] -lt 3 -or ([int]$ver[0] -eq 3 -and [int]$ver[1] -lt 10)) {
            Write-Host "  ✗ Python 版本过低 (需要 >= 3.10)" -ForegroundColor Red
            $allOk = $false
        }
    } else {
        Write-Host "  ✗ python (未找到)" -ForegroundColor Red
        $allOk = $false
    }

    # pip
    $pip = Get-Command pip -ErrorAction SilentlyContinue
    if ($pip) {
        Write-Host "  ✓ pip" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ pip (未找到，尝试使用 python -m pip)" -ForegroundColor Yellow
    }

    Write-Host ""

    if (-not $allOk) {
        Write-Err "缺少必要的系统依赖"
        Write-Host ""
        Write-Dim "请先安装缺失的依赖:"
        Write-Host "  下载 Git: https://git-scm.com/download/win" -ForegroundColor Cyan
        Write-Host "  下载 Python: https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host ""
        exit 1
    }

    Write-Success "所有依赖检查通过"
    Write-Host ""
}

# ============================================
# 备份现有配置
# ============================================
function Backup-Existing {
    if (Test-Path $InstallDir) {
        Write-Host "▸ 备份现有配置" -ForegroundColor White
        Print-Divider
        Write-Warn "发现已存在的 AgentHub 配置"

        $confirm = Read-Host "  是否备份? [y/N]"
        Write-Host ""

        if ($confirm -match "^[Yy]$") {
            $backupDir = "$env:USERPROFILE\.agenthub.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
            Write-Info "正在备份到 $backupDir..."
            try {
                Copy-Item -Path $InstallDir -Destination $backupDir -Recurse -Force -ErrorAction Stop
                Write-Success "备份完成"
            } catch {
                Write-Err "备份失败: $_"
                exit 1
            }
        } else {
            Write-Warn "跳过备份，现有配置将被覆盖"
            Remove-Item -Recurse -Force $InstallDir -ErrorAction SilentlyContinue
        }
        Write-Host ""
    }
}

# ============================================
# 克隆仓库
# ============================================
function Clone-Repo {
    Write-Host "▸ 下载 AgentHub" -ForegroundColor White
    Print-Divider

    $repoUrl = "https://github.com/xuanyuanluoxue/AgentHub.git"

    if ((Test-Path $InstallDir) -and (Test-Path "$InstallDir\pyproject.toml")) {
        Write-Info "发现已安装的 AgentHub，跳过下载"
        Write-Host "  目录: $InstallDir" -ForegroundColor DarkGray
        Write-Host ""
        return
    }

    Write-Info "正在克隆仓库..."
    Write-Host "  来源: $repoUrl" -ForegroundColor DarkGray
    Write-Host "  目标: $InstallDir" -ForegroundColor DarkGray
    Write-Host ""

    try {
        $gitArgs = @("clone", "--depth", "1", $repoUrl, $InstallDir)
        git $gitArgs 2>&1 | Out-Null

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Success "仓库克隆完成"
            Write-Host ""
        } else {
            throw "git clone failed with exit code $LASTEXITCODE"
        }
    } catch {
        Write-Host ""
        Write-Err "克隆失败: $_"
        Write-Host ""
        Write-Host "请检查:" -ForegroundColor Yellow
        Write-Host "  1. 网络连接是否正常" -ForegroundColor DarkGray
        Write-Host "  2. Git 是否正确配置" -ForegroundColor DarkGray
        Write-Host "  3. 尝试手动克隆: git clone $repoUrl $InstallDir" -ForegroundColor DarkGray
        Write-Host ""
        exit 1
    }
}

# ============================================
# 安装 Python 包
# ============================================
function Install-Package {
    Write-Host "▸ 安装 Python 包" -ForegroundColor White
    Print-Divider

    if (-not (Test-Path "$InstallDir\pyproject.toml")) {
        Write-Err "pyproject.toml 不存在"
        exit 1
    }

    Push-Location $InstallDir

    Write-Info "正在安装 AgentHub CLI..."

    # 尝试 pip install
    $pipCmd = Get-Command pip -ErrorAction SilentlyContinue
    if (-not $pipCmd) {
        Write-Info "使用 python -m pip..."
        $pipCmd = "python -m pip"
    }

    try {
        $installOutput = & python -m pip install -e . 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Success "Python 包安装完成"
        } else {
            throw "pip install failed"
        }
    } catch {
        Write-Host ""
        Write-Warn "安装失败，尝试使用 --user..."
        try {
            $installOutput = & python -m pip install -e . --user 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Success "Python 包安装完成 (--user)"
            } else {
                throw "pip install --user failed"
            }
        } catch {
            Write-Host ""
            Write-Err "安装失败: $_"
            Write-Host ""
            Write-Host "请手动运行以下命令:" -ForegroundColor Yellow
            Write-Host "  cd $InstallDir" -ForegroundColor Cyan
            Write-Host "  pip install -e ." -ForegroundColor Cyan
            Write-Host ""
            Pop-Location
            exit 1
        }
    }

    Pop-Location

    # 验证安装
    Write-Host ""
    $agenthubCmd = Get-Command agenthub -ErrorAction SilentlyContinue
    if ($agenthubCmd) {
        try {
            $version = (agenthub --version 2>&1) -replace "agenthub, version ", ""
            Write-Host "  ✓ agenthub v$version" -ForegroundColor Green
        } catch {
            Write-Host "  ✓ agenthub" -ForegroundColor Green
        }
    } else {
        Write-Host "  ⚠ agenthub (未添加到 PATH)" -ForegroundColor Yellow
        Write-Host "  尝试刷新环境变量..." -ForegroundColor DarkGray
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    }
    Write-Host ""
}

# ============================================
# 初始化配置
# ============================================
function Init-Config {
    Write-Host "▸ 初始化配置" -ForegroundColor White
    Print-Divider

    # 创建必要的目录
    $dirs = @("skills", "agents", "profile", "apps")
    foreach ($dir in $dirs) {
        $path = Join-Path $InstallDir $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Force -Path $path | Out-Null
        }
    }

    # 检查是否已有配置
    $identityFile = Join-Path $InstallDir "profile\identity.yaml"
    if (Test-Path $identityFile) {
        Write-Info "配置文件已存在，跳过初始化"
        Write-Host ""
        return
    }

    Write-Info "创建默认配置文件..."

    # 创建默认 identity.yaml
    @"
name: Your Name
bio: AI enthusiast and developer
contact:
  email: your@email.com
  github: https://github.com/your-username
preferences:
  language: zh-CN
  theme: auto
"@ | Out-File -FilePath $identityFile -Encoding UTF8

    # 创建 registry.json
    @"
{
  "skills": [],
  "agents": [],
  "version": "1.0"
}
"@ | Out-File -FilePath (Join-Path $InstallDir "registry.json") -Encoding UTF8

    Write-Success "配置文件创建完成"
    Write-Host ""
}

# ============================================
# 完成
# ============================================
function Print-Complete {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                      安装完成！                           ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "▸ 下一步" -ForegroundColor White
    Print-Divider
    Write-Host "  1. 编辑配置文件" -ForegroundColor Cyan
    Write-Host "     notepad $InstallDir\profile\identity.yaml" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  2. 尝试验证安装" -ForegroundColor Cyan
    Write-Host "     agenthub status" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  3. 搜索 ClawHub Skills" -ForegroundColor Cyan
    Write-Host "     agenthub clawhub search github" -ForegroundColor DarkGray
    Write-Host ""

    $agenthubCmd = Get-Command agenthub -ErrorAction SilentlyContinue
    if ($agenthubCmd) {
        Write-Host "  ✓ agenthub 已添加到 PATH" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ agenthub 未找到，请重新打开 PowerShell" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  或手动刷新环境变量:" -ForegroundColor Yellow
        Write-Host "  \$env:Path = [System.Environment]::GetEnvironmentVariable('Path','User') + ';' + [System.Environment]::GetEnvironmentVariable('Path','Machine')" -ForegroundColor DarkGray
    }

    Write-Host ""
    Write-Host "帮助文档: https://github.com/xuanyuanluoxue/AgentHub" -ForegroundColor DarkGray
    Write-Host ""
}

# ============================================
# 主流程
# ============================================
function Main {
    Print-Banner
    Check-Dependencies
    Backup-Existing
    Clone-Repo
    Install-Package
    Init-Config
    Print-Complete
}

Main
