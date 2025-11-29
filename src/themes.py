# themes.py – light/dark premium theme for the whole app

import streamlit as st


def apply_theme(mode: str = "Light") -> None:
    """
    Inject global CSS for light/dark premium theme.
    `mode` is "Light" or "Dark".
    """
    is_dark = (mode.lower() == "dark")

    bg = "#020617" if is_dark else "#f3f4f6"
    card_bg = "rgba(15,23,42,0.92)" if is_dark else "rgba(255,255,255,0.96)"
    card_border = "rgba(148,163,184,0.65)" if is_dark else "rgba(148,163,184,0.55)"
    text_main = "#e5e7eb" if is_dark else "#0f172a"
    text_secondary = "#9ca3af" if is_dark else "#6b7280"

    st.markdown(
        f"""
        <style>
        /* Global background */
        .stApp {{
            background: radial-gradient(circle at top, #38bdf8 0, transparent 50%),
                        radial-gradient(circle at bottom, #22c55e 0, transparent 55%),
                        {bg};
            color: {text_main};
        }}

        /* Main content width tweak */
        .block-container {{
            max-width: 1100px;
        }}

        /* Cards used across the app */
        .app-card {{
            background: {card_bg};
            border-radius: 18px;
            border: 1px solid {card_border};
            padding: 1rem 1.2rem;
            box-shadow: 0 10px 30px rgba(15,23,42,0.35);
            backdrop-filter: blur(12px);
            margin-bottom: 0.6rem;
        }}

        .pill-label {{
            display:inline-block;
            padding:0.2rem 0.65rem;
            border-radius:999px;
            font-size:0.75rem;
            letter-spacing:0.08em;
            text-transform:uppercase;
            background: linear-gradient(90deg,#0ea5e9,#22c55e);
            color:white;
            margin-bottom:0.35rem;
        }}

        .main-title {{
            font-size:1.35rem;
            font-weight:700;
            letter-spacing:0.03em;
        }}

        .main-subtitle {{
            font-size:0.85rem;
            color:{text_secondary};
        }}

        .secondary-text {{
            font-size:0.82rem;
            color:{text_secondary};
        }}

        /* Buttons */
        .stButton>button {{
            border-radius:999px;
            padding:0.4rem 0.9rem;
            border:1px solid rgba(148,163,184,0.6);
            font-size:0.9rem;
        }}

        .stButton>button[kind="primary"] {{
            background:linear-gradient(90deg,#0ea5e9,#22c55e);
            color:white;
            border:none;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab"] {{
            font-size:0.9rem;
            padding-top:0.4rem;
            padding-bottom:0.4rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
