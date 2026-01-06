"""
Agent Page - Main AI conversation interface.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="Open Pandas-AI - AI Agent",
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
from core.prompt_builder import build_prompt_with_agent
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
from core.business_examples import get_domain_assets
from core import excel_utils
from db.session import get_session as get_db_session
from db.models import Question, CodeExecution, ConsultingMessage

from agents.registry import get_available_agents, get_agent
from agents.detector import detect_domain

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
st.title("🤖 AI Agent")

if not session.has_data:
    st.warning("⚠️ No data loaded")
    st.info("Load a file to start asking questions.")
    if st.button("🏠 Load Data"):
        st.switch_page("pages/1_🏠_Home.py")
    st.stop()

df = session.df
analysis_df = session.df_norm if session.df_norm is not None else df

# Agent selector (orchestration mode)
available_agents = get_available_agents()
agent_domains = sorted(available_agents.keys())
agent_modes = ["auto"] + agent_domains
current_mode = session.selected_agent_mode if session.selected_agent_mode in agent_modes else "auto"

agent_col_a, agent_col_b = st.columns([2, 3])
with agent_col_a:
    selected_mode = st.selectbox(
        "Mode Agent",
        options=agent_modes,
        index=agent_modes.index(current_mode),
        format_func=lambda d: d.capitalize() if d != "auto" else "Auto",
        key="agent_mode_select",
    )
if selected_mode != session.selected_agent_mode:
    session.set_selected_agent_mode(selected_mode)

# Resolve active agent
active_agent = None
detection = None
if session.selected_agent_mode == "auto":
    detection = detect_domain(analysis_df)
    session.set_agent_detection(
        detected_agent=detection.domain,
        confidence=detection.confidence,
        reasons=detection.reasons,
    )
    active_agent = get_agent(detection.domain)
else:
    session.set_agent_detection(detected_agent=None, confidence=0.0, reasons=[])
    active_agent = get_agent(session.selected_agent_mode)

with agent_col_b:
    if detection:
        reasons_str = "; ".join(detection.reasons[:4]) if detection.reasons else "n/a"
        st.info(
            f"Agent actif: {active_agent.name} (Auto, confiance {detection.confidence:.2f}) — raisons: {reasons_str}"
        )
    else:
        st.info(f"Agent actif: {active_agent.name} (manuel)")

# Data info bar
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"**📊 {session.df_name}** — {len(df):,} rows × {len(df.columns)} columns")
with col2:
    if session.quality_score:
        if session.quality_score >= 80:
            st.success(f"✓ Quality: {session.quality_score:.0f}")
        else:
            st.warning(f"⚠️ Quality: {session.quality_score:.0f}")
with col3:
    if st.button("📊 Explore", key="agent_explore"):
        st.switch_page("pages/2_📊_Data_Explorer.py")

st.markdown("---")

# Memory context banner
render_memory_context_banner()

# Dataset preview (only before first exchange)
if session.has_data and not session.exchanges:
    st.markdown("### 📊 Data Preview")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Rows", f"{len(df):,}")
    with col_b:
        st.metric("Columns", f"{len(df.columns):,}")

    preview_rows = 10
    st.dataframe(df.head(preview_rows), use_container_width=True)
    st.caption(f"Display: {min(preview_rows, len(df))} first rows")
    st.markdown("---")

# Agent follow-up suggestions (before first question)
if session.has_data and not session.exchanges and active_agent:
    agent_context = {
        "df_columns": list(df.columns),
        "language": session.language,
        "user_level": session.user_level,
    }
    agent_suggestions = active_agent.suggest_followups(agent_context)
    if agent_suggestions:
        with st.expander(f"💡 Suggestions de l'agent {active_agent.name}", expanded=True):
            for i, suggestion in enumerate(agent_suggestions[:6], 1):
                if st.button(suggestion, key=f"agent_sugg_{i}"):
                    st.session_state["suggested_question"] = suggestion
                    st.rerun()

# Chat input
st.markdown("### 💬 Ask your question")

# Check for suggested question
question = None
if 'suggested_question' in st.session_state and st.session_state['suggested_question']:
    question = st.session_state['suggested_question']
    st.session_state['suggested_question'] = None
    st.info(f"💡 Suggested question: {question}")

# Input form
with st.form(key="agent_question_form", clear_on_submit=False):
    user_question = st.text_input(
        "Question",
        value=question or "",
        placeholder="Ex: What are the 5 best products by sales?",
        key="agent_question_input",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        submit = st.form_submit_button("🚀 Analyze", use_container_width=True, type="primary")
    with col2:
        generate_viz = st.form_submit_button("📈 + Chart", use_container_width=True)
    with col3:
        export_result = st.form_submit_button("📥 + Export", use_container_width=True)

# Process question
if (submit or generate_viz or export_result) and user_question:
    question = user_question.strip()
    
    # Check that question is not empty
    if not question:
        st.warning("⚠️ Please enter a question.")
        st.stop()
    
    # Global wrapper to ensure display even in case of error
    st.write("🔍 **Debug:** Start processing question")
    
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
        # Display processing indicator
        st.info(f"💬 Processing question: {question[:50]}...")
        st.write("🔍 **Debug:** Entering main try block")
        
        # Detect skills
        detected_skills = detect_skill_from_question(question)
        if detected_skills:
            skills_names = [s['name'] for s in detected_skills]
            st.caption(f"🛠️ Skills detected: {', '.join(skills_names)}")
        
        # Detect intentions (Phase 1)
        intentions = IntentionDetector.detect_all(question)
        primary_intentions = IntentionDetector.detect_primary(question)
        if primary_intentions:
            st.caption(f"🎯 Intentions detected: {', '.join(primary_intentions[:3])}")
        
        # Add to memory
        memory.append("user", question, timestamp=datetime.now().isoformat())
        
        # Process with LLM
        code = None
        try:
            # Only Codestral requires a Mistral API key (offline providers must work without it)
            import os
            selected_provider = (llm_provider or "").lower()
            if selected_provider in ("codestral", "codestral.ai", "mistral", "mistralai"):
                api_key = os.getenv("MISTRAL_API_KEY")
                if not api_key or api_key == "VOTRE_CLE_CODESRAL_ICI":
                    st.error("❌ **Configuration Error**: Mistral API key is not configured for Codestral.")
                    st.info("💡 Set `MISTRAL_API_KEY` in a `.env` file at the project root, or switch provider to LM Studio / Ollama for 100% local usage.")
                    st.code("MISTRAL_API_KEY=your_api_key_here", language="bash")
                    st.stop()
            
            with st.spinner("🧠 Generating code..."):
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
                agent_context = {
                    "language": session.language,
                    "user_level": session.user_level,
                    "df_columns": list(analysis_df.columns),
                    "business_context": business_context,
                }
                agent_prompt = active_agent.build_agent_prompt(agent_context) if active_agent else ""
                agent_plan = active_agent.analysis_plan(question, agent_context) if active_agent else {}
                domain_assets = get_domain_assets(active_agent.domain) if active_agent else {}

                prompt = build_prompt_with_agent(
                    df=analysis_df,
                    question=question,
                    context=context,
                    available_sheets=available_sheets,
                    user_level=session.user_level,
                    detected_skills=skills_list,
                    data_dictionary=data_dictionary,
                    business_context=business_context,
                    agent_prompt=agent_prompt,
                    agent_plan=agent_plan,
                    domain_assets=domain_assets,
                )
                exchange["prompt"] = prompt
                
                # Call LLM
                st.write(f"📡 Calling {provider_label} API...")
                code = call_llm(prompt, model=llm_model, provider=llm_provider)
                st.write(f"✅ Code received ({len(code)} characters)")
                
                # Check that code is not empty
                if not code or len(code.strip()) == 0:
                    st.error("❌ AI did not generate code. Please try again.")
                    should_continue = False
                    exchange["result"] = "Error: Empty code generated by AI"
                    exchange["auto_comment"] = "AI did not generate valid code."
                else:
                    exchange["code"] = code
                    
                    # Security check
                    is_safe, reason = is_code_safe(code)
                    if not is_safe:
                        st.error(f"⚠️ Unsafe code: {reason}")
                        with st.expander("🔧 Generated code (unsafe)"):
                            st.code(code, language="python")
                        should_continue = False
                        exchange["result"] = f"Error: Unsafe code - {reason}"
                        exchange["auto_comment"] = "Generated code was blocked for security reasons."
        except requests.exceptions.RequestException as e:
            st.error(f"❌ **API Connection Error**: {str(e)}")
            st.info("💡 Check your internet connection and that your Mistral API key is valid.")
            st.exception(e)
            should_continue = False
            exchange["result"] = f"API Error: {str(e)}"
            exchange["auto_comment"] = "Unable to contact Mistral API."
        except Exception as e:
            st.error(f"❌ Error during code generation: {str(e)}")
            st.exception(e)
            should_continue = False
            exchange["result"] = f"Error: {str(e)}"
            exchange["auto_comment"] = "An error occurred during code generation."
        
        # If we can't continue, still display what we have
        if not should_continue:
            session.add_exchange(exchange)
            st.markdown("---")
            st.markdown("### 🤖 Response")
            st.error(exchange.get("result", "Unknown error"))
            if exchange.get("auto_comment"):
                st.info(f"🧠 **Analysis:** {exchange['auto_comment']}")
            st.stop()
        
        # Execute code
        raw_result = None
        formatted = None
        validation = None
        try:
            with st.spinner("⚡ Executing..."):
                raw_result = execute_code(code, analysis_df)
                
                # Error handling with auto-correction
                if isinstance(raw_result, str) and raw_result.startswith("Error"):
                    st.warning("⚠️ Error detected, attempting correction...")
                    
                    correction_attempted = False
                    for new_code in handle_code_error(prompt, code, str(raw_result), max_retries=2, llm_provider=llm_provider, llm_model=llm_model):
                        is_safe, reason = is_code_safe(new_code)
                        if not is_safe:
                            continue
                        
                        correction_attempted = True
                        candidate = execute_code(new_code, analysis_df)
                        if not (isinstance(candidate, str) and candidate.startswith("Error")):
                            st.success("✅ Correction successful!")
                            raw_result = candidate
                            code = new_code
                            exchange["code"] = new_code
                            break
                    
                    # If correction failed, display error
                    if isinstance(raw_result, str) and raw_result.startswith("Error"):
                        st.error(f"❌ Execution error: {raw_result}")
                        with st.expander("🔧 Generated code (with error)"):
                            st.code(code, language="python")
                
                if raw_result is not None:
                    # Validation and result enrichment (Phase 1)
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
                    st.error("❌ No result returned by code execution.")
                    formatted = "Error: No result"
                    exchange["result"] = formatted
        except Exception as e:
            st.error(f"❌ Error during code execution: {str(e)}")
            st.exception(e)
            formatted = f"Error: {str(e)}"
            exchange["result"] = formatted
            raw_result = formatted
        
        # Consulting analysis (disabled as per user request)
        auto_comment = "" # Result generated successfully.  # Default value
        # if raw_result is not None:
        #     try:
        #         with st.spinner("🧠 Professional analysis..."):
        #             auto_comment = auto_comment_agent(df=df, result=raw_result, lang=session.language, llm_model=llm_model, llm_provider=llm_provider)
        #             if not auto_comment or len(auto_comment.strip()) == 0:
        #                 auto_comment = "Analysis generated successfully."
        #             exchange["auto_comment"] = auto_comment
        #             memory.append("assistant", auto_comment[:200], timestamp=datetime.now().isoformat())
        #     except Exception as e:
        #         st.warning(f"⚠️ Error during professional analysis: {str(e)}")
        #         auto_comment = "Result generated successfully."
        #         exchange["auto_comment"] = auto_comment
        # else:
        #     auto_comment = "Error during execution."
        #     exchange["auto_comment"] = auto_comment
        
        # Save to database (optional - doesn't block display)
        try:
            user_id = st.session_state.get('user_id')
            if user_id is None:
                # Try to retrieve or create user
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
                    isinstance(raw_result, str) and raw_result.startswith('Error')
                )
                result_text = "" if formatted is None else str(formatted)[:1000]
                ce = CodeExecution(
                    code=code,
                    result=result_text,
                    status='error' if is_error else 'success',
                    error_message=str(raw_result)[:500] if isinstance(raw_result, str) and raw_result.startswith('Error') else None,
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
            # Don't block display if DB fails
            st.warning(f"⚠️ Error saving to database (non-blocking): {str(e)[:100]}")
        
        # Visualization if requested
        if generate_viz and isinstance(formatted, pd.DataFrame) and not formatted.empty:
            with st.spinner("📈 Generating chart..."):
                vis_img, vis_info = generate_and_run_visualization(formatted, question, llm_provider=llm_provider, llm_model=llm_model)
                if vis_img:
                    exchange["vis_img"] = vis_img
                    exchange["vis_info"] = vis_info
        
        # Add exchange to session (must be done before display)
        session.add_exchange(exchange)
        
        st.markdown("---")
        
        # Display result with enhanced information (Phase 1)
        st.markdown("### 🤖 Response")
        
        # Display warnings if present
        if validation and validation.get('warnings'):
            for warning in validation['warnings']:
                st.warning(warning)
        
        # Display interpretation if present
        if validation and validation.get('interpretation'):
            st.info(f"💡 {validation['interpretation']}")
        
        # Result
        if isinstance(formatted, pd.DataFrame):
            if not formatted.empty:
                max_rows = session.display_max_rows
                display_df = formatted if max_rows == "All" else formatted.head(int(max_rows))
                st.dataframe(display_df, use_container_width=True)
                st.caption(f"Display: {len(display_df)} / {len(formatted)} rows")
                
                # Statistical context if available
                if validation and validation.get('context'):
                    ctx = validation['context']
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if 'shape' in ctx:
                            st.metric("Dimensions", ctx['shape'])
                    with col_b:
                        if 'full_rows' in ctx:
                            st.metric("Complete total", f"{ctx['full_rows']:,} rows")
                    with col_c:
                        if 'quality_score' in validation:
                            score = validation['quality_score']
                            st.metric("Result quality", f"{score}%")
                
                # Actions
                col1, col2, col3 = st.columns(3)
                with col1:
                    try:
                        buffer = excel_utils.export_dataframe_to_buffer(formatted)
                        st.download_button(
                            "📥 Download Excel",
                            data=buffer,
                            file_name=f"result_{datetime.now().strftime('%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"result_excel_{len(session.exchanges)}"
                        )
                    except Exception as e:
                        st.error(f"Export error: {e}")
                with col2:
                    if st.button("📈 Generate Chart", key=f"result_viz_{len(session.exchanges)}"):
                        try:
                            with st.spinner("Generating..."):
                                vis_img, _ = generate_and_run_visualization(formatted, question, llm_provider=llm_provider, llm_model=llm_model)
                                if vis_img:
                                    st.image(vis_img)
                        except Exception as e:
                            st.error(f"Visualization error: {e}")
                with col3:
                    pass
                
                # Follow-up suggestions
                if validation and validation.get('suggestions'):
                    with st.expander("💬 Suggested follow-up questions"):
                        for i, suggestion in enumerate(validation['suggestions'], 1):
                            st.write(f"{i}. {suggestion}")
            else:
                st.warning("⚠️ Result is an empty DataFrame.")
        elif formatted is not None:
            st.write(formatted)
        else:
            st.error("❌ No result to display.")
        
        # Visualization
        if exchange.get("vis_img"):
            st.image(exchange["vis_img"], caption="📈 Generated visualization")
        
        # Code (if expert mode)
        if session.show_code and code:
            with st.expander("🔧 Generated code"):
                st.code(code, language="python")
        
        # Followup suggestions
        if formatted is not None and not (isinstance(formatted, pd.DataFrame) and formatted.empty):
            render_followup_suggestions(question, formatted)
        
        # Confirmation message
        st.success("✅ Processing completed successfully!")
    
    except Exception as global_error:
        # In case of global error, display at least a message
        st.error(f"❌ Critical error during processing: {str(global_error)}")
        st.exception(global_error)
        
        # Try to display what could be generated
        if 'exchange' in locals() and exchange.get('result'):
            st.markdown("### ⚠️ Partial Result")
            st.write(exchange['result'])
        elif 'formatted' in locals() and formatted:
            st.markdown("### ⚠️ Partial Result")
            st.write(formatted)

# History
st.markdown("---")
st.markdown("### 📚 Session History")

exchanges = session.exchanges
if exchanges:
    render_chat_history(exchanges, show_code=session.show_code, limit=5)
else:
    st.info("💭 Ask your first question to start the analysis.")

# Memory panel (expandable)
st.markdown("---")
render_memory_panel(expanded=False, show_actions=True)
