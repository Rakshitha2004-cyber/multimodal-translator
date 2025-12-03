# conversation.py – Doctor–Patient live chat with PDF export

from __future__ import annotations

import tempfile
import streamlit as st
from fpdf import FPDF

from mic_ui import medical_mic
from translate import translate_text
from stt import speech_to_text
from tts import text_to_speech_file, cleanup_temp_file
from languages import get_all_languages


def _init_history():
    if "conv_history" not in st.session_state:
        st.session_state.conv_history = []


def _append_message(
    speaker: str,
    src_lang: str,
    tgt_lang: str,
    original_text: str,
    translated_text: str,
):
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
              <div style="font-size:0.9rem; margin-bottom:0.15rem;">
                <b>Spoken:</b> {original}
              </div>
              <div style="font-size:0.9rem;">
                <b>Translated:</b> {translated}
              </div>
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


def _process_turn(role: str, audio_data, src_lang: str, tgt_lang: str):
    """
    Full pipeline for one side:
    audio -> text -> translation -> TTS + history
    `audio_data` is what comes back from medical_mic (usually bytes).
    """
    if audio_data is None:
        st.error(f"Please record {role.lower()} audio first.")
        return

    audio_bytes = audio_data
    if isinstance(audio_bytes, tuple):
        audio_bytes = audio_bytes[0]
    if hasattr(audio_bytes, "read"):
        audio_bytes = audio_bytes.read()

    if not isinstance(audio_bytes, (bytes, bytearray)):
        try:
            audio_bytes = bytes(audio_bytes)
        except Exception:
            st.error("Internal error: could not convert recorded audio.")
            return

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(audio_bytes)
    tmp.flush()
    tmp.close()
    wav_path = tmp.name

    try:
        with st.spinner(f"Recognizing {role} speech..."):
            # ✅ NO keyword argument here
            original_text = speech_to_text(wav_path, src_lang)

        if not original_text or not original_text.strip():
            st.error(f"Could not recognize {role.lower()} speech. Please try again.")
            return

        with st.spinner("Translating and generating reply audio..."):
            translated_text = translate_text(original_text, src_lang, tgt_lang)

            st.markdown(
                f"**{role} said:** {original_text}<br/>"
                f"**Translated:** {translated_text}",
                unsafe_allow_html=True,
            )

            _append_message(role, src_lang, tgt_lang, original_text, translated_text)

            if translated_text and translated_text.strip():
                tts_path = text_to_speech_file(translated_text, tgt_lang)
                if tts_path:
                    with open(tts_path, "rb") as f:
                        audio_out = f.read()
                    st.audio(audio_out, format="audio/mp3")
                    cleanup_temp_file(tts_path)
    finally:
        cleanup_temp_file(wav_path)
