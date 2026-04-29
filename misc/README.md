# AgentHub 安装脚本

> 统一 AI 工具的 Skill · Agent · 画像 · 记忆系统 四大共享生态

## 目录结构

```
misc/
├── install.sh              # 安装路由脚本
├── uninstall.sh            # 卸载路由脚本
├── update.sh               # 更新路由脚本
├── reinstall.sh            # 重装路由脚本（恢复出厂设置）
├── open.sh                 # 打开项目目录
└── install/                # 各系统安装脚本
    ├── linux/install.sh
    ├── macos/install.sh
    ├── wsl/install.sh
    └── windows/install.ps1
```

## 一键安装

### Linux / macOS / WSL

```bash
curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install/windows/install.ps1 | iex
```

## 功能

| 命令 | 说明 |
|------|------|
| `install` | 安装 |
| `uninstall` | 卸载 |
| `update` | 更新 |
| `reinstall` | 恢复出厂设置 |
| `open` | 打开项目目录 |

## 使用方法

### 交互模式

```bash
curl -fsSL .../install.sh | bash
```

### 非交互模式

```bash
curl -fsSL .../install.sh | bash -s -- install
curl -fsSL .../install.sh | bash -s -- uninstall
curl -fsSL .../install.sh | bash -s -- update
curl -fsSL .../install.sh | bash -s -- reinstall
curl -fsSL .../install.sh | bash -s -- open
```

## 安装位置

```
~/.agenthub/   # Linux/macOS/WSL
%USERPROFILE%\.agenthub\   # Windows
```

## 安装后

```bash
agenthub --help     # 查看帮助
```