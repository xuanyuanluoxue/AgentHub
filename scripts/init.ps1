# AgentHub 初始化脚本 - Windows PowerShell

Write-Host "🚀 AgentHub 初始化..." -ForegroundColor Cyan

# 检查 Git
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    Write-Host "✓ Git 已安装" -ForegroundColor Green
} else {
    Write-Host "❌ Git 未安装" -ForegroundColor Red
    exit 1
}

# 检查 Python (可选)
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    Write-Host "✓ Python 已安装" -ForegroundColor Green
} else {
    Write-Host "⚠ Python 未安装 (可选)" -ForegroundColor Yellow
}

# 检查 Node.js (可选)
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    Write-Host "✓ Node.js 已安装" -ForegroundColor Green
} else {
    Write-Host "⚠ Node.js 未安装 (可选)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📁 目录结构:" -ForegroundColor Cyan
Write-Host "├── profile/      # 用户画像"
Write-Host "├── skills/       # 共享技能库"
Write-Host "├── agents/       # Agent 配置"
Write-Host "├── projects/     # 项目配置"
Write-Host "└── docs/         # 文档"

Write-Host ""
Write-Host "✅ 初始化完成！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:"
Write-Host "  1. 编辑 profile/identity.md 填写你的信息"
Write-Host "  2. 查看 agents/router.md 了解路由规则"
Write-Host "  3. 查看 skills/ 了解可用技能"
