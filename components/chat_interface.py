"""
Interface de chat améliorée pour Open Pandas-AI.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from core.session_manager import get_session_manager

def render_chat_message(
    role: str,
    content: str,
    timestamp: Optional[str] = None,
    result: Any = None,
    code: Optional[str] = None,
    show_code: bool = False,
    actions: Optional[Dict[str, Callable]] = None,
    key_prefix: str = "msg"
):
    """
    Affiche un message de chat stylisé.
    
    Args:
        role: 'user' ou 'assistant'
        content: Contenu du message
        timestamp: Horodatage optionnel
        result: Résultat de l'exécution (DataFrame, etc.)
        code: Code généré (pour l'assistant)
        show_code: Afficher le code généré
        actions: Dict d'actions {label: callback}
        key_prefix: Préfixe pour les clés Streamlit
    """
    
    is_user = role == 'user'
    
    # Container avec style
    with st.container():
        # En-tête du message
        col1, col2 = st.columns([1, 10])
        
        with col1:
            if is_user:
                st.markdown("### 👤")
            else:
                st.markdown("### 🤖")
        
        with col2:
            # Nom et timestamp
            name = "Vous" if is_user else "Assistant IA"
            time_str = f" • {timestamp}" if timestamp else ""
            st.markdown(f"**{name}**{time_str}")
            
            # Contenu du message
            if is_user:
                st.markdown(f"> {content}")
            else:
                st.markdown(content)
        
        # Résultat (pour l'assistant)
        if result is not None and not is_user:
            _render_result_in_chat(result, key_prefix)
        
        # Code généré
        if code and show_code and not is_user:
            with st.expander("🔧 Code généré", expanded=False):
                st.code(code, language="python")
        
        # Actions
        if actions and not is_user:
            cols = st.columns(len(actions))
            for i, (label, callback) in enumerate(actions.items()):
                with cols[i]:
                    if st.button(label, key=f"{key_prefix}_action_{i}", use_container_width=True):
                        callback()
        
        st.markdown("---")


def _render_result_in_chat(result: Any, key_prefix: str):
    """Affiche le resultat dans le contexte du chat."""
    
    if isinstance(result, pd.DataFrame):
        if not result.empty:
            session = get_session_manager()
            max_rows = session.display_max_rows
            display_df = result if max_rows == "Toutes" else result.head(int(max_rows))
            st.dataframe(display_df, use_container_width=True, height=300)
            st.caption(f"Affichage: {len(display_df)} / {len(result)} lignes - {len(result.columns)} colonnes")
    elif isinstance(result, (int, float)):
        st.metric("Resultat", f"{result:,.2f}" if isinstance(result, float) else f"{result:,}")
    elif isinstance(result, str):
        st.info(result)
    elif isinstance(result, (list, tuple)):
        st.write(result)
    else:
        st.write(result)


def render_chat_input(
    placeholder: str = "Posez votre question...",
    key: str = "chat_input",
    suggested_question: Optional[str] = None
) -> Optional[str]:
    """
    Affiche la zone de saisie du chat.
    
    Args:
        placeholder: Texte placeholder
        key: Clé Streamlit
        suggested_question: Question pré-remplie (depuis suggestions)
    
    Returns:
        La question saisie ou None
    """
    
    # Vérifier si une suggestion est en attente
    if 'suggested_question' in st.session_state and st.session_state['suggested_question']:
        suggested = st.session_state['suggested_question']
        st.session_state['suggested_question'] = None  # Consommer la suggestion
        return suggested
    
    # Zone de saisie avec formulaire
    with st.form(key=f"{key}_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            question = st.text_input(
                "Question",
                placeholder=placeholder,
                key=f"{key}_input",
                label_visibility="collapsed"
            )
        
        with col2:
            submit = st.form_submit_button("➤", use_container_width=True)
        
        if submit and question:
            return question
    
    return None


def render_chat_history(
    exchanges: list,
    show_code: bool = False,
    limit: int = 10
):
    """
    Affiche l'historique du chat.
    
    Args:
        exchanges: Liste des échanges
        show_code: Afficher le code généré
        limit: Nombre maximum d'échanges à afficher
    """
    
    if not exchanges:
        st.info("💭 Aucun échange pour le moment. Posez une question pour commencer.")
        return
    
    # Afficher les derniers échanges (du plus récent au plus ancien)
    for i, exchange in enumerate(reversed(exchanges[-limit:])):
        question = exchange.get('question', '')
        result = exchange.get('result')
        code = exchange.get('code', '')
        auto_comment = exchange.get('auto_comment', '')
        timestamp = exchange.get('timestamp', '')
        
        # Message utilisateur
        render_chat_message(
            role='user',
            content=question,
            timestamp=timestamp,
            key_prefix=f"hist_user_{i}"
        )
        
        # Message assistant
        render_chat_message(
            role='assistant',
            content=auto_comment if auto_comment else "Voici le résultat:",
            result=result,
            code=code,
            show_code=show_code,
            key_prefix=f"hist_asst_{i}"
        )


def render_typing_indicator():
    """Affiche un indicateur de frappe/chargement."""
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 5px;">
        <span>🤖 L'assistant réfléchit</span>
        <div class="typing-dots">
            <span>.</span><span>.</span><span>.</span>
        </div>
    </div>
    <style>
    .typing-dots span {
        animation: blink 1.4s infinite;
        animation-fill-mode: both;
    }
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes blink {
        0% { opacity: 0.2; }
        20% { opacity: 1; }
        100% { opacity: 0.2; }
    }
    </style>
    """, unsafe_allow_html=True)


def render_processing_status(status: str, progress: float = None):
    """
    Affiche le statut de traitement.
    
    Args:
        status: Message de statut
        progress: Progression (0-1) ou None pour indéterminé
    """
    
    if progress is not None:
        st.progress(progress)
    
    st.markdown(f"⏳ {status}")
