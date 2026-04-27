# AgentHub AI 使用指南

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

## 📁 文件位置

| 文件 | 路径 |
|------|------|
| 用户画像 | `~/.agenthub/profile/identity.yaml` |
| Skills 注册表 | `~/.agenthub/registry.json` |
| 记忆存储 | `~/.agenthub/memory/` |
| 配置文件 | `~/.agenthub/config.yaml` |

---

*本文档由 AgentHub 自动生成*
