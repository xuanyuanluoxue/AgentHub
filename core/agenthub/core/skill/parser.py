# -*- coding: utf-8 -*-
"""
Skill 解析器 - 解析 SKILL.md 文件

支持两种格式：
1. AgentHub 格式：顶级字段 (name, version, description, trigger)
2. ClawHub 格式：metadata 嵌套字段
"""

import re
import yaml
from pathlib import Path
from typing import Optional
from agenthub.core.skill.models import SkillMetadata


class SkillParseError(Exception):
    """解析错误"""
    pass


class SkillParser:
    """
    SKILL.md 解析器

    解析 Skill 的 YAML frontmatter 和 Markdown 正文
    """

    FRONTMATTER_PATTERN = re.compile(
        r'^---\s*\n(.*?)\n---\s*\n(.*)$',
        re.DOTALL | re.MULTILINE
    )

    @classmethod
    def parse_file(cls, path: str | Path) -> SkillMetadata:
        """
        解析 SKILL.md 文件

        Args:
            path: SKILL.md 文件路径

        Returns:
            SkillMetadata 对象

        Raises:
            SkillParseError: 解析失败
        """
        path = Path(path)

        if not path.exists():
            raise SkillParseError(f"文件不存在: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return cls.parse_content(content, base_path=str(path.parent))

    @classmethod
    def parse_content(cls, content: str, base_path: Optional[str] = None) -> SkillMetadata:
        """
        解析 SKILL.md 内容

        Args:
            content: SKILL.md 文件内容
            base_path: 基础路径（用于设置 path 字段）

        Returns:
            SkillMetadata 对象
        """
        # 提取 frontmatter
        match = cls.FRONTMATTER_PATTERN.match(content.strip())

        if not match:
            raise SkillParseError(
                "无法解析 YAML frontmatter，"
                "确保文件以 --- 开头和结尾"
            )

        frontmatter_text = match.group(1)
        markdown_body = match.group(2).strip()

        # 解析 YAML
        try:
            # 使用 safe_load 避免执行任意代码
            data = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            raise SkillParseError(f"YAML 解析失败: {e}")

        if data is None:
            raise SkillParseError("YAML frontmatter 为空")

        if not isinstance(data, dict):
            raise SkillParseError(f"YAML 应为字典类型，得到: {type(data)}")

        # 处理 ClawHub 格式 (metadata 嵌套)
        data = cls._normalize_metadata(data)

        # 提取必需字段
        required_fields = ['name', 'version', 'description', 'trigger']
        for field in required_fields:
            if field not in data:
                raise SkillParseError(f"缺少必需字段: {field}")

        # 构建 SkillMetadata
        metadata = SkillMetadata(
            name=data.pop('name'),
            version=data.pop('version'),
            description=data.pop('description'),
            trigger=data.pop('trigger'),
            content=markdown_body,
            path=base_path,
            **{k: v for k, v in data.items() if v is not None}
        )

        return metadata

    @classmethod
    def _normalize_metadata(cls, data: dict) -> dict:
        """
        规范化元数据，支持 ClawHub 格式

        ClawHub 格式示例:
        ---
        name: hello-world
        triggers:
          - "hello"
        metadata:
          version: "1.0.0"
          category: productivity
        ---

        转换为:
        ---
        name: hello-world
        triggers: ["hello"]
        version: "1.0.0"
        category: productivity
        ---
        """
        # 如果有 metadata 嵌套，提取到顶级
        if 'metadata' in data and isinstance(data['metadata'], dict):
            metadata = data.pop('metadata')
            for key, value in metadata.items():
                # 只填充顶级不存在的字段
                if key not in data:
                    data[key] = value

        # 兼容 ClawHub 的 triggers（复数）vs AgentHub 的 trigger（单数）
        if 'triggers' in data and 'trigger' not in data:
            data['trigger'] = data.pop('triggers')

        # 处理 trigger/triggers 可能是字符串的情况
        if 'trigger' in data:
            if isinstance(data['trigger'], str):
                data['trigger'] = [data['trigger']]
            # 如果是空数组，设为默认空数组（后续可设置默认值）
            if not data['trigger']:
                data['trigger'] = []

        return data
    
    @classmethod
    def parse_directory(cls, dir_path: str | Path) -> SkillMetadata:
        """
        解析 Skill 目录（自动查找 SKILL.md）
        
        Args:
            dir_path: Skill 根目录
            
        Returns:
            SkillMetadata 对象
        """
        dir_path = Path(dir_path)
        skill_md = dir_path / "SKILL.md"
        
        if not skill_md.exists():
            raise SkillParseError(f"目录中不存在 SKILL.md: {dir_path}")
        
        return cls.parse_file(skill_md)
    
    @classmethod
    def validate_skill_dir(cls, dir_path: str | Path) -> tuple[bool, list[str]]:
        """
        验证 Skill 目录结构
        
        Args:
            dir_path: Skill 根目录
            
        Returns:
            (is_valid, errors)
        """
        errors = []
        dir_path = Path(dir_path)
        
        # 检查 SKILL.md
        skill_md = dir_path / "SKILL.md"
        if not skill_md.exists():
            errors.append("缺少 SKILL.md")
            return (False, errors)
        
        # 解析并验证元数据
        try:
            metadata = cls.parse_file(skill_md)
            is_valid, meta_errors = metadata.validate()
            errors.extend(meta_errors)
        except SkillParseError as e:
            errors.append(str(e))
            return (False, errors)
        
        return (len(errors) == 0, errors)
    
    @classmethod
    def write_skill_md(
        cls, 
        path: str | Path,
        metadata: SkillMetadata,
        include_content: bool = True
    ) -> None:
        """
        写入 SKILL.md 文件
        
        Args:
            path: 输出路径
            metadata: Skill 元数据
            include_content: 是否包含正文
        """
        path = Path(path)
        
        # 构建 frontmatter
        frontmatter = {
            'name': metadata.name,
            'version': metadata.version,
            'description': metadata.description,
            'trigger': metadata.trigger,
        }
        
        # 添加可选字段
        optional_fields = [
            'author', 'tags', 'category', 'dependencies',
            'tools', 'platform', 'license', 'homepage', 'source'
        ]
        for field in optional_fields:
            value = getattr(metadata, field, None)
            if value:
                frontmatter[field] = value
        
        # 序列化为 YAML
        yaml_text = yaml.dump(
            frontmatter,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )
        
        # 组装完整内容
        lines = ['---', yaml_text.rstrip(), '---']
        
        if include_content and metadata.content:
            lines.extend(['', metadata.content])
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
