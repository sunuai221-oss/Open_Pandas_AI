"""
Dashboard Components - Composants réutilisables pour afficher les analyses en format dashboard
Inspiré par les templates Keen IO Dashboards
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional


def render_dashboard_header(title: str, subtitle: str = "", icon: str = "📊"):
    """
    Rend l'en-tête du dashboard.
    
    Args:
        title: Titre principal
        subtitle: Sous-titre (optionnel)
        icon: Emoji pour le titre
    """
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"# {icon}")
    with col2:
        st.markdown(f"# {title}")
        if subtitle:
            st.markdown(f"*{subtitle}*")
    st.divider()


def render_metric_card(label: str, value: Any, delta: Optional[str] = None, color: str = "blue"):
    """
    Rend une card de métrique (KPI).
    
    Args:
        label: Label de la métrique
        value: Valeur à afficher
        delta: Changement optionnel (+5%, -2.3%, etc.)
        color: Couleur (blue, green, red, orange)
    """
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.metric(label, value)
        
        if delta:
            with col2:
                st.caption(delta)


def render_stats_grid(stats: Dict[str, Any], columns: int = 3):
    """
    Rend une grille de statistiques (KPIs).
    
    Args:
        stats: Dict {label: value, ...}
        columns: Nombre de colonnes
    """
    cols = st.columns(columns)
    
    for i, (label, value) in enumerate(stats.items()):
        with cols[i % columns]:
            st.metric(label, value)


def render_result_card(
    title: str,
    result: Any,
    question: str = "",
    timestamp: str = "",
    show_code: bool = False,
    code: str = ""
):
    """
    Rend une card de résultat d'analyse.
    
    Args:
        title: Titre de la card
        result: Résultat (DataFrame, nombre, texte)
        question: Question originale
        timestamp: Timestamp de l'exécution
        show_code: Afficher le code?
        code: Code exécuté
    """
    with st.container():
        # En-tête
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {title}")
        with col2:
            if timestamp:
                st.caption(f"🕐 {timestamp}")
        
        # Contenu
        if isinstance(result, pd.DataFrame):
            st.dataframe(result, use_container_width=True)
            st.caption(f"📊 {len(result)} lignes × {len(result.columns)} colonnes")
        else:
            st.write(result)
        
        # Métadonnées
        if question:
            st.caption(f"❓ {question}")
        
        # Code (optionnel)
        if show_code and code:
            with st.expander("🔧 Code exécuté"):
                st.code(code, language="python")


def render_dashboard_grid(
    exchanges: List[Dict[str, Any]],
    columns: int = 2,
    show_code: bool = False
):
    """
    Rend un grid de résultats d'analyse.
    
    Args:
        exchanges: Liste des échanges {question, result, code, timestamp}
        columns: Nombre de colonnes
        show_code: Afficher les codes?
    """
    if not exchanges:
        st.info("📭 Aucune analyse pour le moment. Commencez par poser une question!")
        return
    
    cols = st.columns(columns)
    
    for i, exchange in enumerate(exchanges):
        with cols[i % columns]:
            render_result_card(
                title=f"Analyse #{len(exchanges) - i}",
                result=exchange.get('result'),
                question=exchange.get('question', ''),
                timestamp=exchange.get('timestamp', ''),
                show_code=show_code,
                code=exchange.get('code', '')
            )


def render_timeline(exchanges: List[Dict[str, Any]]):
    """
    Rend une timeline des analyses.
    
    Args:
        exchanges: Liste des échanges
    """
    if not exchanges:
        st.info("📭 Aucune analyse pour le moment.")
        return
    
    st.markdown("### 📍 Timeline des analyses")
    
    for i, exchange in enumerate(reversed(exchanges)):
        # Container pour chaque item
        with st.container():
            col1, col2 = st.columns([1, 10])
            
            with col1:
                st.markdown(f"**#{len(exchanges) - i}**")
            
            with col2:
                # Question
                st.markdown(f"**❓ {exchange.get('question', 'Sans titre')[:70]}...**")
                
                # Timestamp
                if exchange.get('timestamp'):
                    st.caption(f"🕐 {exchange['timestamp']}")
                
                # Résumé du résultat
                result = exchange.get('result')
                if isinstance(result, pd.DataFrame):
                    st.caption(f"📊 {len(result)} lignes")
                elif isinstance(result, str):
                    st.caption(result[:100])
                else:
                    st.caption(str(result)[:100])
        
        st.divider()


def render_dashboard_summary(exchanges: List[Dict[str, Any]]):
    """
    Rend un résumé du dashboard.
    
    Args:
        exchanges: Liste des échanges
    """
    if not exchanges:
        return
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total analyses", len(exchanges))
    
    with col2:
        successful = sum(1 for e in exchanges if e.get('result') and not str(e.get('result')).startswith('Erreur'))
        st.metric("✅ Réussies", successful)
    
    with col3:
        failed = sum(1 for e in exchanges if str(e.get('result', '')).startswith('Erreur'))
        st.metric("❌ Échouées", failed)


def render_hero_section(
    title: str,
    subtitle: str,
    cta_button: str = "",
    cta_callback=None
):
    """
    Rend une section hero (grand en-tête avec appel à l'action).
    
    Args:
        title: Titre principal
        subtitle: Sous-titre
        cta_button: Texte du bouton (optionnel)
        cta_callback: Callback du bouton
    """
    with st.container():
        st.markdown(f"<h1 style='text-align: center; color: #E8A17A;'>{title}</h1>", 
                   unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #666;'>{subtitle}</h3>", 
                   unsafe_allow_html=True)
        
        if cta_button:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button(cta_button, use_container_width=True, type="primary"):
                    if cta_callback:
                        cta_callback()
        
        st.divider()


def render_insight_box(title: str, content: str, icon: str = "💡"):
    """
    Rend une boîte d'insight/conseil.
    
    Args:
        title: Titre de l'insight
        content: Contenu
        icon: Emoji
    """
    with st.container():
        st.markdown(f"### {icon} {title}")
        st.markdown(f"> {content}")


def render_comparison_table(
    data: Dict[str, List[Any]],
    title: str = "Comparaison"
):
    """
    Rend un tableau de comparaison.
    
    Args:
        data: Dict {colonne: [valeurs]}
        title: Titre
    """
    st.markdown(f"### {title}")
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def render_empty_state(title: str, description: str, icon: str = "📭"):
    """
    Rend un état vide.
    
    Args:
        title: Titre
        description: Description
        icon: Emoji
    """
    st.markdown(f"""
    <div style='text-align: center; padding: 40px;'>
        <div style='font-size: 48px;'>{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)
