from unittest.mock import patch

import pandas as pd

from core import llm
from core.prompt_builder import build_prompt
from core.code_security import is_code_safe
from core.executor import execute_code
from core.formatter import format_result
from core.consulting import auto_comment_agent


@patch('core.consulting.call_llm')
@patch('core.llm.call_llm')
def test_end_to_end_pipeline_with_mocked_llm(mock_llm_call, mock_consulting_call):
    mock_llm_call.return_value = "result = df['sales'].sum()"
    mock_consulting_call.return_value = "Analyse synthetique"

    df = pd.DataFrame({"sales": [10, 20, 30], "country": ["FR", "US", "FR"]})
    question = "Quelle est la somme des ventes ?"

    prompt = build_prompt(df, question)
    code = llm.call_llm(prompt)
    is_safe, reason = is_code_safe(code)
    assert is_safe, reason

    raw_result = execute_code(code, df)
    assert raw_result == 60

    formatted = format_result(raw_result)
    assert formatted == 60

    comment = auto_comment_agent(df=df, result=raw_result)
    assert comment == "Analyse synthetique"

    assert mock_llm_call.called
    assert mock_consulting_call.called
