from core.llm import call_llm
import pandas as pd
from datetime import datetime

def build_auto_comment_prompt(
    df: pd.DataFrame = None,
    result: pd.DataFrame = None,
    additional_context: str = "",
    lang: str = "fr"
) -> str:
    """
    Génère un prompt pour une analyse professionnelle intelligente du résultat.
    Différencie numérique, catégoriel, texte : adapte la demande selon le type de colonne.
    Supporte le français et l’anglais.
    """

    context = ""
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    if df is not None:
        max_cols_preview = 8
        preview_cols = df.columns[:max_cols_preview]
        df_preview = df.loc[:, preview_cols].head(5)
        context += (
            f"#### Données d'origine (aperçu partiel)\n"
            f"{df_preview.to_markdown(index=False)}\n"
            f"- Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes\n"
            f"- Colonnes et types : {', '.join([f'{c} ({t})' for c, t in zip(df.columns, df.dtypes)])}\n"
            f"- Valeurs manquantes (top 5) : {dict(df.isnull().sum().sort_values(ascending=False).head(5))}\n"
        )
        numeric = df.select_dtypes(include='number')
        if not numeric.empty:
            stats = numeric.describe().T
            outlier_report = ""
            for col in stats.index:
                mini, maxi, mean, std = stats.loc[col, ['min', 'max', 'mean', 'std']]
                if abs(maxi - mean) > 2 * std or abs(mini - mean) > 2 * std:
                    outlier_report += f"Colonne {col} : possible valeur atypique (min={mini}, max={maxi}, moyenne={mean:.1f}, écart-type={std:.1f})\n"
            context += f"- Statistiques principales :\n{stats.to_markdown()}\n"
            if outlier_report:
                context += f"- Alerte sur valeurs atypiques détectées :\n{outlier_report}"
        cats = [c for c in df.select_dtypes(include=['object', 'category']).columns if df[c].nunique() <= 10]
        for c in cats:
            context += f"- {c} (valeurs uniques) : {df[c].unique().tolist()}\n"

    # ---------- Analyse Résultat ----------
    if result is not None:
        if isinstance(result, pd.DataFrame) and not result.empty:
            max_cols_res = 8
            preview_cols_r = result.columns[:max_cols_res]
            result_preview = result.loc[:, preview_cols_r].head(5)
            context += (
                "\n#### Résultat à commenter (aperçu partiel)\n"
                f"{result_preview.to_markdown(index=False)}\n"
                f"- Dimensions : {result.shape[0]} lignes × {result.shape[1]} colonnes\n"
                f"- Colonnes : {', '.join(str(c) for c in result.columns)}\n"
            )
            numeric_r = result.select_dtypes(include='number')
            if not numeric_r.empty:
                stats_r = numeric_r.describe().T
                context += f"- Statistiques principales (résultat) :\n{stats_r.to_markdown()}\n"
            # Ajout : aperçu catégories pour les colonnes non numériques avec peu de modalités
            cats_r = [c for c in result.select_dtypes(include=['object', 'category']).columns if result[c].nunique() <= 10]
            for c in cats_r:
                context += f"- {c} (valeurs uniques dans le résultat) : {result[c].unique().tolist()}\n"
        else:
            context += f"\n#### Résultat à commenter\n{str(result)}\n"

    # ---------- Ajout du contexte additionnel ----------
    if additional_context:
        context += f"\n#### Contexte additionnel\n{additional_context}\n"

    # ---------- Prompt différencié par type ----------
    if lang == "en":
        prompt = (
            f"You are an expert Data Scientist and AI Consultant (analysis date: {now_str}).\n"
            "For each column in the result:\n"
            "- If numeric: give mean, median, min, max, distribution, missing values, outliers, possible correlations.\n"
            "- If categorical: show number of categories, frequencies for top values, rare values, missing rate.\n"
            "- If text: summarize uniqueness, min/max/average length, duplication rate, repetitive or suspicious patterns, possible data improvement suggestions.\n"
            "- If image or link column: indicate missing or duplicate items.\n"
            "Never report statistics that do not make sense for the column type. End each column with a practical recommendation if relevant.\n"
            f"{context}\n"
            "Generate ONLY the detailed analytical text."
        )
    else:
        prompt = (
            f"Tu es un expert Data Scientist et Consultant IA (date analyse : {now_str}).\n"
            "Pour chaque colonne du résultat :\n"
            "- Si c’est une colonne numérique, donne : moyenne, médiane, min, max, distribution, valeurs manquantes, outliers, corrélations éventuelles.\n"
            "- Si c’est une colonne catégorielle, indique : nombre de modalités, effectifs des principales valeurs, taux de valeurs rares, taux de valeurs manquantes.\n"
            "- Si c’est une colonne texte (ex : description), indique : nombre de valeurs uniques, longueur min/max/moyenne des textes, taux de doublons, présence de motifs répétitifs ou suspects, suggestions éventuelles d’amélioration.\n"
            "- Si c’est une colonne d’image ou de lien, signale les valeurs manquantes et doublons éventuels.\n"
            "N’affiche JAMAIS de stats qui ne s’appliquent pas au type de colonne. Termine chaque colonne par une recommandation métier si pertinent.\n"
            f"{context}\n"
            "Génère UNIQUEMENT le texte analytique détaillé."
        )
    return prompt

def auto_comment_agent(
    df: pd.DataFrame = None,
    result: pd.DataFrame = None,
    additional_context: str = "",
    llm_model: str = "codestral-latest",
    lang: str = "fr",
    llm_provider: str = None
):
    """
    Génère automatiquement une description professionnelle intelligente sur le résultat analysé,
    adaptée au type de chaque colonne.
    """
    prompt = build_auto_comment_prompt(
        df=df,
        result=result,
        additional_context=additional_context,
        lang=lang
    )
    answer = call_llm(prompt, model=llm_model, provider=llm_provider)
    return answer
