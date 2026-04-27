# AgentHub

> 统一 AI 工具的 Skill · Agent · 用户画像 · 记忆系统 四大共享生态

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚠️ 隐私声明

> **重要**: AgentHub 是**公共开源模板项目**，不包含任何私人信息。
>
> - 所有文档中的路径、账号、人名等均为**占位符**
> - 如果你看到类似 `your-server-ip`、`username`、`your-org` 等，请理解为占位符
> - 如需使用，请基于模板创建你自己的配置

---

## 🎯 项目愿景

当前 AI 开发工具（OpenClaw、OpenCode、ClawHub、Claude Code 等）各自为战：
- Skill 无法互通，重复开发
- Agent 每工具独立配置
- 用户画像换工具就丢失
- 记忆不持久，每次对话重新开始

**AgentHub 致力于构建跨平台统一规范，实现四大共享生态。**

---

## 💎 四大核心卖点

### 1️⃣ 共享 Skill 库 — 一次编写，到处运行

| 特性 | 说明 |
|------|------|
| **统一格式** | YAML frontmatter + Markdown，工具无关 |
| **跨平台兼容** | OpenClaw / OpenCode / ClawHub / Hermes 通用 |
| **依赖管理** | SemVer 版本控制，自动解析依赖 |
| **触发词机制** | 智能匹配用户输入，自动加载 Skill |
| **云端市场** | 无需 API Key，直接安装 ClawHub 商店 Skills |

```
skills/
├── github-pr/              # GitHub PR 管理
├── adb-debug/              # ADB 调试
├── browser-bridge/         # 浏览器自动化
└── 50+ 共享 Skill
```

**🚀 一键安装 ClawHub 商店 Skills（无需 API Key）：**
```bash
agenthub clawhub search github     # 搜索 Skills
agenthub clawhub install github    # 安装到本地
```

[📖 Skill 规范 v2.0](./docs/design/skill-format.md)

---

### 2️⃣ 共享 Agent 库 — 专业角色，智能路由

| 特性 | 说明 |
|------|------|
| **类型定义** | Router（路由型）+ Specialist（专家型） |
| **技能绑定** | 自动加载所需 Skills |
| **记忆配置** | 短期/长期记忆策略可定制 |
| **跨工具共享** | 同一 Agent 配置，多工具通用 |

```
agents/
├── main-agent/             # 主路由入口
├── dev-agent/              # 开发专家
├── life-agent/             # 生活服务
├── ops-agent/              # 运营助手
└── productivity-agent/     # 效率工具
```

[📖 Agent 规范 v1.0](./docs/agent-format.md)

---

### 3️⃣ 共享用户画像 — 工具无关，永久携带

| 特性 | 说明 |
|------|------|
| **统一格式** | YAML + Markdown，纯文本工具无关 |
| **身份信息** | 基础资料、联系方式、社交账号 |
| **偏好设置** | 审美偏好、沟通风格、回复习惯 |
| **常用路径** | 项目目录、知识库、配置文件路径 |

```
profile/
├── identity.yaml           # 身份信息
├── skills.md              # 技能图谱
├── contacts/              # 联系人（全中文命名）
└── growth/                # 成长轨迹
```

[📖 用户画像规范 v1.0](./docs/user-profile-spec.md)

---

### 4️⃣ 共享记忆系统 — 持久记忆，持续学习

| 特性 | 说明 |
|------|------|
| **多层记忆** | 短期 / 长期 / 知识库 三层架构 |
| **向量检索** | 基于语义相似度的记忆召回 |
| **上下文管理** | 智能裁剪上下文窗口 |
| **跨工具同步** | 记忆在多工具间共享 |

```
memory/
├── short_term/            # 短期记忆（会话级）
├── long_term/              # 长期记忆（持久化）
├── knowledge/              # 知识库（结构化）
└── retrieval/              # 检索引擎
```

[📖 记忆系统设计](./docs/memory-system.md)

---

## 📁 目录结构

```
.agenthub/
├── core/agenthub/          # Python 包
│   ├── cli/                # CLI 命令
│   └── core/               # Agent / Memory / Skill / Config
├── docs/                   # 规范文档
│   ├── skill-format.md     # ★ Skill 规范
│   ├── agent-format.md     # ★ Agent 规范
│   ├── user-profile-spec.md # ★ 用户画像规范
│   └── memory-system.md    # ★ 记忆系统设计
├── profile/                # ★ 用户画像
├── agents/                 # ★ Agent 配置
├── skills/                 # ★ Skill 示例
└── skills-library/         # ★ 共享技能库
```

---

## 🚀 快速开始

### 一键安装（推荐）

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/your-org/agenthub/main/scripts/install.ps1 | iex
```

**Linux / macOS / WSL:**
```bash
curl -fsSL https://raw.githubusercontent.com/your-org/agenthub/main/scripts/install.sh | bash
```

### 手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/agenthub.git ~/.agenthub

# 2. 安装 Python 包
cd ~/.agenthub
pip install -e .

# 3. 初始化配置
agenthub init --template    # 快速初始化（使用模板）
agenthub init              # 交互式初始化（自定义名称）

# 4. 开始使用
agenthub --help
```

### 安装后

```bash
agenthub skill list        # 查看已安装 Skills
agenthub agent list        # 查看已安装 Agents
agenthub profile validate   # 验证配置
```

---

## 🤝 支持的工具

| 工具 | Skill | Agent | 画像 | 记忆 |
|------|-------|-------|------|------|
| OpenClaw | ✅ | ✅ | ✅ | ✅ |
| OpenCode | ✅ | ✅ | ✅ | ✅ |
| ClawHub | ✅ | ✅ | ✅ | ✅ |
| Hermes Agent | ✅ | ✅ | ✅ | ✅ |
| Claude Code | ✅ | 🔄 | 🔄 | 🔄 |

---

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [项目愿景](./docs/project/项目愿景.md) | 问题分析、解决方案、核心价值 |
| [AI 使用指南](./docs/for-ai/AI_GUIDE.md) | **★ AI 助手必读** |
| [Skill 规范](./docs/design/skill-format.md) | v2.0 规范详解 + 示例 |
| [Agent 规范](./docs/design/agent-format.md) | v1.0 规范详解 + 示例 |
| [用户画像规范](./docs/for-ai/user-profile-spec.md) | v1.0 规范详解 |
| [记忆系统设计](./docs/design/memory-system.md) | 多层记忆架构 |

---

## 🔑 核心价值

| 价值 | 说明 |
|------|------|
| **降本增效** | Skill 复用，避免重复开发 |
| **生态互通** | 打破工具壁垒，自由切换 |
| **知识沉淀** | Agent、Profile、Memory 共享，集体智慧 |
| **持续学习** | 记忆持久化，AI 越用越懂你 |

---

## 📄 License

MIT License

---

*愿景驱动，代码落地。*
