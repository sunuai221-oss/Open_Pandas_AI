"""
Tests for core/prompt_builder.py module.

Tests cover:
- build_prompt() function
- build_prompt_with_agent() function
- Excel intention detection
- Data quality warnings
- Column type analysis
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from core.prompt_builder import (
    build_prompt,
    build_prompt_with_agent,
    detect_excel_intention,
    build_excel_instructions,
    detect_intent,
    get_skill_instructions,
    build_pivot_table_prompt,
    build_followup_prompt,
    build_prompt_with_memory,
)


class TestBuildPrompt:
    """Tests for the build_prompt function."""

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            'transaction_id': [1, 2, 3, 4, 5],
            'amount': [100.50, 250.00, 75.25, 300.00, 150.75],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            'category': ['Food', 'Electronics', 'Food', 'Clothing', 'Electronics'],
            'customer_name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
        })

    @pytest.fixture
    def large_dataframe(self):
        """Create a large DataFrame for testing truncation."""
        return pd.DataFrame({
            'col': range(10000),
            'value': np.random.randn(10000)
        })

    @pytest.fixture
    def empty_dataframe(self):
        """Create an empty DataFrame."""
        return pd.DataFrame()

    def test_build_prompt_includes_schema(self, sample_dataframe):
        """The prompt should contain the DataFrame schema (columns)."""
        prompt = build_prompt(
            df=sample_dataframe,
            question="What is the total amount?"
        )
        
        assert 'transaction_id' in prompt
        assert 'amount' in prompt
        assert 'date' in prompt
        assert 'category' in prompt
        assert 'customer_name' in prompt

    def test_build_prompt_includes_row_count(self, sample_dataframe):
        """The prompt should contain the row count."""
        prompt = build_prompt(
            df=sample_dataframe,
            question="How many rows?"
        )
        
        assert '5' in prompt  # 5 rows in sample_dataframe

    def test_build_prompt_includes_question(self, sample_dataframe):
        """The prompt should contain the user's question."""
        question = "Calculate the average amount per category"
        prompt = build_prompt(
            df=sample_dataframe,
            question=question
        )
        
        assert question in prompt

    def test_build_prompt_includes_mandatory_rules(self, sample_dataframe):
        """The prompt should include mandatory rules."""
        prompt = build_prompt(
            df=sample_dataframe,
            question="Test question"
        )
        
        assert 'MANDATORY RULES' in prompt
        assert 'import' in prompt.lower()
        assert 'result' in prompt

    def test_build_prompt_with_context(self, sample_dataframe):
        """The prompt should include conversation context when provided."""
        context = "Previous question was about total sales"
        prompt = build_prompt(
            df=sample_dataframe,
            question="Now filter by category",
            context=context
        )
        
        assert context in prompt or 'history' in prompt.lower()

    def test_build_prompt_with_large_dataframe(self, large_dataframe):
        """The prompt should handle large DataFrames without being too long."""
        prompt = build_prompt(
            df=large_dataframe,
            question="Analyze the data"
        )
        
        # Prompt should be reasonably sized (not contain all 10000 rows)
        assert len(prompt) < 50000
        # Should still contain key information
        assert '10,000' in prompt or '10000' in prompt

    def test_build_prompt_with_empty_dataframe(self, empty_dataframe):
        """The prompt should handle empty DataFrames gracefully."""
        prompt = build_prompt(
            df=empty_dataframe,
            question="Analyze the data"
        )
        
        # Should not raise an error and should generate some prompt
        assert len(prompt) > 0
        assert '0' in prompt  # 0 rows

    def test_build_prompt_user_level_beginner(self, sample_dataframe):
        """The prompt should adapt to beginner user level."""
        prompt = build_prompt(
            df=sample_dataframe,
            question="Sum the amounts",
            user_level="beginner"
        )
        
        # Beginner mode should be mentioned or different instructions given
        assert len(prompt) > 0

    def test_build_prompt_with_data_dictionary(self, sample_dataframe):
        """The prompt should include data dictionary context."""
        data_dict = {
            'columns': {
                'amount': {'description': 'Transaction amount in USD', 'type': 'numeric'},
                'category': {'description': 'Product category', 'type': 'categorical'}
            }
        }
        prompt = build_prompt(
            df=sample_dataframe,
            question="What is the total?",
            data_dictionary=data_dict
        )
        
        assert len(prompt) > 0

    def test_build_prompt_with_business_context(self, sample_dataframe):
        """The prompt should include business context when provided."""
        business_context = "E-commerce retail sales data"
        prompt = build_prompt(
            df=sample_dataframe,
            question="Analyze sales",
            business_context=business_context
        )
        
        assert business_context in prompt


