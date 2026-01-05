import os
from typing import List, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

CODESRAL_API_URL = "https://codestral.mistral.ai/v1/chat/completions"
OLLAMA_API_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LM_STUDIO_API_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")

DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "lmstudio")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "codestral-latest")


def _extract_code(content: str) -> str:
    start_tag = "<startCode>"
    start = content.find(start_tag)
    if start != -1:
        end = content.find("<endCode>", start + len(start_tag))
        if end == -1:
            end = content.find("</startCode>", start + len(start_tag))
        if end == -1:
            end = content.find("</endCode>", start + len(start_tag))
        if end != -1:
            return content[start + len(start_tag):end].strip()
    return content.strip()


def _call_codestral(prompt: str, model: str) -> str:
    api_key = os.getenv("MISTRAL_API_KEY") or "VOTRE_CLE_CODESRAL_ICI"
    messages = [
        {"role": "system", "content": "Tu es un expert Python/Pandas. Genere uniquement le code demande."},
        {"role": "user", "content": prompt},
    ]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(
        CODESRAL_API_URL,
        headers=headers,
        json={"model": model, "messages": messages},
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return _extract_code(content)


def _call_ollama(prompt: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Tu es un expert Python/Pandas. Genere uniquement le code demande."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    response = requests.post(
        f"{OLLAMA_API_URL}/api/chat",
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    content = response.json().get("message", {}).get("content", "")
    return _extract_code(content)


def _call_lm_studio(prompt: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Tu es un expert Python/Pandas. Genere uniquement le code demande."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    response = requests.post(
        f"{LM_STUDIO_API_URL}/v1/chat/completions",
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return _extract_code(content)


def call_llm(prompt: str, model: Optional[str] = None, provider: Optional[str] = None) -> str:
    """
    Call the selected LLM provider and extract code between <startCode>/<endCode>.
    provider: 'codestral' | 'ollama' | 'lmstudio'
    """
    selected_provider = (provider or DEFAULT_PROVIDER or "codestral").lower()
    selected_model = model or DEFAULT_MODEL

    if selected_provider == "ollama":
        return _call_ollama(prompt, selected_model)
    if selected_provider in ("lmstudio", "lm_studio", "lm-studio"):
        return _call_lm_studio(prompt, selected_model)
    return _call_codestral(prompt, selected_model)


def list_models(provider: str) -> List[str]:
    """
    Return available models for the provider.
    """
    provider = provider.lower()
    try:
        if provider == "ollama":
            response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m.get("name") for m in models if m.get("name")]
        if provider in ("lmstudio", "lm_studio", "lm-studio"):
            response = requests.get(f"{LM_STUDIO_API_URL}/v1/models", timeout=5)
            response.raise_for_status()
            models = response.json().get("data", [])
            return [m.get("id") for m in models if m.get("id")]
    except Exception:
        return []
    return []
