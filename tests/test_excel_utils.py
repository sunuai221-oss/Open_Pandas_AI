"""
Unit tests for core/excel_utils.py module
"""

import os
import tempfile
from io import BytesIO
from pathlib import Path

import pytest
import pandas as pd

from core import excel_utils


# ============ FIXTURES ============

@pytest.fixture
def sample_dataframe():
    """Simple test DataFrame."""
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'City': ['Paris', 'London', 'Berlin', 'Madrid'],
        'Sales': [1000, 1500, 2000, 1200]
    })


@pytest.fixture
def sample_excel_file(sample_dataframe, tmp_path):
    """Creates a temporary Excel file with a single sheet."""
    file_path = tmp_path / "test_single.xlsx"
    sample_dataframe.to_excel(file_path, index=False, sheet_name="Sheet1")
    return file_path


@pytest.fixture
def multi_sheet_excel_file(sample_dataframe, tmp_path):
    """Creates a temporary Excel file with multiple sheets."""
    file_path = tmp_path / "test_multi.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        sample_dataframe.to_excel(writer, sheet_name='Sales', index=False)
        sample_dataframe.head(2).to_excel(writer, sheet_name='Summary', index=False)
        sample_dataframe.tail(2).to_excel(writer, sheet_name='Details', index=False)
    return file_path


@pytest.fixture
def sample_csv_file(sample_dataframe, tmp_path):
    """Creates a temporary CSV file."""
    file_path = tmp_path / "test.csv"
    sample_dataframe.to_csv(file_path, index=False)
    return file_path


# ============ TESTS DETECT_EXCEL_SHEETS ============

class TestDetectExcelSheets:
    
    def test_single_sheet(self, sample_excel_file):
        """Test detection of a file with a single sheet."""
        sheets = excel_utils.detect_excel_sheets(sample_excel_file)
        assert len(sheets) == 1
        assert sheets[0] == "Sheet1"
    
    def test_multiple_sheets(self, multi_sheet_excel_file):
        """Test detection of a file with multiple sheets."""
        sheets = excel_utils.detect_excel_sheets(multi_sheet_excel_file)
        assert len(sheets) == 3
        assert "Sales" in sheets
        assert "Summary" in sheets
        assert "Details" in sheets
    
    def test_with_buffer(self, sample_dataframe):
        """Test detection from a BytesIO buffer."""
        buffer = BytesIO()
        sample_dataframe.to_excel(buffer, index=False)
        buffer.seek(0)
        
        sheets = excel_utils.detect_excel_sheets(buffer)
        assert len(sheets) == 1
    
    def test_invalid_file(self, tmp_path):
        """Test with an invalid file."""
        invalid_file = tmp_path / "invalid.xlsx"
        invalid_file.write_text("not an excel file")
        
        with pytest.raises(ValueError):
            excel_utils.detect_excel_sheets(invalid_file)


# ============ TESTS READ_EXCEL_MULTI_SHEETS ============

class TestReadExcelMultiSheets:
    
    def test_read_specific_sheet(self, multi_sheet_excel_file):
        """Test reading a specific sheet."""
        df = excel_utils.read_excel_multi_sheets(multi_sheet_excel_file, sheet_name="Sales")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4
    
    def test_read_all_sheets(self, multi_sheet_excel_file):
        """Test reading all sheets."""
        result = excel_utils.read_excel_multi_sheets(multi_sheet_excel_file, sheet_name=None)
        assert isinstance(result, dict)
        assert len(result) == 3
        assert "Sales" in result
        assert "Summary" in result
        assert "Details" in result
        assert isinstance(result["Sales"], pd.DataFrame)
    
    def test_read_single_sheet_file(self, sample_excel_file):
        """Test reading a single-sheet file."""
        df = excel_utils.read_excel_multi_sheets(sample_excel_file, sheet_name="Sheet1")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4
    
    def test_with_buffer(self, sample_dataframe):
        """Test reading from a buffer."""
        buffer = BytesIO()
        sample_dataframe.to_excel(buffer, index=False, sheet_name="Data")
        buffer.seek(0)
        
        df = excel_utils.read_excel_multi_sheets(buffer, sheet_name="Data")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4


# ============ TESTS EXPORT_DATAFRAME_TO_EXCEL ============

