# -*- coding: utf-8 -*-
"""
配置管理 - YAML 配置加载
"""

import os
from pathlib import Path
from typing import Optional, Any
import yaml


class ConfigError(Exception):
    """配置错误"""
    pass


class AgentHubConfig:
    """
    AgentHub 配置类

    支持从以下位置加载配置（按优先级）：
    1. 环境变量 AGENTHUB_CONFIG
    2. ~/.agenthub/config.yaml
    3. 项目根目录/config.yaml
    """

    DEFAULT_CONFIG = {
        "name": "AgentHub",
        "version": "0.2.0",
        "description": "AI 工具管理平台",
        "language": "zh-CN",
        "theme": "dark",
        "autoSync": True,
        "sharedSkillsPath": None,
        "tools": ["opencode", "openclaw", "claude", "codebuddy", "cursor", "hermes"],
        "agents": [],
        "skills": [],
        "database": {
            "type": "json",
            "path": "~/.agenthub/registry.json",
        },
        "log": {
            "level": "INFO",
            "path": "~/.agenthub/logs/agenthub.log",
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 可选，指定配置文件路径
        """
        self._data: dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._load(config_path)

    @staticmethod
    def _find_config_file() -> Optional[Path]:
        """查找配置文件"""
        candidates = [
            Path(os.environ.get("AGENTHUB_CONFIG", "")),
            Path.home() / ".agenthub" / "config.yaml",
            Path.home() / ".agenthub" / "config.yml",
        ]
        for path in candidates:
            if path.exists() and path.stat().st_size > 0:
                return path
        return None

    def _load(self, config_path: Optional[str] = None):
        """加载配置"""
        self._data = self.DEFAULT_CONFIG.copy()

        if config_path:
            self._config_path = Path(config_path)
        else:
            self._config_path = self._find_config_file()

        if self._config_path and self._config_path.exists():
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                if user_config:
                    self._merge_config(self._data, user_config)
            except yaml.YAMLError as e:
                raise ConfigError(f"配置文件解析失败: {e}")
            except Exception as e:
                raise ConfigError(f"读取配置文件失败: {e}")

    def _merge_config(self, base: dict, updates: dict):
        """深度合并配置"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号路径

        Examples:
            config.get("database.type")
            config.get("tools", [])
        """
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any):
        """设置配置值，支持点号路径"""
        keys = key.split(".")
        data = self._data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    def save(self, path: Optional[str] = None):
        """保存配置到文件"""
        save_path = Path(path) if path else self._config_path
        if not save_path:
            save_path = Path.home() / ".agenthub" / "config.yaml"

        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._data, f, allow_unicode=True, default_flow_style=False)
        self._config_path = save_path

    @property
    def data(self) -> dict:
        """获取完整配置字典"""
        return self._data.copy()

    @property
    def config_path(self) -> Optional[Path]:
        """获取配置文件路径"""
        return self._config_path

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None


_global_config: Optional[AgentHubConfig] = None


def get_config() -> AgentHubConfig:
    """获取全局配置单例"""
    global _global_config
    if _global_config is None:
        _global_config = AgentHubConfig()
    return _global_config


def load_config(config_path: Optional[str] = None) -> AgentHubConfig:
    """加载配置"""
    global _global_config
    _global_config = AgentHubConfig(config_path)
    return _global_config
