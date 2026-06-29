from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.utils.file_utils import safe_file_stem


def ensure_audio_dir() -> Path:
    settings.audio_dir.mkdir(parents=True, exist_ok=True)
    return settings.audio_dir


def build_audio_path(job_id: str, voice_name: str) -> Path:
    ensure_audio_dir()
    filename = f"{job_id}_{safe_file_stem(voice_name)}.mp3"
    return settings.audio_dir / filename


def build_audio_url(file_path: Path) -> str:
    return f"{settings.backend_url.rstrip('/')}/audio/{file_path.name}"

