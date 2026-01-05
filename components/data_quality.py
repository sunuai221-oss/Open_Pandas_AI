"""
Data validation and quality component.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List
from core.data_validator import DataValidator


def render_quality_panel(df: pd.DataFrame, expanded: bool = False):
    """
    Displays the complete data quality panel.
    
    Args:
        df: DataFrame to validate
        expanded: If True, details are displayed by default
    """
    if df is None or df.empty:
        st.info("Load data to see the quality report")
        return
    
    # Validation
    validator = DataValidator(df)
    result = validator.validate_all()
    
    quality_score = result.get('quality_score', 100)
    issues = result.get('issues', [])
    summary = result.get('summary', {})
    recommendations = result.get('recommendations', [])
    
    # Header with score
    _render_quality_header(quality_score, summary)
    
    # Issues by level
    if issues:
        _render_issues_list(issues, expanded)
    
    # Recommendations
    if recommendations:
        _render_recommendations(recommendations)
    
    # Detailed report
    with st.expander("📊 Complete Technical Report", expanded=False):
        st.json(result)
    
    return result


def _render_quality_header(score: float, summary: Dict):
    """Displays header with quality score."""
    
    # Determine color and status
    if score >= 80:
        color = "green"
        status = "Excellent"
        icon = "✅"
    elif score >= 60:
        color = "orange"
        status = "Acceptable"
        icon = "⚠️"
    else:
        color = "red"
        status = "Problematic"
        icon = "❌"
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### 📊 Data Quality")
        
        # Progress bar
        st.progress(score / 100)
        st.markdown(f"**{icon} {score:.0f}/100** — {status}")
    
    with col2:
        st.metric("Rows", f"{summary.get('data_shape', (0,))[0]:,}")
    
    with col3:
        st.metric("Columns", f"{summary.get('data_shape', (0, 0))[1]}")
    
    # Issues summary
    critical = summary.get('critical_issues', 0)
    warnings = summary.get('warning_issues', 0)
    infos = summary.get('info_issues', 0)
    
    if critical > 0 or warnings > 0:
        cols = st.columns(3)
        with cols[0]:
            if critical > 0:
                st.error(f"🚨 {critical} critical")
        with cols[1]:
            if warnings > 0:
                st.warning(f"⚠️ {warnings} warning(s)")
        with cols[2]:
            if infos > 0:
                st.info(f"ℹ️ {infos} info(s)")


def _render_issues_list(issues: List[Dict], expanded: bool):
    """Displays the list of detected issues."""
    
    # Group by level
    critical = [i for i in issues if i.get('level') == 'CRITICAL']
    warnings = [i for i in issues if i.get('level') == 'WARNING']
    infos = [i for i in issues if i.get('level') == 'INFO']
    
    with st.expander(f"🔍 Issue Details ({len(issues)})", expanded=expanded):
        
        # Critical
        if critical:
            st.markdown("#### 🚨 Critical Issues")
            for issue in critical:
                with st.container():
                    st.error(f"**{issue.get('category', 'Unknown')}**: {issue.get('message', '')}")
                    cols = issue.get('affected_columns', [])
                    if cols:
                        st.caption(f"Columns: {', '.join(cols)}")
                    rec = issue.get('recommendation', '')
                    if rec:
                        st.info(f"💡 {rec}")
        
        # Warnings
        if warnings:
            st.markdown("#### ⚠️ Warnings")
            for issue in warnings:
                with st.container():
                    st.warning(f"**{issue.get('category', 'Unknown')}**: {issue.get('message', '')}")
                    rec = issue.get('recommendation', '')
                    if rec:
                        st.caption(f"💡 {rec}")
        
        # Infos
        if infos:
            st.markdown("#### ℹ️ Information")
            for issue in infos:
                st.info(f"**{issue.get('category', 'Unknown')}**: {issue.get('message', '')}")


def _render_recommendations(recommendations: List[str]):
    """Displays recommendations."""
    
    with st.expander("💡 Recommendations", expanded=False):
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")


def render_quality_badge(score: Optional[float]) -> str:
    """
    Returns an HTML badge for the quality score.
    """
    if score is None:
        return ""
    
    if score >= 80:
        color = "#28a745"
        text = "Excellent"
    elif score >= 60:
        color = "#ffc107"
        text = "Acceptable"
    else:
        color = "#dc3545"
        text = "Needs Improvement"
    
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
    Displays a compact quality summary.
    """
    if df is None or df.empty:
        return
    
    validator = DataValidator(df)
    result = validator.validate_all()
    score = result.get('quality_score', 100)
    
    if score >= 80:
        st.success(f"✅ Quality: {score:.0f}/100")
    elif score >= 60:
        st.warning(f"⚠️ Quality: {score:.0f}/100")
    else:
        st.error(f"❌ Quality: {score:.0f}/100")


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
