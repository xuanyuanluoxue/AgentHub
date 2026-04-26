#!/bin/bash
# AgentHub Web 启动脚本

cd "$(dirname "$0")"

echo "正在安装依赖..."
pip install -r requirements.txt -q

echo "启动 AgentHub Web Server..."
python main.py
