"""
Composant d'affichage des suggestions intelligentes.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import pandas as pd
from core.suggestions import SmartSuggestions, get_suggestions, get_followup_suggestions


def render_suggestions(
    df: Optional[pd.DataFrame] = None,
    user_level: str = 'expert',
    limit: int = 6,
    title: str = "💡 Suggestions"
):
    """
    Affiche les suggestions sous forme de boutons cliquables.
    
    Args:
        df: DataFrame actuel
        user_level: Niveau utilisateur ('beginner' ou 'expert')
        limit: Nombre maximum de suggestions
        title: Titre de la section
    """
    suggestions = get_suggestions(df=df, user_level=user_level, limit=limit)
    
    if not suggestions:
        return
    
    st.markdown(f"### {title}")
    
    # Afficher en colonnes
    cols_per_row = 3
    for i in range(0, len(suggestions), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, suggestion in enumerate(suggestions[i:i+cols_per_row]):
            with cols[j]:
                icon = suggestion.get('icon', '💡')
                text = suggestion.get('text', '')
                
                if st.button(
                    f"{icon} {text}",
                    key=f"suggestion_{i+j}_{text[:20]}",
                    use_container_width=True
                ):
                    st.session_state['suggested_question'] = text
                    st.rerun()


def render_suggestion_chips(
    suggestions: List[Dict[str, Any]],
    key_prefix: str = "chip"
):
    """
    Affiche les suggestions sous forme de chips/tags horizontaux.
    """
    if not suggestions:
        return
    
    # CSS pour les chips
    st.markdown("""
    <style>
    .suggestion-chip {
        display: inline-block;
        background: rgba(100, 150, 200, 0.2);
        border: 1px solid rgba(100, 150, 200, 0.5);
        border-radius: 20px;
        padding: 5px 15px;
        margin: 3px;
        cursor: pointer;
        font-size: 14px;
    }
    .suggestion-chip:hover {
        background: rgba(100, 150, 200, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            icon = suggestion.get('icon', '💡')
            text = suggestion.get('text', '')
            
            if st.button(f"{icon} {text}", key=f"{key_prefix}_{i}", use_container_width=True):
                st.session_state['suggested_question'] = text
                st.rerun()


def render_followup_suggestions(
    last_question: str,
    last_result: Any,
    limit: int = 3
):
    """
    Affiche les suggestions de suivi après une réponse.
    """
    followups = get_followup_suggestions(last_question, last_result, limit)
    
    if not followups:
        return
    
    st.markdown("**💬 Questions de suivi suggérées:**")
    
    cols = st.columns(len(followups))
    for i, suggestion in enumerate(followups):
        with cols[i]:
            icon = suggestion.get('icon', '➡️')
            text = suggestion.get('text', '')
            
            if st.button(
                f"{icon} {text}",
                key=f"followup_{i}_{text[:10]}",
                use_container_width=True
            ):
                st.session_state['suggested_question'] = text
                st.rerun()


def render_quick_actions(df: Optional[pd.DataFrame] = None):
    """
    Affiche des actions rapides basées sur les données.
    """
    if df is None:
        return
    
    st.markdown("### ⚡ Actions rapides")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Résumé statistique", key="quick_stats", use_container_width=True):
            st.session_state['suggested_question'] = "Résumé statistique complet"
            st.rerun()
    
    with col2:
        if st.button("🔍 Détecter anomalies", key="quick_anomaly", use_container_width=True):
            st.session_state['suggested_question'] = "Détecte les valeurs aberrantes"
            st.rerun()
    
    with col3:
        if st.button("📈 Visualiser", key="quick_viz", use_container_width=True):
            st.session_state['suggested_question'] = "Génère un graphique récapitulatif"
            st.rerun()
    
    with col4:
        if st.button("📥 Exporter Excel", key="quick_export", use_container_width=True):
            st.session_state['suggested_question'] = "Exporte les données en Excel"
            st.rerun()


def render_domain_suggestions(df: Optional[pd.DataFrame] = None, limit: int = 3):
    """
    Affiche des suggestions spécifiques au domaine détecté.
    """
    if df is None:
        return
    
    suggester = SmartSuggestions(df=df)
    domain_suggestions = suggester.get_domain_suggestions(limit)
    
    if not domain_suggestions:
        return
    
    domain = suggester.detect_domain()
    domain_names = {
        'sales': '🛒 Ventes',
        'hr': '👥 RH',
        'finance': '💰 Finance'
    }
    
    st.markdown(f"### {domain_names.get(domain, '🎯')} Suggestions métier")
    
    cols = st.columns(len(domain_suggestions))
    for i, suggestion in enumerate(domain_suggestions):
        with cols[i]:
            if st.button(
                suggestion['text'],
                key=f"domain_{i}",
                use_container_width=True
            ):
                st.session_state['suggested_question'] = suggestion['text']
                st.rerun()
