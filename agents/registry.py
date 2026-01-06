from __future__ import annotations

from typing import Dict, List, Tuple, Type

import pandas as pd

from agents.base import BaseAgent
from agents.detector import DetectionResult, detect_domain
from agents.domains import CRMAgent, EcommerceAgent, FinanceAgent, GenericAgent, HRAgent

_AGENTS: Dict[str, BaseAgent] = {}


def register_agent(agent_class: Type[BaseAgent]) -> None:
    """
    Register an agent class by its `domain`.
    """
    agent = agent_class()
    _AGENTS[agent.domain] = agent


def _ensure_defaults_registered() -> None:
    if _AGENTS:
        return
    register_agent(GenericAgent)
    register_agent(FinanceAgent)
    register_agent(HRAgent)
    register_agent(CRMAgent)
    register_agent(EcommerceAgent)


def get_available_agents() -> Dict[str, BaseAgent]:
    _ensure_defaults_registered()
    return dict(_AGENTS)


def get_agent(domain: str) -> BaseAgent:
    _ensure_defaults_registered()
    key = (domain or "").lower()
    if key in _AGENTS:
        return _AGENTS[key]
    return _AGENTS["generic"]


def auto_select_agent(df: pd.DataFrame, schema=None, business_examples=None) -> Tuple[str, float, List[str]]:
    """
    Auto-select an agent based on dataframe/schema.
    Returns: (domain, confidence, reasons)
    """
    _ = (schema, business_examples)
    detection: DetectionResult = detect_domain(df)
    return detection.domain, detection.confidence, detection.reasons

