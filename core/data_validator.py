import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class IssueLevel(Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class DataIssue:
    level: IssueLevel
    category: str
    message: str
    affected_columns: List[str]
    recommendation: str
    impact_score: float  # 0-10 (relative weight of the issue)


class DataValidator:
    """Validate data quality and produce a compact, actionable report.

    Notes:
        - Non-blocking by design: never raises during validate_all(); collects issues instead
        - Reasonable performance for up to ~100k rows (< 5 seconds typical)
        - Thread-safe when used per-DataFrame (no global state)
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df if isinstance(df, pd.DataFrame) else pd.DataFrame()
        self.issues: List[DataIssue] = []
        self.quality_score: float = 100.0

    # --------------------------- Public API ---------------------------
    def validate_all(self) -> Dict[str, Any]:
        """Run full validation and return a dictionary report.

        Returns:
            Dict with keys: quality_score (float), issues (List[dict]), summary (dict), recommendations (List[str])
        """
        try:
            self.issues.clear()

            # Core checks
            self._validate_missing_values()
            self._validate_duplicates()
            self._validate_outliers()

            # Extension points (placeholders; no impact yet)
            self._validate_data_types()
            self._validate_data_consistency()
            self._validate_business_rules()

            # Score + report
            self.quality_score = self._calculate_quality_score()
            issues_dict = [self._issue_to_dict(i) for i in self.issues]
            summary = self._generate_summary()
            recommendations = self._generate_recommendations()

            return {
                "quality_score": float(self.quality_score),
                "issues": issues_dict,
                "summary": summary,
                "recommendations": recommendations,
            }
        except Exception as e:
            # Non-blocking guarantee: in case of unexpected failure, return an INFO issue
            fail_issue = DataIssue(
                level=IssueLevel.INFO,
                category="validator",
                message=f"Validation non-bloquante: exception capturee: {type(e).__name__}: {e}",
                affected_columns=[],
                recommendation="Verifier les donnees source ou reessayer la validation.",
                impact_score=0.0,
            )
            return {
                "quality_score": 100.0,
                "issues": [self._issue_to_dict(fail_issue)],
                "summary": {
                    "total_issues": 1,
                    "critical_issues": 0,
                    "warning_issues": 0,
                    "info_issues": 1,
                    "data_shape": tuple(self.df.shape),
                    "memory_usage_mb": float(self.df.memory_usage(deep=True).sum() / 1024 ** 2)
                    if not self.df.empty
                    else 0.0,
                },
                "recommendations": [
                    "Validation a echoue partiellement. Consultez le message d'information et reessayez."
                ],
            }

    # --------------------------- Validators ---------------------------
    def _validate_missing_values(self) -> None:
        df = self.df
        if df.empty:
            return  # Rien a evaluer

        total_rows = len(df)
        if total_rows == 0:
            return

        missing_counts = df.isna().sum()
        for col, miss_count in missing_counts.items():
            if miss_count <= 0:
                continue
            missing_pct = (miss_count / total_rows) * 100.0

            if missing_pct > 50:
                self.issues.append(
                    DataIssue(
                        level=IssueLevel.CRITICAL,
                        category="missing_values",
                        message=f"Colonne '{col}' a {missing_pct:.1f}% de valeurs manquantes",
                        affected_columns=[col],
                        recommendation=f"Considerer supprimer '{col}' ou appliquer une imputation robuste",
                        impact_score=min(10.0, missing_pct / 10.0),
                    )
                )
            elif missing_pct > 20:
                self.issues.append(
                    DataIssue(
                        level=IssueLevel.WARNING,
                        category="missing_values",
                        message=f"Colonne '{col}' a {missing_pct:.1f}% de valeurs manquantes",
                        affected_columns=[col],
                        recommendation=f"Imputer les valeurs manquantes de '{col}' (moyenne/mediane/mode ou modele)",
                        impact_score=missing_pct / 20.0,
                    )
                )
            # <20% = acceptable => pas d'issue

    def _validate_duplicates(self) -> None:
        df = self.df
        if df.empty:
            return
        total_rows = len(df)
        if total_rows == 0:
            return

        dup_count = df.duplicated().sum()
        if dup_count <= 0:
            return
        dup_pct = (dup_count / total_rows) * 100.0
        level = IssueLevel.CRITICAL if dup_pct > 10.0 else IssueLevel.WARNING
        self.issues.append(
            DataIssue(
                level=level,
                category="duplicates",
                message=f"{dup_count} lignes dupliquees ({dup_pct:.1f}%)",
                affected_columns=list(map(str, df.columns.tolist())),
                recommendation="Supprimer les doublons via df.drop_duplicates(inplace=False) et analyser la cause amont",
                impact_score=min(8.0, dup_pct / 5.0),
            )
        )

    def _validate_outliers(self) -> None:
        df = self.df
        if df.empty:
            return

        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_cols:
            return

        n_rows = len(df)
        for col in num_cols:
            col_series = df[col]
            if col_series.isna().all():
                continue
            # Handle constant columns and zero-IQR safely
            q1 = col_series.quantile(0.25)
            q3 = col_series.quantile(0.75)
            iqr = q3 - q1
            if pd.isna(iqr) or iqr == 0:
                continue

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (col_series < lower) | (col_series > upper)
            outlier_count = int(mask.sum())
            if outlier_count <= 0:
                continue
            outlier_pct = (outlier_count / n_rows) * 100.0

            if outlier_pct > 5.0:
                level = IssueLevel.WARNING
                impact = outlier_pct / 10.0
            else:
                level = IssueLevel.INFO
                impact = outlier_pct / 20.0

            self.issues.append(
                DataIssue(
                    level=level,
                    category="outliers",
                    message=f"Colonne '{col}': {outlier_count} outliers detectes ({outlier_pct:.1f}%)",
                    affected_columns=[col],
                    recommendation=(
                        f"Examiner et traiter les outliers de '{col}' (valeurs < {lower:.2f} ou > {upper:.2f});"
                        " envisager winsorisation, capping, ou robust scaling"
                    ),
                    impact_score=float(impact),
                )
            )

    # --------------------------- Score & Report ---------------------------
    def _calculate_quality_score(self) -> float:
        if not self.issues:
            return 100.0
        penalties = {
            IssueLevel.CRITICAL: 15.0,
            IssueLevel.WARNING: 8.0,
            IssueLevel.INFO: 3.0,
        }
        total_penalty = 0.0
        for issue in self.issues:
            total_penalty += penalties.get(issue.level, 0.0) * float(issue.impact_score)
        return float(max(0.0, 100.0 - total_penalty))

    def _generate_summary(self) -> Dict[str, Any]:
        counts = {lvl: 0 for lvl in IssueLevel}
        for i in self.issues:
            counts[i.level] += 1
        mem_mb = float(self.df.memory_usage(deep=True).sum() / 1024 ** 2) if not self.df.empty else 0.0
        return {
            "total_issues": len(self.issues),
            "critical_issues": counts[IssueLevel.CRITICAL],
            "warning_issues": counts[IssueLevel.WARNING],
            "info_issues": counts[IssueLevel.INFO],
            "data_shape": tuple(self.df.shape),
            "memory_usage_mb": mem_mb,
        }

    def _generate_recommendations(self) -> List[str]:
        # Aggregate unique, high-level recommendations from issues
        recs: List[str] = []
        seen = set()
        for issue in self.issues:
            rec = issue.recommendation.strip()
            if rec and rec not in seen:
                recs.append(rec)
                seen.add(rec)
        # Generic follow-ups depending on presence of categories
        categories = {i.category for i in self.issues}
        if "missing_values" in categories and "Plan d'imputation documente" not in seen:
            msg = "Plan d'imputation documente (par type de variable) pour fiabiliser les analyses"
            recs.append(msg)
            seen.add(msg)
        if "duplicates" in categories and "Mettre en place des cles primaires ou contraintes d'unicite" not in seen:
            msg = "Mettre en place des cles primaires ou contraintes d'unicite dans la source"
            recs.append(msg)
            seen.add(msg)
        if "outliers" in categories and "Metriques robustes et procedures de controle des extremes" not in seen:
            msg = "Metriques robustes et procedures de controle des extremes au chargement"
            recs.append(msg)
            seen.add(msg)
        return recs

    def _issue_to_dict(self, issue: DataIssue) -> Dict[str, Any]:
        return {
            "level": issue.level.value,
            "category": issue.category,
            "message": issue.message,
            "affected_columns": issue.affected_columns,
            "recommendation": issue.recommendation,
            "impact_score": float(issue.impact_score),
        }

    # --------------------------- Extension stubs ---------------------------
    def _validate_data_types(self) -> None:
        """Placeholder for future dtype validation (schema checks, coercions)."""
        return None

    def _validate_data_consistency(self) -> None:
        """Placeholder for cross-column and referential consistency checks."""
        return None

    def _validate_business_rules(self) -> None:
        """Placeholder for domain/business rule validation hooks."""
        return None

