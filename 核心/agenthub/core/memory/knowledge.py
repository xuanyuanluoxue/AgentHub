# -*- coding: utf-8 -*-
"""
知识图谱 - Knowledge Graph
L4 级别记忆 - 实体关系网络
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from enum import Enum


class RelationType(Enum):
    """关系类型枚举"""
    IS_A = "is_a"           # 实体类型
    PART_OF = "part_of"     # 组成关系
    WORKS_ON = "works_on"   # 工作关系
    KNOWS = "knows"         # 认识关系
    USES = "uses"           # 使用关系
    CREATED = "created"     # 创建关系
    SIMILAR = "similar"     # 相似关系
    CONTRACTS = "contracts" # 对立关系


@dataclass
class KGNode:
    """知识图谱节点"""
    id: str
    label: str
    node_type: str  # person, project, skill, concept, tool, etc.
    properties: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    access_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "KGNode":
        return cls(**data)


@dataclass
class KGEdge:
    """知识图谱边"""
    id: str
    source: str  # 源节点 ID
    target: str  # 目标节点 ID
    relation: str  # 关系类型
    properties: dict = field(default_factory=dict)
    weight: float = 1.0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "KGEdge":
        return cls(**data)


class KnowledgeGraph:
    """
    知识图谱管理器

    管理 L4 知识图谱 - 实体关系网络
    支持实体识别、关系推理、图遍历
    """

    def __init__(self, base_path: str = "~/.agenthub/memory/knowledge"):
        self.base_path = Path(base_path).expanduser()
        self.nodes_path = self.base_path / "nodes"
        self.edges_path = self.base_path / "edges"
        self.nodes_path.mkdir(parents=True, exist_ok=True)
        self.edges_path.mkdir(parents=True, exist_ok=True)

    def _get_node_path(self, node_id: str) -> Path:
        return self.nodes_path / f"{node_id}.json"

    def _get_edge_path(self, edge_id: str) -> Path:
        return self.edges_path / f"{edge_id}.json"

    def add_node(
        self,
        label: str,
        node_type: str,
        properties: dict = None,
    ) -> KGNode:
        """添加节点"""
        node_id = f"{node_type}_{label.lower().replace(' ', '_')}"
        node = KGNode(
            id=node_id,
            label=label,
            node_type=node_type,
            properties=properties or {},
        )
        self._save_node(node)
        return node

    def _save_node(self, node: KGNode):
        path = self._get_node_path(node.id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(node.to_dict(), f, ensure_ascii=False, indent=2)

    def get_node(self, node_id: str) -> Optional[KGNode]:
        path = self._get_node_path(node_id)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return KGNode.from_dict(json.load(f))
        return None

    def find_node(self, label: str, node_type: str = None) -> Optional[KGNode]:
        """查找节点"""
        pattern = f"{node_type}_*.json" if node_type else "*.json"
        label_slug = label.lower().replace(' ', '_')

        for node_file in self.nodes_path.glob(pattern):
            try:
                with open(node_file, 'r', encoding='utf-8') as f:
                    node = KGNode.from_dict(json.load(f))
                    if node.label.lower().replace(' ', '_') == label_slug:
                        return node
            except Exception:
                continue
        return None

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        weight: float = 1.0,
        properties: dict = None,
    ) -> Optional[KGEdge]:
        """添加边"""
        # 确保节点存在
        if not self.get_node(source_id) or not self.get_node(target_id):
            return None

        edge_id = f"{source_id}_{relation}_{target_id}"
        edge = KGEdge(
            id=edge_id,
            source=source_id,
            target=target_id,
            relation=relation,
            weight=weight,
            properties=properties or {},
        )

        path = self._get_edge_path(edge_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(edge.to_dict(), f, ensure_ascii=False, indent=2)

        return edge

    def get_edges_from(self, node_id: str) -> list[KGEdge]:
        """获取从某节点出发的所有边"""
        edges = []
        for edge_file in self.edges_path.glob(f"{node_id}_*.json"):
            try:
                with open(edge_file, 'r', encoding='utf-8') as f:
                    edges.append(KGEdge.from_dict(json.load(f)))
            except Exception:
                continue
        return edges

    def get_neighbors(self, node_id: str, relation: str = None) -> list[tuple[KGNode, KGEdge]]:
        """获取邻居节点"""
        neighbors = []
        for edge in self.get_edges_from(node_id):
            if relation and edge.relation != relation:
                continue
            target_node = self.get_node(edge.target)
            if target_node:
                neighbors.append((target_node, edge))
        return neighbors

    def traverse(self, start_id: str, max_depth: int = 2) -> dict:
        """图遍历 - BFS"""
        visited = {start_id: 0}
        queue = [start_id]

        while queue:
            current = queue.pop(0)
            if visited[current] >= max_depth:
                continue

            for node, edge in self.get_neighbors(current):
                if node.id not in visited:
                    visited[node.id] = visited[current] + 1
                    queue.append(node.id)

        return visited

    def get_stats(self) -> dict:
        """获取图统计"""
        node_count = len(list(self.nodes_path.glob("*.json")))
        edge_count = len(list(self.edges_path.glob("*.json")))

        node_types = {}
        for node_file in self.nodes_path.glob("*.json"):
            try:
                with open(node_file, 'r', encoding='utf-8') as f:
                    node = KGNode.from_dict(json.load(f))
                    node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
            except Exception:
                continue

        return {
            "nodes": node_count,
            "edges": edge_count,
            "node_types": node_types,
        }

    def delete_node(self, node_id: str) -> bool:
        """删除节点及其所有边"""
        node_path = self._get_node_path(node_id)
        if node_path.exists():
            node_path.unlink()

            # 删除相关边
            for edge_file in self.edges_path.glob(f"{node_id}_*.json"):
                edge_file.unlink()
            for edge_file in self.edges_path.glob(f"*_{node_id}"):
                edge_file.unlink()
            return True
        return False

    def export_graph(self) -> dict:
        """导出完整图"""
        nodes = []
        for node_file in self.nodes_path.glob("*.json"):
            try:
                with open(node_file, 'r', encoding='utf-8') as f:
                    nodes.append(json.load(f))
            except Exception:
                continue

        edges = []
        for edge_file in self.edges_path.glob("*.json"):
            try:
                with open(edge_file, 'r', encoding='utf-8') as f:
                    edges.append(json.load(f))
            except Exception:
                continue

        return {"nodes": nodes, "edges": edges}
