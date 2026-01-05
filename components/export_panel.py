"""
Panneau d'export multi-format pour Open Pandas-AI.
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
    title: str = "📥 Export des données",
    show_options: bool = True,
    key_prefix: str = "export"
):
    """
    Affiche le panneau d'export complet.
    
    Args:
        df: DataFrame à exporter
        title: Titre du panneau
        show_options: Afficher les options avancées
        key_prefix: Préfixe pour les clés Streamlit
    """
    
    if df is None or df.empty:
        st.info("Aucune donnée à exporter")
        return
    
    st.markdown(f"### {title}")
    
    # Info sur les données
    st.caption(f"📊 {len(df):,} lignes × {len(df.columns)} colonnes")
    
    # Options d'export
    if show_options:
        with st.expander("⚙️ Options d'export", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                sheet_name = st.text_input(
                    "Nom de la feuille",
                    value="Données",
                    key=f"{key_prefix}_sheet_name"
                )
                
                include_index = st.checkbox(
                    "Inclure l'index",
                    value=False,
                    key=f"{key_prefix}_include_index"
                )
            
            with col2:
                format_style = st.selectbox(
                    "Style de formatage",
                    options=['auto', 'professional', 'modern', 'minimal', 'none'],
                    index=0,
                    key=f"{key_prefix}_format_style"
                )
    else:
        sheet_name = "Données"
        include_index = False
        format_style = 'auto'
    
    st.markdown("---")
    
    # Boutons d'export
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
    """Affiche le bouton d'export Excel."""
    
    st.markdown("#### 📗 Excel")
    
    # Préparer le fichier
    buffer = BytesIO()
    
    # Export avec pandas
    df.to_excel(buffer, sheet_name=sheet_name, index=include_index, engine='openpyxl')
    
    # Appliquer le formatage si demandé
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
        "📥 Télécharger .xlsx",
        data=buffer,
        file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_excel_download",
        use_container_width=True
    )
    
    st.caption("Formaté avec styles")


def _render_csv_export(df: pd.DataFrame, include_index: bool, key_prefix: str):
    """Affiche le bouton d'export CSV."""
    
    st.markdown("#### 📄 CSV")
    
    csv = df.to_csv(index=include_index)
    
    st.download_button(
        "📥 Télécharger .csv",
        data=csv,
        file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        key=f"{key_prefix}_csv_download",
        use_container_width=True
    )
    
    st.caption("Format universel")


def _render_json_export(df: pd.DataFrame, key_prefix: str):
    """Affiche le bouton d'export JSON."""
    
    st.markdown("#### 📋 JSON")
    
    json_data = df.to_json(orient='records', force_ascii=False, indent=2)
    
    st.download_button(
        "📥 Télécharger .json",
        data=json_data,
        file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        key=f"{key_prefix}_json_download",
        use_container_width=True
    )
    
    st.caption("Pour API/web")


def render_quick_export_buttons(df: pd.DataFrame, key_prefix: str = "quick"):
    """
    Affiche des boutons d'export rapides (sans options).
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
    title: str = "📥 Export multi-feuilles",
    key_prefix: str = "multi"
):
    """
    Permet d'exporter plusieurs feuilles dans un seul fichier Excel.
    
    Args:
        sheets: Dict {nom_feuille: DataFrame}
        title: Titre du panneau
        key_prefix: Préfixe pour les clés
    """
    
    if not sheets:
        st.info("Aucune donnée à exporter")
        return
    
    st.markdown(f"### {title}")
    st.caption(f"📑 {len(sheets)} feuilles disponibles")
    
    # Sélection des feuilles à exporter
    selected = st.multiselect(
        "Sélectionner les feuilles à inclure",
        options=list(sheets.keys()),
        default=list(sheets.keys()),
        key=f"{key_prefix}_select_sheets"
    )
    
    if not selected:
        st.warning("Sélectionnez au moins une feuille")
        return
    
    # Préparer le fichier multi-feuilles
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for sheet_name in selected:
            df = sheets[sheet_name]
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Excel limite à 31 chars
    buffer.seek(0)
    
    st.download_button(
        f"📥 Télécharger ({len(selected)} feuilles)",
        data=buffer,
        file_name=f"export_multi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key_prefix}_multi_download",
        use_container_width=True
    )
