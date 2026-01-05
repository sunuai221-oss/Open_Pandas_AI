"""
Tests d'intégration pour les composants frontend de Open Pandas-AI.
"""

import pytest
import pandas as pd
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSessionManager:
    """Tests pour le gestionnaire de session."""
    
    def test_session_manager_import(self):
        """Vérifie que le module s'importe correctement."""
        from core.session_manager import SessionManager, get_session_manager
        assert SessionManager is not None
        assert get_session_manager is not None
    
    def test_session_manager_defaults(self):
        """Vérifie les valeurs par défaut."""
        from core.session_manager import SessionManager
        # Note: Ce test nécessite un contexte Streamlit pour fonctionner pleinement
        # Ici on vérifie simplement que la classe existe
        assert hasattr(SessionManager, 'KEYS')


class TestSuggestions:
    """Tests pour le module de suggestions."""
    
    def test_smart_suggestions_import(self):
        """Vérifie que le module s'importe correctement."""
        from core.suggestions import SmartSuggestions, get_suggestions
        assert SmartSuggestions is not None
        assert get_suggestions is not None
    
    def test_suggestions_with_dataframe(self):
        """Teste la génération de suggestions avec un DataFrame."""
        from core.suggestions import SmartSuggestions
        
        df = pd.DataFrame({
            'ventes': [100, 200, 150, 300],
            'region': ['Nord', 'Sud', 'Est', 'Ouest'],
            'date': pd.date_range('2024-01-01', periods=4)
        })
        
        suggester = SmartSuggestions(df=df)
        suggestions = suggester.generate(limit=5)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
        
        # Vérifier la structure
        if suggestions:
            for s in suggestions:
                assert 'text' in s
                assert 'type' in s
    
    def test_domain_detection(self):
        """Teste la détection de domaine."""
        from core.suggestions import SmartSuggestions
        
        # DataFrame avec colonnes de ventes
        df_sales = pd.DataFrame({
            'sales': [100, 200],
            'product': ['A', 'B'],
            'revenue': [1000, 2000]
        })
        
        suggester = SmartSuggestions(df=df_sales)
        domain = suggester.detect_domain()
        assert domain == 'sales'
        
        # DataFrame avec colonnes RH
        df_hr = pd.DataFrame({
            'employee': ['John', 'Jane'],
            'salary': [50000, 60000],
            'department': ['IT', 'HR']
        })
        
        suggester = SmartSuggestions(df=df_hr)
        domain = suggester.detect_domain()
        assert domain == 'hr'


class TestMemory:
    """Tests pour le module de mémoire."""
    
    def test_memory_import(self):
        """Vérifie que le module s'importe correctement."""
        from core.memory import SessionMemory, get_memory
        assert SessionMemory is not None
        assert get_memory is not None
    
    def test_memory_methods_exist(self):
        """Vérifie que les méthodes attendues existent."""
        from core.memory import SessionMemory
        
        methods = [
            'append', 'get_last', 'get_all', 'as_string',
            'get_context_for_prompt', 'clear', 'export',
            'import_history', 'to_json', 'from_json'
        ]
        
        for method in methods:
            assert hasattr(SessionMemory, method), f"Méthode {method} manquante"


class TestPromptBuilder:
    """Tests pour le constructeur de prompts."""
    
    def test_prompt_builder_import(self):
        """Vérifie que le module s'importe correctement."""
        from core.prompt_builder import (
            build_prompt, detect_excel_intention,
            build_prompt_with_memory, detect_intent
        )
        assert build_prompt is not None
        assert detect_excel_intention is not None
        assert build_prompt_with_memory is not None
        assert detect_intent is not None
    
    def test_excel_intention_detection(self):
        """Teste la détection d'intentions Excel."""
        from core.prompt_builder import detect_excel_intention
        
        # Pivot table
        result = detect_excel_intention("créer un tableau croisé dynamique")
        assert result['pivot_table'] == True
        
        # Export
        result = detect_excel_intention("exporter en Excel")
        assert result['export_excel'] == True
        
        # Groupby
        result = detect_excel_intention("grouper par région")
        assert result['groupby'] == True
    
    def test_intent_detection(self):
        """Teste la détection d'intentions générales."""
        from core.prompt_builder import detect_intent
        
        # Visualisation
        result = detect_intent("génère un graphique des ventes")
        assert result['visualization'] == True
        
        # Statistiques
        result = detect_intent("calcule la moyenne et la médiane")
        assert result['statistics'] == True
        
        # Filtrage
        result = detect_intent("filtre les ventes supérieures à 1000")
        assert result['filtering'] == True
    
    def test_build_prompt_structure(self):
        """Teste la structure du prompt généré."""
        from core.prompt_builder import build_prompt
        
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        prompt = build_prompt(df, "question test")
        
        # Vérifier les éléments clés
        assert "expert Python" in prompt
        assert "<startCode>" in prompt
        assert "<endCode>" in prompt
        assert "Colonnes" in prompt


