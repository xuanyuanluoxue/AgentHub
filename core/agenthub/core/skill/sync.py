# -*- coding: utf-8 -*-
"""
Skill 同步器 - 将 Skill 同步到各 AI 工具
"""

import shutil
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from agenthub.core.skill.models import SkillMetadata
from agenthub.core.skill.registry import SkillRegistry


@dataclass
class SyncTarget:
    """同步目标"""
    name: str  # 目标名称
    path: str  # 目标路径
    enabled: bool = True


class SyncConfig:
    """同步配置"""
    
    # 默认 AI 工具路径
    DEFAULT_TARGETS = {
        "opencode": "~/.config/opencode/skills",
        "openclaw": "~/.openclaw/skills",
        "claude": "~/.claude/skills",
        "cursor": "~/.cursor/skills",
        "hermes": "~/.hermes/skills",
    }
    
    def __init__(self):
        self.targets: dict[str, SyncTarget] = {}
        
        # 初始化默认目标
        for name, path in self.DEFAULT_TARGETS.items():
            self.targets[name] = SyncTarget(
                name=name,
                path=str(Path(path).expanduser()),
                enabled=False,  # 默认禁用，需要用户启用
            )
    
    def enable(self, name: str) -> bool:
        """启用目标"""
        if name in self.targets:
            self.targets[name].enabled = True
            return True
        return False
    
    def disable(self, name: str) -> bool:
        """禁用目标"""
        if name in self.targets:
            self.targets[name].enabled = False
            return True
        return False
    
    def get_enabled(self) -> list[SyncTarget]:
        """获取已启用的目标"""
        return [t for t in self.targets.values() if t.enabled]
    
    def add_custom_target(self, name: str, path: str):
        """添加自定义目标"""
        self.targets[name] = SyncTarget(
            name=name,
            path=str(Path(path).expanduser()),
            enabled=True,
        )
    
    def remove_target(self, name: str) -> bool:
        """移除目标"""
        if name in self.targets and name not in self.DEFAULT_TARGETS:
            del self.targets[name]
            return True
        return False


class SyncResult:
    """同步结果"""
    
    def __init__(
        self,
        skill_name: str,
        success: bool,
        target: str,
        message: str = "",
    ):
        self.skill_name = skill_name
        self.success = success
        self.target = target
        self.message = message
    
    def __str__(self) -> str:
        status = "✓" if self.success else "✗"
        return f"[{status}] {self.skill_name} -> {self.target}: {self.message}"


class SkillSync:
    """
    Skill 同步器
    
    将 Skill 同步到各 AI 工具的 skills 目录
    """
    
    def __init__(self, registry: Optional[SkillRegistry] = None):
        """
        初始化同步器
        
        Args:
            registry: 注册表实例
        """
        self.registry = registry or SkillRegistry()
        self.config = SyncConfig()
    
    def sync_skill(
        self,
        skill_name: str,
        targets: Optional[list[str]] = None,
    ) -> list[SyncResult]:
        """
        同步单个 Skill 到指定目标
        
        Args:
            skill_name: Skill 名称
            targets: 目标列表，None 表示所有已启用目标
            
        Returns:
            SyncResult 列表
        """
        results = []
        
        # 获取 Skill 元数据
        metadata = self.registry.get(skill_name)
        if not metadata:
            return [SyncResult(
                skill_name, False, "any",
                "Skill 不存在"
            )]
        
        # 确定目标列表
        if targets:
            target_list = [
                self.config.targets[t] 
                for t in targets 
                if t in self.config.targets
            ]
        else:
            target_list = self.config.get_enabled()
        
        # 同步到每个目标
        for target in target_list:
            result = self._sync_to_target(metadata, target)
            results.append(result)
        
        return results
    
    def _sync_to_target(
        self,
        metadata: SkillMetadata,
        target: SyncTarget,
    ) -> SyncResult:
        """同步到单个目标"""
        try:
            source_path = Path(metadata.path)
            target_path = Path(target.path) / metadata.name
            
            # 创建目标目录
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果已存在，移除
            if target_path.exists():
                shutil.rmtree(target_path)
            
            # 复制
            shutil.copytree(source_path, target_path)
            
            return SyncResult(
                skill_name=metadata.name,
                success=True,
                target=target.name,
                message=f"已同步到 {target.path}",
            )
            
        except Exception as e:
            return SyncResult(
                skill_name=metadata.name,
                success=False,
                target=target.name,
                message=str(e),
            )
    
    def sync_all(
        self,
        targets: Optional[list[str]] = None,
    ) -> list[SyncResult]:
        """
        同步所有 Skill 到指定目标
        
        Args:
            targets: 目标列表，None 表示所有已启用目标
            
        Returns:
            SyncResult 列表
        """
        results = []
        
        for skill in self.registry.list_all():
            results.extend(self.sync_skill(skill.name, targets))
        
        return results
    
    def pull(
        self,
        skill_name: str,
        source_tool: str,
    ) -> SyncResult:
        """
        从 AI 工具拉取 Skill 到本地注册表
        
        Args:
            skill_name: Skill 名称
            source_tool: 源工具名称（如 'opencode'）
            
        Returns:
            SyncResult
        """
        if source_tool not in self.config.targets:
            return SyncResult(
                skill_name, False, source_tool,
                f"未知工具: {source_tool}"
            )
        
        target = self.config.targets[source_tool]
        source_path = Path(target.path) / skill_name
        
        if not source_path.exists():
            return SyncResult(
                skill_name, False, source_tool,
                f"Skill 目录不存在: {source_path}"
            )
        
        try:
            self.registry.register(source_path)
            return SyncResult(
                skill_name, True, source_tool,
                f"已从 {source_tool} 拉取"
            )
        except Exception as e:
            return SyncResult(
                skill_name, False, source_tool,
                str(e)
            )
    
    def list_targets(self) -> list[SyncTarget]:
        """列出所有同步目标"""
        return list(self.config.targets.values())
    
    def get_sync_status(self, skill_name: str) -> dict:
        """
        获取 Skill 的同步状态
        
        Args:
            skill_name: Skill 名称
            
        Returns:
            {target_name: is_synced}
        """
        metadata = self.registry.get(skill_name)
        if not metadata:
            return {}
        
        status = {}
        for name, target in self.config.targets.items():
            target_path = Path(target.path) / skill_name
            status[name] = target_path.exists()
        
        return status
