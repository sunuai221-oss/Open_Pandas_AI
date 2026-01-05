"""
User feedback components for Open Pandas-AI.
Loading indicators, messages, tooltips and onboarding.
"""

import streamlit as st
from typing import Optional, List, Callable
import time


def show_loading(message: str = "Loading..."):
    """
    Displays a styled loading indicator.
    
    Args:
        message: Message to display
    """
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 15px;
        background: rgba(233, 69, 96, 0.1);
        border-radius: 10px;
        border-left: 4px solid #e94560;
    ">
        <div style="
            width: 24px;
            height: 24px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #e94560;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
        <span>{message}</span>
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)


def show_success(message: str, icon: str = "✅"):
    """
    Displays a styled success message.
    
    Args:
        message: Success message
        icon: Icon to display
    """
    st.markdown(f"""
    <div style="
        padding: 15px 20px;
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(32, 201, 151, 0.1) 100%);
        border-radius: 10px;
        border-left: 4px solid #28a745;
        color: #28a745;
        font-weight: 500;
    ">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)


def show_error(message: str, icon: str = "❌"):
    """
    Displays a styled error message.
    
    Args:
        message: Error message
        icon: Icon to display
    """
    st.markdown(f"""
    <div style="
        padding: 15px 20px;
        background: rgba(220, 53, 69, 0.1);
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        color: #dc3545;
        font-weight: 500;
    ">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)


def show_warning(message: str, icon: str = "⚠️"):
    """
    Displays a styled warning message.
    
    Args:
        message: Warning message
        icon: Icon to display
    """
    st.markdown(f"""
    <div style="
        padding: 15px 20px;
        background: rgba(255, 193, 7, 0.1);
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        color: #f5a623;
        font-weight: 500;
    ">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)


def show_info(message: str, icon: str = "ℹ️"):
    """
    Displays a styled info message.
    
    Args:
        message: Info message
        icon: Icon to display
    """
    st.markdown(f"""
    <div style="
        padding: 15px 20px;
        background: rgba(23, 162, 184, 0.1);
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        color: #17a2b8;
        font-weight: 500;
    ">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)


def show_tooltip(text: str, help_text: str):
    """
    Displays text with tooltip.
    
    Args:
        text: Main text
        help_text: Help text on hover
    """
    st.markdown(f"""
    <span title="{help_text}" style="
        cursor: help;
        border-bottom: 1px dotted var(--text-secondary);
    ">{text}</span>
    """, unsafe_allow_html=True)


def render_progress_steps(
    steps: List[str],
    current_step: int,
    completed_steps: Optional[List[int]] = None
):
    """
    Displays a progress bar with steps.
    
    Args:
        steps: List of step names
        current_step: Index of current step (0-based)
        completed_steps: List of completed step indices
    """
    if completed_steps is None:
        completed_steps = list(range(current_step))
    
    html = '<div style="display: flex; justify-content: space-between; margin: 20px 0;">'
    
    for i, step in enumerate(steps):
        if i in completed_steps:
            status = "completed"
            color = "#28a745"
            icon = "✓"
        elif i == current_step:
            status = "current"
            color = "#e94560"
            icon = str(i + 1)
        else:
            status = "pending"
            color = "#6c757d"
            icon = str(i + 1)
        
        html += f"""
        <div style="text-align: center; flex: 1;">
            <div style="
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: {color};
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 8px;
                font-weight: bold;
            ">{icon}</div>
            <div style="font-size: 12px; color: {color};">{step}</div>
        </div>
        """
        
        if i < len(steps) - 1:
            line_color = "#28a745" if i in completed_steps else "#e0e0e0"
            html += f"""
            <div style="
                flex: 1;
                height: 2px;
                background: {line_color};
                align-self: center;
                margin-top: -20px;
            "></div>
            """
    
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_onboarding():
    """
    Displays onboarding guide for new users.
    """
    if st.session_state.get('onboarding_completed', False):
        return
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        border: 1px solid rgba(233, 69, 96, 0.3);
    ">
        <h2 style="color: #e94560; margin-bottom: 20px;">👋 Welcome to Open Pandas-AI!</h2>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">
            Analyze your data in natural language using artificial intelligence.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Steps
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 15px;">
            <div style="font-size: 2rem;">📂</div>
            <h4>1. Load</h4>
            <p style="font-size: 12px; color: var(--text-secondary);">Upload a CSV or Excel file</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 15px;">
            <div style="font-size: 2rem;">🔍</div>
            <h4>2. Explore</h4>
            <p style="font-size: 12px; color: var(--text-secondary);">Check your data quality</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 15px;">
            <div style="font-size: 2rem;">💬</div>
            <h4>3. Question</h4>
            <p style="font-size: 12px; color: var(--text-secondary);">Ask your questions in natural language</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 15px;">
            <div style="font-size: 2rem;">📥</div>
            <h4>4. Export</h4>
            <p style="font-size: 12px; color: var(--text-secondary);">Download results to Excel</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("✓ Got it, let's start", key="onboarding_dismiss", type="primary"):
        st.session_state['onboarding_completed'] = True
        st.rerun()


def render_empty_state(
    title: str,
    message: str,
    icon: str = "📭",
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None
):
    """
    Displays empty state with message and optional action.
    
    Args:
        title: Title
        message: Explanatory message
        icon: Icon
        action_label: Action button label
        action_callback: Button callback
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 60px 20px;
        background: rgba(100, 100, 100, 0.05);
        border-radius: 15px;
        margin: 30px 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 20px;">{icon}</div>
        <h3 style="margin-bottom: 10px;">{title}</h3>
        <p style="color: var(--text-secondary); max-width: 400px; margin: 0 auto;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if action_label:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, use_container_width=True, type="primary"):
                if action_callback:
                    action_callback()


def render_help_tooltip(key: str):
    """
    Affiche une icône d'aide avec tooltip contextuel.
    
    Args:
        key: Clé du message d'aide
    """
    help_texts = {
        'pivot_table': "Un tableau croisé dynamique permet de résumer et analyser des données en groupant par colonnes.",
        'quality_score': "Le score de qualité mesure la fiabilité de vos données (valeurs manquantes, doublons, etc.)",
        'memory': "La mémoire permet à l'agent de se souvenir du contexte de la conversation.",
        'sandbox': "Le code est exécuté dans un environnement sécurisé isolé pour protéger votre système.",
    }
    
    text = help_texts.get(key, "Aide non disponible")
    st.markdown(f'<span title="{text}" style="cursor: help;">❓</span>', unsafe_allow_html=True)


def show_processing_status(status: str, progress: Optional[float] = None):
    """
    Affiche un statut de traitement avec barre de progression optionnelle.
    
    Args:
        status: Message de statut
        progress: Progression (0-1) ou None pour indéterminé
    """
    if progress is not None:
        st.progress(progress)
    
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        color: var(--text-secondary);
    ">
        <div class="loader" style="
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #e94560;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
        <span>⏳ {status}</span>
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)


def show_keyboard_shortcuts():
    """Affiche les raccourcis clavier disponibles."""
    st.markdown("""
    ### ⌨️ Raccourcis clavier
    
    | Raccourci | Action |
    |-----------|--------|
    | `Ctrl + Enter` | Envoyer la question |
    | `Ctrl + E` | Export rapide |
    | `Ctrl + N` | Nouvelle analyse |
    | `Ctrl + H` | Afficher l'historique |
    """)
