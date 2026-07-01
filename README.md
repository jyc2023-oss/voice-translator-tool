# VoiceBridge Studio

将中文短视频口播文案一键改写成自然英文口播，并生成可试听、可下载的英文语音。项目面向 AI 工程师笔试场景，强调可运行、可演示、可部署。

## 在线能力概览

- 中文文案提交、长度校验、错误提示
- OpenAI-compatible / DeepSeek 翻译链路
- ElevenLabs 多音色异步生成
- 任务状态轮询：`pending` / `translating` / `synthesizing` / `completed` / `failed`
- 英文文案复制、音频播放下载、逐句高亮
- 历史记录搜索、复用、删除
- ElevenLabs 动态音色列表与默认音色配置

## 技术栈

```text
frontend/  React + Vite + TypeScript
backend/   FastAPI + SQLAlchemy + SQLite
storage/   Local audio files + SQLite metadata
```

## 本地运行

### 后端

```bash
cd backend
copy .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
copy .env.example .env
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### 一键启动

根目录提供了 `start-dev.bat`。

- 前端：`http://127.0.0.1:5173`
- 后端文档：`http://127.0.0.1:8000/docs`

## 环境变量

后端读取 `backend/.env`：

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
FIELD_ENCRYPTION_KEY=

ELEVENLABS_API_KEY=
ELEVENLABS_DEFAULT_VOICE_ID=EXAVITQu4vr4xnSDxMaL
ELEVENLABS_MODEL=eleven_multilingual_v2
ELEVENLABS_MAX_CONCURRENCY=2

HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./app.db
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
REQUEST_TIMEOUT_SECONDS=60
MAX_SOURCE_CHARS=2000
MAX_VOICE_COUNT=3
AUDIO_DIR=./audio
```

前端可选环境变量：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 数据位置

- 数据库：`backend/app.db`
- 音频目录：`backend/audio`

## 安全增强

- 浏览器到前端、前端到后端、后端到第三方 API 全链路通过 HTTPS 部署
- 后端新增基础安全响应头：`HSTS`、`X-Frame-Options`、`X-Content-Type-Options`、`Referrer-Policy`
- 数据库敏感字段支持应用层加密：`source_text`、`translated_text`、`error_message`
- 字段加密依赖环境变量 `FIELD_ENCRYPTION_KEY`
- 历史搜索会先解密再做内存筛选，适合当前演示规模

### 生成 Fernet 密钥

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 迁移已有明文历史数据

```bash
cd backend
python -m scripts.migrate_encrypt_existing_jobs
```

## API

- `POST /api/jobs`：创建任务
- `GET /api/jobs/{job_id}`：查询任务
- `GET /api/history`：获取历史记录
- `DELETE /api/history/{job_id}`：删除历史记录
- `GET /api/health`：健康检查

## 部署

### 前端部署到 Vercel

- Root Directory：`frontend`
- 环境变量：`VITE_API_BASE_URL=https://your-render-backend.onrender.com`

### 后端部署到 Render

项目根目录提供 `render.yaml`，可直接按 Blueprint 部署。

需要补齐这些环境变量：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `FIELD_ENCRYPTION_KEY`
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_DEFAULT_VOICE_ID`
- `BACKEND_URL`
- `FRONTEND_URL`

## 已知限制

- 逐句高亮当前为估算版，不是强制对齐版
- “推荐免费可用” 仅依据 `premade` 分类做经验提示，不等同于 ElevenLabs 套餐承诺
- 默认将 ElevenLabs 并发限制为 `2`，用于规避低套餐并发上限
- Render 免费实例不提供持久化磁盘，重部署后本地 SQLite 与音频可能丢失
- 若未配置 `FIELD_ENCRYPTION_KEY`，系统仍能兼容旧数据运行，但不会启用数据库字段加密

## 安全提醒

- `.env` 不要提交到 GitHub
- 已暴露过的密钥建议统一轮换
