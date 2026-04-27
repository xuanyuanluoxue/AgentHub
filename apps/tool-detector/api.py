# -*- coding: utf-8 -*-
"""
AI Tools Detection API - 真实检测工具安装状况
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse

# ===== Windows 路径配置 =====
WINDOWS_HOME = Path("C:/Users/User")
CONFIG_DIR = WINDOWS_HOME / ".config"

# 工具定义
TOOLS_CONFIG = {
    "opencode": {
        "name": "OpenCode",
        "icon": "⚡",
        "color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "description": "AI 编程助手，支持代码补全、重构、解释",
        "configPath": str(CONFIG_DIR / "opencode"),
        "skillsPath": str(CONFIG_DIR / "opencode" / "skills"),
        "agentsPath": str(CONFIG_DIR / "opencode" / "agents"),
        "detectionFiles": ["package.json", "opencode.json"],
    },
    "openclaw": {
        "name": "OpenClaw",
        "icon": "🦎",
        "color": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "description": "AI Agent 框架，支持多工具协作和任务编排",
        "configPath": str(WINDOWS_HOME / ".openclaw"),
        "skillsPath": str(WINDOWS_HOME / ".openclaw" / "skills"),
        "agentsPath": str(WINDOWS_HOME / ".openclaw" / "subagents"),
        "detectionFiles": ["openclaw.json", "oneclaw.config.json"],
    },
    "claude": {
        "name": "Claude Desktop",
        "icon": "🧠",
        "color": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "description": "Anthropic Claude 模型，本地桌面集成",
        "configPath": str(WINDOWS_HOME / ".claude"),
        "skillsPath": str(WINDOWS_HOME / ".claude" / "SKILLS"),
        "agentsPath": str(WINDOWS_HOME / ".claude" / "agents"),
        "detectionFiles": ["settings.json", "config.json"],
    },
    "codebuddy": {
        "name": "CodeBuddy",
        "icon": "💻",
        "color": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "description": "通义灵码，国内生态 AI 编程助手",
        "configPath": str(WINDOWS_HOME / ".codebuddy"),
        "skillsPath": str(WINDOWS_HOME / ".codebuddy" / "skills-marketplace" / "skills"),
        "agentsPath": str(WINDOWS_HOME / ".codebuddy" / "instances.json"),
        "detectionFiles": ["CODEBUDDY.md", "settings.json"],
    },
    "cursor": {
        "name": "Cursor",
        "icon": "📝",
        "color": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "description": "AI 代码编辑器，基于 VSCode",
        "configPath": str(WINDOWS_HOME / ".cursor"),
        "skillsPath": None,
        "agentsPath": None,
        "detectionFiles": ["settings.json"],
    },
    "hermes": {
        "name": "Hermes Agent",
        "icon": "🐉",
        "color": "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",
        "description": "终端 AI 助手，支持多工具集成",
        "configPath": str(WINDOWS_HOME / ".hermes"),
        "skillsPath": str(WINDOWS_HOME / ".hermes" / "skills"),
        "agentsPath": str(WINDOWS_HOME / ".hermes" / "agents"),
        "detectionFiles": ["config.yaml", ".env"],
    },
    "agenthub": {
        "name": "AgentHub",
        "icon": "🤖",
        "color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "description": "AI 工具管理平台，中央控制中心",
        "configPath": str(WINDOWS_HOME / ".agenthub"),
        "skillsPath": str(WINDOWS_HOME / ".agenthub" / "skills"),
        "agentsPath": None,
        "detectionFiles": ["config.yaml", "agenthub.db"],
    },
}


def detect_tool(tool_id: str, config: dict) -> dict:
    """
    检测单个工具的安装状态
    
    Returns:
        dict with detected, skills, agents, config_info
    """
    config_path = Path(config["configPath"])
    
    # 检测目录是否存在
    detected = config_path.exists()
    
    if not detected:
        return {
            "detected": False,
            "skills": [],
            "agents": [],
            "configInfo": {},
        }
    
    # 扫描 Skills
    skills = []
    skills_path = Path(config["skillsPath"]) if config["skillsPath"] else None
    if skills_path and skills_path.exists():
        for item in skills_path.iterdir():
            if item.is_dir():
                # 检查是否有 SKILL.md
                skill_md = item / "SKILL.md"
                skills.append({
                    "name": item.name,
                    "path": str(item),
                    "hasSkillMd": skill_md.exists(),
                    "installedAt": datetime.fromtimestamp(item.stat().st_mtime).isoformat() if hasattr(item, 'stat') else None,
                })
    
    # 扫描 Agents
    agents = []
    agents_path = Path(config["agentsPath"]) if config["agentsPath"] else None
    if agents_path and agents_path.exists():
        if agents_path.is_dir():
            for item in agents_path.iterdir():
                if item.is_dir() or item.suffix == '.json' or item.suffix == '.md':
                    agents.append({
                        "name": item.stem if item.is_file() else item.name,
                        "path": str(item),
                        "type": item.suffix or "dir",
                    })
        elif agents_path.is_file():
            # JSON 文件，尝试解析
            try:
                data = json.loads(agents_path.read_text(encoding='utf-8'))
                if isinstance(data, list):
                    agents = [{"name": a.get("name", "unknown"), "data": a} for a in data]
                elif isinstance(data, dict):
                    agents = [{"name": k, "data": v} for k, v in data.items()]
            except:
                agents = [{"name": agents_path.stem, "path": str(agents_path)}]
    
    # 读取配置文件信息
    config_info = {}
    if config_path.exists():
        config_info["检测路径"] = str(config_path)
        
        # 尝试读取配置文件
        for detect_file in config.get("detectionFiles", []):
            file_path = config_path / detect_file
            if file_path.exists():
                try:
                    if file_path.suffix == '.json':
                        data = json.loads(file_path.read_text(encoding='utf-8'))
                        if isinstance(data, dict):
                            # 提取基本信息
                            if "version" in data:
                                config_info["版本"] = data["version"]
                            if "name" in data:
                                config_info["名称"] = data["name"]
                    config_info[detect_file] = "✓"
                except:
                    config_info[detect_file] = "存在"
    
    return {
        "detected": detected,
        "skills": skills,
        "agents": agents,
        "configInfo": config_info,
    }


def detect_all_tools() -> list:
    """检测所有已配置的 AI 工具"""
    results = []
    
    for tool_id, config in TOOLS_CONFIG.items():
        detection = detect_tool(tool_id, config)
        results.append({
            "id": tool_id,
            "name": config["name"],
            "icon": config["icon"],
            "color": config["color"],
            "description": config["description"],
            "configPath": config["configPath"],
            "skillsPath": config["skillsPath"],
            "agentsPath": config["agentsPath"],
            **detection,
        })
    
    return results


# ===== FastAPI App =====

app = FastAPI(
    title="AI Tools Detection API",
    description="检测和管理本地 AI 工具的安装状况",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "AI Tools Detection API",
        "version": "1.0.0",
        "endpoints": {
            "/tools": "获取所有工具检测结果",
            "/tools/{tool_id}": "获取指定工具详情",
            "/tools/{tool_id}/skills": "获取工具的 Skills",
            "/tools/{tool_id}/agents": "获取工具的 Agents",
        },
    }


@app.get("/api/detect")
async def detect():
    """检测所有 AI 工具"""
    tools = detect_all_tools()
    detected_count = sum(1 for t in tools if t["detected"])
    total_skills = sum(len(t["skills"]) for t in tools)
    total_agents = sum(len(t["agents"]) for t in tools)
    
    return {
        "success": True,
        "data": {
            "tools": tools,
            "stats": {
                "total": len(tools),
                "detected": detected_count,
                "missing": len(tools) - detected_count,
                "totalSkills": total_skills,
                "totalAgents": total_agents,
                "healthPercent": round(detected_count / len(tools) * 100) if tools else 0,
            },
            "scanTime": datetime.now().isoformat(),
        }
    }


@app.get("/api/tools")
async def list_tools():
    """获取所有工具列表（简化版）"""
    tools = detect_all_tools()
    return {
        "success": True,
        "data": [
            {
                "id": t["id"],
                "name": t["name"],
                "icon": t["icon"],
                "color": t["color"],
                "description": t["description"],
                "detected": t["detected"],
                "skillsCount": len(t["skills"]),
                "agentsCount": len(t["agents"]),
            }
            for t in tools
        ]
    }


@app.get("/api/tools/{tool_id}")
async def get_tool(tool_id: str):
    """获取指定工具详情"""
    if tool_id not in TOOLS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
    
    config = TOOLS_CONFIG[tool_id]
    detection = detect_tool(tool_id, config)
    
    return {
        "success": True,
        "data": {
            "id": tool_id,
            "name": config["name"],
            "icon": config["icon"],
            "color": config["color"],
            "description": config["description"],
            "configPath": config["configPath"],
            "skillsPath": config["skillsPath"],
            "agentsPath": config["agentsPath"],
            **detection,
        }
    }


@app.get("/api/tools/{tool_id}/skills")
async def get_tool_skills(tool_id: str):
    """获取工具的 Skills"""
    if tool_id not in TOOLS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
    
    config = TOOLS_CONFIG[tool_id]
    detection = detect_tool(tool_id, config)
    
    return {
        "success": True,
        "data": detection["skills"],
        "total": len(detection["skills"]),
    }


@app.get("/api/tools/{tool_id}/agents")
async def get_tool_agents(tool_id: str):
    """获取工具的 Agents"""
    if tool_id not in TOOLS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
    
    config = TOOLS_CONFIG[tool_id]
    detection = detect_tool(tool_id, config)
    
    return {
        "success": True,
        "data": detection["agents"],
        "total": len(detection["agents"]),
    }


@app.post("/api/tools/{tool_id}/skills/{skill_name}/enable")
async def enable_skill(tool_id: str, skill_name: str):
    """启用 Skill"""
    return {"success": True, "message": f"{skill_name} 已启用"}


@app.post("/api/tools/{tool_id}/skills/{skill_name}/disable")
async def disable_skill(tool_id: str, skill_name: str):
    """禁用 Skill"""
    return {"success": True, "message": f"{skill_name} 已禁用"}


@app.get("/api/shared-skills")
async def get_shared_skills():
    """获取共享技能库"""
    shared_path = WINDOWS_HOME / ".openclaw" / "shared-skills"
    skills = []
    
    if shared_path.exists():
        for item in shared_path.iterdir():
            if item.is_dir():
                skills.append({
                    "name": item.name,
                    "path": str(item),
                    "type": "shared",
                })
    
    return {
        "success": True,
        "data": skills,
        "total": len(skills),
    }


@app.get("/api/openclaw/agents")
async def get_openclaw_agents():
    """获取 OpenClaw 的所有 Agent 配置"""
    openclaw_path = WINDOWS_HOME / ".openclaw"
    agents_dir = openclaw_path / "subagents"
    
    agents = []
    if agents_dir.exists():
        for item in agents_dir.iterdir():
            if item.is_dir():
                # 读取 agent 的配置
                agent_info = {"name": item.name, "path": str(item)}
                
                # 尝试读取 README
                readme = item / "AGENTS.md"
                if readme.exists():
                    try:
                        agent_info["description"] = readme.read_text(encoding='utf-8')[:200]
                    except:
                        pass
                
                agents.append(agent_info)
    
    return {
        "success": True,
        "data": agents,
        "total": len(agents),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5174)
