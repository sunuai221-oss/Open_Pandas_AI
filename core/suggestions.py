"""
Module de suggestions intelligentes pour Open Pandas-AI.
Génère des suggestions contextuelles basées sur les données et l'historique.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime


class SmartSuggestions:
    """
    Génère des suggestions de questions contextuelles basées sur :
    - Le type de colonnes du DataFrame
    - L'historique des échanges
    - Le dernier résultat obtenu
    """
    
    TEMPLATES = {
        'numeric': [
            "Quelle est la moyenne de {col} ?",
            "Top 10 par {col} décroissant",
            "Distribution de {col}",
            "Détecter les outliers dans {col}",
            "Statistiques descriptives de {col}",
            "Corrélation entre {col} et les autres colonnes numériques",
        ],
        'categorical': [
            "Répartition par {col}",
            "Combien de valeurs uniques dans {col} ?",
            "Grouper par {col} et calculer les totaux",
            "Top 5 des {col} les plus fréquents",
            "Filtrer où {col} égale une valeur spécifique",
        ],
        'datetime': [
            "Évolution temporelle par {col}",
            "Tendance mensuelle sur {col}",
            "Saisonnalité de {col}",
            "Comparer les périodes par {col}",
        ],
        'general': [
            "Résumé statistique complet",
            "Créer un tableau croisé dynamique",
            "Exporter les résultats en Excel",
            "Générer un graphique récapitulatif",
            "Détecter les valeurs manquantes",
            "Identifier les doublons",
        ],
        'followup': [
            "Détailler par {col}",
            "Visualiser ce résultat",
            "Exporter en Excel",
            "Filtrer sur les valeurs extrêmes",
            "Comparer avec une autre période",
        ]
    }
    
    DOMAIN_TEMPLATES = {
        'sales': [
            "Chiffre d'affaires par région",
            "Top produits par ventes",
            "Évolution des ventes mensuelles",
            "Panier moyen par client",
        ],
        'hr': [
            "Répartition par département",
            "Ancienneté moyenne",
            "Turnover par équipe",
            "Distribution des salaires",
        ],
        'finance': [
            "Total des transactions",
            "Moyenne par catégorie",
            "Évolution du solde",
            "Détection des anomalies",
        ]
    }
    
    def __init__(
        self,
        df: Optional[pd.DataFrame] = None,
        exchanges: Optional[List[Dict]] = None,
        user_level: str = 'expert'
    ):
        self.df = df
        self.exchanges = exchanges or []
        self.user_level = user_level
        
    def generate(self, limit: int = 6) -> List[Dict[str, Any]]:
        """
        Génère des suggestions basées sur le DataFrame actuel.
        
        Returns:
            Liste de suggestions avec text, type, column, icon
        """
        suggestions = []
        
        if self.df is None or self.df.empty:
            # Suggestions génériques si pas de données
            return [
                {'text': "Chargez un fichier pour commencer", 'type': 'info', 'column': None, 'icon': '📁'},
            ]
        
        # Suggestions par type de colonne
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Colonnes numériques
        for col in numeric_cols[:2]:
            templates = self.TEMPLATES['numeric'][:2] if self.user_level == 'beginner' else self.TEMPLATES['numeric'][:3]
            for template in templates:
                suggestions.append({
                    'text': template.format(col=col),
                    'type': 'numeric',
                    'column': col,
                    'icon': '🔢'
                })
        
        # Colonnes catégorielles
        for col in categorical_cols[:2]:
            templates = self.TEMPLATES['categorical'][:1] if self.user_level == 'beginner' else self.TEMPLATES['categorical'][:2]
            for template in templates:
                suggestions.append({
                    'text': template.format(col=col),
                    'type': 'categorical',
                    'column': col,
                    'icon': '📊'
                })
        
        # Colonnes datetime
        for col in datetime_cols[:1]:
            for template in self.TEMPLATES['datetime'][:1]:
                suggestions.append({
                    'text': template.format(col=col),
                    'type': 'datetime',
                    'column': col,
                    'icon': '📅'
                })
        
        # Suggestions générales
        general_limit = 2 if self.user_level == 'beginner' else 3
        for template in self.TEMPLATES['general'][:general_limit]:
            suggestions.append({
                'text': template,
                'type': 'general',
                'column': None,
                'icon': '💡'
            })
        
        # Déduplication et limitation
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s['text'] not in seen:
                seen.add(s['text'])
                unique_suggestions.append(s)
        
        return unique_suggestions[:limit]
    
    def generate_followup(
        self,
        last_question: str,
        last_result: Any,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Génère des suggestions de suivi basées sur le dernier échange.
        """
        followups = []
        question_lower = last_question.lower()
        
        # Suggestions basées sur le type de résultat
        if isinstance(last_result, pd.DataFrame) and not last_result.empty:
            cols = last_result.columns.tolist()
            
            followups.append({
                'text': "Visualiser ce résultat en graphique",
                'type': 'viz',
                'icon': '📈'
            })
            followups.append({
                'text': "Exporter ce résultat en Excel",
                'type': 'export',
                'icon': '📥'
            })
            
            if len(cols) > 0:
                followups.append({
                    'text': f"Détailler par {cols[0]}",
                    'type': 'detail',
                    'icon': '🔍'
                })
        
        # Suggestions basées sur le contenu de la question
        if 'top' in question_lower:
            followups.append({
                'text': "Et le bottom 5 ?",
                'type': 'inverse',
                'icon': '🔄'
            })
        
        if 'moyenne' in question_lower or 'mean' in question_lower:
            followups.append({
                'text': "Et la médiane ?",
                'type': 'related',
                'icon': '📊'
            })
        
        if 'région' in question_lower or 'region' in question_lower:
            followups.append({
                'text': "Comparer aussi par produit ?",
                'type': 'extend',
                'icon': '➕'
            })
        
        if 'mois' in question_lower or 'mensuel' in question_lower:
            followups.append({
                'text': "Voir la tendance annuelle ?",
                'type': 'extend',
                'icon': '📆'
            })
        
        return followups[:limit]
    
    def detect_domain(self) -> Optional[str]:
        """
        Détecte le domaine métier probable des données.
        """
        if self.df is None:
            return None
        
        cols_lower = [c.lower() for c in self.df.columns]
        
        # Détection ventes
        sales_keywords = ['sales', 'revenue', 'ventes', 'ca', 'chiffre', 'product', 'produit', 'price', 'prix']
        if any(kw in ' '.join(cols_lower) for kw in sales_keywords):
            return 'sales'
        
        # Détection RH
        hr_keywords = ['employee', 'salary', 'salaire', 'department', 'département', 'hire', 'embauche', 'job', 'poste']
        if any(kw in ' '.join(cols_lower) for kw in hr_keywords):
            return 'hr'
        
        # Détection Finance
        finance_keywords = ['amount', 'montant', 'transaction', 'balance', 'solde', 'account', 'compte', 'debit', 'credit']
        if any(kw in ' '.join(cols_lower) for kw in finance_keywords):
            return 'finance'
        
        return None
    
    def get_domain_suggestions(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retourne des suggestions spécifiques au domaine détecté.
        """
        domain = self.detect_domain()
        if domain and domain in self.DOMAIN_TEMPLATES:
            return [
                {'text': s, 'type': 'domain', 'domain': domain, 'icon': '🎯'}
                for s in self.DOMAIN_TEMPLATES[domain][:limit]
            ]
        return []


def get_suggestions(
    df: Optional[pd.DataFrame] = None,
    exchanges: Optional[List[Dict]] = None,
    user_level: str = 'expert',
    limit: int = 6
) -> List[Dict[str, Any]]:
    """
    Fonction utilitaire pour générer des suggestions.
    """
    suggester = SmartSuggestions(df, exchanges, user_level)
    return suggester.generate(limit)


def get_followup_suggestions(
    last_question: str,
    last_result: Any,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Fonction utilitaire pour générer des suggestions de suivi.
    """
    suggester = SmartSuggestions()
    return suggester.generate_followup(last_question, last_result, limit)
