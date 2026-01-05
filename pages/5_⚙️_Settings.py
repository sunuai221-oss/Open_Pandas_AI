"""
Page Settings - Paramètres utilisateur.
"""

import streamlit as st
import json
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="Open Pandas-AI - Paramètres",
    page_icon="⚙️",
    layout="wide"
)

from components.sidebar import render_minimal_sidebar
from components.llm_provider import render_llm_provider_selector
from core.session_manager import get_session_manager
from core.memory import SessionMemory

# Session
session = get_session_manager()
memory = SessionMemory()

# Sidebar
render_minimal_sidebar()

# Header
st.title("⚙️ Paramètres")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["?? Pr?f?rences", "LLM Provider", "?? M?moire", "?? Session", "?? ? propos"])

# Tab 1: Préférences
with tab1:
    st.markdown("### 👤 Préférences utilisateur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Mode d'affichage")
        
        user_level = st.radio(
            "Niveau utilisateur",
            options=['expert', 'beginner'],
            index=0 if session.user_level == 'expert' else 1,
            format_func=lambda x: "🎓 Expert - Toutes les options" if x == 'expert' else "🌱 Débutant - Interface simplifiée",
            horizontal=True
        )
        if user_level != session.user_level:
            session.set_user_level(user_level)
            st.success(f"Mode changé en: {user_level}")
        
        st.markdown("---")
        
        language = st.selectbox(
            "🌐 Langue",
            options=['fr', 'en'],
            index=0 if session.language == 'fr' else 1,
            format_func=lambda x: "🇫🇷 Français" if x == 'fr' else "🇬🇧 English"
        )
        if language != session.language:
            session.set_language(language)
            st.success(f"Langue changée en: {language}")
    
    with col2:
        st.markdown("#### Affichage du code")
        
        show_code = st.checkbox(
            "Afficher le code Python généré",
            value=session.show_code,
            help="Affiche le code généré par l'IA pour chaque question"
        )
        if show_code != session.show_code:
            session.set_show_code(show_code)
            st.success("Préférence mise à jour")
        
        st.markdown("---")
        
        st.markdown("#### Thème")
        st.info("Le thème est géré par Streamlit. Allez dans Paramètres > Thème dans le menu (☰)")

# Tab 2: LLM Provider
with tab2:
    render_llm_provider_selector(title="LLM Provider")

# Tab 3: M?moire
with tab3:
    st.markdown("### 🧠 Gestion de la mémoire")
    
    messages = memory.get_all()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.metric("Messages en mémoire", len(messages))
        
        if messages:
            st.markdown("#### Aperçu du contexte")
            with st.expander("Voir les messages", expanded=False):
                for msg in messages:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    timestamp = msg.get('timestamp', '')
                    
                    icon = "👤" if role == 'user' else "🤖"
                    st.markdown(f"**{icon} {role}** {f'• {timestamp}' if timestamp else ''}")
                    st.markdown(f"> {content[:200]}{'...' if len(content) > 200 else ''}")
                    st.markdown("---")
    
    with col2:
        st.markdown("#### Actions")
        
        if st.button("🗑️ Effacer la mémoire", use_container_width=True, type="secondary"):
            memory.clear()
            st.success("Mémoire effacée")
            st.rerun()
        
        st.markdown("---")
        
        # Export
        st.markdown("#### Export/Import")
        
        export_data = json.dumps(memory.export(), ensure_ascii=False, indent=2)
        st.download_button(
            "💾 Exporter la mémoire",
            data=export_data,
            file_name=f"memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        uploaded = st.file_uploader("📂 Importer une mémoire", type=['json'], key="settings_memory_import")
        if uploaded:
            try:
                imported = json.load(uploaded)
                memory.import_history(imported)
                st.success("Mémoire importée avec succès")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur d'import: {e}")

# Tab 4: Session
with tab4:
    st.markdown("### 📊 Informations de session")
    
    metrics = session.get_session_metrics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Identité")
        st.code(f"Session ID: {session.session_id}")
        st.metric("Durée", f"{metrics['duration_minutes']} minutes")
    
    with col2:
        st.markdown("#### Activité")
        st.metric("Échanges", metrics['exchange_count'])
        st.metric("Données chargées", "Oui" if metrics['has_data'] else "Non")
    
    with col3:
        st.markdown("#### Données")
        if metrics['has_data']:
            st.info(f"📁 {metrics['data_name'] or 'DataFrame'}")
            if metrics['quality_score']:
                st.metric("Qualité", f"{metrics['quality_score']:.0f}/100")
        else:
            st.warning("Aucune donnée")
    
    st.markdown("---")
    
    st.markdown("#### Actions de session")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Réinitialiser les données", use_container_width=True):
            session.reset_data()
            st.success("Données réinitialisées")
            st.rerun()
    
    with col2:
        if st.button("⚠️ Réinitialiser la session complète", use_container_width=True, type="secondary"):
            if st.checkbox("Je confirme vouloir tout réinitialiser"):
                session.reset_session()
                memory.clear()
                st.success("Session réinitialisée")
                st.rerun()

# Tab 4: À propos
with tab4:
    st.markdown("### ℹ️ À propos de Open Pandas-AI")
    
    st.markdown("""
    **Open Pandas-AI** est un agent d'analyse de données intelligent qui permet 
    d'interroger vos fichiers CSV et Excel en langage naturel.
    
    #### 🛠️ Technologies utilisées
    
    | Composant | Technologie |
    |-----------|-------------|
    | Frontend | Streamlit |
    | LLM | Codestral (Mistral AI) |
    | Data Processing | Pandas |
    | Base de données | PostgreSQL / SQLite |
    | Exécution sécurisée | Docker Sandbox |
    
    #### 🔒 Sécurité
    
    - Exécution du code dans un environnement sandboxé
    - Analyse AST du code généré
    - Blocage des opérations dangereuses
    - Pas d'accès réseau dans le sandbox
    
    #### 🎯 Fonctionnalités principales
    
    - ✅ Analyse de données en langage naturel
    - ✅ Support multi-fichiers (CSV, Excel)
    - ✅ Support multi-feuilles Excel
    - ✅ Tableaux croisés dynamiques
    - ✅ Génération de graphiques
    - ✅ Export Excel formaté
    - ✅ Détection d'anomalies
    - ✅ Mémoire contextuelle
    - ✅ Analyse professionnelle des résultats
    
    #### 📝 Licence
    
    Open source - MIT License
    
    ---
    
    *Version 2.0 - Refonte Frontend Multi-Pages*
    """)
    
    # API Status
    st.markdown("---")
    st.markdown("#### 🔌 Statut API")
    
    try:
        from core.llm import call_llm
        st.success("✅ API Mistral AI connectée")
    except Exception as e:
        st.error(f"❌ Erreur API: {e}")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Accueil", use_container_width=True):
        st.switch_page("pages/1_🏠_Home.py")
with col2:
    if st.button("🤖 Agent IA", use_container_width=True, type="primary"):
        st.switch_page("pages/3_🤖_Agent.py")
