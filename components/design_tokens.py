"""
Design tokens for the UI theme system.
Keeps colors, spacing, typography, radii, shadows, z-index, and transitions.
"""

from typing import Dict


DESIGN_TOKENS: Dict[str, Dict] = {
    "colors": {
        "dark": {
            "primary": "#60a5fa",
            "primary_light": "#93c5fd",
            "primary_dark": "#1d4ed8",
            "accent": "#f59e0b",
            "bg_primary": "#0b1220",
            "bg_secondary": "#111827",
            "bg_tertiary": "#1f2937",
            "text_primary": "#f9fafb",
            "text_secondary": "#d1d5db",
            "text_muted": "#9ca3af",
            "border": "#374151",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "info": "#38bdf8",
        },
        "light": {
            "primary": "#000000",
            "primary_light": "#111111",
            "primary_dark": "#111111",
            "accent": "#ea580c",
            "bg_primary": "#f8fafc",
            "bg_secondary": "#ffffff",
            "bg_tertiary": "#f1f5f9",
            "text_primary": "#0f172a",
            "text_secondary": "#334155",
            "text_muted": "#64748b",
            "border": "#e2e8f0",
            "success": "#16a34a",
            "warning": "#d97706",
            "error": "#dc2626",
            "info": "#0284c7",
        },
    },
    "spacing": {
        "xs": "4px",
        "sm": "8px",
        "md": "12px",
        "lg": "16px",
        "xl": "24px",
        "2xl": "32px",
        "3xl": "40px",
    },
    "typography": {
        "font_family": "ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
        "font_size": {
            "xs": "12px",
            "sm": "14px",
            "base": "16px",
            "lg": "18px",
            "xl": "20px",
            "2xl": "24px",
            "3xl": "30px",
        },
        "font_weight": {
            "normal": "400",
            "medium": "500",
            "semibold": "600",
            "bold": "700",
        },
    },
    "radii": {
        "none": "0",
        "sm": "4px",
        "md": "8px",
        "lg": "12px",
        "xl": "16px",
        "full": "9999px",
    },
    "shadows": {
        "sm": "0 1px 2px rgba(0, 0, 0, 0.08)",
        "md": "0 4px 8px rgba(0, 0, 0, 0.12)",
        "lg": "0 10px 20px rgba(0, 0, 0, 0.18)",
    },
    "z_index": {
        "dropdown": 10,
        "overlay": 20,
        "modal": 30,
        "tooltip": 40,
    },
    "transitions": {
        "fast": "150ms ease-in-out",
        "normal": "250ms ease-in-out",
        "slow": "350ms ease-in-out",
    },
}


def _get_token(section: str, key: str) -> str:
    if section not in DESIGN_TOKENS or key not in DESIGN_TOKENS[section]:
        raise KeyError(f"Token not found: {section}.{key}")
    return DESIGN_TOKENS[section][key]


def get_color(color_key: str, theme: str) -> str:
    """Return a color by key for the given theme ('light' or 'dark')."""
    if theme not in ("light", "dark"):
        raise ValueError("theme must be 'light' or 'dark'")
    colors = DESIGN_TOKENS["colors"][theme]
    if color_key not in colors:
        raise KeyError(f"Color not found: {color_key}")
    return colors[color_key]


def get_all_colors(theme: str) -> Dict[str, str]:
    """Return the full color palette for the given theme."""
    if theme not in ("light", "dark"):
        raise ValueError("theme must be 'light' or 'dark'")
    return dict(DESIGN_TOKENS["colors"][theme])


def get_spacing(spacing_key: str) -> str:
    """Return a spacing token."""
    return _get_token("spacing", spacing_key)


def get_font_size(size_key: str) -> str:
    """Return a font size token."""
    sizes = DESIGN_TOKENS["typography"]["font_size"]
    if size_key not in sizes:
        raise KeyError(f"Font size not found: {size_key}")
    return sizes[size_key]


def get_radius(radius_key: str) -> str:
    """Return a border radius token."""
    return _get_token("radii", radius_key)
