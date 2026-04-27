# AgentHub AI 使用指南

> ⚠️ **AI 必读** | 版本: v2.1 | 更新: 2026-04-27
> **首次使用本项目前，必须先完成下方「快速初始化」步骤！**

---

## 🚀 快速初始化（30秒完成）

任何 AI 首次启动时，**立即执行**以下三步，禁止跳过：

### Step 1 — 注册自己

读取 `~/.agenthub/agents/registry.json`，若自己未在其中，执行注册：

```python
import json, os
from datetime import datetime

path = os.path.expanduser("~/.agenthub/agents/registry.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
reg = json.load(open(path)) if os.path.exists(path) else {"agents": {}}

my_id = "your-agent-id"  # 改为你自己的 ID
if my_id not in reg["agents"]:
    reg["agents"][my_id] = {
        "id": my_id, "signature": f"[{my_id}]", "display_name": "Your Name",
        "type": "general", "first_seen": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_active": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "capabilities": [], "platform": "unknown", "status": "active"
    }
    json.dump(reg, open(path,"w"), ensure_ascii=False, indent=2)
    print(f"[{my_id}] 注册成功")
else:
    print(f"[{my_id}] 已注册")
```

### Step 2 — 读取用户画像

```bash
cat ~/.agenthub/profile/identity.yaml
cat ~/.agenthub/profile/health/身体.md
```

### Step 3 — 确认记忆系统

检查以下目录存在：`~/.agenthub/memory/`、`~/.agenthub/agents/`、`~/.agenthub/profile/`

**完成后才能开始工作。** 详见 `agents/onboarding-protocol.md`。

---

> 版本: v2.1 | 更新: 2026-04-27
> 本文档供 AI 助手阅读，了解如何使用 AgentHub 框架。

---

## 🎯 是什么

AgentHub 是一个**跨平台 AI 工具配置框架**，让 AI 助手能够：
- 加载共享 Skills（可复用功能模块）
- 使用统一的用户画像（了解用户偏好）
- 利用持久化记忆（跨会话学习）

## 📂 关键目录

| 目录 | 作用 |
|------|------|
| `~/.agenthub/profile/` | 用户画像，包含身份、偏好、路径 |
| `~/.agenthub/skills/` | 已安装的 Skills |
| `~/.agenthub/agents/` | Agent 配置文件 |
| `~/.agenthub/memory/` | 记忆存储 |

## 👤 用户画像

**必读文件**: `~/.agenthub/profile/identity.yaml`

```yaml
name: 用户名
basic:
  email: user@example.com
  location: 城市
personality:
  communication_style: 直接/委婉
preferences:
  aesthetic:
    primary_color: "#c45d2c"
```

**读取方式**:
```python
import yaml
with open("~/.agenthub/profile/identity.yaml") as f:
    profile = yaml.safe_load(f)
```

## 🛠️ Skills 使用

Skills 是可复用的功能模块，通过**触发词**自动加载。

### 触发词示例

| Skill | 触发词 | 功能 |
|-------|--------|------|
| github-pr | "github pr"、"推送" | GitHub PR 管理 |
| adb-debug | "adb"、"调试" | Android 调试 |
| browser-bridge | "浏览器"、"打开网页" | 浏览器自动化 |

### 加载 Skill

```python
from agenthub.core.skill.registry import SkillRegistry

registry = SkillRegistry()
skill = registry.get("github-pr")  # 按名称获取
results = registry.find_by_trigger("用户说想管理pr")  # 按触发词查找
```

## 🤖 Agents

Agents 是专业角色配置，定义了该 AI 的职责和技能绑定。

### 内置 Agents

| Agent | 类型 | 职责 |
|-------|------|------|
| main-agent | router | 总调度入口 |
| dev-agent | specialist | 开发任务 |
| life-agent | specialist | 生活服务 |
| ops-agent | specialist | 运营任务 |

### 路由规则

```
用户输入 → 触发词匹配 → 选择 Agent → 执行 Skill → 返回结果
```

## 💾 记忆系统

AgentHub 提供多层记忆，AI 应该主动写入重要信息。

### 记忆层级

