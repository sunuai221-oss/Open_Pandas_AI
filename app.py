"""
Open Pandas-AI - Point d'entree principal
Application multi-pages avec architecture refaite.
"""

import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Open Pandas-AI",
    page_icon="OP",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Open Pandas-AI - Analyse de donnees par intelligence artificielle"
    }
)

# Imports des composants et modules
from components.theme_selector import init_theme_system
from components.sidebar import render_sidebar
from components.llm_provider import render_llm_provider_selector

# Initialiser le theme systeme (apres set_page_config)
init_theme_system("light")

# En-tete principal
st.markdown("""
<div style="text-align: center; padding: 40px 0;">
    <h1>Open Pandas-AI</h1>
    <p class="main-subtitle text-lg font-medium">Analysez vos donnees avec la puissance de l'IA</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab"] button,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] p {
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] button,
    .stTabs [data-baseweb="tab"][aria-selected="true"] span,
    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

tab_home, tab_llm = st.tabs(["Accueil", "LLM Provider"])
with tab_llm:
    render_llm_provider_selector()

with tab_home:
    # Verification de la redirection automatique
    if "first_load" not in st.session_state:
        st.session_state["first_load"] = True

    # Contenu principal - Page de bienvenue
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Explorer\n\nExplorez et validez la qualite de vos donnees avec des outils interactifs.")

    with col2:
        st.info("Analyser\n\nPosez vos questions en langage naturel et obtenez des reponses instantanees.")

    with col3:
        st.info("Exporter\n\nExportez vos resultats en Excel avec un formatage professionnel.")

    st.markdown("---")

    # Navigation vers les pages
    st.markdown("""
    <h3 class="section-header text-2xl font-bold">Commencer</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Charger des donnees", use_container_width=True, type="primary"):
            st.switch_page("pages/1_??_Home.py")

        if st.button("Explorer les donnees", use_container_width=True):
            st.switch_page("pages/2_??_Data_Explorer.py")

    with col2:
        if st.button("Commencer l'analyse IA", use_container_width=True, type="primary"):
            st.switch_page("pages/3_??_Agent.py")

        if st.button("Voir l'historique", use_container_width=True):
            st.switch_page("pages/4_??_History.py")

    st.markdown("---")

    # Competences de l'agent
    st.markdown("""
    <h3 class="section-header text-2xl font-bold">Ce que l'agent peut faire</h3>
    """, unsafe_allow_html=True)

    skills = [
        ("Tableaux croises dynamiques", "Creer des pivot tables en un clic"),
        ("Visualisations", "Generer des graphiques automatiquement"),
        ("Fusion de fichiers", "Combiner plusieurs fichiers Excel/CSV"),
        ("Export Excel", "Exporter les resultats avec formatage"),
        ("Detection d'anomalies", "Identifier les valeurs aberrantes"),
        ("Statistiques", "Calculs avances (moyenne, mediane, correlations...)"),
    ]

    cols = st.columns(3)
    for i, (title, desc) in enumerate(skills):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card" style="padding: 15px; text-align: center;">
                <div style="font-weight: 600; margin-bottom: 4px;">{title}</div>
                <div class="skill-description text-sm text-slate-600">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer-text text-center py-5 text-slate-600">
        <p>Open Pandas-AI - Version 2.0</p>
        <p style="font-size: 12px;">Powered by Codestral (Mistral AI) / Pandas / Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar avec infos
st.sidebar.markdown("## Open Pandas-AI")
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="sidebar-content text-slate-900">
<h3 class="sidebar-header text-lg font-bold">Guide rapide</h3>

<p class="sidebar-text text-slate-700">
1. <strong>Chargez</strong> un fichier CSV ou Excel<br>
2. <strong>Explorez</strong> vos donnees<br>
3. <strong>Posez</strong> vos questions a l'IA<br>
4. <strong>Exportez</strong> les resultats
</p>

<hr>

<h3 class="sidebar-header text-lg font-bold">Navigation</h3>

<ul class="sidebar-list text-slate-700">
<li>Home - Dashboard</li>
<li>Explorer - Qualite des donnees</li>
<li>Agent - Questions IA</li>
<li>History - Historique</li>
<li>Settings - Parametres</li>
</ul>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Parametres", use_container_width=True):
    st.switch_page("pages/5_??_Settings.py")
