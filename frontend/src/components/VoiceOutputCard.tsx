import { useMemo, useState } from 'react'

import type { VoiceOutput } from '../types'

interface VoiceOutputCardProps {
  output: VoiceOutput
}

export default function VoiceOutputCard({ output }: VoiceOutputCardProps) {
  const [currentTime, setCurrentTime] = useState(0)

  const activeSentenceIndex = useMemo(() => {
    return output.alignment.findIndex((item) => currentTime >= item.start && currentTime <= item.end)
  }, [currentTime, output.alignment])

  return (
    <article className="voice-card">
      <div className="voice-card__header">
        <div>
          <h4>{output.voice_name}</h4>
          <p>{output.voice_id}</p>
        </div>
        <span className={`status status--${output.status}`}>{output.status}</span>
      </div>

      {output.error_message ? <p className="voice-card__error">{output.error_message}</p> : null}

      {output.audio_url ? (
        <>
          <div className="voice-card__meta">
            <span>{output.duration_seconds ? `${output.duration_seconds.toFixed(2)} 秒` : '时长读取中'}</span>
            <span>{output.alignment.length} 句同步片段</span>
          </div>
          <audio controls src={output.audio_url} onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)} />
          <a className="ghost-button" href={output.audio_url} download>
            下载音频
          </a>
        </>
      ) : (
        <p className="voice-card__hint">音频生成完成后会显示在这里。</p>
      )}

      {output.alignment.length > 0 ? (
        <div className="alignment-box">
          {output.alignment.map((item, index) => (
            <span
              key={`${output.output_id}-${index}`}
              className={index === activeSentenceIndex ? 'alignment-box__sentence active' : 'alignment-box__sentence'}
            >
              {item.sentence}
            </span>
          ))}
        </div>
      ) : null}
    </article>
  )
}
