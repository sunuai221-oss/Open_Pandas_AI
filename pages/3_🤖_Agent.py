"""
Page Agent - Interface de conversation IA principale.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="Open Pandas-AI - Agent IA",
    page_icon="🤖",
    layout="wide"
)

from components.sidebar import render_sidebar
from components.memory_viewer import render_memory_context_banner, render_memory_panel
from components.suggestions import render_followup_suggestions
from components.chat_interface import render_chat_message, render_chat_input, render_chat_history
from components.result_display import render_result
from components.skills_catalog import detect_skill_from_question
from core.session_manager import get_session_manager
from core.memory import SessionMemory
from core.prompt_builder import build_prompt
from core.llm import call_llm
from core.intention_detector import IntentionDetector
from core.formatter import format_result, format_result_with_validation
import requests
from core.executor import execute_code
from core.code_security import is_code_safe
from core.error_handler import handle_code_error
from core.consulting import auto_comment_agent
from core.visualization import generate_and_run_visualization
from core.business_examples import get_business_example
from core import excel_utils
from db.session import get_session as get_db_session
from db.models import Question, CodeExecution, ConsultingMessage

# Session
session = get_session_manager()
memory = SessionMemory()

llm_provider = session.llm_provider
llm_model = session.llm_model
provider_labels = {
    "codestral": "Codestral",
    "ollama": "Ollama",
    "lmstudio": "LM Studio",
}
provider_label = provider_labels.get((llm_provider or "").lower(), llm_provider or "Unknown")
model_used_label = f"{provider_label} ({llm_model})" if llm_model else provider_label
business_context = None
if session.business_example_key:
    example = get_business_example(session.business_example_key)
    if example:
        business_context = f"{example.get('dataset_name', session.business_example_key)} ({example.get('domain', 'unknown')})"
    else:
        business_context = session.business_example_key
elif session.business_domain and session.business_domain != "auto":
    business_context = session.business_domain

# Sidebar
render_sidebar()

# Header
st.title("🤖 Agent IA")

if not session.has_data:
    st.warning("⚠️ Aucune donnée chargée")
    st.info("Chargez un fichier pour commencer à poser des questions.")
    if st.button("🏠 Charger des données"):
        st.switch_page("pages/1_🏠_Home.py")
    st.stop()

df = session.df
analysis_df = session.df_norm if session.df_norm is not None else df

# Data info bar
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"**📊 {session.df_name}** — {len(df):,} lignes × {len(df.columns)} colonnes")
with col2:
    if session.quality_score:
        if session.quality_score >= 80:
            st.success(f"✓ Qualité: {session.quality_score:.0f}")
        else:
            st.warning(f"⚠️ Qualité: {session.quality_score:.0f}")
with col3:
    if st.button("📊 Explorer", key="agent_explore"):
        st.switch_page("pages/2_📊_Data_Explorer.py")

st.markdown("---")

# Memory context banner
render_memory_context_banner()

# Dataset preview (only before first exchange)
if session.has_data and not session.exchanges:
    st.markdown("### 📊 Aperçu des données")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Lignes", f"{len(df):,}")
    with col_b:
        st.metric("Colonnes", f"{len(df.columns):,}")

    preview_rows = 10
    st.dataframe(df.head(preview_rows), use_container_width=True)
    st.caption(f"Affichage: {min(preview_rows, len(df))} premières lignes")
    st.markdown("---")

# Chat input
st.markdown("### 💬 Posez votre question")

# Check for suggested question
question = None
if 'suggested_question' in st.session_state and st.session_state['suggested_question']:
    question = st.session_state['suggested_question']
    st.session_state['suggested_question'] = None
    st.info(f"💡 Question suggérée: {question}")

# Input form
with st.form(key="agent_question_form", clear_on_submit=False):
    user_question = st.text_input(
        "Question",
        value=question or "",
        placeholder="Ex: Quels sont les 5 meilleurs produits par ventes ?",
        key="agent_question_input",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        submit = st.form_submit_button("🚀 Analyser", use_container_width=True, type="primary")
    with col2:
        generate_viz = st.form_submit_button("📈 + Graphique", use_container_width=True)
    with col3:
        export_result = st.form_submit_button("📥 + Export", use_container_width=True)

# Process question
if (submit or generate_viz or export_result) and user_question:
    question = user_question.strip()
    
    # Vérifier que la question n'est pas vide
    if not question:
        st.warning("⚠️ Veuillez saisir une question.")
        st.stop()
    
    # Wrapper global pour garantir l'affichage même en cas d'erreur
    st.write("🔍 **Debug:** Début du traitement de la question")
    
    exchange = {
        "question": question,
        "timestamp": datetime.now().strftime("%H:%M"),
        "prompt": "",
        "code": "",
        "result": None,
        "auto_comment": "",
        "vis_img": None,
    }
    
    # Flag pour savoir si on doit continuer
    should_continue = True
    
    try:
        # Afficher un indicateur de traitement
        st.info(f"💬 Traitement de la question: {question[:50]}...")
        st.write("🔍 **Debug:** Entrée dans le bloc try principal")
        
        # Detect skills
        detected_skills = detect_skill_from_question(question)
        if detected_skills:
            skills_names = [s['name'] for s in detected_skills]
            st.caption(f"🛠️ Compétences détectées: {', '.join(skills_names)}")
        
        # Detect intentions (Phase 1)
        intentions = IntentionDetector.detect_all(question)
        primary_intentions = IntentionDetector.detect_primary(question)
        if primary_intentions:
            st.caption(f"🎯 Intentions détectées: {', '.join(primary_intentions[:3])}")
        
        # Add to memory
        memory.append("user", question, timestamp=datetime.now().isoformat())
        
        # Process with LLM
        code = None
        try:
            # Vérifier que l'API key est configurée
            import os
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key or api_key == "VOTRE_CLE_CODESRAL_ICI":
                st.error("❌ **Erreur de configuration** : La clé API Mistral n'est pas configurée.")
                st.info("💡 Veuillez définir la variable d'environnement `MISTRAL_API_KEY` dans un fichier `.env` à la racine du projet.")
                st.code("MISTRAL_API_KEY=votre_cle_api_ici", language="bash")
                st.stop()
            
            with st.spinner("🧠 Génération du code..."):
                # Build prompt with enhanced context (Phase 1)
                context = memory.as_string(last_n=3)
                available_sheets = list(session.all_sheets.keys()) if session.all_sheets else None
                
                # Get skills list for prompt
                skills_list = None
                if detected_skills:
                    skills_list = [s['name'] for s in detected_skills]
                
                # Get data dictionary from session if available
                data_dictionary = st.session_state.get('data_dictionary')
                
                # Build enriched prompt with intentions
                prompt = build_prompt(
                    df=analysis_df,
                    question=question,
                    context=context,
                    available_sheets=available_sheets,
                    user_level=session.user_level,
                    detected_skills=skills_list,
                    data_dictionary=data_dictionary,
                    business_context=business_context
                )
                exchange["prompt"] = prompt
                
                # Call LLM
                st.write(f"📡 Appel de l'API {provider_label}...")
                code = call_llm(prompt, model=llm_model, provider=llm_provider)
                st.write(f"✅ Code reçu ({len(code)} caractères)")
                
                # Vérifier que le code n'est pas vide
                if not code or len(code.strip()) == 0:
                    st.error("❌ L'IA n'a pas généré de code. Veuillez réessayer.")
                    should_continue = False
                    exchange["result"] = "Erreur: Code vide généré par l'IA"
                    exchange["auto_comment"] = "L'IA n'a pas généré de code valide."
                else:
                    exchange["code"] = code
                    
                    # Security check
                    is_safe, reason = is_code_safe(code)
                    if not is_safe:
                        st.error(f"⚠️ Code non sécurisé: {reason}")
                        with st.expander("🔧 Code généré (non sécurisé)"):
                            st.code(code, language="python")
                        should_continue = False
                        exchange["result"] = f"Erreur: Code non sécurisé - {reason}"
                        exchange["auto_comment"] = "Le code généré a été bloqué pour des raisons de sécurité."
        except requests.exceptions.RequestException as e:
            st.error(f"❌ **Erreur de connexion API** : {str(e)}")
            st.info("💡 Vérifiez votre connexion internet et que votre clé API Mistral est valide.")
            st.exception(e)
            should_continue = False
            exchange["result"] = f"Erreur API: {str(e)}"
            exchange["auto_comment"] = "Impossible de contacter l'API Mistral."
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération du code: {str(e)}")
            st.exception(e)
            should_continue = False
            exchange["result"] = f"Erreur: {str(e)}"
            exchange["auto_comment"] = "Une erreur s'est produite lors de la génération du code."
        
        # Si on ne peut pas continuer, afficher quand même ce qu'on a
        if not should_continue:
            session.add_exchange(exchange)
            st.markdown("---")
            st.markdown("### 🤖 Réponse")
            st.error(exchange.get("result", "Erreur inconnue"))
            if exchange.get("auto_comment"):
                st.info(f"🧠 **Analyse:** {exchange['auto_comment']}")
            st.stop()
        
        # Execute code
        raw_result = None
        formatted = None
        validation = None
        try:
            with st.spinner("⚡ Exécution..."):
                raw_result = execute_code(code, analysis_df)
                
                # Error handling with auto-correction
                if isinstance(raw_result, str) and raw_result.startswith("Erreur"):
                    st.warning("⚠️ Erreur détectée, tentative de correction...")
                    
                    correction_attempted = False
                    for new_code in handle_code_error(prompt, code, str(raw_result), max_retries=2, llm_provider=llm_provider, llm_model=llm_model):
                        is_safe, reason = is_code_safe(new_code)
                        if not is_safe:
                            continue
                        
                        correction_attempted = True
                        candidate = execute_code(new_code, df)
                        if not (isinstance(candidate, str) and candidate.startswith("Erreur")):
                            st.success("✅ Correction réussie!")
                            raw_result = candidate
                            code = new_code
                            exchange["code"] = new_code
                            break
                    
                    # Si la correction a échoué, afficher l'erreur
                    if isinstance(raw_result, str) and raw_result.startswith("Erreur"):
                        st.error(f"❌ Erreur d'exécution: {raw_result}")
                        with st.expander("🔧 Code généré (avec erreur)"):
                            st.code(code, language="python")
                
                if raw_result is not None:
                    # Validation et enrichissement du résultat (Phase 1)
                    validation = format_result_with_validation(
                        result=raw_result,
                        question=question,
                        original_df=analysis_df,
                        detected_skills=[s['name'] for s in detected_skills] if detected_skills else None
                    )
                    formatted = validation['formatted']
                    exchange["result"] = formatted
                    exchange["validation"] = validation
                else:
                    st.error("❌ Aucun résultat retourné par l'exécution du code.")
                    formatted = "Erreur: Aucun résultat"
                    exchange["result"] = formatted
        except Exception as e:
            st.error(f"❌ Erreur lors de l'exécution du code: {str(e)}")
            st.exception(e)
            formatted = f"Erreur: {str(e)}"
            exchange["result"] = formatted
            raw_result = formatted
        
        # Consulting analysis (disabled as per user request)
        auto_comment = "" # Résultat généré avec succès.  # Valeur par défaut
        # if raw_result is not None:
        #     try:
        #         with st.spinner("🧠 Analyse professionnelle..."):
        #             auto_comment = auto_comment_agent(df=df, result=raw_result, lang=session.language, llm_model=llm_model, llm_provider=llm_provider)
        #             if not auto_comment or len(auto_comment.strip()) == 0:
        #                 auto_comment = "Analyse générée avec succès."
        #             exchange["auto_comment"] = auto_comment
        #             memory.append("assistant", auto_comment[:200], timestamp=datetime.now().isoformat())
        #     except Exception as e:
        #         st.warning(f"⚠️ Erreur lors de l'analyse professionnelle: {str(e)}")
        #         auto_comment = "Résultat généré avec succès."
        #         exchange["auto_comment"] = auto_comment
        # else:
        #     auto_comment = "Erreur lors de l'exécution."
        #     exchange["auto_comment"] = auto_comment
        
        # Save to database (optionnel - ne bloque pas l'affichage)
        try:
            user_id = st.session_state.get('user_id')
            if user_id is None:
                # Essayer de récupérer ou créer l'utilisateur
                from db.queries import get_or_create_user
                with get_db_session() as db_session:
                    user = get_or_create_user(db_session, session.session_id)
                    user_id = user.id
                    st.session_state['user_id'] = user_id
            
            with get_db_session() as db_session:
                q = Question(question=question, user_id=user_id, file_id=st.session_state.get('file_id'))
                db_session.add(q)
                db_session.commit()
                db_session.refresh(q)
                
                is_error = raw_result is None or (
                    isinstance(raw_result, str) and raw_result.startswith('Erreur')
                )
                result_text = "" if formatted is None else str(formatted)[:1000]
                ce = CodeExecution(
                    code=code,
                    result=result_text,
                    status='error' if is_error else 'success',
                    error_message=str(raw_result)[:500] if isinstance(raw_result, str) and raw_result.startswith('Erreur') else None,
                    model_used=model_used_label,
                    question_id=q.id
                )
                db_session.add(ce)
                
                cm = ConsultingMessage(
                    message=auto_comment,
                    role="assistant",
                    model_used=model_used_label,
                    question_id=q.id
                )
                db_session.add(cm)
                db_session.commit()
        except Exception as e:
            # Ne pas bloquer l'affichage si la DB échoue
            st.warning(f"⚠️ Erreur lors de la sauvegarde en base de données (non bloquant): {str(e)[:100]}")
        
        # Visualization if requested
        if generate_viz and isinstance(formatted, pd.DataFrame) and not formatted.empty:
            with st.spinner("📈 Génération du graphique..."):
                vis_img, vis_info = generate_and_run_visualization(formatted, question, llm_provider=llm_provider, llm_model=llm_model)
                if vis_img:
                    exchange["vis_img"] = vis_img
                    exchange["vis_info"] = vis_info
        
        # Add exchange to session (doit être fait avant l'affichage)
        session.add_exchange(exchange)
        
        st.markdown("---")
        
        # Display result with enhanced information (Phase 1)
        st.markdown("### 🤖 Réponse")
        
        # Afficher les warnings si présents
        if validation and validation.get('warnings'):
            for warning in validation['warnings']:
                st.warning(warning)
        
        # Afficher l'interprétation si présente
        if validation and validation.get('interpretation'):
            st.info(f"💡 {validation['interpretation']}")
        
        # Result
        if isinstance(formatted, pd.DataFrame):
            if not formatted.empty:
                max_rows = session.display_max_rows
                display_df = formatted if max_rows == "Toutes" else formatted.head(int(max_rows))
                st.dataframe(display_df, use_container_width=True)
                st.caption(f"Affichage: {len(display_df)} / {len(formatted)} lignes")
                
                # Contexte statistique si disponible
                if validation and validation.get('context'):
                    ctx = validation['context']
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if 'shape' in ctx:
                            st.metric("Dimensions", ctx['shape'])
                    with col_b:
                        if 'full_rows' in ctx:
                            st.metric("Total complet", f"{ctx['full_rows']:,} lignes")
                    with col_c:
                        if 'quality_score' in validation:
                            score = validation['quality_score']
                            st.metric("Qualité résultat", f"{score}%")
                
                # Actions
                col1, col2, col3 = st.columns(3)
                with col1:
                    try:
                        buffer = excel_utils.export_dataframe_to_buffer(formatted)
                        st.download_button(
                            "📥 Télécharger Excel",
                            data=buffer,
                            file_name=f"resultat_{datetime.now().strftime('%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"result_excel_{len(session.exchanges)}"
                        )
                    except Exception as e:
                        st.error(f"Erreur export: {e}")
                with col2:
                    if st.button("📈 Générer graphique", key=f"result_viz_{len(session.exchanges)}"):
                        try:
                            with st.spinner("Génération..."):
                                vis_img, _ = generate_and_run_visualization(formatted, question, llm_provider=llm_provider, llm_model=llm_model)
                                if vis_img:
                                    st.image(vis_img)
                        except Exception as e:
                            st.error(f"Erreur visualisation: {e}")
                with col3:
                    pass
                
                # Suggestions de suivi
                if validation and validation.get('suggestions'):
                    with st.expander("💬 Questions de suivi suggérées"):
                        for i, suggestion in enumerate(validation['suggestions'], 1):
                            st.write(f"{i}. {suggestion}")
            else:
                st.warning("⚠️ Le résultat est un DataFrame vide.")
        elif formatted is not None:
            st.write(formatted)
        else:
            st.error("❌ Aucun résultat à afficher.")
        
        # Visualization
        if exchange.get("vis_img"):
            st.image(exchange["vis_img"], caption="📈 Visualisation générée")
        
        # Code (if expert mode)
        if session.show_code and code:
            with st.expander("🔧 Code généré"):
                st.code(code, language="python")
        
        # Followup suggestions
        if formatted is not None and not (isinstance(formatted, pd.DataFrame) and formatted.empty):
            render_followup_suggestions(question, formatted)
        
        # Message de confirmation
        st.success("✅ Traitement terminé avec succès!")
    
    except Exception as global_error:
        # En cas d'erreur globale, afficher au moins un message
        st.error(f"❌ Erreur critique lors du traitement: {str(global_error)}")
        st.exception(global_error)
        
        # Essayer d'afficher ce qui a pu être généré
        if 'exchange' in locals() and exchange.get('result'):
            st.markdown("### ⚠️ Résultat partiel")
            st.write(exchange['result'])
        elif 'formatted' in locals() and formatted:
            st.markdown("### ⚠️ Résultat partiel")
            st.write(formatted)

# History
st.markdown("---")
st.markdown("### 📚 Historique de la session")

exchanges = session.exchanges
if exchanges:
    render_chat_history(exchanges, show_code=session.show_code, limit=5)
else:
    st.info("💭 Posez votre première question pour commencer l'analyse.")

# Memory panel (expandable)
st.markdown("---")
render_memory_panel(expanded=False, show_actions=True)
