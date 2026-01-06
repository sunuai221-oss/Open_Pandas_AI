from __future__ import annotations

from typing import Any, Dict, List

from agents.base import BaseAgent

FINANCE_PROMPT_FR = """\
AGENT FINANCE (priorite haute)
- Interprete correctement les signes (debit/credit) et verifie les montants negatifs.
- Arrondis les montants a 2 decimales quand tu produis un resultat numerique.
- Pour les analyses temporelles, privilegie un regroupement par mois/trimestre si une colonne date existe.
- Attention aux doublons de transactions et aux montants nuls.
"""

FINANCE_PROMPT_EN = """\
FINANCE AGENT (high priority)
- Correctly interpret signs (debit/credit) and verify negative amounts.
- Round monetary values to 2 decimals when producing numeric outputs.
- For time-based analyses, group by month/quarter if a date column exists.
- Watch for duplicate transactions and zero amounts.
"""


class FinanceAgent(BaseAgent):
    name = "Finance"
    domain = "finance"
    description = "Agent specialise Finance (transactions, reporting, reconciliations)"
    supported_tasks = ["transaction_analysis", "reporting", "reconciliation"]

    def build_agent_prompt(self, context: Dict[str, Any]) -> str:
        lang = (context.get("language") or "fr").lower()
        return FINANCE_PROMPT_FR if lang == "fr" else FINANCE_PROMPT_EN

    def suggest_followups(self, context: Dict[str, Any]) -> List[str]:
        _ = context
        return [
            "Quel est le total des montants par categorie et par mois ?",
            "Peux-tu identifier les top 10 transactions (valeur absolue) ?",
            "Y a-t-il des anomalies (montants nuls, dates manquantes, doublons) ?",
        ]

