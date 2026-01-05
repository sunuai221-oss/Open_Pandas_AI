"""
Page Dashboard - Affiche les analyses précédentes dans un format dashboard professionnel
Inspiré par les templates Keen IO Dashboards
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
    subtitle="Visualisez toutes vos analyses et résultats",
    icon="📈"
)

# === EMPTY STATE ===
if not session.exchanges:
    render_empty_state(
        title="Aucune analyse",
        description="Commencez par poser une question dans l'Agent pour voir vos analyses ici",
        icon="📭"
    )
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🚀 Aller à l'Agent", use_container_width=True, type="primary"):
            st.switch_page("pages/3_🤖_Agent.py")
    st.stop()

# === RÉSUMÉ ===
st.markdown("## 📊 Résumé")
render_dashboard_summary(session.exchanges)

# === VUES ===
tab_grid, tab_timeline, tab_detailed = st.tabs(["📱 Grid View", "📍 Timeline", "🔍 Détail"])

# Tab 1: Grid View
with tab_grid:
    st.markdown("### Vue en grille")
    
    # Options
    col1, col2 = st.columns([2, 1])
    with col1:
        columns = st.slider("Colonnes", 1, 4, 2)
    with col2:
        show_code = st.checkbox("Montrer le code", value=False)
    
    # Grid
    render_dashboard_grid(
        exchanges=session.exchanges,
        columns=columns,
        show_code=show_code
    )

# Tab 2: Timeline
with tab_timeline:
    st.markdown("### Vue timeline")
    render_timeline(session.exchanges)

# Tab 3: Analyse détaillée
with tab_detailed:
    st.markdown("### Analyse détaillée")
    
    if session.exchanges:
        # Sélecteur
        options = [
            f"#{len(session.exchanges) - i}: {e.get('question', 'Sans titre')[:50]}"
            for i, e in enumerate(session.exchanges)
        ]
        selected_idx = st.selectbox("Sélectionnez une analyse", range(len(options)), format_func=lambda i: options[i])
        
        # Afficher l'analyse sélectionnée
        exchange = session.exchanges[selected_idx]
        
        st.markdown(f"### ❓ Question")
        st.markdown(f"> **{exchange.get('question', 'Sans titre')}**")
        
        if exchange.get('timestamp'):
            st.caption(f"🕐 {exchange['timestamp']}")
        
        # Résultat
        st.markdown(f"### 🎯 Résultat")
        result = exchange.get('result')
        if isinstance(result, pd.DataFrame):
            st.dataframe(result, use_container_width=True)
            st.caption(f"📊 {len(result)} lignes × {len(result.columns)} colonnes")
        else:
            st.write(result)
        
        # Métadonnées de validation (si disponibles)
        if exchange.get('validation'):
            st.markdown(f"### ✅ Validation")
            validation = exchange['validation']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'quality_score' in validation:
                    st.metric("Score de qualité", f"{validation['quality_score']}%")
            with col2:
                if 'warnings' in validation and validation['warnings']:
                    st.metric("⚠️ Avertissements", len(validation['warnings']))
            with col3:
                if 'suggestions' in validation and validation['suggestions']:
                    st.metric("💬 Suggestions", len(validation['suggestions']))
            
            # Warnings
            if validation.get('warnings'):
                with st.expander("📋 Détails des avertissements"):
                    for w in validation['warnings']:
                        st.warning(w)
            
            # Suggestions
            if validation.get('suggestions'):
                with st.expander("💬 Questions suggérées"):
                    for i, s in enumerate(validation['suggestions'], 1):
                        st.markdown(f"{i}. {s}")
            
            # Interprétation
            if validation.get('interpretation'):
                st.markdown(f"### 💡 Interprétation")
                st.info(validation['interpretation'])
        
        # Code
        if exchange.get('code'):
            with st.expander("🔧 Code exécuté"):
                st.code(exchange['code'], language="python")

# === FOOTER ===
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("➕ Nouvelle analyse", use_container_width=True):
        st.switch_page("pages/3_🤖_Agent.py")

with col2:
    if st.button("📊 Explorer les données", use_container_width=True):
        st.switch_page("pages/2_📊_Data_Explorer.py")

with col3:
    if st.button("⚙️ Paramètres", use_container_width=True):
        st.switch_page("pages/5_⚙️_Settings.py")

st.caption("💡 Conseil: Cliquez sur 'Nouvelle analyse' pour ajouter plus d'analyses à ce dashboard")
