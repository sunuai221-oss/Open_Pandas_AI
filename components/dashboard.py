"""
Dashboard Components - Reusable components to display analyses in dashboard format
Inspired by Keen IO Dashboard templates
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional


def render_dashboard_header(title: str, subtitle: str = "", icon: str = "📊"):
    """
    Renders dashboard header.
    
    Args:
        title: Main title
        subtitle: Subtitle (optional)
        icon: Emoji for title
    """
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"# {icon}")
    with col2:
        st.markdown(f"# {title}")
        if subtitle:
            st.markdown(f"*{subtitle}*")
    st.divider()


def render_metric_card(label: str, value: Any, delta: Optional[str] = None, color: str = "blue"):
    """
    Renders a metric card (KPI).
    
    Args:
        label: Metric label
        value: Value to display
        delta: Optional change (+5%, -2.3%, etc.)
        color: Color (blue, green, red, orange)
    """
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.metric(label, value)
        
        if delta:
            with col2:
                st.caption(delta)


def render_stats_grid(stats: Dict[str, Any], columns: int = 3):
    """
    Renders a statistics grid (KPIs).
    
    Args:
        stats: Dict {label: value, ...}
        columns: Number of columns
    """
    cols = st.columns(columns)
    
    for i, (label, value) in enumerate(stats.items()):
        with cols[i % columns]:
            st.metric(label, value)


def render_result_card(
    title: str,
    result: Any,
    question: str = "",
    timestamp: str = "",
    show_code: bool = False,
    code: str = ""
):
    """
    Renders an analysis result card.
    
    Args:
        title: Card title
        result: Result (DataFrame, number, text)
        question: Original question
        timestamp: Execution timestamp
        show_code: Show code?
        code: Executed code
    """
    with st.container():
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {title}")
        with col2:
            if timestamp:
                st.caption(f"🕐 {timestamp}")
        
        # Content
        if isinstance(result, pd.DataFrame):
            st.dataframe(result, use_container_width=True)
            st.caption(f"📊 {len(result)} rows × {len(result.columns)} columns")
        else:
            st.write(result)
        
        # Metadata
        if question:
            st.caption(f"❓ {question}")
        
        # Code (optional)
        if show_code and code:
            with st.expander("🔧 Executed Code"):
                st.code(code, language="python")


def render_dashboard_grid(
    exchanges: List[Dict[str, Any]],
    columns: int = 2,
    show_code: bool = False
):
    """
    Renders an analysis results grid.
    
    Args:
        exchanges: List of exchanges {question, result, code, timestamp}
        columns: Number of columns
        show_code: Show codes?
    """
    if not exchanges:
        st.info("📭 No analysis yet. Start by asking a question!")
        return
    
    cols = st.columns(columns)
    
    for i, exchange in enumerate(exchanges):
        with cols[i % columns]:
            render_result_card(
                title=f"Analysis #{len(exchanges) - i}",
                result=exchange.get('result'),
                question=exchange.get('question', ''),
                timestamp=exchange.get('timestamp', ''),
                show_code=show_code,
                code=exchange.get('code', '')
            )


def render_timeline(exchanges: List[Dict[str, Any]]):
    """
    Renders an analysis timeline.
    
    Args:
        exchanges: List of exchanges
    """
    if not exchanges:
        st.info("📭 No analysis yet.")
        return
    
    st.markdown("### 📍 Analysis Timeline")
    
    for i, exchange in enumerate(reversed(exchanges)):
        # Container for each item
        with st.container():
            col1, col2 = st.columns([1, 10])
            
            with col1:
                st.markdown(f"**#{len(exchanges) - i}**")
            
            with col2:
                # Question
                st.markdown(f"**❓ {exchange.get('question', 'No title')[:70]}...**")
                
                # Timestamp
                if exchange.get('timestamp'):
                    st.caption(f"🕐 {exchange['timestamp']}")
                
                # Result summary
                result = exchange.get('result')
                if isinstance(result, pd.DataFrame):
                    st.caption(f"📊 {len(result)} rows")
                elif isinstance(result, str):
                    st.caption(result[:100])
                else:
                    st.caption(str(result)[:100])
        
        st.divider()


def render_dashboard_summary(exchanges: List[Dict[str, Any]]):
    """
    Renders dashboard summary.
    
    Args:
        exchanges: List of exchanges
    """
    if not exchanges:
        return
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Analyses", len(exchanges))
    
    with col2:
        successful = sum(1 for e in exchanges if e.get('result') and not str(e.get('result')).startswith('Error'))
        st.metric("✅ Successful", successful)
    
    with col3:
        failed = sum(1 for e in exchanges if str(e.get('result', '')).startswith('Error'))
        st.metric("❌ Failed", failed)


def render_hero_section(
    title: str,
    subtitle: str,
    cta_button: str = "",
    cta_callback=None
):
    """
    Renders a hero section (large header with call to action).
    
    Args:
        title: Main title
        subtitle: Subtitle
        cta_button: Button text (optional)
        cta_callback: Button callback
    """
    with st.container():
        st.markdown(f"<h1 style='text-align: center; color: #E8A17A;'>{title}</h1>", 
                   unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #666;'>{subtitle}</h3>", 
                   unsafe_allow_html=True)
        
        if cta_button:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button(cta_button, use_container_width=True, type="primary"):
                    if cta_callback:
                        cta_callback()
        
        st.divider()


def render_insight_box(title: str, content: str, icon: str = "💡"):
    """
    Renders an insight/advice box.
    
    Args:
        title: Insight title
        content: Content
        icon: Emoji
    """
    with st.container():
        st.markdown(f"### {icon} {title}")
        st.markdown(f"> {content}")


def render_comparison_table(
    data: Dict[str, List[Any]],
    title: str = "Comparison"
):
    """
    Renders a comparison table.
    
    Args:
        data: Dict {column: [values]}
        title: Title
    """
    st.markdown(f"### {title}")
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def render_empty_state(title: str, description: str, icon: str = "📭"):
    """
    Renders an empty state.
    
    Args:
        title: Title
        description: Description
        icon: Emoji
    """
    st.markdown(f"""
    <div style='text-align: center; padding: 40px;'>
        <div style='font-size: 48px;'>{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)
