export type JobStatus = 'pending' | 'translating' | 'synthesizing' | 'completed' | 'failed'

export interface AlignmentItem {
  sentence: string
  start: number
  end: number
}

export interface VoiceSelection {
  voice_id: string
  voice_name?: string
}

export interface VoiceCatalogItem {
  voice_id: string
  voice_name: string
  category: string
  labels: string[]
  preview_url?: string | null
  description?: string | null
  is_default: boolean
  is_recommended_free: boolean
}

export interface VoiceOutput {
  output_id: string
  voice_id: string
  voice_name: string
  status: JobStatus
  audio_url?: string | null
  duration_seconds?: number | null
  alignment: AlignmentItem[]
  error_message?: string | null
}

export interface Job {
  job_id: string
  status: JobStatus
  source_text: string
  translated_text?: string | null
  error_message?: string | null
  created_at: string
  updated_at: string
  outputs: VoiceOutput[]
}

export interface HistoryResponse {
  items: Job[]
  total: number
  page: number
  page_size: number
}

export interface VoiceCatalogResponse {
  items: VoiceCatalogItem[]
}
