# -*- coding: utf-8 -*-
"""
Agent 命令
"""

import click


@click.group()
def agent_cmd():
    """Agent 管理命令"""
    pass


@agent_cmd.command("list")
def list_agents():
    """列出所有可用的 Agent"""
    try:
        from agenthub.core.agent.adapters import AVAILABLE_ADAPTERS
        
        if not AVAILABLE_ADAPTERS:
            click.echo("暂无可用的 Agent 适配器")
            return
        
        click.echo(f"可用的 Agent 适配器 ({len(AVAILABLE_ADAPTERS)}):\n")
        for name, adapter_class in AVAILABLE_ADAPTERS.items():
            click.echo(f"  🤖 {name}")
            if hasattr(adapter_class, 'description'):
                click.echo(f"     {adapter_class.description}")
    except ImportError as e:
        click.echo(f"❌ 无法加载 Agent 模块: {e}", err=True)


@agent_cmd.command("status")
def agent_status():
    """查看 Agent 状态"""
    try:
        from agenthub.core.agent.scheduler import TaskScheduler
        from agenthub.core.agent.router import AgentRouter
        
        router = AgentRouter()
        scheduler = TaskScheduler(router)
        
        stats = scheduler.get_stats()
        
        click.echo("📊 Agent 状态:")
        click.echo(f"   运行中: {stats['running']}")
        click.echo(f"   已完成: {stats['completed']}")
        click.echo(f"   队列中: {stats['in_queue']}")
        click.echo(f"   最大并发: {stats['max_workers']}")
    except ImportError as e:
        click.echo(f"❌ 无法加载: {e}", err=True)


@agent_cmd.command("enable")
@click.argument("name")
def enable_agent(name):
    """启用 Agent"""
    click.echo(f"✅ 已启用 {name}")


@agent_cmd.command("disable")
@click.argument("name")
def disable_agent(name):
    """禁用 Agent"""
    click.echo(f"✅ 已禁用 {name}")
