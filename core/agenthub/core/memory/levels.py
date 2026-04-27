# -*- coding: utf-8 -*-
"""
多级记忆引擎 - AgentHub Memory System
L0-L4 五级记忆体系实现
"""

import time
import json
from enum import IntEnum
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from pathlib import Path


class MemoryLevel(IntEnum):
    """记忆级别枚举"""
    L0_INSTANT = 0  # 瞬时记忆：单次回复，Token 缓存
    L1_WORKING = 1  # 工作记忆：会话内，@记住 触发
    L2_SHORT_TERM = 2  # 短期记忆：1-7天，多次提及/重要事件
    L3_LONG_TERM = 3  # 长期记忆：永久，反复验证/用户确认
    L4_KNOWLEDGE = 4  # 知识图谱：永久，实体关系推理


@dataclass
class MemoryItem:
    """记忆条目"""
    id: str
    content: str
    level: int
    importance: float = 0.5  # 0.0-1.0 重要性评分
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    source: str = ""  # 来源：conversation, manual, extracted
    ttl: Optional[int] = None  # 生存时间（秒），None=永久

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryItem":
        return cls(**data)

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def access(self):
        """记录访问"""
        self.access_count += 1
        self.last_accessed = time.time()


class MemoryLevelConfig:
    """记忆级别配置"""

    CONFIG = {
        MemoryLevel.L0_INSTANT: {
            "name": "瞬时记忆",
            "ttl": 300,  # 5 分钟
            "max_items": 100,
            "upgrade_threshold": 0.0,  # L0 不会自动升级
            "auto_decay": True,
        },
        MemoryLevel.L1_WORKING: {
            "name": "工作记忆",
            "ttl": 3600,  # 1 小时
            "max_items": 50,
            "upgrade_threshold": 3,  # 访问 3 次以上可考虑升级
            "auto_decay": True,
        },
        MemoryLevel.L2_SHORT_TERM: {
            "name": "短期记忆",
            "ttl": 604800,  # 7 天
            "max_items": 200,
            "upgrade_threshold": 5,  # 访问 5 次以上
            "auto_decay": True,
        },
        MemoryLevel.L3_LONG_TERM: {
            "name": "长期记忆",
            "ttl": None,  # 永久
            "max_items": 1000,
            "upgrade_threshold": 10,  # 访问 10 次以上
            "auto_decay": False,
        },
        MemoryLevel.L4_KNOWLEDGE: {
            "name": "知识图谱",
            "ttl": None,  # 永久
            "max_items": 5000,
            "upgrade_threshold": 20,  # 需明确标记为知识
            "auto_decay": False,
        },
    }

    @classmethod
    def get_config(cls, level: MemoryLevel) -> dict:
        return cls.CONFIG[level]

    @classmethod
    def get_ttl(cls, level: MemoryLevel) -> Optional[int]:
        return cls.CONFIG[level]["ttl"]


