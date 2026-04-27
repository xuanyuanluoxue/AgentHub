# -*- coding: utf-8 -*-
"""
ClawHub 命令 - 与 ClawHub 云端技能市场交互

用户需要先配置 ClawHub API Key 才能使用搜索功能
设置方式: agenthub config set clawhub.api_key YOUR_KEY
"""

import click
import json
import urllib.request
import urllib.parse
import urllib.error
import tempfile
import shutil
import zipfile
import io
from pathlib import Path
from typing import Optional

CLAWHUB_API_BASE = "https://clawhub.com"
CLAWHUB_API_V1 = "https://claudebot-8-0-0-0-51d8d7f9f0cb4897abd5b2fb42d6b1b0.convex.cloud"
CLAWHUB_SKILLS_PER_PAGE = 20


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


def _http_get(url: str, headers: dict = None, timeout: int = 30) -> dict:
    """发送 HTTP GET 请求"""
    default_headers = {
        "Accept": "application/json",
        "User-Agent": "AgentHub/1.0"
    }
    if headers:
        default_headers.update(headers)

    try:
        req = urllib.request.Request(url, headers=default_headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise ClawHubError("需要登录，请先设置 ClawHub API Key: agenthub config set clawhub.api_key YOUR_KEY")
        elif e.code == 404:
            raise ClawHubError(f"资源不存在: {url}")
        else:
            raise ClawHubError(f"HTTP 错误 {e.code}: {e.reason}")
    except Exception as e:
        raise ClawHubError(f"网络请求失败: {e}")


def _http_post(url: str, data: dict, headers: dict = None, timeout: int = 30) -> dict:
    """发送 HTTP POST 请求"""
    default_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "AgentHub/1.0"
    }
    if headers:
        default_headers.update(headers)

    try:
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=default_headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise ClawHubError("需要登录，请先设置 ClawHub API Key: agenthub config set clawhub.api_key YOUR_KEY")
        raise ClawHubError(f"HTTP 错误 {e.code}: {e.reason}")
    except Exception as e:
        raise ClawHubError(f"网络请求失败: {e}")


def _get_auth_headers() -> dict:
    """获取认证头"""
    api_key = _get_config_value("clawhub.api_key")
    if api_key:
        return {"Authorization": f"Bearer {api_key}"}
    return {}


@click.group()
def clawhub():
    """ClawHub 云端技能市场交互"""
    pass


@clawhub.command("search")
@click.argument("query")
@click.option("--page", "-p", default=1, help="页码")
@click.option("--limit", "-l", default=10, help="每页数量")
def search(query, page, limit):
    """搜索 ClawHub 上的 Skills"""
    click.echo(f"🔍 在 ClawHub 搜索: {query}")
    click.echo()

    headers = _get_auth_headers()

    try:
        encoded_query = urllib.parse.quote(query)
        url = f"{CLAWHUB_API_V1}/api/skills?q={encoded_query}&limit={limit}&page={page}"

        data = _http_get(url, headers=headers)

        items = data.get("items", []) or data.get("results", []) or []

        if items:
            click.echo(f"找到 {len(items)} 个结果:\n")
            for skill in items:
                name = skill.get("name", "unnamed")
                desc = skill.get("description", skill.get("tagline", ""))
                author = skill.get("author", skill.get("owner", ""))
                downloads = skill.get("downloads", skill.get("installCount", 0))

                click.echo(f"  📦 {name}")
                if desc:
                    click.echo(f"     {desc[:60]}...")
                if author:
                    click.echo(f"     作者: {author}")
                if downloads:
                    click.echo(f"     ⬇️  {downloads} 下载")
                click.echo()
                click.echo(f"  安装命令: agenthub clawhub install {name}")
                click.echo()
        else:
            click.echo("⚠️  未找到结果或需要登录")
            click.echo("   如需登录，请设置 API Key:")
            click.echo("   agenthub config set clawhub.api_key YOUR_KEY")
            click.echo()
            click.echo("   然后重试: agenthub clawhub search <keyword>")

    except ClawHubError as e:
        click.echo(f"❌ 搜索失败: {e}", err=True)
        click.echo("\n💡 备选方案:")
        click.echo("   1. 访问 https://clawhub.com 直接搜索")
        click.echo("   2. 手动下载后用 `agenthub skill install <path>` 安装")


