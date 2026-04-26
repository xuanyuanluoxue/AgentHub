# -*- coding: utf-8 -*-
"""
Agent 模块测试
"""

import pytest
import threading
import time

from agenthub.core.agent.models import (
    Task, TaskStatus, TaskPriority, TaskResult,
    AgentConfig, AgentCapability, RouterRule
)
from agenthub.core.agent.router import AgentRouter, NoAgentAvailableError
from agenthub.core.agent.scheduler import TaskScheduler
from agenthub.core.agent.state import AgentState
from agenthub.core.agent.adapters.base import AdapterConfig, CliAgentAdapter


# Mock adapter for testing
class MockAdapter(CliAgentAdapter):
    """测试用 Mock 适配器"""
    
    def __init__(self, name="mock", available=True, capabilities=None):
        config = AdapterConfig(name=name, adapter_type="mock")
        super().__init__(config)
        self._available = available
        self._capabilities = capabilities or [AgentCapability.CODE_GENERATION]
        self.executed_tasks = []
    
    @property
    def name(self):
        return self.config.name
    
    @property
    def adapter_type(self):
        return "mock"
    
    @property
    def capabilities(self):
        return self._capabilities
    
    def is_available(self):
        return self._available
    
    def build_command(self, task):
        return ["mock", task.description]
    
    def parse_output(self, output):
        return {"result": output}


# ===== 测试 Task 模型 =====

class TestTask:
    """Task 测试"""
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task(description="测试任务")
        
        assert task.id is not None
        assert task.description == "测试任务"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.NORMAL
    
    def test_task_mark_running(self):
        """测试标记运行"""
        task = Task(description="测试")
        task.mark_running("test-agent")
        
        assert task.status == TaskStatus.RUNNING
        assert task.assigned_agent == "test-agent"
        assert task.started_at is not None
    
    def test_task_mark_completed(self):
        """测试标记完成"""
        task = Task(description="测试")
        task.mark_running("test-agent")
        task.mark_completed({"result": "success"})
        
        assert task.status == TaskStatus.COMPLETED
        assert task.result == {"result": "success"}
        assert task.completed_at is not None
    
    def test_task_mark_failed(self):
        """测试标记失败"""
        task = Task(description="测试")
        task.mark_failed("错误信息")
        
        assert task.status == TaskStatus.FAILED
        assert task.error == "错误信息"
    
    def test_task_duration(self):
        """测试运行时长计算"""
        task = Task(description="测试")
        task.mark_running("agent")
        time.sleep(0.1)
        task.mark_completed("done")
        
        duration = task.duration_seconds()
        assert duration is not None
        assert duration >= 0.1


# ===== 测试 Router =====

class TestAgentRouter:
    """AgentRouter 测试"""
    
    def test_register_agent(self):
        """测试注册 Agent"""
        router = AgentRouter()
        config = AgentConfig(name="test", adapter_type="mock")
        adapter = MockAdapter("test")
        
        router.register_agent(config, adapter)
        
        assert "test" in router._agents
        assert "test" in router._adapters
    
    def test_route_no_agent(self):
        """测试无 Agent 时路由失败"""
        router = AgentRouter()
        task = Task(description="测试")
        
        with pytest.raises(NoAgentAvailableError):
            router.route(task)
    
    def test_route_basic(self):
        """测试基本路由"""
        router = AgentRouter()
        
        # 注册 Agent
        config = AgentConfig(name="test", adapter_type="mock")
        adapter = MockAdapter("test", available=True)
        router.register_agent(config, adapter)
        
        # 路由
        task = Task(description="测试")
        agent_name = router.route(task)
        
        assert agent_name == "test"
    
    def test_route_by_priority(self):
        """测试按优先级路由"""
        router = AgentRouter()
        
        # 注册两个 Agent
        config1 = AgentConfig(name="agent1", adapter_type="mock", weight=1.0)
        config2 = AgentConfig(name="agent2", adapter_type="mock", weight=2.0)
        adapter1 = MockAdapter("agent1")
        adapter2 = MockAdapter("agent2")
        
        router.register_agent(config1, adapter1)
        router.register_agent(config2, adapter2)
        
        # 应该选择负载更轻的
        task = Task(description="测试")
        agent_name = router.route(task)
        
        assert agent_name in ["agent1", "agent2"]
    
    def test_router_stats(self):
        """测试统计信息"""
        router = AgentRouter()
        config = AgentConfig(name="test", adapter_type="mock")
        adapter = MockAdapter("test")
        router.register_agent(config, adapter)
        
        stats = router.get_stats()
        
        assert stats["total_agents"] == 1
        assert stats["available_agents"] == 1


