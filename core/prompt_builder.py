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
    Adds rules for Excel requests to avoid formula errors
    and keep workbooks dynamic.
    """
    if not any(intentions.values()):
        return ""

    return (
        "\n\nXLSX RULES (LLM QUALITY):\n"
        "- Use Excel formulas (e.g., '=SUM(A1:A10)') instead of hardcoded calculated values.\n"
        "- Place calculations in formulas, never Python calculated values.\n"
        "- No file read/write (I/O) in this code.\n"
        "- If Excel export requested: put result in 'result' (DataFrame or value).\n"
        "- If a formula is needed in the result, place the formula as a string.\n"
        "- Avoid formula errors: no division by zero, correct references.\n"
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
        detected_skills: Detected skills
        data_dictionary: Enriched data dictionary
    
    Returns:
        Complete and enriched prompt for the LLM
    """
    # === 1. DATA ANALYSIS ===
    preview = df.head(5).to_string(index=False)
    columns = ', '.join(str(c) for c in df.columns)
    n_rows = len(df)
    
    # Type analysis with advice
    type_analysis = _analyze_column_types(df)
    
    # Preview unique values on categorical columns
    sample_uniques = []
    for col in df.select_dtypes(include=["object", "category"]).columns:
        uniques = df[col].dropna().unique()[:3]
        sample_uniques.append(f"   {col}: {', '.join(map(str, uniques))}")
    
    unique_str_part = ""
    if sample_uniques:
        unique_str_part = "Example values (categorical columns):\n" + "\n".join(sample_uniques) + "\n"
    
    # === 2. DATA DICTIONARY ===
    dictionary_context = ""
    if data_dictionary:
        dictionary_context = DataDictionaryManager.create_prompt_context(data_dictionary) + "\n\n"
    
    # === 3. INTENTION DETECTION ===
    all_intentions = IntentionDetector.detect_all(question)
    primary_intentions = IntentionDetector.detect_primary(question)
    specialized_instructions = IntentionDetector.get_instructions(all_intentions)
    
    # === 4. USER CONTEXT ===
    user_context = ""
    if user_level == "beginner":
        user_context = " The user is a beginner - prioritize code clarity and simplicity.\n"
    
    skills_info = ""
    if detected_skills:
        skills_str = ', '.join(detected_skills)
        skills_info = f" Detected skills: {skills_str}\n"
    
    # === 5. BUSINESS CONTEXT & QUALITY ===
    quality_warning = _get_quality_warning(df)
    business_context_str = f"Business context:\n{business_context}\n\n" if business_context else ""
    
    # === 6. EXCEL INSTRUCTIONS ===
    intentions_excel = detect_excel_intention(question)
    excel_instructions = build_excel_instructions(intentions_excel, available_sheets)
    xlsx_skill_instructions = build_xlsx_skill_instructions(intentions_excel)
    
    # === 7. HISTORICAL CONTEXT ===
    context_part = (
        f" Conversation history:\n{context}\n\n"
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
    """Analyzes types with processing advice."""
    lines = []
    
    for col, dtype in df.dtypes.items():
        dtype_str = str(dtype)
        
        # Specific advice based on type
        if dtype in ['object', 'string']:
            # Check if it's a date
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
            if sample and isinstance(sample, str):
                if any(sep in str(sample) for sep in ['-', '/', '2024', '2025']):
                    lines.append(f"   {col} ({dtype}) - Probably a date, convert to datetime")
                else:
                    uniques = df[col].nunique()
                    if uniques < 50:
                        lines.append(f"   {col} ({dtype}) - Categorical ({uniques} unique values) - DO NOT SUM, DO NOT DO NUMERIC CALCULATIONS")
                    else:
                        lines.append(f"   {col} ({dtype}) - Free text ({uniques} unique values) - DO NOT SUM, DO NOT DO NUMERIC CALCULATIONS")
        
        elif dtype in ['int64', 'int32', 'float64', 'float32']:
            lines.append(f"   {col} ({dtype}) - Numeric, ready for calculations (sum, mean, min, max, etc.)")
        
        elif dtype == 'bool':
            lines.append(f"   {col} ({dtype}) - Boolean (True/False) - Can be summed (.mean() for %)")
        
        else:
            lines.append(f"   {col} ({dtype})")
    
    # Add global warning
    non_numeric_cols = df.select_dtypes(exclude=['number', 'bool']).columns.tolist()
    if non_numeric_cols:
        lines.append(f"\n IMPORTANT: The following columns are NON-NUMERIC and CANNOT be summed:")
        for col in non_numeric_cols:
            lines.append(f"   {col}")
    
    return '\n'.join(lines) if lines else "No columns"


def _get_quality_warning(df: pd.DataFrame) -> str:
    """Generates a warning if data quality is poor."""
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    duplicates = df.duplicated().sum()
    
    warnings = []
    
    if missing_pct > 20:
        warnings.append(f" **Missing data:** {missing_pct:.1f}% - Use dropna() or fillna()")
    
    if duplicates > 0:
        dup_pct = (duplicates / len(df)) * 100
        warnings.append(f" **Duplicates detected:** {duplicates} rows ({dup_pct:.1f}%) - Consider drop_duplicates()")
    
    if warnings:
        return " DATA QUALITY:\n" + "\n".join(warnings) + "\n\n"
    
    return ""


def build_pivot_table_prompt(
    df: pd.DataFrame,
    question: str,
    suggested_values: Optional[str] = None,
    suggested_index: Optional[str] = None,
    suggested_columns: Optional[str] = None
) -> str:
    """
    Builds a specialized prompt for creating pivot tables.
    
    Args:
        df: Source DataFrame
        question: User's question
        suggested_values: Suggested column for values
        suggested_index: Suggested column for index
        suggested_columns: Suggested column for columns
    
    Returns:
        Specialized pivot table prompt
    """
    # Column analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    preview = df.head(3).to_string(index=False)
    
    prompt = (
        "You are an expert in creating pivot tables with Pandas.\n\n"
        f"DataFrame 'df' ({len(df)} rows) - Preview:\n"
        f"{preview}\n\n"
        f"Numeric columns (for values): {', '.join(numeric_cols)}\n"
        f"Categorical columns (for index/columns): {', '.join(categorical_cols)}\n\n"
        "RULES:\n"
        "- Use df.pivot_table(values=..., index=..., columns=..., aggfunc=..., fill_value=0)\n"
        "- End with .reset_index() to get a clean DataFrame\n"
        "- Store the result in the 'result' variable\n"
        "- Do NOT use import\n"
        "- Aggregation functions: 'sum', 'mean', 'count', 'min', 'max'\n\n"
        f"Question: {question}\n\n"
        "<startCode>\n"
        f"# Pivot table for: {question}\n"
        "<endCode>"
    )
    
    prompt = _sanitize_ascii(prompt)
    return prompt


def build_xlsx_skill_instructions(intentions: Dict[str, bool]) -> str:
    """
    Adds rules for Excel requests to avoid formula errors
    and keep workbooks dynamic.
    """
    if not any(intentions.values()):
        return ""

    return (
        "\n\nXLSX RULES (LLM QUALITY):\n"
        "- Use Excel formulas (e.g., '=SUM(A1:A10)') instead of hardcoded calculated values.\n"
        "- Place calculations in formulas, never Python calculated values.\n"
        "- No file read/write (I/O) in this code.\n"
        "- If Excel export requested: put result in 'result' (DataFrame or value).\n"
        "- If a formula is needed in the result, place the formula as a string.\n"
        "- Avoid formula errors: no division by zero, correct references.\n"
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
    Builds an enriched prompt with memory context and user level.
    
    Args:
        df: DataFrame to analyze
        question: User's question
        memory_context: Context of previous exchanges (from SessionMemory)
        available_sheets: List of available Excel sheets
        user_level: User level ('beginner' or 'expert')
        detected_skills: List of skills detected in the question
    
    Returns:
        Complete prompt for the LLM
    """
    # Build enriched context
    context_parts = []
    
    if memory_context:
        context_parts.append(f"### CONVERSATION CONTEXT ###\n{memory_context}\n")
    
    if detected_skills:
        skills_str = ", ".join(detected_skills)
        context_parts.append(f"### DETECTED SKILLS ###\nSkills used: {skills_str}\n")
    
    full_context = "\n".join(context_parts)
    
    # Adapt instructions based on level
    if user_level == 'beginner':
        # Beginner mode: more detailed instructions
        additional_instructions = (
            "\n"
            " BEGINNER MODE - Detailed instructions:\n"
            "- Generate simple and readable code\n"
            "- Add explanatory comments\n"
            "- Prioritize basic operations\n"
            "- Avoid complex one-liners\n"
        )
    else:
        additional_instructions = ""
    
    # Use standard build_prompt with enriched context
    base_prompt = build_prompt(df, question, context=full_context, available_sheets=available_sheets)
    
    # Inject level instructions
    if additional_instructions:
        base_prompt = base_prompt.replace(
            " MANDATORY RULES:",
            f"{additional_instructions}\n MANDATORY RULES:"
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
    Builds a prompt for a follow-up question based on a previous result.
    
    Args:
        df: Original DataFrame
        original_question: Initial question
        original_result: Result of the initial question
        followup_question: Follow-up question
    
    Returns:
        Prompt for the follow-up question
    """
    # Summary of previous result
    if isinstance(original_result, pd.DataFrame):
        result_summary = f"DataFrame with {len(original_result)} rows, columns: {', '.join(original_result.columns[:5])}"
        result_preview = original_result.head(3).to_string(index=False)
    else:
        result_summary = str(original_result)[:200]
        result_preview = str(original_result)[:500]
    
    prompt = (
        "### FOLLOW-UP CONTEXT ###\n"
        f"Previous question: {original_question}\n"
        f"Previous result ({result_summary}):\n"
        f"{result_preview}\n\n"
        "### NEW QUESTION ###\n"
        f"The user now asks: {followup_question}\n\n"
        "Generate code to answer this follow-up question using the original DataFrame 'df'.\n"
        "If you need to reuse the previous result, first execute the code to obtain it.\n\n"
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
