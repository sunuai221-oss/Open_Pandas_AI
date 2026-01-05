"""
Tests d'intégration pour les fonctionnalités Excel dans Open Pandas-AI.
Teste le flux complet : upload → question → export.
"""

import os
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
import pandas as pd

from core import excel_utils
from core import excel_formatter
from core.prompt_builder import build_prompt, detect_excel_intention, build_excel_instructions


# ============ FIXTURES ============

@pytest.fixture
def sample_sales_data():
    """Données de ventes pour tests d'intégration."""
    return pd.DataFrame({
        'Region': ['North', 'North', 'South', 'South', 'East', 'East', 'West', 'West'],
        'Product': ['Widget', 'Gadget', 'Widget', 'Gadget', 'Widget', 'Gadget', 'Widget', 'Gadget'],
        'Quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q2'],
        'Sales': [1000, 1500, 2000, 2500, 1200, 1800, 900, 1100],
        'Profit': [100, 150, 200, 250, 120, 180, 90, 110]
    })


@pytest.fixture
def multi_sheet_workbook(sample_sales_data, tmp_path):
    """Fichier Excel avec plusieurs feuilles."""
    file_path = tmp_path / "sales_report.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        sample_sales_data.to_excel(writer, sheet_name='Sales', index=False)
        sample_sales_data.groupby('Region')['Sales'].sum().reset_index().to_excel(
            writer, sheet_name='Summary', index=False
        )
    return file_path


# ============ TESTS FLUX COMPLET ============

class TestIntegrationFlow:
    """Tests du flux complet upload → question → export."""
    
    def test_full_flow_with_single_sheet(self, sample_sales_data, tmp_path):
        """Test flux complet avec fichier mono-feuille."""
        # 1. Créer fichier Excel
        input_file = tmp_path / "input.xlsx"
        sample_sales_data.to_excel(input_file, index=False)
        
        # 2. Détecter les feuilles
        sheets = excel_utils.detect_excel_sheets(input_file)
        assert len(sheets) == 1
        
        # 3. Lire les données
        df = excel_utils.read_excel_multi_sheets(input_file, sheet_name=sheets[0])
        assert len(df) == 8
        
        # 4. Construire un prompt
        question = "Calcule le total des ventes par région"
        prompt = build_prompt(df, question)
        assert "Region" in prompt
        assert "Sales" in prompt
        
        # 5. Simuler résultat (ce que le LLM aurait produit)
        result = df.groupby('Region')['Sales'].sum().reset_index()
        
        # 6. Exporter en Excel
        output_file = tmp_path / "output.xlsx"
        excel_utils.export_dataframe_to_excel(result, output_file)
        assert output_file.exists()
        
        # 7. Vérifier le contenu exporté
        exported = pd.read_excel(output_file)
        assert len(exported) == 4  # 4 régions
        assert 'Sales' in exported.columns
    
    def test_full_flow_with_multi_sheets(self, multi_sheet_workbook):
        """Test flux complet avec fichier multi-feuilles."""
        # 1. Détecter les feuilles
        sheets = excel_utils.detect_excel_sheets(multi_sheet_workbook)
        assert len(sheets) == 2
        assert 'Sales' in sheets
        assert 'Summary' in sheets
        
        # 2. Lire toutes les feuilles
        all_sheets = excel_utils.read_excel_multi_sheets(multi_sheet_workbook, sheet_name=None)
        assert len(all_sheets) == 2
        
        # 3. Construire prompt avec info multi-sheets
        df = all_sheets['Sales']
        question = "Analyse les ventes par produit"
        prompt = build_prompt(df, question, available_sheets=list(all_sheets.keys()))
        assert "Sales" in prompt or "feuilles" in prompt.lower()
    
    def test_pivot_table_flow(self, sample_sales_data, tmp_path):
        """Test flux avec création de pivot table."""
        # 1. Détecter intention pivot
        question = "Crée un tableau croisé dynamique des ventes par région et produit"
        intentions = detect_excel_intention(question)
        assert intentions['pivot_table'] is True
        
        # 2. Construire les instructions
        instructions = build_excel_instructions(intentions)
        assert "pivot" in instructions.lower()
        
        # 3. Créer le pivot table
        pivot = excel_utils.create_pivot_table(
            sample_sales_data,
            values='Sales',
            index='Region',
            columns='Product',
            aggfunc='sum'
        )
        
        assert isinstance(pivot, pd.DataFrame)
        assert len(pivot) == 4  # 4 régions
        
        # 4. Exporter
        output_file = tmp_path / "pivot.xlsx"
        excel_utils.export_dataframe_to_excel(pivot, output_file)
        assert output_file.exists()
    
    def test_merge_files_flow(self, tmp_path):
        """Test flux avec fusion de fichiers."""
        # Créer deux fichiers à fusionner
        df1 = pd.DataFrame({
            'ID': [1, 2, 3],
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Score_Q1': [85, 90, 78]
        })
        df2 = pd.DataFrame({
            'ID': [1, 2, 3],
            'Score_Q2': [88, 92, 80]
        })
        
        file1 = tmp_path / "q1.xlsx"
        file2 = tmp_path / "q2.xlsx"
        df1.to_excel(file1, index=False)
        df2.to_excel(file2, index=False)
        
        # Détecter intention merge
        question = "Fusionner les données Q1 et Q2"
        intentions = detect_excel_intention(question)
        assert intentions['merge'] is True
        
        # Fusionner
        merged = excel_utils.merge_excel_files([file1, file2], merge_type='merge', merge_key='ID')
        
        assert len(merged) == 3
        assert 'Score_Q1' in merged.columns
        assert 'Score_Q2' in merged.columns
        
        # Exporter le résultat
        output_file = tmp_path / "merged.xlsx"
        excel_utils.export_dataframe_to_excel(merged, output_file)
        assert output_file.exists()