@clawhub.command("browse")
@click.option("--category", "-c", default=None, help="分类筛选 (mcp-tools/prompts/workflows/dev-tools/data-apis/security/automation/other)")
@click.option("--page", "-p", default=1, help="页码")
@click.option("--limit", "-l", default=20, help="每页数量")
def browse(category, page, limit):
    """浏览 ClawHub Skills 列表"""
    click.echo("🌐 ClawHub 技能市场")
    click.echo("=" * 50)

    headers = _get_auth_headers()

    try:
        params = f"limit={limit}&page={page}"
        if category:
            params += f"&category={category}"

        url = f"{CLAWHUB_API_V1}/api/skills?{params}"

        data = _http_get(url, headers=headers)

        items = data.get("items", []) or data.get("results", []) or []

        if items:
            click.echo(f"\n找到 {len(items)} 个 Skills:\n")
            for skill in items:
                name = skill.get("name", "unnamed")
                desc = skill.get("description", skill.get("tagline", ""))[:50]
                click.echo(f"  📦 {name} - {desc}...")
                click.echo(f"     安装: agenthub clawhub install {name}")
                click.echo()
        else:
            click.echo("⚠️  未找到结果，可能需要登录")
            click.echo("   设置 API Key: agenthub config set clawhub.api_key YOUR_KEY")

        click.echo(f"\n💡 完整浏览请访问: https://clawhub.com/skills")

    except ClawHubError as e:
        click.echo(f"❌ 浏览失败: {e}", err=True)


@clawhub.command("install")
@click.argument("skill_id_or_url")
@click.option("--name", "-n", default=None, help="指定安装后的名称")
def install(skill_id_or_url, name):
    """
    从 ClawHub 安装 Skill 到本地

    用法:
      agenthub clawhub install <skill-name>   # 直接安装
      agenthub clawhub install <url>           # 从 URL 安装
    """
    click.echo(f"📦 从 ClawHub 安装 Skill: {skill_id_or_url}")

    headers = _get_auth_headers()

    # 解析输入
    if skill_id_or_url.startswith("http"):
        skill_id = _extract_skill_id(skill_id_or_url)
    else:
        skill_id = skill_id_or_url

    click.echo(f"   Skill ID: {skill_id}")

    try:
        # 获取 Skill 详情
        click.echo("\n📡 获取 Skill 信息...")
        skill_info = _fetch_skill_info(skill_id, headers)

        if not skill_info:
            click.echo("❌ 未找到该 Skill，可能需要登录或 Skill 不存在")
            click.echo("\n💡 如需登录，请设置 API Key:")
            click.echo("   agenthub config set clawhub.api_key YOUR_KEY")
            return

        skill_name = skill_info.get("name", skill_id)
        click.echo(f"   名称: {skill_name}")
        click.echo(f"   版本: {skill_info.get('version', 'unknown')}")

        # 下载 Skill
        click.echo("\n📥 下载 Skill...")
        temp_dir = _download_skill(skill_info, headers)

        if not temp_dir:
            click.echo("❌ 下载失败")
            return

        # 安装到本地
        from agenthub.core.skill.registry import SkillRegistry, RegistryError

        install_name = name or skill_name
        target_dir = Path.home() / ".agenthub" / "skills" / install_name

        # 如果已存在，先移除
        if target_dir.exists():
            shutil.rmtree(target_dir)

        # 移动临时目录到目标位置
        shutil.move(str(temp_dir), str(target_dir))

        # 注册
        registry = SkillRegistry()
        registry.reload()

        click.echo(f"\n✅ 安装成功!")
        click.echo(f"   名称: {install_name}")
        click.echo(f"   路径: {target_dir}")
        click.echo(f"\n   使用: agenthub skill info {install_name}")

    except ClawHubError as e:
        click.echo(f"❌ 安装失败: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ 安装失败: {e}", err=True)


@clawhub.command("info")
@click.argument("skill_id")
def info(skill_id):
    """查看 ClawHub 上 Skill 的详情"""
    headers = _get_auth_headers()

    try:
        skill_info = _fetch_skill_info(skill_id, headers)

        if not skill_info:
            click.echo("❌ 未找到该 Skill")
            click.echo("\n💡 如需登录，请设置 API Key:")
            click.echo("   agenthub config set clawhub.api_key YOUR_KEY")
            return

        click.echo(f"📦 {skill_info.get('name', skill_id)}")
        click.echo(f"   版本: {skill_info.get('version', 'unknown')}")
        click.echo(f"   描述: {skill_info.get('description', skill_info.get('tagline', 'N/A'))}")
        click.echo(f"   作者: {skill_info.get('author', skill_info.get('owner', 'N/A'))}")
        click.echo(f"   分类: {skill_info.get('category', 'N/A')}")

        downloads = skill_info.get("downloads", skill_info.get("installCount", 0))
        if downloads:
            click.echo(f"   下载: {downloads}")

        rating = skill_info.get("rating", skill_info.get("avgRating", 0))
        if rating:
            click.echo(f"   评分: {rating}")

        tags = skill_info.get("tags", [])
        if tags:
            click.echo(f"   标签: {', '.join(tags)}")

        click.echo(f"\n💡 安装命令: agenthub clawhub install {skill_id}")

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