class MemoryEngine:
    """
    多级记忆引擎核心类

    使用示例:
        engine = MemoryEngine("~/.agenthub/memory")
        engine.add("用户叫用户名", level=MemoryLevel.L1_WORKING, tags=["用户信息"])
        items = engine.search("用户名字")
        engine.cleanup()  # 清理过期记忆
    """

    def __init__(self, base_path: str = "~/.agenthub/memory"):
        self.base_path = Path(base_path).expanduser()
        self.levels = {}

        # 初始化各层级目录
        for level in MemoryLevel:
            level_path = self.base_path / f"L{level.value}_{level.name.lower().replace('_','_')}"
            level_path.mkdir(parents=True, exist_ok=True)
            self.levels[level] = level_path

        self._index_file = self.base_path / "_index" / "memory_index.json"
        self._index_file.parent.mkdir(parents=True, exist_ok=True)
        self._index = self._load_index()

    def _load_index(self) -> dict:
        """加载索引"""
        if self._index_file.exists():
            with open(self._index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_index(self):
        """保存索引"""
        with open(self._index_file, 'w', encoding='utf-8') as f:
            json.dump(self._index, f, ensure_ascii=False, indent=2)

    def _get_storage_path(self, item_id: str, level: MemoryLevel) -> Path:
        """获取存储路径"""
        return self.levels[level] / f"{item_id}.json"

    def add(
        self,
        content: str,
        level: MemoryLevel = MemoryLevel.L1_WORKING,
        importance: float = 0.5,
        tags: list[str] = None,
        metadata: dict = None,
        source: str = "manual",
        ttl: int = None,
    ) -> MemoryItem:
        """
        添加记忆

        Args:
            content: 记忆内容
            level: 记忆级别
            importance: 重要性 (0.0-1.0)
            tags: 标签
            metadata: 元数据
            source: 来源
            ttl: 生存时间（秒）

        Returns:
            MemoryItem: 创建的记忆条目
        """
        item_id = f"{int(time.time() * 1000)}_{hash(content) % 100000:05d}"
        item = MemoryItem(
            id=item_id,
            content=content,
            level=level.value,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            source=source,
            ttl=ttl or MemoryLevelConfig.get_ttl(level),
        )

        # 保存到文件
        path = self._get_storage_path(item_id, MemoryLevel(level))
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)

        # 更新索引
        self._index[item_id] = {
            "level": level.value,
            "path": str(path),
            "tags": item.tags,
            "importance": importance,
        }
        self._save_index()

        return item

    def get(self, item_id: str) -> Optional[MemoryItem]:
        """获取单条记忆"""
        for level in MemoryLevel:
            path = self._get_storage_path(item_id, level)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    item = MemoryItem.from_dict(data)
                    item.access()
                    self._save_item(item)
                    return item
        return None

    def search(
        self,
        query: str,
        level: MemoryLevel = None,
        tags: list[str] = None,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """
        搜索记忆

        Args:
            query: 搜索关键词
            level: 限定级别，None=全部
            tags: 限定标签
            limit: 返回数量

        Returns:
            list[MemoryItem]: 匹配的记忆列表
        """
        results = []
        query_lower = query.lower()

        search_levels = [level] if level else list(MemoryLevel)

        for lvl in search_levels:
            level_path = self.levels[lvl]
            if not level_path.exists():
                continue

            for item_file in level_path.glob("*.json"):
                try:
                    with open(item_file, 'r', encoding='utf-8') as f:
                        item = MemoryItem.from_dict(json.load(f))

                    # 检查过期
                    if item.is_expired():
                        continue

                    # 检查标签过滤
                    if tags and not any(tag in item.tags for tag in tags):
                        continue

                    # 简单关键词匹配
                    if query_lower in item.content.lower():
                        results.append(item)

                except Exception:
                    continue

        # 按相关性排序
        results.sort(key=lambda x: (x.importance, x.access_count), reverse=True)
        return results[:limit]

    def upgrade(self, item_id: str, target_level: MemoryLevel = None) -> bool:
        """
        升级记忆到更高级别

        Args:
            item_id: 记忆 ID
            target_level: 目标级别，None=自动判断

        Returns:
            bool: 是否成功
        """
        item = self.get(item_id)
        if not item:
            return False

        current_level = MemoryLevel(item.level)

        if target_level is None:
            # 自动判断：基于访问次数
            if item.access_count >= 20:
                target_level = MemoryLevel.L4_KNOWLEDGE
            elif item.access_count >= 10:
                target_level = MemoryLevel.L3_LONG_TERM
            elif item.access_count >= 5:
                target_level = MemoryLevel.L2_SHORT_TERM
            else:
                return False

        if target_level.value <= current_level.value:
            return False

        # 从原级别删除
        old_path = self._get_storage_path(item_id, current_level)
        if old_path.exists():
            old_path.unlink()

        # 更新级别并移动
        item.level = target_level.value
        item.updated_at = time.time()

        new_path = self._get_storage_path(item_id, target_level)
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)

        # 更新索引
        self._index[item_id]["level"] = target_level.value
        self._index[item_id]["path"] = str(new_path)
        self._save_index()

        return True

    def downgrade(self, item_id: str, target_level: MemoryLevel = None) -> bool:
        """降级记忆"""
        item = self.get(item_id)
        if not item:
            return False

        current_level = MemoryLevel(item.level)

        if target_level is None:
            # 自动降级：基于时间衰减
            if item.is_expired():
                if current_level == MemoryLevel.L2_SHORT_TERM:
                    target_level = MemoryLevel.L1_WORKING
                elif current_level == MemoryLevel.L1_WORKING:
                    target_level = MemoryLevel.L0_INSTANT
                else:
                    target_level = MemoryLevel(current_level.value - 1) if current_level.value > 0 else MemoryLevel.L0_INSTANT
            else:
                return False

        if target_level.value >= current_level.value:
            return False

        # 移动到新级别
        old_path = self._get_storage_path(item_id, current_level)
        if old_path.exists():
            old_path.unlink()

        item.level = target_level.value
        item.updated_at = time.time()

        new_path = self._get_storage_path(item_id, target_level)
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)

        self._index[item_id]["level"] = target_level.value
        self._index[item_id]["path"] = str(new_path)
        self._save_index()

        return True

    def delete(self, item_id: str) -> bool:
        """删除记忆"""
        for level in MemoryLevel:
            path = self._get_storage_path(item_id, level)
            if path.exists():
                path.unlink()
                if item_id in self._index:
                    del self._index[item_id]
                self._save_index()
                return True
        return False

    def cleanup(self) -> int:
        """
        清理过期记忆

        Returns:
            int: 清理的记忆数量
        """
        cleaned = 0
        for level in MemoryLevel:
            level_path = self.levels[level]
            if not level_path.exists():
                continue

            for item_file in level_path.glob("*.json"):
                try:
                    with open(item_file, 'r', encoding='utf-8') as f:
                        item = MemoryItem.from_dict(json.load(f))

                    if item.is_expired():
                        item_file.unlink()
                        if item.id in self._index:
                            del self._index[item.id]
                        cleaned += 1

                except Exception:
                    continue

        self._save_index()
        return cleaned

    def _save_item(self, item: MemoryItem):
        """保存单条记忆"""
        path = self._get_storage_path(item.id, MemoryLevel(item.level))
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)

    def get_stats(self) -> dict:
        """获取记忆统计"""
        stats = {}
        for level in MemoryLevel:
            level_path = self.levels[level]
            count = len(list(level_path.glob("*.json"))) if level_path.exists() else 0
            stats[f"L{level.value}_{level.name.lower()}"] = {
                "count": count,
                "name": MemoryLevelConfig.get_config(level)["name"],
                "ttl": MemoryLevelConfig.get_config(level)["ttl"],
            }
        return stats

    def export_all(self) -> list[dict]:
        """导出所有记忆为列表"""
        all_items = []
        for level in MemoryLevel:
            level_path = self.levels[level]
            if not level_path.exists():
                continue

            for item_file in level_path.glob("*.json"):
                try:
                    with open(item_file, 'r', encoding='utf-8') as f:
                        all_items.append(json.load(f))
                except Exception:
                    continue

        return all_items


if __name__ == "__main__":
    # 测试
    engine = MemoryEngine("~/.agenthub/test_memory")
    engine.add("用户叫用户名", level=MemoryLevel.L2_SHORT_TERM, tags=["用户信息"])
    engine.add("用户的项目叫 AgentHub", level=MemoryLevel.L2_SHORT_TERM, tags=["项目"])
    print(engine.get_stats())
    print(engine.search("用户名"))
