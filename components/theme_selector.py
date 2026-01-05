"""
Theme selector widget and initializer for Streamlit.
"""

from typing import Dict
import streamlit as st

from components.theme_manager import ThemeManager
from components.css_generator import inject_custom_css


def init_theme_system(default_mode: str = ThemeManager.THEME_AUTO) -> None:
    """Initialize theme and inject CSS for the current theme."""
    ThemeManager.init_theme(default_mode)
    inject_custom_css(ThemeManager.get_current_theme())


def render_theme_selector() -> None:
    """Render the theme selector UI in sidebar."""
    current_mode = ThemeManager.get_mode()
    mode = st.selectbox(
        "Theme",
        options=ThemeManager.VALID_MODES,
        index=ThemeManager.VALID_MODES.index(current_mode),
        format_func=lambda m: m.capitalize(),
        key="theme_selector_mode",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Light", key="theme_light", use_container_width=True):
            ThemeManager.set_mode(ThemeManager.THEME_LIGHT)
            st.rerun()
    with col2:
        if st.button("Dark", key="theme_dark", use_container_width=True):
            ThemeManager.set_mode(ThemeManager.THEME_DARK)
            st.rerun()
    with col3:
        if st.button("Auto", key="theme_auto", use_container_width=True):
            ThemeManager.set_mode(ThemeManager.THEME_AUTO)
            st.rerun()

    if mode != current_mode:
        ThemeManager.set_mode(mode)
        st.rerun()

    st.caption(f"Active theme: {ThemeManager.get_current_theme()}")


def render_theme_preview() -> None:
    """Render a preview of theme colors."""
    colors: Dict[str, str] = ThemeManager.get_colors()
    st.markdown("### Theme preview")
    keys = list(colors.keys())
    cols = st.columns(4)
    for idx, key in enumerate(keys):
        with cols[idx % 4]:
            st.markdown(
                f"""
                <div style="
                    background:{colors[key]};
                    padding: 8px;
                    border-radius: 6px;
                    color: #000;
                    margin-bottom: 6px;
                    border: 1px solid rgba(0,0,0,0.1);
                ">
                    <div style="font-size: 12px;">{key}</div>
                    <div style="font-size: 10px;">{colors[key]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
