# realtime.py

import streamlit as st
from stt import speech_to_text
from tts import text_to_speech_file
from translate import translate_text
from themes import apply_theme

def realtime_page(theme):
    apply_theme(theme)

    st.title("🎙️ Real-Time Speech Translator")

    from_lang = st.selectbox("Select Your Language", st.session_state.languages)
    to_lang = st.selectbox("Translate To", st.session_state.languages)

    st.info("🎧 Click Start and begin speaking. The system will automatically translate continuously.")

    if "live" not in st.session_state:
        st.session_state.live = False

    col1, col2 = st.columns(2)

    if col1.button("▶ Start Live Translation"):
        st.session_state.live = True

    if col2.button("⏹ Stop"):
        st.session_state.live = False

    live_text = st.empty()

    if st.session_state.live:
        st.warning("Listening...")

        # Loop simulation (actual continuous STT optional)
        import time
        for i in range(3):
            live_text.write(f"Recognizing speech chunk {i+1}...")
            time.sleep(1)

        st.success("✨ Real-time translation coming next phase (full version).")
