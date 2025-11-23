# themes.py

import streamlit as st


def _inject_base_css():
    """Shared CSS for cards, buttons, tags etc."""
    if st.session_state.get("base_css_loaded"):
        return

    st.markdown(
        """
        <style>
        /* Global background + layout tweaks */
        .stApp {
            background: radial-gradient(circle at top left, #eff6ff 0, #f9fafb 35%, #ffffff 100%);
        }

        /* Top title spacing */
        .main-title {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            margin-bottom: 0.2rem;
        }
        .main-subtitle {
            font-size: 0.95rem;
            color: #6b7280;
            margin-bottom: 1.5rem;
        }

        /* Generic card */
        .app-card {
            border-radius: 20px;
            padding: 1.1rem 1.3rem;
            margin-bottom: 1rem;
            background: rgba(255,255,255,0.9);
            border: 1px solid rgba(148,163,184,0.55);
            box-shadow: 0 18px 36px rgba(15,23,42,0.08);
            backdrop-filter: blur(12px);
        }

        .app-card h4 {
            margin-top: 0;
            margin-bottom: 0.4rem;
            font-size: 1.05rem;
            font-weight: 600;
            color: #0f172a;
        }

        .tag-chip {
            display: inline-flex;
            align-items: center;
            padding: 0.18rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            background: rgba(59,130,246,0.1);
            color: #1d4ed8;
            margin-right: 0.3rem;
        }

        .pill-label {
            display: inline-flex;
            align-items: center;
            padding: 0.16rem 0.5rem;
            border-radius: 999px;
            font-size: 0.78rem;
            background: rgba(15,23,42,0.04);
            color: #374151;
            margin-bottom: 0.4rem;
        }

        .primary-button > button {
            border-radius: 999px !important;
            font-weight: 600 !important;
            padding: 0.45rem 1.5rem !important;
            box-shadow: 0 10px 20px rgba(220,38,38,0.35) !important;
        }

        .secondary-text {
            font-size: 0.8rem;
            color: #6b7280;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["base_css_loaded"] = True


def apply_theme(theme: str):
    """
    Apply light / dark feel using simple CSS.
    IMPORTANT: Do NOT call st.set_page_config here (only from main_app)
    """
    _inject_base_css()

    if theme.lower() == "dark":
        st.markdown(
            """
            <style>
            .stApp {
                background: radial-gradient(circle at top left, #0f172a 0, #020617 40%, #020617 100%);
                color: #e5e7eb;
            }
            .app-card {
                background: rgba(15,23,42,0.9);
                border-color: rgba(148,163,184,0.55);
                box-shadow: 0 18px 40px rgba(0,0,0,0.7);
            }
            .app-card h4 { color: #e5e7eb; }
            .main-title { color: #e5e7eb; }
            .main-subtitle { color: #9ca3af; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Light mode tweaks (already mostly handled by base CSS)
        st.markdown(
            """
            <style>
            .main-title { color: #0f172a; }
            </style>
            """,
            unsafe_allow_html=True,
        )
