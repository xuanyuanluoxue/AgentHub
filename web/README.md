# AgentHub Web

> AgentHub AI 工具管理平台的 Web 管理界面

## 快速开始

### 前端（纯静态）

直接用浏览器打开 `frontend/index.html` 即可预览。

### 后端（FastAPI）

```bash
cd backend
pip install -r requirements.txt
python main.py
```

然后访问 http://localhost:5173

## 功能

- 📊 **仪表盘** - 系统状态概览
- 📦 **技能库** - 安装/管理 Skill
- 🤖 **Agent 管理** - 查看 Agent 状态和任务
- ⚙️ **设置** - 同步目标配置

## 技术栈

- 前端：Vue 3 + TailwindCSS（CDN）
- 后端：FastAPI + uvicorn
- 通信：REST API + Axios
