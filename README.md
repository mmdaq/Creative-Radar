# Creative Radar

> 《创意提示器 Creative Radar》—— 每日创意情报 + 灵感学习卡片 + 邮件推送系统。

## 项目定位

不是普通 RSS 聚合器，而是「每日创意情报 + 灵感学习卡片 + 每日邮件推送」系统。

最终价值：每天打开邮箱，看到**值得花 30 分钟学习的 10～20 个创意**。

## 技术栈

- **后端**：Python + FastAPI + SQLAlchemy + Pydantic + APScheduler
- **数据库**：SQLite（第一版）→ PostgreSQL（V2）
- **前端**：React + TypeScript + Vite + Tailwind CSS
- **AI**：OpenAI Compatible API（LM Studio / Ollama / DeepSeek / Qwen / OpenAI）
- **邮件**：SMTP（QQ/163/Gmail/Outlook/企业邮箱）
- **定时**：APScheduler 或 Windows 任务计划程序

## 目录结构

```

# Creative Radar

> 《创意提示器 Creative Radar》—— 每日创意情报 + 灵感学习卡片 + 邮件推送系统。

## 项目定位

不是普通 RSS 聚合器，而是「每日创意情报 + 灵感学习卡片 + 每日邮件推送」系统。

最终价值：每天打开邮箱，看到**值得花 30 分钟学习的 10～20 个创意**。

## 技术栈

- **后端**：Python + FastAPI + SQLAlchemy + Pydantic + APScheduler
- **数据库**：SQLite（第一版）→ PostgreSQL（V2）
- **前端**：React + TypeScript + Vite + Tailwind CSS
- **AI**：OpenAI Compatible API（LM Studio / Ollama / DeepSeek / Qwen / OpenAI）
- **邮件**：SMTP（QQ/163/Gmail/Outlook/企业邮箱）
- **定时**：APScheduler 或 Windows 任务计划程序

## 目录结构

```
CreativeRadar/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/          ← REST 接口
│   │   ├── collectors/   ← 数据源采集
│   │   ├── ai/           ← AI 分析模块
│   │   ├── database/     ← SQLAlchemy 模型 + 引擎 + 数据
│   │   ├── services/     ← 去重、排名、邮件
│   │   └── scheduler/    ← 定时任务
│   ├── requirements.txt
│   └── tests/
├── frontend/             ← React 单页应用
├── prompts/              ← AI 分析模板
├── email/                ← 邮件模板
├── data/                 ← 数据文件
├── scripts/              ← Windows 一键启动脚本
└── docs/                 ← 安装/配置/数据源/AI/开发文档
```

## 快速开始

```bash
# 1. 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 2. 初始化数据库
cd app
python -m database init

# 3. 启动后端
python -m app.main

# 4. 启动前端
cd ../../frontend
npm install
npm run dev
```

## 文档

- `docs/INSTALL.md` — 安装与启动
- `docs/CONFIG.md` — 配置说明
- `docs/SOURCES.md` — 数据源接入指南
- `docs/AI.md` — AI 模型与分析说明
- `docs/DEVELOPMENT.md` — 开发规范
