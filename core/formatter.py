import pandas as pd
from typing import Any, Dict, Optional, List
from core.result_validator import ResultValidator


def format_result(result: Any, question: str = "", original_df: pd.DataFrame = None) -> Any:
    """
    Mise en forme automatique du résultat pour Streamlit avec validation enrichie.
    
    Args:
        result: Résultat brut de l'exécution
        question: Question originale (optionnel)
        original_df: DataFrame original pour contexte (optionnel)
    
    Returns:
        Résultat formaté prêt pour affichage
    """
    # Si pas de contexte, fallback simple
    if question == "" and original_df is None:
        return _format_simple(result)
    
    # Validation et enrichissement
    if original_df is not None and question:
        validated = ResultValidator.validate_and_enrich(
            result=result,
            question=question,
            original_df=original_df
        )
        return validated['formatted']
    
    return _format_simple(result)


def format_result_with_validation(
    result: Any,
    question: str,
    original_df: pd.DataFrame,
    detected_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Formate ET valide le résultat, retournant tous les métadonnées.
    
    Args:
        result: Résultat brut
        question: Question originale
        original_df: DataFrame source
        detected_skills: Skills détectées
    
    Returns:
        Dict complet avec formatage, warnings, contexte, suggestions
    """
    return ResultValidator.validate_and_enrich(
        result=result,
        question=question,
        original_df=original_df,
        detected_skills=detected_skills
    )


def _format_simple(result: Any) -> Any:
    """Formatage simple sans contexte."""
    
    if isinstance(result, pd.DataFrame):
        return result
    elif isinstance(result, (list, tuple)):
        return ', '.join(map(str, result))
    elif result is None:
        return "Aucun résultat à afficher."
    elif isinstance(result, float):
        return round(result, 4)
    else:
        return str(result)
