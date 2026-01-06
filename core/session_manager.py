"""
Gestionnaire de session centralisé pour Open Pandas-AI.
Gère l'état partagé entre les pages multi-pages Streamlit.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class SessionManager:
    """
    Gestionnaire centralisé de l'état de session.
    Synchronise les données entre les différentes pages Streamlit.
    """
    
    # Clés de session standardisées
    KEYS = {
        'session_id': 'session_id',
        'session_start': 'session_start',
        'df': 'df',
        'df_name': 'df_name',
        'df_norm': 'df_norm',
        'all_sheets': 'all_sheets',
        'selected_sheet': 'selected_sheet',
        'uploaded_files': 'uploaded_files',
        'exchanges': 'exchanges',
        'user_id': 'user_id',
        'file_id': 'file_id',
        'mode': 'mode',
        'user_level': 'user_level',
        'language': 'language',
        'theme': 'theme',
        'show_code': 'show_code',
        'display_max_rows': 'display_max_rows',
        'quality_score': 'quality_score',
        'validation_result': 'validation_result',
        'llm_provider': 'llm_provider',
        'llm_model': 'llm_model',
        'business_domain': 'business_domain',
        'business_example_key': 'business_example_key',
        # Agent orchestration (new)
        'selected_agent_mode': 'selected_agent_mode',  # "auto"|"finance"|"hr"|"crm"|"ecommerce"|...
        'detected_agent': 'detected_agent',
        'detection_confidence': 'detection_confidence',
        'detection_reasons': 'detection_reasons',
    }
    
    def __init__(self):
        """Initialise le gestionnaire de session."""
        self._init_session()
    
    def _init_session(self):
        """Initialise les valeurs par défaut de la session."""
        defaults = {
            'session_id': str(uuid.uuid4()),
            'session_start': datetime.now(),
            'df': None,
            'df_name': None,
            'df_norm': None,
            'all_sheets': None,
            'selected_sheet': None,
            'uploaded_files': [],
            'exchanges': [],
            'user_id': None,
            'file_id': None,
            'mode': 'question',
            'user_level': 'expert',  # 'beginner' ou 'expert'
            'language': 'fr',
            'theme': 'dark',
            'show_code': True,
            'display_max_rows': 25,
            'quality_score': None,
            'validation_result': None,
            'llm_provider': 'lmstudio',
            'llm_model': 'codestral-latest',
            'business_domain': 'auto',
            'business_example_key': None,
            # Agent orchestration (new)
            'selected_agent_mode': 'auto',
            'detected_agent': None,
            'detection_confidence': 0.0,
            'detection_reasons': [],
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    # ============ GETTERS ============
    
    @property
    def session_id(self) -> str:
        return st.session_state.get('session_id', '')
    
    @property
    def session_duration_minutes(self) -> int:
        start = st.session_state.get('session_start', datetime.now())
        return int((datetime.now() - start).total_seconds() / 60)
    
    @property
    def df(self) -> Optional[pd.DataFrame]:
        return st.session_state.get('df')
    
    @property
    def df_name(self) -> Optional[str]:
        return st.session_state.get('df_name')

    @property
    def df_norm(self) -> Optional[pd.DataFrame]:
        return st.session_state.get('df_norm')
    
    @property
    def has_data(self) -> bool:
        return st.session_state.get('df') is not None
    
    @property
    def all_sheets(self) -> Optional[Dict[str, pd.DataFrame]]:
        return st.session_state.get('all_sheets')
    
    @property
    def selected_sheet(self) -> Optional[str]:
        return st.session_state.get('selected_sheet')
    
    @property
    def exchanges(self) -> List[Dict[str, Any]]:
        return st.session_state.get('exchanges', [])
    
    @property
    def exchange_count(self) -> int:
        return len(self.exchanges)
    
    @property
    def user_level(self) -> str:
        return st.session_state.get('user_level', 'expert')
    
    @property
    def language(self) -> str:
        return st.session_state.get('language', 'fr')
    
    @property
    def show_code(self) -> bool:
        return st.session_state.get('show_code', True)

    @property
    def display_max_rows(self):
        return st.session_state.get('display_max_rows', 25)
    
    @property
    def quality_score(self) -> Optional[float]:
        return st.session_state.get('quality_score')
    
    @property
    def validation_result(self) -> Optional[Dict]:
        return st.session_state.get('validation_result')

    @property
    def llm_provider(self) -> str:
        return st.session_state.get('llm_provider', 'codestral')

    @property
    def llm_model(self) -> str:
        return st.session_state.get('llm_model', 'codestral-latest')

    @property
    def business_domain(self) -> str:
        return st.session_state.get('business_domain', 'auto')

    @property
    def business_example_key(self) -> Optional[str]:
        return st.session_state.get('business_example_key')

    @property
    def selected_agent_mode(self) -> str:
        return st.session_state.get('selected_agent_mode', 'auto')

    @property
    def detected_agent(self) -> Optional[str]:
        return st.session_state.get('detected_agent')

    @property
    def detection_confidence(self) -> float:
        return float(st.session_state.get('detection_confidence', 0.0) or 0.0)

    @property
    def detection_reasons(self) -> List[str]:
        return st.session_state.get('detection_reasons', []) or []
    
    # ============ SETTERS ============
    
    def set_dataframe(self, df: pd.DataFrame, name: str = None):
        """Définit le DataFrame actif."""
        st.session_state['df'] = df
        st.session_state['df_name'] = name
        st.session_state['df_norm'] = None
        # Reset validation when data changes
        st.session_state['quality_score'] = None
        st.session_state['validation_result'] = None
    
    def set_df_norm(self, df: Optional[pd.DataFrame]):
        """Definit le DataFrame normalise pour l'analyse."""
        st.session_state['df_norm'] = df

    def set_all_sheets(self, sheets: Dict[str, pd.DataFrame]):
        """Définit toutes les feuilles Excel."""
        st.session_state['all_sheets'] = sheets
    
    def set_selected_sheet(self, sheet_name: str):
        """Définit la feuille sélectionnée."""
        st.session_state['selected_sheet'] = sheet_name
    
    def set_user_level(self, level: str):
        """Définit le niveau utilisateur ('beginner' ou 'expert')."""
        if level in ['beginner', 'expert']:
            st.session_state['user_level'] = level
    
    def set_language(self, lang: str):
        """Définit la langue ('fr' ou 'en')."""
        if lang in ['fr', 'en']:
            st.session_state['language'] = lang
    
    def set_show_code(self, show: bool):
        """Définit si le code généré doit être affiché."""
        st.session_state['show_code'] = show

    def set_display_max_rows(self, value):
        """Definit le nombre de lignes a afficher dans l'UI."""
        st.session_state['display_max_rows'] = value

    def set_llm_provider(self, provider: str):
        """Définit le provider LLM."""
        st.session_state['llm_provider'] = provider

    def set_llm_model(self, model: str):
        """Définit le modèle LLM."""
        st.session_state['llm_model'] = model

    def set_business_domain(self, domain: str):
        """Définit le domaine métier."""
        st.session_state['business_domain'] = domain

    def set_business_example_key(self, key: Optional[str]):
        """Définit l'exemple métier sélectionné."""
        st.session_state['business_example_key'] = key

    def set_selected_agent_mode(self, mode: str):
        """Définit le mode agent: auto | finance | hr | crm | ecommerce | generic"""
        st.session_state['selected_agent_mode'] = (mode or 'auto').lower()

    def set_agent_detection(self, detected_agent: Optional[str], confidence: float = 0.0, reasons: Optional[List[str]] = None):
        """Stocke la detection d'agent (si mode auto)."""
        st.session_state['detected_agent'] = detected_agent
        st.session_state['detection_confidence'] = float(confidence or 0.0)
        st.session_state['detection_reasons'] = reasons or []
    
    def set_validation_result(self, result: Dict, score: float):
        """Définit le résultat de validation."""
        st.session_state['validation_result'] = result
        st.session_state['quality_score'] = score
    
    def set_user_and_file_ids(self, user_id: int, file_id: int):
        """Définit les IDs utilisateur et fichier pour la DB."""
        st.session_state['user_id'] = user_id
        st.session_state['file_id'] = file_id
    
    # ============ EXCHANGES ============
    
    def add_exchange(self, exchange: Dict[str, Any]):
        """Ajoute un échange à l'historique."""
        if 'exchanges' not in st.session_state:
            st.session_state['exchanges'] = []
        st.session_state['exchanges'].append(exchange)
    
    def get_last_exchanges(self, n: int = 5) -> List[Dict[str, Any]]:
        """Récupère les N derniers échanges."""
        return self.exchanges[-n:] if self.exchanges else []
    
    def clear_exchanges(self):
        """Efface tous les échanges."""
        st.session_state['exchanges'] = []
    
    # ============ NAVIGATION ============
    
    def navigate_to(self, page: str):
        """Navigue vers une page spécifique."""
        st.session_state['mode'] = page
    
    # ============ METRICS ============
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de la session."""
        return {
            'session_id': self.session_id[:8] + '...',
            'duration_minutes': self.session_duration_minutes,
            'exchange_count': self.exchange_count,
            'has_data': self.has_data,
            'data_name': self.df_name,
            'quality_score': self.quality_score,
            'user_level': self.user_level,
        }
    
    # ============ RESET ============
    
    def reset_session(self):
        """Réinitialise la session complète."""
        keys_to_clear = [
            'df', 'df_name', 'df_norm', 'all_sheets', 'selected_sheet',
            'uploaded_files', 'exchanges', 'quality_score', 'validation_result'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                st.session_state[key] = None if key != 'exchanges' else []
    
    def reset_data(self):
        """Réinitialise uniquement les données."""
        st.session_state['df'] = None
        st.session_state['df_name'] = None
        st.session_state['df_norm'] = None
        st.session_state['all_sheets'] = None
        st.session_state['selected_sheet'] = None
        st.session_state['quality_score'] = None
        st.session_state['validation_result'] = None


# Instance singleton
_session_manager = None


def get_session_manager() -> SessionManager:
    """Retourne l'instance singleton du gestionnaire de session."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
