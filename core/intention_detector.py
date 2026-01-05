"""
Détecteur d'intentions pour les questions analytiques.
Identifie 15+ intentions spécifiques pour générer un code optimisé.
"""

from typing import Dict, List, Set
import re


class IntentionDetector:
    """Détecte les intentions analytiques dans une question utilisateur."""
    
    # Mots-clés pour chaque intention
    FILTERING_KEYWORDS = {
        'filter', 'where', 'où', 'avec', 'sans', 'sauf', 'uniquement', 'seul',
        'exclude', 'exclure', 'supprimer', 'remove', 'greater', 'less', 'plus', 'moins',
        'entre', 'between', 'depuis', 'until', 'pendant', 'au-delà', 'only', 'just'
    }
    
    SORTING_KEYWORDS = {
        'sort', 'trier', 'order', 'ordonner', 'classement', 'ranking',
        'top', 'meilleur', 'best', 'worst', 'pire', 'croissant', 'décroissant',
        'ascending', 'descending', 'asc', 'desc', 'ranked', 'hiérarchie'
    }
    
    STATISTICAL_KEYWORDS = {
        'moyenne', 'average', 'mean', 'median', 'médiane', 'mode', 'std', 'écart-type',
        'variance', 'percentile', 'quartile', 'quantile', 'distribution', 'summary',
        'résumé', 'statistique', 'stat', 'correlation', 'corrélation'
    }
    
    AGGREGATION_KEYWORDS = {
        'total', 'sum', 'somme', 'count', 'nombre', 'nombre de', 'combien',
        'aggregate', 'agrégation', 'regrouper', 'group', 'groupby', 'par groupe',
        'accumulate', 'cumulative', 'cumulé', 'cumulée'
    }
    
    TIME_SERIES_KEYWORDS = {
        'date', 'temps', 'time', 'série', 'series', 'temporelle', 'trend', 'tendance',
        'jour', 'day', 'mois', 'month', 'année', 'year', 'période', 'period',
        'historique', 'history', 'chronologique', 'evolution', 'évolution'
    }
    
    JOIN_KEYWORDS = {
        'fusionner', 'merge', 'joindre', 'join', 'combiner', 'combine',
        'concatenate', 'concaténer', 'liaison', 'relation', 'lier'
    }
    
    ANOMALY_KEYWORDS = {
        'anomalie', 'anomaly', 'outlier', 'aberrant', 'bizarre', 'strange',
        'inusuel', 'unusual', 'erreur', 'error', 'suspect', 'suspicious',
        'valeur aberrante', 'extrême', 'extreme'
    }
    
    TRANSFORMATION_KEYWORDS = {
        'transformer', 'transform', 'convertir', 'convert', 'calculer', 'calculate',
        'dériver', 'derive', 'créer', 'create', 'générer', 'generate',
        'normaliser', 'normalize', 'standardiser', 'standardize', 'formater', 'format'
    }
    
    DUPLICATE_KEYWORDS = {
        'doublon', 'duplicate', 'dupliqué', 'unique', 'distinct', 'deduplicate',
        'suppression de doublons', 'remove duplicates', 'occurrences'
    }
    
    MISSING_KEYWORDS = {
        'vide', 'empty', 'manquant', 'missing', 'null', 'nan', 'absent',
        'complétude', 'completeness', 'remplir', 'fill', 'imputer'
    }
    
    SEGMENT_KEYWORDS = {
        'segmenter', 'segment', 'catégorie', 'category', 'groupe', 'group',
        'classification', 'classify', 'profil', 'profile', 'type', 'classe'
    }
    
    RANKING_KEYWORDS = {
        'rang', 'rank', 'position', 'classement', 'scoring', 'score',
        'percentile', 'percentil', 'top n', 'bottom'
    }
    
    COMPARISON_KEYWORDS = {
        'comparer', 'compare', 'différence', 'difference', 'vs', 'versus',
        'écart', 'gap', 'changement', 'change', 'évolution', 'variation'
    }
    
    PIVOT_KEYWORDS = {
        'pivot', 'tableau croisé', 'crosstab', 'cross-tab', 'résumé par',
        'agrégation par', 'dimension', 'mesure'
    }
    
    PATTERN_KEYWORDS = {
        'pattern', 'motif', 'tendance', 'trend', 'régularité', 'règle',
        'récurrence', 'recurrence', 'cyclique', 'cyclical'
    }
    
    EXPORT_KEYWORDS = {
        'export', 'exporter', 'télécharger', 'download', 'sauvegarder',
        'save', 'enregistrer', 'excel', 'csv', 'json'
    }
    
    @classmethod
    def detect_all(cls, question: str) -> Dict[str, bool]:
        """
        Détecte toutes les intentions dans une question.
        
        Args:
            question: Question de l'utilisateur
        
        Returns:
            Dict avec toutes les intentions détectées
        """
        question_lower = question.lower()
        
        return {
            'filtering': cls._has_keywords(question_lower, cls.FILTERING_KEYWORDS),
            'sorting': cls._has_keywords(question_lower, cls.SORTING_KEYWORDS),
            'statistical': cls._has_keywords(question_lower, cls.STATISTICAL_KEYWORDS),
            'aggregation': cls._has_keywords(question_lower, cls.AGGREGATION_KEYWORDS),
            'time_series': cls._has_keywords(question_lower, cls.TIME_SERIES_KEYWORDS),
            'join': cls._has_keywords(question_lower, cls.JOIN_KEYWORDS),
            'anomaly_detection': cls._has_keywords(question_lower, cls.ANOMALY_KEYWORDS),
            'transformation': cls._has_keywords(question_lower, cls.TRANSFORMATION_KEYWORDS),
            'duplicate_handling': cls._has_keywords(question_lower, cls.DUPLICATE_KEYWORDS),
            'missing_values': cls._has_keywords(question_lower, cls.MISSING_KEYWORDS),
            'segmentation': cls._has_keywords(question_lower, cls.SEGMENT_KEYWORDS),
            'ranking': cls._has_keywords(question_lower, cls.RANKING_KEYWORDS),
            'comparison': cls._has_keywords(question_lower, cls.COMPARISON_KEYWORDS),
            'pivot_table': cls._has_keywords(question_lower, cls.PIVOT_KEYWORDS),
            'pattern_detection': cls._has_keywords(question_lower, cls.PATTERN_KEYWORDS),
            'export': cls._has_keywords(question_lower, cls.EXPORT_KEYWORDS),
        }
    
    @classmethod
    def detect_primary(cls, question: str) -> List[str]:
        """
        Détecte les intentions primaires (les plus importantes).
        
        Args:
            question: Question de l'utilisateur
        
        Returns:
            Liste des intentions primaires par ordre d'importance
        """
        all_intentions = cls.detect_all(question)
        primary = [k for k, v in all_intentions.items() if v]
        
        # Tri par priorité heuristique
        priority_order = [
            'pivot_table', 'aggregation', 'filtering', 'sorting',
            'statistical', 'transformation', 'time_series',
            'comparison', 'segmentation', 'ranking'
        ]
        
        primary_sorted = sorted(
            primary,
            key=lambda x: priority_order.index(x) if x in priority_order else 999
        )
        
        return primary_sorted[:3]  # Top 3 intentions
    
    @classmethod
    def get_instructions(cls, intentions: Dict[str, bool]) -> str:
        """
        Génère les instructions spécifiques basées sur les intentions détectées.
        
        Args:
            intentions: Dict des intentions
        
        Returns:
            String avec instructions pour le prompt
        """
        instructions = []
        
        if intentions.get('pivot_table'):
            instructions.append(
                "📊 PIVOT TABLE DÉTECTÉE:\n"
                "- Utilise df.pivot_table(values='...', index='...', columns='...', aggfunc='...')\n"
                "- Fonctions d'agrégation: 'sum', 'mean', 'count', 'min', 'max', 'std'\n"
                "- Termine par .reset_index() pour un DataFrame propre"
            )
        
        if intentions.get('aggregation'):
            instructions.append(
                "📈 AGRÉGATION DÉTECTÉE:\n"
                "- Utilise df.groupby(...).agg({...}) pour regrouper\n"
                "- Spécifie clairement les colonnes à grouper et à agréger\n"
                "- N'oublie pas .reset_index() si le résultat doit être un DataFrame"
            )
        
        if intentions.get('filtering'):
            instructions.append(
                "🔍 FILTRAGE DÉTECTÉ:\n"
                "- Utilise des conditions booléennes: df[df['col'] > valeur]\n"
                "- Combine avec & (et) ou | (ou), pas 'and'/'or'\n"
                "- Vérifie que les valeurs et types de colonnes sont corrects"
            )
        
        if intentions.get('sorting'):
            instructions.append(
                "🔤 TRI DÉTECTÉ:\n"
                "- Utilise df.sort_values(by=['col1', 'col2'], ascending=[True, False])\n"
                "- Précise si croissant (ascending=True) ou décroissant (ascending=False)\n"
                "- N'oublie pas .reset_index(drop=True) pour les index continus"
            )
        
        if intentions.get('statistical'):
            instructions.append(
                "📊 STATISTIQUES DÉTECTÉES:\n"
                "- Pour moyenne: df['col'].mean()\n"
                "- Pour écart-type: df['col'].std()\n"
                "- Pour percentile: df['col'].quantile(0.25 / 0.50 / 0.75)\n"
                "- Utilise describe() pour un résumé complet"
            )
        
        if intentions.get('time_series'):
            instructions.append(
                "⏰ SÉRIE TEMPORELLE DÉTECTÉE:\n"
                "- Assure-toi que la colonne date est en format datetime\n"
                "- Utilise df['date'].dt.year / .month / .day pour extraire\n"
                "- Pour grouper par période: df.groupby(df['date'].dt.to_period('M'))"
            )
        
        if intentions.get('transformation'):
            instructions.append(
                "🔄 TRANSFORMATION DÉTECTÉE:\n"
                "- Pour nouvelles colonnes: df['new_col'] = df['col1'] + df['col2']\n"
                "- Pour conversions: df['col'].astype(type)\n"
                "- Pour nettoyage texte: df['col'].str.lower() / .str.strip()"
            )
        
        if intentions.get('anomaly_detection'):
            instructions.append(
                "⚠️ DÉTECTION D'ANOMALIES:\n"
                "- Utilise l'écart-type: mean ± 3*std pour les outliers\n"
                "- IQR method: Q1 - 1.5*IQR ou Q3 + 1.5*IQR\n"
                "- Identifie les valeurs NULL et les doublons"
            )
        
        if intentions.get('comparison'):
            instructions.append(
                "⚖️ COMPARAISON DÉTECTÉE:\n"
                "- Utilise des groupby avec diff() ou pct_change() pour les variations\n"
                "- Compare les distributions avec describe() sur les groupes\n"
                "- Calcule l'écart absolu ou en pourcentage"
            )
        
        if intentions.get('segmentation'):
            instructions.append(
                "🎯 SEGMENTATION DÉTECTÉE:\n"
                "- Utilise pd.cut() pour créer des tranches numériques\n"
                "- Utilise pd.qcut() pour découper par quantiles\n"
                "- Utilise groupby() pour analyser par segment"
            )
        
        if intentions.get('ranking'):
            instructions.append(
                "🏆 RANKING DÉTECTÉ:\n"
                "- Utilise df.nlargest(n, 'col') ou df.nsmallest(n, 'col')\n"
                "- Pour un rang: df['rank'] = df['col'].rank(method='dense')\n"
                "- Trie ensuite par rang décroissant"
            )
        
        if intentions.get('duplicate_handling'):
            instructions.append(
                "🔁 DOUBLONS DÉTECTÉS:\n"
                "- Pour les identifier: df[df.duplicated()]\n"
                "- Pour les supprimer: df.drop_duplicates()\n"
                "- Par colonne spécifique: df.drop_duplicates(subset=['col'])"
            )
        
        if intentions.get('missing_values'):
            instructions.append(
                "⊘ VALEURS MANQUANTES DÉTECTÉES:\n"
                "- Pour les identifier: df.isnull().sum()\n"
                "- Pour les remplir: df.fillna(value)\n"
                "- Pour les supprimer: df.dropna()"
            )
        
        if intentions.get('join'):
            instructions.append(
                "🔗 FUSION DÉTECTÉE:\n"
                "- Cette application ne gère qu'un DataFrame à la fois\n"
                "- Explique comment fusionner manuellement les données\n"
                "- Ou crée une variable 'result' avec les étapes"
            )
        
        if intentions.get('pattern_detection'):
            instructions.append(
                "🔎 MOTIF/TENDANCE DÉTECTÉ:\n"
                "- Utilise groupby pour identifier les motifs\n"
                "- Vérifie la corrélation avec .corr()\n"
                "- Cherche les cycles ou récurrences"
            )
        
        if instructions:
            return "\n\n🎯 INSTRUCTIONS SPÉCIALISÉES:\n" + "\n\n".join(instructions) + "\n"
        
        return ""
    
    @staticmethod
    def _has_keywords(text: str, keywords: Set[str]) -> bool:
        """
        Vérifie si au moins un mot-clé est présent dans le texte.
        
        Args:
            text: Texte à analyser
            keywords: Ensemble de mots-clés
        
        Returns:
            True si au moins un mot-clé trouvé
        """
        # Tokenize basique
        words = re.findall(r'\b\w+\b', text)
        return any(word in keywords for word in words)
