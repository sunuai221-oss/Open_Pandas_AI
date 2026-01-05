"""
Theme manager for Streamlit session state.
Supports light, dark, and auto modes.
"""

from typing import Dict
import streamlit as st

from components.design_tokens import get_all_colors, get_color


class ThemeManager:
    THEME_AUTO = "auto"
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    VALID_MODES = [THEME_AUTO, THEME_LIGHT, THEME_DARK]

    _SESSION_KEY = "theme_mode"

    @classmethod
    def init_theme(cls, default_mode: str = THEME_AUTO) -> None:
        """Initialize theme in Streamlit session_state."""
        if default_mode not in cls.VALID_MODES:
            default_mode = cls.THEME_AUTO
        if cls._SESSION_KEY not in st.session_state:
            st.session_state[cls._SESSION_KEY] = default_mode

    @classmethod
    def get_mode(cls) -> str:
        """Return the current theme mode (auto/light/dark)."""
        return st.session_state.get(cls._SESSION_KEY, cls.THEME_AUTO)

    @classmethod
    def set_mode(cls, mode: str) -> None:
        """Set the theme mode."""
        if mode not in cls.VALID_MODES:
            raise ValueError(f"Invalid theme mode: {mode}")
        st.session_state[cls._SESSION_KEY] = mode

    @classmethod
    def get_current_theme(cls) -> str:
        """Resolve the active theme to 'light' or 'dark'."""
        mode = cls.get_mode()
        if mode in (cls.THEME_LIGHT, cls.THEME_DARK):
            return mode
        # Auto: best-effort detection from Streamlit config
        try:
            base = st.get_option("theme.base")
            if base in (cls.THEME_LIGHT, cls.THEME_DARK):
                return base
        except Exception:
            pass
        return cls.THEME_DARK

    @classmethod
    def is_dark(cls) -> bool:
        return cls.get_current_theme() == cls.THEME_DARK

    @classmethod
    def is_light(cls) -> bool:
        return cls.get_current_theme() == cls.THEME_LIGHT

    @classmethod
    def toggle_theme(cls) -> None:
        current = cls.get_current_theme()
        cls.set_mode(cls.THEME_LIGHT if current == cls.THEME_DARK else cls.THEME_DARK)

    @classmethod
    def get_colors(cls) -> Dict[str, str]:
        return get_all_colors(cls.get_current_theme())

    @classmethod
    def get_color(cls, color_key: str) -> str:
        return get_color(color_key, cls.get_current_theme())


class _ThemeProxy:
    """Instance-style proxy for ThemeManager."""

    def init_theme(self, default_mode: str = ThemeManager.THEME_AUTO) -> None:
        ThemeManager.init_theme(default_mode)

    def get_mode(self) -> str:
        return ThemeManager.get_mode()

    def set_mode(self, mode: str) -> None:
        ThemeManager.set_mode(mode)

    def get_current_theme(self) -> str:
        return ThemeManager.get_current_theme()

    def is_dark(self) -> bool:
        return ThemeManager.is_dark()

    def is_light(self) -> bool:
        return ThemeManager.is_light()

    def toggle_theme(self) -> None:
        ThemeManager.toggle_theme()

    def get_colors(self) -> Dict[str, str]:
        return ThemeManager.get_colors()

    def get_color(self, color_key: str) -> str:
        return ThemeManager.get_color(color_key)


theme = _ThemeProxy()
