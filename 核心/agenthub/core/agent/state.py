# -*- coding: utf-8 -*-
"""
Agent State - 状态管理
"""

import json
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import threading


@dataclass
class AgentStateSnapshot:
    """Agent 状态快照"""
    timestamp: str
    agents: dict[str, dict]
    tasks: dict[str, dict]
    metrics: dict
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "agents": self.agents,
            "tasks": self.tasks,
            "metrics": self.metrics,
        }


class AgentState:
    """
    Agent 状态管理器
    
    管理 Agent 和任务的运行时状态，支持持久化
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化状态管理器
        
        Args:
            storage_path: 状态文件路径，None 表示内存存储
        """
        self._storage_path = storage_path
        self._lock = threading.RLock()
        
        # 内存状态
        self._agent_states: dict[str, dict] = {}
        self._task_states: dict[str, dict] = {}
        self._metrics: dict[str, Any] = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_tokens": 0,
        }
        
        # 加载持久化状态
        if storage_path:
            self._load()
    
    # ===== Agent 状态 =====
    
    def set_agent_state(self, agent_name: str, state: dict):
        """
        设置 Agent 状态
        
        Args:
            agent_name: Agent 名称
            state: 状态字典
        """
        with self._lock:
            self._agent_states[agent_name] = {
                **state,
                "updated_at": datetime.now().isoformat(),
            }
            self._save()
    
    def get_agent_state(self, agent_name: str) -> Optional[dict]:
        """获取 Agent 状态"""
        with self._lock:
            return self._agent_states.get(agent_name)
    
    def list_agent_states(self) -> dict[str, dict]:
        """列出所有 Agent 状态"""
        with self._lock:
            return dict(self._agent_states)
    
    def update_agent_metric(self, agent_name: str, metric: str, value: Any):
        """更新 Agent 指标"""
        with self._lock:
            if agent_name not in self._agent_states:
                self._agent_states[agent_name] = {}
            
            if "metrics" not in self._agent_states[agent_name]:
                self._agent_states[agent_name]["metrics"] = {}
            
            self._agent_states[agent_name]["metrics"][metric] = value
            self._agent_states[agent_name]["updated_at"] = datetime.now().isoformat()
            self._save()
    
    # ===== Task 状态 =====
    
    def set_task_state(self, task_id: str, state: dict):
        """
        设置任务状态
        
        Args:
            task_id: 任务 ID
            state: 状态字典
        """
        with self._lock:
            self._task_states[task_id] = {
                **state,
                "updated_at": datetime.now().isoformat(),
            }
            self._save()
    
    def get_task_state(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        with self._lock:
            return self._task_states.get(task_id)
    
    def list_task_states(self, agent_name: Optional[str] = None) -> dict[str, dict]:
        """
        列出任务状态
        
        Args:
            agent_name: 可选，筛选特定 Agent 的任务
        """
        with self._lock:
            if agent_name:
                return {
                    tid: state 
                    for tid, state in self._task_states.items()
                    if state.get("agent") == agent_name
                }
            return dict(self._task_states)
    
    def delete_task_state(self, task_id: str) -> bool:
        """删除任务状态"""
        with self._lock:
            if task_id in self._task_states:
                del self._task_states[task_id]
                self._save()
                return True
            return False
    
    # ===== 全局指标 =====
    
    def increment_metric(self, metric: str, value: int = 1):
        """增加指标"""
        with self._lock:
            if metric not in self._metrics:
                self._metrics[metric] = 0
            self._metrics[metric] += value
            self._save()
    
    def set_metric(self, metric: str, value: Any):
        """设置指标"""
        with self._lock:
            self._metrics[metric] = value
            self._save()
    
    def get_metrics(self) -> dict:
        """获取所有指标"""
        with self._lock:
            return dict(self._metrics)
    
    # ===== 快照 =====
    
    def create_snapshot(self) -> AgentStateSnapshot:
        """创建状态快照"""
        with self._lock:
            return AgentStateSnapshot(
                timestamp=datetime.now().isoformat(),
                agents=dict(self._agent_states),
                tasks=dict(self._task_states),
                metrics=dict(self._metrics),
            )
    
    def restore_snapshot(self, snapshot: AgentStateSnapshot):
        """恢复状态快照"""
        with self._lock:
            self._agent_states = snapshot.agents
            self._task_states = snapshot.tasks
            self._metrics = snapshot.metrics
            self._save()
    
    # ===== 持久化 =====
    
    def _get_storage_file(self) -> Optional[Path]:
        """获取存储文件路径"""
        if not self._storage_path:
            return None
        return Path(self._storage_path).expanduser()
    
    def _load(self):
        """加载持久化状态"""
        storage_file = self._get_storage_file()
        if not storage_file or not storage_file.exists():
            return
        
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._agent_states = data.get("agents", {})
            self._task_states = data.get("tasks", {})
            self._metrics = data.get("metrics", self._metrics)
        except (json.JSONDecodeError, IOError):
            pass  # 忽略加载错误
    
    def _save(self):
        """保存状态到持久化"""
        storage_file = self._get_storage_file()
        if not storage_file:
            return
        
        try:
            storage_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "agents": self._agent_states,
                "tasks": self._task_states,
                "metrics": self._metrics,
                "saved_at": datetime.now().isoformat(),
            }
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass  # 忽略保存错误
    
    # ===== 清理 =====
    
    def clear_agent_states(self):
        """清空所有 Agent 状态"""
        with self._lock:
            self._agent_states.clear()
            self._save()
    
    def clear_task_states(self, before: Optional[datetime] = None):
        """
        清空任务状态
        
        Args:
            before: 可选，删除此时间之前的任务
        """
        with self._lock:
            if before is None:
                self._task_states.clear()
            else:
                self._task_states = {
                    tid: state 
                    for tid, state in self._task_states.items()
                    if datetime.fromisoformat(state.get("updated_at", "2000-01-01")) > before
                }
            self._save()
    
    def reset_metrics(self):
        """重置指标"""
        with self._lock:
            self._metrics = {
                "total_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "total_tokens": 0,
            }
            self._save()
