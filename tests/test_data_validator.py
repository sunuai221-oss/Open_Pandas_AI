import pandas as pd
import numpy as np
import pytest

from core.data_validator import DataValidator, IssueLevel


class TestDataValidator:
    def test_perfect_data_quality(self):
        df = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "salary": [50000, 60000, 70000, 55000, 65000],
        })
        validator = DataValidator(df)
        result = validator.validate_all()
        assert result["quality_score"] == 100.0
        assert isinstance(result["issues"], list)
        assert len(result["issues"]) == 0

    def test_missing_values_detection(self):
        df = pd.DataFrame({
            "col_critical": [1, None, None, None, None],  # 80% missing
            "col_warning": [1, 2, None, None, 5],         # 40% missing
            "col_ok": [1, 2, 3, 4, 5],                    # 0% missing
        })
        validator = DataValidator(df)
        result = validator.validate_all()

        critical = [i for i in result["issues"] if i["level"] == "CRITICAL" and i["category"] == "missing_values"]
        warning = [i for i in result["issues"] if i["level"] == "WARNING" and i["category"] == "missing_values"]

        assert len(critical) == 1
        assert critical[0]["affected_columns"] == ["col_critical"]

        assert len(warning) == 1
        assert warning[0]["affected_columns"] == ["col_warning"]

    def test_duplicates_detection(self):
        df = pd.DataFrame({
            "a": [1, 2, 3, 1, 2],
            "b": ["x", "y", "z", "x", "y"],
        })
        validator = DataValidator(df)
        result = validator.validate_all()

        dup_issues = [i for i in result["issues"] if i["category"] == "duplicates"]
        assert len(dup_issues) == 1
        assert "2 lignes dupliquees" in dup_issues[0]["message"]
        # 2 duplicated (second occurrences) out of 5 rows = 40%
        assert dup_issues[0]["message"].endswith(")")

    def test_outliers_detection(self):
        df = pd.DataFrame({
            "normal_col": [1, 2, 3, 4, 5],
            "outlier_col": [1, 2, 3, 4, 100],  # 100 is an outlier by IQR
        })
        validator = DataValidator(df)
        result = validator.validate_all()

        outliers = [i for i in result["issues"] if i["category"] == "outliers"]
        assert len(outliers) >= 1
        cols = {i["affected_columns"][0] for i in outliers}
        assert "outlier_col" in cols

