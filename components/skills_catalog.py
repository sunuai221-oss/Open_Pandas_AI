"""
Catalogue des compétences IA pour Open Pandas-AI.
"""

import streamlit as st
from typing import List, Dict, Optional


SKILLS = [
    {
        'id': 'pivot',
        'name': 'Pivot Tables',
        'icon': '📊',
        'description': 'Créer des tableaux croisés dynamiques',
        'keywords': ['pivot', 'croisé', 'crosstab', 'résumer', 'agrégation'],
        'example': 'Crée un pivot des ventes par région et produit',
        'category': 'analysis'
    },
    {
        'id': 'viz',
        'name': 'Visualisations',
        'icon': '📈',
        'description': 'Générer des graphiques automatiquement',
        'keywords': ['graphique', 'chart', 'visualiser', 'plot', 'courbe', 'histogramme'],
        'example': 'Génère un graphique des ventes mensuelles',
        'category': 'visualization'
    },
    {
        'id': 'merge',
        'name': 'Fusion de fichiers',
        'icon': '🔗',
        'description': 'Combiner plusieurs fichiers Excel/CSV',
        'keywords': ['fusionner', 'combiner', 'merge', 'join', 'concat'],
        'example': 'Fusionne les données Q1 et Q2',
        'category': 'data'
    },
    {
        'id': 'export',
        'name': 'Export Excel',
        'icon': '📥',
        'description': 'Exporter les résultats formatés',
        'keywords': ['export', 'excel', 'télécharger', 'xlsx', 'sauvegarder'],
        'example': 'Exporte ce résultat en Excel formaté',
        'category': 'export'
    },
    {
        'id': 'anomaly',
        'name': 'Détection d\'anomalies',
        'icon': '🔍',
        'description': 'Identifier les valeurs aberrantes',
        'keywords': ['anomalie', 'outlier', 'aberrant', 'atypique', 'suspect'],
        'example': 'Détecte les anomalies dans les ventes',
        'category': 'analysis'
    },
    {
        'id': 'stats',
        'name': 'Statistiques',
        'icon': '🧮',
        'description': 'Calculs statistiques avancés',
        'keywords': ['moyenne', 'médiane', 'écart-type', 'corrélation', 'distribution'],
        'example': 'Calcule les statistiques descriptives complètes',
        'category': 'analysis'
    },
    {
        'id': 'filter',
        'name': 'Filtrage avancé',
        'icon': '🎯',
        'description': 'Filtrer et sélectionner des données',
        'keywords': ['filtrer', 'sélectionner', 'where', 'condition', 'critère'],
        'example': 'Filtre les ventes supérieures à 1000€',
        'category': 'data'
    },
    {
        'id': 'groupby',
        'name': 'Agrégation',
        'icon': '📦',
        'description': 'Grouper et agréger des données',
        'keywords': ['grouper', 'agréger', 'group by', 'somme', 'total'],
        'example': 'Total des ventes par catégorie',
        'category': 'analysis'
    },
]


def render_skills_sidebar():
    """
    Affiche le catalogue de skills dans la sidebar.
    """
    st.sidebar.markdown("### 🛠️ Compétences IA")
    
    with st.sidebar.expander("Voir les compétences", expanded=False):
        for skill in SKILLS:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{skill['icon']} {skill['name']}**")
                st.caption(skill['description'])
            with col2:
                if st.button("➜", key=f"try_skill_{skill['id']}", help=f"Essayer: {skill['example']}"):
                    st.session_state['suggested_question'] = skill['example']
                    st.rerun()


def render_skills_grid():
    """
    Affiche les skills dans une grille (pour la page principale).
    """
    st.markdown("### 🛠️ Compétences de l'agent")
    
    # Grouper par catégorie
    categories = {}
    for skill in SKILLS:
        cat = skill.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)
    
    category_names = {
        'analysis': '📊 Analyse',
        'visualization': '📈 Visualisation',
        'data': '📁 Données',
        'export': '📥 Export',
        'other': '🔧 Autres'
    }
    
    for cat, skills in categories.items():
        st.markdown(f"#### {category_names.get(cat, cat)}")
        
        cols = st.columns(len(skills))
        for i, skill in enumerate(skills):
            with cols[i]:
                with st.container():
                    st.markdown(f"**{skill['icon']} {skill['name']}**")
                    st.caption(skill['description'])
                    if st.button("Essayer", key=f"grid_skill_{skill['id']}", use_container_width=True):
                        st.session_state['suggested_question'] = skill['example']
                        st.rerun()


def render_skill_cards(limit: int = 4):
    """
    Affiche des cartes de skills horizontalement.
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
            
            if st.button("Essayer", key=f"card_skill_{skill['id']}", use_container_width=True):
                st.session_state['suggested_question'] = skill['example']


def detect_skill_from_question(question: str) -> List[Dict]:
    """
    Détecte les skills pertinents pour une question donnée.
    
    Args:
        question: La question de l'utilisateur
        
    Returns:
        Liste des skills détectés
    """
    question_lower = question.lower()
    detected = []
    
    for skill in SKILLS:
        if any(kw in question_lower for kw in skill['keywords']):
            detected.append(skill)
    
    return detected


def get_skill_by_id(skill_id: str) -> Optional[Dict]:
    """
    Récupère un skill par son ID.
    """
    for skill in SKILLS:
        if skill['id'] == skill_id:
            return skill
    return None


def get_skills_for_prompt() -> str:
    """
    Retourne une description des skills pour enrichir le prompt.
    """
    lines = ["Compétences disponibles:"]
    for skill in SKILLS:
        lines.append(f"- {skill['name']}: {skill['description']}")
    return "\n".join(lines)
