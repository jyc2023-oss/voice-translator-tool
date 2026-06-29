# AI工程师实习生笔试题复杂严谨实现方案

> 项目主题：中文口播文本转英文翻译 + 英文语音生成网页工具  
> 目标定位：不是一个简单 Demo，而是一个可部署、可扩展、具备工程质量和产品意识的 AI Native 小工具。  
> 适用场景：运营人员输入中文短视频口播文案，系统自动生成自然、适合海外短视频传播的英文文案，并调用 ElevenLabs 生成可播放、可下载的英文语音，同时保存历史记录。

---

## 1. 题目理解与核心目标

本题要求实现一个可以运行的网页工具，用户输入中文口播文本后，系统需要输出英文翻译，并生成对应的英文语音。页面需要展示英文文本，支持一键复制，同时提供英文音频的在线播放与下载按钮，并保存历史记录。

该题的本质不是考察传统机器学习建模，也不是要求训练翻译模型或语音模型，而是考察候选人是否能将真实业务需求快速转化为可运行、可部署、可维护的 AI 工程产品。它综合考察前后端开发、第三方 AI API 调用、异步任务处理、音频文件管理、异常处理、产品体验设计和 AI Native 开发意识。

因此，本方案不采用“所有逻辑写在一个页面里”的粗糙实现，而是设计为一个具备前后端分离、任务状态管理、历史记录持久化、多音色扩展、播放同步高亮能力的完整工程项目。

---

## 2. 需求拆解

### 2.1 基础功能需求

系统至少需要实现以下功能：

1. 中文文本输入  
   用户在网页文本框中输入中文口播文案，系统需要支持较长文本输入，例如短视频广告文案、产品介绍文案、直播带货脚本等。

2. 英文翻译生成  
   用户点击生成按钮后，后端调用大语言模型 API，将中文口播文本翻译为自然、流畅、适合英文口播场景的英文文本，而不是机械直译。

3. 英文文本展示与复制  
   页面展示翻译后的英文文本，并提供复制按钮，用户可直接复制英文文案用于其他平台。

4. 英文语音生成  
   系统将英文文本发送给 ElevenLabs TTS API，生成英文语音文件。

5. 音频播放  
   页面提供音频播放器，支持用户在线试听生成的语音。

6. 音频下载  
   页面提供下载按钮，用户可下载 MP3 文件。

7. 历史记录  
   系统保存用户过去生成过的中文文本、英文翻译、音频文件、所用音色、生成时间等信息，并支持再次播放和下载。

---

### 2.2 进阶功能需求

为了提高作品质量，本方案建议实现以下进阶功能：

1. 多音色并发生成与对比  
   同一段英文文本可以使用多个 ElevenLabs 音色并发生成音频，页面并排展示多个音色结果，用户可独立试听并选择下载。

2. 语音自然度优化  
   通过配置 ElevenLabs 的 voice settings，例如 stability、similarity_boost、style、use_speaker_boost 等参数，使生成语音更接近真人短视频口播，而不是机械朗读。

3. 逐句同步高亮  
   将英文文本切分为句子，并估算每句对应的播放时间。在音频播放过程中，页面根据 currentTime 动态高亮当前句子，实现类似字幕同步效果。

4. 历史记录检索与复用  
   历史记录支持按关键词搜索、按时间排序、重新生成音频、复制英文文本、删除记录等操作。

5. 任务状态管理  
   由于翻译和音频生成都可能耗时，系统需要显示任务状态，例如 pending、translating、synthesizing、completed、failed，避免用户误以为页面卡死。

6. 错误提示与恢复机制  
   当 API Key 错误、余额不足、文本过长、网络超时或第三方接口失败时，系统应返回明确的错误信息，并允许用户重新生成。

---

## 3. 技术栈选型

### 3.1 推荐技术栈

本项目建议采用如下技术栈：

| 模块 | 技术方案 | 选择理由 |
|---|---|---|
| 前端框架 | React + Vite + TypeScript | 开发速度快，生态成熟，适合构建交互式页面 |
| UI 样式 | Tailwind CSS + shadcn/ui | 快速构建现代化界面，视觉效果好 |
| 后端框架 | FastAPI | Python 生态友好，接口开发简洁，适合 AI API 集成 |
| 数据库 | SQLite / PostgreSQL | 本地 Demo 可用 SQLite，部署生产可换 PostgreSQL |
| ORM | SQLAlchemy | 便于定义数据模型和迁移 |
| 翻译模型 | OpenAI / DeepSeek / Gemini API | 使用 LLM 实现更自然的口播式翻译 |
| TTS | ElevenLabs API | 语音自然度高，适合英文口播 |
| 文件存储 | 本地 static/audio 或对象存储 | Demo 阶段用本地，部署阶段可换 S3/R2 |
| 异步任务 | FastAPI BackgroundTasks / Celery | 防止长任务阻塞请求 |
| 部署 | Vercel + Render/Railway | 前后端分离部署简单 |

