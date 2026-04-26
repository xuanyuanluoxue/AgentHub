# -*- coding: utf-8 -*-
"""
Agent 数据模型
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from datetime import datetime
import uuid


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class AgentCapability(Enum):
    """Agent 能力"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    CREATIVE = "creative"
    CONVERSATION = "conversation"


@dataclass
class AgentConfig:
    """Agent 配置"""
    name: str
    adapter_type: str  # e.g., "claude", "codex", "opencode"
    
    # 可选配置
    description: Optional[str] = None
    capabilities: list[AgentCapability] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    timeout: int = 300  # 秒
    enabled: bool = True
    
    # 适配器特定配置
    adapter_config: dict = field(default_factory=dict)
    
    # 权重（用于负载均衡）
    weight: float = 1.0
    
    def supports_capability(self, cap: AgentCapability) -> bool:
        """检查是否支持某能力"""
        return cap in self.capabilities
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "adapter_type": self.adapter_type,
            "description": self.description,
            "capabilities": [c.value for c in self.capabilities],
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "timeout": self.timeout,
            "enabled": self.enabled,
            "adapter_config": self.adapter_config,
            "weight": self.weight,
        }


@dataclass
class Task:
    """任务"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    
    # 任务类型
    task_type: str = "general"  # general, code, research, creative
    
    # 优先级
    priority: TaskPriority = TaskPriority.NORMAL
    
    # 状态
    status: TaskStatus = TaskStatus.PENDING
    
    # 依赖
    dependencies: list[str] = field(default_factory=list)  # 依赖的任务 ID
    
    # 输入
    input_data: dict = field(default_factory=dict)
    
    # 输出
    result: Optional[Any] = None
    error: Optional[str] = None
    
    # 执行信息
    assigned_agent: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def mark_running(self, agent_name: str):
        """标记为运行中"""
        self.status = TaskStatus.RUNNING
        self.assigned_agent = agent_name
        self.started_at = datetime.now()
    
    def mark_completed(self, result: Any):
        """标记为完成"""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str):
        """标记为失败"""
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
    
    def mark_cancelled(self):
        """标记为取消"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def duration_seconds(self) -> Optional[float]:
        """运行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "input_data": self.input_data,
            "result": self.result,
            "error": self.error,
            "assigned_agent": self.assigned_agent,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "duration_seconds": self.duration_seconds(),
            "metadata": self.metadata,
        }


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    agent_name: Optional[str] = None
    duration_seconds: Optional[float] = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "agent_name": self.agent_name,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


@dataclass
class RouterRule:
    """路由规则"""
    name: str
    description: Optional[str] = None
    
    # 匹配条件
    keywords: list[str] = field(default_factory=list)  # 关键词匹配
    task_types: list[str] = field(default_factory=list)  # 任务类型匹配
    capabilities: list[AgentCapability] = field(default_factory=list)  # 需要的能力
    
    # 目标
    target_agent: Optional[str] = None  # 指定的 Agent
    target_adapter: Optional[str] = None  # 指定的适配器类型
    
    # 优先级（数字越大优先级越高）
    priority: int = 0
    
    def matches(self, task: Task) -> bool:
        """检查任务是否匹配此规则"""
        # 检查任务类型
        if self.task_types and task.task_type not in self.task_types:
            return False
        
        # 检查关键词
        if self.keywords:
            desc_lower = task.description.lower()
            if not any(kw.lower() in desc_lower for kw in self.keywords):
                return False
        
        return True
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "task_types": self.task_types,
            "capabilities": [c.value for c in self.capabilities],
            "target_agent": self.target_agent,
            "target_adapter": self.target_adapter,
            "priority": self.priority,
        }
