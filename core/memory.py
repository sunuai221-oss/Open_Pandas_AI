# core/memory.py

"""
Module de mémoire de session amélioré pour Open Pandas-AI.
Gère le contexte conversationnel avec métadonnées enrichies.
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import copy


class SessionMemory:
    """
    Gestionnaire de mémoire de session avec support de métadonnées enrichies.
    
    Fonctionnalités:
    - Stockage des échanges user/assistant avec timestamps
    - Métadonnées par message (fichier, résultat summary, durée)
    - Export/import JSON
    - Contexte formaté pour prompts LLM
    - Persistance DB optionnelle
    """
    
    def __init__(self, key: str = "chat_history"):
        """
        Initialise la mémoire de session.
        
        Args:
            key: Clé de stockage dans st.session_state
        """
        self.key = key
        if self.key not in st.session_state:
            st.session_state[self.key] = []
    
    def append(
        self,
        role: str,
        content: str,
        timestamp: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        file_name: Optional[str] = None,
        result_summary: Optional[str] = None,
        question_id: Optional[int] = None
    ):
        """
        Ajoute un message à la mémoire avec métadonnées enrichies.
        
        Args:
            role: 'user' ou 'assistant'
            content: Contenu du message
            timestamp: Horodatage ISO (auto-généré si None)
            meta: Métadonnées additionnelles
            file_name: Nom du fichier analysé
            result_summary: Résumé du résultat (pour assistant)
            question_id: ID de la question en DB
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        msg = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        # Métadonnées enrichies
        if meta:
            msg["meta"] = meta
        if file_name:
            msg["file_name"] = file_name
        if result_summary:
            msg["result_summary"] = result_summary
        if question_id:
            msg["question_id"] = question_id
        
        st.session_state[self.key].append(msg)
    
    def get_last(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Renvoie les n derniers messages.
        
        Args:
            n: Nombre de messages à récupérer
            
        Returns:
            Liste des n derniers messages
        """
        return st.session_state[self.key][-n:]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Renvoie tous les messages de la session."""
        return st.session_state[self.key]
    
    def as_string(self, last_n: Optional[int] = None, include_meta: bool = False) -> str:
        """
        Formate les derniers échanges pour un prompt LLM.
        
        Args:
            last_n: Nombre de messages (None = tous)
            include_meta: Inclure les métadonnées
            
        Returns:
            Chaîne formatée des échanges
        """
        messages = self.get_last(last_n) if last_n else self.get_all()
        
        lines = []
        for m in messages:
            role = m.get('role', 'unknown')
            content = m.get('content', '')
            
            if include_meta:
                timestamp = m.get('timestamp', '')
                file_name = m.get('file_name', '')
                meta_str = f" [{timestamp}]" if timestamp else ""
                meta_str += f" (fichier: {file_name})" if file_name else ""
                lines.append(f"{role}{meta_str}: {content}")
            else:
                lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def get_context_for_prompt(self, last_n: int = 3, max_chars: int = 2000) -> str:
        """
        Génère un contexte optimisé pour les prompts LLM.
        
        Args:
            last_n: Nombre de messages à inclure
            max_chars: Limite de caractères
            
        Returns:
            Contexte formaté pour le prompt
        """
        messages = self.get_last(last_n)
        
        if not messages:
            return ""
        
        context_lines = ["Contexte des échanges précédents:"]
        
        for msg in messages:
            role = "Utilisateur" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')[:500]  # Limiter chaque message
            
            # Ajouter résumé si disponible
            summary = msg.get('result_summary', '')
            if summary:
                context_lines.append(f"- {role}: {content}")
                context_lines.append(f"  (Résultat: {summary})")
            else:
                context_lines.append(f"- {role}: {content}")
        
        context = "\n".join(context_lines)
        
        # Respecter la limite de caractères
        if len(context) > max_chars:
            context = context[:max_chars] + "..."
        
        return context
    
    def get_user_questions(self) -> List[str]:
        """
        Récupère uniquement les questions de l'utilisateur.
        
        Returns:
            Liste des questions
        """
        return [
            m.get('content', '')
            for m in st.session_state[self.key]
            if m.get('role') == 'user'
        ]
    
    def get_topics(self) -> List[str]:
        """
        Extrait les sujets principaux abordés (pour suggestions).
        
        Returns:
            Liste des mots-clés/sujets
        """
        questions = self.get_user_questions()
        
        # Mots-clés à ignorer
        stopwords = {'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 
                     'qui', 'que', 'quoi', 'comment', 'combien', 'quel', 'quelle',
                     'est', 'sont', 'dans', 'pour', 'par', 'avec', 'sur', 'en'}
        
        topics = []
        for q in questions:
            words = q.lower().split()
            topics.extend([w for w in words if len(w) > 3 and w not in stopwords])
        
        # Retourner les mots les plus fréquents
        from collections import Counter
        counter = Counter(topics)
        return [word for word, _ in counter.most_common(10)]
    
    def clear(self):
        """Efface la mémoire de session."""
        st.session_state[self.key] = []
    
    def export(self) -> List[Dict[str, Any]]:
        """
        Export JSON/serialisable de la mémoire.
        
        Returns:
            Copie profonde de la mémoire
        """
        return copy.deepcopy(st.session_state[self.key])
    
    def import_history(self, history: List[Dict[str, Any]]):
        """
        Recharge une mémoire sauvegardée.
        
        Args:
            history: Liste de messages à importer
        """
        st.session_state[self.key] = copy.deepcopy(history)
    
    def to_json(self) -> str:
        """
        Exporte la mémoire en JSON string.
        
        Returns:
            String JSON
        """
        return json.dumps(self.export(), ensure_ascii=False, indent=2)
    
    def from_json(self, json_str: str):
        """
        Importe la mémoire depuis un JSON string.
        
        Args:
            json_str: String JSON à importer
        """
        history = json.loads(json_str)
        self.import_history(history)
    
    @property
    def count(self) -> int:
        """Nombre de messages en mémoire."""
        return len(st.session_state.get(self.key, []))
    
    @property
    def is_empty(self) -> bool:
        """Vérifie si la mémoire est vide."""
        return self.count == 0
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Calcule les statistiques de la session.
        
        Returns:
            Dict avec les statistiques
        """
        messages = self.get_all()
        user_msgs = [m for m in messages if m.get('role') == 'user']
        assistant_msgs = [m for m in messages if m.get('role') == 'assistant']
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_msgs),
            'assistant_messages': len(assistant_msgs),
            'files_mentioned': list(set(
                m.get('file_name') for m in messages if m.get('file_name')
            )),
            'question_ids': list(set(
                m.get('question_id') for m in messages if m.get('question_id')
            ))
        }


# Fonction utilitaire pour obtenir la mémoire globale
def get_memory(key: str = "chat_history") -> SessionMemory:
    """
    Retourne l'instance de mémoire pour la clé donnée.
    
    Args:
        key: Clé de stockage
        
    Returns:
        Instance SessionMemory
    """
    return SessionMemory(key=key)
