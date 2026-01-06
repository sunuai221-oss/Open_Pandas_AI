"""
LLM provider selector UI.
"""

import os
import streamlit as st

from core.llm import list_models
from core.session_manager import get_session_manager


PROVIDERS = [
    ("lmstudio", "Local - LM Studio"),
    ("ollama", "Local - Ollama"),
    ("codestral", "Cloud - Codestral (requires API key)"),
]

# Set OFFLINE_ONLY=true in env to completely hide cloud providers
_OFFLINE_ONLY = os.getenv("OFFLINE_ONLY", "").lower() in ("1", "true", "yes")


def render_llm_provider_selector(title: str = "LLM Provider") -> None:
    session = get_session_manager()
    st.markdown(f"### {title}")

    # Filter providers when OFFLINE_ONLY mode is enabled
    available_providers = [(k, l) for k, l in PROVIDERS if not (_OFFLINE_ONLY and k == "codestral")]
    provider_labels = {key: label for key, label in available_providers}
    provider_keys = [key for key, _ in available_providers]

    current_provider = session.llm_provider if session.llm_provider in provider_keys else "lmstudio"
    provider = st.selectbox(
        "Provider",
        options=provider_keys,
        index=provider_keys.index(current_provider) if current_provider in provider_keys else 0,
        format_func=lambda key: provider_labels.get(key, key),
        key="llm_provider_select",
    )

    if _OFFLINE_ONLY:
        st.caption("Mode 100% local activé (OFFLINE_ONLY=true)")

    if provider != session.llm_provider:
        session.set_llm_provider(provider)
        session.set_llm_model("")

    col1, col2 = st.columns([3, 1])
    with col1:
        models = list_models(provider)
    with col2:
        if st.button("Refresh", key="llm_model_refresh", use_container_width=True):
            models = list_models(provider)

    if provider == "codestral" and not models:
        models = ["codestral-latest"]

    _render_provider_status(provider, models)

    model = session.llm_model if session.llm_model in models else (models[0] if models else "")
    if models:
        selected = st.selectbox(
            "Model",
            options=models,
            index=models.index(model) if model in models else 0,
            key="llm_model_select",
        )
        if selected != session.llm_model:
            session.set_llm_model(selected)
    else:
        st.warning("No models detected. Make sure the provider is running.")
        manual = st.text_input(
            "Manual model name",
            value=session.llm_model or "",
            key="llm_model_manual",
            placeholder="ex: llama3.1, mistral, gemma2",
        )
        if manual and manual != session.llm_model:
            session.set_llm_model(manual)


def _render_provider_status(provider: str, models: list) -> None:
    status_ok = False
    detail = ""

    if provider == "codestral":
        api_key = os.getenv("MISTRAL_API_KEY", "")
        if api_key and api_key != "VOTRE_CLE_CODESRAL_ICI":
            status_ok = True
        else:
            detail = "Missing MISTRAL_API_KEY"
    else:
        status_ok = len(models) > 0
        if not status_ok:
            detail = "Provider offline or no models"

    if status_ok:
        st.success("Provider status: OK")
    else:
        st.error(f"Provider status: Offline - {detail}")
