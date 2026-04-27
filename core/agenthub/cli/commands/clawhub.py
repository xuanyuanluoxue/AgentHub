# -*- coding: utf-8 -*-
"""
ClawHub 命令 - 与 ClawHub 云端技能市场交互

支持多种安装方式（按优先级）：
1. openclaw CLI (官方主推)
2. clawhub CLI
3. 网页下载 (最后备选)
"""

import click
import json
import subprocess
import urllib.request
import urllib.parse
import re
import tempfile
import shutil
from pathlib import Path
from typing import Optional

CLAWHUB_URL = "https://clawhub.ai"


class ClawHubError(Exception):
    """ClawHub 相关错误"""
    pass


def _get_config_value(key: str) -> Optional[str]:
    """从 AgentHub 配置获取值"""
    try:
        from agenthub.core.config import get_config
        cfg = get_config()
        return cfg.get(key)
    except:
        return None


def _check_cli(cli_name: str, args: list = None) -> bool:
    """检查 CLI 是否可用"""
    try:
        cmd = [cli_name] + (args or ["--version"])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except:
        return False


def _has_openclaw() -> bool:
    """检查 OpenClaw CLI 是否可用"""
    return _check_cli("openclaw", ["skills", "--version"])


def _has_clawhub() -> bool:
    """检查 clawhub CLI 是否可用"""
    # 方法1: 检查 clawhub 是否直接安装（可能不在 PATH 中）
    clawhub_paths = [
        "clawhub",
        "C:/Users/Chatxavier/AppData/Roaming/npm/clawhub",
        "C:/Users/Chatxavier/AppData/Roaming/npm/clawhub.cmd",
    ]
    for path in clawhub_paths:
        try:
            result = subprocess.run(
                [path, "--help"],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )
            if result.returncode == 0 and "ClawHub" in result.stdout:
                return True
        except:
            pass

    # 方法2: 尝试 npx（通过 shell）
    try:
        result = subprocess.run(
            "npx clawhub@latest --help",
            capture_output=True,
            text=True,
            timeout=30,
            shell=True
        )
        return result.returncode == 0 and "ClawHub" in result.stdout
    except:
        pass

    return False


def _run_command(cmd: list, timeout: int = 120) -> tuple:
    """运行命令并返回 (returncode, stdout, stderr)"""
    # Windows 上需要 shell=True 才能找到 npx/clawhub
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        raise ClawHubError("命令执行超时")
    except FileNotFoundError:
        raise ClawHubError(f"未找到命令: {cmd[0] if isinstance(cmd, list) else cmd}")
    except Exception as e:
        raise ClawHubError(f"执行失败: {e}")


def _parse_skill_page(html: str, skill_path: str) -> dict:
    """从 HTML 页面解析 skill 信息"""
    info = {
        "name": skill_path.split("/")[-1] if "/" in skill_path else skill_path,
        "path": skill_path,
        "description": "",
        "author": "",
        "version": "",
        "downloads": 0,
        "stars": 0,
        "readme": "",
    }

    title_match = re.search(r'<title>([^<]+)</title>', html)
    if title_match:
        info["name"] = title_match.group(1).split("—")[0].strip()

    desc_match = re.search(r'class="[^"]*description[^"]*">([^<]+)', html)
    if desc_match:
        info["description"] = desc_match.group(1).strip()

    downloads_match = re.search(r'([\d.]+k?)\s*downloads', html)
    if downloads_match:
        info["downloads"] = downloads_match.group(1)

    stars_match = re.search(r'⭐\s*([\d.]+[km]?)', html)
    if stars_match:
        info["stars"] = stars_match.group(1)

    # 尝试提取 README 内容 (在 <pre><code> 或 <p> 标签中)
    readme_match = re.search(r'GitHub Skill\s*\n(.+?)(?=Comments|Loading|$)', html, re.DOTALL)
    if readme_match:
        info["readme"] = readme_match.group(1).strip()

    return info


@click.group()
def clawhub():
    """ClawHub 云端技能市场交互"""
    pass


