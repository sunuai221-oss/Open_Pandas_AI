"""
Agents package.

Provides:
- Agent base interface (`BaseAgent`)
- Registry helpers (`register_agent`, `get_available_agents`, `get_agent`, `auto_select_agent`)
- Domain detection (`detect_domain`)
"""

from agents.base import BaseAgent
from agents.registry import register_agent, get_available_agents, get_agent, auto_select_agent
from agents.detector import DetectionResult, detect_domain

__all__ = [
    "BaseAgent",
    "register_agent",
    "get_available_agents",
    "get_agent",
    "auto_select_agent",
    "DetectionResult",
    "detect_domain",
]

