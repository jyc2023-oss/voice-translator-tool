from __future__ import annotations

from app.utils.text_utils import split_sentences


def estimate_alignment(text: str, duration_seconds: float | None) -> list[dict]:
    sentences = split_sentences(text)
    if not sentences:
        return []

    total_duration = duration_seconds or max(3.0, len(text.split()) * 0.42)
    total_weight = sum(max(len(sentence.split()), 1) for sentence in sentences)

    cursor = 0.0
    alignment: list[dict] = []
    for index, sentence in enumerate(sentences):
        weight = max(len(sentence.split()), 1)
        sentence_duration = total_duration * weight / total_weight
        end = total_duration if index == len(sentences) - 1 else round(cursor + sentence_duration, 3)
        alignment.append({"sentence": sentence, "start": round(cursor, 3), "end": round(end, 3)})
        cursor = end
    return alignment

