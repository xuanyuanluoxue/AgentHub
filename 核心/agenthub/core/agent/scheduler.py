# -*- coding: utf-8 -*-
"""
Agent Scheduler - 任务调度器
"""

import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Optional, Callable, Any
from dataclasses import dataclass, field

from agenthub.core.agent.models import Task, TaskStatus, TaskResult, TaskPriority
from agenthub.core.agent.router import AgentRouter, NoAgentAvailableError
from agenthub.core.agent.adapters.base import BaseAgentAdapter


@dataclass
class ScheduleResult:
    """调度结果"""
    task_id: str
    scheduled: bool
    agent_name: Optional[str] = None
    error: Optional[str] = None


class TaskScheduler:
    """
    任务调度器
    
    管理任务队列，执行 DAG 调度，支持并发
    """
    
    def __init__(
        self,
        router: AgentRouter,
        max_workers: int = 4,
        enable_dag: bool = True,
    ):
        """
        初始化调度器
        
        Args:
            router: 路由引擎
            max_workers: 最大并发数
            enable_dag: 是否启用 DAG 调度（依赖管理）
        """
        self.router = router
        self.max_workers = max_workers
        self.enable_dag = enable_dag
        
        # 任务队列（按优先级）
        self._task_queue = queue.PriorityQueue()
        
        # 进行中的任务
        self._running_tasks: dict[str, Task] = {}
        self._running_lock = threading.Lock()
        
        # 任务结果
        self._results: dict[str, TaskResult] = {}
        self._results_lock = threading.Lock()
        
        # 完成的任务（用于 DAG）
        self._completed_tasks: set[str] = set()
        
        # 回调
        self._callbacks: dict[str, list[Callable]] = {
            "task_scheduled": [],
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "task_cancelled": [],
        }
        
        # 执行器
        self._executor: Optional[ThreadPoolExecutor] = None
        self._shutdown = False
    
    # ===== 生命周期 =====
    
    def start(self):
        """启动调度器"""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
            self._shutdown = False
    
    def stop(self, wait: bool = True):
        """停止调度器"""
        self._shutdown = True
        if self._executor:
            self._executor.shutdown(wait=wait)
            self._executor = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    # ===== 任务管理 =====
    
    def submit(self, task: Task) -> ScheduleResult:
        """
        提交任务
        
        Args:
            task: 任务对象
            
        Returns:
            ScheduleResult
        """
        if self._shutdown:
            return ScheduleResult(task.id, False, error="调度器已停止")
        
        # 检查依赖
        if self.enable_dag and task.dependencies:
            unmet = self._check_dependencies(task)
            if unmet:
                return ScheduleResult(
                    task.id, False,
                    error=f"依赖未满足: {', '.join(unmet)}"
                )
        
        # 路由到 Agent
        try:
            agent_name = self.router.route(task)
        except NoAgentAvailableError as e:
            return ScheduleResult(task.id, False, error=str(e))
        
        # 加入队列
        self._task_queue.put((task.priority.value, task.id, task))
        
        # 触发回调
        self._trigger_callback("task_scheduled", task, agent_name)
        
        return ScheduleResult(task.id, True, agent_name)
    
    def submit_batch(self, tasks: list[Task]) -> list[ScheduleResult]:
        """批量提交任务"""
        return [self.submit(task) for task in tasks]
    
    def cancel(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否成功取消
        """
        with self._running_lock:
            if task_id in self._running_tasks:
                task = self._running_tasks[task_id]
                task.mark_cancelled()
                return True
        
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        with self._running_lock:
            return self._running_tasks.get(task_id)
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        with self._results_lock:
            return self._results.get(task_id)
    
    def list_tasks(self, status: TaskStatus = None) -> list[Task]:
        """列出任务"""
        with self._running_lock:
            tasks = list(self._running_tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return tasks
    
    # ===== 执行 =====
    
    def execute_next(self) -> Optional[TaskResult]:
        """
        执行下一个任务（阻塞）
        
        Returns:
            任务结果或 None
        """
        if self._shutdown:
            return None
        
        try:
            # 取出任务
            priority, task_id, task = self._task_queue.get(timeout=1)
        except queue.Empty:
            return None
        
        return self._execute_task(task)
    
    def execute_all(self, timeout: Optional[float] = None) -> list[TaskResult]:
        """
        执行所有队列中的任务
        
        Args:
            timeout: 最大等待时间（秒）
            
        Returns:
            结果列表
        """
        results = []
        start_time = time.time()
        
        while not self._shutdown:
            # 检查超时
            if timeout and (time.time() - start_time) > timeout:
                break
            
            # 检查队列
            if self._task_queue.empty():
                break
            
            result = self.execute_next()
            if result:
                results.append(result)
        
        return results
    
    def _execute_task(self, task: Task) -> Optional[TaskResult]:
        """执行单个任务"""
        # 检查依赖（再次检查）
        if self.enable_dag and task.dependencies:
            unmet = self._check_dependencies(task)
            if unmet:
                task.mark_failed(f"依赖未满足: {', '.join(unmet)}")
                return self._make_result(task)
        
        # 分配 Agent
        try:
            agent_name = self.router.route(task)
        except NoAgentAvailableError as e:
            task.mark_failed(str(e))
            return self._make_result(task)
        
        # 获取适配器
        adapter = self.router._adapters.get(agent_name)
        if not adapter:
            task.mark_failed(f"找不到适配器: {agent_name}")
            return self._make_result(task)
        
        # 标记运行
        task.mark_running(agent_name)
        
        with self._running_lock:
            self._running_tasks[task.id] = task
        
        self._trigger_callback("task_started", task)
        
        # 执行
        result = adapter.execute(task)
        
        # 更新状态
        with self._running_lock:
            if task.id in self._running_tasks:
                del self._running_tasks[task.id]
        
        # 处理结果
        if result.success:
            task.mark_completed(result.result)
            self._trigger_callback("task_completed", task, result)
        else:
            task.mark_failed(result.error)
            self._trigger_callback("task_failed", task, result)
        
        # 记录结果
        with self._results_lock:
            self._results[task.id] = result
        
        # 标记完成
        with self._running_lock:
            self._completed_tasks.add(task.id)
        
        return result
    
    def _check_dependencies(self, task: Task) -> list[str]:
        """检查依赖是否满足"""
        unmet = []
        for dep_id in task.dependencies:
            if dep_id not in self._completed_tasks:
                # 检查依赖任务是否失败
                with self._results_lock:
                    if dep_id in self._results and not self._results[dep_id].success:
                        unmet.append(dep_id)
        return unmet
    
    def _make_result(self, task: Task) -> TaskResult:
        """从任务创建结果"""
        return TaskResult(
            task_id=task.id,
            success=task.status == TaskStatus.COMPLETED,
            result=task.result,
            error=task.error,
            agent_name=task.assigned_agent,
            duration_seconds=task.duration_seconds(),
        )
    
    # ===== 回调 =====
    
    def on(self, event: str, callback: Callable):
        """
        注册回调
        
        Args:
            event: 事件类型 (task_scheduled/task_started/task_completed/task_failed/task_cancelled)
            callback: 回调函数
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, *args):
        """触发回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args)
            except Exception:
                pass  # 回调错误不中断主流程
    
    # ===== 统计 =====
    
    def get_stats(self) -> dict:
        """获取调度统计"""
        with self._running_lock:
            running = len(self._running_tasks)
            completed = len(self._completed_tasks)
        
        with self._results_lock:
            total_results = len(self._results)
            success_count = sum(1 for r in self._results.values() if r.success)
            failed_count = total_results - success_count
        
        return {
            "running": running,
            "completed": completed,
            "in_queue": self._task_queue.qsize(),
            "total_results": total_results,
            "success": success_count,
            "failed": failed_count,
            "max_workers": self.max_workers,
            "shutdown": self._shutdown,
        }
