# homepage.py

import streamlit as st
from themes import apply_theme


def show_homepage(theme: str):
    apply_theme(theme)

    st.markdown(
        """
        <div class="app-card" style="margin-top:0.8rem;">
          <div style="display:flex; align-items:center; gap:0.8rem;">
            <div style="
                height: 46px; width: 46px;
                border-radius: 999px;
                display:flex; align-items:center; justify-content:center;
                background: radial-gradient(circle at 30% 20%, #22c55e 0, #0ea5e9 50%, #1d4ed8 100%);
                color:white; font-size:1.7rem;">
              🩺
            </div>
            <div>
              <div class="main-title">Multimodal AI Medical Translator</div>
              <div class="main-subtitle">
                Bridging the language gap between doctors and rural patients using speech, text & image understanding.
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown(
            """
            <div class="app-card">
              <h4>Why this project?</h4>
              <p style="font-size:0.9rem; line-height:1.55;">
                In many rural areas, patients are not comfortable with English or even the
                regional language used by doctors. Misunderstanding prescriptions or symptoms
                can directly affect treatment quality.
              </p>
              <p style="font-size:0.9rem; line-height:1.55;">
                This Multimodal AI Medical Translator allows doctors and patients to communicate
                through <b>speech</b>, <b>text</b> and <b>images of prescriptions</b> while supporting 100+ languages,
                making healthcare more inclusive and accessible.
              </p>
              <div style="margin-top:0.3rem;">
                <span class="tag-chip">🌍 100+ languages</span>
                <span class="tag-chip">🎙️ Speech to Speech</span>
                <span class="tag-chip">📝 Handwritten OCR</span>
                <span class="tag-chip">🤝 Doctor–Patient Chat</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="app-card">
              <h4>Core Capabilities</h4>
              <ul style="font-size:0.9rem; padding-left:1.1rem; margin-top:0.4rem;">
                <li>Patient speech ➝ recognized, translated & spoken out in doctor’s language.</li>
                <li>Doctor’s reply ➝ translated & spoken back in patient’s language.</li>
                <li>Text translation across 100+ languages with TTS support.</li>
                <li>Image / prescription OCR for both printed and handwritten text.</li>
                <li>Dedicated doctor–patient conversation mode with history.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="app-card">
              <h4>How to use?</h4>
              <ol style="font-size:0.9rem; padding-left:1.1rem; margin-top:0.4rem;">
                <li>Select your <b>Theme</b> (Light or Dark) from the sidebar.</li>
                <li>Go to <b>Translator</b> for one-way speech / text / image translation.</li>
                <li>Go to <b>Doctor–Patient Chat</b> for back-and-forth conversation.</li>
                <li>Choose the <b>patient</b> & <b>doctor</b> languages from the dropdown.</li>
                <li>Use microphone or upload audio / images depending on the mode.</li>
              </ol>
              <p class="secondary-text">
                Tip: Use headphones during demos so evaluators can clearly hear both voices.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="app-card">
              <h4>Project Highlights</h4>
              <ul style="font-size:0.9rem; padding-left:1.1rem; margin-top:0.4rem;">
                <li>Built entirely with Python & Streamlit.</li>
                <li>Modular design – STT, TTS, Translation & OCR as separate blocks.</li>
                <li>Easy to extend with new languages or models in future.</li>
                <li>Deployed as a real web app using Streamlit Community Cloud.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
st.warning(
    "⚠️ This tool is for communication support only and **does not replace** "
    "professional medical diagnosis or decision-making."
)
