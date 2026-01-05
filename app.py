"""
Open Pandas-AI - Main entry point
Multi-page application with refactored architecture.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Open Pandas-AI",
    page_icon="OP",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Open Pandas-AI - Data analysis with artificial intelligence"
    }
)

# Component and module imports
from components.theme_selector import init_theme_system
from components.sidebar import render_sidebar
from components.llm_provider import render_llm_provider_selector

# Initialize theme system (after set_page_config)
init_theme_system("light")

# Main header
st.markdown("""
<div style="text-align: center; padding: 40px 0;">
    <h1>Open Pandas-AI</h1>
    <p class="main-subtitle text-lg font-medium">Analyze your data with the power of AI</p>
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

tab_home, tab_llm = st.tabs(["Home", "LLM Provider"])
with tab_llm:
    render_llm_provider_selector()

with tab_home:
    # Automatic redirect verification
    if "first_load" not in st.session_state:
        st.session_state["first_load"] = True

    # Main content - Welcome page
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Explore\n\nExplore and validate your data quality with interactive tools.")

    with col2:
        st.info("Analyze\n\nAsk your questions in natural language and get instant answers.")

    with col3:
        st.info("Export\n\nExport your results to Excel with professional formatting.")

    st.markdown("---")

    # Navigation to pages
    st.markdown("""
    <h3 class="section-header text-2xl font-bold">Get Started</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Load Data", use_container_width=True, type="primary"):
            st.switch_page("pages/1_??_Home.py")

        if st.button("Explore Data", use_container_width=True):
            st.switch_page("pages/2_??_Data_Explorer.py")

    with col2:
        if st.button("Start AI Analysis", use_container_width=True, type="primary"):
            st.switch_page("pages/3_??_Agent.py")

        if st.button("View History", use_container_width=True):
            st.switch_page("pages/4_??_History.py")

    st.markdown("---")

    # Agent capabilities
    st.markdown("""
    <h3 class="section-header text-2xl font-bold">What the agent can do</h3>
    """, unsafe_allow_html=True)

    skills = [
        ("Pivot Tables", "Create pivot tables with one click"),
        ("Visualizations", "Generate charts automatically"),
        ("File Merging", "Combine multiple Excel/CSV files"),
        ("Excel Export", "Export results with formatting"),
        ("Anomaly Detection", "Identify outliers"),
        ("Statistics", "Advanced calculations (mean, median, correlations...)"),
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

# Sidebar with info
st.sidebar.markdown("## Open Pandas-AI")
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="sidebar-content text-slate-900">
<h3 class="sidebar-header text-lg font-bold">Quick Guide</h3>

<p class="sidebar-text text-slate-700">
1. <strong>Load</strong> a CSV or Excel file<br>
2. <strong>Explore</strong> your data<br>
3. <strong>Ask</strong> your questions to the AI<br>
4. <strong>Export</strong> the results
</p>

<hr>

<h3 class="sidebar-header text-lg font-bold">Navigation</h3>

<ul class="sidebar-list text-slate-700">
<li>Home - Dashboard</li>
<li>Explorer - Data Quality</li>
<li>Agent - AI Questions</li>
<li>History - History</li>
<li>Settings - Settings</li>
</ul>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Settings", use_container_width=True):
    st.switch_page("pages/5_??_Settings.py")