# ===== 测试 Scheduler =====

class TestTaskScheduler:
    """TaskScheduler 测试"""
    
    def test_scheduler_submit(self):
        """测试提交任务"""
        router = AgentRouter()
        config = AgentConfig(name="test", adapter_type="mock")
        adapter = MockAdapter("test")
        router.register_agent(config, adapter)
        
        scheduler = TaskScheduler(router)
        task = Task(description="测试任务")
        
        result = scheduler.submit(task)
        
        assert result.scheduled
        assert result.agent_name == "test"
    
    def test_scheduler_dag_dependency(self):
        """测试 DAG 依赖"""
        router = AgentRouter()
        config = AgentConfig(name="test", adapter_type="mock")
        adapter = MockAdapter("test")
        router.register_agent(config, adapter)
        
        scheduler = TaskScheduler(router, enable_dag=True)
        
        task1 = Task(description="任务1")
        task2 = Task(description="任务2", dependencies=[task1.id])
        
        # task1 先提交
        result1 = scheduler.submit(task1)
        assert result1.scheduled
        
        # task2 依赖 task1
        result2 = scheduler.submit(task2)
        assert result2.scheduled


# ===== 测试 State =====

class TestAgentState:
    """AgentState 测试"""
    
    def test_set_get_agent_state(self):
        """测试 Agent 状态存取"""
        state = AgentState()
        
        state.set_agent_state("test", {"status": "idle", "tasks": 5})
        retrieved = state.get_agent_state("test")
        
        assert retrieved is not None
        assert retrieved["status"] == "idle"
        assert retrieved["tasks"] == 5
    
    def test_set_get_task_state(self):
        """测试任务状态存取"""
        state = AgentState()
        
        state.set_task_state("task-1", {"status": "running", "agent": "test"})
        retrieved = state.get_task_state("task-1")
        
        assert retrieved is not None
        assert retrieved["status"] == "running"
    
    def test_metrics(self):
        """测试指标"""
        state = AgentState()
        
        state.increment_metric("total_tasks")
        state.increment_metric("total_tasks", 2)
        
        metrics = state.get_metrics()
        
        assert metrics["total_tasks"] == 3
    
    def test_snapshot(self):
        """测试快照"""
        state = AgentState()
        state.set_agent_state("test", {"status": "idle"})
        state.set_task_state("task-1", {"status": "done"})
        
        snapshot = state.create_snapshot()
        
        assert snapshot.agents["test"]["status"] == "idle"
        assert snapshot.tasks["task-1"]["status"] == "done"


# ===== 测试 RouterRule =====

class TestRouterRule:
    """RouterRule 测试"""
    
    def test_rule_matches_keyword(self):
        """测试关键词匹配"""
        rule = RouterRule(
            name="code-rule",
            keywords=["代码", "code"],
        )
        
        task1 = Task(description="写代码")
        task2 = Task(description="聊天")
        
        assert rule.matches(task1)
        assert not rule.matches(task2)
    
    def test_rule_matches_task_type(self):
        """测试任务类型匹配"""
        rule = RouterRule(
            name="code-task",
            task_types=["code"],
        )
        
        task1 = Task(description="测试", task_type="code")
        task2 = Task(description="测试", task_type="research")
        
        assert rule.matches(task1)
        assert not rule.matches(task2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
