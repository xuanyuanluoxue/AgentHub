# -*- coding: utf-8 -*-
"""
Skill 依赖解析器
"""

from typing import Optional
from agenthub.core.skill.models import DependencySpec, SkillMetadata
from agenthub.core.skill.registry import SkillRegistry


class DependencyError(Exception):
    """依赖错误"""
    pass


class CircularDependencyError(DependencyError):
    """循环依赖错误"""
    pass


class UnsatisfiedDependencyError(DependencyError):
    """未满足的依赖"""
    def __init__(self, skill_name: str, dependency: str, required_version: str):
        self.skill_name = skill_name
        self.dependency = dependency
        self.required_version = required_version
        super().__init__(
            f"Skill '{skill_name}' 需要的依赖 '{dependency}@{required_version}' 未满足"
        )


class DependencyResolver:
    """
    依赖解析器
    
    解析 Skill 的依赖关系，检测循环依赖，验证版本兼容性
    """
    
    def __init__(self, registry: Optional[SkillRegistry] = None):
        """
        初始化解析器
        
        Args:
            registry: 注册表实例
        """
        self.registry = registry or SkillRegistry()
    
    def parse_dependencies(self, skill_metadata: SkillMetadata) -> list[DependencySpec]:
        """
        解析 Skill 的依赖列表
        
        Args:
            skill_metadata: Skill 元数据
            
        Returns:
            DependencySpec 列表
        """
        return [
            DependencySpec.parse(dep) 
            for dep in skill_metadata.dependencies
        ]
    
    def check_dependencies(self, skill_metadata: SkillMetadata) -> tuple[bool, list[str]]:
        """
        检查依赖是否满足
        
        Args:
            skill_metadata: Skill 元数据
            
        Returns:
            (is_satisfied, error_messages)
        """
        errors = []
        
        for dep_spec in self.parse_dependencies(skill_metadata):
            # 检查是否已安装
            if not self.registry.exists(dep_spec.name):
                errors.append(
                    f"缺少依赖: {dep_spec.name} ({dep_spec.version_range})"
                )
                continue
            
            # 获取已安装版本
            installed = self.registry.get(dep_spec.name)
            if not installed:
                errors.append(f"无法获取依赖信息: {dep_spec.name}")
                continue
            
            # 检查版本
            if not dep_spec.matches(installed.version):
                errors.append(
                    f"依赖版本不匹配: {dep_spec.name} "
                    f"需要 {dep_spec.version_range}，已安装 {installed.version}"
                )
        
        return (len(errors) == 0, errors)
    
    def get_install_order(self, skill_names: list[str]) -> list[str]:
        """
        获取安装顺序（按依赖排序）
        
        Args:
            skill_names: 需要安装的 Skill 名称列表
            
        Returns:
            排序后的安装顺序
        """
        # 获取所有 Skill 的依赖
        all_deps = {}
        for name in skill_names:
            skill = self.registry.get(name)
            if skill:
                all_deps[name] = [
                    DependencySpec.parse(d).name 
                    for d in skill.dependencies
                ]
        
        # 计算入度
        in_degree = {name: 0 for name in skill_names}
        for name in skill_names:
            for dep in all_deps.get(name, []):
                if dep in skill_names:
                    in_degree[name] += 1
        
        # 拓扑排序（Kahn 算法）
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # 弹出入度为 0 的节点
            node = queue.pop(0)
            result.append(node)
            
            # 更新依赖它的节点的入度
            for name in skill_names:
                if node in all_deps.get(name, []):
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)
        
        # 检查循环依赖
        if len(result) != len(skill_names):
            # 找出循环依赖的节点
            remaining = set(skill_names) - set(result)
            raise CircularDependencyError(
                f"检测到循环依赖，涉及: {', '.join(remaining)}"
            )
        
        return result
    
    def detect_circular_dependencies(self, skill_metadata: SkillMetadata) -> list[list[str]]:
        """
        检测循环依赖
        
        使用 DFS 检测从指定 Skill 开始的循环依赖
        
        Args:
            skill_metadata: Skill 元数据
            
        Returns:
            循环依赖路径列表，每条路径是一个循环
        """
        cycles = []
        
        def dfs(skill_name: str, path: list[str], visited: set[str], rec_stack: set[str]):
            """DFS 遍历"""
            visited.add(skill_name)
            rec_stack.add(skill_name)
            path.append(skill_name)
            
            # 获取依赖
            skill = self.registry.get(skill_name)
            if skill:
                for dep_str in skill.dependencies:
                    dep = DependencySpec.parse(dep_str).name
                    
                    if dep not in visited:
                        dfs(dep, path.copy(), visited, rec_stack)
                    elif dep in rec_stack:
                        # 发现循环
                        cycle_start = path.index(dep)
                        cycle = path[cycle_start:] + [dep]
                        cycles.append(cycle)
            
            rec_stack.remove(skill_name)
        
        # 从当前 Skill 开始 DFS
        visited = set()
        for dep_str in skill_metadata.dependencies:
            dep_name = DependencySpec.parse(dep_str).name
            if dep_name not in visited and self.registry.exists(dep_name):
                dfs(dep_name, [], visited, set())
        
        return cycles
    
    def resolve_all_dependencies(self, skill_metadata: SkillMetadata) -> list[str]:
        """
        解析 Skill 的所有依赖（包括传递依赖）
        
        Args:
            skill_metadata: Skill 元数据
            
        Returns:
            按安装顺序排列的依赖列表
        """
        # 收集所有依赖
        all_deps = set()
        
        def collect_deps(name: str):
            skill = self.registry.get(name)
            if not skill:
                return
            
            for dep_str in skill.dependencies:
                dep_name = DependencySpec.parse(dep_str).name
                if dep_name not in all_deps:
                    all_deps.add(dep_name)
                    collect_deps(dep_name)
        
        collect_deps(skill_metadata.name)
        
        # 排序
        return self.get_install_order(list(all_deps))
    
    def validate_installation(self, skill_metadata: SkillMetadata) -> tuple[bool, list[str]]:
        """
        验证 Skill 是否可以安装
        
        综合检查：
        - 依赖是否满足
        - 是否有循环依赖
        - 平台是否兼容
        
        Args:
            skill_metadata: Skill 元数据
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # 检查依赖
        deps_ok, dep_errors = self.check_dependencies(skill_metadata)
        errors.extend(dep_errors)
        
        # 检查循环依赖
        if self.registry.exists(skill_metadata.name):
            cycles = self.detect_circular_dependencies(skill_metadata)
            if cycles:
                errors.append(f"检测到循环依赖: {cycles}")
        
        # 检查平台兼容性（需要获取当前平台）
        # import platform
        # current_platform = ...
        # if skill_metadata.platform != Platform.ALL and skill_metadata.platform != current_platform:
        #     errors.append(f"平台不兼容: 需要 {skill_metadata.platform.value}")
        
        return (len(errors) == 0, errors)
