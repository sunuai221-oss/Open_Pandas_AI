"""
Page History - Historique des analyses.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuration
st.set_page_config(
    page_title="Open Pandas-AI - Historique",
    page_icon="📚",
    layout="wide"
)

from components.sidebar import render_minimal_sidebar
from core.session_manager import get_session_manager
from db.session import get_session as get_db_session
from db.models import Question, CodeExecution, UploadedFile, ConsultingMessage

# Session
session = get_session_manager()

# Sidebar
render_minimal_sidebar()

# Header
st.title("📚 Historique des analyses")

# Stats overview
col1, col2, col3, col4 = st.columns(4)

try:
    with get_db_session() as db_session:
        total_questions = db_session.query(Question).count()
        total_executions = db_session.query(CodeExecution).count()
        success_count = db_session.query(CodeExecution).filter_by(status='success').count()
        total_files = db_session.query(UploadedFile).count()
        
        success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0
except Exception:
    total_questions = 0
    total_executions = 0
    success_rate = 0
    total_files = 0

with col1:
    st.metric("📝 Questions totales", total_questions)
with col2:
    st.metric("⚡ Exécutions", total_executions)
with col3:
    st.metric("✅ Taux de succès", f"{success_rate:.0f}%")
with col4:
    st.metric("📁 Fichiers traités", total_files)

st.markdown("---")

# Filters
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input("🔍 Rechercher dans les questions", placeholder="Ex: ventes, pivot, moyenne...")
with col2:
    status_filter = st.selectbox("Statut", ["Tous", "Succès", "Erreur"])
with col3:
    date_filter = st.selectbox("Période", ["Tout", "Aujourd'hui", "7 derniers jours", "30 derniers jours"])

st.markdown("---")

# Load history from database
try:
    with get_db_session() as db_session:
        query = db_session.query(Question).order_by(Question.created_at.desc())
        
        # Apply date filter
        if date_filter == "Aujourd'hui":
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Question.created_at >= today)
        elif date_filter == "7 derniers jours":
            week_ago = datetime.now() - timedelta(days=7)
            query = query.filter(Question.created_at >= week_ago)
        elif date_filter == "30 derniers jours":
            month_ago = datetime.now() - timedelta(days=30)
            query = query.filter(Question.created_at >= month_ago)
        
        # Search filter
        if search_query:
            query = query.filter(Question.question.ilike(f"%{search_query}%"))
        
        questions = query.limit(100).all()
        
        if not questions:
            st.info("📭 Aucune question trouvée avec ces critères.")
        else:
            st.markdown(f"### 📋 {len(questions)} résultat(s)")
            
            for i, q in enumerate(questions):
                # Get execution info
                execution = db_session.query(CodeExecution).filter_by(question_id=q.id).first()
                consulting = db_session.query(ConsultingMessage).filter_by(question_id=q.id).first()
                
                # Apply status filter
                if execution:
                    if status_filter == "Succès" and execution.status != 'success':
                        continue
                    elif status_filter == "Erreur" and execution.status == 'success':
                        continue
                
                # Display question
                with st.expander(
                    f"{'✅' if execution and execution.status == 'success' else '❌'} {q.question[:80]}{'...' if len(q.question) > 80 else ''}",
                    expanded=False
                ):
                    # Metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"📅 {q.created_at.strftime('%d/%m/%Y %H:%M') if q.created_at else 'N/A'}")
                    with col2:
                        if execution:
                            st.caption(f"⚡ {execution.status}")
                    with col3:
                        if execution:
                            st.caption(f"🤖 {execution.model_used or 'Codestral'}")
                    
                    # Full question
                    st.markdown("**Question:**")
                    st.markdown(f"> {q.question}")
                    
                    # Code
                    if execution and execution.code:
                        st.markdown("**Code généré:**")
                        st.code(execution.code, language="python")
                    
                    # Result preview
                    if execution and execution.result:
                        st.markdown("**Résultat:**")
                        st.text(execution.result[:500] + "..." if len(execution.result) > 500 else execution.result)
                    
                    # Consulting comment
                    if consulting:
                        st.markdown("**Analyse:**")
                        st.info(consulting.message[:300] + "..." if len(consulting.message) > 300 else consulting.message)
                    
                    # Actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Ré-exécuter", key=f"rerun_{q.id}"):
                            st.session_state['suggested_question'] = q.question
                            st.switch_page("pages/3_🤖_Agent.py")
                    with col2:
                        if st.button("📋 Copier la question", key=f"copy_{q.id}"):
                            st.code(q.question)
                    
                    st.markdown("---")

except Exception as e:
    st.error(f"Erreur lors du chargement de l'historique: {e}")

# Session history (in-memory)
st.markdown("---")
st.markdown("### 💬 Échanges de cette session")

exchanges = session.exchanges
if exchanges:
    for i, exchange in enumerate(reversed(exchanges[-10:])):
        with st.expander(f"🗣️ {exchange.get('question', 'N/A')[:60]}...", expanded=False):
            st.caption(f"⏰ {exchange.get('timestamp', 'N/A')}")
            
            if exchange.get('code'):
                st.code(exchange['code'], language="python")
            
            result = exchange.get('result')
            if isinstance(result, pd.DataFrame):
                st.dataframe(result.head(10), use_container_width=True)
            elif result:
                st.write(result)
            
            if exchange.get('auto_comment'):
                st.info(exchange['auto_comment'])
else:
    st.info("Aucun échange dans cette session.")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Accueil", use_container_width=True):
        st.switch_page("pages/1_🏠_Home.py")
with col2:
    if st.button("🤖 Agent IA", use_container_width=True, type="primary"):
        st.switch_page("pages/3_🤖_Agent.py")