# ============ TESTS FORMATAGE INTÉGRÉ ============

class TestFormattingIntegration:
    """Tests d'intégration du formatage Excel."""
    
    def test_export_with_professional_formatting(self, sample_sales_data, tmp_path):
        """Test export avec formatage professionnel."""
        output_file = tmp_path / "formatted.xlsx"
        
        # Export avec formatage auto
        excel_utils.export_dataframe_to_excel(
            sample_sales_data,
            output_file,
            auto_format=True
        )
        
        # Appliquer formatage avancé
        excel_formatter.format_excel_output(output_file, {
            'auto_width': True,
            'header_style': {'bg_color': 'header_bg_dark', 'font_color': 'white'},
            'alternating_rows': True,
            'borders': 'thin'
        })
        
        assert output_file.exists()
        
        # Vérifier que le fichier peut être relu
        df_read = pd.read_excel(output_file)
        assert len(df_read) == len(sample_sales_data)
    
    def test_buffer_formatting_for_download(self, sample_sales_data):
        """Test formatage buffer pour téléchargement Streamlit."""
        # Export vers buffer
        buffer = excel_utils.export_dataframe_to_buffer(sample_sales_data, auto_format=True)
        
        # Vérifier que le buffer est valide
        assert isinstance(buffer, BytesIO)
        assert len(buffer.getvalue()) > 0
        
        # Vérifier qu'on peut le relire
        buffer.seek(0)
        df_read = pd.read_excel(buffer)
        assert len(df_read) == len(sample_sales_data)
    
    def test_conditional_formatting(self, sample_sales_data, tmp_path):
        """Test formatage conditionnel."""
        output_file = tmp_path / "conditional.xlsx"
        sample_sales_data.to_excel(output_file, index=False, engine='openpyxl')
        
        from openpyxl import load_workbook
        wb = load_workbook(output_file)
        ws = wb.active
        
        # Appliquer formatage conditionnel sur colonne Sales (D)
        excel_formatter.apply_conditional_formatting(
            ws, 'D', 'data_bar', start_row=2
        )
        
        # Appliquer échelle de couleurs sur Profit (E)
        excel_formatter.apply_conditional_formatting(
            ws, 'E', 'color_scale', start_row=2
        )
        
        wb.save(output_file)
        
        # Vérifier que le fichier est toujours valide
        df_read = pd.read_excel(output_file)
        assert len(df_read) == len(sample_sales_data)


# ============ TESTS PROMPT BUILDER ============

class TestPromptBuilderIntegration:
    """Tests d'intégration du prompt builder avec Excel."""
    
    def test_prompt_with_pivot_detection(self, sample_sales_data):
        """Test prompt avec détection de pivot table."""
        question = "Crée un pivot table des ventes par région"
        prompt = build_prompt(sample_sales_data, question)
        
        # Le prompt doit contenir des instructions pivot
        assert "pivot" in prompt.lower()
        assert "aggfunc" in prompt.lower() or "agrégation" in prompt.lower()
    
    def test_prompt_with_export_detection(self, sample_sales_data):
        """Test prompt avec détection d'export."""
        question = "Exporte les résultats en Excel"
        prompt = build_prompt(sample_sales_data, question)
        
        # Le prompt doit mentionner que l'export sera automatique
        assert "result" in prompt.lower()
    
    def test_prompt_with_groupby_detection(self, sample_sales_data):
        """Test prompt avec détection de groupby."""
        question = "Groupe les données par région et calcule la moyenne"
        intentions = detect_excel_intention(question)
        
        assert intentions['groupby'] is True
        
        instructions = build_excel_instructions(intentions)
        assert "groupby" in instructions.lower() or "group" in instructions.lower()
    
    def test_prompt_with_multi_sheets_context(self, sample_sales_data):
        """Test prompt avec contexte multi-feuilles."""
        available_sheets = ['Sales', 'Summary', 'Details']
        question = "Analyse les données de la feuille Summary"
        
        prompt = build_prompt(sample_sales_data, question, available_sheets=available_sheets)
        
        # Le prompt devrait mentionner les feuilles disponibles
        assert "Sales" in prompt or "feuilles" in prompt.lower()


