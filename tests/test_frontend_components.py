"""
Integration tests for Open Pandas-AI frontend components.
"""

import pytest
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSessionManager:
    """Tests for session manager."""
    
    def test_session_manager_import(self):
        """Verifies that the module imports correctly."""
        from core.session_manager import SessionManager, get_session_manager
        assert SessionManager is not None
        assert get_session_manager is not None
    
    def test_session_manager_defaults(self):
        """Verifies default values."""
        from core.session_manager import SessionManager
        # Note: This test requires a Streamlit context to function fully
        # Here we simply verify that the class exists
        assert hasattr(SessionManager, 'KEYS')


class TestSuggestions:
    """Tests for suggestions module."""
    
    def test_smart_suggestions_import(self):
        """Verifies that the module imports correctly."""
        from core.suggestions import SmartSuggestions, get_suggestions
        assert SmartSuggestions is not None
        assert get_suggestions is not None
    
    def test_suggestions_with_dataframe(self):
        """Tests suggestion generation with a DataFrame."""
        from core.suggestions import SmartSuggestions
        
        df = pd.DataFrame({
            'sales': [100, 200, 150, 300],
            'region': ['North', 'South', 'East', 'West'],
            'date': pd.date_range('2024-01-01', periods=4)
        })
        
        suggester = SmartSuggestions(df=df)
        suggestions = suggester.generate(limit=5)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
        
        # Verify structure
        if suggestions:
            for s in suggestions:
                assert 'text' in s
                assert 'type' in s
    
    def test_domain_detection(self):
        """Tests domain detection."""
        from core.suggestions import SmartSuggestions
        
        # DataFrame with sales columns
        df_sales = pd.DataFrame({
            'sales': [100, 200],
            'product': ['A', 'B'],
            'revenue': [1000, 2000]
        })
        
        suggester = SmartSuggestions(df=df_sales)
        domain = suggester.detect_domain()
        assert domain == 'sales'
        
        # DataFrame with HR columns
        df_hr = pd.DataFrame({
            'employee': ['John', 'Jane'],
            'salary': [50000, 60000],
            'department': ['IT', 'HR']
        })
        
        suggester = SmartSuggestions(df=df_hr)
        domain = suggester.detect_domain()
        assert domain == 'hr'


class TestMemory:
    """Tests for memory module."""
    
    def test_memory_import(self):
        """Verifies that the module imports correctly."""
        from core.memory import SessionMemory, get_memory
        assert SessionMemory is not None
        assert get_memory is not None
    
    def test_memory_methods_exist(self):
        """Verifies that expected methods exist."""
        from core.memory import SessionMemory
        
        methods = [
            'append', 'get_last', 'get_all', 'as_string',
            'get_context_for_prompt', 'clear', 'export',
            'import_history', 'to_json', 'from_json'
        ]
        
        for method in methods:
            assert hasattr(SessionMemory, method), f"Method {method} missing"


class TestPromptBuilder:
    """Tests for prompt builder."""
    
    def test_prompt_builder_import(self):
        """Verifies that the module imports correctly."""
        from core.prompt_builder import (
            build_prompt, detect_excel_intention,
            build_prompt_with_memory, detect_intent
        )
        assert build_prompt is not None
        assert detect_excel_intention is not None
        assert build_prompt_with_memory is not None
        assert detect_intent is not None
    
    def test_excel_intention_detection(self):
        """Tests Excel intention detection."""
        from core.prompt_builder import detect_excel_intention
        
        # Pivot table
        result = detect_excel_intention("create a pivot table")
        assert result['pivot_table'] == True
        
        # Export
        result = detect_excel_intention("export to Excel")
        assert result['export_excel'] == True
        
        # Groupby
        result = detect_excel_intention("group by region")
        assert result['groupby'] == True
    
    def test_intent_detection(self):
        """Tests general intention detection."""
        from core.prompt_builder import detect_intent
        
        # Visualization
        result = detect_intent("generate a sales chart")
        assert result['visualization'] == True
        
        # Statistics
        result = detect_intent("calculate mean and median")
        assert result['statistics'] == True
        
        # Filtering
        result = detect_intent("filter sales above 1000")
        assert result['filtering'] == True
    
    def test_build_prompt_structure(self):
        """Tests generated prompt structure."""
        from core.prompt_builder import build_prompt
        
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        prompt = build_prompt(df, "test question")
        
        # Verify key elements
        assert "expert Python" in prompt
        assert "<startCode>" in prompt
        assert "<endCode>" in prompt
        assert "Columns" in prompt


