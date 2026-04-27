# AgentHub 开发文档

> 本目录为开发专用，不提交 Git。

---

## 📌 项目定位

**AgentHub** 是一个**公共开源项目模板**，用于展示 AI 工具统一的 Skill · Agent · 用户画像 · 记忆系统 四大共享生态的架构设计。

### 与 xavier 的关系

| 项目 | 定位 | 内容 |
|------|------|------|
| **xavier** | 私人使用版 | 包含个人真实数据（姓名、联系方式、路径等） |
| **agenthub** | 公共模板版 | 仅包含架构设计和示例，无任何私人信息 |

> ⚠️ **重要**: AgentHub 是模板项目，不包含任何私人信息。所有文档中的路径、账号、人名等均为**占位符**，仅用于展示架构设计。

### 隐私声明

AgentHub 公共版本已移除：
- ❌ 个人信息（姓名、邮箱、电话）
- ❌ 私人路径（`C:\Users\Chatxavier\`、`D:\Obsidian\`）
- ❌ 服务器地址（IP、域名）
- ❌ 社交账号（GitHub、微信等）

---

## 📦 xavier 用户使用指南

如果你想基于 AgentHub 创建自己的配置：

1. **克隆项目**
   ```bash
   git clone https://github.com/your-org/agenthub.git ~/.agenthub
   ```

2. **替换个人信息**
   - 修改 `profile/identity.yaml` 为你的真实信息
   - 修改 `agents/` 下 Agent 配置中的路径为你的路径
   - 修改 `docs/` 中示例路径为你的实际路径

3. **初始化**
   ```bash
   cd ~/.agenthub
   pip install -e .
   agenthub init
   ```

---

## 📁 项目结构

```
.agenthub/
├── core/agenthub/          # Python 包源码
├── docs/                   # 架构文档（模板形式）
├── profile/                # 用户画像模板
├── agents/                 # Agent 配置模板
├── skills/                # Skill 示例模板
└── skills-library/         # 共享技能库模板
```

---

## 🔧 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python >= 3.10 |
| CLI | Click |
| 配置 | PyYAML |
| 版本 | SemVer |
| 测试 | Pytest |

---

## ⚠️ 开发注意事项

1. **dev/ 目录不提交 Git**（已加入 .gitignore）
2. **secrets/ 目录不提交 Git**（已加入 .gitignore）
3. **隐私检查**：所有公共文档不得包含私人信息
4. **路径规范**：使用 `~/`、`~/.config/` 等通用路径

---

## 🚀 快速开始

### 一键安装

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/your-org/agenthub/main/scripts/install.ps1 | iex
```

**Linux / macOS / WSL:**
```bash
curl -fsSL https://raw.githubusercontent.com/your-org/agenthub/main/scripts/install.sh | bash
```

### 初始化命令

```bash
agenthub init --template    # 快速初始化
agenthub init -n "你的名字"  # 指定名称
agenthub init --force      # 强制重新初始化
```

---

*最后更新：2026-04-27*
