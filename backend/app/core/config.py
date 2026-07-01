from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
AUDIO_DIR = BASE_DIR / "audio"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Chinese Voice-over Translator"
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    openai_model: str | None = Field(default=None, alias="OPENAI_MODEL")
    field_encryption_key: str | None = Field(default=None, alias="FIELD_ENCRYPTION_KEY")

    elevenlabs_api_key: str | None = Field(default=None, alias="ELEVENLABS_API_KEY")
    elevenlabs_default_voice_id: str | None = Field(default=None, alias="ELEVENLABS_DEFAULT_VOICE_ID")
    elevenlabs_model: str = Field(default="eleven_multilingual_v2", alias="ELEVENLABS_MODEL")
    elevenlabs_max_concurrency: int = Field(default=2, alias="ELEVENLABS_MAX_CONCURRENCY")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    backend_url: str = Field(default="http://localhost:8000", alias="BACKEND_URL")
    request_timeout_seconds: float = Field(default=60.0, alias="REQUEST_TIMEOUT_SECONDS")
    max_source_chars: int = Field(default=2000, alias="MAX_SOURCE_CHARS")
    max_voice_count: int = Field(default=3, alias="MAX_VOICE_COUNT")
    audio_dir_value: str | None = Field(default=None, alias="AUDIO_DIR")

    @property
    def audio_dir(self) -> Path:
        if self.audio_dir_value:
            return Path(self.audio_dir_value)
        return AUDIO_DIR


settings = Settings()
