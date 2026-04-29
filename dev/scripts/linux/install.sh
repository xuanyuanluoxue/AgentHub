# AgentHub 安装脚本

> 支持 Linux / macOS / Windows (WSL/Git Bash)

## 使用方法

### Linux / macOS / WSL

```bash
curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash
# 或
bash <(curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh)
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.ps1 | iex
```

### Windows (Git Bash / WSL)

```bash
curl -fsSL https://raw.githubusercontent.com/xuanyuanluoxue/AgentHub/main/misc/install.sh | bash
```

---

## 脚本说明

| 脚本 | 说明 |
|------|------|
| `install.sh` | Linux/macOS/WSL 安装脚本 |
| `install.ps1` | Windows PowerShell 安装脚本 |
| `uninstall.sh` | Linux/macOS 卸载脚本 |
| `uninstall.ps1` | Windows 卸载脚本 |

---

## 安装选项

- **交互模式**：直接运行脚本，显示菜单选择
- **非交互模式**：`--install` 安装，`--uninstall` 卸载

---

*最后更新：2026-04-29*