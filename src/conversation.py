from __future__ import annotations

import tempfile
import os
import streamlit as st

from stt import speech_to_text
from translate import translate_text
from tts import text_to_speech

# -------- OPTIONAL PDF SUPPORT (CRASH SAFE) -------- #
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False


# ---------------- PDF (UNICODE SAFE & CRASH SAFE) ---------------- #

def _download_history_pdf_button():
    history = st.session_state.get("conversation_history", [])
    if not history or not PDF_AVAILABLE:
        return

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_path = tmp.name

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        x = 40
        y = height - 40
        c.setFont("Helvetica", 11)

        c.drawString(x, y, "Doctor - Patient Conversation")
        y -= 30

        for role, msg in history:
            text = f"{role}: {msg}"
            for line in text.split("\n"):
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y = height - 40
                c.drawString(x, y, line)
                y -= 15

        c.save()

        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 Download Conversation PDF",
                f,
                file_name="conversation.pdf",
                mime="application/pdf",
            )

    except Exception as e:
        st.warning("PDF generation failed")

    finally:
        if "pdf_path" in locals() and os.path.exists(pdf_path):
            os.remove(pdf_path)


# ---------------- MAIN UI ---------------- #

def show_conversation(theme_choice: str, languages: list[str]):
    st.header("Doctor – Patient Conversation")

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    col1, col2 = st.columns(2)

    # ---------- DOCTOR ---------- #
    with col1:
        st.subheader("Doctor")
        doctor_lang = st.selectbox(
            "Doctor language", languages, key="doc_lang"
        )
        doctor_audio = st.audio_input(
            "🎤 Record doctor audio", key="doctor_audio"
        )

    # ---------- PATIENT ---------- #
    with col2:
        st.subheader("Patient")
        patient_lang = st.selectbox(
            "Patient language", languages, key="pat_lang"
        )
        patient_audio = st.audio_input(
            "🎤 Record patient audio", key="patient_audio"
        )

    st.divider()
    col3, col4 = st.columns(2)

    # ---------- DOCTOR → PATIENT ---------- #
    with col3:
        if st.button("Doctor → Patient"):
            if not doctor_audio:
                st.warning("Please record doctor audio first")
            else:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                        f.write(doctor_audio.getbuffer())
                        wav_path = f.name

                    text = speech_to_text(wav_path, doctor_lang)
                    if text:
                        translated = translate_text(
                            text, doctor_lang, patient_lang
                        )
                        st.session_state.conversation_history.append(
                            ("Doctor", text)
                        )
                        st.session_state.conversation_history.append(
                            ("Patient", translated)
                        )
                        text_to_speech(translated, patient_lang)
                    else:
                        st.warning("Speech could not be recognized")

                except Exception as e:
                    st.error("Doctor → Patient processing failed")

                finally:
                    if "wav_path" in locals() and os.path.exists(wav_path):
                        os.remove(wav_path)

    # ---------- PATIENT → DOCTOR ---------- #
    with col4:
        if st.button("Patient → Doctor"):
            if not patient_audio:
                st.warning("Please record patient audio first")
            else:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                        f.write(patient_audio.getbuffer())
                        wav_path = f.name

                    text = speech_to_text(wav_path, patient_lang)
                    if text:
                        translated = translate_text(
                            text, patient_lang, doctor_lang
                        )
                        st.session_state.conversation_history.append(
                            ("Patient", text)
                        )
                        st.session_state.conversation_history.append(
                            ("Doctor", translated)
                        )
                        text_to_speech(translated, doctor_lang)
                    else:
                        st.warning("Speech could not be recognized")

                except Exception:
                    st.error("Patient → Doctor processing failed")

                finally:
                    if "wav_path" in locals() and os.path.exists(wav_path):
                        os.remove(wav_path)

    st.divider()

    # ---------- HISTORY ---------- #
    if st.session_state.conversation_history:
        st.subheader("Conversation History")
        for role, msg in st.session_state.conversation_history:
            st.write(f"**{role}:** {msg}")

        _download_history_pdf_button()
    else:
        st.info("No conversation yet")
