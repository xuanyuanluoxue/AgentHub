# AgentHub 安装脚本

> 统一 AI 工具的 Skill · Agent · 画像 · 记忆系统 四大共享生态

## 目录结构

```
misc/
├── install.sh              # 路由脚本（自动检测系统）
└── install/
    ├── linux/              # Linux 安装脚本
    │   └── install.sh
    ├── macos/              # macOS 安装脚本
    │   └── install.sh
    ├── wsl/                # WSL 安装脚本
    │   └── install.sh
    └── windows/            # Windows 安装脚本
        └── install.ps1
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

| 操作 | 说明 |
|------|------|
| `install` | 安装 |
| `uninstall` | 卸载 |
| `update` | 更新 |
| `reinstall` | 恢复出厂设置 |

## 使用方法

### 交互模式（直接运行）

```bash
curl -fsSL .../install.sh | bash
```

### 非交互模式（指定操作）

```bash
curl -fsSL .../install.sh | bash -s -- install
curl -fsSL .../install.sh | bash -s -- uninstall
curl -fsSL .../install.sh | bash -s -- update
curl -fsSL .../install.sh | bash -s -- reinstall
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

## 项目更新

已安装用户可以通过以下命令更新：

```bash
agenthub update
```

或手动：
```bash
cd ~/.agenthub && git pull && pip install -e .
```