@clawhub.command("search")
@click.argument("query")
@click.option("--page", "-p", default=1, help="页码")
def search(query, page):
    """搜索 ClawHub 上的 Skills"""
    click.echo(f"🔍 在 ClawHub 搜索: {query}")
    click.echo()

    # 尝试用 openclaw 或 clawhub CLI
    if _has_openclaw():
        click.echo("📡 使用 OpenClaw CLI 搜索...")
        returncode, stdout, stderr = _run_command(["openclaw", "skills", "search", query])
        if returncode == 0:
            click.echo(stdout)
            return
        click.echo(f"⚠️  OpenClaw 搜索失败: {stderr}")

    if _has_clawhub():
        click.echo("📡 使用 clawhub CLI 搜索...")
        returncode, stdout, stderr = _run_command(["npx", "clawhub@latest", "search", query])
        if returncode == 0:
            click.echo(stdout)
            return
        click.echo(f"⚠️  clawhub 搜索失败: {stderr}")

    # CLI 都不可用，提示用户
    click.echo("⚠️  未找到 OpenClaw 或 clawhub CLI")
    click.echo()
    click.echo("💡 安装方式:")
    click.echo("   # OpenClaw (官方主推)")
    click.echo("   npm install -g openclaw")
    click.echo()
    click.echo("   # 或 clawhub")
    click.echo("   npm install -g clawhub@latest")
    click.echo()
    click.echo(f"   或访问 {CLAWHUB_URL}/skills 直接搜索")


@clawhub.command("browse")
@click.option("--category", "-c", default=None, help="分类筛选")
def browse(category):
    """浏览 ClawHub Skills"""
    click.echo("🌐 ClawHub 技能市场")
    click.echo("=" * 50)
    click.echo()
    click.echo("💡 请访问以下网址浏览 Skills:")
    if category:
        click.echo(f"   {CLAWHUB_URL}/skills?category={category}")
    else:
        click.echo(f"   {CLAWHUB_URL}/skills")
    click.echo()
    click.echo("   找到后用 `agenthub clawhub install <slug>` 安装")


@clawhub.command("install")
@click.argument("skill_path")
@click.option("--source", "-s", type=click.Choice(["auto", "openclaw", "clawhub", "web"]), default="auto", help="安装来源")
def install(skill_path, source):
    """
    从 ClawHub 安装 Skill 到本地

    用法:
      agenthub clawhub install <slug>              # 如: github, github-cli
      agenthub clawhub install <owner/repo>        # 如: steipete/github (会自动转换)
      agenthub clawhub install <url>               # 如: https://clawhub.ai/steipete/github
    """
    click.echo(f"📦 从 ClawHub 安装 Skill: {skill_path}")

    # 解析 URL
    if skill_path.startswith("http"):
        parts = skill_path.rstrip("/").split("/")
        skill_path = parts[-1]  # URL 只取最后一个部分作为 slug

    # 解析 owner/name 格式 (转换为 slug)
    if "/" in skill_path:
        # steipete/github -> github (取第二部分)
        # 但有些 skill slug 就是 owner/repo 格式
        # 尝试直接用 slug，如果失败再用搜索
        pass

    click.echo(f"   Skill: {skill_path}")

    # 获取 skill 信息
    click.echo("\n📡 获取 Skill 信息...")
    info = _fetch_skill_info(skill_path)
    if info:
        click.echo(f"   名称: {info['name']}")
        click.echo(f"   描述: {info['description'][:50]}..." if info['description'] else "")

    # 根据 source 选择安装方式
    success = False

    if source == "auto":
        # 自动选择：openclaw > clawhub > web
        if _has_openclaw():
            click.echo("\n📡 使用 OpenClaw CLI 安装 (官方推荐)...")
            success = _install_with_openclaw(skill_path)
        elif _has_clawhub():
            click.echo("\n📡 使用 clawhub CLI 安装...")
            success = _install_with_clawhub(skill_path)
        else:
            click.echo("\n📡 尝试网页安装...")
            success = _install_from_web(skill_path, info)

    elif source == "openclaw":
        if not _has_openclaw():
            click.echo("❌ OpenClaw CLI 未安装")
            click.echo("   npm install -g openclaw")
            return
        success = _install_with_openclaw(skill_path)

    elif source == "clawhub":
        if not _has_clawhub():
            click.echo("❌ clawhub CLI 未安装")
            click.echo("   npm install -g clawhub@latest")
            return
        success = _install_with_clawhub(skill_path)

    elif source == "web":
        success = _install_from_web(skill_path, info)

    if success:
        click.echo("\n✅ 安装完成!")
        click.echo("   运行 `agenthub skill list` 查看")
    else:
        click.echo("\n❌ 安装失败")
        click.echo(f"   请手动访问 {CLAWHUB_URL}/skills/{skill_path}")


