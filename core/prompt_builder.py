import pandas as pd
from typing import Optional, List, Dict, Any
from core.intention_detector import IntentionDetector
from core.data_dictionary_manager import DataDictionaryManager


def detect_excel_intention(question: str) -> Dict[str, bool]:
    """
    Detects Excel-related intentions in the user's question.
    
    Args:
        question: User's question
    
    Returns:
        Dict with detected intentions
    """
    question_lower = question.lower()
    
    return {
        'pivot_table': any(kw in question_lower for kw in [
            'pivot', 'tableau croise', 'tableau croise', 'crosstab', 
            'resumer par', 'resumer par', 'agreger par', 'agreger par'
        ]),
        'export_excel': any(kw in question_lower for kw in [
            'export', 'excel', 'telecharger', 'telecharger', 'sauvegarder',
            'download', 'xlsx', 'enregistrer', 'exporter'
        ]),
        'multi_sheets': any(kw in question_lower for kw in [
            'feuille', 'sheet', 'onglet', 'feuilles', 'sheets'
        ]),
        'merge': any(kw in question_lower for kw in [
            'fusionner', 'combiner', 'merge', 'joindre', 'join', 
            'concatener', 'concatener', 'concat'
        ]),
        'groupby': any(kw in question_lower for kw in [
            'grouper', 'regrouper', 'par groupe', 'group by', 'groupby'
        ])
    }


def build_excel_instructions(intentions: Dict[str, bool], available_sheets: Optional[List[str]] = None) -> str:
    """
    Builds specific instructions for Excel operations.
    
    Args:
        intentions: Dict of detected intentions
        available_sheets: List of available sheets if multi-sheets
    
    Returns:
        Additional instructions for the prompt
    """
    instructions = []
    
    if intentions.get('pivot_table'):
        instructions.append(
            " PIVOT TABLE REQUESTED :\n"
            "- Use df.pivot_table(values='...', index='...', columns='...', aggfunc='sum')\n"
            "- Available aggregation functions: 'sum', 'mean', 'count', 'min', 'max', 'std'\n"
            "- To reset index after pivot: .reset_index()\n"
            "- Example: result = df.pivot_table(values='sales', index='region', columns='product', aggfunc='sum').reset_index()"
        )
    
    if intentions.get('export_excel'):
        instructions.append(
            " EXCEL EXPORT :\n"
            "- Simply place your result in the 'result' variable\n"
            "- Excel export will be handled automatically by the application\n"
            "- Do NOT use to_excel() in your code"
        )
    
    if intentions.get('multi_sheets') and available_sheets:
        sheets_str = ', '.join(available_sheets[:5])
        if len(available_sheets) > 5:
            sheets_str += f", ... ({len(available_sheets)} sheets total)"
        instructions.append(
            f" MULTI-SHEETS :\n"
            f"- Available sheets: {sheets_str}\n"
            f"- Work with the DataFrame 'df' which contains the currently selected sheet"
        )
    
    if intentions.get('merge'):
        instructions.append(
            " MERGE/FUSION :\n"
            "- To merge two columns into one: df['new'] = df['col1'].astype(str) + df['col2'].astype(str)\n"
            "- To concatenate filtered rows: use boolean conditions\n"
            "- Multiple file merging is handled automatically by the application"
        )
    
    if intentions.get('groupby'):
        instructions.append(
            " GROUPBY/AGGREGATION :\n"
            "- Use df.groupby('column').agg({'col1': 'sum', 'col2': 'mean'})\n"
            "- For multiple columns: df.groupby(['col1', 'col2'])\n"
            "- Don't forget .reset_index() if you want a clean DataFrame as output"
        )
    
    if instructions:
        return "\n\n DETECTED SPECIFIC INSTRUCTIONS :\n" + "\n\n".join(instructions) + "\n"
    return ""


def build_xlsx_skill_instructions(intentions: Dict[str, bool]) -> str:
    """
    Ajoute des regles pour les demandes Excel afin d'eviter les erreurs de formule
    et de garder les classeurs dynamiques.
    """
    if not any(intentions.values()):
        return ""

    return (
        "\n\nXLSX RULES (LLM QUALITY):\n"
        "- Utilise des formules Excel (ex: '=SUM(A1:A10)') au lieu de valeurs calculees en dur.\n"
        "- Place les calculs dans des formules, jamais des valeurs Python calculees.\n"
        "- Pas de lecture/ecriture de fichiers (I/O) dans ce code.\n"
        "- Si export Excel demande: mets le resultat dans 'result' (DataFrame ou valeur).\n"
        "- Si une formule est necessaire dans le resultat, place la formule comme string.\n"
        "- Evite les erreurs de formule: pas de division par zero, references correctes.\n"
    )


