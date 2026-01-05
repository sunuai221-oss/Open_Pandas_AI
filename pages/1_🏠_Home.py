"""
Page d'accueil - Dashboard principal de Open Pandas-AI.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Open Pandas-AI - Home",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports des composants et modules
from components.sidebar import render_sidebar
from components.suggestions import render_suggestions, render_quick_actions
from components.skills_catalog import render_skill_cards
from core.session_manager import get_session_manager
from core import excel_utils
from core.smart_dictionary_detector import detect_and_load_dictionary, auto_generate_dictionary
from core.data_dictionary_manager import DataDictionaryManager
from core.dataset_adapters import normalize_df_for_example
from core.business_examples import get_business_example
from db.session import get_session
from db.models import User, UploadedFile

# Initialiser le gestionnaire de session
session = get_session_manager()

# Sidebar
render_sidebar()

# ============ HEADER ============
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1>📂 Espace de Travail</h1>
    <p style="color: var(--text-secondary);">Chargez et gérez vos données pour l'analyse IA</p>
</div>
""", unsafe_allow_html=True)

# ============ UPLOAD ZONE ============
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📂 Charger vos données")
    
    uploaded_files = st.file_uploader(
        "Glissez vos fichiers ici ou cliquez pour parcourir",
        type=["csv", "xls", "xlsx", "xlsm"],
        accept_multiple_files=True,
        help="Formats supportés: CSV, Excel (XLS, XLSX, XLSM)",
        key="home_uploader"
    )
    
    if uploaded_files:
        if len(uploaded_files) == 1:
            uploaded_file = uploaded_files[0]
            filename = uploaded_file.name
            
            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                    session.set_dataframe(df, filename)
                    df_norm = None
                    if session.business_example_key:
                        df_norm = normalize_df_for_example(df, session.business_example_key)
                    session.set_df_norm(df_norm)
                    session.set_all_sheets(None)
                elif filename.endswith((".xls", ".xlsx", ".xlsm")):
                    sheets = excel_utils.detect_excel_sheets(uploaded_file)
                    uploaded_file.seek(0)
                    
                    if len(sheets) > 1:
                        st.info(f"📊 {len(sheets)} feuilles détectées")
                        selected_sheet = st.selectbox(
                            "Sélectionner une feuille",
                            sheets,
                            key="home_sheet_selector"
                        )
                        uploaded_file.seek(0)
                        df = excel_utils.read_excel_multi_sheets(uploaded_file, sheet_name=selected_sheet)
                        session.set_selected_sheet(selected_sheet)
                        
                        if st.checkbox("Charger toutes les feuilles"):
                            uploaded_file.seek(0)
                            all_sheets = excel_utils.read_excel_multi_sheets(uploaded_file, sheet_name=None)
                            session.set_all_sheets(all_sheets)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    session.set_dataframe(df, filename)
                    df_norm = None
                    if session.business_example_key:
                        df_norm = normalize_df_for_example(df, session.business_example_key)
                    session.set_df_norm(df_norm)
                
                st.success(f"✅ **{filename}** chargé - {len(df):,} lignes × {len(df.columns)} colonnes")
                
                # ===== SYSTÈME HYBRIDE DE DICTIONNAIRE =====
                st.markdown("---")
                st.markdown("### 📚 Dictionnaire de données")
                
                # Détecter le type de dataset
                with st.spinner("🔍 Analyse du dataset..."):
                    dictionary = None
                    matched_key = None
                    confidence = 0.0

                    if session.business_example_key:
                        example = get_business_example(session.business_example_key)
                        if example:
                            dictionary = DataDictionaryManager.normalize_dictionary(example)
                            dictionary['detection'] = {
                                'method': 'manual_selection',
                                'selected_example': example.get('dataset_name', session.business_example_key),
                                'domain': example.get('domain'),
                            }
                            matched_key = session.business_example_key
                            confidence = 1.0

                    if dictionary is None:
                        matched_key, dictionary, confidence = detect_and_load_dictionary(df)

                    if df_norm is None and matched_key == "ecommerce_gnc_order":
                        df_norm = normalize_df_for_example(df, matched_key)
                        session.set_df_norm(df_norm)
                
                # Enrichir avec les statistiques
                dictionary = DataDictionaryManager.normalize_dictionary(dictionary)
                stats_df = df_norm if df_norm is not None else df
                dictionary = DataDictionaryManager.enrich_with_statistics(dictionary, stats_df)
                
                # Sauvegarder en session
                DataDictionaryManager.save_to_session(dictionary, st.session_state)
                
                # Affichage du résultat de détection
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if matched_key:
                        st.success(f"✅ **Type détecté**: {dictionary.get('dataset_name', 'Unknown')}")
                        st.info(f"Domaine: **{dictionary.get('domain')}** | Confiance: **{confidence*100:.0f}%**")
                    else:
                        st.warning("⚠️ **Type non reconnu** - Dictionnaire généré automatiquement")
                        st.info(f"Confiance: **Auto-détecte**")
                
                with col2:
                    if st.button("📖 Voir détails", key="show_dict_details"):
                        st.session_state['show_dictionary'] = True
                
                # Afficher la validation
                validation = DataDictionaryManager.validate_dictionary(dictionary, stats_df)

                if session.business_example_key:
                    missing_docs = validation['coverage']['total_columns'] - validation['coverage']['documented_columns']
                    if missing_docs > 0:
                        st.warning(f"Selection manuelle: {missing_docs} colonne(s) non documentee(s).")
                        if st.button("Completer automatiquement le dictionnaire", key="auto_merge_dictionary"):
                            auto_dictionary = auto_generate_dictionary(stats_df)
                            dictionary = DataDictionaryManager.merge_dictionaries(dictionary, auto_dictionary)
                            dictionary = DataDictionaryManager.enrich_with_statistics(dictionary, stats_df)
                            DataDictionaryManager.save_to_session(dictionary, st.session_state)
                            validation = DataDictionaryManager.validate_dictionary(dictionary, stats_df)
                            st.success("Dictionnaire complete automatiquement.")

                
                col_val1, col_val2 = st.columns(2)
                with col_val1:
                    st.metric(
                        "Couverture documentation",
                        f"{validation['coverage']['coverage_pct']:.0f}%",
                        f"{validation['coverage']['documented_columns']}/{validation['coverage']['total_columns']} colonnes"
                    )
                
                with col_val2:
                    if validation['warnings']:
                        st.warning(f"⚠️ {len(validation['warnings'])} avertissements")
                        with st.expander("Voir les avertissements"):
                            for warning in validation['warnings']:
                                st.write(f"• {warning}")
                
                # Affichage détaillé du dictionnaire
                if st.session_state.get('show_dictionary'):
                    st.markdown("---")
                    st.markdown("#### Dictionnaire complet")
                    
                    with st.expander("📋 Colonnes et descriptions", expanded=True):
                        for col_name, col_info in dictionary['columns'].items():
                            col1, col2, col3 = st.columns([2, 1, 2])
                            
                            with col1:
                                st.write(f"**{col_name}**")
                                if 'description' in col_info:
                                    st.caption(col_info['description'])
                            
                            with col2:
                                st.caption(f"Type: {col_info.get('data_type', 'unknown')}")
                            
                            with col3:
                                if 'statistics' in col_info:
                                    stats = col_info['statistics']
                                    st.caption(f"Null: {stats.get('null_pct', 0):.1f}% | Uniques: {stats.get('unique_count', 0)}")
                    
                    # Option pour enrichir manuellement
                    if st.button("✏️ Enrichir le dictionnaire", key="enrich_dict"):
                        st.session_state['enrich_mode'] = True
                
                # Mode enrichissement
                if st.session_state.get('enrich_mode'):
                    st.markdown("---")
                    st.markdown("#### ✏️ Enrichissement manuel")
                    st.info("Ajoutez des descriptions, règles métier et règles de validation")
                    
                    # Sélectionner une colonne à enrichir
                    cols_to_enrich = [c for c in dictionary['columns'].keys()]
                    selected_col = st.selectbox("Sélectionner une colonne", cols_to_enrich, key="enrich_col_select")
                    
                    col_dict = dictionary['columns'][selected_col]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_desc = st.text_area(
                            "Description",
                            value=col_dict.get('description', ''),
                            key=f"desc_{selected_col}"
                        )
                        
                        new_type = st.selectbox(
                            "Type de données",
                            ["string", "integer", "float", "datetime", "enum", "boolean"],
                            index=0,
                            key=f"type_{selected_col}"
                        )
                    
                    with col2:
                        new_rules = st.text_area(
                            "Règles métier (une par ligne)",
                            value="\n".join(col_dict.get('business_rules', [])),
                            key=f"rules_{selected_col}"
                        )
                        
                        new_validation = st.text_area(
                            "Règles de validation (une par ligne)",
                            value="\n".join(col_dict.get('validation_rules', [])),
                            key=f"validation_{selected_col}"
                        )
                    
                    if st.button("💾 Sauvegarder", key="save_enrichment"):
                        dictionary['columns'][selected_col]['description'] = new_desc
                        dictionary['columns'][selected_col]['data_type'] = new_type
                        dictionary['columns'][selected_col]['business_rules'] = [r.strip() for r in new_rules.split('\n') if r.strip()]
                        dictionary['columns'][selected_col]['validation_rules'] = [r.strip() for r in new_validation.split('\n') if r.strip()]
                        DataDictionaryManager.save_to_session(dictionary, st.session_state)
                        st.success(f"✅ Colonne '{selected_col}' enrichie")
                
                # Enregistrer en base
                with get_session() as db_session:
                    user = db_session.query(User).filter_by(session_id=session.session_id).first()
                    if not user:
                        user = User(session_id=session.session_id)
                        db_session.add(user)
                        db_session.commit()
                        db_session.refresh(user)
                    
                    session.set_user_and_file_ids(user.id, None)
                
            except Exception as e:
                st.error(f"Erreur de chargement: {e}")
        else:
            st.info(f"📁 {len(uploaded_files)} fichiers sélectionnés")
            merge_type = st.radio(
                "Comment traiter ces fichiers ?",
                ["Analyser séparément", "Fusionner (concat)"],
                horizontal=True
            )
            
            if merge_type == "Analyser séparément":
                names = [f.name for f in uploaded_files]
                selected = st.selectbox("Fichier à analyser", names)
                file = next(f for f in uploaded_files if f.name == selected)
                
                if file.name.endswith(".csv"):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                session.set_dataframe(df, selected)
            else:
                try:
                    df = excel_utils.merge_excel_files(uploaded_files, merge_type='concat')
                    session.set_dataframe(df, f"Merged_{len(uploaded_files)}_files")
                    st.success(f"✅ Fichiers fusionnés - {len(df):,} lignes")
                except Exception as e:
                    st.error(f"Erreur de fusion: {e}")

