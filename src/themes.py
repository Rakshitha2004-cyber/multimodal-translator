# themes.py
# themes.py

import streamlit as st

LIGHT_THEME = """
<style>
/* Whole app background */
.stApp {
    background: linear-gradient(180deg, #f5faff 0%, #ffffff 40%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #e3f2fd !important;
    border-right: 1px solid #bbdefb;
}

/* Page title */
h1 {
    color: #0d47a1 !important;
}

/* Subheaders */
h2, h3, h4 {
    color: #1565c0 !important;
}

/* Tabs underline color */
button[role="tab"][aria-selected="true"] {
    border-bottom: 3px solid #e53935 !important;
}

/* Primary buttons */
button[kind="primary"] {
    border-radius: 999px !important;
    font-weight: 600 !important;
}

/* Cards like upload boxes */
[data-testid="stFileUploader"] {
    background-color: #ffffffaa;
    border-radius: 16px;
    padding: 0.5rem;
}
</style>
"""

DARK_THEME = """
<style>
/* Whole app background */
.stApp {
    background: radial-gradient(circle at top, #1f2933 0%, #050816 55%, #020308 100%);
    color: #f5f5f5;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827 !important;
    color: #f9fafb !important;
    border-right: 1px solid #374151;
}

/* Page title */
h1 {
    color: #e5e7eb !important;
}

/* Subheaders */
h2, h3, h4 {
    color: #93c5fd !important;
}

/* Tabs */
button[role="tab"] {
    color: #9ca3af !important;
}
button[role="tab"][aria-selected="true"] {
    color: #f97316 !important;
    border-bottom: 3px solid #f97316 !important;
}

/* Primary buttons */
button[kind="primary"] {
    background: #f97316 !important;
    color: #111827 !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
}

/* File uploader card */
[data-testid="stFileUploader"] {
    background-color: #111827;
    border-radius: 16px;
    padding: 0.5rem;
    border: 1px solid #374151;
}
</style>
"""

def apply_theme(mode: str):
    """Apply the selected theme."""
    if mode == "Dark":
        st.markdown(DARK_THEME, unsafe_allow_html=True)
    else:
        st.markdown(LIGHT_THEME, unsafe_allow_html=True)
