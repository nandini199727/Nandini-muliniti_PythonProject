from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Iterable


def load_json_file(path: str) -> Any:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Quiz file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc.msg} (line {exc.lineno}, col {exc.colno})") from exc


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def utc_timestamp_compact() -> str:
    # Example: 20260311T112233Z
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


_NON_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")


def safe_slug(text: str, max_len: int = 40) -> str:
    text = text.strip().lower()
    text = _NON_FILENAME.sub("-", text).strip("-")
    if not text:
        return "quiz"
    return text[:max_len]


def pct(numer: int, denom: int) -> float:
    return (numer / denom) * 100.0 if denom else 0.0


def mean(values: Iterable[float]) -> float:
    total = 0.0
    count = 0
    for v in values:
        total += float(v)
        count += 1
    return total / count if count else 0.0