def build_prompt(
    df: pd.DataFrame, 
    question: str, 
    context: str = "",
    available_sheets: Optional[List[str]] = None,
    user_level: str = "expert",
    detected_skills: Optional[List[str]] = None,
    data_dictionary: Optional[Dict[str, Any]] = None,
    business_context: Optional[str] = None
) -> str:
    """
    Builds the enriched prompt for the LLM with intention detection.
    
    Args:
        df: DataFrame to analyze
        question: User's question
        context: Context of previous exchanges
        available_sheets: List of available Excel sheets
        user_level: User level ('beginner' or 'expert')
        detected_skills: Skills detectees
        data_dictionary: Dictionnaire de donnees enrichi
    
    Returns:
        Prompt complet et enrichi pour le LLM
    """
    # === 1. ANALYSE DES DONNEES ===
    preview = df.head(5).to_string(index=False)
    columns = ', '.join(str(c) for c in df.columns)
    n_rows = len(df)
    
    # Analyse des types avec conseils
    type_analysis = _analyze_column_types(df)
    
    # Apercu valeurs uniques sur colonnes categorielles
    sample_uniques = []
    for col in df.select_dtypes(include=["object", "category"]).columns:
        uniques = df[col].dropna().unique()[:3]
        sample_uniques.append(f"   {col}: {', '.join(map(str, uniques))}")
    
    unique_str_part = ""
    if sample_uniques:
        unique_str_part = "Exemples de valeurs (colonnes categorielles):\n" + "\n".join(sample_uniques) + "\n"
    
    # === 2. DICTIONNAIRE DE DONNEES ===
    dictionary_context = ""
    if data_dictionary:
        dictionary_context = DataDictionaryManager.create_prompt_context(data_dictionary) + "\n\n"
    
    # === 3. DETECTION D'INTENTIONS ===
    all_intentions = IntentionDetector.detect_all(question)
    primary_intentions = IntentionDetector.detect_primary(question)
    specialized_instructions = IntentionDetector.get_instructions(all_intentions)
    
    # === 4. CONTEXTE UTILISATEUR ===
    user_context = ""
    if user_level == "beginner":
        user_context = " L'utilisateur est debutant - privilegie la clarte et la simplicite du code.\n"
    
    skills_info = ""
    if detected_skills:
        skills_str = ', '.join(detected_skills)
        skills_info = f" Competences detectees: {skills_str}\n"
    
    # === 5. CONTEXTE METIER & QUALITE ===
    quality_warning = _get_quality_warning(df)
    business_context_str = f"Business context:\n{business_context}\n\n" if business_context else ""
    
    # === 6. INSTRUCTIONS EXCEL ===
    intentions_excel = detect_excel_intention(question)
    excel_instructions = build_excel_instructions(intentions_excel, available_sheets)
    xlsx_skill_instructions = build_xlsx_skill_instructions(intentions_excel)
    
    # === 7. CONTEXTE HISTORIQUE ===
    context_part = (
        f" Historique de la conversation:\n{context}\n\n"
        if context else ""
    )
    
    # === FINAL PROMPT CONSTRUCTION ===
    prompt = (
        f"{context_part}"
        f"You are a Python, Pandas and data analysis expert.\n"
        f"{user_context}"
        f"{skills_info}"
        f"\n"
        f" DATA TO ANALYZE:\n"
        f"The DataFrame 'df' contains **{n_rows:,} rows** and **{len(df.columns)} columns**.\n"
        f"\nPreview of the first 5 rows:\n{preview}\n\n"
        f" Available columns:\n{columns}\n\n"
        f" Column types:\n{type_analysis}\n\n"
        f"{unique_str_part}"
        f"{dictionary_context}"
        f"{business_context_str}"
        f"{quality_warning}"
        f"{excel_instructions}"
        f"{xlsx_skill_instructions}"
        f"{specialized_instructions}"
        f"\n"
        f"You have direct access to utility functions (without import):\n"
        f"calculate_age, calculate_days_between, extract_year, is_valid_email, "
        f"anonymize_phone, get_country_code, format_currency, round_to, age_category, "
        f"tenure_years, valid_female_percentage, female_percentage, valid_email_percentage, "
        f"mean_age_females, mean_age_males\n"
        f"\n"
        f" MANDATORY RULES:\n"
        f"1. NEVER use import or from...import\n"
        f"2. NEVER use pd. or pandas. (no pd.DataFrame, no pd.read_csv)\n"
        f"3. NEVER overwrite the 'df' variable\n"
        f"4. Don't limit df with head()/sample() unless the user asks for a preview\n"
        f"5. Use df methods directly (df.groupby(), df.sum(), etc.)\n"
        f"6. For groupby+apply: work on the group passed as argument, not df[...]\n"
        f"7. For percentages: use (col == 'value').mean() * 100\n"
        f"8. Store your result in the 'result' variable\n"
        f"9. Your response must ONLY contain code between <startCode> and <endCode>\n"
        f"10. No comments or explanations outside the code\n"
        f"11. No print() output unless that's the expected response\n"
        f"12. NEVER do .sum() on a NON-NUMERIC column (text, string, etc.)\n"
        f"13. NEVER do arithmetic calculations (+, -, *, /) on non-numeric columns\n"
        f"14. If column is text/string: use .count(), .value_counts(), .nunique(), .str.len()\n"
        f"\n"
        f" USER QUESTION:\n"
        f"{question}\n"
        f"\n"
        f"<startCode>\n"
        f"# Solution for: {question}\n"
        f"<endCode>"
    )
    
    prompt = _sanitize_ascii(prompt)
    return prompt


