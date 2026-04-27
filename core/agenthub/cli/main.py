# -*- coding: utf-8 -*-
"""
AgentHub CLI - 命令行入口
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
# cli/main.py 在 core/agenthub/cli/main.py
# 项目根目录需要 parent.parent.parent.parent
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "core"))

import click
from typing import Optional

from agenthub.cli.commands import skill_cmd, agent_cmd, task_cmd, registry_cmd, clawhub


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
@click.option("--template", "-t", is_flag=True, help="使用模板初始化（跳过交互）")
@click.option("--force", "-f", is_flag=True, help="强制重新初始化")
@click.option("--name", "-n", default=None, help="设置你的名称")
def init(template, force, name):
    """
    初始化 AgentHub - 在 ~/.agenthub 创建配置目录

    示例:
      agenthub init              # 交互式初始化
      agenthub init --template   # 使用默认模板快速初始化
      agenthub init --force     # 强制重新初始化
    """
    config_dir = Path.home() / ".agenthub"
    profile_dir = config_dir / "profile"
    agents_dir = config_dir / "agents"

    if config_dir.exists() and not force:
        click.echo(f"✅ AgentHub 已初始化 ({config_dir})")
        click.echo(f"   运行 `agenthub init --force` 强制重新初始化")
        return

    click.echo("🚀 AgentHub 初始化向导")
    click.echo("=" * 50)

    if template:
        user_name = "用户"
    else:
        if name:
            user_name = name
        else:
            user_name = click.prompt("请输入你的名称", default="用户")

    click.echo(f"\n📁 创建配置目录: {config_dir}")

    dirs = [
        "skills",
        "agents",
        "profile",
        "projects",
        "docs",
        "secrets",
        "data",
        "backup",
        "logs",
    ]

    for d in dirs:
        (config_dir / d).mkdir(parents=True, exist_ok=True)
        click.echo(f"   📁 {d}/")

    click.echo("\n📝 创建配置文件...")

    config_file = config_dir / "config.yaml"
    config_file.write_text(f"""name: AgentHub
version: "0.1.0"
description: AI 工具管理平台中央控制中心
configPath: ~/.agenthub
sharedSkillsPath: ~/shared-skills
theme: dark
language: zh-CN
autoSync: true
userName: {user_name}
tools:
  - opencode
  - openclaw
  - claude
  - codebuddy
  - cursor
  - hermes
skills: []
agents: []
""")
    click.echo("   📄 config.yaml")

    profile_identity = profile_dir / "identity.yaml"
    profile_identity.write_text(f"""---
name: {user_name}
alias:
  - "{user_name}"

basic:
  gender: 男/女
  birth: 2000-01-01
  age: 25
  phone: 138xxxxxxx
  email: user@example.com
  location: 城市
  native_language: 普通话

contact:
  phone: 138xxxxxxx
  email: user@example.com
  qq: 123456
  wechat: wechat_id

online:
  blog: https://example.com
  github: https://github.com/username

school:
  name: 学校名称
  college: 学院
  major: 专业
  class: 班级
  student_id: 学号
  duration: 2020.9 - 2024.7

tech_stack:
  python: ⭐⭐⭐⭐ 熟练
  javascript: ⭐⭐⭐ 中级

personality:
  traits:
    - 特质1
    - 特质2
  communication_style: 直接
  mbti: INFP

preferences:
  aesthetic:
    primary_color: "#c45d2c"
    secondary_color: "#e8a838"
  response_style:
    emoji: true
    language: zh-CN

ai_assistant:
  name: 小X
  style: 温暖/专业/朋友风格
  emoji: 🌸
  taboo: "不做过度的寒暄"

updated: {datetime.now().strftime('%Y-%m-%d')}
""")
    click.echo("   📄 profile/identity.yaml")

    profile_readme = profile_dir / "README.md"
    profile_readme.write_text(f"""# 用户画像

> {user_name} 的个人配置目录

