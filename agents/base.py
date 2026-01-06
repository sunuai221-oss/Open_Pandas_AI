from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

import pandas as pd


class BaseAgent(ABC):
    """
    Minimal agent interface used to inject domain/business guidance into the user prompt.

    Notes:
    - The LLM must still output ONLY code between <startCode>/<endCode>.
    - Agents should NOT require network/filesystem access.
    """

    name: str = "Generic"
    domain: str = "generic"  # ecommerce|crm|hr|finance|generic
    description: str = "Default generic agent"
    supported_tasks: List[str] = []
    toolbox: Optional[Dict[str, Callable[..., Any]]] = None

    @abstractmethod
    def build_agent_prompt(self, context: Dict[str, Any]) -> str:
        """
        Return agent instructions to inject BEFORE the main prompt built by core.prompt_builder.build_prompt().
        """

    @abstractmethod
    def suggest_followups(self, context: Dict[str, Any]) -> List[str]:
        """Return follow-up question suggestions for the current context."""

    def preflight_checks(self, df: pd.DataFrame, schema: Dict[str, Any]) -> List[str]:
        """
        Optional checks to run client-side (NOT in sandbox) before asking the LLM.
        Return a list of human-readable warnings.
        """

        _ = (df, schema)
        return []

    def analysis_plan(self, user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional structured analysis plan.
        This plan is rendered as TEXT in the prompt; we do NOT require JSON output from the LLM.
        """

        _ = (user_query, context)
        return {}

