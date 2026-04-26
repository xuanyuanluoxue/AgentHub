# -*- coding: utf-8 -*-
"""
Registry 命令
"""

import click


@click.group()
def registry_cmd():
    """注册表管理命令"""
    pass


@registry_cmd.command("info")
def registry_info():
    """查看注册表信息"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    stats = registry.get_stats()
    
    click.echo("📋 Skill 注册表信息:")
    click.echo(f"   总数: {stats['total']}")
    click.echo(f"   最后更新: {stats['last_updated'] or '从未更新'}")


@registry_cmd.command("rebuild")
def rebuild_registry():
    """重建注册表"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    result = registry.rebuild()
    
    click.echo("🔧 重建注册表:")
    click.echo(f"   新增: {result['added']}")
    if result['errors']:
        click.echo(f"   错误数: {len(result['errors'])}")
        for err in result['errors']:
            click.echo(f"      - {err}")
    else:
        click.echo("   ✅ 无错误")


@registry_cmd.command("repair")
def repair_registry():
    """修复注册表"""
    from agenthub.core.skill.registry import SkillRegistry
    
    registry = SkillRegistry()
    registry.reload()
    
    click.echo("✅ 注册表已重新加载")


@registry_cmd.command("clear")
def clear_registry():
    """清空注册表"""
    from agenthub.core.skill.registry import SkillRegistry
    
    if click.confirm("确定要清空注册表吗？这将移除所有已安装的 Skill"):
        registry = SkillRegistry()
        # 清空 skills 目录
        import shutil
        skills_dir = registry.skills_dir
        if skills_dir.exists():
            shutil.rmtree(skills_dir)
            skills_dir.mkdir()
        
        # 重建空注册表
        registry.reload()
        click.echo("✅ 注册表已清空")
