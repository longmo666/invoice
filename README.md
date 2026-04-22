# 智能票据识别平台

基于 AI 的发票与票据自动识别系统，支持增值税普通发票、高铁票等多种票据类型的上传、识别、复核、导出。

## 功能概览

- **发票识别** — 上传图片/PDF，AI 自动提取发票号码、金额、买卖方等结构化字段
- **高铁票识别** — 识别车次、座位、票价、乘客信息等
- **待复核** — 低置信度结果进入人工复核队列，确认后入库
- **记录管理** — 分页浏览、搜索、批量删除、导出 CSV/Excel
- **文件清洗** — 批量文件分类整理（独立模块）
- **AI 配置管理** — 支持 OpenAI / Anthropic / Gemini / 智谱等多家 AI 服务商，可在线测试连接和样本识别
- **用户体系** — 注册/登录、配额管理、密码修改
- **管理员后台** — 用户管理、全局任务查看、AI 配置

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 19 + TypeScript + Vite + Tailwind CSS |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| AI 接入 | 多供应商统一抽象（OpenAI / Anthropic / Gemini / 智谱 OCR） |
| 部署 | Nginx（前端静态托管）+ Uvicorn（后端 ASGI） |

## 项目结构

```
invoice/
├── src/                          # 前端源码
│   ├── app/
│   │   ├── components/           # 页面组件
│   │   │   ├── Layout.tsx        # 用户端布局（侧边栏 + 子 Tab）
│   │   │   ├── AdminLayout.tsx   # 管理端布局
│   │   │   ├── UploadRecognition.tsx  # 上传识别页（壳组件）
│   │   │   ├── PendingReview.tsx      # 待复核页（壳组件）
│   │   │   ├── RecordList.tsx         # 记录列表页
│   │   │   ├── recognition-upload/    # 上传模块 hook + 类型
│   │   │   ├── pending-review/        # 复核模块 hook
│   │   │   ├── admin-recognition/     # 管理端识别模块
│   │   │   └── ui/                    # shadcn/ui 基础组件
│   │   └── routes.tsx            # 路由定义
│   ├── lib/
│   │   ├── api/                  # API 客户端
│   │   ├── services/             # 业务服务层
│   │   ├── helpers/              # 纯函数工具
│   │   ├── types/                # TypeScript 类型定义
│   │   └── hooks/                # 通用 hooks
│   └── main.tsx                  # 入口
├── backend/                      # 后端源码
│   ├── app/
│   │   ├── api/v1/routers/       # API 路由
│   │   │   ├── recognition.py    # 识别任务（用户端）
│   │   │   ├── admin_recognition.py  # 识别任务（管理端）
│   │   │   ├── ai_config.py      # AI 配置管理
│   │   │   ├── auth.py           # 认证
│   │   │   ├── users.py          # 用户管理
│   │   │   └── cleaning.py       # 文件清洗
│   │   ├── models/               # SQLAlchemy ORM 模型
│   │   ├── schemas/              # Pydantic 请求/响应 Schema
│   │   ├── services/
│   │   │   ├── recognition/      # 识别核心
│   │   │   │   ├── provider_base.py       # AI 客户端抽象基类
│   │   │   │   ├── unified_client.py      # 统一 AI 客户端
│   │   │   │   ├── zhipu_ocr_client.py    # 智谱 OCR 专用客户端
│   │   │   │   ├── provider_factory.py    # 客户端工厂
│   │   │   │   ├── pdf_strategy_runner.py # PDF 识别策略
│   │   │   │   ├── recognition_orchestrator.py # 识别编排器
│   │   │   │   ├── prompts.py             # Prompt 模板
│   │   │   │   └── preprocessors/         # 文件预处理器
│   │   │   ├── ai/               # AI 共享基础设施
│   │   │   │   ├── request_builders/  # 请求构建器（按 API 风格）
│   │   │   │   ├── response_parsers/  # 响应解析器
│   │   │   │   ├── http_helpers.py    # URL/Header 构造
│   │   │   │   └── transport.py       # 传输模式枚举
│   │   │   └── *.py              # 其他业务服务
│   │   ├── repositories/         # 数据访问层
│   │   ├── core/                 # 配置、安全、响应封装
│   │   └── db/                   # 数据库初始化
│   ├── migrations/               # SQL 迁移脚本
│   ├── requirements.txt
│   ├── setup.sh                  # 一键初始化脚本
│   └── .env.example              # 环境变量模板
├── package.json
├── vite.config.ts
├── index.html
└── .gitignore
```

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.9
- pip

### 1. 克隆项目

```bash
git clone https://github.com/longmo666/invoice.git
cd invoice
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，修改 SECRET_KEY 为一个 32 位以上的随机字符串
# 例如: openssl rand -hex 32

# 初始化数据库和管理员账号
python -m app.db.init_admin

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问 http://localhost:8000/docs 可查看 API 文档。

### 3. 启动前端

```bash
# 回到项目根目录
cd ..

npm install
npm run dev
```

访问 http://localhost:5173 即可使用。

### 4. 配置 AI 服务

登录管理员后台 → AI 配置 → 新增配置：

- 填入 AI 服务商的 API Key、Base URL、模型名称
- 支持的 API 风格：`openai_chat_completions`、`anthropic_messages`、`gemini_generate_content`、`zhipu_chat_completions`、`zhipu_ocr`
- 点击"测试连接"验证配置
- 激活配置后即可使用识别功能

## 生产部署

### 构建前端

```bash
npm run build
# 产物在 dist/ 目录
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /var/www/invoice;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 50M;
    }
}
```

### 后端后台运行

```bash
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
```

## 环境变量说明

### 后端 (`backend/.env`)

| 变量 | 说明 | 默认值 |
|---|---|---|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./invoice.db` |
| `SECRET_KEY` | JWT 签名密钥（必须修改，≥32 字符） | 无 |
| `ALGORITHM` | JWT 算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | `1440` |
| `CORS_ORIGINS` | 允许的跨域来源 | `["http://localhost:5173"]` |
| `ADMIN_PASSWORD` | 初始管理员密码（首次 init 时使用） | 自动生成 |

### 前端 (`.env.development` / `.env.production`)

| 变量 | 说明 |
|---|---|
| `VITE_API_BASE_URL` | 后端 API 地址，开发环境 `http://localhost:8000/api/v1`，生产环境 `/api/v1` |

## API 概览

| 模块 | 端点 | 说明 |
|---|---|---|
| 认证 | `POST /api/v1/auth/login` | 用户登录 |
| 认证 | `POST /api/v1/auth/admin-login` | 管理员登录 |
| 识别 | `POST /api/v1/recognition/tasks` | 创建识别任务（上传文件） |
| 识别 | `GET /api/v1/recognition/tasks/paginated` | 分页查询任务列表 |
| 识别 | `GET /api/v1/recognition/pending-review` | 获取待复核列表 |
| 识别 | `PUT /api/v1/recognition/items/{id}/review` | 提交复核结果 |
| AI 配置 | `GET /api/v1/ai-configs` | 获取 AI 配置列表 |
| AI 配置 | `POST /api/v1/ai-configs/test-connection` | 测试 AI 连接 |
| 管理 | `GET /api/v1/recognition/admin/tasks/paginated` | 管理端任务列表 |
| 用户 | `GET /api/v1/admin/users` | 用户管理 |

完整 API 文档启动后端后访问 `/docs`。

## License

MIT
