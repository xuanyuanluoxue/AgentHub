# -*- coding: utf-8 -*-
"""
上下文提取器 - Context Extractor
从对话中自动提取关键信息并分配到记忆级别
"""

import re
import time
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from .levels import MemoryLevel, MemoryItem
from .short_term import ShortTermMemory
from .long_term import LongTermMemory


@dataclass
class ExtractedInfo:
    """提取的信息"""
    content: str
    category: str  # user_info, project, preference, fact, etc.
    confidence: float = 1.0
    suggested_level: MemoryLevel = MemoryLevel.L2_SHORT_TERM
    tags: list[str] = field(default_factory=list)


class ContextExtractor:
    """
    上下文提取器

    从对话中自动识别和提取关键信息
    支持用户信息、项目信息、偏好设置等自动提取
    """

    # 提取规则
    PATTERNS = {
        # 用户信息
        "user_name": [
            r"我叫(.+)",
            r"我是(.+)",
            r"我的名字是(.+)",
        ],
        "user_info": [
            r"我(.+)岁的",
            r"我在(.+)工作",
            r"我是(.+)专业的",
        ],
        # 项目信息
        "project": [
            r"我的项目叫(.+)",
            r"在做(.+)项目",
            r"项目是(.+)",
        ],
        # 偏好设置
        "preference": [
            r"我喜欢(.+)",
            r"我不喜欢(.+)",
            r"偏好(.+)",
        ],
        # 技能相关
        "skill": [
            r"会(.+)",
            r"擅长(.+)",
            r"用(.+)开发",
        ],
    }

    # 置信度关键词
    CONFIDENCE_HIGH = ["肯定", "确定", "绝对", "一定", "明确"]
    CONFIDENCE_LOW = ["大概", "可能", "应该", "好像", "估计"]

    def __init__(
        self,
        short_term: ShortTermMemory = None,
        long_term: LongTermMemory = None,
    ):
        self.short_term = short_term
        self.long_term = long_term

    def extract(self, text: str) -> list[ExtractedInfo]:
        """
        从文本中提取信息

        Args:
            text: 输入文本

        Returns:
            list[ExtractedInfo]: 提取的信息列表
        """
        results = []

        for category, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    content = match.group(1).strip()
                    confidence = self._calc_confidence(text)

                    suggested_level = self._suggest_level(category, content)

                    results.append(ExtractedInfo(
                        content=content,
                        category=category,
                        confidence=confidence,
                        suggested_level=suggested_level,
                        tags=[category],
                    ))

        return results

    def _calc_confidence(self, text: str) -> float:
        """计算置信度"""
        base = 0.7

        for keyword in self.CONFIDENCE_HIGH:
            if keyword in text:
                base = min(1.0, base + 0.2)

        for keyword in self.CONFIDENCE_LOW:
            if keyword in text:
                base = max(0.3, base - 0.2)

        return base

    def _suggest_level(self, category: str, content: str) -> MemoryLevel:
        """建议记忆级别"""
        if category == "user_name":
            return MemoryLevel.L3_LONG_TERM  # 名字是长期记忆
        elif category == "project":
            return MemoryLevel.L2_SHORT_TERM
        elif category == "preference":
            return MemoryLevel.L3_LONG_TERM  # 偏好是长期记忆
        elif category == "skill":
            return MemoryLevel.L3_LONG_TERM
        else:
            return MemoryLevel.L2_SHORT_TERM

    def process_conversation(self, role: str, content: str) -> list[ExtractedInfo]:
        """
        处理对话并提取信息

        Args:
            role: 角色 (user/assistant)
            content: 对话内容

        Returns:
            list[ExtractedInfo]: 提取的信息
        """
        if role != "user":
            return []

        extracted = self.extract(content)

        # 自动存储到短期记忆
        if self.short_term:
            for info in extracted:
                self.short_term.extract_to_working(
                    info.content,
                    importance=info.confidence,
                )

        return extracted

    def bulk_extract(self, conversations: list[dict]) -> list[ExtractedInfo]:
        """
        批量处理对话历史

        Args:
            conversations: [{"role": "user", "content": "..."}, ...]

        Returns:
            list[ExtractedInfo]: 所有提取的信息
        """
        all_results = []
        for conv in conversations:
            results = self.process_conversation(
                conv.get("role", "user"),
                conv.get("content", ""),
            )
            all_results.extend(results)

        return all_results
