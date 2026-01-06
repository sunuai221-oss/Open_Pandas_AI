"""
Smart Dictionary Detector - Détection intelligente du type de dataset
Essaie de matcher avec les exemples métiers, sinon détection automatique
"""

from typing import Dict, Tuple, Optional, Any
import pandas as pd
from difflib import SequenceMatcher
from core.business_examples import get_all_business_examples, normalize_column_name


class SmartDictionaryDetector:
    """Détecte intelligemment le type de dataset et son dictionnaire"""
    
    # Seuil de correspondance (%)
    MATCH_THRESHOLD = 0.70
    
    @classmethod
    def detect(cls, df: pd.DataFrame) -> Tuple[Optional[str], Dict[str, Any], float]:
        """
        Détecte le type de dataset et trouve le meilleur match.
        
        Args:
            df: DataFrame à analyser
        
        Returns:
            Tuple (matched_example_key, dictionary, confidence_score)
            - matched_example_key: Clé de l'exemple trouvé ou None
            - dictionary: Dictionnaire complet (prédéfini ou généré)
            - confidence: Score de confiance 0-1
        """
        # Analyser les colonnes
        df_columns = set(normalize_column_name(col) for col in df.columns)
        df_column_info = cls._analyze_columns(df)
        
        # Chercher les matches
        best_match = None
        best_score = 0
        best_example_key = None
        
        for example_key, example in get_all_business_examples().items():
            columns = example.get("columns", {})
            example_columns = {normalize_column_name(c) for c in columns.keys()}
            
            # Calculer la similarité
            score = cls._calculate_similarity(df_columns, example_columns)
            
            if score > best_score:
                best_score = score
                best_match = example
                best_example_key = example_key
        
        # Décider: utiliser le match ou générer automatiquement
        if best_score >= cls.MATCH_THRESHOLD:
            # Match trouvé: enrichir avec les infos du DataFrame
            dictionary = cls._enrich_matched_dictionary(best_match, df_column_info)
            return best_example_key, dictionary, best_score
        else:
            # Pas de match: générer automatiquement
            dictionary = cls._auto_generate_dictionary(df_column_info)
            return None, dictionary, 0.0
    
    @staticmethod
    def _analyze_columns(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyse les caractéristiques de chaque colonne"""
        analysis = {}
        
        for col in df.columns:
            col_data = df[col].dropna()
            col_lower = str(col).lower()
            col_clean = normalize_column_name(col)
            
            # Déterminer le type plus précisément
            is_numeric = pd.api.types.is_numeric_dtype(df[col])
            is_datetime = pd.api.types.is_datetime64_any_dtype(df[col])
            is_bool = df[col].dtype == 'bool'
            
            # Pour colonnes object, tenter de détecter le vrai type
            if not is_numeric and not is_datetime and not is_bool:
                # Vérifier si contient des dates
                if len(col_data) > 0:
                    sample = col_data.iloc[0]
                    if isinstance(sample, str):
                        # Chercher patterns de date
                        is_date_like = any(
                            pd.to_datetime(col_data[:10], errors='coerce').notna().sum() > 7
                            for _ in [None]
                        )
                        if not is_date_like:
                            is_numeric = False
            
            analysis[col] = {
                'original_name': col,
                'clean_name': col_clean,
                'dtype': str(df[col].dtype),
                'null_count': df[col].isna().sum(),
                'null_pct': (df[col].isna().sum() / len(df)) * 100,
                'unique_count': df[col].nunique(),
                'unique_pct': (df[col].nunique() / len(df)) * 100,
                'sample_values': col_data.unique()[:5].tolist() if len(col_data) > 0 else [],
                'is_categorical': not is_numeric and df[col].nunique() < len(df) * 0.1,  # < 10% unique
                'is_numeric': is_numeric,
                'is_datetime': is_datetime,
                'is_bool': is_bool,
                # Tester si vraiment numérique en essayant une conversion
                'can_be_numeric': False
            }
            
            # Vérifier si convertible en numérique
            if not is_numeric and len(col_data) > 0:
                try:
                    pd.to_numeric(col_data[:10], errors='coerce').notna().sum()
                    analysis[col]['can_be_numeric'] = pd.to_numeric(col_data[:10], errors='coerce').notna().sum() >= 8
                except:
                    pass
        
        return analysis
    
    @staticmethod
    def _calculate_similarity(df_columns: set, example_columns: set) -> float:
        """Calcule le score de similarité entre deux ensembles de colonnes"""
        if not example_columns:
            return 0.0
        
        # Intersection normalisée
        matches = len(df_columns & example_columns)
        total = len(example_columns)
        
        # Score basique
        base_score = matches / total if total > 0 else 0.0
        
        # Bonus si colonnes supplémentaires (peut être naturel)
        extra_columns = len(df_columns - example_columns)
        
        # Pénalité légère si trop de colonnes manquent
        if matches < total * 0.5:
            return 0.0  # Trop peu de matches
        
        return base_score
    
    @classmethod
    def _enrich_matched_dictionary(cls, matched_example: Dict, df_column_info: Dict) -> Dict:
        """Enrichit le dictionnaire prédéfini avec les infos du DataFrame"""
        enriched = matched_example.copy()
        enriched['detection'] = {
            'method': 'matched_to_business_example',
            'matched_example': enriched.get('dataset_name'),
            'confidence': 'high'
        }
        
        # Enrichir chaque colonne avec les stats du DataFrame
        columns = enriched.get('columns', {}) or {}
        norm_map = {normalize_column_name(k): k for k in columns}
        for col_name, col_info in df_column_info.items():
            clean_col = normalize_column_name(col_name)
            dict_key = norm_map.get(clean_col)
            if dict_key:
                enriched['columns'][dict_key]['detected_stats'] = {
                    'null_pct': col_info['null_pct'],
                    'unique_count': col_info['unique_count'],
                    'sample_values': col_info['sample_values'],
                }
        return enriched
    
    @staticmethod
    def _auto_generate_dictionary(df_column_info: Dict) -> Dict:
        """Génère automatiquement un dictionnaire pour un DataFrame inconnu"""
        dictionary = {
            'detection': {
                'method': 'auto_generated',
                'matched_example': None,
                'confidence': 'low'
            },
            'dataset_name': 'Auto-detected Dataset',
            'domain': 'unknown',
            'description': 'Dataset automatically analyzed. Please enrich this dictionary.',
            'columns': {}
        }
        
        for col_name, col_info in df_column_info.items():
            clean_col = col_info['clean_name']
            
            # Générer description basée sur le nom
            description = SmartDictionaryDetector._generate_description(col_name, col_info)
            
            # Déterminer le type de données
            if col_info['is_numeric']:
                data_type = 'float' if 'float' in col_info['dtype'] else 'integer'
                possible_values = None
            elif col_info['is_categorical']:
                data_type = 'enum'
                possible_values = list(df_column_info[col_name]['sample_values'])
            elif col_info['is_datetime']:
                data_type = 'datetime'
                possible_values = None
            elif col_info.get('can_be_numeric', False):
                # Convertible en numérique
                data_type = 'float'
                possible_values = None
            else:
                data_type = 'string'
                possible_values = None
            
            # Construire la colonne
            column_dict = {
                'description': description,
                'data_type': data_type,
                'detected_stats': {
                    'null_pct': round(col_info['null_pct'], 2),
                    'unique_count': col_info['unique_count'],
                    'sample_values': col_info['sample_values'],
                },
                'examples': col_info['sample_values'],
            }
            
            if possible_values:
                column_dict['possible_values'] = possible_values
            
            dictionary['columns'][clean_col] = column_dict
        
        return dictionary
    
    @staticmethod
    def _generate_description(col_name: str, col_info: Dict) -> str:
        """Génère une description basée sur le nom et les stats"""
        col_lower = col_name.lower()
        
        # Patterns courants
        patterns = {
            'id': 'Unique identifier',
            'email': 'Email address',
            'phone': 'Phone number',
            'date': 'Date/Time information',
            'name': 'Name or description',
            'price': 'Monetary value',
            'amount': 'Monetary amount',
            'quantity': 'Numeric count',
            'status': 'Current status or state',
            'category': 'Category or classification',
            'count': 'Number of items',
            'total': 'Total sum',
            'average': 'Average or mean value',
            'percentage': 'Percentage value',
        }
        
        for pattern, desc in patterns.items():
            if pattern in col_lower:
                return f"{desc} ({col_name})"
        
        # Description par défaut
        if col_info['is_categorical']:
            return f"Categorical variable: {col_name}"
        elif col_info['is_numeric']:
            return f"Numeric value: {col_name}"
        elif col_info['is_datetime']:
            return f"Date/Time: {col_name}"
        else:
            return f"Text field: {col_name}"


def detect_and_load_dictionary(df: pd.DataFrame) -> Tuple[Optional[str], Dict[str, Any], float]:
    """
    Fonction de convenience pour détecter et charger le dictionnaire.
    
    Args:
        df: DataFrame uploadé
    
    Returns:
        Tuple (matched_example_key, dictionary, confidence)
    """
    return SmartDictionaryDetector.detect(df)


def auto_generate_dictionary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a dictionary for a DataFrame without matching to examples."""
    df_column_info = SmartDictionaryDetector._analyze_columns(df)
    return SmartDictionaryDetector._auto_generate_dictionary(df_column_info)