def _sanitize_ascii(text: str) -> str:
    """Best-effort ASCII cleanup for prompt text."""
    return text.encode('ascii', 'ignore').decode('ascii')


def _analyze_column_types(df: pd.DataFrame) -> str:
    """Analyse les types avec conseils sur le traitement."""
    lines = []
    
    for col, dtype in df.dtypes.items():
        dtype_str = str(dtype)
        
        # Conseil specifique selon le type
        if dtype in ['object', 'string']:
            # Verifier si c'est une date
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
            if sample and isinstance(sample, str):
                if any(sep in str(sample) for sep in ['-', '/', '2024', '2025']):
                    lines.append(f"   {col} ({dtype}) -  Probablement une date, a convertir en datetime")
                else:
                    uniques = df[col].nunique()
                    if uniques < 50:
                        lines.append(f"   {col} ({dtype}) -  Categorique ({uniques} valeurs uniques) -  NE PAS SOMMER, NE PAS FAIRE DE CALCUL NUMERIQUE")
                    else:
                        lines.append(f"   {col} ({dtype}) - Texte libre ({uniques} valeurs uniques) -  NE PAS SOMMER, NE PAS FAIRE DE CALCUL NUMERIQUE")
        
        elif dtype in ['int64', 'int32', 'float64', 'float32']:
            lines.append(f"   {col} ({dtype}) -  Numerique, pret pour calculs (sum, mean, min, max, etc.)")
        
        elif dtype == 'bool':
            lines.append(f"   {col} ({dtype}) -  Booleen (True/False) -  Peut etre somme (.mean() pour %)")
        
        else:
            lines.append(f"   {col} ({dtype})")
    
    # Ajouter avertissement global
    non_numeric_cols = df.select_dtypes(exclude=['number', 'bool']).columns.tolist()
    if non_numeric_cols:
        lines.append(f"\n IMPORTANT: Les colonnes suivantes sont NON-NUMERIQUES et ne peuvent PAS etre sommees:")
        for col in non_numeric_cols:
            lines.append(f"   {col}")
    
    return '\n'.join(lines) if lines else "Aucune colonne"


def _get_quality_warning(df: pd.DataFrame) -> str:
    """Genere un avertissement si la qualite des donnees est mauvaise."""
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    duplicates = df.duplicated().sum()
    
    warnings = []
    
    if missing_pct > 20:
        warnings.append(f" **Donnees manquantes:** {missing_pct:.1f}% - Utilise dropna() ou fillna()")
    
    if duplicates > 0:
        dup_pct = (duplicates / len(df)) * 100
        warnings.append(f"i **Doublons detectes:** {duplicates} lignes ({dup_pct:.1f}%) - Considere drop_duplicates()")
    
    if warnings:
        return " QUALITE DES DONNEES:\n" + "\n".join(warnings) + "\n\n"
    
    return ""


