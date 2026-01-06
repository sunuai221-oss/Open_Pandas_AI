from __future__ import annotations

from typing import Any, Dict, List

from agents.base import BaseAgent

HR_PROMPT_FR = """\
AGENT RH (priorite haute)
- Donnees potentiellement sensibles: evite toute re-identification et sois prudent sur les analyses individuelles.
- Si salary/remuneration existe: verifie valeurs negatives/zero et fais attention aux outliers.
- Pour anciennete: utilise une colonne date d'embauche si disponible (hire_date / date_embauche).
- Segmente souvent par department, job_title, status si present.
"""

HR_PROMPT_EN = """\
HR AGENT (high priority)
- Potentially sensitive data: avoid re-identification and be cautious with individual-level outputs.
- If salary/compensation exists: check negatives/zeros and watch outliers.
- For tenure: use hire date if available (hire_date).
- Often segment by department, job_title, status when present.
"""


class HRAgent(BaseAgent):
    name = "HR"
    domain = "hr"
    description = "Agent specialise RH (effectifs, salaires, anciennete, departements)"
    supported_tasks = ["headcount", "compensation", "tenure", "attrition"]

    def build_agent_prompt(self, context: Dict[str, Any]) -> str:
        lang = (context.get("language") or "fr").lower()
        return HR_PROMPT_FR if lang == "fr" else HR_PROMPT_EN

    def suggest_followups(self, context: Dict[str, Any]) -> List[str]:
        _ = context
        return [
            "Quel est le salaire moyen/median par departement et poste ?",
            "Quelle est la repartition des effectifs par departement et statut ?",
            "Quelle est l'anciennete moyenne par departement ?",
        ]

