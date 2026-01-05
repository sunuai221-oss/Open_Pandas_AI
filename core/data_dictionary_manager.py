"""
Data Dictionary Manager - Gère le cycle de vie du dictionnaire
Fusion, enrichissement, validation, stockage
"""

from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime


class DataDictionaryManager:
    """Gère les dictionnaires de données"""

    @staticmethod
    def normalize_dictionary(dictionary: Dict) -> Dict:
        """Normalize dictionary schema for prompt usage."""
        if not dictionary:
            return {}
        normalized = dictionary.copy()
        columns = dictionary.get('columns', {}) or {}
        normalized_columns = {}

        for name, info in columns.items():
            col = info.copy() if isinstance(info, dict) else {}
            description = col.get('description') or col.get('desc') or ''
            data_type = col.get('data_type') or col.get('type') or 'unknown'

            business_rules = col.get('business_rules') or []
            if isinstance(business_rules, str):
                business_rules = [business_rules]
            if not isinstance(business_rules, list):
                business_rules = []

            validation_rules = col.get('validation_rules') or col.get('validation') or []
            if isinstance(validation_rules, str):
                validation_rules = [v.strip() for v in validation_rules.split(',') if v.strip()]
            if not isinstance(validation_rules, list):
                validation_rules = []

            examples = col.get('examples') or col.get('sample_values') or []
            if not examples:
                detected_stats = col.get('detected_stats') or {}
                if isinstance(detected_stats, dict):
                    examples = detected_stats.get('sample_values') or detected_stats.get('unique_values') or []
            if not examples:
                stats = col.get('statistics') or {}
                if isinstance(stats, dict):
                    examples = stats.get('unique_values') or []
            if isinstance(examples, (str, int, float)):
                examples = [examples]

            possible_values = col.get('possible_values') or []
            if isinstance(possible_values, (str, int, float)):
                possible_values = [possible_values]

            normalized_columns[name] = {
                **col,
                'description': description,
                'data_type': data_type,
                'business_rules': business_rules,
                'validation_rules': validation_rules,
                'examples': examples,
                'possible_values': possible_values,
            }

        normalized['columns'] = normalized_columns
        return normalized
    
    @staticmethod
    def merge_dictionaries(base_dict: Dict, auto_detected: Dict) -> Dict:
        """
        Fusionne un dictionnaire prédéfini avec des infos auto-détectées.
        
        Args:
            base_dict: Dictionnaire prédéfini
            auto_detected: Colonnes auto-détectées
        
        Returns:
            Dictionnaire fusionné
        """
        merged = DataDictionaryManager.normalize_dictionary(base_dict)
        auto_detected = DataDictionaryManager.normalize_dictionary(auto_detected)
        
        # Ajouter les colonnes détectées qui ne sont pas dans le dictionnaire
        for col_name, col_info in auto_detected['columns'].items():
            if col_name not in merged['columns']:
                merged['columns'][col_name] = {
                    'description': col_info.get('description', 'Auto-detected column'),
                    'data_type': col_info.get('data_type', 'unknown'),
                    'auto_detected': True,
                    'detected_stats': col_info.get('detected_stats', {}),
                    'examples': col_info.get('examples', []),
                }
        
        return merged
    
    @staticmethod
    def enrich_with_statistics(dictionary: Dict, df: pd.DataFrame) -> Dict:
        """
        Enrichit le dictionnaire avec des statistiques du DataFrame.
        
        Args:
            dictionary: Dictionnaire de données
            df: DataFrame pour analyse
        
        Returns:
            Dictionnaire enrichi
        """
        enriched = dictionary.copy()
        enriched['enrichment'] = {
            'timestamp': datetime.now().isoformat(),
            'row_count': len(df),
            'column_count': len(df.columns),
        }
        
        enriched['statistics'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            'missing_values_pct': round((df.isna().sum().sum() / (len(df) * len(df.columns))) * 100, 2),
        }
        
        # Enrichir chaque colonne avec les stats détaillées
        for col in df.columns:
            col_clean = col.lower().replace(' ', '_')
            
            if col_clean in enriched['columns']:
                col_stats = {
                    'row_count': len(df),
                    'null_count': int(df[col].isna().sum()),
                    'null_pct': round((df[col].isna().sum() / len(df)) * 100, 2),
                    'unique_count': int(df[col].nunique()),
                    'unique_pct': round((df[col].nunique() / len(df)) * 100, 2),
                }
                
                # Statistiques numériques
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_stats['min'] = float(df[col].min())
                    col_stats['max'] = float(df[col].max())
                    col_stats['mean'] = float(df[col].mean())
                    col_stats['median'] = float(df[col].median())
                    col_stats['std'] = float(df[col].std())
                
                # Valeurs uniques pour catégories
                if col_stats['unique_count'] < 20:
                    col_stats['unique_values'] = df[col].unique().tolist()
                
                enriched['columns'][col_clean]['statistics'] = col_stats
        
        return enriched
    
    @staticmethod
    def validate_dictionary(dictionary: Dict, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valide la complétude du dictionnaire.
        
        Args:
            dictionary: Dictionnaire à valider
            df: DataFrame de référence
        
        Returns:
            Rapport de validation avec warnings et suggestions
        """
        validation = {
            'is_valid': True,
            'warnings': [],
            'suggestions': [],
            'coverage': {
                'total_columns': len(df.columns),
                'documented_columns': 0,
                'coverage_pct': 0.0
            }
        }
        
        df_columns = set(col.lower().replace(' ', '_') for col in df.columns)
        dict_columns = set(dictionary['columns'].keys())
        
        # Colonnes documentées
        validation['coverage']['documented_columns'] = len(dict_columns & df_columns)
        validation['coverage']['coverage_pct'] = round(
            (validation['coverage']['documented_columns'] / len(df_columns)) * 100, 2
        )
        
        # Warnings pour colonnes manquantes
        missing_docs = df_columns - dict_columns
        if missing_docs:
            validation['is_valid'] = False
            validation['warnings'].append(
                f"{len(missing_docs)} column(s) not documented: {', '.join(sorted(missing_docs))}"
            )
            validation['suggestions'].append(
                "Please add documentation for all columns in the dictionary"
            )
        
        # Colonnes orphelines (dans dict mais pas dans df)
        orphan_columns = dict_columns - df_columns
        if orphan_columns:
            validation['warnings'].append(
                f"{len(orphan_columns)} column(s) in dictionary not in data: {', '.join(sorted(orphan_columns))}"
            )
        
        # Warnings pour colonnes avec beaucoup de null
        for col in df.columns:
            col_clean = col.lower().replace(' ', '_')
            null_pct = (df[col].isna().sum() / len(df)) * 100
            
            if null_pct > 50:
                validation['warnings'].append(
                    f"Column '{col}' has {null_pct:.1f}% missing values"
                )
                validation['suggestions'].append(
                    f"Consider if '{col}' is necessary or investigate missing data in '{col}'"
                )
        
        # Check pour descriptions
        for col, col_dict in dictionary['columns'].items():
            if 'description' not in col_dict or not col_dict['description']:
                validation['warnings'].append(f"Column '{col}' lacks description")
                validation['suggestions'].append(f"Add meaningful description for '{col}'")
        
        return validation
    
    @staticmethod
    def get_column_rules(dictionary: Dict, column_name: str) -> Dict[str, Any]:
        """Récupère les règles pour une colonne spécifique"""
        dictionary = DataDictionaryManager.normalize_dictionary(dictionary)
        col_clean = column_name.lower().replace(' ', '_')
        columns = dictionary.get('columns', {})
        
        if col_clean not in columns:
            return {}
        
        col_dict = columns[col_clean]
        rules = {
            'name': column_name,
            'clean_name': col_clean,
            'description': col_dict.get('description', 'N/A'),
            'data_type': col_dict.get('data_type', 'unknown'),
            'possible_values': col_dict.get('possible_values', []),
            'validation_rules': col_dict.get('validation_rules', []),
            'business_rules': col_dict.get('business_rules', []),
            'examples': col_dict.get('examples', []),
        }
        
        if 'statistics' in col_dict:
            rules['statistics'] = col_dict['statistics']
        
        return rules
    
    @staticmethod
    def save_to_session(dictionary: Dict, session_state) -> None:
        """Sauvegarde le dictionnaire dans la session Streamlit"""
        session_state['data_dictionary'] = dictionary
        session_state['dictionary_loaded_at'] = datetime.now().isoformat()
    
    @staticmethod
    def load_from_session(session_state) -> Optional[Dict]:
        """Charge le dictionnaire de la session Streamlit"""
        return session_state.get('data_dictionary')
    
    @staticmethod
    def export_to_dict(dictionary: Dict) -> Dict:
        """Exporte le dictionnaire en format dict (pour sauvegarde)"""
        return {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'dataset_name': dictionary.get('dataset_name'),
                'domain': dictionary.get('domain'),
            },
            'columns': dictionary.get('columns', {}),
            'detection': dictionary.get('detection', {}),
        }
    
    @staticmethod
    def create_prompt_context(dictionary: Dict) -> str:
        """Crée un contexte pour le prompt LLM basé sur le dictionnaire"""
        dictionary = DataDictionaryManager.normalize_dictionary(dictionary)
        lines = []
        
        lines.append("## Data Dictionary")
        if 'dataset_name' in dictionary:
            lines.append(f"**Dataset**: {dictionary['dataset_name']}")
        
        if 'domain' in dictionary:
            lines.append(f"**Domain**: {dictionary['domain']}")
        
        lines.append("\n### Available Columns:")

        columns = dictionary.get('columns', {})
        if not columns:
            return "## Data Dictionary\n(No columns available)"

        
        for col_name, col_info in columns.items():
            lines.append(f"\n- **{col_name}**")
            if 'description' in col_info:
                lines.append(f"  - Description: {col_info['description']}")
            
            if 'data_type' in col_info:
                lines.append(f"  - Type: {col_info['data_type']}")
            
            if 'possible_values' in col_info:
                values = col_info['possible_values']
                if isinstance(values, list) and len(values) > 0:
                    lines.append(f"  - Possible values: {', '.join(str(v) for v in values[:5])}")
            
            if 'business_rules' in col_info:
                rules = col_info['business_rules']
                if rules:
                    for rule in rules[:3]:
                        lines.append(f"  - Rule: {rule}")
            
            if 'validation_rules' in col_info:
                rules = col_info['validation_rules']
                if rules:
                    lines.append(f"  - Validation: {', '.join(str(r) for r in rules[:3])}")

            if 'examples' in col_info:
                examples = col_info['examples']
                if examples:
                    lines.append(f"  - Examples: {', '.join(str(e) for e in examples[:3])}")

            # Ajouter les stats si disponibles
            if 'statistics' in col_info:
                stats = col_info['statistics']
                if 'null_pct' in stats:
                    lines.append(f"  - Missing: {stats['null_pct']:.1f}%")
                if 'unique_count' in stats:
                    lines.append(f"  - Unique values: {stats['unique_count']}")
        
        return "\n".join(lines)


def create_dictionary_context_for_prompt(dictionary: Dict) -> str:
    """Fonction de convenience pour créer le contexte du dictionnaire"""
    return DataDictionaryManager.create_prompt_context(dictionary)