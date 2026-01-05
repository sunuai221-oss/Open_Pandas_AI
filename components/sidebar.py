"""
Unified contextual sidebar for Open Pandas-AI.
Displays session information, memory, skills and active data.
"""

import streamlit as st
from typing import Optional
from core.session_manager import get_session_manager
from core.memory import SessionMemory
from components.theme_selector import init_theme_system
from components.business_domain_selector import render_business_domain_selector


def render_sidebar():
    """
    Displays the complete contextual sidebar.
    """
    init_theme_system("light")
    session = get_session_manager()
    
    # Logo and title
    st.sidebar.markdown("## 🤖 Open Pandas-AI")
    st.sidebar.markdown("---")
    
    # Session section
    _render_session_info(session)
    
    st.sidebar.markdown("---")
    
    # Memory section
    _render_memory_status()
    
    st.sidebar.markdown("---")
    
    # Active data section
    _render_data_status(session)

    st.sidebar.markdown("---")

    # Business context section
    render_business_domain_selector(title="Business Context")

    st.sidebar.markdown("---")
    
    # Preferences section
    _render_preferences(session)


def _render_session_info(session):
    """Displays session information."""
    st.sidebar.markdown("### 👤 Session")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.caption("ID")
        st.code(session.session_id[:8] + "...")
    with col2:
        st.caption("Duration")
        st.markdown(f"**{session.session_duration_minutes}** min")
    
    # Metrics
    metrics = session.get_session_metrics()
    st.sidebar.caption(f"📊 {metrics['exchange_count']} exchanges")


def _render_memory_status():
    """Displays memory status."""
    st.sidebar.markdown("### 🧠 Memory")
    
    memory = SessionMemory()
    messages = memory.get_all()
    
    if messages:
        st.sidebar.success(f"✓ {len(messages)} exchanges in context")
        
        # Preview of last exchanges
        with st.sidebar.expander("View context", expanded=False):
            for msg in messages[-3:]:
                role_icon = "👤" if msg.get('role') == 'user' else "🤖"
                content = msg.get('content', '')[:50]
                st.caption(f"{role_icon} {content}...")
        
        # Actions
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🗑️ Clear", key="sidebar_clear_memory", use_container_width=True):
                memory.clear()
                st.rerun()
        with col2:
            if st.button("💾 Export", key="sidebar_export_memory", use_container_width=True):
                data = memory.export()
                st.download_button(
                    "📥 JSON",
                    data=str(data),
                    file_name="memory_export.json",
                    key="sidebar_download_memory"
                )
    else:
        st.sidebar.info("Memory empty")


def _render_data_status(session):
    """Displays loaded data status."""
    st.sidebar.markdown("### 📊 Active Data")
    
    if session.has_data:
        df = session.df
        name = session.df_name or "DataFrame"
        
        st.sidebar.markdown(f"**{name}**")
        st.sidebar.caption(f"{len(df):,} rows × {len(df.columns)} columns")
        
        # Quality score
        quality = session.quality_score
        if quality is not None:
            if quality >= 80:
                st.sidebar.success(f"✓ Quality: {quality:.0f}/100")
            elif quality >= 60:
                st.sidebar.warning(f"⚠️ Quality: {quality:.0f}/100")
            else:
                st.sidebar.error(f"❌ Quality: {quality:.0f}/100")
        
        # Multi-sheets info
        if session.all_sheets:
            st.sidebar.caption(f"📑 {len(session.all_sheets)} sheets available")
            if session.selected_sheet:
                st.sidebar.caption(f"Active sheet: {session.selected_sheet}")
        
        # Button to change data
        if st.sidebar.button("📂 Change File", key="sidebar_change_file", use_container_width=True):
            session.reset_data()
            st.rerun()
    else:
        st.sidebar.info("No data loaded")
        st.sidebar.caption("Upload a CSV or Excel file to start")


def _render_preferences(session):
    """Displays user preferences."""
    st.sidebar.markdown("### ⚙️ Preferences")
    
    # User mode
    user_level = st.sidebar.selectbox(
        "Mode",
        options=['expert', 'beginner'],
        index=0 if session.user_level == 'expert' else 1,
        format_func=lambda x: "🎓 Expert" if x == 'expert' else "🌱 Beginner",
        key="sidebar_user_level"
    )
    if user_level != session.user_level:
        session.set_user_level(user_level)
    
    # Language
    language = st.sidebar.selectbox(
        "Language",
        options=['fr', 'en'],
        index=0 if session.language == 'fr' else 1,
        format_func=lambda x: "🇫🇷 Français" if x == 'fr' else "🇬🇧 English",
        key="sidebar_language"
    )
    if language != session.language:
        session.set_language(language)
    
    # Show code
    show_code = st.sidebar.checkbox(
        "Show generated code",
        value=session.show_code,
        key="sidebar_show_code"
    )
    if show_code != session.show_code:
        session.set_show_code(show_code)



def render_minimal_sidebar():
    """
    Displays a minimal sidebar for secondary pages.
    """
    init_theme_system("light")
    session = get_session_manager()
    
    st.sidebar.markdown("## 🤖 Open Pandas-AI")
    st.sidebar.markdown("---")
    
    # Basic session info
    st.sidebar.caption(f"Session: {session.session_id[:8]}...")
    st.sidebar.caption(f"Duration: {session.session_duration_minutes} min")
    
    if session.has_data:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**📊 {session.df_name or 'Data'}**")
        st.sidebar.caption(f"{len(session.df):,} rows")


def render_navigation_buttons():
    """
    Displays quick navigation buttons in the sidebar.
    """
    st.sidebar.markdown("### 🧭 Navigation")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.switch_page("pages/1_🏠_Home.py")
        if st.button("🤖 Agent", key="nav_agent", use_container_width=True):
            st.switch_page("pages/3_🤖_Agent.py")
    with col2:
        if st.button("📊 Explorer", key="nav_explorer", use_container_width=True):
            st.switch_page("pages/2_📊_Data_Explorer.py")
        if st.button("📚 History", key="nav_history", use_container_width=True):
            st.switch_page("pages/4_📚_History.py")
