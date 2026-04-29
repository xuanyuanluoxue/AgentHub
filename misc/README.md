# AgentHub 安装脚本

> 统一 AI 工具的 Skill · Agent · 画像 · 记忆系统 四大共享生态

## 一键安装

### Linux / macOS / WSL

```bash
curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash
```

或指定操作：
```bash
# 安装
curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash -s -- --install

# 卸载
curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash -s -- --uninstall
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.ps1 | iex
```

## 脚本说明

| 脚本 | 说明 | 平台 |
|------|------|------|
| `install.sh` | 路由脚本，自动检测系统 | Linux/macOS/WSL/Windows |
| `install.ps1` | 安装脚本 | Windows PowerShell |
| `install-linux.sh` | Linux 安装脚本 | Linux |
| `install-macos.sh` | macOS 安装脚本 | macOS |
| `install-wsl.sh` | WSL 安装脚本 | WSL |
| `uninstall.sh` | 卸载路由脚本 | Linux/macOS/WSL/Windows |
| `uninstall.ps1` | 卸载脚本 | Windows PowerShell |
| `uninstall-linux.sh` | Linux 卸载脚本 | Linux |
| `uninstall-macos.sh` | macOS 卸载脚本 | macOS |
| `uninstall-wsl.sh` | WSL 卸载脚本 | WSL |

## 安装选项

- **交互模式**：直接运行脚本，显示菜单选择
- **非交互模式**：`--install` 安装，`--uninstall` 卸载

## 系统检测

`install.sh` 会自动检测以下系统：
- Linux
- macOS
- Windows Subsystem for Linux (WSL)
- Windows (Git Bash / MSYS)

## 安装后

```bash
agenthub --help     # 查看帮助
agenthub init        # 初始化配置
```

## 卸载

```bash
# Linux/macOS/WSL
curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash -s -- --uninstall

# Windows
irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.ps1 | iex -Uninstall
```

---

*最后更新：2026-04-29*