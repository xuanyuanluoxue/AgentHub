# -*- coding: utf-8 -*-
"""
OpenAI Codex Adapter
"""

import shutil
from typing import Any

from agenthub.core.agent.adapters.base import AdapterConfig, CliAgentAdapter
from agenthub.core.agent.models import Task, TaskResult, AgentCapability


class CodexAdapter(CliAgentAdapter):
    """
    OpenAI Codex 适配器
    
    通过 codex 命令行工具调用 Codex
    """
    
    def __init__(self, config: AdapterConfig = None):
        if config is None:
            config = AdapterConfig(
                name="codex",
                adapter_type="codex",
                command="codex",
            )
        super().__init__(config)
    
    @property
    def name(self) -> str:
        return "codex"
    
    @property
    def adapter_type(self) -> str:
        return "codex"
    
    @property
    def capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability.CODE_GENERATION,
            AgentCapability.TESTING,
            AgentCapability.DEBUGGING,
        ]
    
    def is_available(self) -> bool:
        """检查 codex 命令是否可用"""
        return shutil.which("codex") is not None
    
    def build_command(self, task: Task) -> list[str]:
        """构建 codex 命令"""
        cmd = ["codex"]
        
        # 添加任务描述
        cmd.extend(["--prompt", task.description])
        
        return cmd
    
    def parse_output(self, output: str) -> Any:
        """解析 Codex 输出"""
        return output.strip()
    
    def can_handle(self, task: Task) -> bool:
        """检查是否能处理"""
        if not self.is_available():
            return False
        
        # Codex 适合纯代码生成任务
        code_keywords = ["代码", "code", "write", "function", "class"]
        
        desc_lower = task.description.lower()
        return any(kw.lower() in desc_lower for kw in code_keywords)
