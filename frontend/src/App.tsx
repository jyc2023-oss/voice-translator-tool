import { useEffect, useMemo, useState } from 'react'

import { createJob, deleteHistory, getHistory, getJob, getVoiceCatalog } from './api/client'
import HistoryList from './components/HistoryList'
import VoiceOutputCard from './components/VoiceOutputCard'
import type { Job, VoiceCatalogItem, VoiceSelection } from './types'

const EXAMPLE_TEXT =
  '还在为割草头疼吗？太阳底下忙活大半天，又累又费劲儿，清理碎草还麻烦！这款全自动割草机器人，轻松帮你搞定庭院草坪。'

const VOICE_PRESETS = [
  {
    voice_id: 'EXAVITQu4vr4xnSDxMaL',
    voice_name: 'Sarah',
    category: 'premade',
    labels: ['female', 'mature', 'confident'],
    description: '成熟稳重，适合广告口播和产品介绍',
    preview_url: null,
    is_default: true,
    is_recommended_free: true,
  },
  {
    voice_id: 'hpp4J3VqNfWAUOO0d1Us',
    voice_name: 'Bella',
    category: 'premade',
    labels: ['female', 'bright', 'warm'],
    description: '轻快亲和，适合短视频种草和生活方式内容',
    preview_url: null,
    is_default: false,
    is_recommended_free: true,
  },
  {
    voice_id: 'pNInz6obpgDQGcFmaJgB',
    voice_name: 'Adam',
    category: 'premade',
    labels: ['male', 'firm', 'dominant'],
    description: '低沉有力度，适合科技、工具类和功能卖点强化',
    preview_url: null,
    is_default: false,
    is_recommended_free: true,
  },
  {
    voice_id: 'TX3LPaxmHKxFdv7VOQHJ',
    voice_name: 'Liam',
    category: 'premade',
    labels: ['male', 'energetic', 'creator'],
    description: '更像短视频创作者，适合节奏快的带货口播',
    preview_url: null,
    is_default: false,
    is_recommended_free: true,
  },
  {
    voice_id: 'SAz9YHcvj6GT2YYXdXww',
    voice_name: 'River',
    category: 'premade',
    labels: ['neutral', 'informative'],
    description: '中性克制，适合说明型内容和功能演示',
    preview_url: null,
    is_default: false,
    is_recommended_free: true,
  },
  {
    voice_id: 'CwhRBWXzGAHq8TQ4Fs17',
    voice_name: 'Roger',
    category: 'premade',
    labels: ['male', 'casual', 'resonant'],
    description: '松弛自然，适合更口语化的海外广告表达',
    preview_url: null,
    is_default: false,
    is_recommended_free: true,
  },
] satisfies VoiceCatalogItem[]

const STATUS_META = {
  pending: { label: '已创建任务', description: '任务已进入队列，准备开始处理。', step: 0 },
  translating: { label: '正在改写英文口播', description: '翻译模型正在把中文文案改写成自然英文。', step: 1 },
  synthesizing: { label: '正在生成语音', description: 'ElevenLabs 正在为所选音色并发生成音频。', step: 2 },
  completed: { label: '生成完成', description: '英文文案、音频和历史记录都已经准备好。', step: 3 },
  failed: { label: '生成失败', description: '本次任务未完成，请查看错误提示并重试。', step: 3 },
} as const

function parseVoiceInput(rawValue: string): VoiceSelection[] {
  return rawValue
    .split(/[\n,]+/)
    .map((value) => value.trim())
    .filter(Boolean)
    .map((voiceId, index) => ({
      voice_id: voiceId,
      voice_name: `Voice ${index + 1}`,
    }))
}

