# conversation.py – Doctor–Patient live chat with PDF export

from __future__ import annotations

import streamlit as st
from fpdf import FPDF

from mic_ui import medical_mic
from translate import translate_text
from stt import speech_to_text
from tts import text_to_speech_file, cleanup_temp_file
from languages import get_all_languages


def _loader(message: str):
    """Small helper to show a lightweight loading message."""
    with st.spinner(message):
        yield


def _init_history():
    if "conv_history" not in st.session_state:
        st.session_state.conv_history = []


def _append_message(speaker: str, src_lang: str, tgt_lang: str,
                    original_text: str, translated_text: str):
    st.session_state.conv_history.append(
        {
            "speaker": speaker,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "original": original_text,
            "translated": translated_text,
        }
    )


def _render_history():
    if not st.session_state.conv_history:
        st.info("No conversation yet. Start by recording from Doctor or Patient.")
        return

    for msg in st.session_state.conv_history:
        speaker = msg["speaker"]
        original = msg["original"]
        translated = msg["translated"]
        src_lang = msg["src_lang"]
        tgt_lang = msg["tgt_lang"]

        st.markdown(
            f"""
            <div class="app-card" style="margin-bottom:0.4rem;">
              <div class="pill-label">{speaker}</div>
              <div style="font-size:0.82rem; color:#9ca3af; margin-bottom:0.2rem;">
                {src_lang} → {tgt_lang}
              </div>
              <div style="font-size:0.9rem; margin-bottom:0.15rem;"><b>Spoken:</b> {original}</div>
              <div style="font-size:0.9rem;"><b>Translated:</b> {translated}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _download_history_pdf_button():
    if not st.session_state.conv_history:
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Doctor–Patient Conversation", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "", 11)

    for msg in st.session_state.conv_history:
        speaker = msg["speaker"]
        src_lang = msg["src_lang"]
        tgt_lang = msg["tgt_lang"]
        original = msg["original"]
        translated = msg["translated"]

        pdf.multi_cell(0, 6, f"{speaker} ({src_lang} → {tgt_lang})")
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 5, f"Spoken: {original}")
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 5, f"Translated: {translated}")
        pdf.ln(2)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")

    st.download_button(
        label="📄 Download conversation as PDF",
        data=pdf_bytes,
        file_name="doctor_patient_conversation.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def _process_turn(role: str, audio_bytes: bytes, src_lang: str, tgt_lang: str):
    """
    Full pipeline for one side:
    audio -> text -> translation -> TTS + history
    """
    if not audio_bytes:
        st.error(f"Please record {role.lower()} audio first.")
        return

    # Save audio to temp WAV
    import tempfile

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(audio_bytes)
    tmp.flush()
    tmp.close()
    wav_path = tmp.name

    try:
        with st.spinner(f"Recognizing {role} speech..."):
            original_text = speech_to_text(wav_path, source_language_name=src_lang)

        if not original_text or not original_text.strip():
            st.error(f"Could not recognize {role.lower()} speech. Please try again.")
            return

        with st.spinner("Translating and generating reply audio..."):
            translated_text = translate_text(original_text, src_lang, tgt_lang)

            # Show text in UI
            st.markdown(
                f"**{role} said:** {original_text}<br/>"
                f"**Translated:** {translated_text}",
                unsafe_allow_html=True,
            )

            # Add to history
            _append_message(role, src_lang, tgt_lang, original_text, translated_text)

            # TTS playback
            if translated_text.strip():
                tts_path = text_to_speech_file(translated_text, tgt_lang)
                if tts_path:
                    with open(tts_path, "rb") as f:
                        audio_out = f.read()
                    st.audio(audio_out, format="audio/mp3")
                    cleanup_temp_file(tts_path)
    finally:
        cleanup_temp_file(wav_path)


def show_conversation(theme_choice: str, languages: list[str] | None = None):
    """
    Main entry for the Doctor–Patient chat tab.
    """
    _init_history()

    if languages is None:
        languages = get_all_languages()

    st.markdown(
        """
        <div class="app-card" style="margin-top:0.8rem;">
          <div class="pill-label">Doctor–Patient chat</div>
          <div class="main-title" style="margin-bottom:0;">Live two-way translation</div>
          <div class="main-subtitle">
            Use the microphones below for each side. Each turn is recognized, translated,
            spoken out loud, and added to the conversation log.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_doc, col_pat = st.columns(2)

    with col_doc:
        st.markdown("#### 👩‍⚕️ Doctor side")
        doctor_lang = st.selectbox("Doctor speaks", languages, key="conv_doc_lang")

    with col_pat:
        st.markdown("#### 🧑‍🌾 Patient side")
        patient_lang = st.selectbox("Patient speaks", languages, key="conv_pat_lang")

    st.markdown("---")

    # Microphones
    col_mic_doc, col_mic_pat = st.columns(2)

    with col_mic_doc:
        st.markdown("##### Doctor microphone")
        doc_audio = medical_mic("Doctor microphone", key="conv_doc_mic")

    with col_mic_pat:
        st.markdown("##### Patient microphone")
        pat_audio = medical_mic("Patient microphone", key="conv_pat_mic")

    st.markdown("")

    col_buttons = st.columns(2)
    with col_buttons[0]:
        doc_to_pat = st.button("👩‍⚕️ Doctor → Patient", use_container_width=True)
    with col_buttons[1]:
        pat_to_doc = st.button("🧑‍🌾 Patient → Doctor", use_container_width=True)

    if doc_to_pat:
        _process_turn("Doctor", doc_audio, doctor_lang, patient_lang)

    if pat_to_doc:
        _process_turn("Patient", pat_audio, patient_lang, doctor_lang)

    st.markdown("---")
    st.markdown("### 🗂 Conversation history")
    _render_history()
    _download_history_pdf_button()
