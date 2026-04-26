# -*- coding: utf-8 -*-
"""
记忆检索器 - Memory Retrieval
支持自然语言查询的记忆检索
"""

import re
import json
from pathlib import Path
from typing import Optional, Any
from .levels import MemoryLevel, MemoryItem, MemoryEngine
from .long_term import LongTermMemory
from .knowledge import KnowledgeGraph


class MemoryRetrieval:
    """
    记忆检索器

    支持：
    - 关键词检索
    - 自然语言查询
    - 图关系查询
    - 时间范围查询
    """

    def __init__(
        self,
        memory_engine: MemoryEngine = None,
        long_term: LongTermMemory = None,
        knowledge_graph: KnowledgeGraph = None,
    ):
        self.engine = memory_engine
        self.long_term = long_term
        self.knowledge_graph = knowledge_graph

    def retrieve(
        self,
        query: str,
        level: MemoryLevel = None,
        tags: list[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        检索记忆

        Args:
            query: 查询内容
            level: 限定级别
            tags: 限定标签
            limit: 返回数量

        Returns:
            list[dict]: 检索结果
        """
        results = []

        # 1. 关键词检索
        if self.engine:
            items = self.engine.search(query, level=level, tags=tags, limit=limit)
            for item in items:
                results.append({
                    "type": "memory",
                    "level": f"L{item.level}",
                    "content": item.content,
                    "importance": item.importance,
                    "tags": item.tags,
                    "source": item.source,
                    "created_at": item.created_at,
                })

        # 2. 实体检索
        if self.long_term:
            entities = self.long_term.search(query)
            for entity in entities:
                results.append({
                    "type": "entity",
                    "entity_type": entity.entity_type,
                    "name": entity.name,
                    "description": entity.description,
                    "facts": entity.facts,
                    "relationships": entity.relationships,
                })

        return results

    def retrieve_with_context(
        self,
        query: str,
        max_context_size: int = 5,
    ) -> str:
        """
        检索记忆并生成上下文字符串

        Args:
            query: 查询内容
            max_context_size: 最大上下文条目数

        Returns:
            str: 格式化的上下文字符串
        """
        results = self.retrieve(query, limit=max_context_size)

        if not results:
            return ""

        lines = ["## 相关记忆"]
        for i, result in enumerate(results, 1):
            if result["type"] == "memory":
                lines.append(f"\n### {result['level']} - {result.get('source', 'unknown')}")
                lines.append(result["content"])
            elif result["type"] == "entity":
                lines.append(f"\n### 实体: {result['name']} ({result['entity_type']})")
                lines.append(result.get("description", ""))
                if result.get("facts"):
                    lines.append("**Facts:**")
                    for fact in result["facts"][:3]:
                        lines.append(f"- {fact['fact']}")

        return "\n".join(lines)

    def retrieve_related(
        self,
        entity_name: str,
        max_depth: int = 2,
    ) -> dict:
        """
        检索相关实体和关系

        Args:
            entity_name: 实体名称
            max_depth: 最大深度

        Returns:
            dict: 相关实体和关系
        """
        if not self.knowledge_graph:
            return {}

        node = self.knowledge_graph.find_node(entity_name)
        if not node:
            return {}

        # 图遍历
        visited = self.knowledge_graph.traverse(node.id, max_depth=max_depth)

        related = []
        for neighbor_id, depth in visited.items():
            if neighbor_id == node.id:
                continue
            neighbor_node = self.knowledge_graph.get_node(neighbor_id)
            if neighbor_node:
                edges = self.knowledge_graph.get_edges_from(neighbor_id)
                related.append({
                    "node": neighbor_node,
                    "depth": depth,
                    "relations": [e.relation for e in edges if e.target == node.id],
                })

        return {
            "center": node,
            "related": related,
        }
