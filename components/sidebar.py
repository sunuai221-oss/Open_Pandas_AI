"""
Sidebar contextuelle unifiée pour Open Pandas-AI.
Affiche les informations de session, mémoire, skills et données actives.
"""

import streamlit as st
from typing import Optional
from core.session_manager import get_session_manager
from core.memory import SessionMemory
from components.theme_selector import init_theme_system
from components.business_domain_selector import render_business_domain_selector


def render_sidebar():
    """
    Affiche la sidebar contextuelle complète.
    """
    init_theme_system("light")
    session = get_session_manager()
    
    # Logo et titre
    st.sidebar.markdown("## 🤖 Open Pandas-AI")
    st.sidebar.markdown("---")
    
    # Section Session
    _render_session_info(session)
    
    st.sidebar.markdown("---")
    
    # Section Mémoire
    _render_memory_status()
    
    st.sidebar.markdown("---")
    
    # Section Données actives
    _render_data_status(session)

    st.sidebar.markdown("---")

    # Section Contexte metier
    render_business_domain_selector(title="Contexte metier")

    st.sidebar.markdown("---")
    
    # Section Préférences
    _render_preferences(session)


def _render_session_info(session):
    """Affiche les informations de session."""
    st.sidebar.markdown("### 👤 Session")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.caption("ID")
        st.code(session.session_id[:8] + "...")
    with col2:
        st.caption("Durée")
        st.markdown(f"**{session.session_duration_minutes}** min")
    
    # Métriques
    metrics = session.get_session_metrics()
    st.sidebar.caption(f"📊 {metrics['exchange_count']} échanges")


def _render_memory_status():
    """Affiche le statut de la mémoire."""
    st.sidebar.markdown("### 🧠 Mémoire")
    
    memory = SessionMemory()
    messages = memory.get_all()
    
    if messages:
        st.sidebar.success(f"✓ {len(messages)} échanges en contexte")
        
        # Aperçu des derniers échanges
        with st.sidebar.expander("Voir le contexte", expanded=False):
            for msg in messages[-3:]:
                role_icon = "👤" if msg.get('role') == 'user' else "🤖"
                content = msg.get('content', '')[:50]
                st.caption(f"{role_icon} {content}...")
        
        # Actions
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🗑️ Effacer", key="sidebar_clear_memory", use_container_width=True):
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
        st.sidebar.info("Mémoire vide")


def _render_data_status(session):
    """Affiche le statut des données chargées."""
    st.sidebar.markdown("### 📊 Données actives")
    
    if session.has_data:
        df = session.df
        name = session.df_name or "DataFrame"
        
        st.sidebar.markdown(f"**{name}**")
        st.sidebar.caption(f"{len(df):,} lignes × {len(df.columns)} colonnes")
        
        # Score de qualité
        quality = session.quality_score
        if quality is not None:
            if quality >= 80:
                st.sidebar.success(f"✓ Qualité: {quality:.0f}/100")
            elif quality >= 60:
                st.sidebar.warning(f"⚠️ Qualité: {quality:.0f}/100")
            else:
                st.sidebar.error(f"❌ Qualité: {quality:.0f}/100")
        
        # Multi-sheets info
        if session.all_sheets:
            st.sidebar.caption(f"📑 {len(session.all_sheets)} feuilles disponibles")
            if session.selected_sheet:
                st.sidebar.caption(f"Feuille active: {session.selected_sheet}")
        
        # Bouton pour changer de données
        if st.sidebar.button("📂 Changer de fichier", key="sidebar_change_file", use_container_width=True):
            session.reset_data()
            st.rerun()
    else:
        st.sidebar.info("Aucune donnée chargée")
        st.sidebar.caption("Uploadez un fichier CSV ou Excel pour commencer")


def _render_preferences(session):
    """Affiche les préférences utilisateur."""
    st.sidebar.markdown("### ⚙️ Préférences")
    
    # Mode utilisateur
    user_level = st.sidebar.selectbox(
        "Mode",
        options=['expert', 'beginner'],
        index=0 if session.user_level == 'expert' else 1,
        format_func=lambda x: "🎓 Expert" if x == 'expert' else "🌱 Débutant",
        key="sidebar_user_level"
    )
    if user_level != session.user_level:
        session.set_user_level(user_level)
    
    # Langue
    language = st.sidebar.selectbox(
        "Langue",
        options=['fr', 'en'],
        index=0 if session.language == 'fr' else 1,
        format_func=lambda x: "🇫🇷 Français" if x == 'fr' else "🇬🇧 English",
        key="sidebar_language"
    )
    if language != session.language:
        session.set_language(language)
    
    # Afficher le code
    show_code = st.sidebar.checkbox(
        "Afficher le code généré",
        value=session.show_code,
        key="sidebar_show_code"
    )
    if show_code != session.show_code:
        session.set_show_code(show_code)



def render_minimal_sidebar():
    """
    Affiche une sidebar minimale pour les pages secondaires.
    """
    init_theme_system("light")
    session = get_session_manager()
    
    st.sidebar.markdown("## 🤖 Open Pandas-AI")
    st.sidebar.markdown("---")
    
    # Info session basique
    st.sidebar.caption(f"Session: {session.session_id[:8]}...")
    st.sidebar.caption(f"Durée: {session.session_duration_minutes} min")
    
    if session.has_data:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**📊 {session.df_name or 'Données'}**")
        st.sidebar.caption(f"{len(session.df):,} lignes")


def render_navigation_buttons():
    """
    Affiche les boutons de navigation rapide dans la sidebar.
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
        if st.button("📚 Historique", key="nav_history", use_container_width=True):
            st.switch_page("pages/4_📚_History.py")
