from __future__ import annotations

from typing import Any, Optional


def safe_ratio(numerator: Any, denominator: Any) -> Optional[float]:
    """
    Pure helper to compute a ratio safely (returns None on invalid inputs / division by zero).
    """
    try:
        d = float(denominator)
        if d == 0:
            return None
        return float(numerator) / d
    except Exception:
        return None