# ============ TESTS SÉCURITÉ ============

class TestSecurityIntegration:
    """Tests de sécurité pour les opérations Excel."""
    
    def test_to_excel_detection(self, sample_sales_data):
        """Test détection de to_excel dans le code."""
        code_with_to_excel = "df.to_excel('output.xlsx', index=False)"
        
        should_export = excel_utils.should_export_to_excel(
            "Affiche les données",
            code_with_to_excel,
            sample_sales_data
        )
        
        assert should_export is True
    
    def test_path_validation_in_export(self, sample_sales_data, tmp_path):
        """Test que l'export est limité aux chemins valides."""
        # Export vers chemin valide (dans tmp_path)
        valid_path = tmp_path / "valid.xlsx"
        result = excel_utils.export_dataframe_to_excel(sample_sales_data, valid_path)
        assert Path(result).exists()
    
    def test_file_size_limit(self, tmp_path):
        """Test comportement avec fichiers volumineux."""
        # Créer un DataFrame assez gros
        large_df = pd.DataFrame({
            'A': range(50000),
            'B': ['data'] * 50000
        })
        
        output_file = tmp_path / "large.xlsx"
        excel_utils.export_dataframe_to_excel(large_df, output_file)
        
        # Vérifier que le fichier existe et peut être relu
        assert output_file.exists()
        df_read = pd.read_excel(output_file)
        assert len(df_read) == 50000


# ============ TESTS EDGE CASES ============

class TestEdgeCasesIntegration:
    """Tests de cas limites."""
    
    def test_empty_dataframe_flow(self, tmp_path):
        """Test flux complet avec DataFrame vide."""
        empty_df = pd.DataFrame()
        
        # Export
        output_file = tmp_path / "empty.xlsx"
        excel_utils.export_dataframe_to_excel(empty_df, output_file)
        assert output_file.exists()
        
        # Buffer
        buffer = excel_utils.export_dataframe_to_buffer(empty_df)
        assert isinstance(buffer, BytesIO)
    
    def test_special_characters_in_data(self, tmp_path):
        """Test avec caractères spéciaux."""
        df = pd.DataFrame({
            'Nom': ['Élise', 'François', '日本語', 'Müller'],
            'Description': ['Café & Thé', '<script>alert()</script>', 'Test"quotes"', "It's OK"]
        })
        
        output_file = tmp_path / "special.xlsx"
        excel_utils.export_dataframe_to_excel(df, output_file)
        
        # Vérifier que le fichier peut être relu
        df_read = pd.read_excel(output_file)
        assert df_read['Nom'].iloc[0] == 'Élise'
        assert df_read['Description'].iloc[1] == '<script>alert()</script>'
    
    def test_numeric_column_names(self, tmp_path):
        """Test avec noms de colonnes numériques."""
        df = pd.DataFrame({
            2020: [100, 200, 300],
            2021: [150, 250, 350],
            2022: [180, 280, 380]
        })
        
        output_file = tmp_path / "numeric_cols.xlsx"
        excel_utils.export_dataframe_to_excel(df, output_file)
        
        df_read = pd.read_excel(output_file)
        assert len(df_read) == 3
    
    def test_mixed_types_in_column(self, tmp_path):
        """Test avec types mixtes dans une colonne."""
        df = pd.DataFrame({
            'Mixed': [1, 'two', 3.0, None, True]
        })
        
        output_file = tmp_path / "mixed.xlsx"
        excel_utils.export_dataframe_to_excel(df, output_file)
        
        df_read = pd.read_excel(output_file)
        assert len(df_read) == 5


# ============ TESTS PERFORMANCE ============

class TestPerformanceIntegration:
    """Tests de performance basiques."""
    
    def test_large_multi_sheet_file(self, tmp_path):
        """Test lecture d'un fichier multi-feuilles volumineux."""
        file_path = tmp_path / "large_multi.xlsx"
        
        # Créer fichier avec plusieurs grandes feuilles
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for i in range(5):
                df = pd.DataFrame({
                    'Col_A': range(1000),
                    'Col_B': [f'Value_{j}' for j in range(1000)]
                })
                df.to_excel(writer, sheet_name=f'Sheet_{i}', index=False)
        
        # Lire toutes les feuilles
        result = excel_utils.read_excel_multi_sheets(file_path, sheet_name=None)
        
        assert len(result) == 5
        for sheet_name, df in result.items():
            assert len(df) == 1000
    
    def test_validation_performance(self, tmp_path):
        """Test validation d'un fichier volumineux."""
        file_path = tmp_path / "large_validation.xlsx"
        
        large_df = pd.DataFrame({
            'A': range(10000),
            'B': ['data'] * 10000
        })
        large_df.to_excel(file_path, index=False)
        
        result = excel_utils.validate_excel_file(file_path)
        
        assert result['valid'] is True
        assert result['total_rows'] == 10000