@clawhub.command("login")
@click.argument("api_key")
def login(api_key):
    """设置 ClawHub API Key"""
    try:
        from agenthub.core.config import get_config

        cfg = get_config()
        cfg.set("clawhub.api_key", api_key)
        cfg.save()

        click.echo("✅ ClawHub API Key 已保存!")
        click.echo("\n测试连接...")
        click.echo("   运行: agenthub clawhub search <keyword>")

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

    if api_key:
        click.echo("✅ 已配置 ClawHub API Key")
        click.echo(f"   Key: {api_key[:8]}...{api_key[-4:]}")
    else:
        click.echo("⚠️  未配置 ClawHub API Key")
        click.echo("\n设置方式:")
        click.echo("   agenthub clawhub login YOUR_API_KEY")
        click.echo("\n获取 API Key: https://clawhub.com/settings")

    click.echo(f"\n🌐 ClawHub: https://clawhub.com")


def _extract_skill_id(url: str) -> str:
    """从 URL 提取 Skill ID"""
    parts = url.rstrip("/").split("/")
    if parts:
        return parts[-1]
    return url


def _fetch_skill_info(skill_id: str, headers: dict = None) -> Optional[dict]:
    """获取 Skill 信息"""
    try:
        url = f"{CLAWHUB_API_V1}/api/skills/{skill_id}"
        return _http_get(url, headers=headers)
    except ClawHubError:
        # 尝试搜索 API
        try:
            url = f"{CLAWHUB_API_V1}/api/skills?q={urllib.parse.quote(skill_id)}&limit=5"
            data = _http_get(url, headers=headers)
            items = data.get("items", []) or data.get("results", []) or []
            for item in items:
                if item.get("name", "").lower() == skill_id.lower():
                    return item
        except:
            pass
    return None


def _download_skill(skill_info: dict, headers: dict = None) -> Optional[Path]:
    """下载 Skill 到临时目录"""
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix="agenthub_skill_"))

        # 尝试多种方式获取 Skill 内容

        # 方式1: 直接下载 ZIP
        download_url = skill_info.get("downloadUrl") or skill_info.get("zipUrl") or skill_info.get("url")
        if download_url:
            try:
                req = urllib.request.Request(download_url, headers={
                    "User-Agent": "AgentHub/1.0",
                    **headers
                })
                with urllib.request.urlopen(req, timeout=60) as resp:
                    zip_data = io.BytesIO(resp.read())

                with zipfile.ZipFile(zip_data, 'r') as zf:
                    zf.extractall(temp_dir)

                # 检查是否解压到了子目录
                subdirs = [d for d in temp_dir.iterdir() if d.is_dir()]
                if len(subdirs) == 1 and (temp_dir / subdirs[0].name / "SKILL.md").exists():
                    # SKILL.md 在子目录中，移动内容到 temp_dir
                    inner_dir = temp_dir / subdirs[0].name
                    for item in inner_dir.iterdir():
                        shutil.move(str(item), str(temp_dir / item.name))
                    shutil.rmtree(inner_dir)

                return temp_dir
            except Exception:
                pass

        # 方式2: 从 sourceUrl 克隆
        source_url = skill_info.get("sourceUrl") or skill_info.get("repo") or skill_info.get("github")
        if source_url and "github.com" in str(source_url):
            try:
                import subprocess
                subprocess.run(["git", "clone", "--depth", "1", source_url, str(temp_dir)],
                             capture_output=True, timeout=60)
                if (temp_dir / "SKILL.md").exists():
                    return temp_dir
                shutil.rmtree(temp_dir)
            except:
                pass

        # 方式3: 直接创建（如果只有元数据）
        name = skill_info.get("name", "unknown")
        skill_md = temp_dir / "SKILL.md"
        skill_md.write_text(f"""# {name}

{skill_info.get('description', skill_info.get('tagline', ''))}

## 安装信息

- 版本: {skill_info.get('version', '1.0.0')}
- 作者: {skill_info.get('author', skill_info.get('owner', 'N/A'))}
- 来源: ClawHub

## 使用说明

请访问 https://clawhub.com/skills/{name} 查看完整文档
""", encoding="utf-8")

        return temp_dir

    except Exception as e:
        return None