---

### 3.2 为什么不建议只写纯前端？

可以直接在前端调用 ElevenLabs API，但不建议这样做，原因如下：

第一，API Key 会暴露在浏览器中，存在安全风险。  
第二，历史记录难以可靠持久化。  
第三，后续如果要加入多用户、权限、限流、缓存、日志分析等功能，纯前端结构扩展性较差。  
第四，音频文件管理、错误重试、并发任务控制更适合放在后端完成。

因此，严谨方案应采用前后端分离架构：前端只负责交互展示，后端负责调用 AI API、保存数据、管理音频文件和返回任务状态。

---

## 4. 系统总体架构

整体架构如下：

```text
用户浏览器
   │
   │ 1. 输入中文口播文本
   ▼
React 前端页面
   │
   │ POST /api/jobs
   ▼
FastAPI 后端
   │
   ├── 调用 LLM 翻译 API
   │
   ├── 调用 ElevenLabs TTS API
   │
   ├── 保存音频文件
   │
   ├── 写入数据库历史记录
   │
   └── 返回任务结果
   ▼
SQLite / PostgreSQL + Audio Storage
   │
   ▼
前端展示英文文本、播放器、下载按钮、历史记录
```

---

## 5. 后端设计

### 5.1 后端目录结构

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── errors.py
│   ├── api/
│   │   ├── routes_jobs.py
│   │   ├── routes_history.py
│   │   └── routes_audio.py
│   ├── services/
│   │   ├── translation_service.py
│   │   ├── elevenlabs_service.py
│   │   ├── sentence_align_service.py
│   │   └── storage_service.py
│   ├── models/
│   │   └── job.py
│   ├── schemas/
│   │   └── job_schema.py
│   ├── db/
│   │   ├── session.py
│   │   └── base.py
│   └── utils/
│       ├── text_utils.py
│       └── file_utils.py
├── audio/
├── requirements.txt
└── .env
```

---

### 5.2 数据模型设计

核心表：`generation_jobs`

字段建议如下：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | UUID | 任务唯一 ID |
| source_text | TEXT | 用户输入的中文文本 |
| translated_text | TEXT | 生成的英文文本 |
| status | VARCHAR | pending / translating / synthesizing / completed / failed |
| voice_id | VARCHAR | ElevenLabs 音色 ID |
| voice_name | VARCHAR | 音色名称 |
| audio_path | VARCHAR | 音频文件本地路径 |
| audio_url | VARCHAR | 前端可访问的音频 URL |
| duration_seconds | FLOAT | 音频时长 |
| alignment_json | JSON | 逐句高亮时间轴 |
| error_message | TEXT | 失败原因 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

如果实现多音色并发，建议拆成两张表：

```text
generation_jobs
voice_outputs
```

其中 `generation_jobs` 保存一次文本生成任务，`voice_outputs` 保存每个音色对应的音频结果。

---

## 6. API 接口设计

### 6.1 创建生成任务

```http
POST /api/jobs
```

请求体：

```json
{
  "source_text": "还在为割草头疼吗？太阳底下忙活大半天...",
  "voice_ids": ["21m00Tcm4TlvDq8ikWAM", "EXAVITQu4vr4xnSDxMaL"],
  "mode": "multi_voice"
}
```

响应体：

```json
{
  "job_id": "b9f7c2d0-8b21-4a60-8d11-4c1a70f64d91",
  "status": "pending"
}
```

---

### 6.2 查询任务状态

```http
GET /api/jobs/{job_id}
```

响应体：

```json
{
  "job_id": "b9f7c2d0-8b21-4a60-8d11-4c1a70f64d91",
  "status": "completed",
  "source_text": "...",
  "translated_text": "...",
  "outputs": [
    {
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "voice_name": "Rachel",
      "audio_url": "/audio/b9f7c2d0-rachel.mp3",
      "duration_seconds": 38.5,
      "alignment": [
        {
          "sentence": "Are you tired of mowing the lawn?",
          "start": 0.0,
          "end": 2.4
        }
      ]
    }
  ]
}
```

---

### 6.3 获取历史记录

```http
GET /api/history?page=1&page_size=10&keyword=lawn
```

响应体：

```json
{
  "items": [
    {
      "job_id": "...",
      "source_text": "...",
      "translated_text": "...",
      "created_at": "2026-06-29T10:00:00",
      "outputs": [...]
    }
  ],
  "total": 35
}
```

---

### 6.4 删除历史记录

```http
DELETE /api/history/{job_id}
```

---

## 7. 翻译模块设计

### 7.1 翻译目标

本项目中的翻译不应该是普通直译，而应是“英文短视频口播文案改写式翻译”。

也就是说，系统应将中文内容翻译为自然、有营销感、适合英语母语用户听觉习惯的英文表达。

例如原文：

```text
还在为割草头疼吗？太阳底下忙活大半天，又累又费劲儿，清理碎草还麻烦！
```

普通直译可能是：

```text
Are you still having a headache about mowing the lawn? Working under the sun for half a day is tiring and troublesome.
```

更适合短视频口播的翻译应是：

```text
Still tired of mowing your lawn under the hot sun? Spending hours pushing a mower, sweating, and cleaning up grass clippings is exhausting.
```

后者更自然，也更适合英文广告口播。

---

### 7.2 翻译 Prompt 设计

推荐使用如下系统提示词：

```text
You are a professional bilingual copywriter specializing in short-form video ads for English-speaking audiences.

