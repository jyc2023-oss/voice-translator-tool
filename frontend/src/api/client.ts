import type { HistoryResponse, Job, VoiceCatalogResponse, VoiceSelection } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000'

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = '请求失败'
    try {
      const data = (await response.json()) as { detail?: string }
      detail = data.detail || detail
    } catch {
      detail = response.statusText || detail
    }
    throw new Error(detail)
  }
  return (await response.json()) as T
}

export async function createJob(sourceText: string, voices: VoiceSelection[]): Promise<Job> {
  const response = await fetch(`${API_BASE_URL}/api/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_text: sourceText,
      voices,
    }),
  })
  return parseJson<Job>(response)
}

export async function getJob(jobId: string): Promise<Job> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`)
  return parseJson<Job>(response)
}

export async function getHistory(keyword = ''): Promise<HistoryResponse> {
  const url = new URL(`${API_BASE_URL}/api/history`)
  if (keyword.trim()) {
    url.searchParams.set('keyword', keyword.trim())
  }
  const response = await fetch(url)
  return parseJson<HistoryResponse>(response)
}

export async function deleteHistory(jobId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/history/${jobId}`, { method: 'DELETE' })
  await parseJson<{ success: boolean }>(response)
}

export async function getVoiceCatalog(): Promise<VoiceCatalogResponse> {
  const response = await fetch(`${API_BASE_URL}/api/audio/voices`)
  return parseJson<VoiceCatalogResponse>(response)
}
