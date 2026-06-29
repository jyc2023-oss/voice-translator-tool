import type { Job } from '../types'

interface HistoryListProps {
  items: Job[]
  loading: boolean
  onReuse: (job: Job) => void
  onDelete: (jobId: string) => void
  deletingJobId: string | null
}

export default function HistoryList({ items, loading, onReuse, onDelete, deletingJobId }: HistoryListProps) {
  if (loading) {
    return <div className="panel">正在加载历史记录...</div>
  }

  if (!items.length) {
    return <div className="panel">还没有历史记录，先生成一条看看效果。</div>
  }

  return (
    <div className="history-list">
      {items.map((item) => (
        <article className="history-card" key={item.job_id}>
          <div className="history-card__top">
            <span className={`status status--${item.status}`}>{item.status}</span>
            <time>{new Date(item.created_at).toLocaleString()}</time>
          </div>
          <h4>{item.source_text}</h4>
          <p>{item.translated_text || '等待翻译结果...'}</p>
          <div className="history-card__meta">
            <span>{item.outputs.filter((output) => output.status === 'completed').length} 个可用音频</span>
            <span>{item.outputs.map((output) => output.voice_name).join(' / ') || '默认音色'}</span>
          </div>
          <div className="history-card__actions">
            <button className="ghost-button" onClick={() => onReuse(item)} type="button">
              查看结果
            </button>
            <button
              className="ghost-button ghost-button--danger"
              onClick={() => onDelete(item.job_id)}
              type="button"
              disabled={deletingJobId === item.job_id}
            >
              {deletingJobId === item.job_id ? '删除中...' : '删除'}
            </button>
          </div>
        </article>
      ))}
    </div>
  )
}
