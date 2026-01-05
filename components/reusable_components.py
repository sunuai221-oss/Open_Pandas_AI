"""
Reusable UI components built on the theme system.
"""

from typing import List, Dict, Callable, Optional, Any
import streamlit as st

from components.theme_manager import ThemeManager


def render_card(
    title: Optional[str] = None,
    content: Optional[str] = None,
    footer: Optional[str] = None,
    expandable: bool = False,
    key: Optional[str] = None,
    css_class: str = "card",
) -> None:
    colors = ThemeManager.get_colors()
    body = ""
    if title:
        body += f"<h4 style='margin: 0 0 8px 0;'>{title}</h4>"
    if content:
        body += f"<div>{content}</div>"
    if footer:
        body += f"<div style='margin-top: 10px; color: {colors['text_muted']};'>{footer}</div>"

    html = f"<div class='{css_class}'>{body}</div>"
    if expandable:
        with st.expander(title or "Details", expanded=False):
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def render_button_group(
    buttons: List[Dict[str, str]],
    on_click_callback: Optional[Callable[[str], None]] = None,
    orientation: str = "horizontal",
) -> None:
    if orientation == "vertical":
        cols = [st.container()]
    else:
        cols = st.columns(len(buttons))

    for idx, button in enumerate(buttons):
        label = button.get("label", "Button")
        key = button.get("key", f"btn_{idx}")
        icon = button.get("icon", "")
        text = f"{icon} {label}".strip()
        target = cols[idx] if orientation != "vertical" else cols[0]
        with target:
            if st.button(text, key=key, use_container_width=True):
                if on_click_callback:
                    on_click_callback(key)


def render_stat_card(
    label: str,
    value: Any,
    unit: str = "",
    change: Optional[float] = None,
    trend: Optional[str] = None,
) -> None:
    colors = ThemeManager.get_colors()
    trend_color = colors["success"] if trend == "up" else colors["error"] if trend == "down" else colors["text_muted"]
    change_text = ""
    if change is not None:
        sign = "+" if change > 0 else ""
        change_text = f"<div style='color: {trend_color}; font-size: 12px;'>{sign}{change}%</div>"
    st.markdown(
        f"""
        <div class="card">
            <div style="font-size: 12px; color: {colors['text_muted']};">{label}</div>
            <div style="font-size: 22px; font-weight: 700;">{value}{unit}</div>
            {change_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badge(label: str, variant: str = "info", size: str = "md") -> None:
    colors = ThemeManager.get_colors()
    palette = {
        "primary": colors["primary"],
        "success": colors["success"],
        "warning": colors["warning"],
        "error": colors["error"],
        "info": colors["info"],
    }
    size_map = {"sm": "10px", "md": "12px", "lg": "14px"}
    bg = palette.get(variant, colors["primary"])
    st.markdown(
        f"""
        <span class="badge" style="background:{bg}; color: white; font-size:{size_map.get(size, '12px')};">
            {label}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_alert(message: str, alert_type: str = "info", dismissible: bool = False, key: Optional[str] = None) -> None:
    colors = ThemeManager.get_colors()
    palette = {
        "success": colors["success"],
        "warning": colors["warning"],
        "error": colors["error"],
        "info": colors["info"],
    }
    bg = palette.get(alert_type, colors["info"])
    if dismissible:
        st.toast(message)
        return
    st.markdown(
        f"""
        <div class="alert" style="border-color:{bg}; color:{colors['text_primary']};">
            <span style="color:{bg}; font-weight:600;">{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_divider() -> None:
    st.markdown("<hr/>", unsafe_allow_html=True)


def render_section_header(title: str, subtitle: Optional[str] = None, icon: Optional[str] = None) -> None:
    icon_html = f"<span style='margin-right:6px;'>{icon}</span>" if icon else ""
    sub_html = f"<div style='color: var(--color-text-muted);'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header">
            <h3 style="margin: 0;">{icon_html}{title}</h3>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_box(
    title: str,
    content: str,
    icon: Optional[str] = None,
    variant: str = "info",
) -> None:
    colors = ThemeManager.get_colors()
    palette = {
        "info": colors["info"],
        "tip": colors["success"],
        "note": colors["primary"],
        "warning": colors["warning"],
    }
    border = palette.get(variant, colors["info"])
    icon_html = f"<span style='margin-right:6px;'>{icon}</span>" if icon else ""
    st.markdown(
        f"""
        <div class="card" style="border-left: 4px solid {border};">
            <div style="font-weight: 600;">{icon_html}{title}</div>
            <div style="color: {colors['text_secondary']}; margin-top: 4px;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(metrics: List[Dict[str, Any]]) -> None:
    cols = st.columns(len(metrics))
    for idx, metric in enumerate(metrics):
        label = metric.get("label", "")
        value = metric.get("value", "")
        unit = metric.get("unit", "")
        change = metric.get("change")
        trend = metric.get("trend")
        with cols[idx]:
            if change is not None:
                delta = f"{change}{unit}" if unit else str(change)
                st.metric(label, value, delta=delta)
            else:
                st.metric(label, value)