def _install_with_openclaw(skill_path: str) -> bool:
    """使用 OpenClaw CLI 安装"""
    try:
        returncode, stdout, stderr = _run_command(
            ["openclaw", "skills", "install", skill_path]
        )
        if returncode == 0:
            click.echo(f"   {stdout}")
            _sync_to_agenthub(skill_path)
            return True
        else:
            click.echo(f"   ⚠️  {stderr}")
            return False
    except ClawHubError as e:
        click.echo(f"   ❌ {e}")
        return False


def _install_with_clawhub(skill_path: str) -> bool:
    """使用 clawhub CLI 安装到 AgentHub skills 目录"""
    try:
        # 安装到 ~/.agenthub/skills
        skills_dir = Path.home() / ".agenthub" / "skills"
        returncode, stdout, stderr = _run_command(
            ["npx", "clawhub@latest", "install", skill_path, "--dir", str(skills_dir)]
        )
        if returncode == 0:
            click.echo(f"   {stdout.strip()}")
            _sync_to_agenthub(skill_path)
            return True
        else:
            click.echo(f"   ⚠️  {stderr.strip()}")
            return False
    except ClawHubError as e:
        click.echo(f"   ❌ {e}")
        return False


def _install_from_web(skill_path: str, info: dict = None) -> bool:
    """从网页下载 SKILL.md 并安装"""
    if not info:
        info = _fetch_skill_info(skill_path)

    if not info or not info.get("readme"):
        click.echo("   ⚠️  无法获取 README，尝试下载 SKILL.md...")

        # 尝试直接从 GitHub 下载
        github_urls = [
            f"https://raw.githubusercontent.com/{skill_path}/main/SKILL.md",
            f"https://raw.githubusercontent.com/{skill_path}/master/SKILL.md",
        ]

        for url in github_urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "AgentHub/1.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    content = resp.read().decode("utf-8")
                    if "SKILL" in content or "#" in content:
                        return _install_skill_md(skill_path, content)
            except:
                continue

        click.echo("   ❌ 无法下载 SKILL.md")
        return False

    # 使用页面中的 README 内容
    return _install_skill_md(skill_path, info["readme"])


