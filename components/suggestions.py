"""
Smart suggestions display component.
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
    Displays suggestions as clickable buttons.
    
    Args:
        df: Current DataFrame
        user_level: User level ('beginner' or 'expert')
        limit: Maximum number of suggestions
        title: Section title
    """
    suggestions = get_suggestions(df=df, user_level=user_level, limit=limit)
    
    if not suggestions:
        return
    
    st.markdown(f"### {title}")
    
    # Display in columns
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
    Displays suggestions as horizontal chips/tags.
    """
    if not suggestions:
        return
    
    # CSS for chips
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
    Displays follow-up suggestions after a response.
    """
    followups = get_followup_suggestions(last_question, last_result, limit)
    
    if not followups:
        return
    
    st.markdown("**💬 Suggested Follow-up Questions:**")
    
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
    Displays quick actions based on data.
    """
    if df is None:
        return
    
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Statistical Summary", key="quick_stats", use_container_width=True):
            st.session_state['suggested_question'] = "Complete statistical summary"
            st.rerun()
    
    with col2:
        if st.button("🔍 Detect Anomalies", key="quick_anomaly", use_container_width=True):
            st.session_state['suggested_question'] = "Detect outliers"
            st.rerun()
    
    with col3:
        if st.button("📈 Visualize", key="quick_viz", use_container_width=True):
            st.session_state['suggested_question'] = "Generate a summary chart"
            st.rerun()
    
    with col4:
        if st.button("📥 Export Excel", key="quick_export", use_container_width=True):
            st.session_state['suggested_question'] = "Export data to Excel"
            st.rerun()


def render_domain_suggestions(df: Optional[pd.DataFrame] = None, limit: int = 3):
    """
    Displays domain-specific suggestions.
    """
    if df is None:
        return
    
    suggester = SmartSuggestions(df=df)
    domain_suggestions = suggester.get_domain_suggestions(limit)
    
    if not domain_suggestions:
        return
    
    domain = suggester.detect_domain()
    domain_names = {
        'sales': '🛒 Sales',
        'hr': '👥 HR',
        'finance': '💰 Finance'
    }
    
    st.markdown(f"### {domain_names.get(domain, '🎯')} Business Suggestions")
    
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
