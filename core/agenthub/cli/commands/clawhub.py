# -*- coding: utf-8 -*-
"""
ClawHub 命令 - 与 ClawHub 云端技能市场交互

用户需要先安装 ClawHub CLI 才能使用
安装方式: npm install -g clawhub@latest

设置 API Key (可选): agenthub config set clawhub.api_key YOUR_KEY
"""

import click
import json
import subprocess
import urllib.request
import urllib.parse
import re
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


def _check_clawhub_cli() -> bool:
    """检查 clawhub CLI 是否已安装"""
    try:
        result = subprocess.run(
            ["npx", "clawhub@latest", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except:
        return False


def _run_clawhub(args: list) -> tuple[int, str, str]:
    """运行 clawhub CLI 命令"""
    try:
        result = subprocess.run(
            ["npx", "clawhub@latest"] + args,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        raise ClawHubError("命令执行超时")
    except Exception as e:
        raise ClawHubError(f"执行失败: {e}")


def _get_skill_page(skill_path: str) -> Optional[str]:
    """获取 ClawHub skill 页面的 HTML"""
    url = f"{CLAWHUB_URL}/skills/{skill_path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgentHub/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except:
        return None


def _parse_skill_from_html(html: str, skill_path: str) -> dict:
    """从 HTML 页面解析 skill 信息"""
    info = {
        "name": skill_path.split("/")[-1] if "/" in skill_path else skill_path,
        "path": skill_path,
        "description": "",
        "author": "",
        "version": "",
        "downloads": 0,
        "stars": 0,
    }

    # 简单解析 - 从 HTML 中提取信息
    title_match = re.search(r'<title>([^<]+)</title>', html)
    if title_match:
        info["name"] = title_match.group(1).split("—")[0].strip()

    desc_match = re.search(r'class="[^"]*description[^"]*">([^<]+)', html)
    if desc_match:
        info["description"] = desc_match.group(1).strip()

    downloads_match = re.search(r'([\d.]+k?)·\s*([\d.]+k?)\s*downloads', html)
    if downloads_match:
        info["downloads"] = downloads_match.group(2)

    return info


@click.group()
def clawhub():
    """ClawHub 云端技能市场交互"""
    pass


@clawhub.command("search")
@click.argument("query")
@click.option("--page", "-p", default=1, help="页码")
def search(query, page):
    """搜索 ClawHub 上的 Skills (需要 clawhub CLI)"""
    click.echo(f"🔍 在 ClawHub 搜索: {query}")
    click.echo()

    if not _check_clawhub_cli():
        click.echo("⚠️  需要先安装 ClawHub CLI:")
        click.echo("   npm install -g clawhub@latest")
        click.echo()
        click.echo("   或者直接访问 https://clawhub.com 搜索")
        return

    try:
        returncode, stdout, stderr = _run_clawhub(["search", query])

        if returncode == 0:
            click.echo(stdout)
        else:
            click.echo(f"❌ 搜索失败: {stderr}", err=True)

    except ClawHubError as e:
        click.echo(f"❌ 搜索失败: {e}", err=True)


@clawhub.command("browse")
@click.option("--category", "-c", default=None, help="分类筛选")
@click.option("--page", "-p", default=1, help="页码")
def browse(category, page):
    """浏览 ClawHub Skills 列表"""
    click.echo("🌐 ClawHub 技能市场")
    click.echo("=" * 50)
    click.echo()
    click.echo("💡 请访问以下网址浏览 Skills:")
    click.echo(f"   {CLAWHUB_URL}/skills")
    if category:
        click.echo(f"   {CLAWHUB_URL}/skills?category={category}")
    click.echo()
    click.echo("   找到后用 `agenthub clawhub install <owner/name>` 安装")


@clawhub.command("install")
@click.argument("skill_path")
@click.option("--global-install", "-g", is_flag=True, help="全局安装")
def install(skill_path, global_install):
    """
    从 ClawHub 安装 Skill 到本地

    用法:
      agenthub clawhub install <owner/name>   # 如: steipete/github
      agenthub clawhub install <url>          # 如: https://clawhub.com/steipete/github
    """
    click.echo(f"📦 从 ClawHub 安装 Skill: {skill_path}")

    # 解析 URL 或 owner/name
    if skill_path.startswith("http"):
        # 从 URL 提取 owner/name
        parts = skill_path.rstrip("/").split("/")
        skill_path = f"{parts[-2]}/{parts[-1]}"
    elif "/" not in skill_path:
        click.echo("❌ 格式错误，应为 owner/name 或完整 URL")
        click.echo("   示例: agenthub clawhub install steipete/github")
        return

    click.echo(f"   安装: {skill_path}")

    # 先尝试使用 clawhub CLI
    if _check_clawhub_cli():
        click.echo("\n📡 使用 clawhub CLI 安装...")
        try:
            args = ["install", skill_path]
            if global_install:
                args.insert(1, "-g")

            returncode, stdout, stderr = _run_clawhub(args)

            if returncode == 0:
                click.echo(f"\n✅ 安装成功!")
                click.echo(stdout)

                # 同步到 AgentHub 注册表
                _sync_to_agenthub(skill_path)
            else:
                click.echo(f"❌ 安装失败: {stderr}", err=True)
                click.echo("\n💡 备选方案: 手动下载安装")
                click.echo(f"   1. 访问 {CLAWHUB_URL}/skills/{skill_path}")
                click.echo(f"   2. 下载 SKILL.md")
                click.echo(f"   3. agenthub skill install <path>")

        except ClawHubError as e:
            click.echo(f"❌ 安装失败: {e}", err=True)
    else:
        click.echo("\n⚠️  clawhub CLI 未安装")
        click.echo("   正在尝试通过网页安装...")

        # 备选方案: 从网页获取 SKILL.md 内容
        _install_from_web(skill_path)


def _sync_to_agenthub(skill_path: str):
    """同步 clawhub 安装的 skill 到 AgentHub 注册表"""
    try:
        from agenthub.core.skill.registry import SkillRegistry

        registry = SkillRegistry()
        registry.rebuild()

        click.echo(f"\n✅ 已同步到 AgentHub 注册表")
        click.echo(f"   使用 agenthub skill list 查看已安装的 Skills")

    except Exception as e:
        click.echo(f"\n⚠️  同步失败: {e}", err=True)
        click.echo("   Skill 已安装，但可能需要手动注册")


def _install_from_web(skill_path: str):
    """从 ClawHub 网页获取 SKILL.md 并安装"""
    click.echo("\n📡 获取 Skill 信息...")

    html = _get_skill_page(skill_path)
    if not html:
        click.echo(f"❌ 无法访问 {CLAWHUB_URL}/skills/{skill_path}")
        return

    info = _parse_skill_from_html(html, skill_path)
    click.echo(f"   名称: {info['name']}")
    click.echo(f"   描述: {info['description'][:50]}...")

    # 尝试下载 SKILL.md
    click.echo("\n📥 尝试下载 SKILL.md...")

    readme_urls = [
        f"{CLAWHUB_URL}/skills/{skill_path}/raw/main/SKILL.md",
        f"{CLAWHUB_URL}/skills/{skill_path}/raw/master/SKILL.md",
        f"https://raw.githubusercontent.com/{skill_path}/main/SKILL.md",
        f"https://raw.githubusercontent.com/{skill_path}/master/SKILL.md",
    ]

    skill_md_content = None
    for url in readme_urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AgentHub/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read().decode("utf-8")
                if "SKILL" in content or "#" in content:
                    skill_md_content = content
                    break
        except:
            continue

    if skill_md_content:
        # 保存到临时目录并安装
        import tempfile
        import shutil

        temp_dir = Path(tempfile.mkdtemp(prefix="agenthub_skill_"))
        skill_file = temp_dir / "SKILL.md"
        skill_file.write_text(skill_md_content, encoding="utf-8")

        try:
            from agenthub.core.skill.registry import SkillRegistry, RegistryError

            registry = SkillRegistry()
            info = registry.register(temp_dir)

            click.echo(f"\n✅ 安装成功!")
            click.echo(f"   名称: {info.name}")
            click.echo(f"   版本: {info.version}")
            click.echo(f"   路径: {info.path}")

        except RegistryError as e:
            click.echo(f"❌ 安装失败: {e}", err=True)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        click.echo("❌ 无法下载 SKILL.md")
        click.echo(f"\n💡 请手动安装:")
        click.echo(f"   1. 访问 {CLAWHUB_URL}/skills/{skill_path}")
        click.echo(f"   2. 复制 SKILL.md 内容到本地")
        click.echo(f"   3. agenthub skill install <path>")


@clawhub.command("info")
@click.argument("skill_path")
def info(skill_path):
    """查看 ClawHub 上 Skill 的详情"""
    if "/" not in skill_path and not skill_path.startswith("http"):
        click.echo("❌ 格式错误，应为 owner/name")
        return

    if skill_path.startswith("http"):
        parts = skill_path.rstrip("/").split("/")
        skill_path = f"{parts[-2]}/{parts[-1]}"

    click.echo(f"📦 {skill_path}")
    click.echo(f"   页面: {CLAWHUB_URL}/skills/{skill_path}")
    click.echo()

    html = _get_skill_page(skill_path)
    if html:
        info_data = _parse_skill_from_html(html, skill_path)
        click.echo(f"   名称: {info_data['name']}")
        if info_data['description']:
            click.echo(f"   描述: {info_data['description'][:80]}")
        if info_data['downloads']:
            click.echo(f"   下载: {info_data['downloads']}")
    else:
        click.echo("   无法获取详情，请访问网页查看")

    click.echo(f"\n💡 安装命令: agenthub clawhub install {skill_path}")


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
@click.argument("api_key")
def login(api_key):
    """设置 ClawHub API Key (用于 CLI)"""
    try:
        from agenthub.core.config import get_config

        cfg = get_config()
        cfg.set("clawhub.api_key", api_key)
        cfg.save()

        click.echo("✅ ClawHub API Key 已保存!")
        click.echo("\n💡 如果需要 CLI 认证，可能还需要:")
        click.echo("   npx clawhub@latest login")

    except Exception as e:
        click.echo(f"❌ 保存失败: {e}", err=True)


@clawhub.command("logout")
def logout():
    """清除 ClawHub API Key"""
    try:
        from agenthub.core.config import get_config

        cfg = get_config()
        cfg.set("clawhub.api_key", "")
        cfg.save()

        click.echo("✅ 已清除 ClawHub API Key")

    except Exception as e:
        click.echo(f"❌ 清除失败: {e}", err=True)


@clawhub.command("status")
def status():
    """检查 ClawHub 连接状态"""
    api_key = _get_config_value("clawhub.api_key")
    has_cli = _check_clawhub_cli()

    click.echo("🌐 ClawHub 状态")
    click.echo("=" * 40)
    click.echo(f"   网站: {CLAWHUB_URL}")
    click.echo(f"   CLI:  {'✅ 已安装' if has_cli else '❌ 未安装'}")

    if api_key:
        click.echo(f"   API Key: ✅ 已配置")
    else:
        click.echo(f"   API Key: ⚠️  未配置")

    click.echo()
    if not has_cli:
        click.echo("💡 安装 CLI: npm install -g clawhub@latest")
    else:
        click.echo("💡 可用命令:")
        click.echo("   agenthub clawhub search <keyword>")
        click.echo("   agenthub clawhub install <owner/name>")


@clawhub.command("setup")
def setup():
    """安装 clawhub CLI"""
    click.echo("📦 安装 ClawHub CLI...")

    try:
        result = subprocess.run(
            ["npm", "install", "-g", "clawhub@latest"],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            click.echo("✅ 安装成功!")
            click.echo("\n下一步:")
            click.echo("   agenthub clawhub status  # 检查状态")
            click.echo("   agenthub clawhub browse  # 浏览 Skills")
        else:
            click.echo(f"❌ 安装失败: {result.stderr}", err=True)
            click.echo("\n💡 或手动安装:")
            click.echo("   npm install -g clawhub@latest")

    except FileNotFoundError:
        click.echo("❌ 未找到 npm，请先安装 Node.js")
        click.echo("   https://nodejs.org/")
    except Exception as e:
        click.echo(f"❌ 安装失败: {e}", err=True)


def _extract_skill_id(url: str) -> str:
    """从 URL 提取 Skill ID"""
    parts = url.rstrip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return url