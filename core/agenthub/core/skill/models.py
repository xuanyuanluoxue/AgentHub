# -*- coding: utf-8 -*-
"""
Skill 数据模型
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re


class SkillCategory(Enum):
    """Skill 分类"""
    DEV = "dev"
    PRODUCTIVITY = "productivity"
    AI = "ai"
    SYSTEM = "system"


class Platform(Enum):
    """支持平台"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    ALL = "all"


@dataclass
class SkillMetadata:
    """
    Skill 元数据
    
    对应 SKILL.md 的 YAML frontmatter
    """
    name: str
    version: str
    description: str
    trigger: list[str]
    
    # 可选字段
    author: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    category: Optional[SkillCategory] = None
    dependencies: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    platform: Platform = Platform.ALL
    license: Optional[str] = None
    homepage: Optional[str] = None
    source: Optional[str] = None
    
    # 正文（Markdown）
    content: str = ""
    
    # 解析后的附加信息
    path: Optional[str] = None  # Skill 所在目录
    installed_at: Optional[str] = None  # 安装时间
    source_type: str = "local"  # local / registry / git
    
    def __post_init__(self):
        """类型转换"""
        if isinstance(self.category, str):
            try:
                self.category = SkillCategory(self.category)
            except ValueError:
                self.category = None
        
        if isinstance(self.platform, str):
            try:
                self.platform = Platform(self.platform)
            except ValueError:
                self.platform = Platform.ALL
    
    @property
    def version_tuple(self) -> tuple:
        """版本号元组，用于比较"""
        return tuple(int(x) for x in self.version.lstrip('v').split('.')[:3])
    
    def matches_trigger(self, text: str) -> bool:
        """检查文本是否匹配触发词"""
        text_lower = text.lower()
        for trigger in self.trigger:
            if trigger.lower() in text_lower:
                return True
        return False
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        验证元数据是否合法
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # name: 非空，kebab-case
        if not self.name:
            errors.append("name 不能为空")
        elif not re.match(r'^[a-z0-9][a-z0-9-]*$', self.name):
            errors.append(f"name 格式错误：{self.name}，应为 kebab-case")
        
        # version: SemVer 格式
        if not re.match(r'^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$', self.version):
            errors.append(f"version 格式错误：{self.version}，应为 SemVer")
        
        # description: 非空
        if not self.description:
            errors.append("description 不能为空")
        
        # trigger: 非空
        if not self.trigger:
            errors.append("trigger 不能为空")
        
        return (len(errors) == 0, errors)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "trigger": self.trigger,
            "author": self.author,
            "tags": self.tags,
            "category": self.category.value if self.category else None,
            "dependencies": self.dependencies,
            "tools": self.tools,
            "platform": self.platform.value,
            "license": self.license,
            "homepage": self.homepage,
            "source": self.source,
            "content": self.content,
            "path": self.path,
            "installed_at": self.installed_at,
            "source_type": self.source_type,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SkillMetadata":
        """从字典创建"""
        # 过滤 None 值
        data = {k: v for k, v in data.items() if v is not None}
        return cls(**data)


@dataclass 
class DependencySpec:
    """依赖规格"""
    name: str
    version_range: str  # e.g., "^1.0.0", ">=1.0.0"
    
    @classmethod
    def parse(cls, spec: str) -> "DependencySpec":
        """
        解析依赖字符串
        
        Examples:
            "github-pr@^1.0.0" -> DependencySpec(name="github-pr", version_range="^1.0.0")
            "github-pr" -> DependencySpec(name="github-pr", version_range="*")
        """
        if '@' in spec:
            name, version_range = spec.split('@', 1)
        else:
            name = spec
            version_range = "*"
        return cls(name=name.strip(), version_range=version_range.strip())
    
    def matches(self, version: str) -> bool:
        """检查版本是否满足范围"""
        import semver
        
        try:
            if self.version_range == "*":
                return True
            
            if self.version_range.startswith("^"):
                # ^1.0.0 -> >=1.0.0 <2.0.0
                base = self.version_range[1:]
                return semver.match(version, f">={base}") and semver.match(version, f"<{semver.bump_major(base)}")
            
            elif self.version_range.startswith("~"):
                # ~1.0.0 -> >=1.0.0 <1.1.0
                base = self.version_range[1:]
                return semver.match(version, f">={base}") and semver.match(version, f"<{semver.bump_minor(base)}")
            
            else:
                return semver.match(version, self.version_range)
                
        except Exception:
            return False


@dataclass
class SkillInstallInfo:
    """Skill 安装信息"""
    name: str
    version: str
    path: str
    installed_at: str
    source: str = "local"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "path": self.path,
            "installed_at": self.installed_at,
            "source": self.source,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SkillInstallInfo":
        return cls(**data)


@dataclass
class RegistryData:
    """注册表数据"""
    skills: dict[str, SkillInstallInfo] = field(default_factory=dict)
    index_updated_at: str = ""
    
    def to_dict(self) -> dict:
        return {
            "skills": {k: v.to_dict() for k, v in self.skills.items()},
            "index_updated_at": self.index_updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RegistryData":
        skills = {
            k: SkillInstallInfo.from_dict(v) 
            for k, v in data.get("skills", {}).items()
        }
        return cls(
            skills=skills,
            index_updated_at=data.get("index_updated_at", ""),
        )
