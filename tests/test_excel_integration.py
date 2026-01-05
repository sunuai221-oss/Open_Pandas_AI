"""
Integration tests for Excel features in Open Pandas-AI.
Tests the complete flow: upload → question → export.
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
    """Sales data for integration tests."""
    return pd.DataFrame({
        'Region': ['North', 'North', 'South', 'South', 'East', 'East', 'West', 'West'],
        'Product': ['Widget', 'Gadget', 'Widget', 'Gadget', 'Widget', 'Gadget', 'Widget', 'Gadget'],
        'Quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q2'],
        'Sales': [1000, 1500, 2000, 2500, 1200, 1800, 900, 1100],
        'Profit': [100, 150, 200, 250, 120, 180, 90, 110]
    })


@pytest.fixture
def multi_sheet_workbook(sample_sales_data, tmp_path):
    """Excel file with multiple sheets."""
    file_path = tmp_path / "sales_report.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        sample_sales_data.to_excel(writer, sheet_name='Sales', index=False)
        sample_sales_data.groupby('Region')['Sales'].sum().reset_index().to_excel(
            writer, sheet_name='Summary', index=False
        )
    return file_path


# ============ COMPLETE FLOW TESTS ============

class TestIntegrationFlow:
    """Tests for complete flow: upload → question → export."""
    
    def test_full_flow_with_single_sheet(self, sample_sales_data, tmp_path):
        """Test complete flow with single-sheet file."""
        # 1. Create Excel file
        input_file = tmp_path / "input.xlsx"
        sample_sales_data.to_excel(input_file, index=False)
        
        # 2. Detect sheets
        sheets = excel_utils.detect_excel_sheets(input_file)
        assert len(sheets) == 1
        
        # 3. Read data
        df = excel_utils.read_excel_multi_sheets(input_file, sheet_name=sheets[0])
        assert len(df) == 8
        
        # 4. Build prompt
        question = "Calculate total sales by region"
        prompt = build_prompt(df, question)
        assert "Region" in prompt
        assert "Sales" in prompt
        
        # 5. Simulate result (what LLM would have produced)
        result = df.groupby('Region')['Sales'].sum().reset_index()
        
        # 6. Export to Excel
        output_file = tmp_path / "output.xlsx"
        excel_utils.export_dataframe_to_excel(result, output_file)
        assert output_file.exists()
        
        # 7. Verify exported content
        exported = pd.read_excel(output_file)
        assert len(exported) == 4  # 4 regions
        assert 'Sales' in exported.columns
    
    def test_full_flow_with_multi_sheets(self, multi_sheet_workbook):
        """Test complete flow with multi-sheet file."""
        # 1. Detect sheets
        sheets = excel_utils.detect_excel_sheets(multi_sheet_workbook)
        assert len(sheets) == 2
        assert 'Sales' in sheets
        assert 'Summary' in sheets
        
        # 2. Read all sheets
        all_sheets = excel_utils.read_excel_multi_sheets(multi_sheet_workbook, sheet_name=None)
        assert len(all_sheets) == 2
        
        # 3. Build prompt with multi-sheet info
        df = all_sheets['Sales']
        question = "Analyze sales by product"
        prompt = build_prompt(df, question, available_sheets=list(all_sheets.keys()))
        assert "Sales" in prompt or "sheets" in prompt.lower()
    
    def test_pivot_table_flow(self, sample_sales_data, tmp_path):
        """Test flow with pivot table creation."""
        # 1. Detect pivot intention
        question = "Create a pivot table of sales by region and product"
        intentions = detect_excel_intention(question)
        assert intentions['pivot_table'] is True
        
        # 2. Build instructions
        instructions = build_excel_instructions(intentions)
        assert "pivot" in instructions.lower()
        
        # 3. Create pivot table
        pivot = excel_utils.create_pivot_table(
            sample_sales_data,
            values='Sales',
            index='Region',
            columns='Product',
            aggfunc='sum'
        )
        
        assert isinstance(pivot, pd.DataFrame)
        assert len(pivot) == 4  # 4 regions
        
        # 4. Export
        output_file = tmp_path / "pivot.xlsx"
        excel_utils.export_dataframe_to_excel(pivot, output_file)
        assert output_file.exists()
    
    def test_merge_files_flow(self, tmp_path):
        """Test flow with file merging."""
        # Create two files to merge
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
        
        # Detect merge intention
        question = "Merge Q1 and Q2 data"
        intentions = detect_excel_intention(question)
        assert intentions['merge'] is True
        
        # Merge
        merged = excel_utils.merge_excel_files([file1, file2], merge_type='merge', merge_key='ID')
        
        assert len(merged) == 3
        assert 'Score_Q1' in merged.columns
        assert 'Score_Q2' in merged.columns
        
        # Export result
        output_file = tmp_path / "merged.xlsx"
        excel_utils.export_dataframe_to_excel(merged, output_file)
        assert output_file.exists()


# ============ FORMATTING INTEGRATION TESTS ============

class TestFormattingIntegration:
    """Excel formatting integration tests."""
    
    def test_export_with_professional_formatting(self, sample_sales_data, tmp_path):
        """Test export with professional formatting."""
        output_file = tmp_path / "formatted.xlsx"
        
        # Export with auto formatting
        excel_utils.export_dataframe_to_excel(
            sample_sales_data,
            output_file,
            auto_format=True
        )
        
        # Apply advanced formatting
        excel_formatter.format_excel_output(output_file, {
            'auto_width': True,
            'header_style': {'bg_color': 'header_bg_dark', 'font_color': 'white'},
            'alternating_rows': True,
            'borders': 'thin'
        })
        
        assert output_file.exists()
        
        # Verify file can be reread
        df_read = pd.read_excel(output_file)
        assert len(df_read) == len(sample_sales_data)
    
    def test_buffer_formatting_for_download(self, sample_sales_data):
        """Test buffer formatting for Streamlit download."""
        # Export to buffer
        buffer = excel_utils.export_dataframe_to_buffer(sample_sales_data, auto_format=True)
        
        # Verify buffer is valid
        assert isinstance(buffer, BytesIO)
        assert len(buffer.getvalue()) > 0
        
        # Verify we can reread it
        buffer.seek(0)
        df_read = pd.read_excel(buffer)
        assert len(df_read) == len(sample_sales_data)
    
    def test_conditional_formatting(self, sample_sales_data, tmp_path):
        """Test conditional formatting."""
        output_file = tmp_path / "conditional.xlsx"
        sample_sales_data.to_excel(output_file, index=False, engine='openpyxl')
        
        from openpyxl import load_workbook
        wb = load_workbook(output_file)
        ws = wb.active
        
        # Apply conditional formatting on Sales column (D)
        excel_formatter.apply_conditional_formatting(
            ws, 'D', 'data_bar', start_row=2
        )
        
        # Apply color scale on Profit column (E)
        excel_formatter.apply_conditional_formatting(
            ws, 'E', 'color_scale', start_row=2
        )
        
        wb.save(output_file)
        
        # Verify file is still valid
        df_read = pd.read_excel(output_file)
        assert len(df_read) == len(sample_sales_data)


# ============ PROMPT BUILDER TESTS ============

class TestPromptBuilderIntegration:
    """Prompt builder integration tests with Excel."""
    
    def test_prompt_with_pivot_detection(self, sample_sales_data):
        """Test prompt with pivot table detection."""
        question = "Create a pivot table of sales by region"
        prompt = build_prompt(sample_sales_data, question)
        
        # Prompt must contain pivot instructions
        assert "pivot" in prompt.lower()
        assert "aggfunc" in prompt.lower() or "aggregation" in prompt.lower()
    
    def test_prompt_with_export_detection(self, sample_sales_data):
        """Test prompt with export detection."""
        question = "Export results to Excel"
        prompt = build_prompt(sample_sales_data, question)
        
        # Prompt must mention that export will be automatic
        assert "result" in prompt.lower()
    
    def test_prompt_with_groupby_detection(self, sample_sales_data):
        """Test prompt with groupby detection."""
        question = "Group data by region and calculate the mean"
        intentions = detect_excel_intention(question)
        
        assert intentions['groupby'] is True
        
        instructions = build_excel_instructions(intentions)
        assert "groupby" in instructions.lower() or "group" in instructions.lower()
    
    def test_prompt_with_multi_sheets_context(self, sample_sales_data):
        """Test prompt with multi-sheet context."""
        available_sheets = ['Sales', 'Summary', 'Details']
        question = "Analyze data from the Summary sheet"
        
        prompt = build_prompt(sample_sales_data, question, available_sheets=available_sheets)
        
        # Prompt should mention available sheets
        assert "Sales" in prompt or "sheets" in prompt.lower()


# ============ SECURITY TESTS ============

class TestSecurityIntegration:
    """Security tests for Excel operations."""
    
    def test_to_excel_detection(self, sample_sales_data):
        """Test detection of to_excel in code."""
        code_with_to_excel = "df.to_excel('output.xlsx', index=False)"
        
        should_export = excel_utils.should_export_to_excel(
            "Display data",
            code_with_to_excel,
            sample_sales_data
        )
        
        assert should_export is True
    
    def test_path_validation_in_export(self, sample_sales_data, tmp_path):
        """Test that export is limited to valid paths."""
        # Export to valid path (in tmp_path)
        valid_path = tmp_path / "valid.xlsx"
        result = excel_utils.export_dataframe_to_excel(sample_sales_data, valid_path)
        assert Path(result).exists()
    
    def test_file_size_limit(self, tmp_path):
        """Test behavior with large files."""
        # Create a fairly large DataFrame
        large_df = pd.DataFrame({
            'A': range(50000),
            'B': ['data'] * 50000
        })
        
        output_file = tmp_path / "large.xlsx"
        excel_utils.export_dataframe_to_excel(large_df, output_file)
        
        # Verify file exists and can be reread
        assert output_file.exists()
        df_read = pd.read_excel(output_file)
        assert len(df_read) == 50000


# ============ EDGE CASES TESTS ============

class TestEdgeCasesIntegration:
    """Edge cases tests."""
    
    def test_empty_dataframe_flow(self, tmp_path):
        """Test complete flow with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        # Export
        output_file = tmp_path / "empty.xlsx"
        excel_utils.export_dataframe_to_excel(empty_df, output_file)
        assert output_file.exists()
        
        # Buffer
        buffer = excel_utils.export_dataframe_to_buffer(empty_df)
        assert isinstance(buffer, BytesIO)
    
    def test_special_characters_in_data(self, tmp_path):
        """Test with special characters."""
        df = pd.DataFrame({
            'Name': ['Élise', 'François', '日本語', 'Müller'],
            'Description': ['Café & Thé', '<script>alert()</script>', 'Test"quotes"', "It's OK"]
        })
        
        output_file = tmp_path / "special.xlsx"
        excel_utils.export_dataframe_to_excel(df, output_file)
        
        # Verify file can be reread
        df_read = pd.read_excel(output_file)
        assert df_read['Name'].iloc[0] == 'Élise'
        assert df_read['Description'].iloc[1] == '<script>alert()</script>'
    
    def test_numeric_column_names(self, tmp_path):
        """Test with numeric column names."""
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
        """Test with mixed types in a column."""
        df = pd.DataFrame({
            'Mixed': [1, 'two', 3.0, None, True]
        })
        
        output_file = tmp_path / "mixed.xlsx"
        excel_utils.export_dataframe_to_excel(df, output_file)
        
        df_read = pd.read_excel(output_file)
        assert len(df_read) == 5


# ============ PERFORMANCE TESTS ============

class TestPerformanceIntegration:
    """Basic performance tests."""
    
    def test_large_multi_sheet_file(self, tmp_path):
        """Test reading a large multi-sheet file."""
        file_path = tmp_path / "large_multi.xlsx"
        
        # Create file with multiple large sheets
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for i in range(5):
                df = pd.DataFrame({
                    'Col_A': range(1000),
                    'Col_B': [f'Value_{j}' for j in range(1000)]
                })
                df.to_excel(writer, sheet_name=f'Sheet_{i}', index=False)
        
        # Read all sheets
        result = excel_utils.read_excel_multi_sheets(file_path, sheet_name=None)
        
        assert len(result) == 5
        for sheet_name, df in result.items():
            assert len(df) == 1000
    
    def test_validation_performance(self, tmp_path):
        """Test validation of a large file."""
        file_path = tmp_path / "large_validation.xlsx"
        
        large_df = pd.DataFrame({
            'A': range(10000),
            'B': ['data'] * 10000
        })
        large_df.to_excel(file_path, index=False)
        
        result = excel_utils.validate_excel_file(file_path)
        
        assert result['valid'] is True
        assert result['total_rows'] == 10000

