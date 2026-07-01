from __future__ import annotations

from pathlib import Path

import httpx
from mutagen.mp3 import MP3

from app.core.config import settings
from app.core.errors import ExternalServiceError
from app.schemas.job_schema import VoiceCatalogItem
from app.utils.error_utils import summarize_http_error


VOICE_SETTINGS = {
    "stability": 0.35,
    "similarity_boost": 0.85,
    "style": 0.45,
    "use_speaker_boost": True,
}


async def list_voices() -> list[VoiceCatalogItem]:
    if not settings.elevenlabs_api_key:
        raise ExternalServiceError("缺少 `ELEVENLABS_API_KEY`，暂时无法读取音色列表。", status_code=500)

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": settings.elevenlabs_api_key}

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ExternalServiceError(summarize_http_error("读取 ElevenLabs 音色列表失败", exc), status_code=502) from exc
    except httpx.HTTPError as exc:
        raise ExternalServiceError("读取 ElevenLabs 音色列表失败，请检查网络或 API Key。", status_code=502) from exc

    payload = response.json()
    voices = payload.get("voices") or []
    items: list[VoiceCatalogItem] = []
    for voice in voices:
        labels = [
            label
            for label in [
                voice.get("labels", {}).get("accent"),
                voice.get("labels", {}).get("age"),
                voice.get("labels", {}).get("gender"),
                voice.get("labels", {}).get("descriptive"),
                voice.get("labels", {}).get("use_case"),
            ]
            if label
        ]
        category = (voice.get("category") or "unknown").lower()
        items.append(
            VoiceCatalogItem(
                voice_id=voice.get("voice_id", ""),
                voice_name=voice.get("name", "Unnamed Voice"),
                category=category,
                labels=labels,
                preview_url=voice.get("preview_url"),
                description=voice.get("description"),
                is_default=voice.get("voice_id") == settings.elevenlabs_default_voice_id,
                is_recommended_free=category == "premade",
            )
        )

    items.sort(
        key=lambda item: (
            not item.is_recommended_free,
            not item.is_default,
            item.voice_name.lower(),
        )
    )
    return items


async def synthesize_speech(text: str, voice_id: str, target_path: Path) -> float | None:
    if not settings.elevenlabs_api_key:
        raise ExternalServiceError("缺少 `ELEVENLABS_API_KEY`，暂时无法生成语音。", status_code=500)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": settings.elevenlabs_model,
        "voice_settings": VOICE_SETTINGS,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ExternalServiceError(summarize_http_error("语音合成失败", exc), status_code=502) from exc
    except httpx.HTTPError as exc:
        raise ExternalServiceError("ElevenLabs 连接失败，请检查网络或 API Key。", status_code=502) from exc

    target_path.write_bytes(response.content)
    try:
        return round(MP3(target_path).info.length, 3)
    except Exception:
        return None
