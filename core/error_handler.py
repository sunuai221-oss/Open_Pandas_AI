from core.llm import call_llm

def handle_code_error(prompt: str, code: str, error_msg: str, max_retries=2, llm_provider: str = None, llm_model: str = None):
    """
    En cas d'erreur à l’exécution, re-prompt Codestral en expliquant l’erreur.
    Réessaie jusqu’à max_retries fois.
    """
    for _ in range(max_retries):
        correction_prompt = (
            f"Le code suivant a échoué à l'exécution sur un DataFrame pandas nommé 'df' :\n"
            f"<startCode>\n{code}\n<endCode>\n"
            f"L’erreur obtenue était : {error_msg}\n"
            "Merci de corriger uniquement le code Python entre <startCode> et <endCode> pour qu’il fonctionne correctement. "
            "N’ajoute aucune explication, seulement le code corrigé."
        )
        # On concatène au prompt initial pour garder le contexte du DataFrame
        new_code = call_llm(prompt + "\n" + correction_prompt, model=llm_model, provider=llm_provider)
        yield new_code  # Generator pattern pour chaque correction produite
        code = new_code  # Pour le prochain tour