Your task is to translate Chinese spoken promotional scripts into natural, persuasive, and fluent English voice-over scripts.

Requirements:
1. Preserve the original selling points and emotional appeal.
2. Do not translate word by word.
3. Make the output sound natural when spoken aloud.
4. Use concise, vivid, and consumer-friendly expressions.
5. Keep the tone energetic but not exaggerated.
6. Return only the English script, without explanations.
```

用户输入：

```text
Translate the following Chinese short-video voice-over script into English:

{source_text}
```

---

### 7.3 翻译质量控制

后端应在翻译后进行基本校验：

1. 英文文本不能为空。
2. 英文文本不应包含明显中文字符。
3. 英文长度不应异常短，例如少于中文长度的 20%。
4. 若模型返回解释性内容，例如 “Here is the translation:”，应自动清理。
5. 对超长文本进行长度限制，避免超过 TTS API 限制。

---

## 8. ElevenLabs 语音生成模块设计

### 8.1 基础调用流程

后端将英文文本发送到 ElevenLabs：

```http
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
```

请求体大致如下：

```json
{
  "text": "Still tired of mowing your lawn under the hot sun?",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.45,
    "similarity_boost": 0.85,
    "style": 0.35,
    "use_speaker_boost": true
  }
}
```

返回值是音频二进制内容，后端保存为 MP3 文件，并生成可访问的 audio_url。

---

### 8.2 语音自然度参数建议

短视频口播不适合过于平稳的机械朗读，因此推荐参数：

```json
{
  "stability": 0.35,
  "similarity_boost": 0.85,
  "style": 0.45,
  "use_speaker_boost": true
}
```

解释如下：

- `stability` 较低时，语音情绪起伏更明显，更像真人口播。
- `similarity_boost` 较高时，更能保持选定音色特征。
- `style` 适当提高后，语音更有表现力。
- `use_speaker_boost` 可以增强音色清晰度和辨识度。

需要注意的是，参数不是越高越好。过低的 stability 可能导致语音不稳定，过高的 style 可能导致夸张或不自然。建议提供一个“自然口播”预设，而不是让用户直接面对复杂参数。

---

## 9. 多音色并发对比设计

### 9.1 产品逻辑

用户输入一段中文文案后，系统自动生成英文文本，并同时使用多个音色生成语音。例如：

```text
Rachel - 成熟女声，适合广告口播
Bella - 年轻女声，适合短视频种草
Adam - 男声，适合科技产品介绍
```

页面展示为：

```text
英文翻译文本

