# conversation.py
# conversation.py – Doctor–Patient back-and-forth mode (final)

from __future__ import annotations

import tempfile

import streamlit as st

from mic_ui import medical_mic
from stt import speech_to_text
from translate import translate_text
from tts import text_to_speech_file, cleanup_temp_file


def _append_history(role: str, src_text: str, tgt_text: str):
    """
    Save one turn of the conversation into session_state.
    """
    if "conv_history" not in st.session_state:
        st.session_state["conv_history"] = []

    st.session_state["conv_history"].append(
        {
            "role": role,
            "source": src_text,
            "translated": tgt_text,
        }
    )


def _render_history():
    """
    Show conversation history nicely.
    """
    history = st.session_state.get("conv_history", [])
    if not history:
        st.info("No conversation yet. Record speech from patient or doctor to begin.")
        return

    st.markdown("### 🧾 Conversation History")
    for i, turn in enumerate(history, start=1):
        role = turn["role"]
        src = turn["source"]
        tgt = turn["translated"]

        st.markdown(
            f"""
            <div class="app-card" style="margin-bottom:0.6rem;">
              <div class="pill-label">Turn {i} – {role}</div>
              <div style="font-size:0.9rem; margin-top:0.3rem;">
                <b>Original:</b> {src}
              </div>
              <div style="font-size:0.9rem; margin-top:0.2rem;">
                <b>Translated:</b> {tgt}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _process_speech(
    audio_bytes: bytes | None,
    from_lang_name: str,
    to_lang_name: str,
    speaker_label: str,
    listener_label: str,
):
    """
    Common helper to process a recorded utterance:
    - STT in speaker language
    - Translate to listener language
    - TTS audio in listener language
    """
    if audio_bytes is None:
        st.error(f"Please record {speaker_label} audio before processing.")
        return

    # Save mic bytes to temp WAV
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(audio_bytes)
    tmp.flush()
    tmp.close()
    audio_path = tmp.name

    try:
        # ---- STT ----
        with st.spinner(f"Recognizing {speaker_label.lower()} speech..."):
            src_text = speech_to_text(audio_path, from_lang_name)

        if not src_text or not src_text.strip():
            st.error(
                "I could not recognize any speech. "
                "Please record again, speaking clearly and closer to the microphone."
            )
            return

        # ---- Translation ----
        with st.spinner("Translating and generating reply audio..."):
            tgt_text = translate_text(src_text, from_lang_name, to_lang_name)

        _append_history(f"{speaker_label} ➜ {listener_label}", src_text, tgt_text)

        st.success(f"{speaker_label} speech processed.")
        st.markdown(f"**Recognized {speaker_label.lower()} speech:**")
        st.write(src_text)
        st.markdown(f"**Translated for {listener_label.lower()}:**")
        st.write(tgt_text)

        # ---- TTS in listener language ----
        if tgt_text and tgt_text.strip():
            tts_path = text_to_speech_file(tgt_text, to_lang_name)
            if tts_path:
                with open(tts_path, "rb") as f:
                    audio_bytes_out = f.read()
                st.markdown(f"**{listener_label} hears (audio):**")
                st.audio(audio_bytes_out, format="audio/mp3")
                cleanup_temp_file(tts_path)

    except Exception as e:
        st.error(f"Error while processing {speaker_label.lower()} speech: {e}")
    finally:
        cleanup_temp_file(audio_path)


def show_conversation(theme_choice: str, languages: list[str]):
    """
    Main entry point for Doctor–Patient Chat page.
    Called from main_app.main().
    """

    default_patient = languages.index("English") if "English" in languages else 0
    default_doctor = (
        languages.index("Hindi")
        if "Hindi" in languages
        else (1 if len(languages) > 1 else 0)
    )

    st.markdown(
        """
        <div class="app-card" style="margin-top:0.8rem;">
          <div class="pill-label">Doctor–Patient Conversation Mode</div>
          <div style="display:flex; align-items:center; gap:0.4rem;">
            <span style="font-size:1.3rem;">🗣️</span>
            <div class="main-subtitle">
              Turn-based conversation: patient speaks, doctor hears translation;
              then doctor replies, patient hears translation.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Language configuration
    st.markdown("### 🌐 Choose conversation languages")
    col_plang, col_dlang = st.columns(2)
    with col_plang:
        patient_lang = st.selectbox(
            "Patient language", languages, index=default_patient, key="conv_patient_lang"
        )
    with col_dlang:
        doctor_lang = st.selectbox(
            "Doctor language", languages, index=default_doctor, key="conv_doctor_lang"
        )

    st.markdown("---")

    # Ensure session_state keys exist
    if "conv_patient_audio" not in st.session_state:
        st.session_state["conv_patient_audio"] = None
    if "conv_doctor_audio" not in st.session_state:
        st.session_state["conv_doctor_audio"] = None

    # Two-column layout: Patient speaks, Doctor speaks
    col_patient, col_doctor = st.columns(2)

    # ----- Patient side -----
    with col_patient:
        st.markdown("### 👩‍🌾 Patient Speaks")
        st.markdown("**Patient Microphone**")
        st.caption("Tap the microphone once to start, and again to stop recording.")

        audio_patient = medical_mic("Patient microphone", key="conv_patient_mic")
        if audio_patient is not None:
            st.session_state["conv_patient_audio"] = audio_patient
            st.success("Recording saved.")
            st.audio(audio_patient, format="audio/wav")

        if st.button("Process Patient Speech", key="btn_process_patient"):
            _process_speech(
                st.session_state["conv_patient_audio"],
                patient_lang,
                doctor_lang,
                "Patient",
                "Doctor",
            )

    # ----- Doctor side -----
    with col_doctor:
        st.markdown("### 🧑‍⚕️ Doctor Speaks")
        st.markdown("**Doctor Microphone**")
        st.caption("Tap the microphone once to start, and again to stop recording.")

        audio_doctor = medical_mic("Doctor microphone", key="conv_doctor_mic")
        if audio_doctor is not None:
            st.session_state["conv_doctor_audio"] = audio_doctor
            st.info("Record audio above, then click the button to process.")
            st.audio(audio_doctor, format="audio/wav")

        if st.button("Process Doctor Speech", key="btn_process_doctor"):
            _process_speech(
                st.session_state["conv_doctor_audio"],
                doctor_lang,
                patient_lang,
                "Doctor",
                "Patient",
            )

    st.markdown("---")
    _render_history()
