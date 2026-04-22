#!/bin/bash

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env

# 初始化数据库和管理员账号
python -m app.db.init_admin

echo "✅ 后端初始化完成"
echo "运行命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
