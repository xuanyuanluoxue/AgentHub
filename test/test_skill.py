# -*- coding: utf-8 -*-
"""
AgentHub Skill 模块测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from agenthub.core.skill.models import (
    SkillMetadata, SkillCategory, Platform,
    DependencySpec, RegistryData, SkillInstallInfo
)
from agenthub.core.skill.parser import SkillParser, SkillParseError
from agenthub.core.skill.registry import SkillRegistry, RegistryError


# ===== 测试数据 =====

MINIMAL_SKILL = """---
name: test-skill
version: 1.0.0
description: Test description
trigger:
  - "test"
---

# Test Skill

This is a test skill.
"""

COMPLETE_SKILL = """---
name: complete-skill
version: 1.2.3-beta.1
description: A complete test skill
author: Test Author
tags:
  - test
  - example
category: dev
trigger:
  - "complete"
  - "测试"
dependencies:
  - other-skill@^1.0.0
tools:
  - python
  - git
platform: linux
license: MIT
homepage: https://example.com
source: https://github.com/example/skill
---

# Complete Skill

This skill has all fields.
"""

INVALID_SKILL_NO_NAME = """---
version: 1.0.0
description: Missing name
trigger:
  - "test"
---

# Invalid
"""

INVALID_SKILL_BAD_VERSION = """---
name: bad-version
version: not-a-semver
description: Test
trigger:
  - "test"
---

# Invalid
"""


# ===== 测试 SkillParser =====

class TestSkillParser:
    """SkillParser 测试"""
    
    def test_parse_minimal_skill(self):
        """测试解析最小 Skill"""
        metadata = SkillParser.parse_content(MINIMAL_SKILL)
        
        assert metadata.name == "test-skill"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test description"
        assert "test" in metadata.trigger
        assert metadata.content.strip() == "# Test Skill\n\nThis is a test skill."
    
    def test_parse_complete_skill(self):
        """测试解析完整 Skill"""
        metadata = SkillParser.parse_content(COMPLETE_SKILL)
        
        assert metadata.name == "complete-skill"
        assert metadata.version == "1.2.3-beta.1"
        assert metadata.author == "Test Author"
        assert "test" in metadata.tags
        assert metadata.category == SkillCategory.DEV
        assert metadata.platform == Platform.LINUX
        assert len(metadata.dependencies) == 1
        assert "python" in metadata.tools
    
    def test_parse_invalid_no_name(self):
        """测试解析缺少 name 的 Skill"""
        with pytest.raises(SkillParseError) as exc_info:
            SkillParser.parse_content(INVALID_SKILL_NO_NAME)
        assert "name" in str(exc_info.value)
    
    def test_parse_invalid_bad_version(self):
        """测试解析非法版本号"""
        with pytest.raises(SkillParseError) as exc_info:
            SkillParser.parse_content(INVALID_SKILL_BAD_VERSION)
        assert "version" in str(exc_info.value)
    
    def test_validate_skill_metadata(self):
        """测试元数据验证"""
        metadata = SkillParser.parse_content(MINIMAL_SKILL)
        is_valid, errors = metadata.validate()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_write_skill_md(self):
        """测试写入 SKILL.md"""
        metadata = SkillParser.parse_content(MINIMAL_SKILL)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            SkillParser.write_skill_md(temp_path, metadata)
            
            # 重新读取验证
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert "---" in content
            assert "name: test-skill" in content
            assert "version: 1.0.0" in content
        finally:
            Path(temp_path).unlink()


# ===== 测试 SkillMetadata =====

class TestSkillMetadata:
    """SkillMetadata 测试"""
    
    def test_matches_trigger(self):
        """测试触发词匹配"""
        metadata = SkillParser.parse_content(MINIMAL_SKILL)
        
        assert metadata.matches_trigger("hello test world")
        assert metadata.matches_trigger("TEST")
        assert not metadata.matches_trigger("hello world")
    
    def test_version_tuple(self):
        """测试版本号元组"""
        metadata = SkillParser.parse_content(MINIMAL_SKILL)
        
        assert metadata.version_tuple == (1, 0, 0)


# ===== 测试 DependencySpec =====

class TestDependencySpec:
    """DependencySpec 测试"""
    
    def test_parse_with_version(self):
        """测试解析带版本的依赖"""
        spec = DependencySpec.parse("github-pr@^1.0.0")
        
        assert spec.name == "github-pr"
        assert spec.version_range == "^1.0.0"
    
    def test_parse_without_version(self):
        """测试解析不带版本的依赖"""
        spec = DependencySpec.parse("some-skill")
        
        assert spec.name == "some-skill"
        assert spec.version_range == "*"
    
    def test_matches_exact(self):
        """测试精确版本匹配"""
        spec = DependencySpec.parse("skill@1.0.0")
        
        assert spec.matches("1.0.0")
        assert not spec.matches("2.0.0")
    
    def test_matches_wildcard(self):
        """测试通配符匹配"""
        spec = DependencySpec.parse("skill@*")
        
        assert spec.matches("1.0.0")
        assert spec.matches("99.99.99")


# ===== 测试 SkillRegistry =====

class TestSkillRegistry:
    """SkillRegistry 测试"""
    
    @pytest.fixture
    def temp_registry_dir(self):
        """创建临时注册表目录"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)
    
    @pytest.fixture
    def registry(self, temp_registry_dir):
        """创建注册表实例"""
        return SkillRegistry(base_path=temp_registry_dir)
    
    @pytest.fixture
    def temp_skill_dir(self, temp_registry_dir):
        """创建临时 Skill 目录"""
        skill_dir = Path(temp_registry_dir) / "test-skill"
        skill_dir.mkdir()
        
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(MINIMAL_SKILL, encoding='utf-8')
        
        return skill_dir
    
    def test_register_skill(self, registry, temp_skill_dir):
        """测试注册 Skill"""
        info = registry.register(temp_skill_dir)
        
        assert info.name == "test-skill"
        assert info.version == "1.0.0"
        assert registry.exists("test-skill")
    
    def test_unregister_skill(self, registry, temp_skill_dir):
        """测试取消注册"""
        registry.register(temp_skill_dir)
        result = registry.unregister("test-skill")
        
        assert result
        assert not registry.exists("test-skill")
    
    def test_get_skill(self, registry, temp_skill_dir):
        """测试获取 Skill"""
        registry.register(temp_skill_dir)
        metadata = registry.get("test-skill")
        
        assert metadata is not None
        assert metadata.name == "test-skill"
    
    def test_list_all(self, registry, temp_skill_dir):
        """测试列出所有 Skill"""
        registry.register(temp_skill_dir)
        skills = registry.list_all()
        
        assert len(skills) == 1
        assert skills[0].name == "test-skill"
    
    def test_search(self, registry, temp_skill_dir):
        """测试搜索"""
        registry.register(temp_skill_dir)
        results = registry.search("test")
        
        assert len(results) == 1
        assert results[0].name == "test-skill"
    
    def test_find_by_trigger(self, registry, temp_skill_dir):
        """测试按触发词查找"""
        registry.register(temp_skill_dir)
        results = registry.find_by_trigger("hello test world")
        
        assert len(results) == 1
    
    def test_rebuild(self, registry, temp_skill_dir):
        """测试重建注册表"""
        # 先手动复制到 skills 目录
        skills_dir = Path(registry.skills_dir)
        dest = skills_dir / "test-skill"
        shutil.copytree(temp_skill_dir, dest)
        
        result = registry.rebuild()
        
        assert result["added"] == 1
        assert registry.exists("test-skill")


# ===== 运行测试 =====

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
