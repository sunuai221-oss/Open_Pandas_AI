from __future__ import annotations

from typing import Any, Dict, List

from agents.base import BaseAgent

CRM_PROMPT_FR = """\
AGENT CRM (priorite haute)
- Interprete correctement les etapes du pipeline (stage) et calcule les taux de conversion si pertinent.
- Segmente par source, industry, stage et periode (created_date) quand possible.
- Attention aux doublons de leads/comptes et aux emails manquants.
"""

CRM_PROMPT_EN = """\
CRM AGENT (high priority)
- Correctly interpret pipeline stages and compute conversion rates when relevant.
- Segment by source, industry, stage and time (created_date) when possible.
- Watch for duplicate leads/accounts and missing emails.
"""


class CRMAgent(BaseAgent):
    name = "CRM"
    domain = "crm"
    description = "Agent specialise CRM (leads, pipeline, comptes)"
    supported_tasks = ["lead_analysis", "pipeline", "conversion"]

    def build_agent_prompt(self, context: Dict[str, Any]) -> str:
        lang = (context.get("language") or "fr").lower()
        return CRM_PROMPT_FR if lang == "fr" else CRM_PROMPT_EN

    def suggest_followups(self, context: Dict[str, Any]) -> List[str]:
        _ = context
        return [
            "Quelle est la repartition des leads par source et par stage ?",
            "Quel est le taux de conversion par source (stage final / total) ?",
            "Combien de leads ont ete crees par mois ?",
        ]

