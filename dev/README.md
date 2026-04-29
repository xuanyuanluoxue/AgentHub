# AgentHub 开发文档

> 本目录为开发专用，不提交 Git。
>
> **版本**: v1.0 | 更新: 2026-04-29

---

## 项目定位

**AgentHub** 是跨平台 AI 工具管理平台的**公共开源模板**，用于统一 Skill · Agent · 用户画像 · 记忆系统四大共享生态。

| 组件 | 技术 |
|------|------|
| 语言 | Python >= 3.10 |
| CLI | Click |
| 配置 | PyYAML |
| 版本 | SemVer |

---

## 目录结构

```
dev/
├── README.md              ← 开发文档索引
├── SPEC.md               ← 项目规格
├── PROGRESS.md           ← 开发进度
├── TROUBLESHOOTING.md    ← 问题排查
│
└── apps/                  ← 应用示例
    └── tool-detector/     ← AI 工具检测器
```

> 安装脚本已移至 `misc/` 目录
dev/
├── README.md              ← 开发文档索引
├── SPEC.md               ← 项目规格
├── PROGRESS.md           ← 开发进度
├── TROUBLESHOOTING.md    ← 问题排查
│
├── install.sh             ← 一键安装脚本（Linux/macOS）
│
├── apps/                  ← 应用示例
│   └── tool-detector/     ← AI 工具检测器
│
└── scripts/               ← 平台安装脚本
    ├── linux/
    ├── macos/
    └── windows/
```

---

## 核心文档

| 文档 | 说明 |
|------|------|
| [SPEC.md](./SPEC.md) | 项目规格 — 功能定义和技术决策 |
| [PROGRESS.md](./PROGRESS.md) | 开发进度 |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | 问题排查 |

---

## 快速开始

```bash
# 安装依赖
pip install -e .

# 运行 CLI
agenthub --help

# 初始化
agenthub init
```

---

## 开发注意事项

1. **dev/ 目录不提交 Git**（已加入 .gitignore）
2. **secrets/ 目录不提交 Git**（已加入 .gitignore）
3. **隐私检查**：所有公共文档不得包含私人信息
4. **路径规范**：使用 `~/.agenthub/` 等通用路径

---

*最后更新：2026-04-29*