音色 A   [播放] [下载]
音色 B   [播放] [下载]
音色 C   [播放] [下载]
```

---

### 9.2 并发实现

后端可以使用 `asyncio.gather` 并发调用 ElevenLabs：

```python
outputs = await asyncio.gather(
    synthesize(text, voice_id_1),
    synthesize(text, voice_id_2),
    synthesize(text, voice_id_3),
    return_exceptions=True
)
```

对于失败的音色，不应让整个任务失败，而应将该音色标记为 failed，其余成功音色正常展示。

---

## 10. 逐句同步高亮设计

### 10.1 基础实现思路

严格意义上的逐句同步需要 TTS 服务返回 word-level 或 sentence-level timestamps。如果当前 ElevenLabs 接口没有直接返回精确时间戳，则可以采用估算方案：

1. 将英文文本按句子切分。
2. 获取音频总时长。
3. 根据每句字符数或词数占比估算时间范围。
4. 播放时监听 audio.currentTime。
5. 根据当前时间找到对应句子并高亮。

例如：

```json
[
  {
    "sentence": "Still tired of mowing your lawn under the hot sun?",
    "start": 0.0,
    "end": 3.1
  },
  {
    "sentence": "This fully automatic lawn-mowing robot does the work for you.",
    "start": 3.1,
    "end": 7.4
  }
]
```

这种方案不是绝对精确，但对于 Demo 和笔试作品已经足够体现产品思维。如果要进一步严谨，可以使用 ElevenLabs 的 alignment 能力，或引入强制对齐工具，例如 WhisperX、aeneas 等。

---

## 11. 前端设计

### 11.1 页面结构

推荐页面包括以下区域：

```text
顶部标题区
  - 项目名称
  - 简短说明

输入区
  - 中文文本输入框
  - 字数统计
  - 音色选择
  - 生成按钮

结果区
  - 英文翻译文本
  - 一键复制按钮
  - 逐句高亮显示区
  - 音频播放器
  - 下载按钮

多音色对比区
  - 音色卡片
  - 播放按钮
  - 下载按钮
  - 当前选中音色

历史记录区
  - 历史任务列表
  - 搜索框
  - 再次播放
  - 复制
  - 下载
  - 删除
```

---

### 11.2 前端目录结构

```text
frontend/
├── src/
│   ├── api/
│   │   └── client.ts
│   ├── components/
│   │   ├── TextInputPanel.tsx
│   │   ├── TranslationResult.tsx
│   │   ├── VoiceOutputCard.tsx
│   │   ├── AudioPlayerWithHighlight.tsx
│   │   ├── HistoryList.tsx
│   │   └── LoadingState.tsx
│   ├── hooks/
│   │   ├── useJobPolling.ts
│   │   └── useAudioHighlight.ts
│   ├── pages/
│   │   └── HomePage.tsx
│   ├── types/
│   │   └── job.ts
│   └── main.tsx
├── package.json
└── vite.config.ts
```

---

## 12. 用户体验细节

为了让作品不像“学生作业”，建议加入以下细节：

1. 输入框提供示例文本按钮。
2. 点击生成后禁用按钮，防止重复提交。
3. 生成过程中显示阶段提示，例如“正在翻译”“正在生成语音”“正在保存历史记录”。
4. 翻译结果支持一键复制，并弹出复制成功提示。
5. 音频生成失败时，显示具体原因，而不是只显示 Error。
6. 历史记录中保留生成时间和音色信息。
7. 音频下载文件名使用可读格式，例如 `lawn_robot_rachel_20260629.mp3`。
8. 页面在手机端也能正常使用。
9. API Key 不出现在前端代码中。
10. GitHub README 中写清楚运行方法、功能说明和技术亮点。

---

## 13. 安全性与工程规范

### 13.1 API Key 管理

所有敏感信息放在 `.env` 文件：

```env
OPENAI_API_KEY=xxx
ELEVENLABS_API_KEY=xxx
DATABASE_URL=sqlite:///./app.db
AUDIO_BASE_URL=http://localhost:8000/audio
```

`.gitignore` 必须包含：

```text
.env
audio/
__pycache__/
node_modules/
dist/
```

严禁将 API Key 提交到 GitHub。

---

### 13.2 请求限制

后端应设置基本限制：

1. 单次输入文本最大长度，例如 2000 字。
2. 单个 IP 每分钟最多请求若干次。
3. 对空文本、纯标点、过短文本进行拒绝。
4. 对第三方 API 超时设置 timeout。
5. 对失败任务写入 error_message，方便排查。

---

## 14. 部署方案

### 14.1 简化部署

适合笔试提交的部署方式：

- 前端：Vercel
- 后端：Render / Railway
- 数据库：SQLite 或 Render PostgreSQL
- 音频文件：后端本地目录

这种方式部署快，但后端本地音频文件在某些平台可能不持久。因此如果要求更稳定，可以改用 Cloudflare R2、AWS S3 或 Supabase Storage 保存音频。

---

### 14.2 推荐提交内容

最终提交应包括：

1. 部署网址。
2. GitHub 代码仓库。
3. README 文件。
4. 简短录屏演示。
5. `.env.example` 文件。
6. 功能截图。
7. 技术亮点说明。

---

## 15. README 应突出什么

README 不要只写“怎么运行”，还应该体现工程思维。建议结构如下：

```text
# Chinese Voice-over Translator & English TTS Tool

