# -*- coding: utf-8 -*-
"""
长期记忆管理 - Long-term Memory
L3 级别记忆存储
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from .levels import MemoryLevel, MemoryItem


@dataclass
class EntityMemory:
    """实体记忆 - 存储关于特定实体（如人、项目、公司）的长期信息"""
    entity_id: str
    entity_type: str  # person, project, company, skill, etc.
    name: str
    description: str = ""
    facts: list[dict] = field(default_factory=list)  # {"fact": "...", "source": "...", "confidence": 0.9}
    relationships: list[dict] = field(default_factory=list)  # {"related_to": "...", "type": "...", "strength": 0.8}
    metadata: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    access_count: int = 0
    importance: float = 0.5

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EntityMemory":
        return cls(**data)

    def add_fact(self, fact: str, source: str = "conversation", confidence: float = 1.0):
        """添加事实"""
        # 避免重复
        for existing in self.facts:
            if existing["fact"] == fact:
                existing["confidence"] = max(existing["confidence"], confidence)
                return
        self.facts.append({
            "fact": fact,
            "source": source,
            "confidence": confidence,
            "added_at": time.time(),
        })
        self.updated_at = time.time()

    def add_relationship(self, related_to: str, rel_type: str, strength: float = 0.5):
        """添加关联"""
        for existing in self.relationships:
            if existing["related_to"] == related_to:
                existing["strength"] = max(existing["strength"], strength)
                return
        self.relationships.append({
            "related_to": related_to,
            "type": rel_type,
            "strength": strength,
            "added_at": time.time(),
        })
        self.updated_at = time.time()

    def get_summary(self) -> str:
        """获取摘要"""
        lines = [f"# {self.name} ({self.entity_type})"]
        if self.description:
            lines.append(f"\n{self.description}")
        if self.facts:
            lines.append("\n## Facts")
            for fact in self.facts[:5]:
                lines.append(f"- {fact['fact']}")
        if self.relationships:
            lines.append("\n## Relationships")
            for rel in self.relationships[:5]:
                lines.append(f"- [{rel['type']}] {rel['related_to']}")
        return "\n".join(lines)


class LongTermMemory:
    """
    长期记忆管理器

    管理 L3 长期记忆 - 持久化存储重要实体和信息
    """

    def __init__(self, base_path: str = "~/.agenthub/memory/long-term"):
        self.base_path = Path(base_path).expanduser()
        self.entities_path = self.base_path / "entities"
        self.entities_path.mkdir(parents=True, exist_ok=True)

        self._entity_cache: dict[str, EntityMemory] = {}

    def _get_entity_path(self, entity_id: str) -> Path:
        return self.entities_path / f"{entity_id}.json"

    def create_entity(
        self,
        entity_type: str,
        name: str,
        description: str = "",
        metadata: dict = None,
    ) -> EntityMemory:
        """创建实体"""
        entity_id = f"{entity_type}_{name.lower().replace(' ', '_')}_{int(time.time() % 1000000)}"
        entity = EntityMemory(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            description=description,
            metadata=metadata or {},
        )
        self._save_entity(entity)
        return entity

    def get_entity(self, entity_id: str) -> Optional[EntityMemory]:
        """获取实体"""
        if entity_id in self._entity_cache:
            return self._entity_cache[entity_id]

        path = self._get_entity_path(entity_id)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                entity = EntityMemory.from_dict(json.load(f))
                entity.access_count += 1
                self._save_entity(entity)
                self._entity_cache[entity_id] = entity
                return entity
        return None

    def find_entity(self, name: str, entity_type: str = None) -> Optional[EntityMemory]:
        """查找实体"""
        pattern = f"{entity_type}_" if entity_type else ""
        name_slug = name.lower().replace(' ', '_')

        for entity_file in self.entities_path.glob(f"{pattern}*.json"):
            try:
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entity = EntityMemory.from_dict(json.load(f))
                    if entity.name.lower().replace(' ', '_') == name_slug:
                        return entity
            except Exception:
                continue
        return None

    def _save_entity(self, entity: EntityMemory):
        """保存实体"""
        path = self._get_entity_path(entity.entity_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(entity.to_dict(), f, ensure_ascii=False, indent=2)
        self._entity_cache[entity.entity_id] = entity

    def update_entity(self, entity_id: str, **kwargs) -> bool:
        """更新实体"""
        entity = self.get_entity(entity_id)
        if not entity:
            return False

        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        entity.updated_at = time.time()

        self._save_entity(entity)
        return True

    def add_fact_to_entity(self, entity_id: str, fact: str, source: str = "conversation", confidence: float = 1.0) -> bool:
        """向实体添加事实"""
        entity = self.get_entity(entity_id)
        if not entity:
            return False
        entity.add_fact(fact, source, confidence)
        self._save_entity(entity)
        return True

    def list_entities(self, entity_type: str = None, limit: int = 50) -> list[EntityMemory]:
        """列出实体"""
        entities = []
        pattern = f"{entity_type}_*.json" if entity_type else "*.json"

        for entity_file in sorted(
            self.entities_path.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]:
            try:
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entities.append(EntityMemory.from_dict(json.load(f)))
            except Exception:
                continue
        return entities

    def delete_entity(self, entity_id: str) -> bool:
        """删除实体"""
        path = self._get_entity_path(entity_id)
        if path.exists():
            path.unlink()
            if entity_id in self._entity_cache:
                del self._entity_cache[entity_id]
            return True
        return False

    def get_stats(self) -> dict:
        """获取统计"""
        entities = self.list_entities(limit=10000)
        by_type = {}
        for entity in entities:
            by_type[entity.entity_type] = by_type.get(entity.entity_type, 0) + 1
        return {
            "total": len(entities),
            "by_type": by_type,
        }

    def search(self, query: str, entity_type: str = None) -> list[EntityMemory]:
        """搜索实体"""
        results = []
        query_lower = query.lower()

        for entity in self.list_entities(entity_type=entity_type, limit=500):
            if query_lower in entity.name.lower():
                results.append(entity)
            elif query_lower in entity.description.lower():
                results.append(entity)
            elif any(query_lower in fact["fact"].lower() for fact in entity.facts):
                results.append(entity)

        results.sort(key=lambda e: e.access_count, reverse=True)
        return results[:20]
