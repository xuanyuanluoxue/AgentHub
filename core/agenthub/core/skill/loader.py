# -*- coding: utf-8 -*-
"""
Skill 加载器 - 从不同来源加载 Skill
"""

import shutil
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import zipfile
import tarfile

from agenthub.core.skill.models import SkillMetadata
from agenthub.core.skill.parser import SkillParser, SkillParseError
from agenthub.core.skill.registry import SkillRegistry, RegistryError


class LoaderError(Exception):
    """加载错误"""
    pass


class SkillLoader:
    """
    Skill 加载器
    
    支持从以下来源加载 Skill：
    - 本地目录
    - Git 仓库
    - ZIP/TAR 压缩包
    - URL 下载
    """
    
    def __init__(self, registry: Optional[SkillRegistry] = None):
        """
        初始化加载器
        
        Args:
            registry: 可选，注册表实例
        """
        self.registry = registry or SkillRegistry()
    
    def load(self, source: str, install: bool = True) -> SkillMetadata:
        """
        加载 Skill
        
        Args:
            source: 来源（路径、URL、git 地址）
            install: 是否安装到注册表
            
        Returns:
            SkillMetadata
        """
        # 判断来源类型
        if self._is_local_path(source):
            return self._load_local(source, install)
        elif source.startswith('git+') or source.startswith('git://'):
            return self._load_git(source, install)
        elif self._is_url(source):
            return self._load_url(source, install)
        elif source.endswith(('.zip', '.tar', '.gz', '.tgz', '.tar.gz')):
            return self._load_archive(source, install)
        else:
            raise LoaderError(f"不支持的来源格式: {source}")
    
    def _is_local_path(self, source: str) -> bool:
        """检查是否是本地路径"""
        path = Path(source)
        return path.exists() or (Path.cwd() / source).exists()
    
    def _is_url(self, source: str) -> bool:
        """检查是否是 URL"""
        try:
            result = urlparse(source)
            return result.scheme in ('http', 'https')
        except Exception:
            return False
    
    def _load_local(self, source: str, install: bool) -> SkillMetadata:
        """从本地路径加载"""
        source_path = Path(source)
        
        if not source_path.exists():
            # 尝试相对于当前目录
            source_path = Path.cwd() / source
            
        if not source_path.exists():
            raise LoaderError(f"路径不存在: {source}")
        
        # 解析 Skill
        try:
            if source_path.is_dir():
                metadata = SkillParser.parse_directory(source_path)
            else:
                metadata = SkillParser.parse_file(source_path)
        except SkillParseError as e:
            raise LoaderError(f"解析 Skill 失败: {e}")
        
        # 安装到注册表
        if install:
            try:
                self.registry.register(source_path)
            except RegistryError as e:
                raise LoaderError(f"注册 Skill 失败: {e}")
        
        return metadata
    
    def _load_git(self, source: str, install: bool) -> SkillMetadata:
        """从 Git 仓库加载"""
        # 去掉 git+ 前缀
        repo_url = source[4:] if source.startswith('git+') else source
        
        import subprocess
        
        # 临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # 克隆
            try:
                subprocess.run(
                    ['git', 'clone', '--depth', '1', repo_url, str(tmppath)],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError as e:
                raise LoaderError(f"Git 克隆失败: {e.stderr.decode() if e.stderr else str(e)}")
            
            # 查找 SKILL.md
            skill_md = tmppath / "SKILL.md"
            if not skill_md.exists():
                raise LoaderError(f"仓库中没有 SKILL.md")
            
            # 解析
            try:
                metadata = SkillParser.parse_file(skill_md)
            except SkillParseError as e:
                raise LoaderError(f"解析 Skill 失败: {e}")
            
            # 安装
            if install:
                try:
                    self.registry.register(tmppath)
                except RegistryError as e:
                    raise LoaderError(f"注册 Skill 失败: {e}")
            
            return metadata
    
    def _load_url(self, source: str, install: bool) -> SkillMetadata:
        """从 URL 加载"""
        import urllib.request
        import urllib.error
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            archive_path = tmppath / "archive"
            
            # 下载
            try:
                urllib.request.urlretrieve(source, archive_path)
            except urllib.error.URLError as e:
                raise LoaderError(f"下载失败: {e}")
            
            # 根据扩展名判断类型
            if source.endswith('.zip'):
                return self._extract_zip(archive_path, install)
            elif source.endswith(('.tar', '.gz', '.tgz', '.tar.gz')):
                return self._extract_tar(archive_path, install)
            else:
                raise LoaderError(f"不支持的压缩格式: {source}")
    
    def _load_archive(self, source: str, install: bool) -> SkillMetadata:
        """从压缩包加载"""
        source_path = Path(source)
        
        if not source_path.exists():
            raise LoaderError(f"文件不存在: {source}")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            dest_path = tmppath / "extracted"
            
            # 解压
            if source.endswith('.zip'):
                self._extract_zip_file(source_path, dest_path)
            elif source.endswith(('.tar', '.gz', '.tgz', '.tar.gz')):
                self._extract_tar_file(source_path, dest_path)
            else:
                raise LoaderError(f"不支持的压缩格式: {source}")
            
            # 查找 SKILL.md
            skill_md = self._find_skill_md(dest_path)
            if not skill_md:
                raise LoaderError("压缩包中没有找到 SKILL.md")
            
            # 解析
            try:
                metadata = SkillParser.parse_file(skill_md)
            except SkillParseError as e:
                raise LoaderError(f"解析 Skill 失败: {e}")
            
            # 安装
            if install:
                skill_dir = skill_md.parent
                try:
                    self.registry.register(skill_dir)
                except RegistryError as e:
                    raise LoaderError(f"注册 Skill 失败: {e}")
            
            return metadata
    
    def _extract_zip(self, archive_path: Path, install: bool) -> SkillMetadata:
        """解压 ZIP"""
        dest = archive_path.parent / "extracted"
        self._extract_zip_file(archive_path, dest)
        return self._load_extracted(dest, install)
    
    def _extract_tar(self, archive_path: Path, install: bool) -> SkillMetadata:
        """解压 TAR"""
        dest = archive_path.parent / "extracted"
        self._extract_tar_file(archive_path, dest)
        return self._load_extracted(dest, install)
    
    def _extract_zip_file(self, archive_path: Path, dest: Path):
        """解压 ZIP 文件"""
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(dest)
    
    def _extract_tar_file(self, archive_path: Path, dest: Path):
        """解压 TAR 文件"""
        dest.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive_path, 'r:*') as tf:
            tf.extractall(dest)
    
    def _find_skill_md(self, path: Path) -> Optional[Path]:
        """查找 SKILL.md"""
        # 直接在目录中
        if (path / "SKILL.md").exists():
            return path / "SKILL.md"
        
        # 在子目录中（压缩包可能有多层目录）
        for subdir in path.rglob("SKILL.md"):
            return subdir
        
        return None
    
    def _load_extracted(self, extracted_path: Path, install: bool) -> SkillMetadata:
        """加载解压后的目录"""
        skill_md = self._find_skill_md(extracted_path)
        if not skill_md:
            raise LoaderError("解压后没有找到 SKILL.md")
        
        try:
            metadata = SkillParser.parse_file(skill_md)
        except SkillParseError as e:
            raise LoaderError(f"解析 Skill 失败: {e}")
        
        if install:
            skill_dir = skill_md.parent
            try:
                self.registry.register(skill_dir)
            except RegistryError as e:
                raise LoaderError(f"注册 Skill 失败: {e}")
        
        return metadata
    
    def copy_to(self, skill_name: str, target_dir: str | Path) -> bool:
        """
        复制 Skill 到指定目录
        
        Args:
            skill_name: Skill 名称
            target_dir: 目标目录（AI 工具的 skills 目录）
            
        Returns:
            是否成功
        """
        if not self.registry.exists(skill_name):
            return False
        
        skill_meta = self.registry.get(skill_name)
        if not skill_meta:
            return False
        
        source_path = Path(skill_meta.path)
        target_path = Path(target_dir) / skill_name
        
        # 创建目标目录
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 复制
        if target_path.exists():
            shutil.rmtree(target_path)
        shutil.copytree(source_path, target_path)
        
        return True
