"""
Multi-format export panel for Open Pandas-AI.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime
from io import BytesIO

from core import excel_utils
from core import excel_formatter


def render_export_panel(
    df: pd.DataFrame,
    title: str = "📥 Export Data",
    show_options: bool = True,
    key_prefix: str = "export"
):
    """
    Displays the complete export panel.
    
    Args:
        df: DataFrame to export
        title: Panel title
        show_options: Show advanced options
        key_prefix: Prefix for Streamlit keys
    """
    
    if df is None or df.empty:
        st.info("No data to export")
        return
    
    st.markdown(f"### {title}")
    
    # Data info
    st.caption(f"📊 {len(df):,} rows × {len(df.columns)} columns")
    
    # Export options
    if show_options:
        with st.expander("⚙️ Export Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                sheet_name = st.text_input(
                    "Sheet Name",
                    value="Data",
                    key=f"{key_prefix}_sheet_name"
                )
                
                include_index = st.checkbox(
                    "Include Index",
                    value=False,
                    key=f"{key_prefix}_include_index"
                )
            
            with col2:
                format_style = st.selectbox(
                    "Formatting Style",
                    options=['auto', 'professional', 'modern', 'minimal', 'none'],
                    index=0,
                    key=f"{key_prefix}_format_style"
                )
    else:
        sheet_name = "Data"
        include_index = False
        format_style = 'auto'
    
    st.markdown("---")
    
    # Export buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        _render_excel_export(df, sheet_name, include_index, format_style, key_prefix)
    
    with col2:
        _render_csv_export(df, include_index, key_prefix)
    
    with col3:
        _render_json_export(df, key_prefix)


def _render_excel_export(
    df: pd.DataFrame,
    sheet_name: str,
    include_index: bool,
    format_style: str,
    key_prefix: str
):
    """Displays Excel export button."""
    
    st.markdown("#### 📗 Excel")
    
    # Préparer le fichier
    buffer = BytesIO()
    
    # Export avec pandas
    df.to_excel(buffer, sheet_name=sheet_name, index=include_index, engine='openpyxl')
    
    # Apply formatting if requested
    if format_style != 'none':
        buffer.seek(0)
        from openpyxl import load_workbook
        wb = load_workbook(buffer)
        ws = wb.active
        
        if format_style in ['professional', 'modern', 'minimal']:
            excel_formatter.apply_report_style(ws, format_style)
        else:  # auto
            excel_formatter.apply_auto_column_width(ws)
            excel_formatter.apply_header_style(ws)
        
        buffer = BytesIO()
        wb.save(buffer)
    
    buffer.seek(0)
    
    st.download_button(
        "📥 Download .xlsx",
        data=buffer,
        file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_excel_download",
        use_container_width=True
    )
    
    st.caption("Formatted with styles")


def _render_csv_export(df: pd.DataFrame, include_index: bool, key_prefix: str):
    """Displays CSV export button."""
    
    st.markdown("#### 📄 CSV")
    
    csv = df.to_csv(index=include_index)
    
    st.download_button(
        "📥 Download .csv",
        data=csv,
        file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        key=f"{key_prefix}_csv_download",
        use_container_width=True
    )
    
    st.caption("Universal format")


def _render_json_export(df: pd.DataFrame, key_prefix: str):
    """Displays JSON export button."""
    
    st.markdown("#### 📋 JSON")
    
    json_data = df.to_json(orient='records', force_ascii=False, indent=2)
    
    st.download_button(
        "📥 Download .json",
        data=json_data,
        file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        key=f"{key_prefix}_json_download",
        use_container_width=True
    )
    
    st.caption("For API/web")


def render_quick_export_buttons(df: pd.DataFrame, key_prefix: str = "quick"):
    """
    Displays quick export buttons (without options).
    """
    
    if df is None or df.empty:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        buffer = excel_utils.export_dataframe_to_buffer(df, auto_format=True)
        st.download_button(
            "📥 Excel",
            data=buffer,
            file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"{key_prefix}_quick_excel",
            use_container_width=True
        )
    
    with col2:
        csv = df.to_csv(index=False)
        st.download_button(
            "📄 CSV",
            data=csv,
            file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"{key_prefix}_quick_csv",
            use_container_width=True
        )


def render_multi_sheet_export(
    sheets: Dict[str, pd.DataFrame],
    title: str = "📥 Multi-Sheet Export",
    key_prefix: str = "multi"
):
    """
    Allows exporting multiple sheets into a single Excel file.
    
    Args:
        sheets: Dict {sheet_name: DataFrame}
        title: Panel title
        key_prefix: Prefix for keys
    """
    
    if not sheets:
        st.info("No data to export")
        return
    
    st.markdown(f"### {title}")
    st.caption(f"📑 {len(sheets)} sheets available")
    
    # Select sheets to export
    selected = st.multiselect(
        "Select sheets to include",
        options=list(sheets.keys()),
        default=list(sheets.keys()),
        key=f"{key_prefix}_select_sheets"
    )
    
    if not selected:
        st.warning("Select at least one sheet")
        return
    
    # Prepare multi-sheet file
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for sheet_name in selected:
            df = sheets[sheet_name]
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Excel limit is 31 chars
    buffer.seek(0)
    
    st.download_button(
        f"📥 Download ({len(selected)} sheets)",
        data=buffer,
        file_name=f"export_multi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_multi_download",
        use_container_width=True
    )
