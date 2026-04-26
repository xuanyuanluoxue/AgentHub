# -*- coding: utf-8 -*-
"""
Database Manager - SQLite 数据库管理
"""

import sqlite3
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
from contextlib import contextmanager

from agenthub.core.agent.models import Task, TaskStatus, TaskResult


class DatabaseManager:
    """
    SQLite 数据库管理器
    
    管理 AgentHub 的持久化数据：
    - 任务记录
    - 执行历史
    - Skill 使用统计
    """
    
    _local = threading.local()
    
    def __init__(self, db_path: str = "~/.agenthub/agenthub.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取线程局部的数据库连接"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    @contextmanager
    def _cursor(self):
        """数据库游标上下文管理器"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def _init_db(self):
        """初始化数据库表"""
        with self._cursor() as cursor:
            # 任务表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority TEXT NOT NULL DEFAULT 'normal',
                    agent_name TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    result TEXT,
                    error TEXT,
                    metadata TEXT
                )
            """)
            
            # 技能表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    name TEXT PRIMARY KEY,
                    version TEXT NOT NULL,
                    description TEXT,
                    author TEXT,
                    tags TEXT,
                    triggers TEXT,
                    installed_at TEXT NOT NULL,
                    last_used TEXT,
                    use_count INTEGER DEFAULT 0,
                    path TEXT NOT NULL,
                    source TEXT DEFAULT 'local'
                )
            """)
            
            # 执行历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    duration_seconds REAL,
                    success INTEGER NOT NULL,
                    result TEXT,
                    error TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)
            
            # 索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_task ON execution_history(task_id)")
    
    # ===== 任务操作 =====
    
    def save_task(self, task: Task) -> bool:
        """
        保存任务
        
        Args:
            task: 任务对象
            
        Returns:
            是否成功
        """
        with self._cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO tasks 
                (id, name, prompt, status, priority, agent_name, created_at, 
                 started_at, completed_at, result, error, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                task.name,
                task.prompt,
                task.status.value,
                task.priority.value,
                task.assigned_agent,
                task.created_at.isoformat() if task.created_at else datetime.now().isoformat(),
                task.started_at.isoformat() if task.started_at else None,
                task.completed_at.isoformat() if task.completed_at else None,
                task.result,
                task.error,
                json.dumps(task.metadata) if task.metadata else None,
            ))
        return True
    
    def get_task(self, task_id: str) -> Optional[dict]:
        """获取任务"""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """
        列出任务
        
        Args:
            status: 按状态筛选
            limit: 返回数量限制
            offset: 偏移量
        """
        with self._cursor() as cursor:
            if status:
                cursor.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (status, limit, offset)
                )
            else:
                cursor.execute(
                    "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_task_status(self, task_id: str, status: str, **kwargs) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务 ID
            status: 新状态
            **kwargs: 其他字段
        """
        fields = ["status = ?"]
        values = [status]
        
        if "started_at" in kwargs:
            fields.append("started_at = ?")
            values.append(kwargs["started_at"])
        if "completed_at" in kwargs:
            fields.append("completed_at = ?")
            values.append(kwargs["completed_at"])
        if "result" in kwargs:
            fields.append("result = ?")
            values.append(kwargs["result"])
        if "error" in kwargs:
            fields.append("error = ?")
            values.append(kwargs["error"])
        if "agent_name" in kwargs:
            fields.append("agent_name = ?")
            values.append(kwargs["agent_name"])
        
        values.append(task_id)
        
        with self._cursor() as cursor:
            cursor.execute(
                f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        with self._cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0
    
    # ===== 技能操作 =====
    
    def save_skill(self, name: str, info: dict) -> bool:
        """
        保存技能信息
        
        Args:
            name: 技能名称
            info: 技能信息字典
        """
        with self._cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO skills
                (name, version, description, author, tags, triggers, 
                 installed_at, last_used, use_count, path, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                info.get("version", "0.0.0"),
                info.get("description", ""),
                info.get("author"),
                json.dumps(info.get("tags", [])),
                json.dumps(info.get("triggers", [])),
                info.get("installed_at", datetime.now().isoformat()),
                info.get("last_used"),
                info.get("use_count", 0),
                info.get("path", ""),
                info.get("source", "local"),
            ))
        return True
    
    def get_skill(self, name: str) -> Optional[dict]:
        """获取技能信息"""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM skills WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                # 解析 JSON 字段
                if d.get("tags"):
                    d["tags"] = json.loads(d["tags"])
                if d.get("triggers"):
                    d["triggers"] = json.loads(d["triggers"])
                return d
            return None
    
    def list_skills(self) -> list[dict]:
        """列出所有技能"""
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM skills ORDER BY installed_at DESC")
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                if d.get("tags"):
                    d["tags"] = json.loads(d["tags"])
                if d.get("triggers"):
                    d["triggers"] = json.loads(d["triggers"])
                results.append(d)
            return results
    
    def update_skill_usage(self, name: str) -> bool:
        """更新技能使用统计"""
        with self._cursor() as cursor:
            cursor.execute("""
                UPDATE skills 
                SET last_used = ?, use_count = use_count + 1 
                WHERE name = ?
            """, (datetime.now().isoformat(), name))
            return cursor.rowcount > 0
    
    def delete_skill(self, name: str) -> bool:
        """删除技能"""
        with self._cursor() as cursor:
            cursor.execute("DELETE FROM skills WHERE name = ?", (name,))
            return cursor.rowcount > 0
    
    # ===== 执行历史 =====
    
    def save_execution(self, task_id: str, agent_name: str, result: TaskResult) -> bool:
        """
        保存执行记录
        
        Args:
            task_id: 任务 ID
            agent_name: Agent 名称
            result: 执行结果
        """
        with self._cursor() as cursor:
            cursor.execute("""
                INSERT INTO execution_history
                (task_id, agent_name, started_at, duration_seconds, success, result, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                agent_name,
                datetime.now().isoformat(),
                result.duration_seconds,
                1 if result.success else 0,
                result.result,
                result.error,
            ))
        return True
    
    def get_execution_history(
        self,
        task_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        获取执行历史
        
        Args:
            task_id: 按任务筛选
            agent_name: 按 Agent 筛选
            limit: 返回数量
        """
        conditions = []
        values = []
        
        if task_id:
            conditions.append("task_id = ?")
            values.append(task_id)
        if agent_name:
            conditions.append("agent_name = ?")
            values.append(agent_name)
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        with self._cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM execution_history WHERE {where} ORDER BY id DESC LIMIT ?",
                values + [limit]
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== 统计 =====
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        with self._cursor() as cursor:
            # 任务统计
            cursor.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
            task_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
            
            # 技能统计
            cursor.execute("SELECT COUNT(*) as total, SUM(use_count) as uses FROM skills")
            skill_row = cursor.fetchone()
            
            # 执行统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                    AVG(duration_seconds) as avg_duration
                FROM execution_history
            """)
            exec_row = cursor.fetchone()
            
            return {
                "tasks": {
                    "total": sum(task_stats.values()),
                    "pending": task_stats.get("pending", 0),
                    "running": task_stats.get("running", 0),
                    "completed": task_stats.get("completed", 0),
                    "failed": task_stats.get("failed", 0),
                },
                "skills": {
                    "total": skill_row["total"] or 0,
                    "total_uses": skill_row["uses"] or 0,
                },
                "executions": {
                    "total": exec_row["total"] or 0,
                    "success_rate": (
                        exec_row["successes"] / exec_row["total"] * 100
                        if exec_row["total"] and exec_row["total"] > 0 else 0
                    ),
                    "avg_duration": exec_row["avg_duration"] or 0,
                },
            }
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection
