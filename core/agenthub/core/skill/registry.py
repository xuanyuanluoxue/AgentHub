# -*- coding: utf-8 -*-
"""
Skill 注册表 - 管理本地已安装的 Skill
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from agenthub.core.skill.models import RegistryData, SkillInstallInfo, SkillMetadata
from agenthub.core.skill.parser import SkillParser, SkillParseError


class RegistryError(Exception):
    """注册表错误"""
    pass


class SkillRegistry:
    """
    Skill 本地注册表
    
    管理 ~/.agenthub/ 下的 Skill 安装、卸载、查询
    """
    
    def __init__(self, base_path: str = "~/.agenthub"):
        """
        初始化注册表
        
        Args:
            base_path: AgentHub 根目录
        """
        self.base_path = Path(base_path).expanduser()
        self.skills_dir = self.base_path / "skills"
        self.registry_file = self.base_path / "registry.json"
        
        # 确保目录存在
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载注册表
        self._data = self._load()
    
    def _load(self) -> RegistryData:
        """加载注册表"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return RegistryData.from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                # 注册表损坏，创建新的
                return RegistryData()
        return RegistryData()
    
    def _save(self):
        """保存注册表"""
        self._data.index_updated_at = datetime.now().isoformat()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self._data.to_dict(), f, ensure_ascii=False, indent=2)
    
    def register(self, skill_path: str | Path) -> SkillInstallInfo:
        """
        注册一个 Skill（安装到本地注册表）
        
        Args:
            skill_path: Skill 目录或 SKILL.md 路径
            
        Returns:
            SkillInstallInfo
            
        Raises:
            RegistryError: 注册失败
        """
        skill_path = Path(skill_path)
        
        # 如果传入的是 SKILL.md，取其目录
        if skill_path.name == "SKILL.md":
            skill_path = skill_path.parent
        
        # 解析 Skill
        try:
            metadata = SkillParser.parse_directory(skill_path)
        except SkillParseError as e:
            raise RegistryError(f"解析 Skill 失败: {e}")
        
        # 验证元数据
        is_valid, errors = metadata.validate()
        if not is_valid:
            raise RegistryError(f"Skill 元数据验证失败: {', '.join(errors)}")
        
        # 目标路径
        target_dir = self.skills_dir / metadata.name
        
        # 如果已存在，先移除
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # 复制到 skills 目录
        shutil.copytree(skill_path, target_dir)
        
        # 更新注册表
        install_info = SkillInstallInfo(
            name=metadata.name,
            version=metadata.version,
            path=str(target_dir),
            installed_at=datetime.now().isoformat(),
            source="local",
        )
        self._data.skills[metadata.name] = install_info
        self._save()
        
        return install_info
    
    def unregister(self, name: str) -> bool:
        """
        取消注册一个 Skill（从本地移除）
        
        Args:
            name: Skill 名称
            
        Returns:
            是否成功
        """
        if name not in self._data.skills:
            return False
        
        # 删除目录
        skill_dir = Path(self._data.skills[name].path)
        if skill_dir.exists():
            shutil.rmtree(skill_dir)
        
        # 从注册表移除
        del self._data.skills[name]
        self._save()
        
        return True
    
    def get(self, name: str) -> Optional[SkillMetadata]:
        """
        获取 Skill 元数据
        
        Args:
            name: Skill 名称
            
        Returns:
            SkillMetadata 或 None
        """
        if name not in self._data.skills:
            return None
        
        skill_path = self._data.skills[name].path
        try:
            return SkillParser.parse_directory(skill_path)
        except SkillParseError:
            return None
    
    def list_all(self) -> list[SkillMetadata]:
        """
        列出所有已注册的 Skill
        
        Returns:
            SkillMetadata 列表
        """
        results = []
        for name in self._data.skills:
            metadata = self.get(name)
            if metadata:
                results.append(metadata)
        return results
    
    def search(self, query: str) -> list[SkillMetadata]:
        """
        搜索 Skill
        
        Args:
            query: 搜索关键词（匹配 name、description、tags）
            
        Returns:
            匹配的 Skill 列表
        """
        query_lower = query.lower()
        results = []
        
        for skill in self.list_all():
            # 匹配 name
            if query_lower in skill.name.lower():
                results.append(skill)
                continue
            
            # 匹配 description
            if query_lower in skill.description.lower():
                results.append(skill)
                continue
            
            # 匹配 tags
            if any(query_lower in tag.lower() for tag in skill.tags):
                results.append(skill)
                continue
        
        return results
    
    def find_by_trigger(self, text: str) -> list[SkillMetadata]:
        """
        根据触发词查找 Skill
        
        Args:
            text: 输入文本
            
        Returns:
            匹配的 Skill 列表
        """
        results = []
        for skill in self.list_all():
            if skill.matches_trigger(text):
                results.append(skill)
        return results
    
    def exists(self, name: str) -> bool:
        """检查 Skill 是否已注册"""
        return name in self._data.skills
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total": len(self._data.skills),
            "skills": list(self._data.skills.keys()),
            "last_updated": self._data.index_updated_at,
        }
    
    def reload(self):
        """重新加载注册表"""
        self._data = self._load()
    
    def rebuild(self) -> dict:
        """
        重建注册表（扫描 skills 目录）
        
        Returns:
            扫描结果统计
        """
        # 清空现有数据
        self._data = RegistryData()
        
        # 扫描 skills 目录
        added = 0
        errors = []
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            try:
                metadata = SkillParser.parse_directory(skill_dir)
                is_valid, errs = metadata.validate()
                
                if not is_valid:
                    errors.append(f"{skill_dir.name}: {', '.join(errs)}")
                    continue
                
                # 注册
                self._data.skills[metadata.name] = SkillInstallInfo(
                    name=metadata.name,
                    version=metadata.version,
                    path=str(skill_dir),
                    installed_at=datetime.now().isoformat(),
                    source="local",
                )
                added += 1
                
            except Exception as e:
                errors.append(f"{skill_dir.name}: {e}")
        
        self._save()
        
        return {
            "added": added,
            "errors": errors,
        }
