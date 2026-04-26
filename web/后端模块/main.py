# -*- coding: utf-8 -*-
"""
AgentHub Web API - FastAPI 后端
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
# main.py 在 web/后端模块/main.py
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "核心"))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any

# 尝试导入核心模块
try:
    from agenthub.core.skill.registry import SkillRegistry
    from agenthub.core.database import DatabaseManager
    from agenthub.core.agent.models import Task, TaskPriority, TaskStatus
    HAS_CORE = True
except ImportError:
    HAS_CORE = False

# ===== Pydantic Models =====

class TaskCreate(BaseModel):
    prompt: str
    name: Optional[str] = None
    agent_preference: Optional[str] = None
    priority: str = "normal"

class SkillInstall(BaseModel):
    path: str

class SkillSearch(BaseModel):
    query: str

class SettingsUpdate(BaseModel):
    skills_dir: Optional[str] = None
    max_concurrent: Optional[int] = None
    log_level: Optional[str] = None

# ===== FastAPI App =====

app = FastAPI(
    title="AgentHub API",
    description="AI 工具管理平台 REST API",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
db: Optional[DatabaseManager] = None
registry: Optional[SkillRegistry] = None

@app.on_event("startup")
async def startup():
    global db, registry
    if HAS_CORE:
        db = DatabaseManager()
        registry = SkillRegistry()

@app.on_event("shutdown")
async def shutdown():
    if db:
        db.close()

# ===== 辅助函数 =====

def success_response(data: Any, message: str = "成功"):
    return {"success": True, "message": message, "data": data}

def error_response(message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "data": None},
    )

# ===== 路由 =====

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "AgentHub API",
        "version": "0.1.0",
        "status": "running" if HAS_CORE else "limited",
    }

@app.get("/api/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "core_available": HAS_CORE,
        "database_connected": db is not None,
        "timestamp": datetime.now().isoformat(),
    }

# ===== Dashboard =====

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """获取仪表盘统计"""
    if not HAS_CORE or not db:
        # 返回模拟数据
        return success_response({
            "total_skills": 48,
            "total_agents": 4,
            "active_tasks": 2,
            "completed_tasks": 156,
            "recent_activities": [
                {"type": "task", "message": "代码审查完成", "agent": "claude", "time": "2分钟前"},
                {"type": "install", "message": "安装 github-pr skill", "agent": None, "time": "5分钟前"},
                {"type": "task", "message": "PR #42 已合并", "agent": "opencode", "time": "10分钟前"},
            ],
        })
    
    stats = db.get_stats()
    return success_response({
        "total_skills": stats["skills"]["total"],
        "total_agents": 4,  # 固定 4 个内置 Agent
        "active_tasks": stats["tasks"]["running"] + stats["tasks"]["pending"],
        "completed_tasks": stats["tasks"]["completed"],
        "recent_activities": _get_recent_activities(),
    })

def _get_recent_activities():
    """获取最近活动"""
    if not db:
        return []
    
    activities = []
    history = db.get_execution_history(limit=5)
    for h in history:
        activities.append({
            "type": "task",
            "message": f"任务 {h['task_id']} {'成功' if h['success'] else '失败'}",
            "agent": h["agent_name"],
            "time": _format_time(h["started_at"]),
        })
    return activities

def _format_time(iso_time: str) -> str:
    """格式化时间"""
    try:
        dt = datetime.fromisoformat(iso_time)
        delta = datetime.now() - dt
        if delta.total_seconds() < 60:
            return "刚刚"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)}分钟前"
        elif delta.total_seconds() < 86400:
            return f"{int(delta.total_seconds() / 3600)}小时前"
        else:
            return f"{int(delta.total_seconds() / 86400)}天前"
    except:
        return iso_time

# ===== Skills =====

@app.get("/api/skills")
async def list_skills():
    """列出所有 Skills"""
    if not HAS_CORE or not registry:
        return success_response([])
    
    skills = registry.list_all()
    return success_response([
        {
            "name": s.name,
            "version": s.version,
            "description": s.description,
            "author": s.author,
            "tags": s.tags,
            "triggers": s.triggers,
            "dependencies": s.dependencies,
        }
        for s in skills
    ])

@app.post("/api/skills/search")
async def search_skills(body: SkillSearch):
    """搜索 Skills"""
    if not HAS_CORE or not registry:
        return success_response([])
    
    results = registry.search(body.query)
    return success_response([
        {
            "name": s.name,
            "version": s.version,
            "description": s.description,
            "tags": s.tags,
        }
        for s in results
    ])

@app.get("/api/skills/{name}")
async def get_skill(name: str):
    """获取 Skill 详情"""
    if not HAS_CORE or not registry:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill = registry.get(name)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return success_response({
        "name": skill.name,
        "version": skill.version,
        "description": skill.description,
        "author": skill.author,
        "tags": skill.tags,
        "triggers": skill.triggers,
        "dependencies": skill.dependencies,
    })

@app.post("/api/skills/install")
async def install_skill(body: SkillInstall):
    """安装 Skill"""
    if not HAS_CORE or not registry:
        raise HTTPException(status_code=503, detail="Core module not available")
    
    try:
        info = registry.register(body.path)
        # 保存到数据库
        if db:
            db.save_skill(info.name, {
                "version": info.version,
                "path": info.path,
                "installed_at": info.installed_at,
                "source": info.source,
            })
        return success_response({
            "name": info.name,
            "version": info.version,
            "path": info.path,
        }, "安装成功")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/skills/{name}")
async def uninstall_skill(name: str):
    """卸载 Skill"""
    if not HAS_CORE or not registry:
        raise HTTPException(status_code=503, detail="Core module not available")
    
    if registry.unregister(name):
        if db:
            db.delete_skill(name)
        return success_response(None, "卸载成功")
    raise HTTPException(status_code=404, detail="Skill not found")

# ===== Agents =====

@app.get("/api/agents")
async def list_agents():
    """列出所有 Agents"""
    # 固定的 4 个内置 Agent
    agents = [
        {
            "name": "claude",
            "display_name": "Claude",
            "description": "Anthropic Claude 模型，适合复杂推理和代码审查",
            "status": "available",
            "capabilities": ["code_review", "reasoning", "writing"],
        },
        {
            "name": "opencode",
            "display_name": "OpenCode",
            "description": "OpenAI Codex 模型，适合代码生成和补全",
            "status": "available",
            "capabilities": ["code_generation", "completion", "refactoring"],
        },
        {
            "name": "codex",
            "display_name": "Codex",
            "description": "GitHub Codex 模型，适合 GitHub 集成任务",
            "status": "available",
            "capabilities": ["github_actions", "pr_review", "issue_management"],
        },
        {
            "name": "codefy",
            "display_name": "Codefy",
            "description": "通义灵码，适合国内生态集成",
            "status": "available",
            "capabilities": ["alibaba_cloud", "dingtalk", "acos"],
        },
    ]
    return success_response(agents)

@app.get("/api/agents/{name}/status")
async def get_agent_status(name: str):
    """获取 Agent 状态"""
    return success_response({
        "name": name,
        "status": "available",
        "current_task": None,
        "tasks_completed": 0,
        "avg_duration": 0,
    })

# ===== Tasks =====

@app.get("/api/tasks")
async def list_tasks(
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
):
    """列出任务"""
    if not HAS_CORE or not db:
        # 返回模拟数据
        tasks = [
            {"id": "task-001", "name": "代码审查", "prompt": "审查 PR #42", "status": "completed", "agent": "claude", "created_at": "2026-04-26T10:00:00"},
            {"id": "task-002", "name": "安装依赖", "prompt": "运行 npm install", "status": "running", "agent": "opencode", "created_at": "2026-04-26T10:05:00"},
            {"id": "task-003", "name": "生成文档", "prompt": "生成 API 文档", "status": "pending", "agent": None, "created_at": "2026-04-26T10:10:00"},
        ]
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return success_response(tasks[offset:offset+limit])
    
    tasks = db.list_tasks(status=status, limit=limit, offset=offset)
    return success_response(tasks)

@app.post("/api/tasks")
async def create_task(body: TaskCreate):
    """创建任务"""
    if not HAS_CORE or not db:
        task_id = f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return success_response({
            "id": task_id,
            "prompt": body.prompt,
            "name": body.name or body.prompt[:30],
            "status": "pending",
        }, "任务已创建")
    
    priority_map = {
        "low": TaskPriority.LOW,
        "normal": TaskPriority.NORMAL,
        "high": TaskPriority.HIGH,
        "urgent": TaskPriority.URGENT,
    }
    
    task = Task(
        name=body.name or body.prompt[:50],
        prompt=body.prompt,
        agent_preference=body.agent_preference,
        priority=priority_map.get(body.priority, TaskPriority.NORMAL),
    )
    
    db.save_task(task)
    
    return success_response({
        "id": task.id,
        "name": task.name,
        "prompt": task.prompt,
        "status": task.status.value,
        "priority": task.priority.value,
    }, "任务已创建")

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    if not HAS_CORE or not db:
        return success_response({
            "id": task_id,
            "name": "任务",
            "prompt": "任务描述",
            "status": "pending",
        })
    
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return success_response(task)

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    if not HAS_CORE or not db:
        return success_response(None, "任务已删除")
    
    if db.delete_task(task_id):
        return success_response(None, "任务已删除")
    raise HTTPException(status_code=404, detail="Task not found")

# ===== Tools =====

@app.get("/api/tools")
async def list_tools():
    """列出所有可用工具"""
    tools = [
        {"name": "filesystem", "description": "文件系统操作", "status": "available"},
        {"name": "terminal", "description": "终端命令执行", "status": "available"},
        {"name": "browser", "description": "浏览器自动化", "status": "available"},
        {"name": "github", "description": "GitHub API 操作", "status": "available"},
        {"name": "database", "description": "数据库操作", "status": "available"},
        {"name": "websearch", "description": "网络搜索", "status": "available"},
    ]
    return success_response(tools)

# ===== Settings =====

@app.get("/api/settings")
async def get_settings():
    """获取设置"""
    return success_response({
        "skills_dir": str(Path.home() / ".agenthub" / "skills"),
        "max_concurrent": 4,
        "log_level": "INFO",
        "theme": "dark",
        "language": "zh-CN",
    })

@app.put("/api/settings")
async def update_settings(body: SettingsUpdate):
    """更新设置"""
    return success_response(body.dict(exclude_none=True), "设置已更新")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5173)