export default function App() {
  const [sourceText, setSourceText] = useState(EXAMPLE_TEXT)
  const [voiceInput, setVoiceInput] = useState('')
  const [selectedVoiceIds, setSelectedVoiceIds] = useState<string[]>(['EXAVITQu4vr4xnSDxMaL'])
  const [showAdvancedVoices, setShowAdvancedVoices] = useState(false)
  const [voiceCatalog, setVoiceCatalog] = useState<VoiceCatalogItem[]>(VOICE_PRESETS)
  const [voiceCatalogLoading, setVoiceCatalogLoading] = useState(false)
  const [currentJob, setCurrentJob] = useState<Job | null>(null)
  const [historyItems, setHistoryItems] = useState<Job[]>([])
  const [historyKeyword, setHistoryKeyword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [deletingJobId, setDeletingJobId] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [copyMessage, setCopyMessage] = useState('')

  const isPolling = useMemo(() => {
    return currentJob ? ['pending', 'translating', 'synthesizing'].includes(currentJob.status) : false
  }, [currentJob])

  const selectedPresetVoices = useMemo(() => {
    return voiceCatalog.filter((voice) => selectedVoiceIds.includes(voice.voice_id))
  }, [selectedVoiceIds, voiceCatalog])

  const selectedCustomVoices = useMemo(() => parseVoiceInput(voiceInput), [voiceInput])

  const selectedVoices = useMemo(() => {
    const merged = [...selectedPresetVoices, ...selectedCustomVoices]
    const deduped = new Map<string, VoiceSelection>()
    merged.forEach((voice) => {
      deduped.set(voice.voice_id, { voice_id: voice.voice_id, voice_name: voice.voice_name })
    })
    return [...deduped.values()].slice(0, 3)
  }, [selectedCustomVoices, selectedPresetVoices])

  const currentStatusMeta = currentJob ? STATUS_META[currentJob.status] : null
  const completedOutputs = currentJob?.outputs.filter((output) => output.status === 'completed').length ?? 0

  function togglePresetVoice(voiceId: string) {
    setSelectedVoiceIds((current) => {
      if (current.includes(voiceId)) {
        return current.filter((item) => item !== voiceId)
      }
      if (current.length >= 3) {
        setErrorMessage('最多同时选择 3 个音色，便于控制生成时长和成本。')
        return current
      }
      return [...current, voiceId]
    })
  }

  async function loadHistory(keyword = historyKeyword) {
    setHistoryLoading(true)
    try {
      const response = await getHistory(keyword)
      setHistoryItems(response.items)
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '历史记录加载失败')
    } finally {
      setHistoryLoading(false)
    }
  }

  useEffect(() => {
    void loadHistory('')
  }, [])

  useEffect(() => {
    async function loadVoiceCatalog() {
      setVoiceCatalogLoading(true)
      try {
        const response = await getVoiceCatalog()
        if (response.items.length) {
          setVoiceCatalog(response.items)
          const defaultVoice = response.items.find((item) => item.is_default) ?? response.items[0]
          setSelectedVoiceIds((current) => {
            const availableIds = new Set(response.items.map((item) => item.voice_id))
            const stillAvailable = current.filter((voiceId) => availableIds.has(voiceId))
            return stillAvailable.length ? stillAvailable : [defaultVoice.voice_id]
          })
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? `${error.message}，已回退到本地预设音色。` : '音色列表加载失败')
        setVoiceCatalog(VOICE_PRESETS)
      } finally {
        setVoiceCatalogLoading(false)
      }
    }

    void loadVoiceCatalog()
  }, [])

  useEffect(() => {
    if (!isPolling || !currentJob) {
      return
    }

    const timer = window.setInterval(async () => {
      try {
        const latestJob = await getJob(currentJob.job_id)
        setCurrentJob(latestJob)
        if (latestJob.status === 'completed' || latestJob.status === 'failed') {
          await loadHistory()
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : '轮询任务状态失败')
        window.clearInterval(timer)
      }
    }, 2000)

    return () => window.clearInterval(timer)
  }, [currentJob, isPolling])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setErrorMessage('')
    setCopyMessage('')
    try {
      const job = await createJob(sourceText, selectedVoices)
      setCurrentJob(job)
      await loadHistory()
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '提交任务失败')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(jobId: string) {
    setDeletingJobId(jobId)
    setErrorMessage('')
    try {
      await deleteHistory(jobId)
      if (currentJob?.job_id === jobId) {
        setCurrentJob(null)
      }
      await loadHistory()
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '删除失败')
    } finally {
      setDeletingJobId(null)
    }
  }

  async function handleCopy() {
    if (!currentJob?.translated_text) {
      return
    }
    await navigator.clipboard.writeText(currentJob.translated_text)
    setCopyMessage('英文文案已复制')
    window.setTimeout(() => setCopyMessage(''), 1800)
  }

  return (
    <div className="page-shell">
      <header className="hero-panel panel">
        <div>
          <span className="eyebrow">AI Native Tool</span>
          <h1>VoiceBridge Studio</h1>
          <p>把中文短视频口播文案改写成自然英文，并一键生成可试听、可下载的英文语音。</p>
        </div>
        <div className="hero-panel__meta">
          <span>React + FastAPI</span>
          <span>OpenAI-compatible Translation</span>
          <span>ElevenLabs TTS</span>
        </div>
      </header>

      <main className="grid-layout">
        <section className="panel">
          <div className="section-title">
            <div>
              <span className="eyebrow">Input</span>
              <h2>生成任务</h2>
            </div>
            <button className="ghost-button" onClick={() => setSourceText(EXAMPLE_TEXT)} type="button">
              填入示例
            </button>
          </div>

          <form className="job-form" onSubmit={handleSubmit}>
            <label>
              中文口播文案
              <textarea
                value={sourceText}
                onChange={(event) => setSourceText(event.target.value)}
                placeholder="输入中文广告、种草或产品介绍口播稿"
                rows={8}
              />
            </label>

            <div className="voice-picker">
              <div className="voice-picker__header">
                <div>
                  <span className="eyebrow">Voices</span>
                  <h3>多音色选择</h3>
                </div>
                <p>{voiceCatalogLoading ? '正在同步 ElevenLabs 音色...' : `已选择 ${selectedVoices.length} / 3 个音色`}</p>
              </div>

              <div className="voice-picker__grid">
                {voiceCatalog.map((voice) => {
                  const isActive = selectedVoiceIds.includes(voice.voice_id)
                  return (
                    <button
                      className={isActive ? 'voice-option active' : 'voice-option'}
                      key={voice.voice_id}
                      onClick={() => togglePresetVoice(voice.voice_id)}
                      type="button"
                    >
                      <div className="voice-option__top">
                        <strong>{voice.voice_name}</strong>
                        <span>{voice.category}</span>
                      </div>
                      <p>{voice.description || '可直接用于当前账号的 ElevenLabs 语音生成。'}</p>
                      <div className="voice-option__tags">
                        {voice.is_recommended_free ? <em className="voice-badge voice-badge--free">推荐免费可用</em> : null}
                        {voice.is_default ? <em className="voice-badge">默认音色</em> : null}
                        {voice.labels.slice(0, 3).map((label) => (
                          <em className="voice-badge voice-badge--muted" key={`${voice.voice_id}-${label}`}>
                            {label}
                          </em>
                        ))}
                      </div>
                    </button>
                  )
                })}
              </div>

              <div className="voice-picker__tips">
                <span>
                  `premade` 更适合免费账号 API；`professional` 常常需要付费套餐，页面现在会直接标出来。
                </span>
                <button className="ghost-button" onClick={() => setShowAdvancedVoices((value) => !value)} type="button">
                  {showAdvancedVoices ? '收起自定义音色' : '展开自定义音色 ID'}
                </button>
              </div>

              {showAdvancedVoices ? (
                <label>
                  自定义 Voice ID
                  <textarea
                    value={voiceInput}
                    onChange={(event) => setVoiceInput(event.target.value)}
                    placeholder="粘贴你 ElevenLabs 账号里的 Voice ID，用逗号或换行分隔"
                    rows={3}
                  />
                </label>
              ) : null}
            </div>

            <div className="job-form__footer">
              <span>{sourceText.trim().length} / 2000 字符</span>
              <button className="primary-button" type="submit" disabled={submitting}>
                {submitting ? '提交中...' : '开始生成'}
              </button>
            </div>
          </form>

          {errorMessage ? <p className="feedback feedback--error">{errorMessage}</p> : null}
          {copyMessage ? <p className="feedback feedback--success">{copyMessage}</p> : null}
        </section>

        <section className="panel">
          <div className="section-title">
            <div>
              <span className="eyebrow">Result</span>
              <h2>生成结果</h2>
            </div>
            {currentJob ? <span className={`status status--${currentJob.status}`}>{currentJob.status}</span> : null}
          </div>

          {currentJob ? (
            <div className="result-stack">
              {currentStatusMeta ? (
                <div className="status-board">
                  <div className="status-board__header">
                    <div>
                      <h3>{currentStatusMeta.label}</h3>
                      <p>{currentStatusMeta.description}</p>
                    </div>
                    <div className="status-board__metrics">
                      <span>{completedOutputs} 个音色已完成</span>
                      <span>{currentJob.outputs.length} 个音色参与生成</span>
                    </div>
                  </div>
                  <div className="status-track">
                    {['任务创建', '英文改写', '语音生成', '结果就绪'].map((step, index) => (
                      <div className="status-track__step" key={step}>
                        <div className={index <= currentStatusMeta.step ? 'status-track__dot active' : 'status-track__dot'} />
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}

              <div className="result-block">
                <div className="result-block__header">
                  <h3>英文口播文案</h3>
                  <button
                    className="ghost-button"
                    onClick={() => void handleCopy()}
                    type="button"
                    disabled={!currentJob.translated_text}
                  >
                    复制英文
                  </button>
                </div>
                <p className="translation-copy">{currentJob.translated_text || '正在等待翻译结果...'}</p>
                {currentJob.error_message ? <p className="feedback feedback--warn">{currentJob.error_message}</p> : null}
              </div>

              <div className="voice-grid">
                {currentJob.outputs.map((output) => (
                  <VoiceOutputCard key={output.output_id} output={output} />
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              提交任务后，这里会显示翻译结果、多音色音频和逐句高亮效果。
            </div>
          )}
        </section>

        <section className="panel panel--full">
          <div className="section-title">
            <div>
              <span className="eyebrow">History</span>
              <h2>历史记录</h2>
            </div>
            <div className="history-toolbar">
              <input
                value={historyKeyword}
                onChange={(event) => setHistoryKeyword(event.target.value)}
                placeholder="按中文或英文关键词搜索"
              />
              <button className="ghost-button" onClick={() => void loadHistory(historyKeyword)} type="button">
                搜索
              </button>
            </div>
          </div>

          <HistoryList
            items={historyItems}
            loading={historyLoading}
            onReuse={setCurrentJob}
            onDelete={(jobId) => void handleDelete(jobId)}
            deletingJobId={deletingJobId}
          />
        </section>
      </main>
    </div>
  )
}
