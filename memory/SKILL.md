---
name: memory-system
description: AgentHub 记忆系统 - 多层记忆架构。hot/cold/archive 三层 + memories/MEMORY.md。
license: MIT
version: "2.0.0"
category: system
tags:
  - memory
  - context
  - storage
  - agenthub
triggers:
  - "记忆"
  - "记住"
  - "之前做过"
platform:
  - opencode
  - hermes
  - claude
  - any-ai
---

# AgentHub 记忆系统 - AI 使用规范

## 目录结构

```
~/.agenthub/memory/
├── memories/                 # 核心记忆
│   ├── MEMORY.md           # 重要事实（用 § 分隔）
│   └── USER.md             # 用户画像简要
├── hot/                     # 短期记忆（60分钟）
├── cold/                    # 中期记忆（7-30天）
│   ├── facts/              # 事实存储
│   └── preferences/         # 偏好存储
├── archive/                 # 归档记忆（永久）
├── knowledge/               # 知识图谱
│   ├── nodes/
│   └── edges/
├── agents/                  # Agent 注册表
│   ├── registry.json
│   ├── registry-meta.json
│   ├── onboarding-protocol.md
│   └── templates/
└── _index/                  # 索引文件
```

## 记忆层级

| 层级 | 名称 | TTL | 说明 |
|------|------|-----|------|
| Hot | 短期记忆 | 60分钟 | 当前会话的活跃信息 |
| Cold | 中期记忆 | 7-30天 | 重要事实和偏好 |
| Archive | 归档记忆 | 永久 | 经验证的重要信息 |

## 读写规范

### 对话开始时读取

```
1. 读取 memories/MEMORY.md 了解重要事实
2. 读取 memories/USER.md 了解用户画像简要
3. 检查 hot/ 是否有最近会话记录
```

### 对话中写入（立即！）

```
✅ 发现新信息 → 写入 hot/
✅ 用户纠正偏好 → 写入 cold/preferences/
✅ 完成复杂任务 → 写入 cold/
✅ 验证信息有效 → 写入 archive/
✅ 遇到错误/坑 → 追加到 memories/MEMORY.md（使用 § 分隔）
```

## Agent 署名

所有 AI 输出必须带署名：`[agent-id]`

## memories/MEMORY.md 格式

```markdown
# MEMORY.md

- 重要事实/偏好1
§
- 重要事实/偏好2
§
- 重要事实/偏好3
```

---

*参考: Hermes + Xavier 记忆系统设计 v2.0*
