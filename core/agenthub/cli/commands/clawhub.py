# -*- coding: utf-8 -*-
"""
ClawHub 命令 - 与 ClawHub 云端技能市场交互
"""

import click
import json
import urllib.request
import urllib.parse
import tempfile
import shutil
from pathlib import Path


CLAWHUB_API_BASE = "https://clawhub.com"
CLAWHUB_SKILLS_PER_PAGE = 20


class ClawHubError(Exception):
    """ClawHub 相关错误"""
    pass


def _http_get(url: str, timeout: int = 30) -> dict:
    """发送 HTTP GET 请求"""
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "AgentHub/1.0"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise ClawHubError(f"网络请求失败: {e}")


def _search_web(query: str) -> list[dict]:
    """
    通过网页搜索 ClawHub Skills
    由于 API 不稳定，使用模拟数据演示
    """
    # 实际实现时应该解析 ClawHub 网页
    # 这里返回空列表，用户可以使用 clawhub browse 交互式浏览
    return []


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

    try:
        # 构造搜索 URL
        encoded_query = urllib.parse.quote(query)
        url = f"{CLAWHUB_API_BASE}/api/skills?q={encoded_query}&page={page}"

        # 尝试 API
        data = _http_get(url)

        if data.get("skills"):
            skills = data["skills"]
            click.echo(f"找到 {len(skills)} 个结果:\n")
            for skill in skills:
                click.echo(f"  📦 {skill.get('name', 'unnamed')}")
                click.echo(f"     {skill.get('description', '')}")
                if skill.get("downloads"):
                    click.echo(f"     ⬇️  {skill.get('downloads')} 下载")
                click.echo()
        else:
            # API 不可用，提示使用 browse
            click.echo("⚠️  搜索 API 暂时不可用")
            click.echo("   建议使用 `agenthub clawhub browse` 交互式浏览")

    except ClawHubError as e:
        click.echo(f"❌ 搜索失败: {e}", err=True)
        click.echo("\n💡 备选方案:")
        click.echo("   1. 访问 https://clawhub.com 直接搜索")
        click.echo("   2. 使用 `agenthub clawhub browse` 交互式浏览")
        click.echo("   3. 手动下载后用 `agenthub skill install <path>` 安装")


@clawhub.command("browse")
@click.option("--category", "-c", default=None, help="分类筛选")
@click.option("--page", "-p", default=1, help="页码")
def browse(category, page):
    """交互式浏览 ClawHub Skills"""
    click.echo("🌐 ClawHub 技能市场")
    click.echo("=" * 50)
    click.echo(f"浏览分类: {category or '全部'}")
    click.echo(f"页码: {page}")
    click.echo()
    click.echo("💡 请访问 https://clawhub.com/skills 直接浏览")
    click.echo("   找到想要的 Skill 后，用 `agenthub clawhub install <url>` 安装")


@clawhub.command("install")
@click.argument("skill_id_or_url")
@click.option("--name", "-n", default=None, help="指定安装后的名称")
def install(skill_id_or_url, name):
    """
    从 ClawHub 安装 Skill 到本地

    用法:
      agenthub clawhub install <skill-id>     # 安装指定 ID
      agenthub clawhub install <url>          # 从 URL 安装
    """
    click.echo(f"📦 从 ClawHub 安装 Skill...")

    # 解析输入
    if skill_id_or_url.startswith("http"):
        # URL 形式 - 提取 skill ID
        skill_id = _extract_skill_id(skill_id_or_url)
    else:
        skill_id = skill_id_or_url

    click.echo(f"   Skill ID: {skill_id}")

    try:
        # 获取 Skill 详情
        skill_info = _fetch_skill_info(skill_id)

        if not skill_info:
            click.echo("❌ 未找到该 Skill，可能已被删除或不存在")
            return

        # 下载 Skill
        click.echo(f"\n📥 下载 {skill_info['name']}...")
        temp_dir = _download_skill(skill_info)

        if not temp_dir:
            click.echo("❌ 下载失败")
            return

        # 安装到本地
        from agenthub.core.skill.registry import SkillRegistry, RegistryError

        registry = SkillRegistry()
        try:
            info = registry.register(temp_dir)
            click.echo(f"\n✅ 安装成功!")
            click.echo(f"   名称: {info.name}")
            click.echo(f"   版本: {info.version}")
            click.echo(f"   路径: {info.path}")
        except RegistryError as e:
            click.echo(f"❌ 安装失败: {e}", err=True)

        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

    except ClawHubError as e:
        click.echo(f"❌ 安装失败: {e}", err=True)


@clawhub.command("info")
@click.argument("skill_id")
def info(skill_id):
    """查看 ClawHub 上 Skill 的详情"""
    try:
        skill_info = _fetch_skill_info(skill_id)

        if not skill_info:
            click.echo("❌ 未找到该 Skill")
            return

        click.echo(f"📦 {skill_info.get('name', skill_id)}")
        click.echo(f"   版本: {skill_info.get('version', 'unknown')}")
        click.echo(f"   描述: {skill_info.get('description', 'N/A')}")
        click.echo(f"   作者: {skill_info.get('author', 'N/A')}")
        click.echo(f"   分类: {skill_info.get('category', 'N/A')}")

        if skill_info.get("downloads"):
            click.echo(f"   下载: {skill_info['downloads']}")
        if skill_info.get("rating"):
            click.echo(f"   评分: {skill_info['rating']}")
        if skill_info.get("tags"):
            click.echo(f"   标签: {', '.join(skill_info['tags'])}")

    except ClawHubError as e:
        click.echo(f"❌ 获取详情失败: {e}", err=True)


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


def _extract_skill_id(url: str) -> str:
    """从 URL 提取 Skill ID"""
    # https://clawhub.com/skills/github → github
    parts = url.rstrip("/").split("/")
    if parts:
        return parts[-1]
    return url


def _fetch_skill_info(skill_id: str) -> dict | None:
    """
    获取 Skill 信息

    实际实现时应该调用 ClawHub API
    这里使用模拟数据
    """
    # 尝试 API
    try:
        url = f"{CLAWHUB_API_BASE}/api/skills/{skill_id}"
        return _http_get(url)
    except:
        pass

    # 如果 API 失败，返回 None
    # 用户需要手动从网页获取
    return None


def _download_skill(skill_info: dict) -> Path | None:
    """
    下载 Skill 到临时目录

    返回临时目录路径，使用后需要清理
    """
    try:
        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp(prefix="agenthub_skill_"))

        # 实际实现时应该从 skill_info["download_url"] 下载
        # 这里假设 skill_info 包含 SKILL.md 内容或下载链接

        return temp_dir

    except Exception:
        return None