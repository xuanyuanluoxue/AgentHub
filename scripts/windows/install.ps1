# AgentHub Windows 安装脚本
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# ============================================
# 颜色函数
# ============================================
function Write-Info { Write-Host "➜ $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Warn { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Dim { Write-Host $args -ForegroundColor DarkGray }
function Write-Banner {
    Write-Host ""
    Write-Host "  ██╗   ██╗ ██████╗ ██████╗ ██████╗ ██╗   ██╗" -ForegroundColor Magenta
    Write-Host "  ██║   ██║██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝" -ForegroundColor Magenta
    Write-Host "  ██║   ██║██║   ██║██████╔╝██████╔╝ ╚████╔╝ " -ForegroundColor Magenta
    Write-Host "  ╚██╗ ██╔╝██║   ██║██╔══██╗██╔══██╗  ╚██╔╝  " -ForegroundColor Magenta
    Write-Host "   ╚████╔╝ ╚██████╔╝██████╔╝██████╔╝   ██║   " -ForegroundColor Magenta
    Write-Host "    ╚═══╝   ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝   " -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  统一 AI 工具四大共享生态" -ForegroundColor Cyan
    Write-Host "  Skill · Agent · 画像 · 记忆系统" -ForegroundColor DarkGray
    Write-Host ""
}

function Print-Divider {
    Write-Host ("─" * 52) -ForegroundColor DarkGray
}

# ============================================
# 检查依赖
# ============================================
function Check-Deps {
    Write-Host "▸ 检查依赖" -ForegroundColor White
    Print-Divider

    $allOk = $true

    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        $ver = (git --version 2>&1) -replace "^git version ", ""
        Write-Host "  ✓ git $ver" -ForegroundColor Green
    } else {
        Write-Host "  ✗ git (未找到)" -ForegroundColor Red
        $allOk = $false
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $ver = (python --version 2>&1) -replace "^Python ", ""
        Write-Host "  ✓ python $ver" -ForegroundColor Green

        $verNum = $ver -split '\.'
        if ([int]$verNum[0] -lt 3 -or ([int]$verNum[0] -eq 3 -and [int]$verNum[1] -lt 10)) {
            Write-Host "  ✗ Python 版本过低 (需要 >= 3.10)" -ForegroundColor Red
            $allOk = $false
        }
    } else {
        Write-Host "  ✗ python (未找到)" -ForegroundColor Red
        $allOk = $false
    }

    if (-not $allOk) {
        Write-Host ""
        Write-Err "缺少依赖"
        Write-Host "  下载 Git: https://git-scm.com/download/win" -ForegroundColor Cyan
        Write-Host "  下载 Python: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }

    Write-Host ""
    Write-Success "依赖检查通过"
    Write-Host ""
}

# ============================================
# 准备目录
# ============================================
function Prepare-Dir {
    Write-Host "▸ 准备安装目录" -ForegroundColor White
    Print-Divider

    $installDir = "$env:USERPROFILE\.agenthub"

    if (Test-Path "$installDir\pyproject.toml") {
        if ($Force) {
            Write-Info "强制重装，删除旧目录"
            Remove-Item -Recurse -Force $installDir -ErrorAction SilentlyContinue
        } else {
            Write-Host -n "  检测到已安装，是否重装? [y/N]: " -ForegroundColor Yellow
            $resp = Read-Host
            Write-Host ""
            if ($resp -notmatch "^[Yy]$") {
                Write-Info "跳过安装"
                exit 0
            }
            Write-Info "删除旧目录"
            Remove-Item -Recurse -Force $installDir -ErrorAction SilentlyContinue
        }
    }

    Write-Info "创建目录: $installDir"
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    Write-Host ""
}

# ============================================
# 下载代码
# ============================================
function Clone-Repo {
    Write-Host "▸ 下载代码" -ForegroundColor White
    Print-Divider

    $installDir = "$env:USERPROFILE\.agenthub"
    $repoUrl = "https://github.com/xuanyuanluoxue/AgentHub.git"

    Write-Info "克隆仓库..."
    Write-Host "  来源: $repoUrl" -ForegroundColor DarkGray
    Write-Host "  目标: $installDir" -ForegroundColor DarkGray
    Write-Host ""

    try {
        git clone --depth 1 $repoUrl $installDir 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Success "下载完成"
            Write-Host ""
        } else {
            throw "git clone failed"
        }
    } catch {
        Write-Host ""
        Write-Err "克隆失败: $_"
        exit 1
    }
}

