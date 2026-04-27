---
name: github-cli
version: 1.0.0
description: GitHub CLI 工具集，使用 gh 命令与 GitHub 交互，管理仓库、Issue、PR、Actions 等
author: AgentHub Team
tags:
  - github
  - cli
  - git
  - pull-request
  - issue
  - actions
  - repository
category: devops
triggers:
  - "github"
  - "推送"
  - "提交"
  - "pr"
  - "issue"
  - "pull request"
  - "仓库"
platform: all
license: MIT
dependencies: []
---

# GitHub CLI 技能

使用 `gh` 命令与 GitHub 无缝交互，支持仓库管理、Issue、PR、Actions 等操作。

## 安装 gh CLI

### Windows (winget)
```bash
winget install GitHub.cli
```

### macOS
```bash
brew install gh
```

### Linux (Ubuntu/Debian)
```bash
sudo apt install gh
```

### 验证安装
```bash
gh --version
```

## 认证登录

```bash
gh auth login
```

## 核心命令

### 仓库操作

| 命令 | 说明 |
|------|------|
| `gh repo clone <owner>/<repo>` | 克隆仓库 |
| `gh repo create <name>` | 创建新仓库 |
| `gh repo fork <owner>/<repo>` | Fork 仓库 |
| `gh repo view` | 查看当前仓库信息 |
| `gh repo list <user>` | 列出用户仓库 |

### 推送文件

```bash
# 添加文件到暂存区
git add .

# 提交
git commit -m "提交信息"

# 推送
git push -u origin <branch-name>

# 或使用 gh 命令推送 PR
gh pr create --title "PR 标题" --body "PR 描述"
```

### Issue 管理

```bash
# 列出 Issue
gh issue list

# 查看 Issue
gh issue view <issue-number>

# 创建 Issue
gh issue create --title "标题" --body "内容"

# 关闭 Issue
gh issue close <issue-number>
```

### Pull Request

```bash
# 列出 PR
gh pr list

# 查看 PR
gh pr view <pr-number>

# 创建 PR
gh pr create --title "标题" --body "描述" --base main

# 合并 PR
gh pr merge <pr-number>

# 审查 PR
gh pr review <pr-number> --approve
```

### Actions 工作流

```bash
# 列出工作流
gh run list

# 查看运行状态
gh run view <run-id>

# 触发工作流
gh workflow run <workflow-name>

# 下载工作流产物
gh run download <run-id>
```

### API 操作

```bash
# GET 请求
gh api repos/<owner>/<repo>

# 使用 jq 处理 JSON
gh api repos/<owner>/<repo> --jq '.description'

# POST 请求
gh api --method POST repos/<owner>/<repo>/issues --field title="标题"
```

## 常用场景

### 场景 1: 推送本地代码到 GitHub

```bash
# 1. 创建本地仓库
git init
git add .
git commit -m "Initial commit"

# 2. 创建远程仓库
gh repo create my-project --public --source=. --push

# 或先创建仓库，再关联
gh repo create my-project --public
git remote add origin https://github.com/<user>/my-project.git
git push -u origin main
```

### 场景 2: 同步 Fork 仓库

```bash
# 添加上游仓库
git remote add upstream https://github.com/<original>/repo.git

# 获取上游更新
git fetch upstream

# 合并到本地分支
git merge upstream/main

# 推送更新
git push origin main
```

### 场景 3: 创建 PR 并请求审查

```bash
# 1. 创建新分支
git checkout -b feature/new-feature

# 2. 修改代码并提交
git add .
git commit -m "feat: add new feature"

# 3. 推送到远程
git push -u origin feature/new-feature

# 4. 创建 PR
gh pr create --title "feat: add new feature" \
  --body "## Summary\n- 新增功能\n- 修复 Bug" \
  --reviewer @me \
  --base main
```

### 场景 4: 管理 GitHub Actions

```bash
# 查看失败的工作流
gh run list --status failed

# 查看失败原因
gh run view <run-id> --log

# 重新运行失败的 Job
gh run rerun <run-id>
```

## 快捷命令参考

```bash
# 速查表
gh repo                              # 查看当前仓库
gh issue list --state open          # 查看打开的 Issue
gh pr list --state open            # 查看打开的 PR
gh run list --limit 10             # 查看最近 10 个运行
gh api /user                        # 查看当前用户信息

# 常用标志
--json <fields>                     # JSON 输出
--jq <expression>                   # jq 过滤
--limit <number>                    # 限制数量
--state (open|closed|all)          # 状态过滤
--sort (created|updated|comments)  # 排序方式
--direction (asc|desc)             # 排序方向
```

## 权限要求

使用 gh CLI 前需要：
1. 安装 gh CLI
2. 执行 `gh auth login` 进行认证
3. 确保有仓库的访问权限

## 参考链接

- [GitHub CLI 官方文档](https://cli.github.com/manual/)
- [gh api 文档](https://cli.github.com/manual/gh_api)
