# homepage.py – attractive landing / splash section (CRASH SAFE)

import streamlit as st
from pathlib import Path

# OPTIONAL PIL IMPORT (CRASH SAFE)
try:
    from PIL import Image
except Exception:
    Image = None


def show_homepage(theme: str = "Light") -> None:
    """
    Show the home / splash screen with logo, tagline and quick usage steps.
    """
    logo_path = Path(__file__).parent / "assets" / "logo.png"

    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        # -------- LOGO SAFE LOAD -------- #
        if Image and logo_path.exists():
            try:
                logo = Image.open(logo_path)
                st.image(logo, width=140)
            except Exception:
                st.markdown("### 🩺🌍 Multimodal AI Medical Translator")
        else:
            st.markdown("### 🩺🌍 Multimodal AI Medical Translator")

        # -------- INTRO CARD -------- #
        st.markdown(
            """
            <div class="app-card">
              <div class="pill-label">Final-year project</div>
              <div class="main-title">Bridge the language gap in healthcare.</div>
              <div class="main-subtitle" style="margin-top:0.4rem;">
                A multimodal assistant for rural patients and doctors using
                speech, text, and image translation across 100+ languages.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------- HOW TO USE -------- #
        st.markdown(
            """
            <div class="app-card">
              <div class="pill-label">How to use</div>
              <ol style="font-size:0.9rem; margin-left:1rem;">
                <li><b>Translator:</b> Try Speech / Text / Image tabs for one-way translation.</li>
                <li><b>Doctor–Patient Chat:</b> Use both microphones for live two-way dialogue.</li>
                <li><b>Download:</b> Export the conversation as a PDF summary.</li>
              </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        # -------- WHY THIS MATTERS -------- #
        st.markdown(
            """
            <div class="app-card" style="min-height:260px; display:flex; flex-direction:column; justify-content:center;">
              <div style="font-size:0.9rem; margin-bottom:0.5rem;">
                <b>Why this project matters?</b>
              </div>
              <ul style="font-size:0.86rem; padding-left:1.1rem;">
                <li>Rural patients often cannot explain symptoms in the doctor's language.</li>
                <li>Doctors struggle to communicate dosage, precautions, and follow-up.</li>
                <li>This tool enables fast, safe healthcare communication.</li>
              </ul>
              <div style="margin-top:0.7rem; font-size:0.86rem; color:#9ca3af;">
                Demo-ready for viva & presentations – speech, text, image, and conversation modes in one interface.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