## 项目简介
## 在线演示
## 核心功能
## 进阶功能
## 技术架构
## 页面截图
## 本地运行
## 环境变量
## API 设计
## 数据库设计
## 已知问题与后续优化
```

重点突出：

1. 支持中文口播文案翻译为自然英文口播。
2. 集成 ElevenLabs 生成英文语音。
3. 支持音频播放和下载。
4. 支持历史记录。
5. 支持多音色对比。
6. 支持逐句播放高亮。
7. 前后端分离，API Key 安全保存在后端。
8. 具备错误处理、加载状态、任务状态管理。

---

## 16. 开发里程碑

### 阶段一：最小可用版本

目标：完成基础功能。

任务：

1. 搭建 React 前端。
2. 搭建 FastAPI 后端。
3. 实现中文输入。
4. 实现 LLM 翻译。
5. 实现 ElevenLabs 语音生成。
6. 实现音频播放与下载。
7. 使用 SQLite 保存历史记录。

预计时间：半天到一天。

---

### 阶段二：工程化增强

目标：让项目更像真实产品。

任务：

1. 增加任务状态。
2. 增加错误处理。
3. 增加 Loading 状态。
4. 增加复制按钮。
5. 增加历史记录搜索。
6. 增加删除历史记录。
7. 增加 `.env.example` 和 README。

预计时间：半天。

---

### 阶段三：进阶加分功能

目标：明显区别于普通 Demo。

任务：

1. 多音色并发生成。
2. 音色卡片对比。
3. 逐句同步高亮。
4. 语音参数预设。
5. 移动端适配。
6. 录屏演示。

预计时间：一天。

---

## 17. 推荐最终实现等级

如果只是为了交作业，完成基础功能即可。

但如果目标是让老师或面试官觉得“这个人具备 AI 工程实习能力”，建议至少做到：

1. 前后端分离。
2. API Key 后端保存。
3. 翻译不是直译，而是口播文案改写。
4. ElevenLabs 音频可播放、可下载。
5. 历史记录可查看。
6. 多音色对比。
7. README 写清楚架构和亮点。
8. 部署到公网。
9. 提供录屏演示。

这样提交出来的效果会明显强于普通候选人。

---

## 18. 最终项目亮点表述

可以在 README 或答辩中这样总结：

本项目实现了一个面向短视频运营场景的 AI Native 工具。用户输入中文口播文案后，系统通过大语言模型生成自然流畅的英文口播稿，并调用 ElevenLabs API 合成真人感英文语音。系统支持英文文本复制、音频在线播放与下载、历史记录管理、多音色并发对比以及逐句播放高亮。项目采用 React + FastAPI 的前后端分离架构，将 API Key 和第三方服务调用封装在后端，避免敏感信息暴露。相比简单 Demo，本项目更关注真实业务可用性、用户体验和工程可维护性。

---

## 19. 风险与注意事项

1. ElevenLabs 免费额度有限，需要避免频繁重复调用。
2. 翻译模型和 TTS 模型都可能产生延迟，应设计 Loading 和任务状态。
3. 文本过长可能导致 TTS 失败，需要限制长度或分段生成。
4. 音频文件需要统一管理，否则部署后容易丢失。
5. 前端不能暴露 API Key。
6. 如果使用免费部署平台，需要注意冷启动问题。
7. 若要实现非常准确的逐句高亮，需要额外的音频对齐能力，简单估算只能作为近似方案。

---

## 20. 结论

本题虽然表面上是“中文翻译 + 英文语音生成”的小工具，但真正考察的是候选人的 AI 工程综合能力。一个优秀答案不应只停留在“能调用 API”，而应体现完整的产品闭环：用户输入、翻译生成、语音合成、音频播放、文件下载、历史记录、错误处理、部署上线和代码规范。

因此，本方案建议使用 React + FastAPI + LLM API + ElevenLabs + SQLite/PostgreSQL 构建完整项目，并通过多音色对比、语音自然度优化和逐句同步高亮体现进阶能力。最终交付应包含部署链接、GitHub 仓库、README、录屏演示和清晰的功能说明。
