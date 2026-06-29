from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError
from app.utils.text_utils import validate_translation


SYSTEM_PROMPT = """You are a professional bilingual copywriter specializing in short-form video ads for English-speaking audiences.

Your task is to translate Chinese spoken promotional scripts into natural, persuasive, and fluent English voice-over scripts.

Requirements:
1. Preserve the original selling points and emotional appeal.
2. Do not translate word by word.
3. Make the output sound natural when spoken aloud.
4. Use concise, vivid, and consumer-friendly expressions.
5. Keep the tone energetic but not exaggerated.
6. Return only the English script, without explanations."""


async def translate_text(source_text: str) -> str:
    if not settings.openai_api_key:
        raise ExternalServiceError("缺少 `OPENAI_API_KEY`，暂时无法调用翻译模型。", status_code=500)
    if not settings.openai_model:
        raise ExternalServiceError("缺少 `OPENAI_MODEL`，请先在 `.env` 中配置模型名。", status_code=500)

    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.openai_model,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Translate the following Chinese short-video voice-over script into English:\n\n{source_text}",
            },
        ],
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500]
        raise ExternalServiceError(f"翻译模型请求失败：{detail}", status_code=502) from exc
    except httpx.HTTPError as exc:
        raise ExternalServiceError("翻译模型连接失败，请检查网络或 Base URL。", status_code=502) from exc

    data = response.json()
    content = ""
    choices = data.get("choices") or []
    if choices:
        content = choices[0].get("message", {}).get("content", "")
    return validate_translation(source_text, content)

