"""
Enhanced result display component.
"""

import streamlit as st
import pandas as pd
from typing import Any, Optional, Dict
from datetime import datetime

from core.session_manager import get_session_manager

def render_result(
    result: Any,
    title: str = "Result",
    show_stats: bool = True,
    show_actions: bool = True,
    key_prefix: str = "result"
):
    """
    Displays a result in an enhanced way.
    
    Args:
        result: Result to display (DataFrame, scalar, str, etc.)
        title: Section title
        show_stats: Show quick statistics
        show_actions: Show actions (export, etc.)
        key_prefix: Prefix for Streamlit keys
    """
    
    st.markdown(f"### 📊 {title}")
    
    if result is None:
        st.info("No result to display")
        return
    
    if isinstance(result, pd.DataFrame):
        _render_dataframe_result(result, show_stats, show_actions, key_prefix)
    elif isinstance(result, (int, float)):
        _render_numeric_result(result)
    elif isinstance(result, str):
        _render_text_result(result)
    elif isinstance(result, (list, tuple)):
        _render_list_result(result)
    elif isinstance(result, dict):
        _render_dict_result(result)
    else:
        st.write(result)


def _render_dataframe_result(
    df: pd.DataFrame,
    show_stats: bool,
    show_actions: bool,
    key_prefix: str
):
    """Displays a DataFrame result."""
    
    if df.empty:
        st.warning("DataFrame is empty")
        return
    
    # Tabs: Table | Stats | Actions
    tabs = ["📋 Table"]
    if show_stats:
        tabs.append("📈 Statistics")
    
    tab_objects = st.tabs(tabs)
    
    # Table tab
    with tab_objects[0]:
        # Display options
        col1, col2 = st.columns([3, 1])
        with col2:
            session = get_session_manager()
            row_options = [10, 25, 50, 100, 500, "All"]
            current_max_rows = session.display_max_rows
            if current_max_rows not in row_options:
                current_max_rows = 25
            max_rows = st.selectbox(
                "Rows",
                options=row_options,
                index=row_options.index(current_max_rows),
                key=f"{key_prefix}_max_rows"
            )
            if max_rows != session.display_max_rows:
                session.set_display_max_rows(max_rows)
        
        # DataFrame display
        display_df = df if max_rows == "All" else df.head(int(max_rows))
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Info
        st.caption(f"Display: {len(display_df)} / {len(df)} rows • {len(df.columns)} columns")
    
    # Stats tab
    if show_stats and len(tab_objects) > 1:
        with tab_objects[1]:
            _render_quick_stats(df)
    
    # Actions
    if show_actions:
        st.markdown("---")
        _render_result_actions(df, key_prefix)


def _render_quick_stats(df: pd.DataFrame):
    """Displays quick statistics."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Numeric Overview")
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            st.dataframe(numeric_df.describe(), use_container_width=True)
        else:
            st.info("No numeric columns")
    
    with col2:
        st.markdown("#### Categorical Overview")
        cat_df = df.select_dtypes(include=['object', 'category'])
        if not cat_df.empty:
            for col in cat_df.columns[:3]:  # Limit to 3 columns
                st.markdown(f"**{col}**: {df[col].nunique()} unique values")
                st.caption(f"Top: {df[col].value_counts().head(3).to_dict()}")
        else:
            st.info("No categorical columns")


def _render_result_actions(df: pd.DataFrame, key_prefix: str):
    """Displays available actions for the result."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Export Excel
        from core import excel_utils
        buffer = excel_utils.export_dataframe_to_buffer(df, sheet_name="Result")
        st.download_button(
            "📥 Excel",
            data=buffer,
            file_name=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"{key_prefix}_excel",
            use_container_width=True
        )
    
    with col2:
        # Export CSV
        csv = df.to_csv(index=False)
        st.download_button(
            "📄 CSV",
            data=csv,
            file_name=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"{key_prefix}_csv",
            use_container_width=True
        )
    
    with col3:
        if st.button("📈 Visualize", key=f"{key_prefix}_viz", use_container_width=True):
            st.session_state['suggested_question'] = "Generate a chart of this result"
            st.rerun()
    
    with col4:
        if st.button("🔍 Deepen", key=f"{key_prefix}_deep", use_container_width=True):
            st.session_state['suggested_question'] = "Analyze this result in more detail"
            st.rerun()


def _render_numeric_result(value: float):
    """Displays a numeric result."""
    
    if isinstance(value, float):
        formatted = f"{value:,.2f}"
    else:
        formatted = f"{value:,}"
    
    st.metric("Value", formatted)


def _render_text_result(text: str):
    """Affiche un résultat texte."""
    
    if text.startswith("Erreur"):
        st.error(text)
    else:
        st.info(text)


def _render_list_result(items: list):
    """Affiche un résultat liste."""
    
    if len(items) <= 10:
        for item in items:
            st.markdown(f"• {item}")
    else:
        st.write(items[:10])
        st.caption(f"... et {len(items) - 10} autres éléments")


def _render_dict_result(data: dict):
    """Affiche un résultat dictionnaire."""
    
    st.json(data)


def render_result_comparison(result1: Any, result2: Any, labels: tuple = ("Avant", "Après")):
    """
    Affiche une comparaison de deux résultats côte à côte.
    """
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {labels[0]}")
        if isinstance(result1, pd.DataFrame):
            st.dataframe(result1, use_container_width=True)
        else:
            st.write(result1)
    
    with col2:
        st.markdown(f"### {labels[1]}")
        if isinstance(result2, pd.DataFrame):
            st.dataframe(result2, use_container_width=True)
        else:
            st.write(result2)


def render_result_card(
    title: str,
    value: Any,
    subtitle: str = "",
    icon: str = "📊"
):
    """
    Affiche un résultat sous forme de carte.
    """
    
    st.markdown(f"""
    <div style="
        background: rgba(100, 100, 100, 0.1);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    ">
        <div style="font-size: 28px;">{icon}</div>
        <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">{value}</div>
        <div style="font-weight: bold;">{title}</div>
        <div style="color: var(--text-secondary); font-size: 12px;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
