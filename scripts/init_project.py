# -*- coding: utf-8 -*-
"""
AgentHub 快速初始化脚本

使用方法:
    python scripts/init_project.py

其他 AI 工具调用此脚本进行标准化初始化。
"""

import sys
import os
from pathlib import Path

# ===== 配置 =====
PROJECT_ROOT = Path("D:/code/github/agenthub")
SRC_ROOT = PROJECT_ROOT / "src"


def check_environment():
    """第一步：环境检测"""
    print("=" * 50)
    print("第一步：环境检测")
    print("=" * 50)

    errors = []

    # Python 版本
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        errors.append(f"Python 版本过低: {version.major}.{version.minor}, 需要 ≥3.10")
    else:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")

    # 项目路径
    if not PROJECT_ROOT.exists():
        errors.append(f"项目目录不存在: {PROJECT_ROOT}")
    else:
        print(f"  ✅ 项目目录: {PROJECT_ROOT}")

    # 必要文件
    required_files = [
        PROJECT_ROOT / "pyproject.toml",
        PROJECT_ROOT / "src" / "agenthub" / "__init__.py",
        PROJECT_ROOT / "src" / "agenthub" / "cli" / "main.py",
    ]
    for f in required_files:
        if not f.exists():
            errors.append(f"必要文件缺失: {f}")
        else:
            print(f"  ✅ {f.name}")

    if errors:
        print("\n  ❌ 环境检测失败:")
        for e in errors:
            print(f"     - {e}")
        return False

    print("\n  ✅ 环境检测通过")
    return True


def install_dependencies():
    """第二步：安装依赖"""
    print("\n" + "=" * 50)
    print("第二步：安装依赖")
    print("=" * 50)

    # 添加项目路径
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))

    # 安装核心包
    print("\n  📦 安装核心依赖...")
    os.chdir(PROJECT_ROOT)

    # 使用 Python 内部 pip
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"\n  ⚠️  pip install 失败（可能需要管理员权限）")
        print(f"     错误: {result.stderr[:200]}")
        print("\n  请手动执行:")
        print(f"     pip install -e {PROJECT_ROOT}")
    else:
        print("  ✅ 核心依赖安装完成")

    return True


def initialize_project():
    """第三步：初始化项目"""
    print("\n" + "=" * 50)
    print("第三步：初始化项目")
    print("=" * 50)

    home = Path.home()
    config_dir = home / ".agenthub"
    skills_dir = config_dir / "skills"
    logs_dir = config_dir / "logs"

    # 创建目录
    for d in [config_dir, skills_dir, logs_dir]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d}")

    # 创建配置文件
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        config_file.write_text("""# AgentHub 配置文件
version: "0.1.0"

# 数据目录
data_dir: "~/.agenthub"

# Skill 注册表路径
skills_dir: "~/.agenthub/skills"

# Agent 配置
agents:
  max_concurrent: 4
  default_timeout: 300

# 日志配置
logging:
  level: "INFO"
  file: "~/.agenthub/logs/agenthub.log"
""")
        print(f"  ✅ 配置文件: {config_file}")

    print("\n  ✅ 项目初始化完成")


def load_core_modules():
    """第四步：加载核心模块"""
    print("\n" + "=" * 50)
    print("第四步：加载核心模块")
    print("=" * 50)

    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))

    modules = {}

    try:
        from agenthub.core.skill.registry import SkillRegistry
        registry = SkillRegistry()
        modules["registry"] = registry
        print(f"  ✅ SkillRegistry: {len(registry.list_all())} skills")
    except ImportError as e:
        print(f"  ⚠️  SkillRegistry 导入失败: {e}")

    try:
        from agenthub.core.agent.router import AgentRouter
        router = AgentRouter()
        modules["router"] = router
        print(f"  ✅ AgentRouter: {len(router._adapters)} adapters")
    except ImportError as e:
        print(f"  ⚠️  AgentRouter 导入失败: {e}")

    try:
        from agenthub.core.database import DatabaseManager
        db = DatabaseManager()
        modules["db"] = db
        print(f"  ✅ DatabaseManager: {db.db_path}")
    except ImportError as e:
        print(f"  ⚠️  DatabaseManager 导入失败: {e}")

    print("\n  ✅ 核心模块加载完成")
    return modules


def verify_installation():
    """第五步：验证安装"""
    print("\n" + "=" * 50)
    print("第五步：验证安装")
    print("=" * 50)

    results = {
        "environment": False,
        "dependencies": False,
        "initialization": False,
        "core_modules": False,
    }

    # 环境
    results["environment"] = (
        sys.version_info.major >= 3
        and sys.version_info.minor >= 10
        and PROJECT_ROOT.exists()
    )

    # 初始化
    config_dir = Path.home() / ".agenthub"
    results["initialization"] = config_dir.exists()

    # 核心模块
    try:
        sys.path.insert(0, str(SRC_ROOT))
        from agenthub.core.skill.registry import SkillRegistry
        from agenthub.core.database import DatabaseManager
        results["core_modules"] = True
    except ImportError:
        pass

    print("\n  验证结果:")
    for name, passed in results.items():
        status = "✅" if passed else "⚠️ "
        print(f"     {status} {name}")

    all_passed = all(results.values())
    if all_passed:
        print("\n  🎉 AgentHub 安装验证通过!")
    else:
        print("\n  ⚠️  部分验证未通过，请检查上述输出")

    return results


def print_summary():
    """打印总结"""
    print("\n" + "=" * 50)
    print("初始化完成总结")
    print("=" * 50)

    print("""
  📁 项目路径: D:/code/github/agenthub
  📦 Skills目录: ~/.agenthub/skills
  💾 数据库: ~/.agenthub/agenthub.db
  🌐 Web端口: 5173

  常用命令:
    agenthub --help              # 查看帮助
    agenthub skill list          # 列出Skills
    agenthub agent list          # 列出Agents
    agenthub task submit "..."   # 提交任务

  Web UI:
    打开: web/frontend/index.html
    或: python web/backend/main.py

  其他 AI 工具接入:
    1. sys.path.insert(0, 'D:/code/github/agenthub/src')
    2. from agenthub.core.skill.registry import SkillRegistry
    3. registry = SkillRegistry()
""")


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("🚀 AgentHub 初始化脚本")
    print("=" * 50)

    # 执行初始化步骤
    if not check_environment():
        sys.exit(1)

    install_dependencies()
    initialize_project()
    load_core_modules()
    verify_installation()
    print_summary()


if __name__ == "__main__":
    main()
