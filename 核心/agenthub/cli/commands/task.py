# -*- coding: utf-8 -*-
"""
Task 命令
"""

import click
from datetime import datetime


@click.group()
def task_cmd():
    """任务管理命令"""
    pass


@task_cmd.command("list")
@click.option("--status", type=click.Choice(["pending", "running", "completed", "failed"]), help="按状态筛选")
def list_tasks(status):
    """列出任务"""
    from agenthub.core.agent.models import TaskStatus
    
    # 模拟数据
    tasks = [
        {"id": "task-001", "name": "代码审查", "status": "completed", "agent": "claude"},
        {"id": "task-002", "name": "安装依赖", "status": "running", "agent": "opencode"},
        {"id": "task-003", "name": "生成文档", "status": "pending", "agent": None},
    ]
    
    if status:
        status_map = {"pending": "pending", "running": "running", "completed": "completed", "failed": "failed"}
        tasks = [t for t in tasks if t["status"] == status_map.get(status)]
    
    if not tasks:
        click.echo("没有任务")
        return
    
    click.echo(f"任务列表 ({len(tasks)}):\n")
    for task in tasks:
        status_icon = {"pending": "⏳", "running": "🔄", "completed": "✅", "failed": "❌"}.get(task["status"], "❓")
        agent = task["agent"] or "待分配"
        click.echo(f"  {status_icon} {task['id']} | {task['name']} | {agent}")


@task_cmd.command("submit")
@click.argument("prompt")
@click.option("--agent", "-a", help="指定 Agent")
@click.option("--priority", "-p", type=click.Choice(["low", "normal", "high", "urgent"]), default="normal")
def submit_task(prompt, agent, priority):
    """提交新任务"""
    from agenthub.core.agent.models import Task, TaskPriority
    
    priority_map = {
        "low": TaskPriority.LOW,
        "normal": TaskPriority.NORMAL,
        "high": TaskPriority.HIGH,
        "urgent": TaskPriority.URGENT,
    }
    
    task = Task(
        prompt=prompt,
        agent_preference=agent,
        priority=priority_map[priority],
    )
    
    click.echo(f"✅ 任务已提交")
    click.echo(f"   ID: {task.id}")
    click.echo(f"   描述: {task.prompt}")
    click.echo(f"   优先级: {priority}")


@task_cmd.command("cancel")
@click.argument("task_id")
def cancel_task(task_id):
    """取消任务"""
    click.echo(f"✅ 已取消任务 {task_id}")


@task_cmd.command("result")
@click.argument("task_id")
def task_result(task_id):
    """查看任务结果"""
    # 模拟数据
    results = {
        "task-001": {
            "success": True,
            "result": "代码审查完成，发现 3 个问题",
            "duration": "12.5s",
        }
    }
    
    if task_id not in results:
        click.echo(f"❌ 未找到任务: {task_id}", err=True)
        return
    
    r = results[task_id]
    status = "✅ 成功" if r["success"] else "❌ 失败"
    click.echo(f"任务: {task_id}")
    click.echo(f"状态: {status}")
    click.echo(f"结果: {r['result']}")
    click.echo(f"耗时: {r['duration']}")
