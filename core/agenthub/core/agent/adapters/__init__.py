# -*- coding: utf-8 -*-
"""
Agent Adapters - 各框架适配器
"""

from agenthub.core.agent.adapters.base import (
    BaseAgentAdapter,
    AdapterConfig,
    AdapterStatus,
    CliAgentAdapter,
)
from agenthub.core.agent.adapters.claude_adapter import ClaudeAdapter
from agenthub.core.agent.adapters.codex_adapter import CodexAdapter
from agenthub.core.agent.adapters.opencode_adapter import OpenCodeAdapter

__all__ = [
    "BaseAgentAdapter",
    "AdapterConfig",
    "AdapterStatus", 
    "CliAgentAdapter",
    "ClaudeAdapter",
    "CodexAdapter",
    "OpenCodeAdapter",
]