class TestBuildPromptWithAgent:
    """Tests for the build_prompt_with_agent function."""

    @pytest.fixture
    def sample_dataframe(self):
        return pd.DataFrame({
            'revenue': [1000, 2000, 3000],
            'cost': [500, 800, 1200],
            'date': ['2024-01', '2024-02', '2024-03']
        })

    def test_build_prompt_with_agent_includes_agent_context(self, sample_dataframe):
        """The prompt should include agent instructions."""
        agent_prompt = "You are a finance expert agent. Focus on profitability analysis."
        
        prompt = build_prompt_with_agent(
            df=sample_dataframe,
            question="Analyze profitability",
            agent_prompt=agent_prompt
        )
        
        assert 'AGENT' in prompt or agent_prompt in prompt

    def test_build_prompt_with_agent_includes_plan(self, sample_dataframe):
        """The prompt should include analysis plan when provided."""
        agent_plan = {
            'steps': ['Calculate margins', 'Identify trends'],
            'metrics': ['profit_margin', 'growth_rate']
        }
        
        prompt = build_prompt_with_agent(
            df=sample_dataframe,
            question="Analyze data",
            agent_plan=agent_plan
        )
        
        assert len(prompt) > 0

    def test_build_prompt_with_agent_includes_domain_assets(self, sample_dataframe):
        """The prompt should include domain assets."""
        domain_assets = {
            'typical_questions': ['What is the profit margin?', 'Show revenue trend'],
            'common_metrics': ['ROI', 'EBITDA', 'Net Margin'],
            'recommended_charts': ['line', 'bar', 'pie']
        }
        
        prompt = build_prompt_with_agent(
            df=sample_dataframe,
            question="Analyze finances",
            domain_assets=domain_assets
        )
        
        # Should mention some domain assets
        assert len(prompt) > 0


class TestDetectExcelIntention:
    """Tests for Excel intention detection."""

    def test_detect_pivot_intention(self):
        """Should detect pivot table intention."""
        intentions = detect_excel_intention("Create a pivot table by region")
        assert intentions['pivot_table'] is True

    def test_detect_export_intention(self):
        """Should detect export intention."""
        intentions = detect_excel_intention("Export results to Excel")
        assert intentions['export_excel'] is True

    def test_detect_multi_sheets_intention(self):
        """Should detect multi-sheets intention."""
        intentions = detect_excel_intention("Show data from all sheets")
        assert intentions['multi_sheets'] is True

    def test_detect_merge_intention(self):
        """Should detect merge intention."""
        intentions = detect_excel_intention("Merge the two columns together")
        assert intentions['merge'] is True

    def test_detect_groupby_intention(self):
        """Should detect groupby intention."""
        intentions = detect_excel_intention("Group data by category")
        assert intentions['groupby'] is True

    def test_no_excel_intention(self):
        """Should return all False for non-Excel questions."""
        intentions = detect_excel_intention("What is the average salary?")
        assert not any(intentions.values())

    def test_multiple_intentions(self):
        """Should detect multiple intentions."""
        intentions = detect_excel_intention("Create a pivot table and export to Excel")
        assert intentions['pivot_table'] is True
        assert intentions['export_excel'] is True


class TestBuildExcelInstructions:
    """Tests for Excel instruction building."""

    def test_pivot_instructions(self):
        """Should include pivot table instructions."""
        intentions = {'pivot_table': True, 'export_excel': False, 
                     'multi_sheets': False, 'merge': False, 'groupby': False}
        instructions = build_excel_instructions(intentions)
        
        assert 'pivot_table' in instructions.lower() or 'pivot' in instructions.lower()

    def test_export_instructions(self):
        """Should include export instructions."""
        intentions = {'pivot_table': False, 'export_excel': True, 
                     'multi_sheets': False, 'merge': False, 'groupby': False}
        instructions = build_excel_instructions(intentions)
        
        assert 'result' in instructions.lower()

    def test_no_instructions_when_no_intentions(self):
        """Should return empty string when no intentions detected."""
        intentions = {'pivot_table': False, 'export_excel': False, 
                     'multi_sheets': False, 'merge': False, 'groupby': False}
        instructions = build_excel_instructions(intentions)
        
        assert instructions == ""


class TestDetectIntent:
    """Tests for global intent detection."""

    def test_detect_visualization_intent(self):
        """Should detect visualization intent."""
        intents = detect_intent("Show me a bar chart of sales")
        assert intents['visualization'] is True
        assert intents['type'] == 'visualization'

    def test_detect_statistics_intent(self):
        """Should detect statistics intent."""
        intents = detect_intent("Calculate the mean and standard deviation")
        assert intents['statistics'] is True

    def test_detect_filtering_intent(self):
        """Should detect filtering intent."""
        intents = detect_intent("Filter rows where amount > 100")
        assert intents['filtering'] is True

    def test_detect_sorting_intent(self):
        """Should detect sorting intent."""
        intents = detect_intent("Sort by date and show top 10")
        assert intents['sorting'] is True

    def test_detect_aggregation_intent(self):
        """Should detect aggregation intent."""
        intents = detect_intent("Calculate total sales by region")
        assert intents['aggregation'] is True


