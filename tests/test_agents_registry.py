import pandas as pd

from agents.registry import get_agent, get_available_agents, auto_select_agent


def test_registry_has_defaults_and_fallback_generic():
    agents = get_available_agents()
    assert "generic" in agents
    assert "finance" in agents
    assert "hr" in agents
    assert "crm" in agents
    assert "ecommerce" in agents

    unknown = get_agent("does_not_exist")
    assert unknown.domain == "generic"


def test_auto_select_agent_returns_domain_confidence_reasons():
    df = pd.DataFrame(
        {
            "employee_id": ["E1", "E2"],
            "department": ["IT", "HR"],
            "salary": [50000, 60000],
            "hire_date": ["2020-01-01", "2021-05-01"],
        }
    )
    domain, confidence, reasons = auto_select_agent(df, schema=None, business_examples=None)
    assert domain in ("hr", "generic")
    assert isinstance(confidence, float)
    assert isinstance(reasons, list)