def build_pivot_table_prompt(
    df: pd.DataFrame,
    question: str,
    suggested_values: Optional[str] = None,
    suggested_index: Optional[str] = None,
    suggested_columns: Optional[str] = None
) -> str:
    """
    Construit un prompt specialise pour la creation de pivot tables.
    
    Args:
        df: DataFrame source
        question: Question de l'utilisateur
        suggested_values: Colonne suggeree pour les valeurs
        suggested_index: Colonne suggeree pour l'index
        suggested_columns: Colonne suggeree pour les colonnes
    
    Returns:
        Prompt specialise pivot table
    """
    # Analyse des colonnes
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    preview = df.head(3).to_string(index=False)
    
    prompt = (
        "Tu es un expert en creation de tableaux croises dynamiques (pivot tables) avec Pandas.\n\n"
        f"DataFrame 'df' ({len(df)} lignes) - Apercu :\n"
        f"{preview}\n\n"
        f"Colonnes numeriques (pour values) : {', '.join(numeric_cols)}\n"
        f"Colonnes categorielles (pour index/columns) : {', '.join(categorical_cols)}\n\n"
        "REGLES :\n"
        "- Utilise df.pivot_table(values=..., index=..., columns=..., aggfunc=..., fill_value=0)\n"
        "- Termine par .reset_index() pour obtenir un DataFrame propre\n"
        "- Stocke le resultat dans la variable 'result'\n"
        "- N'utilise PAS d'import\n"
        "- Fonctions d'agregation : 'sum', 'mean', 'count', 'min', 'max'\n\n"
        f"Question : {question}\n\n"
        "<startCode>\n"
        f"# Pivot table pour : {question}\n"
        "<endCode>"
    )
    
    prompt = _sanitize_ascii(prompt)
    return prompt


def build_xlsx_skill_instructions(intentions: Dict[str, bool]) -> str:
    """
    Ajoute des regles pour les demandes Excel afin d'eviter les erreurs de formule
    et de garder les classeurs dynamiques.
    """
    if not any(intentions.values()):
        return ""

    return (
        "\n\nXLSX RULES (LLM QUALITY):\n"
        "- Utilise des formules Excel (ex: '=SUM(A1:A10)') au lieu de valeurs calculees en dur.\n"
        "- Place les calculs dans des formules, jamais des valeurs Python calculees.\n"
        "- Pas de lecture/ecriture de fichiers (I/O) dans ce code.\n"
        "- Si export Excel demande: mets le resultat dans 'result' (DataFrame ou valeur).\n"
        "- Si une formule est necessaire dans le resultat, place la formule comme string.\n"
        "- Evite les erreurs de formule: pas de division par zero, references correctes.\n"
    )


def build_prompt_with_memory(
    df: pd.DataFrame,
    question: str,
    memory_context: str = "",
    available_sheets: Optional[List[str]] = None,
    user_level: str = 'expert',
    detected_skills: Optional[List[str]] = None
) -> str:
    """
    Construit un prompt enrichi avec contexte memoire et niveau utilisateur.
    
    Args:
        df: DataFrame a analyser
        question: Question de l'utilisateur
        memory_context: Contexte des echanges precedents (depuis SessionMemory)
        available_sheets: Liste des feuilles Excel disponibles
        user_level: Niveau utilisateur ('beginner' ou 'expert')
        detected_skills: Liste des skills detectes dans la question
    
    Returns:
        Prompt complet pour le LLM
    """
    # Construction du contexte enrichi
    context_parts = []
    
    if memory_context:
        context_parts.append(f"### CONTEXTE DE LA CONVERSATION ###\n{memory_context}\n")
    
    if detected_skills:
        skills_str = ", ".join(detected_skills)
        context_parts.append(f"### COMPETENCES DETECTEES ###\nSkills utilises : {skills_str}\n")
    
    full_context = "\n".join(context_parts)
    
    # Adapter les instructions selon le niveau
    if user_level == 'beginner':
        # Mode debutant : instructions plus detaillees
        additional_instructions = (
            "\n"
            " MODE DEBUTANT - Instructions detaillees :\n"
            "- Genere un code simple et lisible\n"
            "- Ajoute des commentaires explicatifs\n"
            "- Privilegie les operations basiques\n"
            "- Evite les one-liners complexes\n"
        )
    else:
        additional_instructions = ""
    
    # Utiliser le build_prompt standard avec le contexte enrichi
    base_prompt = build_prompt(df, question, context=full_context, available_sheets=available_sheets)
    
    # Injecter les instructions de niveau
    if additional_instructions:
        base_prompt = base_prompt.replace(
            " REGLES OBLIGATOIRES:",
            f"{additional_instructions}\n REGLES OBLIGATOIRES:"
        )
    
    return base_prompt


