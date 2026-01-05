"""
Data Explorer Page - Data exploration and validation.
"""

import streamlit as st
import pandas as pd
import numpy as np

# Configuration
st.set_page_config(
    page_title="Open Pandas-AI - Data Explorer",
    page_icon="📊",
    layout="wide"
)

from components.sidebar import render_sidebar
from components.data_quality import render_quality_panel
from components.result_display import render_result
from components.export_panel import render_export_panel
from core.session_manager import get_session_manager
from core import excel_utils

# Function to clean column names
def clean_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans column names to avoid visualization issues"""
    df = df.copy()
    df.columns = [str(col).strip().replace(':', '_').replace(' ', '_').replace('\n', '_') for col in df.columns]
    return df

# Session
session = get_session_manager()

# Sidebar
render_sidebar()

# Header
st.title("📊 Data Explorer")

if not session.has_data:
    st.warning("⚠️ No data loaded")
    st.info("Return to the home page to load a file.")
    if st.button("🏠 Go to Home"):
        st.switch_page("pages/1_🏠_Home.py")
    st.stop()

df = session.df
# Clean columns to avoid Altair issues
df = clean_dataframe_columns(df)
filename = session.df_name or "DataFrame"

# Info header
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📁 File", filename[:20] + "..." if len(filename) > 20 else filename)
with col2:
    st.metric("📏 Rows", f"{len(df):,}")
with col3:
    st.metric("📊 Columns", len(df.columns))
with col4:
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    st.metric("💾 Memory", f"{memory_mb:.1f} MB")

st.markdown("---")

# Multi-sheets selector
if session.all_sheets:
    st.markdown("### 📑 Excel Sheets")
    sheet_names = list(session.all_sheets.keys())
    selected = st.selectbox(
        "Active sheet",
        sheet_names,
        index=sheet_names.index(session.selected_sheet) if session.selected_sheet in sheet_names else 0
    )
    if selected != session.selected_sheet:
        session.set_dataframe(session.all_sheets[selected], filename)
        session.set_selected_sheet(selected)
        st.rerun()
    st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Table", "📈 Statistics", "🔍 Quality", "📥 Export"])

# Tab 1: Table
with tab1:
    st.markdown("### 📋 Data Overview")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search in data", key="data_search")
    with col2:
        row_options = [10, 25, 50, 100, 500, "All"]
        current_max_rows = session.display_max_rows
        if current_max_rows not in row_options:
            current_max_rows = 25
        max_rows = st.selectbox(
            "Rows to display",
            row_options,
            index=row_options.index(current_max_rows),
            key="data_explorer_max_rows",
        )
        if max_rows != session.display_max_rows:
            session.set_display_max_rows(max_rows)
    with col3:
        columns_filter = st.multiselect(
            "Columns to display",
            df.columns.tolist(),
            default=df.columns.tolist()[:10] if len(df.columns) > 10 else df.columns.tolist()
        )
    
    display_df = df[columns_filter] if columns_filter else df
    
    if search:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
        st.caption(f"🔍 {len(display_df)} results found")
    
    display_slice = display_df if max_rows == "All" else display_df.head(int(max_rows))
    st.dataframe(display_slice, use_container_width=True, height=500)
    st.caption(f"Display: {len(display_slice)} / {len(display_df)} rows")

# Tab 2: Statistics
with tab2:
    st.markdown("### 📈 Descriptive Statistics")
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Numeric", "Categorical", "Correlations"])
    
    with sub_tab1:
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            st.dataframe(numeric_df.describe(), use_container_width=True)
            
            st.markdown("#### 📊 Distributions")
            col = st.selectbox("Column to visualize", numeric_df.columns.tolist(), key="dist_col")
            if col:
                chart_data = df[col].dropna()
                st.bar_chart(chart_data.value_counts().head(20))
        else:
            st.info("No numeric columns")
    
    with sub_tab2:
        cat_df = df.select_dtypes(include=['object', 'category'])
        if not cat_df.empty:
            st.markdown("#### Unique values per column")
            unique_counts = {col: df[col].nunique() for col in cat_df.columns}
            st.dataframe(pd.DataFrame.from_dict(unique_counts, orient='index', columns=['Unique values']))
            
            st.markdown("#### Distribution")
            col = st.selectbox("Column", cat_df.columns.tolist(), key="cat_col")
            if col:
                value_counts = df[col].value_counts().head(15)
                st.bar_chart(value_counts)
        else:
            st.info("No categorical columns")
    
    with sub_tab3:
        numeric_df = df.select_dtypes(include=['number'])
        if len(numeric_df.columns) >= 2:
            st.markdown("#### Correlation matrix")
            corr = numeric_df.corr()
            st.dataframe(corr.style.background_gradient(cmap='RdYlGn', vmin=-1, vmax=1), use_container_width=True)
            
            st.markdown("#### Strong correlations (|r| > 0.5)")
            strong_corrs = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    if abs(corr.iloc[i, j]) > 0.5:
                        strong_corrs.append({
                            'Variable 1': corr.columns[i],
                            'Variable 2': corr.columns[j],
                            'Correlation': f"{corr.iloc[i, j]:.3f}"
                        })
            if strong_corrs:
                st.dataframe(pd.DataFrame(strong_corrs), use_container_width=True)
            else:
                st.info("No strong correlations detected")
        else:
            st.info("Need at least 2 numeric columns to calculate correlations")

# Tab 3: Quality
with tab3:
    result = render_quality_panel(df, expanded=True)
    
    if result:
        session.set_validation_result(result, result.get('quality_score', 100))

# Tab 4: Export
with tab4:
    render_export_panel(df, title="📥 Export Data", key_prefix="explorer_export")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/1_🏠_Home.py")
with col2:
    if st.button("🤖 Analyze with AI", use_container_width=True, type="primary"):
        st.switch_page("pages/3_🤖_Agent.py")
