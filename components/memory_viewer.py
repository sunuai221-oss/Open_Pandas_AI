"""
Session memory visualization component.
"""

import streamlit as st
import json
from typing import Optional
from core.memory import SessionMemory


def render_memory_panel(expanded: bool = False, show_actions: bool = True):
    """
    Displays the complete memory visualization panel.
    
    Args:
        expanded: If True, panel is open by default
        show_actions: If True, displays action buttons
    """
    memory = SessionMemory()
    messages = memory.get_all()
    
    st.markdown("### 🧠 Memory Context")
    
    if not messages:
        st.info("💭 The agent doesn't have context yet. Ask a question to start.")
        return
    
    # Context indicator
    st.success(f"✓ {len(messages)} exchanges in memory - Agent remembers context")
    
    # Display messages
    with st.expander(f"View last {len(messages)} exchanges", expanded=expanded):
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            if role == 'user':
                st.markdown(f"**👤 You** {f'• {timestamp}' if timestamp else ''}")
                st.markdown(f"> {content}")
            else:
                st.markdown(f"**🤖 Assistant** {f'• {timestamp}' if timestamp else ''}")
                st.markdown(f"> {content[:200]}{'...' if len(content) > 200 else ''}")
            
            if i < len(messages) - 1:
                st.markdown("---")
    
    # Actions
    if show_actions:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Memory", key="memory_clear", use_container_width=True):
                memory.clear()
                st.success("Memory cleared")
                st.rerun()
        
        with col2:
            export_data = json.dumps(memory.export(), ensure_ascii=False, indent=2)
            st.download_button(
                "💾 Export JSON",
                data=export_data,
                file_name="memory_export.json",
                mime="application/json",
                key="memory_export",
                use_container_width=True
            )
        
        with col3:
            uploaded = st.file_uploader(
                "📂 Import",
                type=['json'],
                key="memory_import",
                label_visibility="collapsed"
            )
            if uploaded:
                try:
                    imported = json.load(uploaded)
                    memory.import_history(imported)
                    st.success("Memory imported")
                    st.rerun()
                except Exception as e:
                    st.error(f"Import error: {e}")


def render_memory_indicator():
    """
    Displays a compact memory status indicator.
    """
    memory = SessionMemory()
    messages = memory.get_all()
    
    if messages:
        st.markdown(f"🧠 **{len(messages)}** exchanges in context")
    else:
        st.caption("🧠 Memory empty")


def render_memory_context_banner():
    """
    Affiche un bandeau de contexte en haut de la page Agent.
    """
    memory = SessionMemory()
    messages = memory.get_all()
    
    if not messages:
        return
    
    # Créer un résumé du contexte
    last_messages = messages[-3:]
    
    with st.container():
        st.markdown("""
        <style>
        .memory-banner {
            background-color: rgba(0, 100, 200, 0.1);
            border-left: 3px solid #0064c8;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**🧠 Contexte actif** — {len(messages)} échanges en mémoire")
            
            # Aperçu du dernier échange
            if last_messages:
                last_user = None
                for msg in reversed(last_messages):
                    if msg.get('role') == 'user':
                        last_user = msg.get('content', '')[:60]
                        break
                if last_user:
                    st.caption(f"Dernier sujet: \"{last_user}...\"")
        
        with col2:
            if st.button("Voir tout", key="memory_banner_expand"):
                st.session_state['show_memory_detail'] = True


def get_memory_summary(max_length: int = 200) -> str:
    """
    Retourne un résumé textuel de la mémoire pour les prompts.
    """
    memory = SessionMemory()
    return memory.as_string(last_n=5)[:max_length]
