"""
CSS generator for theme tokens and Streamlit overrides.
"""

import streamlit as st

from components.design_tokens import DESIGN_TOKENS, get_all_colors, get_radius, get_spacing


def generate_css_variables(theme: str = "dark") -> str:
    colors = get_all_colors(theme)
    lines = [":root {"]
    for key, value in colors.items():
        lines.append(f"  --color-{key.replace('_', '-')}: {value};")
    for key, value in DESIGN_TOKENS["spacing"].items():
        lines.append(f"  --space-{key}: {value};")
    for key, value in DESIGN_TOKENS["radii"].items():
        lines.append(f"  --radius-{key}: {value};")
    for key, value in DESIGN_TOKENS["shadows"].items():
        lines.append(f"  --shadow-{key}: {value};")
    lines.append("}")
    return "\n".join(lines)


def generate_base_styles() -> str:
    return """
.card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
  color: var(--color-text-primary);
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}
.alert {
  padding: var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}
.section-header {
  margin-bottom: var(--space-md);
  color: var(--color-text-primary);
}
"""


def generate_streamlit_overrides() -> str:
    return """
div.stButton > button {
  background: #000000;
  color: white;
  border: none;
  border-radius: var(--radius-md);
  padding: 0.4rem 0.9rem;
}
div.stButton > button:hover {
  background: #111111;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div {
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}
.stTabs [data-baseweb="tab"] {
  color: var(--color-text-secondary);
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
  color: var(--color-text-primary);
}
"""


def generate_complete_css(theme: str = "dark") -> str:
    return "\n".join(
        [
            generate_css_variables(theme),
            generate_base_styles(),
            generate_streamlit_overrides(),
        ]
    )


def inject_custom_css(theme: str = "dark") -> None:
    css = generate_complete_css(theme)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
