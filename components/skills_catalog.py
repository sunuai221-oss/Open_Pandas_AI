"""
AI skills catalog for Open Pandas-AI.
"""

import streamlit as st
from typing import List, Dict, Optional


SKILLS = [
    {
        'id': 'pivot',
        'name': 'Pivot Tables',
        'icon': '📊',
        'description': 'Create pivot tables',
        'keywords': ['pivot', 'croisé', 'crosstab', 'résumer', 'agrégation'],
        'example': 'Create a pivot of sales by region and product',
        'category': 'analysis'
    },
    {
        'id': 'viz',
        'name': 'Visualizations',
        'icon': '📈',
        'description': 'Generate charts automatically',
        'keywords': ['graphique', 'chart', 'visualiser', 'plot', 'courbe', 'histogramme'],
        'example': 'Generate a chart of monthly sales',
        'category': 'visualization'
    },
    {
        'id': 'merge',
        'name': 'File Merging',
        'icon': '🔗',
        'description': 'Combine multiple Excel/CSV files',
        'keywords': ['fusionner', 'combiner', 'merge', 'join', 'concat'],
        'example': 'Merge Q1 and Q2 data',
        'category': 'data'
    },
    {
        'id': 'export',
        'name': 'Excel Export',
        'icon': '📥',
        'description': 'Export formatted results',
        'keywords': ['export', 'excel', 'télécharger', 'xlsx', 'sauvegarder'],
        'example': 'Export this result to formatted Excel',
        'category': 'export'
    },
    {
        'id': 'anomaly',
        'name': 'Anomaly Detection',
        'icon': '🔍',
        'description': 'Identify outliers',
        'keywords': ['anomalie', 'outlier', 'aberrant', 'atypique', 'suspect'],
        'example': 'Detect anomalies in sales',
        'category': 'analysis'
    },
    {
        'id': 'stats',
        'name': 'Statistics',
        'icon': '🧮',
        'description': 'Advanced statistical calculations',
        'keywords': ['moyenne', 'médiane', 'écart-type', 'corrélation', 'distribution'],
        'example': 'Calculate complete descriptive statistics',
        'category': 'analysis'
    },
    {
        'id': 'filter',
        'name': 'Advanced Filtering',
        'icon': '🎯',
        'description': 'Filter and select data',
        'keywords': ['filtrer', 'sélectionner', 'where', 'condition', 'critère'],
        'example': 'Filter sales above 1000€',
        'category': 'data'
    },
    {
        'id': 'groupby',
        'name': 'Aggregation',
        'icon': '📦',
        'description': 'Group and aggregate data',
        'keywords': ['grouper', 'agréger', 'group by', 'somme', 'total'],
        'example': 'Total sales by category',
        'category': 'analysis'
    },
]


def render_skills_sidebar():
    """
    Displays skills catalog in the sidebar.
    """
    st.sidebar.markdown("### 🛠️ AI Skills")
    
    with st.sidebar.expander("View Skills", expanded=False):
        for skill in SKILLS:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{skill['icon']} {skill['name']}**")
                st.caption(skill['description'])
            with col2:
                if st.button("➜", key=f"try_skill_{skill['id']}", help=f"Try: {skill['example']}"):
                    st.session_state['suggested_question'] = skill['example']
                    st.rerun()


def render_skills_grid():
    """
    Displays skills in a grid (for main page).
    """
    st.markdown("### 🛠️ Agent Capabilities")
    
    # Group by category
    categories = {}
    for skill in SKILLS:
        cat = skill.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)
    
    category_names = {
        'analysis': '📊 Analysis',
        'visualization': '📈 Visualization',
        'data': '📁 Data',
        'export': '📥 Export',
        'other': '🔧 Other'
    }
    
    for cat, skills in categories.items():
        st.markdown(f"#### {category_names.get(cat, cat)}")
        
        cols = st.columns(len(skills))
        for i, skill in enumerate(skills):
            with cols[i]:
                with st.container():
                    st.markdown(f"**{skill['icon']} {skill['name']}**")
                    st.caption(skill['description'])
                    if st.button("Try", key=f"grid_skill_{skill['id']}", use_container_width=True):
                        st.session_state['suggested_question'] = skill['example']
                        st.rerun()


def render_skill_cards(limit: int = 4):
    """
    Displays skill cards horizontally.
    """
    cols = st.columns(limit)
    
    for i, skill in enumerate(SKILLS[:limit]):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background: rgba(100, 100, 100, 0.1);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                height: 120px;
            ">
                <div style="font-size: 24px;">{skill['icon']}</div>
                <div style="font-weight: bold; margin: 5px 0;">{skill['name']}</div>
                <div style="font-size: 12px; color: var(--text-secondary);">{skill['description']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Try", key=f"card_skill_{skill['id']}", use_container_width=True):
                st.session_state['suggested_question'] = skill['example']


def detect_skill_from_question(question: str) -> List[Dict]:
    """
    Detects relevant skills for a given question.
    
    Args:
        question: User's question
        
    Returns:
        List of detected skills
    """
    question_lower = question.lower()
    detected = []
    
    for skill in SKILLS:
        if any(kw in question_lower for kw in skill['keywords']):
            detected.append(skill)
    
    return detected


def get_skill_by_id(skill_id: str) -> Optional[Dict]:
    """
    Retrieves a skill by its ID.
    """
    for skill in SKILLS:
        if skill['id'] == skill_id:
            return skill
    return None


def get_skills_for_prompt() -> str:
    """
    Returns a description of skills to enrich the prompt.
    """
    lines = ["Available capabilities:"]
    for skill in SKILLS:
        lines.append(f"- {skill['name']}: {skill['description']}")
    return "\n".join(lines)
