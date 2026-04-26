# -*- coding: utf-8 -*-
"""
Agent Router - 路由引擎
"""

from typing import Optional
from agenthub.core.agent.models import Task, RouterRule, AgentConfig, AgentCapability
from agenthub.core.agent.adapters.base import BaseAgentAdapter


class RouterError(Exception):
    """路由错误"""
    pass


class NoAgentAvailableError(RouterError):
    """没有可用的 Agent"""
    pass


class AgentRouter:
    """
    Agent 路由引擎
    
    根据任务特征将任务路由到合适的 Agent
    """
    
    def __init__(self):
        self._agents: dict[str, AgentConfig] = {}
        self._adapters: dict[str, BaseAgentAdapter] = {}
        self._rules: list[RouterRule] = []
    
    # ===== Agent 注册 =====
    
    def register_agent(self, agent_config: AgentConfig, adapter: BaseAgentAdapter):
        """
        注册 Agent
        
        Args:
            agent_config: Agent 配置
            adapter: 适配器实例
        """
        self._agents[agent_config.name] = agent_config
        self._adapters[agent_config.name] = adapter
    
    def unregister_agent(self, name: str) -> bool:
        """取消注册 Agent"""
        if name in self._agents:
            del self._agents[name]
            del self._adapters[name]
            return True
        return False
    
    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """获取 Agent 配置"""
        return self._agents.get(name)
    
    def list_agents(self) -> list[AgentConfig]:
        """列出所有 Agent"""
        return list(self._agents.values())
    
    def get_available_agents(self) -> list[str]:
        """获取可用的 Agent 名称"""
        available = []
        for name, adapter in self._adapters.items():
            if adapter.is_available():
                agent_config = self._agents[name]
                if agent_config.enabled:
                    available.append(name)
        return available
    
    # ===== 路由规则 =====
    
    def add_rule(self, rule: RouterRule):
        """
        添加路由规则
        
        规则按 priority 排序，优先级高的先匹配
        """
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, name: str) -> bool:
        """移除路由规则"""
        for i, rule in enumerate(self._rules):
            if rule.name == name:
                del self._rules[i]
                return True
        return False
    
    def clear_rules(self):
        """清空所有规则"""
        self._rules.clear()
    
    # ===== 路由 =====
    
    def route(self, task: Task) -> str:
        """
        路由任务到合适的 Agent
        
        Args:
            task: 任务对象
            
        Returns:
            被选中的 Agent 名称
            
        Raises:
            NoAgentAvailableError: 没有可用的 Agent
        """
        # 1. 按规则匹配
        for rule in self._rules:
            if rule.matches(task):
                # 规则指定了 Agent
                if rule.target_agent and rule.target_agent in self._agents:
                    if self._is_agent_suitable(rule.target_agent, task):
                        return rule.target_agent
                
                # 规则指定了适配器类型
                if rule.target_adapter:
                    agent = self._find_agent_by_adapter(rule.target_adapter, task)
                    if agent:
                        return agent
        
        # 2. 按能力匹配
        if task.task_type:
            agent = self._find_agent_by_task_type(task)
            if agent:
                return agent
        
        # 3. 默认路由（负载均衡）
        agent = self._select_by_load()
        if agent:
            return agent
        
        raise NoAgentAvailableError(f"没有可用的 Agent 来处理任务: {task.description}")
    
    def _is_agent_suitable(self, agent_name: str, task: Task) -> bool:
        """检查 Agent 是否适合处理任务"""
        if agent_name not in self._agents:
            return False
        
        agent_config = self._agents[agent_name]
        adapter = self._adapters[agent_name]
        
        # 检查是否启用
        if not agent_config.enabled:
            return False
        
        # 检查是否可用
        if not adapter.is_available():
            return False
        
        # 检查并发限制
        if adapter._running_tasks >= agent_config.max_concurrent_tasks:
            return False
        
        # 检查能力
        if agent_config.capabilities:
            # 需要任务类型到能力的映射
            pass
        
        return True
    
    def _find_agent_by_adapter(self, adapter_type: str, task: Task) -> Optional[str]:
        """查找指定类型的 Agent"""
        candidates = []
        
        for name, agent_config in self._agents.items():
            if agent_config.adapter_type != adapter_type:
                continue
            
            if not self._is_agent_suitable(name, task):
                continue
            
            candidates.append(name)
        
        if not candidates:
            return None
        
        # 返回负载最轻的
        return min(candidates, key=lambda n: self._adapters[n]._running_tasks)
    
    def _find_agent_by_task_type(self, task: Task) -> Optional[str]:
        """根据任务类型查找 Agent"""
        # 任务类型到适配器类型的映射
        task_type_mapping = {
            "code": ["claude", "codex", "opencode"],
            "research": ["claude", "opencode"],
            "creative": ["claude", "opencode"],
            "general": ["opencode", "claude"],
        }
        
        preferred_adapters = task_type_mapping.get(task.task_type, [])
        
        for adapter_type in preferred_adapters:
            agent = self._find_agent_by_adapter(adapter_type, task)
            if agent:
                return agent
        
        return None
    
    def _select_by_load(self) -> Optional[str]:
        """按负载选择 Agent"""
        candidates = [
            (name, adapter._running_tasks / agent_config.weight)
            for name, (agent_config, adapter) in self._zip_agents_adapters()
            if agent_config.enabled and adapter.is_available()
        ]
        
        if not candidates:
            return None
        
        # 选择负载最轻的
        return min(candidates, key=lambda x: x[1])[0]
    
    def _zip_agents_adapters(self):
        """Zip agents and adapters"""
        for name in self._agents:
            yield name, (self._agents[name], self._adapters[name])
    
    def get_stats(self) -> dict:
        """获取路由统计"""
        return {
            "total_agents": len(self._agents),
            "available_agents": len(self.get_available_agents()),
            "total_rules": len(self._rules),
            "agents": {
                name: {
                    "type": self._agents[name].adapter_type,
                    "enabled": self._agents[name].enabled,
                    "available": self._adapters[name].is_available(),
                    "running_tasks": self._adapters[name]._running_tasks,
                    "capabilities": [c.value for c in self._agents[name].capabilities],
                }
                for name in self._agents
            },
        }
