# -*- coding: utf-8 -*-
"""
Skill 命令
"""

import click


@click.group()
def skill_cmd():
    """Skill 管理命令"""
    pass


@skill_cmd.command("list")
def list_skills():
    """列出所有已安装的 Skills"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    skills = registry.list_all()
    
    if not skills:
        click.echo("尚未安装任何 Skill")
        return
    
    for skill in skills:
        click.echo(f"📦 {skill.name} (v{skill.version})")


@skill_cmd.command("install")
@click.argument("path")
def install_skill(path):
    """安装 Skill"""
    from agenthub.core.skill.registry import SkillRegistry, RegistryError
    
    registry = SkillRegistry()
    try:
        info = registry.register(path)
        click.echo(f"✅ 已安装 {info.name}")
    except RegistryError as e:
        click.echo(f"❌ 安装失败: {e}", err=True)


@skill_cmd.command("uninstall")
@click.argument("name")
def uninstall_skill(name):
    """卸载 Skill"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    if registry.unregister(name):
        click.echo(f"✅ 已卸载 {name}")
    else:
        click.echo(f"❌ 未找到 {name}", err=True)


@skill_cmd.command("info")
@click.argument("name")
def skill_info(name):
    """查看 Skill 详情"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    skill = registry.get(name)
    
    if not skill:
        click.echo(f"❌ 未找到 {name}", err=True)
        return
    
    click.echo(f"📦 {skill.name}")
    click.echo(f"版本: {skill.version}")
    click.echo(f"描述: {skill.description}")
    if skill.triggers:
        click.echo(f"触发词: {', '.join(skill.triggers)}")


@skill_cmd.command("search")
@click.argument("query")
def search_skill(query):
    """搜索 Skill"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    results = registry.search(query)
    
    if not results:
        click.echo(f"未找到: {query}")
        return
    
    for skill in results:
        click.echo(f"📦 {skill.name} - {skill.description}")


@skill_cmd.command("rebuild")
def rebuild_skill():
    """重建注册表"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    result = registry.rebuild()
    
    click.echo(f"✅ 重建完成")
    click.echo(f"   新增: {result['added']}")
    if result['errors']:
        click.echo(f"   错误: {len(result['errors'])}")
        for err in result['errors']:
            click.echo(f"      - {err}")
