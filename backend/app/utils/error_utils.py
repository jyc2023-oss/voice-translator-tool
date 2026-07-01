from __future__ import annotations

import httpx


def summarize_http_error(prefix: str, exc: httpx.HTTPStatusError) -> str:
    status_code = exc.response.status_code
    request_id = (
        exc.response.headers.get("x-request-id")
        or exc.response.headers.get("request-id")
        or exc.response.headers.get("anthropic-request-id")
    )
    parts = [prefix, f"status={status_code}"]
    if request_id:
        parts.append(f"request_id={request_id}")
    return "，".join(parts)
