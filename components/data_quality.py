"""
Composant de validation et qualité des données.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List
from core.data_validator import DataValidator


def render_quality_panel(df: pd.DataFrame, expanded: bool = False):
    """
    Affiche le panneau complet de qualité des données.
    
    Args:
        df: DataFrame à valider
        expanded: Si True, les détails sont affichés par défaut
    """
    if df is None or df.empty:
        st.info("Chargez des données pour voir le rapport de qualité")
        return
    
    # Validation
    validator = DataValidator(df)
    result = validator.validate_all()
    
    quality_score = result.get('quality_score', 100)
    issues = result.get('issues', [])
    summary = result.get('summary', {})
    recommendations = result.get('recommendations', [])
    
    # En-tête avec score
    _render_quality_header(quality_score, summary)
    
    # Issues par niveau
    if issues:
        _render_issues_list(issues, expanded)
    
    # Recommandations
    if recommendations:
        _render_recommendations(recommendations)
    
    # Rapport détaillé
    with st.expander("📊 Rapport technique complet", expanded=False):
        st.json(result)
    
    return result


def _render_quality_header(score: float, summary: Dict):
    """Affiche l'en-tête avec le score de qualité."""
    
    # Déterminer la couleur et le statut
    if score >= 80:
        color = "green"
        status = "Excellente"
        icon = "✅"
    elif score >= 60:
        color = "orange"
        status = "Acceptable"
        icon = "⚠️"
    else:
        color = "red"
        status = "Problématique"
        icon = "❌"
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### 📊 Qualité des données")
        
        # Barre de progression
        st.progress(score / 100)
        st.markdown(f"**{icon} {score:.0f}/100** — {status}")
    
    with col2:
        st.metric("Lignes", f"{summary.get('data_shape', (0,))[0]:,}")
    
    with col3:
        st.metric("Colonnes", f"{summary.get('data_shape', (0, 0))[1]}")
    
    # Résumé des issues
    critical = summary.get('critical_issues', 0)
    warnings = summary.get('warning_issues', 0)
    infos = summary.get('info_issues', 0)
    
    if critical > 0 or warnings > 0:
        cols = st.columns(3)
        with cols[0]:
            if critical > 0:
                st.error(f"🚨 {critical} critique(s)")
        with cols[1]:
            if warnings > 0:
                st.warning(f"⚠️ {warnings} avertissement(s)")
        with cols[2]:
            if infos > 0:
                st.info(f"ℹ️ {infos} info(s)")


def _render_issues_list(issues: List[Dict], expanded: bool):
    """Affiche la liste des problèmes détectés."""
    
    # Grouper par niveau
    critical = [i for i in issues if i.get('level') == 'CRITICAL']
    warnings = [i for i in issues if i.get('level') == 'WARNING']
    infos = [i for i in issues if i.get('level') == 'INFO']
    
    with st.expander(f"🔍 Détail des problèmes ({len(issues)})", expanded=expanded):
        
        # Critiques
        if critical:
            st.markdown("#### 🚨 Problèmes critiques")
            for issue in critical:
                with st.container():
                    st.error(f"**{issue.get('category', 'Inconnu')}**: {issue.get('message', '')}")
                    cols = issue.get('affected_columns', [])
                    if cols:
                        st.caption(f"Colonnes: {', '.join(cols)}")
                    rec = issue.get('recommendation', '')
                    if rec:
                        st.info(f"💡 {rec}")
        
        # Avertissements
        if warnings:
            st.markdown("#### ⚠️ Avertissements")
            for issue in warnings:
                with st.container():
                    st.warning(f"**{issue.get('category', 'Inconnu')}**: {issue.get('message', '')}")
                    rec = issue.get('recommendation', '')
                    if rec:
                        st.caption(f"💡 {rec}")
        
        # Infos
        if infos:
            st.markdown("#### ℹ️ Informations")
            for issue in infos:
                st.info(f"**{issue.get('category', 'Inconnu')}**: {issue.get('message', '')}")


def _render_recommendations(recommendations: List[str]):
    """Affiche les recommandations."""
    
    with st.expander("💡 Recommandations", expanded=False):
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")


def render_quality_badge(score: Optional[float]) -> str:
    """
    Retourne un badge HTML pour le score de qualité.
    """
    if score is None:
        return ""
    
    if score >= 80:
        color = "#28a745"
        text = "Excellente"
    elif score >= 60:
        color = "#ffc107"
        text = "Acceptable"
    else:
        color = "#dc3545"
        text = "À améliorer"
    
    return f"""
    <span style="
        background-color: {color};
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
    ">{score:.0f}/100 - {text}</span>
    """


def render_quality_mini(df: pd.DataFrame):
    """
    Affiche un résumé compact de la qualité.
    """
    if df is None or df.empty:
        return
    
    validator = DataValidator(df)
    result = validator.validate_all()
    score = result.get('quality_score', 100)
    
    if score >= 80:
        st.success(f"✅ Qualité: {score:.0f}/100")
    elif score >= 60:
        st.warning(f"⚠️ Qualité: {score:.0f}/100")
    else:
        st.error(f"❌ Qualité: {score:.0f}/100")


def render_column_quality(df: pd.DataFrame, column: str):
    """
    Affiche la qualité d'une colonne spécifique.
    """
    if column not in df.columns:
        return
    
    col_data = df[column]
    
    # Statistiques de base
    total = len(col_data)
    missing = col_data.isna().sum()
    missing_pct = (missing / total) * 100 if total > 0 else 0
    unique = col_data.nunique()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Valeurs manquantes", f"{missing_pct:.1f}%")
    with col2:
        st.metric("Valeurs uniques", unique)
    with col3:
        st.metric("Type", str(col_data.dtype))
