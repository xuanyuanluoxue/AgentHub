# AgentHub

> 统一 AI 工具的 Skill 生态，让开发者在不同 AI 工具间无缝切换。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 项目愿景

解决 OpenClaw、OpenCode、ClawHub 等各种 AI 工具的 **Skill 不统一问题**。

当前市面上的 AI 开发工具各自维护独立的 Skill 体系，导致 Skill 无法复用、重复开发、生态割裂。AgentHub 致力于构建**跨平台的统一 Skill 规范**，实现「一次编写，到处运行」。

[👉 了解更多](./docs/项目愿景.md)

---

## ✨ 核心特性

- **统一格式** — 所有支持的 AI 工具使用相同的 Skill 规范（v2.0）
- **跨平台兼容** — 一套 Skill，OpenClaw / OpenCode / ClawHub / Hermes 通用
- **共享技能库** — 集中管理，避免重复建设
- **社区共建** — 集体智慧，持续迭代

---

## 📁 目录结构

```
.agenthub/
├── .git/                    # Git 仓库
├── .gitignore               # 忽略规则（dev/ 不提交）
├── docs/
│   ├── 项目愿景.md          # ★ 项目愿景与背景
│   └── skill-format.md      # ★ Skill 规范文档 v2.0
├── skills/
│   ├── 00-SKILL-SPEC.md     # ★ Skill 规范（同步自 xavier）
│   ├── agent/               # Agent 记忆系统
│   └── hello-world/         # 示例 Skill
├── dev/                     # 开发文件（不提交 Git）
└── ...
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 创建第一个 Skill

参考 [docs/skill-format.md](./docs/skill-format.md) 创建你的 Skill。

---

## 📖 Skill 规范（v2.0）

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

详细规范：[docs/skill-format.md](./docs/skill-format.md)

---

## 🤝 支持的工具

| 工具 | 状态 |
|------|------|
| OpenClaw | ✅ 已支持 |
| OpenCode | ✅ 已支持 |
| ClawHub | ✅ 已支持 |
| Hermes Agent | ✅ 已支持 |
| 其他 | 🔄 规划中 |

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [项目愿景](./docs/项目愿景.md) | 项目背景、解决方案、核心价值 |
| [Skill 规范](./docs/skill-format.md) | v2.0 规范详解 |
| [开发指南](./docs/AI_DEVELOPER_GUIDE.md) | 开发者指南 |
| [快速参考](./docs/QUICK_REFERENCE.md) | 常用操作速查 |

---

## 📄 License

MIT License

---

*愿景驱动，代码落地。*