def build_followup_prompt(
    df: pd.DataFrame,
    original_question: str,
    original_result: Any,
    followup_question: str,
    business_context: Optional[str] = None
) -> str:
    """
    Construit un prompt pour une question de suivi basee sur un resultat precedent.
    
    Args:
        df: DataFrame original
        original_question: Question initiale
        original_result: Resultat de la question initiale
        followup_question: Question de suivi
    
    Returns:
        Prompt pour la question de suivi
    """
    # Resume du resultat precedent
    if isinstance(original_result, pd.DataFrame):
        result_summary = f"DataFrame avec {len(original_result)} lignes, colonnes: {', '.join(original_result.columns[:5])}"
        result_preview = original_result.head(3).to_string(index=False)
    else:
        result_summary = str(original_result)[:200]
        result_preview = str(original_result)[:500]
    
    prompt = (
        "### CONTEXTE DE SUIVI ###\n"
        f"Question precedente : {original_question}\n"
        f"Resultat precedent ({result_summary}) :\n"
        f"{result_preview}\n\n"
        "### NOUVELLE QUESTION ###\n"
        f"L'utilisateur pose maintenant : {followup_question}\n\n"
        "Genere du code pour repondre a cette question de suivi en utilisant le DataFrame 'df' original.\n"
        "Si tu dois reutiliser le resultat precedent, execute d'abord le code pour l'obtenir.\n\n"
    )
    
    return build_prompt(df, followup_question, context=prompt, business_context=business_context)


def detect_intent(question: str) -> Dict[str, Any]:
    """
    Detecte l'intention globale de la question.
    
    Args:
        question: Question de l'utilisateur
    
    Returns:
        Dict avec les intentions detectees
    """
    question_lower = question.lower()
    
    intents = {
        'type': 'query',  # 'query', 'visualization', 'export', 'analysis'
        'excel': detect_excel_intention(question),
        'visualization': any(kw in question_lower for kw in [
            'graphique', 'graph', 'chart', 'visualiser', 'visualize',
            'plot', 'courbe', 'histogramme', 'camembert', 'bar'
        ]),
        'statistics': any(kw in question_lower for kw in [
            'moyenne', 'mediane', 'mediane', 'ecart-type', 'ecart-type',
            'statistique', 'stats', 'distribution', 'correlation', 'correlation'
        ]),
        'filtering': any(kw in question_lower for kw in [
            'filtrer', 'filter', 'selectionner', 'selectionner', 'ou', 'ou',
            'condition', 'superieur', 'superieur', 'inferieur', 'inferieur'
        ]),
        'sorting': any(kw in question_lower for kw in [
            'trier', 'sort', 'classement', 'top', 'bottom', 'meilleur', 'pire'
        ]),
        'aggregation': any(kw in question_lower for kw in [
            'total', 'somme', 'sum', 'compter', 'count', 'grouper', 'group'
        ])
    }
    
    # Determiner le type principal
    if intents['visualization']:
        intents['type'] = 'visualization'
    elif intents['excel']['export_excel']:
        intents['type'] = 'export'
    elif intents['statistics']:
        intents['type'] = 'analysis'
    
    return intents


def get_skill_instructions(skill_ids: List[str]) -> str:
    """
    Retourne des instructions specifiques pour les skills detectes.
    
    Args:
        skill_ids: Liste des IDs de skills
    
    Returns:
        Instructions additionnelles
    """
    instructions = {
        'pivot': (
            "Pour creer un pivot table :\n"
            "- Utilise df.pivot_table(values='...', index='...', columns='...', aggfunc='sum')\n"
            "- N'oublie pas .reset_index() a la fin"
        ),
        'viz': (
            "Pour les visualisations :\n"
            "- Stocke le resultat dans 'result'\n"
            "- Le graphique sera genere automatiquement"
        ),
        'stats': (
            "Pour les statistiques :\n"
            "- Utilise df.describe() pour un resume complet\n"
            "- df.corr() pour les correlations\n"
            "- df['col'].value_counts() pour les distributions"
        ),
        'anomaly': (
            "Pour detecter les anomalies :\n"
            "- Utilise les quartiles : Q1, Q3, IQR = Q3-Q1\n"
            "- Outliers : < Q1-1.5*IQR ou > Q3+1.5*IQR"
        ),
        'filter': (
            "Pour filtrer :\n"
            "- df[df['col'] > value]\n"
            "- df.query('col > value')\n"
            "- Conditions multiples : & (et), | (ou)"
        )
    }
    
    result = []
    for skill_id in skill_ids:
        if skill_id in instructions:
            result.append(instructions[skill_id])
    
    return "\n\n".join(result)
