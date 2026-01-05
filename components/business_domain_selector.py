"""
Business domain selector for explicit dataset context.
"""

import streamlit as st

from core.business_examples import list_available_examples, get_business_example
from core.data_dictionary_manager import DataDictionaryManager
from core.dataset_adapters import normalize_df_for_example
from core.session_manager import get_session_manager


def render_business_domain_selector(title: str = "Business Context") -> None:
    session = get_session_manager()
    st.markdown(f"### {title}")

    domains = list_available_examples()
    domain_keys = sorted(domains.keys())

    domain_options = ["auto"] + domain_keys
    current_domain = session.business_domain if session.business_domain in domain_options else "auto"

    domain = st.selectbox(
        "Domain",
        options=domain_options,
        index=domain_options.index(current_domain),
        format_func=lambda d: d.upper() if d != "auto" else "Auto-detection",
        key="business_domain_select",
    )

    if domain != session.business_domain:
        session.set_business_domain(domain)
        session.set_business_example_key(None)
        session.set_df_norm(None)
        st.session_state.pop('data_dictionary', None)
        st.session_state.pop('dictionary_loaded_at', None)

    if domain == "auto":
        st.caption("Auto-detection enabled")
        return

    examples = domains.get(domain, [])
    example_keys = [e["key"] for e in examples]
    example_labels = {e["key"]: e["name"] for e in examples}

    current_example = session.business_example_key if session.business_example_key in example_keys else None
    if not example_keys:
        st.warning("No example available for this domain.")
        return

    selected = st.selectbox(
        "Dataset",
        options=example_keys,
        index=example_keys.index(current_example) if current_example in example_keys else 0,
        format_func=lambda k: example_labels.get(k, k),
        key="business_example_select",
    )

    selection_changed = selected != session.business_example_key
    if selection_changed:
        session.set_business_example_key(selected)
        if session.has_data:
            session.set_df_norm(normalize_df_for_example(session.df, selected))

    example = get_business_example(selected)
    if example:
        if selection_changed or not st.session_state.get('data_dictionary'):
            dictionary = DataDictionaryManager.normalize_dictionary(example)
            dictionary['detection'] = {
                'method': 'manual_selection',
                'selected_example': example.get('dataset_name', selected),
                'domain': example.get('domain'),
            }
            if session.has_data:
                stats_df = session.df_norm if session.df_norm is not None else session.df
                dictionary = DataDictionaryManager.enrich_with_statistics(dictionary, stats_df)
            DataDictionaryManager.save_to_session(dictionary, st.session_state)
        st.caption(example.get("description", ""))
