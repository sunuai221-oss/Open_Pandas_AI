from __future__ import annotations

from typing import Any, Dict, List

from agents.base import BaseAgent

ECOMMERCE_PROMPT_FR = """\
AGENT E-COMMERCE (priorite haute)
- Distingue commandes (orders) / lignes de commande (order lines) / produits / clients si les colonnes le suggerent.
- Pour CA: prefere amount/total/revenue; attention aux lignes (qty * unit_price) vs montant deja calcule.
- Segmente souvent par date (order_date), produit, categorie, client et pays.
- Sur les stocks: verifie valeurs negatives et ruptures (stock==0).
"""

ECOMMERCE_PROMPT_EN = """\
E-COMMERCE AGENT (high priority)
- Distinguish orders vs order lines vs products vs customers when columns suggest it.
- For revenue: prefer amount/total/revenue; watch out for line totals (qty*unit_price) vs precomputed totals.
- Segment by date (order_date), product, category, customer and country.
- For inventory: check negatives and stockouts (stock==0).
"""


class EcommerceAgent(BaseAgent):
    name = "E-commerce"
    domain = "ecommerce"
    description = "Agent specialise E-commerce (ventes, commandes, produits, stock)"
    supported_tasks = ["sales", "customers", "products", "inventory"]

    def build_agent_prompt(self, context: Dict[str, Any]) -> str:
        lang = (context.get("language") or "fr").lower()
        return ECOMMERCE_PROMPT_FR if lang == "fr" else ECOMMERCE_PROMPT_EN

    def suggest_followups(self, context: Dict[str, Any]) -> List[str]:
        _ = context
        return [
            "Quel est le chiffre d'affaires par mois et par categorie ?",
            "Quels sont les top 10 produits par ventes (montant ou quantite) ?",
            "Quels clients sont les plus contributeurs (top 10) ?",
        ]

