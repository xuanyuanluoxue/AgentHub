# -*- coding: utf-8 -*-
"""
Claude Code Adapter
"""

import shutil
from typing import Any

from agenthub.core.agent.adapters.base import AdapterConfig, CliAgentAdapter
from agenthub.core.agent.models import Task, TaskResult, AgentCapability


class ClaudeAdapter(CliAgentAdapter):
    """
    Claude Code 适配器
    
    通过 claude 命令行工具调用 Claude Code
    """
    
    def __init__(self, config: AdapterConfig = None):
        if config is None:
            config = AdapterConfig(
                name="claude",
                adapter_type="claude",
                command="claude",
            )
        super().__init__(config)
    
    @property
    def name(self) -> str:
        return "claude"
    
    @property
    def adapter_type(self) -> str:
        return "claude"
    
    @property
    def capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability.CODE_GENERATION,
            AgentCapability.CODE_REVIEW,
            AgentCapability.DEBUGGING,
            AgentCapability.REFACTORING,
            AgentCapability.DOCUMENTATION,
            AgentCapability.ANALYSIS,
            AgentCapability.RESEARCH,
        ]
    
    def is_available(self) -> bool:
        """检查 claude 命令是否可用"""
        return shutil.which("claude") is not None
    
    def build_command(self, task: Task) -> list[str]:
        """构建 claude 命令"""
        cmd = ["claude"]
        
        # 任务类型决定模式
        if task.task_type == "code":
            cmd.extend(["--dangerously-skip-permissions"])
            # 可以添加更多代码特定参数
        
        # 添加提示词
        cmd.extend(["--print", task.description])
        
        return cmd
    
    def parse_output(self, output: str) -> Any:
        """解析 Claude 输出"""
        return output.strip()
    
    def can_handle(self, task: Task) -> bool:
        """检查是否能处理"""
        if not self.is_available():
            return False
        
        # Claude 适合代码和分析任务
        code_keywords = ["代码", "code", "写", "开发", "debug", "fix"]
        analysis_keywords = ["分析", "analysis", "研究", "research", "review"]
        
        desc_lower = task.description.lower()
        return any(kw.lower() in desc_lower for kw in code_keywords + analysis_keywords)
