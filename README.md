# AgentHub

> AgentHub 项目 — AI Agent 开发与测试工作区

---

## 目录结构

```
.agenthub/
├── .git/                    # Git 仓库
├── .gitignore               # 忽略规则（dev/ 不提交）
├── docs/
│   └── skill-format.md      # ★ Skill 规范文档 v2.0
├── skills/
│   ├── 00-SKILL-SPEC.md     # ★ Skill 规范（同步自 xavier）
│   ├── agent/               # Agent 记忆系统
│   └── hello-world/         # 示例 Skill
├── dev/                     # 开发文件（不提交 Git）
└── ...
```

---

## Skill 规范

AgentHub 使用与 xavier 一致的 Skill 规范（v2.0），对齐 OpenCode/ClawHub 社区：

| 项目 | 说明 |
|------|------|
| 规范文档 | [docs/skill-format.md](./docs/skill-format.md) |
| 规范主本 | [skills/00-SKILL-SPEC.md](./skills/00-SKILL-SPEC.md) |
| 参考规范 | [.xavier/skills/00-SKILL-SPEC.md](../.xavier/skills/00-SKILL-SPEC.md) |

**v2.0 核心变更**：
- `triggers`（复数，对齐社区）
- `metadata.version`（版本放入 metadata 块）
- `license`（社区标准字段）
- 保留 `children`/`parent`（xavier 扩展）

详见：[SKILL.md 编写规范](./docs/skill-format.md)

---

## 开发规范

- **dev/** 目录不提交 Git
- Skill 目录名必须为英文 kebab-case
- SKILL.md 必须包含 YAML frontmatter
- 参考 [.xavier](../.xavier/) 项目结构

---

## SKILL.md 格式要求（v2.0）

```yaml
---
name: skill-name                  # ★ 必需：英文 kebab-case
description: 简短描述              # ★ 必需：一句话说明
license: MIT                      # 推荐：许可证
triggers:                         # ★ 必需：触发词数组（复数）
  - "触发词1"
  - "触发词2"
metadata:
  version: "1.0.0"               # 版本（SemVer）
  category: dev                   # 分类
children: []                      # 父 Skill 填写（xavier 扩展）
parent: parent-skill              # 子 Skill 填写（xavier 扩展）
---
```

---

*最后更新：2026-04-27 | 规范版本：v2.0*
