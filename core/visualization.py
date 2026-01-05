import os
import pandas as pd
from core.llm import call_llm

def build_visualization_prompt(result_df: pd.DataFrame, question: str) -> str:
    """
    Crée un prompt pour demander au LLM de générer du code matplotlib adapté au résultat.
    """
    preview = result_df.head(5).to_string(index=False)
    columns = ', '.join(result_df.columns)
    types = ', '.join(f"{col} ({str(dtype)})" for col, dtype in result_df.dtypes.items())
    prompt = (
        "Tu es un expert Python et en visualisation de données avec matplotlib.\n"
        "Voici un DataFrame nommé 'result_df' :\n"
        f"{preview}\n"
        f"Colonnes : {columns}\n"
        f"Types des colonnes : {types}\n\n"
        "Ta tâche : Écris UNIQUEMENT du code Python entre <startCode> et <endCode>, "
        "sans aucun import, qui produit une visualisation adaptée (camembert, histogramme, barres, etc.) "
        "basée sur la question ci-dessous. Utilise plt.figure() puis plt.savefig('result.png').\n"
        "N’ajoute aucun commentaire ni phrase explicative en dehors du code.\n"
        f"Question : {question}\n"
        "N’utilise que la variable 'result_df'."
    )
    return prompt

def generate_and_run_visualization(result_df: pd.DataFrame, question: str, llm_provider: str = None, llm_model: str = None):
    if os.getenv("ALLOW_UNSAFE_VISUALIZATION", "false").lower() != "true":
        return None, "Visualization is disabled (set ALLOW_UNSAFE_VISUALIZATION=true to override)."

    """
    Orchestration complète :
    - Prompt LLM pour le code de visualisation
    - Exécution du code (génère result.png)
    - Retourne le chemin si succès, sinon None + erreur
    """
    import matplotlib.pyplot as plt
    import io
    prompt = build_visualization_prompt(result_df, question)
    code = call_llm(prompt, model=llm_model, provider=llm_provider)
    # Optionnel : afficher le code généré pour debug
    # print("Code de visualisation généré :\n", code)

    # On force 'plt' et 'result_df' dans le scope d'exécution
    local_vars = {"result_df": result_df, "plt": plt}
    try:
        # Efface l'ancien graphique s’il existe
        if os.path.exists('result.png'):
            os.remove('result.png')
        exec(code, {}, local_vars)
        if os.path.exists('result.png'):
            return 'result.png', code  # On retourne aussi le code pour transparence
        else:
            return None, f"Le code a été exécuté, mais aucun graphique n’a été généré.\nCode généré :\n{code}"
    except Exception as e:
        return None, f"Erreur lors de l’exécution du code de visualisation : {e}\nCode généré :\n{code}"