class TestQueries:
    """Tests pour les requêtes DB."""
    
    def test_queries_import(self):
        """Vérifie que le module s'importe correctement."""
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
    """Tests pour les utilitaires Excel."""
    
    def test_excel_utils_import(self):
        """Vérifie que le module s'importe correctement."""
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
        """Teste la création de pivot tables."""
        from core.excel_utils import create_pivot_table
        
        df = pd.DataFrame({
            'region': ['Nord', 'Nord', 'Sud', 'Sud'],
            'produit': ['A', 'B', 'A', 'B'],
            'ventes': [100, 200, 150, 250]
        })
        
        pivot = create_pivot_table(
            df,
            values='ventes',
            index='region',
            columns='produit',
            aggfunc='sum'
        )
        
        assert isinstance(pivot, pd.DataFrame)
        assert len(pivot) > 0
    
    def test_export_to_buffer(self):
        """Teste l'export vers un buffer."""
        from core.excel_utils import export_dataframe_to_buffer
        from io import BytesIO
        
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        buffer = export_dataframe_to_buffer(df)
        
        assert isinstance(buffer, BytesIO)
        assert buffer.getvalue()  # Non vide
    
    def test_should_export_detection(self):
        """Teste la détection d'intention d'export."""
        from core.excel_utils import should_export_to_excel
        
        df = pd.DataFrame({'col': [1, 2, 3]})
        
        # Devrait détecter l'intention d'export
        assert should_export_to_excel("exporter en Excel", "", df) == True
        assert should_export_to_excel("télécharger les résultats", "", df) == True
        
        # Ne devrait pas détecter
        assert should_export_to_excel("calculer la moyenne", "", df) == False


class TestDataValidator:
    """Tests pour le validateur de données."""
    
    def test_validator_import(self):
        """Vérifie que le module s'importe correctement."""
        from core.data_validator import DataValidator
        assert DataValidator is not None
    
    def test_validation_result_structure(self):
        """Teste la structure du résultat de validation."""
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
    """Tests pour le catalogue de skills."""
    
    def test_skills_catalog_import(self):
        """Vérifie que le module s'importe correctement."""
        from components.skills_catalog import SKILLS, detect_skill_from_question
        assert SKILLS is not None
        assert detect_skill_from_question is not None
    
    def test_skills_structure(self):
        """Vérifie la structure des skills."""
        from components.skills_catalog import SKILLS
        
        required_keys = ['id', 'name', 'icon', 'description', 'keywords', 'example']
        
        for skill in SKILLS:
            for key in required_keys:
                assert key in skill, f"Clé {key} manquante dans skill {skill.get('id')}"
    
    def test_skill_detection(self):
        """Teste la détection de skills depuis une question."""
        from components.skills_catalog import detect_skill_from_question
        
        # Pivot
        skills = detect_skill_from_question("créer un pivot des ventes")
        skill_ids = [s['id'] for s in skills]
        assert 'pivot' in skill_ids
        
        # Visualisation
        skills = detect_skill_from_question("génère un graphique")
        skill_ids = [s['id'] for s in skills]
        assert 'viz' in skill_ids


# Tests de régression
class TestRegression:
    """Tests de régression pour éviter les bugs connus."""
    
    def test_empty_dataframe_handling(self):
        """Teste le comportement avec un DataFrame vide."""
        from core.suggestions import SmartSuggestions
        
        df = pd.DataFrame()
        suggester = SmartSuggestions(df=df)
        suggestions = suggester.generate()
        
        # Ne devrait pas planter
        assert isinstance(suggestions, list)
    
    def test_special_characters_in_questions(self):
        """Teste les caractères spéciaux dans les questions."""
        from core.prompt_builder import build_prompt
        
        df = pd.DataFrame({'col': [1, 2]})
        
        questions = [
            "Quelle est la moyenne ?",
            "Test avec 'guillemets'",
            "Test avec \"double guillemets\"",
            "Test avec <balises>",
        ]
        
        for q in questions:
            # Ne devrait pas planter
            prompt = build_prompt(df, q)
            assert isinstance(prompt, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