| 级别 | 名称 | 说明 |
|------|------|------|
| L0 | 工作记忆 | 当前任务执行中的临时数据 |
| L1 | 上下文 | 当前会话的上下文 |
| L2 | 短期记忆 | 7天内重要的信息 |
| L3 | 长期记忆 | 永久保留的重要事实 |

### 使用记忆

```python
from agenthub.core.memory import MemoryEngine

memory = MemoryEngine("~/.agenthub/memory")

# 记住重要信息
memory.add("用户喜欢简洁的代码风格", level=3)

# 搜索记忆
results = memory.search("用户偏好")
```

### 写入原则

1. **用户明确偏好** → 写入 L3（长期）
2. **项目关键信息** → 写入 L2（短期）
3. **当前任务状态** → 写入 L0/L1（工作）

## 📝 常用命令

```bash
# Skills
agenthub skill list              # 列出 Skills
agenthub skill search <关键词>   # 搜索 Skill

# Agents
agenthub agent list             # 列出 Agents
agenthub agent info <名称>      # 查看详情

# 记忆
agenthub memory stats           # 记忆统计
agenthub memory search <关键词>  # 搜索记忆
```

## 🔑 核心规范

### 1. 优先读取用户画像

首次对话应读取 `~/.agenthub/profile/identity.yaml` 了解用户。

### 2. 主动记忆重要信息

用户告诉的偏好、项目信息等，应主动写入记忆系统。

### 3. 复用 Skills

遇到常见任务，先搜索是否有对应 Skill，避免重复造轮子。

### 4. 遵循触发词机制

Skill 通过触发词激活，不要硬编码 Skill 逻辑。

### 5. 尊重用户隐私

用户画像和记忆中的敏感信息不要外泄。

## 🤖 Agent 注册与署名

### 注册表

所有 AI Agent 都在 `~/.agenthub/agents/registry.json` 注册：

```json
{
  "agents": {
    "dev-agent": {
      "id": "dev-agent",
      "signature": "[dev]",
      "display_name": "Dev Agent",
      "type": "specialist",
      "capabilities": ["coding", "fullstack"],
      "status": "active"
    }
  }
}
```

### 署名格式

所有 AI 输出必须带署名，格式为 `[agent-id]`：

```
[hermes] 已完成记忆系统更新。
[dev] 开始处理开发任务...
[life] 今日课程：无课
```

### 新 AI 注册流程

1. 读取 `~/.agenthub/agents/registry.json`
2. 检查自己是否已注册
3. 未注册则添加自己的身份
4. 每次会话更新 `last_active`

详见 `~/.agenthub/agents/onboarding-protocol.md`

---

## 📁 文件位置

| 文件 | 路径 |
|------|------|
| 用户画像 | `~/.agenthub/profile/identity.yaml` |
| Skills 注册表 | `~/.agenthub/registry.json` |
| Agent 注册表 | `~/.agenthub/agents/registry.json` |
| 记忆存储 | `~/.agenthub/memory/` |
| Agent 模板 | `~/.agenthub/agents/templates/proactive/` |
| 配置文件 | `~/.agenthub/config.yaml` |

---

## 📚 Agent 模板（Proactive Agent 系列）

AgentHub 提供源自 **proactive-agent (Hal Labs)** 的专业模板，位于 `agents/templates/proactive/`：

| 模板 | 说明 |
|------|------|
| `SOUL.md` | Agent 身份与原则定义 |
| `AGENTS.md` | Agent 操作规则与工作流 |
| `HEARTBEAT.md` | 定期自检清单（安全/自我修复/主动） |
| `USER.md` | 用户信息模板 |
| `MEMORY.md` | 长期记忆模板 |
| `ONBOARDING.md` | 新用户初始化向导 |
| `TOOLS.md` | 工具配置与笔记 |

这些模板帮助 Agent 实现：
- **主动** — 不等待指令，主动创造价值
- **持久** — 通过记忆系统跨会话学习
- **安全** — 定期自检，防止prompt注入

---

*本文档由 AgentHub 自动生成，v2.0 新增 Agent 注册与模板支持。*
