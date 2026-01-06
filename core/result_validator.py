"""
Validateur et enrichisseur de résultats analytiques.
Analyse les résultats et suggère des améliorations ou interprétations.
"""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class ResultValidator:
    """Valide, enrichit et prépare les résultats pour affichage."""
    
    @staticmethod
    def validate_and_enrich(
        result: Any,
        question: str,
        original_df: pd.DataFrame,
        detected_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Valide et enrichit un résultat d'exécution.
        
        Args:
            result: Résultat brut de l'exécution
            question: Question originale
            original_df: DataFrame original
            detected_skills: Skills détectées (optionnel)
        
        Returns:
            Dict avec:
            - 'formatted': Résultat formaté pour affichage
            - 'warnings': Liste des avertissements
            - 'context': Contexte statistique
            - 'suggestions': Questions de suivi suggérées
            - 'quality_score': Score de qualité 0-100
        """
        validation = {
            'formatted': result,
            'warnings': [],
            'context': {},
            'suggestions': [],
            'quality_score': 100,
            'interpretation': ""
        }
        
        # Pas de résultat
        if result is None:
            validation['warnings'].append("⚠️ Aucun résultat produit")
            validation['quality_score'] = 0
            return validation
        
        # String d'erreur
        if isinstance(result, str) and result.startswith("Erreur"):
            validation['warnings'].append(f"❌ {result}")
            validation['quality_score'] = 0
            return validation
        
        # DataFrame
        if isinstance(result, pd.DataFrame):
            return ResultValidator._validate_dataframe(
                result, question, original_df, validation
            )
        
        # Nombre
        if isinstance(result, (int, float, np.integer, np.floating)):
            return ResultValidator._validate_numeric(
                result, question, original_df, validation
            )
        
        # Série
        if isinstance(result, pd.Series):
            return ResultValidator._validate_series(
                result, question, original_df, validation
            )
        
        # List/tuple
        if isinstance(result, (list, tuple)):
            return ResultValidator._validate_list(
                result, question, validation
            )
        
        # Autre (dict, bool, etc.)
        validation['formatted'] = str(result)
        return validation
    
    @staticmethod
    def _validate_dataframe(
        df: pd.DataFrame,
        question: str,
        original_df: pd.DataFrame,
        validation: Dict
    ) -> Dict:
        """Valide un résultat DataFrame."""
        
        # Taille
        if len(df) == 0:
            validation['warnings'].append(
                "⚠️ Le résultat est vide. Vérifiez les filtres appliqués."
            )
            validation['quality_score'] -= 30
        elif len(df) > 1000:
            validation['warnings'].append(
                f"ℹ️ Résultat très grand ({len(df):,} lignes). "
                "Considérez un filtre ou un groupby."
            )
            validation['quality_score'] -= 10
        
        # Colonnes
        validation['context']['shape'] = f"{len(df):,} lignes × {len(df.columns)} colonnes"
        validation['context']['columns'] = list(df.columns)
        
        # Valeurs manquantes
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            missing_pct = (missing_counts.sum() / (len(df) * len(df.columns))) * 100
            validation['warnings'].append(
                f"⚠️ {missing_counts.sum()} valeurs manquantes ({missing_pct:.1f}%) "
                f"dans {(missing_counts > 0).sum()} colonne(s)"
            )
            if missing_pct > 20:
                validation['quality_score'] -= 20
            else:
                validation['quality_score'] -= 5
        
        # Doublons
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / len(df)) * 100
            validation['warnings'].append(
                f"ℹ️ {duplicates} doublons détectés ({dup_pct:.1f}%)"
            )
            validation['quality_score'] -= 5
        
        # Statistiques pour colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            validation['context']['numeric_stats'] = {}
            for col in numeric_cols[:5]:  # Max 5 colonnes
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    stats = {
                        'mean': float(col_data.mean()),
                        'std': float(col_data.std()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                    }
                    # Détection d'anomalies (3-sigma)
                    if stats['std'] > 0:
                        lower = stats['mean'] - 3 * stats['std']
                        upper = stats['mean'] + 3 * stats['std']
                        outliers = len(col_data[(col_data < lower) | (col_data > upper)])
                        if outliers > 0:
                            validation['warnings'].append(
                                f"⚠️ {outliers} valeur(s) aberrante(s) dans {col}"
                            )
                            validation['quality_score'] -= 5
                    validation['context']['numeric_stats'][col] = stats
        
        # Interprétation
        validation['interpretation'] = ResultValidator._interpret_dataframe(df, question)
        
        # Suggestions de suivi
        validation['suggestions'] = ResultValidator._suggest_followups_df(df, question)
        # Format pour affichage (resultat complet)
        validation['formatted'] = df
        validation['context']['full_rows'] = len(df)
        
        return validation
    
    @staticmethod
    def _validate_numeric(
        value: float,
        question: str,
        original_df: pd.DataFrame,
        validation: Dict
    ) -> Dict:
        """Valide un résultat numérique."""
        
        validation['formatted'] = round(value, 4) if isinstance(value, float) else value
        validation['context']['type'] = 'numeric'
        validation['context']['value'] = validation['formatted']
        
        # Interprétation contextuelle
        if 'pourcentage' in question.lower() or '%' in question:
            if 0 <= value <= 100:
                validation['context']['formatted_display'] = f"{value:.1f}%"
                validation['interpretation'] = f"Le résultat est **{value:.1f}%**"
            else:
                validation['warnings'].append(
                    f"⚠️ La valeur {value} sort de la plage 0-100 pour un pourcentage"
                )
                validation['quality_score'] -= 10
        
        # Détection de valeurs suspectes
        if value == 0:
            validation['context']['note'] = "Résultat nul - vérifiez les données"
        elif np.isinf(value):
            validation['warnings'].append("❌ Résultat infini (division par zéro ?)")
            validation['quality_score'] -= 30
        elif np.isnan(value):
            validation['warnings'].append("❌ Résultat invalide (NaN)")
            validation['quality_score'] -= 30
        
        return validation
    
    @staticmethod
    def _validate_series(
        series: pd.Series,
        question: str,
        original_df: pd.DataFrame,
        validation: Dict
    ) -> Dict:
        """Valide un résultat Série."""
        
        validation['context']['type'] = 'series'
        validation['context']['name'] = series.name or "Sans nom"
        validation['context']['length'] = len(series)
        
        # Statistiques de base
        if series.dtype in [np.float64, np.int64, int, float]:
            validation['context']['stats'] = {
                'mean': float(series.mean()),
                'std': float(series.std()),
                'min': float(series.min()),
                'max': float(series.max()),
            }
        
        # Valeurs manquantes
        missing = series.isnull().sum()
        if missing > 0:
            validation['warnings'].append(
                f"⚠️ {missing} valeur(s) manquante(s) sur {len(series)}"
            )
            validation['quality_score'] -= 10
        
        # Conversion pour affichage (max 20 éléments)
        validation['formatted'] = series.head(20)
        if len(series) > 20:
            validation['context']['full_length'] = len(series)
        
        return validation
    
    @staticmethod
    def _validate_list(
        items: list,
        question: str,
        validation: Dict
    ) -> Dict:
        """Valide un résultat Liste."""
        
        validation['context']['type'] = 'list'
        validation['context']['length'] = len(items)
        
        if len(items) == 0:
            validation['warnings'].append("⚠️ Liste vide")
            validation['quality_score'] -= 20
        elif len(items) > 1000:
            validation['warnings'].append(
                f"ℹ️ Liste très longue ({len(items)} éléments)"
            )
            validation['quality_score'] -= 5
        # Format pour affichage (resultat complet)
        display = ', '.join(str(i)[:50] for i in items[:10])
        if len(items) > 10:
            display += f", ... ({len(items)} total)"
        validation['formatted'] = display
        
        return validation
    
    @staticmethod
    def _interpret_dataframe(df: pd.DataFrame, question: str) -> str:
        """Génère une interprétation du DataFrame."""
        
        if len(df) == 0:
            return "Aucun résultat correspondant à votre critère."
        
        if len(df) == 1:
            return f"Résultat unique trouvé: **{len(df.columns)} colonne(s)**"
        
        # Identifier le type de résultat
        if 'top' in question.lower() or 'meilleur' in question.lower():
            return f"Top résultats: **{len(df)} lignes** classées"
        
        if 'grouper' in question.lower() or 'groupe' in question.lower():
            return f"Groupements: **{len(df)} groupe(s)** identifié(s)"
        
        if 'filtr' in question.lower():
            return f"Filtrage appliqué: **{len(df):,} lignes** sélectionnées"
        
        if len(df) > 100:
            return f"Résultat large: **{len(df):,} lignes** à explorer"
        
        return f"Résultat: **{len(df)} lignes** × **{len(df.columns)} colonnes**"
    
    @staticmethod
    def _suggest_followups_df(df: pd.DataFrame, question: str) -> List[str]:
        """Suggère des questions de suivi."""
        
        suggestions = []
        
        if len(df) > 0:
            # Suggérer un tri
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                col = numeric_cols[0]
                suggestions.append(f"📊 Trier par {col} (ascendant/descendant)")
            
            # Suggérer un groupby si pas déjà fait
            if 'grouper' not in question.lower() and 'groupe' not in question.lower():
                cat_cols = df.select_dtypes(include=['object']).columns.tolist()
                if cat_cols:
                    col = cat_cols[0]
                    suggestions.append(f"🔀 Regrouper par {col}")
            
            # Suggérer des statistiques
            if numeric_cols:
                col = numeric_cols[0]
                suggestions.append(f"📈 Voir les statistiques de {col}")
        
        return suggestions[:3]  # Max 3 suggestions
