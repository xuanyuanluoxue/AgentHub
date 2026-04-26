# -*- coding: utf-8 -*-
"""
AgentHub CLI - 命令行入口
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
# cli/main.py 在 核心/agenthub/cli/main.py
# 项目根目录需要 parent.parent.parent.parent
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "核心"))

import click
from typing import Optional

from agenthub.cli.commands import skill_cmd, agent_cmd, task_cmd, registry_cmd


@click.group()
@click.version_option(version="0.1.0", prog_name="agenthub")
@click.pass_context
def cli(ctx):
    """🤖 AgentHub - AI 工具管理平台"""
    ctx.ensure_object(dict)
    
    # 检查是否初始化
    config_dir = Path.home() / ".agenthub"
    if not config_dir.exists():
        click.echo("⚠️  AgentHub 未初始化，运行 `agenthub init` 进行初始化")


@cli.command()
def init():
    """初始化 AgentHub - 在用户文件夹创建配置目录"""
    config_dir = Path.home() / ".agenthub"
    
    if config_dir.exists():
        click.echo(f"✅ AgentHub 已初始化 ({config_dir})")
        return
    
    click.echo("🚀 开始初始化 AgentHub...")
    
    # 创建完整目录结构
    dirs = [
        "skills",       # 已安装的 Skills
        "agents",        # Agent 配置文件
        "profile",       # 用户画像
        "projects",      # 项目管理
        "docs",          # 文档
        "secrets",       # 敏感配置 (API密钥等)
        "data",          # 数据存储
        "backup",        # 备份文件
        "logs",          # 运行日志
    ]
    
    for d in dirs:
        (config_dir / d).mkdir(parents=True, exist_ok=True)
    
    # 创建配置文件 config.json
    config_file = config_dir / "config.json"
    config_file.write_text("""{
  "name": "AgentHub",
  "version": "0.1.0",
  "description": "AI 工具管理平台中央控制中心",
  "configPath": "~/.agenthub",
  "sharedSkillsPath": "D:\\\\Obsidian\\\\AI\\\\交接文档\\\\shared-skills",
  "theme": "dark",
  "language": "zh-CN",
  "autoSync": true,
  "tools": [
    "opencode",
    "openclaw",
    "claude",
    "codebuddy",
    "cursor",
    "hermes"
  ],
  "skills": [],
  "agents": []
}
""")
    
    # 创建 README
    readme = config_dir / "README.md"
    readme.write_text("""# AgentHub 配置文件夹

> AI 工具管理平台的默认配置目录

## 目录结构

```
.agenthub/
├── config.json      # 主配置文件
├── skills/          # 已安装的 Skills
├── agents/          # Agent 配置文件
├── profile/         # 用户画像
├── projects/        # 项目管理
├── docs/            # 文档
├── secrets/         # 敏感配置 (API密钥等)
├── data/            # 数据存储
├── backup/          # 备份文件
└── logs/            # 运行日志
```

## 公共资源

- **共享 Skills**: `D:\\Obsidian\\AI\\交接文档\\shared-skills\\` (26+ Skills)
- **用户画像**: `D:\\Obsidian\\AI\\交接文档\\个人画像\\`
- **项目文档**: `D:\\Obsidian\\AI\\小落\\`
- **博客草稿**: `D:\\Obsidian\\AI\\blog-drafts\\`

## 版本

v0.1.0 - 开发中
""")
    
    click.echo(f"✅ AgentHub 初始化完成！")
    click.echo(f"")
    click.echo(f"   📁 配置目录: {config_dir}")
    click.echo(f"")
    click.echo(f"   目录结构:")
    for d in dirs:
        click.echo(f"      📁 {d}/")
    click.echo(f"")
    click.echo(f"   📄 配置文件: config.json")
    click.echo(f"   📄 说明文档: README.md")
    click.echo(f"")
    click.echo(f"🌐 打开管理界面: D:\\code\\github\\agenthub\\web\\工具检测\\index.html")


@cli.command()
@click.argument("query", required=False)
def search(query):
    """搜索 Skills"""
    if not query:
        click.echo("请提供搜索关键词")
        return
    
    from agenthub.core.skill.registry import SkillRegistry
    registry = SkillRegistry()
    results = registry.search(query)
    
    if not results:
        click.echo(f"未找到匹配的 Skill: {query}")
        return
    
    click.echo(f"找到 {len(results)} 个匹配的 Skill:\n")
    for skill in results:
        click.echo(f"  📦 {skill.name}")
        click.echo(f"     版本: {skill.version}")
        click.echo(f"     {skill.description}")
        if skill.tags:
            click.echo(f"     标签: {', '.join(skill.tags)}")
        click.echo()


@cli.command()
def list():
    """列出所有 Skills"""
    from agenthub.core.skill.registry import SkillRegistry
    registry = SkillRegistry()
    skills = registry.list_all()
    
    if not skills:
        click.echo("尚未安装任何 Skill")
        click.echo("运行 `agenthub skill install <path>` 安装 Skill")
        return
    
    click.echo(f"已安装 {len(skills)} 个 Skill:\n")
    for skill in skills:
        status = "✅" if registry.exists(skill.name) else "❌"
        click.echo(f"  {status} {skill.name} (v{skill.version})")
        click.echo(f"      {skill.description}")
        click.echo()


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def install(path):
    """安装 Skill"""
    from agenthub.core.skill.registry import SkillRegistry, RegistryError
    
    registry = SkillRegistry()
    
    try:
        info = registry.register(path)
        click.echo(f"✅ Skill 安装成功!")
        click.echo(f"   名称: {info.name}")
        click.echo(f"   版本: {info.version}")
        click.echo(f"   路径: {info.path}")
    except RegistryError as e:
        click.echo(f"❌ 安装失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("name")
def uninstall(name):
    """卸载 Skill"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    
    if registry.unregister(name):
        click.echo(f"✅ {name} 已卸载")
    else:
        click.echo(f"❌ 未找到 Skill: {name}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("name")
def info(name):
    """查看 Skill 详情"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    skill = registry.get(name)
    
    if not skill:
        click.echo(f"❌ 未找到 Skill: {name}", err=True)
        sys.exit(1)
    
    click.echo(f"📦 {skill.name}")
    click.echo(f"   版本: {skill.version}")
    click.echo(f"   描述: {skill.description}")
    
    if skill.author:
        click.echo(f"   作者: {skill.author}")
    if skill.tags:
        click.echo(f"   标签: {', '.join(skill.tags)}")
    if skill.triggers:
        click.echo(f"   触发词: {', '.join(skill.triggers)}")
    if skill.dependencies:
        click.echo(f"   依赖: {', '.join(skill.dependencies)}")


# 注册子命令
cli.add_command(skill_cmd, name="skill")
cli.add_command(agent_cmd, name="agent")
cli.add_command(task_cmd, name="task")
cli.add_command(registry_cmd, name="registry")


def main():
    """主入口"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
