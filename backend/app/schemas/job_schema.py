from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class VoiceSelection(BaseModel):
    voice_id: str = Field(min_length=1, max_length=128)
    voice_name: str | None = Field(default=None, max_length=128)


class VoiceCatalogItem(BaseModel):
    voice_id: str
    voice_name: str
    category: str
    labels: list[str] = Field(default_factory=list)
    preview_url: str | None = None
    description: str | None = None
    is_default: bool = False
    is_recommended_free: bool = False


class CreateJobRequest(BaseModel):
    source_text: str = Field(min_length=1, max_length=5000)
    voices: list[VoiceSelection] | None = None
    voice_ids: list[str] | None = None


class AlignmentItem(BaseModel):
    sentence: str
    start: float
    end: float


class VoiceOutputResponse(BaseModel):
    output_id: str
    voice_id: str
    voice_name: str
    status: str
    audio_url: str | None = None
    duration_seconds: float | None = None
    alignment: list[AlignmentItem] = Field(default_factory=list)
    error_message: str | None = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    source_text: str
    translated_text: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    outputs: list[VoiceOutputResponse] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    page_size: int


class DeleteResponse(BaseModel):
    success: bool


class VoiceCatalogResponse(BaseModel):
    items: list[VoiceCatalogItem]