with col2:
    st.markdown("### 📊 Session")
    
    metrics = session.get_session_metrics()
    
    st.metric("Échanges", metrics['exchange_count'])
    st.metric("Durée", f"{metrics['duration_minutes']} min")
    
    if session.has_data:
        st.success(f"✅ {session.df_name}")
        if session.quality_score:
            st.metric("Qualité", f"{session.quality_score:.0f}/100")

# ============ DATA PREVIEW ============
if session.has_data:
    st.markdown("---")
    st.markdown("### 👀 Aperçu des données")
    
    df = session.df
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Lignes", f"{len(df):,}")
    with col2:
        st.metric("Colonnes", len(df.columns))
    with col3:
        st.metric("Numériques", len(df.select_dtypes(include=['number']).columns))
    with col4:
        st.metric("Catégorielles", len(df.select_dtypes(include=['object']).columns))
    
    st.dataframe(df.head(10), use_container_width=True)
    
    # Quick actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Explorer les données", use_container_width=True):
            st.switch_page("pages/2_📊_Data_Explorer.py")
    
    with col2:
        if st.button("🤖 Analyser avec l'IA", use_container_width=True, type="primary"):
            st.switch_page("pages/3_🤖_Agent.py")
    
    with col3:
        if st.button("📥 Exporter", use_container_width=True):
            buffer = excel_utils.export_dataframe_to_buffer(df)
            st.download_button(
                "Télécharger Excel",
                data=buffer,
                file_name=f"{session.df_name or 'data'}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ============ SUGGESTIONS ============
st.markdown("---")

if session.has_data:
    render_suggestions(
        df=session.df,
        user_level=session.user_level,
        limit=6,
        title="💡 Suggestions d'analyse"
    )
    
    # Vérifier si une suggestion a été cliquée
    if st.session_state.get('suggested_question'):
        st.switch_page("pages/3_🤖_Agent.py")
else:
    st.markdown("### 💡 Pour commencer")
    st.info("""
    1. **Chargez un fichier** CSV ou Excel ci-dessus
    2. **Explorez** vos données dans l'onglet Data Explorer
    3. **Posez vos questions** à l'agent IA en langage naturel
    4. **Exportez** les résultats en Excel
    """)

# ============ SKILLS ============
st.markdown("---")
st.markdown("### 🛠️ Compétences de l'agent")
render_skill_cards(limit=4)

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 20px;">
    <p>Open Pandas-AI — Analyse de données par IA</p>
    <p style="font-size: 12px;">Powered by Codestral (Mistral AI) • Pandas • Streamlit</p>
</div>
""", unsafe_allow_html=True)
