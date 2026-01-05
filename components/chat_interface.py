"""
Enhanced chat interface for Open Pandas-AI.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from core.session_manager import get_session_manager

def render_chat_message(
    role: str,
    content: str,
    timestamp: Optional[str] = None,
    result: Any = None,
    code: Optional[str] = None,
    show_code: bool = False,
    actions: Optional[Dict[str, Callable]] = None,
    key_prefix: str = "msg"
):
    """
    Displays a styled chat message.
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        timestamp: Optional timestamp
        result: Execution result (DataFrame, etc.)
        code: Generated code (for assistant)
        show_code: Show generated code
        actions: Dict of actions {label: callback}
        key_prefix: Prefix for Streamlit keys
    """
    
    is_user = role == 'user'
    
    # Container with style
    with st.container():
        # Message header
        col1, col2 = st.columns([1, 10])
        
        with col1:
            if is_user:
                st.markdown("### 👤")
            else:
                st.markdown("### 🤖")
        
        with col2:
            # Name and timestamp
            name = "You" if is_user else "AI Assistant"
            time_str = f" • {timestamp}" if timestamp else ""
            st.markdown(f"**{name}**{time_str}")
            
            # Message content
            if is_user:
                st.markdown(f"> {content}")
            else:
                st.markdown(content)
        
        # Result (for assistant)
        if result is not None and not is_user:
            _render_result_in_chat(result, key_prefix)
        
        # Generated code
        if code and show_code and not is_user:
            with st.expander("🔧 Generated Code", expanded=False):
                st.code(code, language="python")
        
        # Actions
        if actions and not is_user:
            cols = st.columns(len(actions))
            for i, (label, callback) in enumerate(actions.items()):
                with cols[i]:
                    if st.button(label, key=f"{key_prefix}_action_{i}", use_container_width=True):
                        callback()
        
        st.markdown("---")


def _render_result_in_chat(result: Any, key_prefix: str):
    """Displays result in chat context."""
    
    if isinstance(result, pd.DataFrame):
        if not result.empty:
            session = get_session_manager()
            max_rows = session.display_max_rows
            display_df = result if max_rows == "All" else result.head(int(max_rows))
            st.dataframe(display_df, use_container_width=True, height=300)
            st.caption(f"Display: {len(display_df)} / {len(result)} rows - {len(result.columns)} columns")
    elif isinstance(result, (int, float)):
        st.metric("Result", f"{result:,.2f}" if isinstance(result, float) else f"{result:,}")
    elif isinstance(result, str):
        st.info(result)
    elif isinstance(result, (list, tuple)):
        st.write(result)
    else:
        st.write(result)


def render_chat_input(
    placeholder: str = "Ask your question...",
    key: str = "chat_input",
    suggested_question: Optional[str] = None
) -> Optional[str]:
    """
    Displays chat input area.
    
    Args:
        placeholder: Placeholder text
        key: Streamlit key
        suggested_question: Pre-filled question (from suggestions)
    
    Returns:
        The entered question or None
    """
    
    # Check if a suggestion is pending
    if 'suggested_question' in st.session_state and st.session_state['suggested_question']:
        suggested = st.session_state['suggested_question']
        st.session_state['suggested_question'] = None  # Consume the suggestion
        return suggested
    
    # Input area with form
    with st.form(key=f"{key}_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            question = st.text_input(
                "Question",
                placeholder=placeholder,
                key=f"{key}_input",
                label_visibility="collapsed"
            )
        
        with col2:
            submit = st.form_submit_button("➤", use_container_width=True)
        
        if submit and question:
            return question
    
    return None


def render_chat_history(
    exchanges: list,
    show_code: bool = False,
    limit: int = 10
):
    """
    Displays chat history.
    
    Args:
        exchanges: List of exchanges
        show_code: Show generated code
        limit: Maximum number of exchanges to display
    """
    
    if not exchanges:
        st.info("💭 No exchanges yet. Ask a question to start.")
        return
    
    # Display last exchanges (from most recent to oldest)
    for i, exchange in enumerate(reversed(exchanges[-limit:])):
        question = exchange.get('question', '')
        result = exchange.get('result')
        code = exchange.get('code', '')
        auto_comment = exchange.get('auto_comment', '')
        timestamp = exchange.get('timestamp', '')
        
        # User message
        render_chat_message(
            role='user',
            content=question,
            timestamp=timestamp,
            key_prefix=f"hist_user_{i}"
        )
        
        # Assistant message
        render_chat_message(
            role='assistant',
            content=auto_comment if auto_comment else "Here is the result:",
            result=result,
            code=code,
            show_code=show_code,
            key_prefix=f"hist_asst_{i}"
        )


def render_typing_indicator():
    """Displays a typing/loading indicator."""
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 5px;">
        <span>🤖 Assistant is thinking</span>
        <div class="typing-dots">
            <span>.</span><span>.</span><span>.</span>
        </div>
    </div>
    <style>
    .typing-dots span {
        animation: blink 1.4s infinite;
        animation-fill-mode: both;
    }
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes blink {
        0% { opacity: 0.2; }
        20% { opacity: 1; }
        100% { opacity: 0.2; }
    }
    </style>
    """, unsafe_allow_html=True)


def render_processing_status(status: str, progress: float = None):
    """
    Displays processing status.
    
    Args:
        status: Status message
        progress: Progress (0-1) or None for indeterminate
    """
    
    if progress is not None:
        st.progress(progress)
    
    st.markdown(f"⏳ {status}")
