from __future__ import annotations

import re
from collections.abc import Iterable


CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
LEADING_LABEL_RE = re.compile(r"^(here is the translation:|translation:)\s*", re.IGNORECASE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def has_chinese(text: str) -> bool:
    return bool(CHINESE_RE.search(text))


def sanitize_translation(text: str) -> str:
    sanitized = LEADING_LABEL_RE.sub("", text.strip())
    return sanitized.strip().strip('"')


def validate_source_text(source_text: str, max_chars: int) -> str:
    text = source_text.strip()
    if not text:
        raise ValueError("请输入中文口播文案。")
    if len(text) > max_chars:
        raise ValueError(f"输入文本过长，最多支持 {max_chars} 个字符。")
    if len(re.sub(r"[\W_]+", "", text)) < 4:
        raise ValueError("请输入更完整的中文文案，当前内容过短。")
    return text


def validate_translation(source_text: str, translated_text: str) -> str:
    text = sanitize_translation(translated_text)
    if not text:
        raise ValueError("翻译结果为空。")
    if has_chinese(text):
        raise ValueError("翻译结果仍包含中文字符。")
    if len(text) < max(10, int(len(source_text) * 0.2)):
        raise ValueError("翻译结果异常偏短，请稍后重试。")
    return text


def split_sentences(text: str) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    parts = [part.strip() for part in SENTENCE_SPLIT_RE.split(cleaned) if part.strip()]
    return parts or [cleaned]


def compact_keywords(parts: Iterable[str]) -> str:
    return " ".join(part for part in parts if part).strip()

