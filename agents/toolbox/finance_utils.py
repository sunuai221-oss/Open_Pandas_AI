from __future__ import annotations

from typing import Any, Optional


def round_money(value: Any, decimals: int = 2) -> Optional[float]:
    """
    Pure helper for rounding monetary values.
    Returns None if the value cannot be converted to float.
    """
    try:
        return round(float(value), decimals)
    except Exception:
        return None

