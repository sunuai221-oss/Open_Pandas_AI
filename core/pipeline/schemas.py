from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class PipelineBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class DatasetRef(PipelineBase):
    name: Optional[str] = None
    rows: int
    columns: List[str] = Field(default_factory=list)
    shape: Tuple[int, int]

    @classmethod
    def from_df(cls, df: pd.DataFrame, name: Optional[str] = None) -> "DatasetRef":
        columns = [str(c) for c in df.columns]
        rows = int(len(df))
        return cls(name=name, rows=rows, columns=columns, shape=(rows, len(columns)))


class SessionContext(PipelineBase):
    language: str = "fr"
    user_level: str = "expert"
    provider: Optional[str] = None
    model: Optional[str] = None
    memory_text: Optional[str] = None
    business_context_label: Optional[str] = None


class DomainDetection(PipelineBase):
    domain: str
    confidence: float
    reasons: List[str] = Field(default_factory=list)
    matched_columns: List[str] = Field(default_factory=list)
    matched_example_key: Optional[str] = None


class IntentDetection(PipelineBase):
    all_flags: Dict[str, bool] = Field(default_factory=dict)
    primary: List[str] = Field(default_factory=list)
    prompt_instructions: str = ""


class AgentSelection(PipelineBase):
    mode: str
    active_domain: str
    active_agent_name: str
    detection: Optional[DomainDetection] = None


class DomainAssets(PipelineBase):
    typical_questions: List[str] = Field(default_factory=list)
    common_metrics: List[str] = Field(default_factory=list)
    recommended_charts: List[str] = Field(default_factory=list)
    quality_rules: List[str] = Field(default_factory=list)
    business_intents: Dict[str, Any] = Field(default_factory=dict)


class AgentPolicy(PipelineBase):
    agent_prompt: str = ""
    agent_plan: Optional[Dict[str, Any]] = None
    domain_assets: Optional[DomainAssets] = None


class PromptBuildInput(PipelineBase):
    df: pd.DataFrame
    question: str
    context: str = ""
    available_sheets: Optional[List[str]] = None
    user_level: str = "expert"
    detected_skills: Optional[List[str]] = None
    data_dictionary: Optional[Dict[str, Any]] = None
    business_context: Optional[str] = None
    agent_prompt: str = ""
    agent_plan: Optional[Dict[str, Any]] = None
    domain_assets: Optional[Dict[str, Any]] = None


class PromptBuildOutput(PipelineBase):
    prompt: str
    version: str = "v1"


class LLMRawResponse(PipelineBase):
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[float] = None


class CodeExtraction(PipelineBase):
    code: str
    method: str = "direct"
    warnings: List[str] = Field(default_factory=list)


class SecurityCheck(PipelineBase):
    is_safe: bool
    reason: str = ""
    blocked_nodes: List[str] = Field(default_factory=list)


class ExecutionRequest(PipelineBase):
    code: str
    df: pd.DataFrame


class ExecutionResult(PipelineBase):
    status: str
    result: Any = None
    result_type: str = "unknown"
    preview: Any = None
    error_message: Optional[str] = None
    can_export_excel: bool = False
    can_generate_chart: bool = False


class ResultValidation(PipelineBase):
    formatted: Any = None
    warnings: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)
    quality_score: int = 0
    interpretation: str = ""


class PipelineMetrics(PipelineBase):
    llm_latency_ms: Optional[float] = None
    execution_ms: Optional[float] = None
    total_ms: Optional[float] = None
    correction_attempts: int = 0
    correction_applied: bool = False


class PipelineResult(PipelineBase):
    status: str
    error_stage: Optional[str] = None
    error_message: Optional[str] = None
    question: str
    dataset: DatasetRef
    session_context: SessionContext
    agent_selection: AgentSelection
    intent_detection: Optional[IntentDetection] = None
    agent_policy: Optional[AgentPolicy] = None
    prompt: Optional[PromptBuildOutput] = None
    llm_raw: Optional[LLMRawResponse] = None
    llm_parse: Optional[CodeExtraction] = None
    security: Optional[SecurityCheck] = None
    execution: Optional[ExecutionResult] = None
    validation: Optional[ResultValidation] = None
    metrics: Optional[PipelineMetrics] = None
