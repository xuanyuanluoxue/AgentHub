# Skill 规范文档 v1.1

> 最后更新：2026-04-27 | 规范版本：v2.0 | 对齐 OpenCode/ClawHub 社区

---

## 1. 概述

Skill 是 AI Agent 的核心扩展单元，每个 Skill 是一个**自包含的功能模块**。一个 Skill 可以包含多个子 Skill（父子结构），也可以包含脚本、模板、参考资料等辅助文件。

---

## 2. 目录结构

### 2.1 独立 Skill

```
skill-name/
├── SKILL.md                     # ★ 核心定义（必需）
├── README.md                    # 使用文档（可选）
├── scripts/                     # 执行脚本（可选）
├── references/                  # 参考资料（可选）
├── templates/                   # 模板文件（可选）
└── assets/                      # 资源文件（可选）
```

### 2.2 父 Skill（带子 Skill）

```
parent-skill/
├── SKILL.md                     # ★ 父 Skill 定义（必需）
├── child-skill-1/              # 子 Skill 1
│   └── SKILL.md
├── child-skill-2/              # 子 Skill 2
│   └── SKILL.md
└── shared/                      # 共享资源（可选）
```

### 2.3 命名规则

| 类型 | 规则 | 示例 |
|------|------|------|
| 目录名 | 英文 kebab-case | `browser-bridge` |
| SKILL.md | 全大写 | `SKILL.md` |
| 脚本 | 与语言一致 | `install.sh`, `build.py` |

**禁止使用中文目录名**。

---

## 3. SKILL.md 格式

### 3.1 YAML Frontmatter（必需）

```yaml
---
name: skill-name                  # ★ 必需：英文 kebab-case，唯一
version: 1.0.0                   # ★ 必需：SemVer 格式
description: 简短描述              # ★ 必需：一句话说明（<100字符）
trigger:                          # ★ 必需：触发词数组
  - "触发词1"
  - "触发词2"
category: dev|life|ops|system|productivity  # 分类
children:                         # 父 Skill 填写
  - child-skill-1
parent: parent-skill             # 子 Skill 填写
---
```

### 3.2 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | Skill 名称，英文 kebab-case，唯一 |
| `version` | string | SemVer 格式，如 `1.0.0` |
| `description` | string | 一句话简短描述（<100字符） |
| `trigger` | string[] | 触发词数组，AI 根据触发词决定加载哪个 Skill |

### 3.3 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `category` | enum | 分类：`dev`, `life`, `ops`, `system`, `productivity` |
| `children` | string[] | 子 Skill 名称列表（父 Skill 填写） |
| `parent` | string | 父 Skill 名称（子 Skill 填写） |
| `tags` | string[] | 标签数组，用于搜索 |
| `dependencies` | string[] | 依赖的其他 Skill（格式：`name@version`） |
| `tools` | string[] | 依赖的系统工具 |
| `platform` | enum | 支持平台：`windows`, `linux`, `macos`, `all` |
| `license` | string | 许可证 |
| `author` | string | 作者名 |

---

## 4. 父子 Skill 结构

### 4.1 设计原则

1. **聚合相关功能** — 多个相关 Skill 聚合为一个父 Skill
2. **统一触发路由** — 用户触发父 Skill 的触发词时，加载父 Skill
3. **子 Skill 可独立使用** — 子 Skill 也可以被独立触发
4. **共享资源放父目录** — 多个子 Skill 共用的脚本、模板放父目录

### 4.2 父 Skill

```yaml
---
name: android
description: Android 设备管理工具集
trigger:
  - "Android"
  - "adb"
version: 1.0.0
category: dev
children:
  - adb-contacts-read
  - adb-wireless-debug
---
```

### 4.3 子 Skill

```yaml
---
name: adb-contacts-read
description: 通过 ADB 读取手机联系人
trigger:
  - "联系人"
  - "通讯录"
version: 1.0.0
category: dev
parent: android
---
```

---

## 5. 分类规范

| 分类 | 说明 | 示例 |
|------|------|------|
| `dev` | 开发相关 | github, browser-bridge, dev-agent |
| `life` | 生活服务 | course-schedule, weather, life-agent |
| `ops` | 运营相关 | blog-manager, feishu-notify, ops-agent |
| `system` | 系统管理 | system-core, windows-powershell-bridge |
| `productivity` | 效率工具 | productivity-agent, humanizer |

---

## 6. 版本管理

使用 [SemVer](https://semver.org/) 格式：

| 版本 | 说明 |
|------|------|
| `1.0.0` | 正式版 |
| `0.1.0` | 开发版 |
| `1.0.0-beta.1` | 测试版 |

---

## 7. 编写 Checklist

创建或更新 Skill 时，检查以下项目：

### 格式检查
- [ ] SKILL.md 以 `---` YAML frontmatter 开头
- [ ] 包含 `name`, `version`, `description`, `trigger` 四个必需字段
- [ ] 目录名为英文 kebab-case（无中文）

### 内容检查
- [ ] 触发词准确（能准确触发且不与常用词冲突）
- [ ] 描述简洁（<100字符）
- [ ] 包含注意事项和常见问题

### 父子结构检查
- [ ] 父 Skill 包含 `children` 字段
- [ ] 子 Skill 包含 `parent` 字段

---

*本规范与 xavier skill-spec v1.1 保持一致*
