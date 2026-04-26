# -*- coding: utf-8 -*-
"""
短期记忆管理 - Short-term Memory
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from .levels import MemoryLevel, MemoryItem


@dataclass
class SessionMemory:
    """会话记忆 - 对应 L0/L1 级别"""
    session_id: str
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    context: list[dict] = field(default_factory=list)  # 对话历史
    extracted_facts: list[str] = field(default_factory=list)  # 提取的事实
    working_memory: list[str] = field(default_factory=list)  # 工作记忆
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SessionMemory":
        return cls(**data)

    def add_turn(self, role: str, content: str):
        """添加对话轮次"""
        self.context.append({
            "role": role,
            "content": content,
            "timestamp": time.time(),
        })
        self.last_accessed = time.time()

    def extract_fact(self, fact: str):
        """提取事实到工作记忆"""
        if fact not in self.working_memory:
            self.working_memory.append(fact)

    def get_context_summary(self, max_turns: int = 10) -> str:
        """获取上下文摘要"""
        recent = self.context[-max_turns:] if self.context else []
        return "\n".join([f"{t['role']}: {t['content'][:100]}..." for t in recent])


class ShortTermMemory:
    """
    短期记忆管理器

    管理 L0（瞬时）和 L1（工作）记忆
    基于会话的上下文管理和事实提取
    """

    def __init__(self, base_path: str = "~/.agenthub/memory/short-term"):
        self.base_path = Path(base_path).expanduser()
        self.sessions_path = self.base_path / "sessions"
        self.sessions_path.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[SessionMemory] = None
        self.current_session_id: Optional[str] = None

    def create_session(self, session_id: str = None) -> SessionMemory:
        """创建新会话"""
        if session_id is None:
            session_id = f"session_{int(time.time() * 1000)}"

        session = SessionMemory(session_id=session_id)
        self._save_session(session)

        self.current_session = session
        self.current_session_id = session_id
        return session

    def load_session(self, session_id: str) -> Optional[SessionMemory]:
        """加载会话"""
        session_file = self.sessions_path / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.current_session = SessionMemory.from_dict(data)
                self.current_session_id = session_id
                return self.current_session
        return None

    def save_session(self):
        """保存当前会话"""
        if self.current_session:
            self._save_session(self.current_session)

    def _save_session(self, session: SessionMemory):
        """保存会话到文件"""
        session_file = self.sessions_path / f"{session.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)

    def add_turn(self, role: str, content: str):
        """添加对话轮次"""
        if not self.current_session:
            self.create_session()
        self.current_session.add_turn(role, content)
        self.save_session()

    def extract_to_working(self, fact: str, importance: float = 0.5):
        """提取事实到工作记忆"""
        if not self.current_session:
            self.create_session()
        self.current_session.extract_fact(fact)
        self.save_session()

    def get_or_create_session(self, session_id: str = None) -> SessionMemory:
        """获取或创建会话"""
        if session_id and self.load_session(session_id):
            return self.current_session
        return self.create_session(session_id)

    def list_sessions(self, limit: int = 20) -> list[dict]:
        """列出最近会话"""
        sessions = []
        for session_file in sorted(
            self.sessions_path.glob("session_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data["session_id"],
                        "created_at": data["created_at"],
                        "last_accessed": data["last_accessed"],
                        "turn_count": len(data.get("context", [])),
                        "fact_count": len(data.get("working_memory", [])),
                    })
            except Exception:
                continue
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        session_file = self.sessions_path / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            if self.current_session_id == session_id:
                self.current_session = None
                self.current_session_id = None
            return True
        return False

    def cleanup_old_sessions(self, days: int = 7) -> int:
        """清理旧会话"""
        cutoff = time.time() - (days * 86400)
        cleaned = 0

        for session_file in self.sessions_path.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if data["last_accessed"] < cutoff:
                    session_file.unlink()
                    cleaned += 1
            except Exception:
                continue

        return cleaned
