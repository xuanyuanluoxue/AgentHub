# -*- coding: utf-8 -*-
"""
OpenCode Adapter
"""

import shutil
from typing import Any

from agenthub.core.agent.adapters.base import AdapterConfig, CliAgentAdapter
from agenthub.core.agent.models import Task, TaskResult, AgentCapability


class OpenCodeAdapter(CliAgentAdapter):
    """
    OpenCode 适配器
    
    通过 opencode 命令行工具调用 OpenCode
    """
    
    def __init__(self, config: AdapterConfig = None):
        if config is None:
            config = AdapterConfig(
                name="opencode",
                adapter_type="opencode",
                command="opencode",
            )
        super().__init__(config)
    
    @property
    def name(self) -> str:
        return "opencode"
    
    @property
    def adapter_type(self) -> str:
        return "opencode"
    
    @property
    def capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability.CODE_GENERATION,
            AgentCapability.CODE_REVIEW,
            AgentCapability.DEBUGGING,
            AgentCapability.REFACTORING,
            AgentCapability.TESTING,
            AgentCapability.DEPLOYMENT,
        ]
    
    def is_available(self) -> bool:
        """检查 opencode 命令是否可用"""
        return shutil.which("opencode") is not None
    
    def build_command(self, task: Task) -> list[str]:
        """构建 opencode 命令"""
        cmd = ["opencode"]
        
        # 根据任务类型选择模式
        if task.task_type == "code":
            cmd.extend(["--mode", "code"])
        elif task.task_type == "research":
            cmd.extend(["--mode", "research"])
        
        # 添加任务描述
        cmd.extend([task.description])
        
        return cmd
    
    def parse_output(self, output: str) -> Any:
        """解析 OpenCode 输出"""
        return output.strip()
    
    def can_handle(self, task: Task) -> bool:
        """检查是否能处理"""
        if not self.is_available():
            return False
        
        # OpenCode 比较通用，大多数任务都能处理
        return True