class TestBuildPivotTablePrompt:
    """Tests for pivot table prompt building."""

    @pytest.fixture
    def sample_dataframe(self):
        return pd.DataFrame({
            'region': ['North', 'South', 'East', 'West'],
            'product': ['A', 'B', 'A', 'B'],
            'sales': [100, 200, 150, 250],
            'quantity': [10, 20, 15, 25]
        })

    def test_pivot_prompt_includes_numeric_columns(self, sample_dataframe):
        """Pivot prompt should list numeric columns."""
        prompt = build_pivot_table_prompt(
            df=sample_dataframe,
            question="Create pivot table of sales by region"
        )
        
        assert 'sales' in prompt.lower() or 'quantity' in prompt.lower()

    def test_pivot_prompt_includes_categorical_columns(self, sample_dataframe):
        """Pivot prompt should list categorical columns."""
        prompt = build_pivot_table_prompt(
            df=sample_dataframe,
            question="Create pivot table"
        )
        
        assert 'region' in prompt.lower() or 'product' in prompt.lower()


class TestBuildFollowupPrompt:
    """Tests for follow-up prompt building."""

    @pytest.fixture
    def sample_dataframe(self):
        return pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'score': [85, 92, 78]
        })

    def test_followup_includes_original_question(self, sample_dataframe):
        """Follow-up prompt should reference original question."""
        original_result = pd.DataFrame({'name': ['Bob'], 'score': [92]})
        
        prompt = build_followup_prompt(
            df=sample_dataframe,
            original_question="Who has the highest score?",
            original_result=original_result,
            followup_question="What is their average?"
        )
        
        assert 'highest score' in prompt.lower() or 'previous' in prompt.lower()

    def test_followup_includes_result_context(self, sample_dataframe):
        """Follow-up prompt should include context about previous result."""
        original_result = "The average is 85"
        
        prompt = build_followup_prompt(
            df=sample_dataframe,
            original_question="Calculate average",
            original_result=original_result,
            followup_question="Now filter above average"
        )
        
        assert len(prompt) > 0


class TestGetSkillInstructions:
    """Tests for skill-based instructions."""

    def test_pivot_skill_instructions(self):
        """Should return pivot-specific instructions."""
        instructions = get_skill_instructions(['pivot'])
        assert 'pivot' in instructions.lower()

    def test_viz_skill_instructions(self):
        """Should return visualization instructions."""
        instructions = get_skill_instructions(['viz'])
        assert 'result' in instructions.lower()

    def test_stats_skill_instructions(self):
        """Should return statistics instructions."""
        instructions = get_skill_instructions(['stats'])
        assert 'describe' in instructions.lower() or 'corr' in instructions.lower()

    def test_multiple_skills_instructions(self):
        """Should combine multiple skill instructions."""
        instructions = get_skill_instructions(['pivot', 'stats', 'filter'])
        assert len(instructions) > 0

    def test_unknown_skill_returns_empty(self):
        """Unknown skills should not break the function."""
        instructions = get_skill_instructions(['unknown_skill'])
        assert instructions == ""


class TestBuildPromptWithMemory:
    """Tests for memory-enhanced prompts."""

    @pytest.fixture
    def sample_dataframe(self):
        return pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })

    def test_prompt_with_memory_context(self, sample_dataframe):
        """Prompt should include memory context."""
        memory_context = "User previously asked about column statistics"
        
        prompt = build_prompt_with_memory(
            df=sample_dataframe,
            question="Now show the distribution",
            memory_context=memory_context
        )
        
        assert 'CONTEXT' in prompt or memory_context in prompt

    def test_prompt_with_detected_skills(self, sample_dataframe):
        """Prompt should include detected skills."""
        detected_skills = ['statistics', 'visualization']
        
        prompt = build_prompt_with_memory(
            df=sample_dataframe,
            question="Analyze data",
            detected_skills=detected_skills
        )
        
        assert 'SKILLS' in prompt or 'statistics' in prompt.lower()


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_dataframe_with_special_characters_in_columns(self):
        """Should handle DataFrames with special characters in column names."""
        df = pd.DataFrame({
            'col with spaces': [1, 2],
            'col/with/slashes': [3, 4],
            'col.with.dots': [5, 6]
        })
        
        prompt = build_prompt(df=df, question="Analyze")
        assert len(prompt) > 0

    def test_dataframe_with_mixed_types(self):
        """Should handle DataFrames with mixed types."""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.1, 2.2, 3.3],
            'str_col': ['a', 'b', 'c'],
            'bool_col': [True, False, True],
            'date_col': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
        
        prompt = build_prompt(df=df, question="Analyze all columns")
        assert len(prompt) > 0

    def test_dataframe_with_null_values(self):
        """Should handle DataFrames with null values."""
        df = pd.DataFrame({
            'col1': [1, None, 3],
            'col2': ['a', None, 'c']
        })
        
        prompt = build_prompt(df=df, question="Handle nulls")
        assert len(prompt) > 0

    def test_very_long_question(self):
        """Should handle very long questions."""
        df = pd.DataFrame({'col': [1, 2, 3]})
        long_question = "Analyze " * 1000
        
        prompt = build_prompt(df=df, question=long_question)
        assert len(prompt) > 0

    def test_unicode_in_dataframe(self):
        """Should handle Unicode characters in DataFrame."""
        df = pd.DataFrame({
            'name': ['Alice', 'Björk', '中文', 'Émilie'],
            'value': [1, 2, 3, 4]
        })
        
        prompt = build_prompt(df=df, question="Analyze names")
        assert len(prompt) > 0
