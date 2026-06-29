# VoiceBridge Studio

中文短视频口播文案一键改写成自然英文口播稿，并生成可试听、可下载的英文语音。项目面向 AI 工程实习笔试场景，强调可运行、可演示、可部署，而不是停留在单页 Demo。

## 在线能力概览

- 中文文案提交、长度校验、错误提示
- DeepSeek / OpenAI-compatible 翻译链路
- ElevenLabs 多音色异步生成
- 任务状态轮询：`pending` / `translating` / `synthesizing` / `completed` / `failed`
- 英文复制、音频播放下载、逐句高亮近似版
- 历史记录搜索、复用、删除
- 可视化多音色选择，支持 ElevenLabs 动态音色列表与自定义 `Voice ID`

## 技术架构

```text
frontend/  React + Vite + TypeScript
backend/   FastAPI + SQLAlchemy + SQLite
storage/   Local audio files + SQLite metadata
```

主流程：

1. 前端提交中文口播文案与音色列表
2. 后端创建任务并异步调用翻译模型
3. 翻译结果写回数据库后，并发调用 ElevenLabs TTS
4. 音频文件写入本地目录，历史记录写入 SQLite
5. 前端轮询任务状态并展示翻译、音频与历史记录

## 项目亮点

- 翻译目标不是直译，而是适合英文口播的广告式改写
- 多音色并发生成，不因单个音色失败而拖垮整个任务
- 前后端分离，密钥只保存在后端
- 逐句高亮采用可解释的时间估算策略，适合作为笔试演示版
- 已准备本地开发脚本、部署配置和环境变量模板

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
npx vite --host 127.0.0.1 --port 5173
```

### 一键启动

项目根目录已提供 [`start-dev.bat`](</D:/大学课程/实习/线上电商/start-dev.bat:1>)。

双击后会打开两个窗口：

- 前端：`http://127.0.0.1:5173`
- 后端文档：`http://127.0.0.1:8000/docs`

## 环境变量

后端读取 `backend/.env`：

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash

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

## 数据落盘位置

- 历史记录数据库：[`backend/app.db`](</D:/大学课程/实习/线上电商/backend/app.db>)
- 音频目录：[`backend/audio`](</D:/大学课程/实习/线上电商/backend/audio>)

## API

- `POST /api/jobs` 创建任务
- `GET /api/jobs/{job_id}` 查询任务
- `GET /api/history` 获取历史记录
- `DELETE /api/history/{job_id}` 删除历史记录
- `GET /api/health` 健康检查

## 部署方案

### 前端部署到 Vercel

建议把 Vercel 的 Root Directory 设为 `frontend`，项目中已提供 [`frontend/vercel.json`](</D:/大学课程/实习/线上电商/frontend/vercel.json:1>)。

需要设置环境变量：

```env
VITE_API_BASE_URL=https://your-render-backend.onrender.com
```

### 后端部署到 Render

项目根目录已提供 [`render.yaml`](</D:/大学课程/实习/线上电商/render.yaml:1>)，适合直接走 Blueprint 部署。

需要在 Render 中补齐这些环境变量：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_DEFAULT_VOICE_ID`
- `BACKEND_URL`
- `FRONTEND_URL`

`render.yaml` 里已经预设：

- `buildCommand: pip install -r requirements.txt`
- `startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- 免费版可直接部署，不依赖磁盘挂载

### 官方参考

- Vercel 文档：`https://vercel.com/docs`
- Render Python 文档：`https://render.com/docs/deploy-fastapi`
- Render Blueprint 文档：`https://render.com/docs/blueprint-spec`

## 建议提交物

- 公网可访问的前端链接
- 后端 Swagger 链接
- GitHub 仓库
- 录屏演示
- README
- 功能截图

## 已知限制与后续优化

- 逐句高亮目前是估算版，不是强制对齐版
- 页面会动态读取 ElevenLabs 音色，但“免费可用”仍是基于 `premade` 分类做经验性提示，不等同于官方套餐承诺
- 默认会把 ElevenLabs TTS 并发限制在 `2`，用于避开免费/低套餐常见的并发上限；如果你升级套餐，可以调高 `ELEVENLABS_MAX_CONCURRENCY`
- Render 免费套餐不支持持久化磁盘，因此重新部署或休眠唤醒后，本地 SQLite 历史记录和音频文件可能丢失；笔试演示阶段可接受，正式上线建议接对象存储和托管数据库
- 还未加入限流、鉴权、监控、结构化日志
- 正式线上建议把音频迁移到对象存储，而不是继续使用本地目录

## 安全提醒

- `.env` 不要提交到 GitHub
- 已暴露过的密钥建议统一轮换