class TestExportDataframeToExcel:
    
    def test_basic_export(self, sample_dataframe, tmp_path):
        """Test basic export."""
        output_path = tmp_path / "output.xlsx"
        result_path = excel_utils.export_dataframe_to_excel(sample_dataframe, output_path)
        
        assert Path(result_path).exists()
        
        # Verify content
        df_read = pd.read_excel(result_path)
        assert len(df_read) == len(sample_dataframe)
        assert list(df_read.columns) == list(sample_dataframe.columns)
    
    def test_export_with_custom_sheet_name(self, sample_dataframe, tmp_path):
        """Test export with custom sheet name."""
        output_path = tmp_path / "output_custom.xlsx"
        excel_utils.export_dataframe_to_excel(
            sample_dataframe, 
            output_path, 
            sheet_name="MyData"
        )
        
        sheets = excel_utils.detect_excel_sheets(output_path)
        assert "MyData" in sheets
    
    def test_export_with_formatting(self, sample_dataframe, tmp_path):
        """Test export with automatic formatting."""
        output_path = tmp_path / "output_formatted.xlsx"
        excel_utils.export_dataframe_to_excel(
            sample_dataframe, 
            output_path, 
            auto_format=True
        )
        
        assert Path(output_path).exists()


# ============ TESTS EXPORT_DATAFRAME_TO_BUFFER ============

class TestExportDataframeToBuffer:
    
    def test_basic_buffer_export(self, sample_dataframe):
        """Test export to buffer."""
        buffer = excel_utils.export_dataframe_to_buffer(sample_dataframe)
        
        assert isinstance(buffer, BytesIO)
        assert buffer.getvalue()  # Not empty
        
        # Verify we can reread
        buffer.seek(0)
        df_read = pd.read_excel(buffer)
        assert len(df_read) == len(sample_dataframe)
    
    def test_buffer_with_custom_sheet(self, sample_dataframe):
        """Test buffer export with custom sheet name."""
        buffer = excel_utils.export_dataframe_to_buffer(
            sample_dataframe, 
            sheet_name="Results"
        )
        
        buffer.seek(0)
        sheets = excel_utils.detect_excel_sheets(buffer)
        assert "Results" in sheets


# ============ TESTS CREATE_PIVOT_TABLE ============

class TestCreatePivotTable:
    
    def test_simple_pivot(self, sample_dataframe):
        """Test creation of a simple pivot table."""
        pivot = excel_utils.create_pivot_table(
            sample_dataframe,
            values='Sales',
            index='City',
            aggfunc='sum'
        )
        
        assert isinstance(pivot, pd.DataFrame)
        assert 'City' in pivot.columns
        assert len(pivot) == 4  # 4 unique cities
    
    def test_pivot_with_columns(self):
        """Test pivot table with columns."""
        df = pd.DataFrame({
            'Region': ['North', 'North', 'South', 'South'],
            'Product': ['A', 'B', 'A', 'B'],
            'Sales': [100, 200, 150, 250]
        })
        
        pivot = excel_utils.create_pivot_table(
            df,
            values='Sales',
            index='Region',
            columns='Product',
            aggfunc='sum'
        )
        
        assert isinstance(pivot, pd.DataFrame)
    
    def test_pivot_invalid_column(self, sample_dataframe):
        """Test pivot with non-existent column."""
        with pytest.raises(ValueError):
            excel_utils.create_pivot_table(
                sample_dataframe,
                values='InvalidColumn',
                index='City',
                aggfunc='sum'
            )


# ============ TESTS MERGE_EXCEL_FILES ============

class TestMergeExcelFiles:
    
    def test_concat_merge(self, sample_excel_file, tmp_path):
        """Test merge by concatenation."""
        # Create a second file
        df2 = pd.DataFrame({
            'Name': ['Eve', 'Frank'],
            'Age': [22, 45],
            'City': ['Rome', 'Tokyo'],
            'Sales': [800, 3000]
        })
        file2 = tmp_path / "test2.xlsx"
        df2.to_excel(file2, index=False)
        
        merged = excel_utils.merge_excel_files(
            [sample_excel_file, file2],
            merge_type='concat'
        )
        
        assert isinstance(merged, pd.DataFrame)
        assert len(merged) == 6  # 4 + 2
    
    def test_merge_on_key(self, tmp_path):
        """Test merge on common column."""
        df1 = pd.DataFrame({'ID': [1, 2, 3], 'Name': ['A', 'B', 'C']})
        df2 = pd.DataFrame({'ID': [1, 2, 3], 'Value': [100, 200, 300]})
        
        file1 = tmp_path / "df1.xlsx"
        file2 = tmp_path / "df2.xlsx"
        df1.to_excel(file1, index=False)
        df2.to_excel(file2, index=False)
        
        merged = excel_utils.merge_excel_files(
            [file1, file2],
            merge_type='merge',
            merge_key='ID'
        )
        
        assert isinstance(merged, pd.DataFrame)
        assert 'Name' in merged.columns
        assert 'Value' in merged.columns
        assert len(merged) == 3
    
    def test_merge_csv_and_excel(self, sample_csv_file, sample_excel_file):
        """Test merge of mixed CSV and Excel files."""
        merged = excel_utils.merge_excel_files(
            [sample_csv_file, sample_excel_file],
            merge_type='concat'
        )
        
        assert isinstance(merged, pd.DataFrame)
        assert len(merged) == 8  # 4 + 4
    
    def test_merge_empty_list(self):
        """Test merge with empty list."""
        with pytest.raises(ValueError):
            excel_utils.merge_excel_files([])