# ============================================
# 安装 Python 包
# ============================================
function Install-Package {
    Write-Host "▸ 安装 Python 包" -ForegroundColor White
    Print-Divider

    $installDir = "$env:USERPROFILE\.agenthub"
    Set-Location $installDir

    if (-not (Test-Path "pyproject.toml")) {
        Write-Err "pyproject.toml 不存在"
        exit 1
    }

    Write-Info "安装中..."
    Write-Host ""

    $ok = $false
    $method = ""

    # 尝试多种安装方法
    $methods = @(
        { python -m pip install --user -e . },
        { python -m pip install --break-system-packages -e . },
        { pip install --user -e . }
    )

    foreach ($m in $methods) {
        Write-Dim "  尝试: $($m.ToString().Split('{')[0].Trim())"
        try {
            & $m 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $ok = $true
                $method = $($m.ToString().Split('{')[0].Trim())
                break
            }
        } catch { }
        Write-Host ""
    }

    if ($ok) {
        Write-Success "安装完成 ($method)"
    } else {
        Write-Err "安装失败"
        Write-Host "  请手动执行: pip install --user -e ." -ForegroundColor Cyan
        exit 1
    }

    Write-Host ""

    # 验证
    $cmd = Get-Command agenthub -ErrorAction SilentlyContinue
    if ($cmd) {
        try {
            $ver = (agenthub --version 2>&1) -replace "agenthub, version ", ""
            Write-Host "  ✓ agenthub v$ver" -ForegroundColor Green
        } catch {
            Write-Host "  ✓ agenthub" -ForegroundColor Green
        }
    } else {
        Write-Host "  ⚠ 请重新打开 PowerShell" -ForegroundColor Yellow
    }
    Write-Host ""
}

# ============================================
# 初始化配置
# ============================================
function Init-Config {
    Write-Host "▸ 初始化配置" -ForegroundColor White
    Print-Divider

    $installDir = "$env:USERPROFILE\.agenthub"

    @("skills", "agents", "profile", "apps") | ForEach-Object {
        New-Item -ItemType Directory -Force -Path "$installDir\$_" | Out-Null
    }

    if (Test-Path "$installDir\profile\identity.yaml") {
        Write-Info "配置已存在，跳过"
        Write-Host ""
        return
    }

    @"
name: Your Name
bio: AI enthusiast and developer
contact:
  email: your@email.com
  github: https://github.com/your-username
preferences:
  language: zh-CN
  theme: auto
"@ | Out-File -FilePath "$installDir\profile\identity.yaml" -Encoding UTF8

    @"
{
  "skills": [],
  "agents": [],
  "version": "1.0"
}
"@ | Out-File -FilePath "$installDir\registry.json" -Encoding UTF8

    Write-Success "配置创建完成"
    Write-Host ""
}

# ============================================
# 完成
# ============================================
function Print-Complete {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "  安装完成！" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    Write-Host "  下一步:"
    Write-Host "    notepad `$env:USERPROFILE\.agenthub\profile\identity.yaml"
    Write-Host "    agenthub status"
    Write-Host ""
    Write-Host "  帮助: https://github.com/xuanyuanluoxue/AgentHub" -ForegroundColor DarkGray
    Write-Host ""
}

# ============================================
# 主流程
# ============================================
function Main {
    Write-Banner
    Check-Deps
    Prepare-Dir
    Clone-Repo
    Install-Package
    Init-Config
    Print-Complete
}

Main
