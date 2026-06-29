from __future__ import annotations

import re
from pathlib import Path


def safe_file_stem(value: str) -> str:
    compact = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return compact or "voice"


def remove_file_if_exists(path: str | None) -> None:
    if not path:
        return
    file_path = Path(path)
    if file_path.exists():
        file_path.unlink()

