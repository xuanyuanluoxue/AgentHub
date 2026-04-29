# AgentHub 安装脚本

> 统一 AI 工具的 Skill · Agent · 画像 · 记忆系统 四大共享生态

## 一键安装

### Linux / macOS / WSL

```bash
curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.ps1 | iex
```

## 功能

| 功能 | 说明 |
|------|------|
| **install** | 安装 AgentHub |
| **uninstall** | 卸载 AgentHub |
| **update** | 更新 AgentHub |
| **reinstall** | 恢复出厂设置（卸载 + 重新安装） |

## 使用方法

### 交互模式（直接运行）

```bash
# Linux/macOS/WSL
curl -fsSL .../install.sh | bash

# Windows
irm .../install.ps1 | iex
```

### 非交互模式（指定操作）

```bash
# Linux/macOS/WSL
curl -fsSL .../install.sh | bash -s -- install
curl -fsSL .../install.sh | bash -s -- uninstall
curl -fsSL .../install.sh | bash -s -- update
curl -fsSL .../install.sh | bash -s -- reinstall

# Windows PowerShell
.\install.ps1 -Action install
.\install.ps1 -Action uninstall
.\install.ps1 -Action update
.\install.ps1 -Action reinstall
```

## 安装位置

```
~/.agenthub/   # Linux/macOS/WSL
%USERPROFILE%\.agenthub\   # Windows
```

## 系统检测

`install.sh` 自动检测以下系统并路由到对应脚本：
- Linux
- macOS
- Windows Subsystem for Linux (WSL)
- Windows (PowerShell)

## 安装后

```bash
agenthub --help     # 查看帮助
```

## 卸载

```bash
curl -fsSL .../install.sh | bash -s -- uninstall
```