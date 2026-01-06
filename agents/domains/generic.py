from __future__ import annotations

from typing import Any, Dict, List

from agents.base import BaseAgent


class GenericAgent(BaseAgent):
    name = "Generic"
    domain = "generic"
    description = "Agent polyvalent pour datasets non specialises"
    supported_tasks = ["aggregation", "filtering", "statistics", "export"]

    def build_agent_prompt(self, context: Dict[str, Any]) -> str:
        # Keep minimal: core.prompt_builder already enforces the hard rules.
        _ = context
        return ""

    def suggest_followups(self, context: Dict[str, Any]) -> List[str]:
        _ = context
        return [
            "Quels sont les indicateurs principaux (moyennes, min/max) pour les colonnes numeriques ?",
            "Peux-tu segmenter les resultats par une colonne categorielle pertinente ?",
            "Y a-t-il des valeurs manquantes ou doublons importants a traiter ?",
        ]