class TestQueries:
    """Tests for DB queries."""
    
    def test_queries_import(self):
        """Verifies that the module imports correctly."""
        from db.queries import (
            get_user_by_username, get_recent_files,
            get_recent_questions, search_questions,
            get_session_stats
        )
        assert get_user_by_username is not None
        assert get_recent_files is not None
        assert get_recent_questions is not None
        assert search_questions is not None
        assert get_session_stats is not None


class TestExcelUtils:
    """Tests for Excel utilities."""
    
    def test_excel_utils_import(self):
        """Verifies that the module imports correctly."""
        from core.excel_utils import (
            detect_excel_sheets, read_excel_multi_sheets,
            export_dataframe_to_buffer, create_pivot_table,
            merge_excel_files, should_export_to_excel
        )
        assert detect_excel_sheets is not None
        assert read_excel_multi_sheets is not None
        assert export_dataframe_to_buffer is not None
        assert create_pivot_table is not None
    
    def test_pivot_table_creation(self):
        """Tests pivot table creation."""
        from core.excel_utils import create_pivot_table
        
        df = pd.DataFrame({
            'region': ['North', 'North', 'South', 'South'],
            'product': ['A', 'B', 'A', 'B'],
            'sales': [100, 200, 150, 250]
        })
        
        pivot = create_pivot_table(
            df,
            values='sales',
            index='region',
            columns='product',
            aggfunc='sum'
        )
        
        assert isinstance(pivot, pd.DataFrame)
        assert len(pivot) > 0
    
    def test_export_to_buffer(self):
        """Tests export to buffer."""
        from core.excel_utils import export_dataframe_to_buffer
        from io import BytesIO
        
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        buffer = export_dataframe_to_buffer(df)
        
        assert isinstance(buffer, BytesIO)
        assert buffer.getvalue()  # Not empty
    
    def test_should_export_detection(self):
        """Tests export intention detection."""
        from core.excel_utils import should_export_to_excel
        
        df = pd.DataFrame({'col': [1, 2, 3]})
        
        # Should detect export intention
        assert should_export_to_excel("export to Excel", "", df) == True
        assert should_export_to_excel("download results", "", df) == True
        
        # Should not detect
        assert should_export_to_excel("calculate mean", "", df) == False


class TestDataValidator:
    """Tests for data validator."""
    
    def test_validator_import(self):
        """Verifies that the module imports correctly."""
        from core.data_validator import DataValidator
        assert DataValidator is not None
    
    def test_validation_result_structure(self):
        """Tests validation result structure."""
        from core.data_validator import DataValidator
        
        df = pd.DataFrame({
            'col1': [1, 2, None, 4],
            'col2': ['a', 'b', 'c', 'd']
        })
        
        validator = DataValidator(df)
        result = validator.validate_all()
        
        assert 'quality_score' in result
        assert 'issues' in result
        assert 'summary' in result
        assert isinstance(result['quality_score'], (int, float))


class TestSkillsCatalog:
    """Tests for skills catalog."""
    
    def test_skills_catalog_import(self):
        """Verifies that the module imports correctly."""
        from components.skills_catalog import SKILLS, detect_skill_from_question
        assert SKILLS is not None
        assert detect_skill_from_question is not None
    
    def test_skills_structure(self):
        """Verifies skills structure."""
        from components.skills_catalog import SKILLS
        
        required_keys = ['id', 'name', 'icon', 'description', 'keywords', 'example']
        
        for skill in SKILLS:
            for key in required_keys:
                assert key in skill, f"Key {key} missing in skill {skill.get('id')}"
    
    def test_skill_detection(self):
        """Tests skill detection from a question."""
        from components.skills_catalog import detect_skill_from_question
        
        # Pivot
        skills = detect_skill_from_question("create a sales pivot")
        skill_ids = [s['id'] for s in skills]
        assert 'pivot' in skill_ids
        
        # Visualization
        skills = detect_skill_from_question("generate a chart")
        skill_ids = [s['id'] for s in skills]
        assert 'viz' in skill_ids


# Regression tests
class TestRegression:
    """Regression tests to avoid known bugs."""
    
    def test_empty_dataframe_handling(self):
        """Tests behavior with an empty DataFrame."""
        from core.suggestions import SmartSuggestions
        
        df = pd.DataFrame()
        suggester = SmartSuggestions(df=df)
        suggestions = suggester.generate()
        
        # Should not crash
        assert isinstance(suggestions, list)
    
    def test_special_characters_in_questions(self):
        """Tests special characters in questions."""
        from core.prompt_builder import build_prompt
        
        df = pd.DataFrame({'col': [1, 2]})
        
        questions = [
            "What is the mean?",
            "Test with 'quotes'",
            "Test with \"double quotes\"",
            "Test with <tags>",
        ]
        
        for q in questions:
            # Should not crash
            prompt = build_prompt(df, q)
            assert isinstance(prompt, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
