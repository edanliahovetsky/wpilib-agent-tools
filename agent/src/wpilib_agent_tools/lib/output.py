"""Output helpers for command modules."""

from __future__ import annotations

import json
from typing import Any


def emit(payload: Any, *, as_json: bool) -> None:
    """Print structured payload either as JSON or repr-like text."""
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    print(payload)


def format_size_bytes(size: int) -> str:
    """Human-friendly byte formatting."""
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{size} B"