def _install_skill_md(skill_path: str, content: str) -> bool:
    """安装 SKILL.md 内容到本地"""
    try:
        name = skill_path.split("/")[-1]
        temp_dir = Path(tempfile.mkdtemp(prefix="agenthub_skill_"))
        skill_file = temp_dir / "SKILL.md"
        skill_file.write_text(content, encoding="utf-8")

        # 尝试从内容中提取名称
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip().lower().replace(" ", "-")

        from agenthub.core.skill.registry import SkillRegistry, RegistryError

        registry = SkillRegistry()
        info = registry.register(str(temp_dir))

        click.echo(f"   ✅ 安装到: {info.path}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True

    except RegistryError as e:
        click.echo(f"   ❌ 注册失败: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False
    except Exception as e:
        click.echo(f"   ❌ 安装失败: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False


def _fetch_skill_info(skill_path: str) -> Optional[dict]:
    """获取 Skill 信息"""
    url = f"{CLAWHUB_URL}/{skill_path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgentHub/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
            return _parse_skill_page(html, skill_path)
    except:
        return None


def _sync_to_agenthub(skill_path: str):
    """同步到 AgentHub 注册表"""
    try:
        from agenthub.core.skill.registry import SkillRegistry
        registry = SkillRegistry()
        registry.rebuild()
        click.echo("   ✅ 已同步到 AgentHub")
    except Exception as e:
        click.echo(f"   ⚠️  同步失败: {e}")


@clawhub.command("info")
@click.argument("skill_path")
def info(skill_path):
    """查看 ClawHub 上 Skill 的详情"""
    if not skill_path.startswith("http") and "/" not in skill_path:
        click.echo("❌ 格式错误，应为 owner/name")
        return

    if skill_path.startswith("http"):
        parts = skill_path.rstrip("/").split("/")
        skill_path = f"{parts[-2]}/{parts[-1]}"

    click.echo(f"📦 {skill_path}")
    click.echo(f"   页面: {CLAWHUB_URL}/{skill_path}")
    click.echo()

    info_data = _fetch_skill_info(skill_path)
    if info_data:
        click.echo(f"   名称: {info_data['name']}")
        if info_data['description']:
            click.echo(f"   描述: {info_data['description'][:80]}")
        if info_data['downloads']:
            click.echo(f"   下载: {info_data['downloads']}")
        if info_data['stars']:
            click.echo(f"   ⭐: {info_data['stars']}")
    else:
        click.echo("   ⚠️  无法获取详情，请访问网页查看")

    click.echo(f"\n💡 安装: agenthub clawhub install {skill_path}")


@clawhub.command("list-categories")
def list_categories():
    """列出所有 Skill 分类"""
    categories = [
        ("mcp-tools", "MCP Tools"),
        ("prompts", "提示词"),
        ("workflows", "工作流"),
        ("dev-tools", "开发工具"),
        ("data-apis", "数据 & APIs"),
        ("security", "安全"),
        ("automation", "自动化"),
        ("other", "其他"),
    ]

    click.echo("📂 ClawHub 技能分类:\n")
    for cat_id, cat_name in categories:
        click.echo(f"  {cat_id:15} - {cat_name}")
    click.echo(f"\n🌐 浏览: {CLAWHUB_URL}/skills")


@clawhub.command("login")
@click.argument("api_key", required=False)
def login(api_key):
    """设置 ClawHub API Key"""
    if not api_key:
        click.echo("请提供 API Key: agenthub clawhub login YOUR_KEY")
        click.echo("获取 Key: https://clawhub.ai/settings")
        return

    try:
        from agenthub.core.config import get_config
        cfg = get_config()
        cfg.set("clawhub.api_key", api_key)
        cfg.save()
        click.echo("✅ API Key 已保存!")
    except Exception as e:
        click.echo(f"❌ 保存失败: {e}", err=True)


@clawhub.command("logout")
def logout():
    """清除 API Key"""
    try:
        from agenthub.core.config import get_config
        cfg = get_config()
        cfg.set("clawhub.api_key", "")
        cfg.save()
        click.echo("✅ 已清除 API Key")
    except Exception as e:
        click.echo(f"❌ 清除失败: {e}", err=True)


@clawhub.command("status")
def status():
    """检查 ClawHub 连接状态"""
    has_openclaw = _has_openclaw()
    has_clawhub = _has_clawhub()
    api_key = _get_config_value("clawhub.api_key")

    click.echo("🌐 ClawHub 状态")
    click.echo("=" * 40)
    click.echo(f"   网站: {CLAWHUB_URL}")
    click.echo(f"   OpenClaw CLI: {'✅ 已安装' if has_openclaw else '❌ 未安装'}")
    click.echo(f"   clawhub CLI:  {'✅ 已安装' if has_clawhub else '❌ 未安装'}")
    click.echo(f"   API Key: {'✅ 已配置' if api_key else '⚠️  未配置'}")

    click.echo()
    if not has_openclaw and not has_clawhub:
        click.echo("💡 安装 CLI (推荐 OpenClaw):")
        click.echo("   npm install -g openclaw")
    else:
        click.echo("💡 可用命令:")
        click.echo("   agenthub clawhub search <keyword>")
        click.echo("   agenthub clawhub install <owner/name>")


@clawhub.command("setup")
def setup():
    """安装 OpenClaw CLI (官方推荐)"""
    click.echo("📦 安装 OpenClaw CLI...")

    try:
        returncode, stdout, stderr = _run_command(
            ["npm", "install", "-g", "openclaw"]
        )

        if returncode == 0:
            click.echo("✅ 安装成功!")
            click.echo("\n下一步:")
            click.echo("   agenthub clawhub status  # 检查状态")
        else:
            click.echo(f"❌ 安装失败: {stderr}")
            click.echo("\n💡 或使用 clawhub:")
            click.echo("   npm install -g clawhub@latest")

    except FileNotFoundError:
        click.echo("❌ 未找到 npm，请先安装 Node.js")
        click.echo("   https://nodejs.org/")
    except ClawHubError as e:
        click.echo(f"❌ 安装失败: {e}")