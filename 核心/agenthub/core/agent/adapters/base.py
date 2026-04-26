# -*- coding: utf-8 -*-
"""
Agent Adapter 基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum

from agenthub.core.agent.models import Task, TaskResult, AgentConfig, AgentCapability


class AdapterStatus(Enum):
    """适配器状态"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AdapterConfig:
    """适配器配置"""
    name: str
    adapter_type: str
    
    # 连接配置
    command: Optional[str] = None  # 启动命令
    args: list[str] = field(default_factory=list)
    env: dict = field(default_factory=dict)
    
    # 运行配置
    working_dir: Optional[str] = None
    timeout: int = 300
    
    # 状态
    enabled: bool = True


class BaseAgentAdapter(ABC):
    """
    Agent 适配器基类
    
    所有 Agent 框架（Claude Code、Codex、OpenCode 等）都通过适配器接入
    """
    
    def __init__(self, config: AdapterConfig):
        self.config = config
        self.status = AdapterStatus.IDLE
        self._running_tasks = 0
    
    @property
    @abstractmethod
    def name(self) -> str:
        """适配器名称"""
        pass
    
    @property
    @abstractmethod
    def adapter_type(self) -> str:
        """适配器类型"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> list[AgentCapability]:
        """此适配器支持的能力"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查适配器是否可用（工具已安装）"""
        pass
    
    @abstractmethod
    def execute(self, task: Task) -> TaskResult:
        """
        执行任务
        
        Args:
            task: 任务对象
            
        Returns:
            TaskResult: 任务结果
        """
        pass
    
    def can_handle(self, task: Task) -> bool:
        """
        检查是否能处理此任务
        
        默认实现：检查 capabilities 是否覆盖任务类型
        子类可以覆盖实现更复杂的逻辑
        """
        return True
    
    def update_status(self, status: AdapterStatus):
        """更新状态"""
        self.status = status
    
    def increment_tasks(self):
        """增加运行中任务数"""
        self._running_tasks += 1
        if self._running_tasks > 0:
            self.status = AdapterStatus.BUSY
    
    def decrement_tasks(self):
        """减少运行中任务数"""
        self._running_tasks = max(0, self._running_tasks - 1)
        if self._running_tasks == 0:
            self.status = AdapterStatus.IDLE
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "name": self.name,
            "type": self.adapter_type,
            "status": self.status.value,
            "running_tasks": self._running_tasks,
            "capabilities": [c.value for c in self.capabilities],
        }


class CliAgentAdapter(BaseAgentAdapter):
    """
    CLI 类型的 Agent 适配器
    
    通过命令行调用外部 Agent 工具
    """
    
    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self._check_cache = None
    
    @abstractmethod
    def build_command(self, task: Task) -> list[str]:
        """构建命令行参数"""
        pass
    
    @abstractmethod
    def parse_output(self, output: str) -> Any:
        """解析输出"""
        pass
    
    def is_available(self) -> bool:
        """检查命令是否可用"""
        if self._check_cache is not None:
            return self._check_cache
        
        import shutil
        if not self.config.command:
            self._check_cache = False
            return False
        
        self._check_cache = shutil.which(self.config.command) is not None
        return self._check_cache
    
    def execute(self, task: Task) -> TaskResult:
        """通过 CLI 执行任务"""
        import subprocess
        import time
        
        start_time = time.time()
        
        try:
            self.increment_tasks()
            
            # 构建命令
            cmd = self.build_command(task)
            
            # 执行
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=self.config.working_dir,
                env={**subprocess.os.environ, **self.config.env},
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                parsed = self.parse_output(result.stdout)
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    result=parsed,
                    agent_name=self.name,
                    duration_seconds=duration,
                )
            else:
                return TaskResult(
                    task_id=task.id,
                    success=False,
                    error=result.stderr or result.stdout,
                    agent_name=self.name,
                    duration_seconds=duration,
                )
                
        except subprocess.TimeoutExpired:
            return TaskResult(
                task_id=task.id,
                success=False,
                error=f"任务超时（{self.config.timeout}秒）",
                agent_name=self.name,
                duration_seconds=time.time() - start_time,
            )
        except Exception as e:
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                agent_name=self.name,
                duration_seconds=time.time() - start_time,
            )
        finally:
            self.decrement_tasks()