## 目录

- `identity.yaml` - 身份信息
- `skills.md` - 技能图谱
- `projects.md` - 项目经验
- `contacts/` - 联系人
- `health/` - 健康记录
- `growth/` - 成长轨迹

## 使用说明

1. 编辑 `identity.yaml` 填入你的真实信息
2. 根据需要编辑其他文件
3. 运行 `agenthub profile validate` 验证配置
""")
    click.echo("   📄 profile/README.md")

    agents_readme = agents_dir / "README.md"
    agents_readme.write_text("""# Agent 配置

本目录存放 Agent 配置文件。

## 使用说明

1. 编辑 Agent 配置文件
2. 运行 `agenthub agent reload` 重新加载

## 内置 Agent

- main-agent - 主路由入口
- dev-agent - 开发任务
- life-agent - 生活服务
- ops-agent - 运营任务
- productivity-agent - 效率工具
""")
    click.echo("   📄 agents/README.md")

    readme = config_dir / "README.md"
    readme.write_text("""# AgentHub 配置文件夹

> AI 工具管理平台的默认配置目录

## 目录结构

```
.agenthub/
├── config.yaml      # 主配置文件
├── skills/          # 已安装的 Skills
├── agents/          # Agent 配置文件
├── profile/         # 用户画像
├── projects/       # 项目管理
├── docs/            # 文档
├── secrets/         # 敏感配置
├── data/            # 数据存储
├── backup/          # 备份文件
└── logs/            # 运行日志
```

## 快速命令

```bash
agenthub --help           # 查看帮助
agenthub skill list       # 查看 Skills
agenthub agent list       # 查看 Agents
agenthub profile validate # 验证配置
```

## 版本

v0.2.0
""")
    click.echo("   📄 README.md")

    click.echo("\n" + "=" * 50)
    click.echo(f"✅ AgentHub 初始化完成！")
    click.echo(f"")
    click.echo(f"   📁 配置目录: {config_dir}")
    click.echo(f"   👤 用户名称: {user_name}")
    click.echo(f"")
    click.echo(f"   下一步:")
    click.echo(f"   1. 编辑 ~/.agenthub/profile/identity.yaml 填入你的信息")
    click.echo(f"   2. 运行 `agenthub skill list` 查看 Skills")
    click.echo(f"   3. 运行 `agenthub agent list` 查看 Agents")


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


@cli.command()
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.option("--list", "-l", is_flag=True, help="列出所有配置")
@click.option("--save", is_flag=True, help="保存配置到文件")
def config(key, value, list, save):
    """查看和修改配置"""
    from agenthub.core.config import get_config, load_config

    cfg = get_config()

    if list:
        import yaml
        click.echo(yaml.dump(cfg.data, allow_unicode=True, default_flow_style=False))
        return

    if save:
        cfg.save()
        click.echo(f"✅ 配置已保存到 {cfg.config_path}")
        return

    if key and value:
        cfg.set(key, value)
        click.echo(f"✅ 已设置 {key} = {value}")
        click.echo("   运行 `agenthub config --save` 保存到文件")
        return

    if key:
        val = cfg.get(key)
        if val is not None:
            click.echo(f"{key} = {val}")
        else:
            click.echo(f"❌ 未找到配置: {key}", err=True)
        return

    click.echo("用法:")
    click.echo("  agenthub config                    # 显示所有配置")
    click.echo("  agenthub config --list             # 列出所有配置")
    click.echo("  agenthub config <key>              # 查看配置值")
    click.echo("  agenthub config <key> <value>     # 设置配置值")
    click.echo("  agenthub config --save             # 保存配置到文件")


# 注册子命令
cli.add_command(skill_cmd, name="skill")
cli.add_command(agent_cmd, name="agent")
cli.add_command(task_cmd, name="task")
cli.add_command(registry_cmd, name="registry")
cli.add_command(clawhub, name="clawhub")


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
