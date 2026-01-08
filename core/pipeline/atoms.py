from __future__ import annotations

import numbers
from time import perf_counter
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from agents.base import BaseAgent
from agents.detector import detect_domain
from core.business_examples import get_domain_assets
from core.code_security import is_code_safe
from core.executor import execute_code
from core.formatter import format_result_with_validation
from core.intention_detector import IntentionDetector
from core.llm import call_llm
from core.prompt_builder import build_prompt_with_agent
from core.pipeline.schemas import (
    AgentPolicy,
    CodeExtraction,
    DomainAssets,
    DomainDetection,
    ExecutionResult,
    IntentDetection,
    LLMRawResponse,
    PromptBuildInput,
    PromptBuildOutput,
    ResultValidation,
    SecurityCheck,
)


def domain_detector_atom(df: pd.DataFrame) -> DomainDetection:
    detection = detect_domain(df)
    return DomainDetection(
        domain=detection.domain,
        confidence=detection.confidence,
        reasons=list(detection.reasons or []),
        matched_columns=list(detection.matched_columns or []),
        matched_example_key=detection.matched_example_key,
    )


def intent_detector_atom(question: str) -> IntentDetection:
    all_flags = IntentionDetector.detect_all(question)
    primary = IntentionDetector.detect_primary(question)
    instructions = IntentionDetector.get_instructions(all_flags)
    return IntentDetection(all_flags=all_flags, primary=primary, prompt_instructions=instructions)


def agent_policy_atom(agent: Optional[BaseAgent], question: str, context: Dict[str, Any]) -> AgentPolicy:
    if not agent:
        return AgentPolicy(agent_prompt="", agent_plan=None, domain_assets=None)
    agent_prompt = agent.build_agent_prompt(context) or ""
    agent_plan = agent.analysis_plan(question, context) or None
    assets = get_domain_assets(agent.domain) or {}
    domain_assets = DomainAssets(**assets) if assets else None
    return AgentPolicy(agent_prompt=agent_prompt, agent_plan=agent_plan, domain_assets=domain_assets)


def prompt_builder_atom(prompt_input: PromptBuildInput) -> PromptBuildOutput:
    prompt = build_prompt_with_agent(
        df=prompt_input.df,
        question=prompt_input.question,
        context=prompt_input.context or "",
        available_sheets=prompt_input.available_sheets,
        user_level=prompt_input.user_level,
        detected_skills=prompt_input.detected_skills,
        data_dictionary=prompt_input.data_dictionary,
        business_context=prompt_input.business_context,
        agent_prompt=prompt_input.agent_prompt,
        agent_plan=prompt_input.agent_plan,
        domain_assets=prompt_input.domain_assets,
    )
    return PromptBuildOutput(prompt=prompt, version="v1")


def llm_call_atom(prompt: str, provider: Optional[str], model: Optional[str]) -> LLMRawResponse:
    start = perf_counter()
    content = call_llm(prompt, model=model, provider=provider)
    latency_ms = (perf_counter() - start) * 1000.0
    return LLMRawResponse(content=content, provider=provider, model=model, latency_ms=latency_ms)


def llm_parse_atom(raw: LLMRawResponse) -> CodeExtraction:
    content = raw.content or ""
    code, method = _extract_code(content)
    warnings = []
    if not code.strip():
        warnings.append("Empty code extracted from LLM response.")
    return CodeExtraction(code=code, method=method, warnings=warnings)


def security_atom(code: str) -> SecurityCheck:
    is_safe, reason = is_code_safe(code)
    return SecurityCheck(is_safe=is_safe, reason=reason or "")


def execute_atom(code: str, df: pd.DataFrame) -> ExecutionResult:
    result = execute_code(code, df)
    if _is_error_result(result):
        return ExecutionResult(
            status="error",
            result=result,
            result_type="error",
            error_message=str(result),
            preview=None,
            can_export_excel=False,
            can_generate_chart=False,
        )

    result_type = _classify_result(result)
    preview = _preview_result(result)
    can_generate_chart = isinstance(result, pd.DataFrame) and not result.empty
    return ExecutionResult(
        status="success",
        result=result,
        result_type=result_type,
        preview=preview,
        error_message=None,
        can_export_excel=False,
        can_generate_chart=can_generate_chart,
    )


def result_validation_atom(
    result: Any,
    question: str,
    df: pd.DataFrame,
    detected_skills: Optional[list[str]] = None,
) -> ResultValidation:
    validation = format_result_with_validation(
        result=result,
        question=question,
        original_df=df,
        detected_skills=detected_skills,
    )
    return ResultValidation(**validation)


def _extract_code(content: str) -> Tuple[str, str]:
    start_tag = "<startCode>"
    end_tag = "<endCode>"
    start = content.find(start_tag)
    if start != -1:
        end = content.find(end_tag, start + len(start_tag))
        if end != -1:
            return content[start + len(start_tag):end].strip(), "tagged"
    return content.strip(), "direct"


def _is_error_result(result: Any) -> bool:
    if not isinstance(result, str):
        return False
    lower = result.strip().lower()
    return lower.startswith("error") or lower.startswith("erreur")


def _classify_result(result: Any) -> str:
    if isinstance(result, pd.DataFrame):
        return "dataframe"
    if isinstance(result, pd.Series):
        return "series"
    if isinstance(result, bool):
        return "bool"
    if isinstance(result, numbers.Integral):
        return "int"
    if isinstance(result, numbers.Real):
        return "float"
    if isinstance(result, (list, tuple, dict)):
        return "collection"
    if isinstance(result, str):
        return "string"
    return "other"


def _preview_result(result: Any) -> Any:
    if isinstance(result, pd.DataFrame):
        return result.head(5)
    if isinstance(result, pd.Series):
        return result.head(10)
    if isinstance(result, (list, tuple)):
        return result[:10]
    if isinstance(result, dict):
        return dict(list(result.items())[:10])
    if isinstance(result, str):
        return result[:500]
    return result
