"""
Dashboard Page - Displays previous analyses in a professional dashboard format
Inspired by Keen IO Dashboard templates
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="Open Pandas-AI - Dashboard",
    page_icon="📈",
    layout="wide"
)

from components.sidebar import render_sidebar
from components.dashboard import (
    render_dashboard_header,
    render_stats_grid,
    render_dashboard_grid,
    render_timeline,
    render_dashboard_summary,
    render_hero_section,
    render_empty_state,
    render_insight_box
)
from core.session_manager import get_session_manager

# Session
session = get_session_manager()

# Sidebar
render_sidebar()

# === HEADER ===
render_dashboard_header(
    title="Analytics Dashboard",
    subtitle="Visualize all your analyses and results",
    icon="📈"
)

# === EMPTY STATE ===
if not session.exchanges:
    render_empty_state(
        title="No Analysis",
        description="Start by asking a question in the Agent to see your analyses here",
        icon="📭"
    )
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🚀 Go to Agent", use_container_width=True, type="primary"):
            st.switch_page("pages/3_🤖_Agent.py")
    st.stop()

# === SUMMARY ===
st.markdown("## 📊 Summary")
render_dashboard_summary(session.exchanges)

# === VIEWS ===
tab_grid, tab_timeline, tab_detailed = st.tabs(["📱 Grid View", "📍 Timeline", "🔍 Detail"])

# Tab 1: Grid View
with tab_grid:
    st.markdown("### Grid View")
    
    # Options
    col1, col2 = st.columns([2, 1])
    with col1:
        columns = st.slider("Columns", 1, 4, 2)
    with col2:
        show_code = st.checkbox("Show Code", value=False)
    
    # Grid
    render_dashboard_grid(
        exchanges=session.exchanges,
        columns=columns,
        show_code=show_code
    )

# Tab 2: Timeline
with tab_timeline:
    st.markdown("### Timeline View")
    render_timeline(session.exchanges)

# Tab 3: Detailed Analysis
with tab_detailed:
    st.markdown("### Detailed Analysis")
    
    if session.exchanges:
        # Selector
        options = [
            f"#{len(session.exchanges) - i}: {e.get('question', 'No title')[:50]}"
            for i, e in enumerate(session.exchanges)
        ]
        selected_idx = st.selectbox("Select an analysis", range(len(options)), format_func=lambda i: options[i])
        
        # Afficher l'analyse sélectionnée
        exchange = session.exchanges[selected_idx]
        
        st.markdown(f"### ❓ Question")
        st.markdown(f"> **{exchange.get('question', 'No title')}**")
        
        if exchange.get('timestamp'):
            st.caption(f"🕐 {exchange['timestamp']}")
        
        # Result
        st.markdown(f"### 🎯 Result")
        result = exchange.get('result')
        if isinstance(result, pd.DataFrame):
            st.dataframe(result, use_container_width=True)
            st.caption(f"📊 {len(result)} rows × {len(result.columns)} columns")
        else:
            st.write(result)
        
        # Validation metadata (if available)
        if exchange.get('validation'):
            st.markdown(f"### ✅ Validation")
            validation = exchange['validation']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'quality_score' in validation:
                    st.metric("Quality Score", f"{validation['quality_score']}%")
            with col2:
                if 'warnings' in validation and validation['warnings']:
                    st.metric("⚠️ Warnings", len(validation['warnings']))
            with col3:
                if 'suggestions' in validation and validation['suggestions']:
                    st.metric("💬 Suggestions", len(validation['suggestions']))
            
            # Warnings
            if validation.get('warnings'):
                with st.expander("📋 Warning Details"):
                    for w in validation['warnings']:
                        st.warning(w)
            
            # Suggestions
            if validation.get('suggestions'):
                with st.expander("💬 Suggested Questions"):
                    for i, s in enumerate(validation['suggestions'], 1):
                        st.markdown(f"{i}. {s}")
            
            # Interpretation
            if validation.get('interpretation'):
                st.markdown(f"### 💡 Interpretation")
                st.info(validation['interpretation'])
        
        # Code
        if exchange.get('code'):
            with st.expander("🔧 Executed Code"):
                st.code(exchange['code'], language="python")

# === FOOTER ===
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("➕ New Analysis", use_container_width=True):
        st.switch_page("pages/3_🤖_Agent.py")

with col2:
    if st.button("📊 Explore Data", use_container_width=True):
        st.switch_page("pages/2_📊_Data_Explorer.py")

with col3:
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/5_⚙️_Settings.py")

st.caption("💡 Tip: Click 'New Analysis' to add more analyses to this dashboard")
