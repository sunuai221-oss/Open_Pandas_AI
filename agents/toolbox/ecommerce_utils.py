from __future__ import annotations

from typing import Any, Optional


def safe_int(value: Any) -> Optional[int]:
    """Pure helper to convert a value to int; returns None on failure."""
    try:
        return int(value)
    except Exception:
        return None