# ============ TESTS VALIDATE_EXCEL_FILE ============

class TestValidateExcelFile:
    
    def test_valid_file(self, sample_excel_file):
        """Test validation of a valid file."""
        result = excel_utils.validate_excel_file(sample_excel_file)
        
        assert result['valid'] is True
        assert result['sheet_count'] == 1
        assert result['total_rows'] == 4
        assert result['error'] is None
    
    def test_multi_sheet_validation(self, multi_sheet_excel_file):
        """Test validation of a multi-sheet file."""
        result = excel_utils.validate_excel_file(multi_sheet_excel_file)
        
        assert result['valid'] is True
        assert result['sheet_count'] == 3
        assert result['total_rows'] == 8  # 4 + 2 + 2
    
    def test_invalid_file(self, tmp_path):
        """Test validation of an invalid file."""
        invalid_file = tmp_path / "invalid.xlsx"
        invalid_file.write_text("not excel")
        
        result = excel_utils.validate_excel_file(invalid_file)
        
        assert result['valid'] is False
        assert result['error'] is not None


# ============ TESTS SHOULD_EXPORT_TO_EXCEL ============

class TestShouldExportToExcel:
    
    def test_export_keyword_in_question(self, sample_dataframe):
        """Test detection of export keyword in question."""
        assert excel_utils.should_export_to_excel(
            "Export results to Excel",
            "",
            sample_dataframe
        ) is True
    
    def test_download_keyword(self, sample_dataframe):
        """Test detection of download keyword."""
        assert excel_utils.should_export_to_excel(
            "Download the data",
            "",
            sample_dataframe
        ) is True
    
    def test_to_excel_in_code(self, sample_dataframe):
        """Test detection of to_excel in code."""
        assert excel_utils.should_export_to_excel(
            "Display results",
            "df.to_excel('output.xlsx')",
            sample_dataframe
        ) is True
    
    def test_no_export_needed(self, sample_dataframe):
        """Test without export intention."""
        assert excel_utils.should_export_to_excel(
            "Calculate the mean",
            "result = df['Sales'].mean()",
            sample_dataframe
        ) is False
    
    def test_non_dataframe_result(self):
        """Test with non-DataFrame result."""
        assert excel_utils.should_export_to_excel(
            "Export to Excel",
            "",
            "string result"
        ) is False


# ============ TESTS EDGE CASES ============

class TestEdgeCases:
    
    def test_empty_dataframe_export(self, tmp_path):
        """Test export of an empty DataFrame."""
        empty_df = pd.DataFrame()
        output_path = tmp_path / "empty.xlsx"
        
        result_path = excel_utils.export_dataframe_to_excel(empty_df, output_path)
        assert Path(result_path).exists()
    
    def test_unicode_content(self, tmp_path):
        """Test with Unicode content."""
        df = pd.DataFrame({
            'Name': ['Élise', 'François', '日本語'],
            'City': ['Zürich', 'München', '東京']
        })
        
        output_path = tmp_path / "unicode.xlsx"
        excel_utils.export_dataframe_to_excel(df, output_path)
        
        df_read = pd.read_excel(output_path)
        assert df_read['Name'].iloc[0] == 'Élise'
        assert df_read['City'].iloc[2] == '東京'
    
    def test_large_dataframe(self, tmp_path):
        """Test with a large DataFrame."""
        large_df = pd.DataFrame({
            'A': range(10000),
            'B': ['value'] * 10000
        })
        
        output_path = tmp_path / "large.xlsx"
        excel_utils.export_dataframe_to_excel(large_df, output_path)
        
        df_read = pd.read_excel(output_path)
        assert len(df_read) == 10000

